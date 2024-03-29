import datetime
import json
import time
import os

import requests

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from urllib.parse import urljoin, urlparse, urlencode

from rest_framework import serializers, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer, OpenApiParameter

from web3 import Web3
from web3.middleware import geth_poa_middleware

from .serializers import StorageSerializer, QuoteSerializer, CreateStorageSerializer
from .models import Quote, Storage, File, PaymentMethod, AcceptedToken, UPLOAD_CODE
from .utils import check_params_validity, upload_files_to_ipfs, upload_files_to_microservice, create_allowance
from web3.auto import w3
from eth_account.messages import encode_defunct


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
        POST a storage service, handling different error codes
        """
        try:
            data = request.data
            print(f"Received registration request data: {data}")

            # Extract the signature and original message from the request data
            signature = data.get('signature')
            original_message = data.get('url')
            
            # Ensure the signature and original message are present
            if not signature or not original_message:
                print("Signature or original message missing in request data.")
                return Response("Invalid input data.", status=400)

            if not data.get('type'):
                print("Type key missing or None in request data.")
                return Response("Invalid input data.", status=400)

            # Verify the signature and get the address that signed the original message
            try:
                print(f"Received signature in request: {signature}")
                print(f"Received original_message in request: {original_message}")
                message = encode_defunct(text=original_message)
                print(f"Encoded message: {message}")
                recovered_address = w3.eth.account.recover_message(message, signature=signature)
                print(f"Recovered Ethereum address: {recovered_address}")
            except Exception as e:
                print("Failed to verify the signature.")
                print(f"Specific error: {e}")
                return Response("Invalid signature.", status=400)

            # Check if the recovered_address matches the APPROVED_ADDRESS from the environment variables
            approved_address = os.environ.get('APPROVED_ADDRESS')
            print(f"Approved Ethereum address from env: {approved_address}")
            if recovered_address.lower() != approved_address.lower():
                print("Registration request received from non-approved address.")
                return Response("Registration request received from non-approved address.", status=403)

            print("Registration request received from approved address. Proceeding with registration.")
            storage, created = Storage.objects.get_or_create(type=data['type'])

            if not created:
                if storage.is_active:
                    print("Chosen storage type is already active and registered.")
                    return Response('Chosen storage type is already active and registered.', status=200)
                else:
                    storage.is_active = True
                    storage.save()
                    print("Chosen storage type reactivated.")
                    return Response('Chosen storage type reactivated.', status=201)

            # Set optional fields
            storage.description = data.get('description')
            storage.url = data.get('url')

            # Validate the storage object
            try:
                storage.full_clean()
            except ValidationError as e:
                print(f"Validation Error: {e}")
                return Response(str(e), status=400)

            # Save the storage object to the database
            storage.save()

            # Handle payment methods and accepted tokens
            for payment_method_data in data.get('payment', []):
                print("Attempting to add payment method")
                payment_method = PaymentMethod(
                    storage=storage, chainId=payment_method_data['chainId'])
                payment_method.save()
                print("Payment method created")

                for token in payment_method_data['acceptedTokens']:
                    print("Attempting to add accepted token")
                    token_title, token_value = list(token.items())[0]
                    accepted_token = AcceptedToken(
                        paymentMethod=payment_method, title=token_title, value=token_value)
                    accepted_token.save()
                    print("Accepted token created")
                
            return Response('Desired storage created.', status=201)
        except Exception as e:
            print(f"Unhandled exception occurred: {e}")
            return Response("Internal server error.", status=500)

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
        print(f"Retrieved storages: {storages}")
        serializer = self.read_serializer_class(storages, many=True)
        print(f"Serialized storages: {serializer.data}")
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
                      {"length": 2},
                      {"length": 2}
                    ],
                    "duration": 1234,
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
        print('data: ', data)

        # Make sure request data contains type and files
        if (not 'type' in data or not 'files' in data):
            print("Error: Type or files key missing in request data.")
            return Response("Invalid input data.", status=400)

        # From type, retrieve associated storage object
        try:
            storage = Storage.objects.get(type=data['type'])
            # If not exists, raise error
        except:
            return Response({'error': 'Chosen storage type does not exist.'}, status=400)
        
        response = None 

        try:
            # For the given type of storage, make a call to the associated service API (mock first) to retrieve a cost associated with that
            headers = {'User-Agent': 'Mozilla/5.0',
                    'Content-Type': 'application/json'}

            get_quote_url = urljoin(storage.url, 'getQuote')
            print(f"Preparing to make request to URL: {get_quote_url}")
            parsed_url = urlparse(get_quote_url)
            print(f"Using port: {parsed_url.port or 'default port (80 or 443)'}")


            # Log the data being sent for troubleshooting
            print(f"Data being sent: {json.dumps(data)}")
            print(f"Headers being sent: {headers}")

            response = requests.post(
                get_quote_url,
                json.dumps(data),
                headers=headers,
                timeout=10  # Set a timeout to avoid indefinite waiting
            )

            # If the request was successful, log the response content
            if response.status_code == 200:
                print(f"Request to {get_quote_url} was successful.")
                print(f"Response received: {response.text}")
            else:
                print(f"Received {response.status_code} status code from {get_quote_url} with response: {response.text}")

        except requests.Timeout:
            print(f"Request to {get_quote_url} timed out.")

        except requests.RequestException as e:
            print(f"An error occurred while making a request to {get_quote_url}. Error: {e}")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        if response is None:
            print("No response was obtained from the API call.")

        try:
            if response:
                print("Response received.")

                if response.status_code == 200:
                    print("Response status code is 200.")

                    try:
                        response_data = json.loads(response.content)
                        print("Response data successfully decoded from JSON.")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        return Response({'error': 'Invalid response format'}, status=500)

                    data['storage'] = storage.pk
                    data['status'] = UPLOAD_CODE[1][0]
                    data['payment']['paymentMethod'] = {'chainId': data['payment']['chainId']}
                    data['payment']['userAddress'] = data['userAddress']
                    data.update(response_data)

                    serializer = QuoteSerializer(data=data)
                    if serializer.is_valid():
                        print("Serializer is valid.")
                        try:
                            quote = serializer.save()
                            print("Quote saved successfully.")
                            return Response({
                                'quoteId': quote.quoteId,
                                'tokenAmount': quote.tokenAmount,
                                'approveAddress': quote.approveAddress,
                                'chainId': data['payment']['paymentMethod']['chainId'],
                                'tokenAddress': quote.tokenAddress
                            }, status=201)
                        except Exception as e:
                            print(f"Error saving quote: {e}")
                            return Response({'error': 'Error saving quote'}, status=500)
                    else:
                        print("Serializer validation failed.")
                        print(serializer.errors)
                        return Response(serializer.errors, status=400)
                else:
                    print(f"Response status code is not 200. Status code: {response.status_code}")
                    try:
                        return Response(response.json(), status=400)
                    except Exception as e:
                        print(f"Error parsing response: {e}")
                        return JsonResponse({'error': 'Invalid response format'}, status=500)
            else:
                print("No response received.")
                return JsonResponse({'error': 'No response received'}, status=500)
        except Exception as e:
            print(f"Unhandled exception: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

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
        get_status_endpoint = f'getStatus?quoteId={quoteId}'
        get_status_url = urljoin(quote.storage.url, get_status_endpoint)
        response = requests.get(
            get_status_url
        )

        try:
            quote.status = json.loads(response.content)['status']
            quote.save()
        except Exception as e:
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
        try:
            quote.save()
        except Exception as e:
            return Response(f"Error updating quote status: {str(e)}", status=500)

        try:
        # Upload files to IPFS
            files_reference = upload_files_to_ipfs(request.FILES, quote)
        except Exception as e:
            return Response(f"Error uploading to IPFS: {str(e)}", status=500)

        # Upload files to micro-service
        try:
            response = upload_files_to_microservice(quote, params, files_reference)
        except Exception as e:
            return Response(f"Error uploading to micro-service: {str(e)}", status=500)

        if (response.status_code == 200):
            print("File upload to microservice succeeded.")
            quote.status = UPLOAD_CODE[5][0]
            try:
                quote.save()
            except Exception as e:
                return Response(f"Error saving quote after successful upload: {str(e)}", status=500)
            return Response("File upload succeeded.", status=200)
        
        else:
            print(f"Microservice upload failed with status code: {response.status_code}. Error message: {response.content}")
            quote.status = UPLOAD_CODE[6][0]
            try:
                quote.save()
            except Exception as e:
                return Response(f"Error updating quote status after failed upload: {str(e)}", status=500)

            return Response(f"Microservice upload failed with status code: {response.status_code}", status=401)



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
        
        # Construct the URL using urljoin
        get_link_url = urljoin(quote.storage.url, 'getLink')

        # Use the params argument to handle query parameters
        query_parameters = {
            'quoteId': str(quoteId),
            'nonce': params['nonce'][0],
            'signature': params['signature'][0]
        }
        
        # Request status of quote from micro-service
        response = requests.get(get_link_url, params=query_parameters)

        if response.status_code != 200:
            return Response(json.loads(response.content), status=400)

        print("Sending response:", response.content)

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
        else:
            try:
                # Attempt to parse the response content as JSON
                responseObj = json.loads(response.content)
                return Response(responseObj, status=response.status_code)
            except json.JSONDecodeError:
                # If response.content is not valid JSON, return it as is
                return Response(response.content, status=response.status_code)


class QuoteHistory(APIView):
    @csrf_exempt
    @extend_schema(
        request=[],
        parameters=[
            OpenApiParameter(
                name='userAddress',
                description='User Address',
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
            ),
            OpenApiParameter(
                name='page',
                description='Page Number',
                type=int
            ),
            OpenApiParameter(
                name='pageSize',
                description='Page Size',
                type=int
            ),
            OpenApiParameter(
                name='storage',
                description='the name of the storage service',
                type=str
            )
        ],
        examples=[
            OpenApiExample(
                "QuoteHistoryResponseExample",
                value=[
                    {
                        "quoteId": "23",
                        "status": 400,
                        "chainId": 80001,
                        "tokenAddress": "0x222",
                        "tokenAmount": "999999999",
                        "approveAddress": "0x1234",
                        "transactionHash": "xxxx"
                    },
                    {
                        "quoteId": "23",
                        "chainId": 80001,
                        "tokenAddress": "0x222",
                        "tokenAmount": "999999999",
                        "approveAddress": "0x1234",
                        "requestId": "xxxx"
                    }
                ],
                request_only=False,
                response_only=True
            )
        ],
        responses={
            200: inline_serializer(
                name='QuoteHistoryResponseSerializer',
                fields={
                    "quoteId": serializers.CharField(),
                    "status": serializers.IntegerField(),
                    "chainId": serializers.IntegerField(),
                    "tokenAddress": serializers.CharField(),
                    "tokenAmount": serializers.CharField(),
                    "approveAddress": serializers.CharField(),
                    "transactionHash": serializers.CharField(),
                    "requestId": serializers.CharField(),
                }
            ),
            404: OpenApiResponse(description='History Not Found.'),
        }
    )
    def get(self, request):
        print(f'Entered getHistory endpoint: {datetime.datetime.now()}')
        params = {**request.GET}

        if not all(key in params for key in ('userAddress', 'nonce', 'signature', 'storage')):
            return Response("Missing query parameters. It must include userAddress, nonce, signature and storage.", status=400)

        print(f'Checked validation at: {datetime.datetime.now()}')

        storage_type = request.GET.get('storage')
        print(f'Retrieved storage type at {datetime.datetime.now()}, {storage_type}')
        userAddress = request.GET.get('userAddress')
        print(f'Retrieved userAddress at {datetime.datetime.now()}, {userAddress}')
        page = request.GET.get('page', 1)
        pageSize = request.GET.get('pageSize', 25)

        """
        Retrieve the quote documents from the micro-services
        """
        try:
            storages = Storage.objects.filter(is_active=True)
            print(f'Storages {storages} at {datetime.datetime.now()}')
        except Exception as e:
            return Response(f"Error while retrieving possible storages: {str(e)}", status=500)

        try:
            storage = Storage.objects.filter(is_active=True, type=storage_type).first()
            if storage is None:
                print(f'No matching storage type found at {datetime.datetime.now()}')
                return Response("No matching storage type found", status=404)

            query_params = {
                'page': page,
                'pageSize': pageSize,
                'userAddress': userAddress,
                'nonce': params['nonce'][0],
                'signature': params['signature'][0],
            }
            absolute_url = urljoin(storage.url, f'getHistory?{urlencode(query_params)}')
            response = requests.get(absolute_url)
            print(f'Got response from microservice at {datetime.datetime.now()}')
            print(f'Response: {response}')

            if response.status_code == 200:
                return Response(response.json(), status=200)
            else:
                return Response(response.json(), status=500)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return Response(f"An error occurred: {str(e)}", status=500)

        
