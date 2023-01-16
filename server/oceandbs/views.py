from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from rest_framework import serializers

from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.conf import settings

from .serializers import StorageSerializer, QuoteSerializer, CreateStorageSerializer
from .models import Quote, Storage, File, UPLOAD_CODE
from .utils import check_params_validity


# Storage service creation class 
class StorageCreationView(APIView):
  write_serializer_class = CreateStorageSerializer

  @csrf_exempt
  def post(self, request):
    """
    POST a storage service, handling different error code
    """
    data = JSONParser().parse(request)

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
      for payment_method in data['paymentMethods']:
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

      return Response('Input data is invalid.', status=400)


# Storage service listing class 
class StorageListView(APIView):
  read_serializer_class = StorageSerializer
  # Info endpoint listing all available storages
  @csrf_exempt
  def get(self, request, format=None):
    """
    List all available storages
    """
    storages = Storage.objects.all()
    serializer = self.read_serializer_class(storages, many=True)
    return Response(serializer.data, status=200)

# Quote creation endpoint
class QuoteCreationView(APIView):
  @csrf_exempt
  @extend_schema(
    request=[],
    parameters=[],
    examples=[
      OpenApiExample(
        "QuoteCreationRequestExample",
        value={
          "type": "filecoin",
          "files": [
            {"length":2343545},
            {"length":2343545}
          ],
          "duration": 4353545453,
          "payment": {
              "payment_method": {
                "chainId": 1,
              },
              "wallet_address": "0xOCEAN_on_MAINNET"
          },
          "userAddress": "0x456"
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
    data = JSONParser().parse(request)

    # Make sure request data contains type and files
    if (not 'type' in data or not 'files' in data):
      return Response("Invalid input data.", status=400)

    # From type, retrieve associated storage object
    try:
      storage = Storage.objects.get(type=data.pop('type'))
      # If not exists, raise error
    except:
      return Response('Storage service does not exist.', status=400)

    # For the given type of storage, make a call to the associated service API (mock first) to retrieve a cost associated with that
    response = requests.post(
      storage.url + 'getQuote/',
      data
    )

    # From the response data:
    if response and response.status_code == 200:
      # Save the quote and cost/payment request
      data = {**data, **json.loads(response.content)}

      # Creating the new payment with status still to execute
      data['storage'] = storage.pk
      data['payment']['paymentMethod'] = data['payment'].pop('payment_method')

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
    else: return Response('Storage service response badly formatted.', status=400)


# Quote detail endpoint displaying the detail of a quote, no update, no deletion for now.
class QuoteStatusView(APIView):
  @csrf_exempt
  def get(self, request):
    """
    Retrieve a quote status from the associated micro-service
    """
    try:
      quoteId = request.GET.get('quoteId')
      quote = Quote.objects.get(quoteId=quoteId)

      # Request status of quote from micro-service
      response = requests.get(
        quote.storage.url + 'quote/' + str(quoteId)
      )

      if (response.status_code == 200):
        quote.status = json.loads(response.content)['status']
        quote.save()

    except Quote.DoesNotExist:
      return HttpResponse(status=404)

    return Response({
      'status': quote.status
    })


# Upload file associated with a quote endpoint
class UploadFile(APIView):
  @csrf_exempt
  def post(self, request, format="multipart"):
    params = {**request.GET}
    quoteId = request.GET.get('quoteId')

    quote = Quote.objects.get(quoteId=quoteId)
    if not quote:
      return Response("No quote associated with the request found.", status=400)

    is_valid = check_params_validity(params, quote)
    if isinstance(is_valid, Response):
      return is_valid

    # Check existence of FILES in the request
    if not request.FILES:
      return Response("No file sent alongside the request.", status=400)

    #TODO: Check upload status to see if files have not been already uploaded

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
      files_reference.append(added_file['cid'])

    data = {
      "quoteId": quote.quoteId,
      "nonce": params['nonce'][0],
      "signature": params['signature'][0],
      "files": files_reference
    }

    # Upload files to micro-service
    response = requests.post(
      quote.storage.url + 'upload/',
      data
    )

    if (response.status_code == 200):
      #TODO: Arrange upload codes
      quote.status = UPLOAD_CODE[4]
      quote.save()

      return Response("File upload succeeded", status=200)

    #TODO: Arrange upload codes
    quote.status = UPLOAD_CODE[5]
    quote.save()

    return Response("Looks like something failed", status=400)


class QuoteLink(APIView):
  @csrf_exempt
  def get(self, request):
    params = {**request.GET}
    quoteId = request.GET.get('quoteId')
    quote = Quote.objects.get(quoteId=quoteId)
  
    if not quote:
      return Response("No quote associated with the request found.", status=400)

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

    return Response({
      "type": quote.storage.type,
      "CID": json.loads(response.content)[0]['CID']
    })
