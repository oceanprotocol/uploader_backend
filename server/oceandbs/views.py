import json
import requests

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.csrf import csrf_exempt

from rest_framework import serializers, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer, OpenApiParameter

from web3 import Web3
from web3.middleware import geth_poa_middleware

from .serializers import StorageSerializer, QuoteSerializer, CreateStorageSerializer
from .models import Quote, Storage, File, PaymentMethod, AcceptedToken, UPLOAD_CODE
from .utils import check_params_validity, upload_files_to_ipfs, upload_files_to_microservice, create_allowance

# Storage service creation class
class StorageCreationView(APIView):
    write_serializer_class = CreateStorageSerializer
    parser_classes = (parsers.JSONParser,)

    @csrf_exempt
    @extend_schema(
        request=[],
        parameters=[],
        examples=[
            OpenApiExample(
                "StorageCreationRequestExample",
                value={
                    "type": "filecoin",
                    "description":  "File storage on FileCoin",
                    "url": "http://localhost:3000/",
                    "payment": [
                      {
                          "chainId": "1",
                          "acceptedTokens": [
                              {
                                  "OCEAN": "0xOCEAN_on_MAINNET"
                              },
                              {
                                  "DAI": "0xDAI_ON_MAINNET"
                              }
                          ]
                      },
                        {
                          "chainId": "polygon_chain_id",
                          "acceptedTokens": [
                              {
                                  "OCEAN": "0xOCEAN_on_POLYGON"
                              },
                              {
                                  "DAI": "0xDAI_ON_POLYGON"
                              }
                          ]
                      }
                    ]
                },
                request_only=True,
                response_only=False
            )
        ],
        responses={
            201: OpenApiResponse(description='Desired storage created.'),
            400: OpenApiResponse(description='Invalid input data.'),
        }
    )
    def post(self, request):
        """
        POST a storage service, handling different error code
        """
        data = request.data

        if not data.get('type'):
            return Response("Invalid input data.", status=400)

        storage, created = Storage.objects.get_or_create(type=data['type'])

        if not created:
            if storage.is_active:
                return Response('Chosen storage type already exists.', status=400)
            else:
                storage.is_active = True
                storage.save()
                return Response('Chosen storage type reactivated.', status=201)

        # Set optional fields
        storage.description = data.get('description')
        storage.url = data.get('url')

        # Validate the storage object
        try:
            storage.full_clean()
        except ValidationError as e:
            print(e)
            return Response('Invalid input data.', status=400)

        # Save the storage object to the database
        storage.save()

        # Handle payment methods and accepted tokens
        for payment_method_data in data.get('payment', []):
            payment_method = PaymentMethod(
                storage=storage, chainId=payment_method_data['chainId'])
            payment_method.save()

            for token in payment_method_data['acceptedTokens']:
                token_title, token_value = list(token.items())[0]
                accepted_token = AcceptedToken(
                    paymentMethod=payment_method, title=token_title, value=token_value)
                accepted_token.save()

        return Response('Desired storage created.', status=201)

# Storage service listing class


class StorageListView(APIView):
    read_serializer_class = StorageSerializer

    # Info endpoint listing all available storages
    @csrf_exempt
    @extend_schema(
        request=[],
        parameters=[],
        examples=[
            OpenApiExample(
                "StorageListResponseExample",
                value=[{
                    "type": "filecoin",
                    "description": "File storage on FileCoin",
                    "payment": [
                        {
                            "chainId": "1",
                            "acceptedTokens": [
                                {
                                    "OCEAN": "0xOCEAN_on_MAINNET"
                                },
                                {
                                    "DAI": "0xDAI_ON_MAINNET"
                                }
                            ]
                        },
                        {
                            "chainId": "polygon_chain_id",
                            "acceptedTokens": [
                                {
                                    "OCEAN": "0xOCEAN_on_POLYGON"
                                },
                                {
                                    "DAI": "0xDAI_ON_POLYGON"
                                }
                            ]
                        }
                    ]
                }
                ],
                request_only=False,
                response_only=True
            )
        ],
        responses={
            200: StorageSerializer
        }
    )
    def get(self, request):
        """
        List all available storages
        """
        storages = Storage.objects.filter(is_active=True)
        serializer = self.read_serializer_class(storages, many=True)
        return Response(serializer.data, status=200)

# Quote creation endpoint


