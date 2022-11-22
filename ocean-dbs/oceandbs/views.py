from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_str
import requests
import json
import random
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample, inline_serializer
from drf_spectacular.types import OpenApiTypes

from .serializers import StorageSerializer, QuoteSerializer
from .models import Quote, Storage, File, UPLOAD_CODE

# Info endpoint listing all available storages
class StorageList(APIView):
  @csrf_exempt
  def get(self, request, format=None):
    """
    List all available storages
    """
    storages = Storage.objects.all()
    serializer = StorageSerializer(storages, many=True)
    return Response(serializer.data, status=200)


# Quote creation endpoint
class QuoteList(APIView):

  @csrf_exempt
  @extend_schema(
    # extra parameters added to the schema
    parameters=[],
    examples=[
      OpenApiExample(
        'Request body example',
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
        }
      )
    ],
    responses={
       200: inline_serializer(
          name='Response body example',
          fields={
            'tokenAmount': serializers.IntegerField(),
            'approveAddress': serializers.CharField(),
            'chainId': serializers.IntegerField(),
            'tokenAddress': serializers.CharField(),
            'tokenAddress': serializers.CharField(),
          },
       ), 
       400: OpenApiResponse(description='Missing callsign'),
    }
  )
  def post(self, request, format=None):
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
      return Response('Chosen storage type does not exist.', status=400)

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
            'chainId': serializer.data['payment']['paymentMethod']['chainId'],
            'tokenAddress': serializer.data['tokenAddress']
          }, status=201)
      return Response(serializer.errors, status=400)
    else: return Response('Storage service response badly formatted', status=400)

# Quote detail endpoint displaying the detail of a quote, no update, no deletion for now.
class QuoteStatus(APIView):
  @csrf_exempt
  def get(self, request, quoteId):
    """
    Retrieve a quote status from the associated micro-service
    """
    try:
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


class UploadFile(APIView):
  @csrf_exempt
  def post(self, request, format="multipart"):
    params = {**request.GET}

    if not all(key in params for key in ('quoteId', 'nonce', 'signature')):
      return Response("Missing query parameters.", status=400)  

    if not request.FILES and not request.FILES['file']:
      return Response("No file sent alongside the request.", status=400)

    if request.FILES:
      quote = Quote.objects.get(quoteId= params['quoteId'][0])
      if not quote:
        return Response("No quote associated with the request found.", status=400)

      #TODO: Need to check:
      #- nonce
      #- signature
      #- if duration of the quote since it has been created is still ok
      #- Upload status to see if files have not been already uploaded
      files = []
      for file in request.FILES:
        #TODO: Forward the files to IPFS, retrieve whatever they provide us (the hash), mocked in the test
        File.objects.create(quote=quote, file=file)
        files.append('superipfshashyouknow' + str(random.randint(0,1523)))
        # print("File after save", file_saved, file_saved.quote)

      # Upload files to micro-service
      response = requests.post(
        quote.storage.url + 'upload/',
        {
          "quoteId": quote.quoteId,
          "nonce": params['nonce'][0],
          "signature": params['signature'][0],
          "files": files
        }
      )

      #TODO: Arrange upload codes
      quote.status = UPLOAD_CODE[2]
      quote.save()

      if (response.status_code == 200):
        return Response("File upload succeeded", status=200)

    return Response("Looks like something failed", status=400)