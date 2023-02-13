import json
import requests

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt

from rest_framework import serializers, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer, OpenApiParameter

from web3 import Web3
from web3.middleware import geth_poa_middleware

from .serializers import StorageSerializer, QuoteSerializer, CreateStorageSerializer
from .models import Quote, Storage, File, UPLOAD_CODE
from .utils import check_params_validity

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
          "payment":[
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

    # Make sure request data contains type and files
    if (not 'type' in data):
      return Response("Invalid input data.", status=400)

    # Check if storage object with given type already exists
    # From type, retrieve associated storage object
    try:
      storage = Storage.objects.get(type=data['type'])
      if storage:
        return Response('Chosen storage type already exists.', status=400)
    except:
      # print(data['payment'])
      for payment_method in data['payment']:
        transit_table = []
        for token in payment_method['acceptedTokens']:
          accepted_token={}
          accepted_token['title'] = list(token.keys())[0]
          accepted_token['value'] = list(token.values())[0]
          transit_table.append(accepted_token)
        
        payment_method['acceptedTokens'] = transit_table

      serializer = self.write_serializer_class(data=data)
      if serializer.is_valid():
          storage = serializer.save()
          return Response('Desired storage created.', status=201)

      return Response('Invalid input data.', status=400)


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
    storages = Storage.objects.all()
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
            {"length":234},
            {"length":236}
          ],
          "duration": 123,
          "payment": {
              "chainId": 80001,
              "tokenAddress": "0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889"
          },
          "userAddress": "0xCC866199C810B216710A3F3714d35920C343a8CD"
        },
        request_only=True, # signal that example only applies to requests
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
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
    response = requests.post(
      storage.url + 'getQuote/',
      json.dumps(data),
      headers=headers
    )

    # From the response data:
    if response and response.status_code == 200:
      # Save the quote and cost/payment request
      data = {**data, **json.loads(response.content)}

      # Creating the new payment with status still to execute
      data['storage'] = storage.pk
      data['payment']['paymentMethod'] = {'chainId': data['payment']['chainId']}
      data['payment']['wallet_adress'] = data['payment']['tokenAddress'] 

      serializer = QuoteSerializer(data=data)
      if serializer.is_valid():
          serializer.save()
          return Response({
            'quoteId': serializer.data['quoteId'],
            'tokenAmount': serializer.data['tokenAmount'],
            'approveAddress': serializer.data['approveAddress'],
            'chainId': data['payment']['paymentMethod']['chainId'],
            'tokenAddress': serializer.data['tokenAddress']
          }, status=201)
      return Response(serializer.errors, status=400)
    else: return Response({'error': 'Storage service response badly formatted.'}, status=400)


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
      quote.storage.url  + 'getStatus?quoteId=' + str(quoteId)
    )

    if (response.status_code == 200):
      quote.status = json.loads(response.content)['status']
      quote.save()

    return Response({
      'status': quote.status
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
    request= {
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
          'file1':{'name':'image.png', 'Hash':'QmPmnyA8ZaYFJknPhVBE1u4hbGqvLGvu5cxCAPb1Nqb1aq',"size":"59"},
          'file2':{"Name":"image2.png",'Hash':'QmUq54U3BVx9vSKRSNVoSCoLD9wBkeDXrzK7FqRgdgnCGK',"size":"59"},
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
    if quote.status in [UPLOAD_CODE[4], UPLOAD_CODE[5]]:
      return Response("Files already uploaded.", status=400)

    # Stating that files are currently uploading
    quote.status = UPLOAD_CODE[4]
    quote.save()

    # Forward the files to IPFS, retrieve whatever the hash they provide us, mocked in the test
    files_reference = []
    url = getattr(settings, 'IPFS_SERVICE_ENDPOINT', "http://127.0.0.1:5001/api/v0/add")

    response = requests.post(url, files=request.FILES)
    files=response.text.splitlines()
    for file in files:
      added_file={}
      json_version = json.loads(file)
      added_file['title']=json_version['Name']
      added_file['cid']=json_version['Hash']
      added_file['public_url']=f"https://ipfs.io/ipfs/{added_file['cid']}?filename={added_file['title']}"

      # Forward the files to IPFS, retrieve whatever they provide us (the hash), mocked in the test
      File.objects.create(quote=quote, **added_file)
      files_reference.append("ipfs://" + str(added_file['cid']))

    try:
      rpcProvider = quote.payment.paymentMethod.rpcEndpointUrl
    except ObjectDoesNotExist:
      rpcProvider = "https://rpc-mumbai.maticvigil.com/"

    my_provider = Web3.HTTPProvider(rpcProvider)
    w3 = Web3(my_provider)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Creating allowance for funds transfer from my user address to the quote paymentAddress
    approvalAddress = quote.approveAddress # '0xAFcE990754C38Be5E0C341707B2A162C4e67547B'
    tokenAddress = quote.tokenAddress # '0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889'
    userAddress = quote.payment.wallet_address #'0xCC866199C810B216710A3F3714d35920C343a8CD'
    
    abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'
    abi = json.loads(abi)
    
    contractAddress = w3.toChecksumAddress(tokenAddress)
    contract = w3.eth.contract(contractAddress, abi=abi)
    
    userAddress = w3.toChecksumAddress(userAddress)
    approvalAddress = w3.toChecksumAddress(approvalAddress)
    nonce = w3.eth.getTransactionCount(userAddress)
    tx_hash = contract.functions.approve(approvalAddress, quote.tokenAmount).buildTransaction({'from': userAddress, 'nonce': nonce})
    signed_tx = w3.eth.account.signTransaction(tx_hash, 'bbb5a2d50f3956e72dd8f38096270d8d951e44da623b1e31422d724e5841c93f')
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction receipt:" + str(tx_receipt))
    print("Contract allowance:" + str(contract.functions.allowance(userAddress, approvalAddress).call()))

    data = {
      "quoteId": quote.quoteId,
      "nonce": params['nonce'][0],
      "signature": params['signature'][0],
      "files": files_reference
    }

    # Upload files to micro-service
    response = requests.post(
      quote.storage.url + 'upload/?quoteId=' + str(quoteId) + '&nonce=' + params['nonce'][0] + '&signature=' + params['signature'][0],
      data
    )

    if (response.status_code == 200):
      quote.status = UPLOAD_CODE[5]
      quote.save()

      return Response("File upload succeeded.", status=200)

    quote.status = UPLOAD_CODE[6]
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
      quote.storage.url + 'getLink?quoteId=' + str(quoteId) + '&nonce=' + params['nonce'][0] + '&signature=' + params['signature'][0]
    )

    print(json.loads(response.content))
    if response.status_code != 200:
      return Response(json.loads(response.content), status=400)

    if quote.storage.type == "arweave":
      #TODO: improve that by managing the different link format from different services.
      responseObj = json.loads(response.content)
      # result = []
      # for item in responseObj:
      #   result.append({''})
      return Response(responseObj, status=200)
    elif quote.storage.type == "filecoin":
      #TODO: improve that by managing the different link format from different services.
      return Response({
        "type": quote.storage.type,
        "CID": json.loads(response.content)[0]['CID']
      })