class QuoteCreationView(APIView):
    parser_classes = (parsers.JSONParser,)

    @csrf_exempt
    @extend_schema(
        request=[],
        parameters=[],
        examples=[
            OpenApiExample(
                "QuoteCreationRequestExample",
                value={
                    "type": "arweave",
                    "files": [
                      {"length": 31},
                      {"length": 21}
                    ],
                    "duration": 12,
                    "payment": {
                        "chainId": 80001,
                        "tokenAddress": "0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889"
                    },
                    "userAddress": "0xCC866199C810B216710A3F3714d35920C343a8CD"
                },
                request_only=True,  # signal that example only applies to requests
                response_only=False
            ),
            OpenApiExample(
                "QuoteCreationResponseExample",
                value={
                    "tokenAmount": 500,
                    "approveAddress": "0x123",
                    "chainId": 1,
                    "tokenAddress": "0xOCEAN_on_MAINNET",
                    "quoteId": "xxxx"
                },
                request_only=False,
                response_only=True
            )
        ],
        responses={
            201: inline_serializer(
                name='ResponseBodyExample',
                fields={
                    'tokenAmount': serializers.IntegerField(),
                    'approveAddress': serializers.CharField(),
                    'chainId': serializers.IntegerField(),
                    'tokenAddress': serializers.CharField(),
                    'tokenAddress': serializers.CharField(),
                }
            ),
            400: OpenApiResponse(description='Storage service response badly formatted.'),
        }
    )
    def post(self, request):
        """
        POST a quote, handle different error code
        """
        data = request.data

        # Make sure request data contains type and files
        if (not 'type' in data or not 'files' in data):
            return Response("Invalid input data.", status=400)

        # From type, retrieve associated storage object
        try:
            storage = Storage.objects.get(type=data['type'])
            # If not exists, raise error
        except:
            return Response({'error': 'Chosen storage type does not exist.'}, status=400)

        # For the given type of storage, make a call to the associated service API (mock first) to retrieve a cost associated with that
        headers = {'User-Agent': 'Mozilla/5.0',
                   'Content-Type': 'application/json'}
        response = requests.post(
            storage.url + 'getQuote/',
            json.dumps(data),
            headers=headers
        )

        if response and response.status_code == 200:
            response_data = json.loads(response.content)

            data['storage'] = storage.pk
            data['status'] = UPLOAD_CODE[1][0]
            data['payment']['paymentMethod'] = {
                'chainId': data['payment']['chainId']}
            data['payment']['userAddress'] = data['userAddress']

            data.update(response_data)

            serializer = QuoteSerializer(data=data)
            if serializer.is_valid():
                quote = serializer.save()
                return Response({
                    'quoteId': quote.quoteId,
                    'tokenAmount': quote.tokenAmount,
                    'approveAddress': quote.approveAddress,
                    'chainId': data['payment']['paymentMethod']['chainId'],
                    'tokenAddress': quote.tokenAddress
                }, status=201)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=400)
        else:
            return Response({'error': 'Storage service response badly formatted.'}, status=400)

# Quote detail endpoint displaying the detail of a quote, no update, no deletion for now.
class QuoteStatusView(APIView):
    @csrf_exempt
    @extend_schema(
        request=[],
        parameters=[
            OpenApiParameter(
                name='quoteId',
                description='Quote ID',
                type=str
            )
        ],
        examples=[
            OpenApiExample(
                "QuoteStatusResponseExample",
                value={
                    "status": 0,
                },
                request_only=False,
                response_only=True
            )
        ],
        responses={
            200: inline_serializer(
                name='QuoteStatusResponseExample',
                fields={
                    'status': serializers.IntegerField()
                }
            ),
            404: OpenApiResponse(description='Quote does not exist.'),
        }
    )
    def get(self, request):
        """
        Retrieve a quote status from the associated micro-service
        """
        quoteId = request.GET.get('quoteId')
        try:
            quote = Quote.objects.get(quoteId=quoteId)
        except Quote.DoesNotExist:
            return Response('Quote does not exist.', status=404)

        # Request status of quote from micro-service
        response = requests.get(
            quote.storage.url + 'getStatus?quoteId=' + str(quoteId)
        )

        try:
            quote.status = json.loads(response.content)['status']
            quote.save()
        except Exception as e:
            print(e)
            quote.status = UPLOAD_CODE[6][0]
            quote.save()

        return Response({
            "status": quote.status
        })

# Upload file associated with a quote endpoint
class UploadFile(APIView):
    @csrf_exempt
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='quoteId',
                description='Quote ID',
                type=str
            ),
            OpenApiParameter(
                name='nonce',
                description='Nonce',
                type=int
            ),
            OpenApiParameter(
                name='signature',
                description='Signature',
                type=str
            )
        ],
        request={
            "multipart/form-data": inline_serializer(
                name="InlineFormSerializer",
                fields={
                    "file1": serializers.FileField(),
                    "file2": serializers.FileField(),
                }
            )
        },
        examples=[
            OpenApiExample(
                "FileUploadRequestExample",
                value={
                    'file1': {'name': 'image.png', 'Hash': 'QmPmnyA8ZaYFJknPhVBE1u4hbGqvLGvu5cxCAPb1Nqb1aq', "size": "59"},
                    'file2': {"Name": "image2.png", 'Hash': 'QmUq54U3BVx9vSKRSNVoSCoLD9wBkeDXrzK7FqRgdgnCGK', "size": "59"},
                },
                media_type='application/x-www-form-urlencoded',
                request_only=True,
                response_only=False
            ),
            OpenApiExample(
                "FileUploadResponseExample",
                value={
                    "File upload succeeded."
                },
                request_only=False,
                response_only=True
            )
        ],
        responses={
            200: OpenApiResponse(description='File upload succeeded.'),
            400: OpenApiResponse(description='Looks like something failed.'),
        }
    )
    def post(self, request, format="multipart"):
        params = {**request.GET}
        quoteId = request.GET.get('quoteId')

        try:
            quote = Quote.objects.get(quoteId=quoteId)
        except Quote.DoesNotExist:
            return Response('Quote does not exist.', status=404)

        is_valid = check_params_validity(params, quote)
        if isinstance(is_valid, Response):
            return is_valid

        # Check existence of FILES in the request
        if not request.FILES:
            return Response("No file sent alongside the request.", status=400)

        # Check upload status to see if files have not been already uploaded
        if quote.status in [UPLOAD_CODE[4][0], UPLOAD_CODE[5][0]]:
            return Response("Files already uploaded.", status=400)

        # Update quote status to uploading
        quote.status = UPLOAD_CODE[4]
        quote.save()

        # Upload files to IPFS
        files_reference = upload_files_to_ipfs(request.FILES, quote)

        # Create allowance for funds transfer
        create_allowance(quote, 'bbb5a2d50f3956e72dd8f38096270d8d951e44da623b1e31422d724e5841c93f')

        # Upload files to micro-service
        response = upload_files_to_microservice(quote, params, files_reference)

        if (response.status_code == 200):
            quote.status = UPLOAD_CODE[5][0]
            quote.save()

            return Response("File upload succeeded.", status=200)

        quote.status = UPLOAD_CODE[6][0]
        quote.save()
        return Response("Looks like something failed.", status=401)


class QuoteLink(APIView):
    @csrf_exempt
    @extend_schema(
        request=[],
        parameters=[
            OpenApiParameter(
                name='quoteId',
                description='Quote ID',
                type=str
            ),
            OpenApiParameter(
                name='nonce',
                description='Nonce',
                type=int
            ),
            OpenApiParameter(
                name='signature',
                description='Signature',
                type=str
            )
        ],
        examples=[
            OpenApiExample(
                "QuoteLinkResponseExample",
                value=[
                    {
                        "type": "filecoin",
                        "CID": "xxxx",
                    }
                ],
                request_only=False,
                response_only=True
            )
        ],
        responses={
            200: inline_serializer(
                name='QuoteLinkResponseSerializer',
                fields={
                    'type': serializers.IntegerField(),
                    'CID': serializers.CharField()
                }
            ),
            404: OpenApiResponse(description='Quote does not exist.'),
        }
    )
    def get(self, request):
        params = {**request.GET}
        quoteId = request.GET.get('quoteId')

        try:
            quote = Quote.objects.get(quoteId=quoteId)
        except Quote.DoesNotExist:
            return Response('Quote does not exist.', status=404)

        is_valid = check_params_validity(params, quote)

        if isinstance(is_valid, Response):
            return is_valid

        """
    Retrieve the quote documents links from the associated micro-service
    """
        # Request status of quote from micro-service
        response = requests.get(
            quote.storage.url + 'getLink?quoteId=' +
            str(quoteId) + '&nonce=' +
            params['nonce'][0] + '&signature=' + params['signature'][0]
        )

        print(json.loads(response.content))
        if response.status_code != 200:
            return Response(json.loads(response.content), status=400)

        if quote.storage.type == "arweave":
            # TODO: improve that by managing the different link format from different services.
            responseObj = json.loads(response.content)
            # result = []
            # for item in responseObj:
            #   result.append({''})
            return Response(responseObj, status=200)
        elif quote.storage.type == "filecoin":
            # TODO: improve that by managing the different link format from different services.
            return Response({
                "type": quote.storage.type,
                "CID": json.loads(response.content)[0]['CID']
            })
