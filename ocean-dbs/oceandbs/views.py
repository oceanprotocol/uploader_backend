from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_str
import requests
import json

from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response

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
  def get(self, request, format=None):
    """
    GET the quote list, handle different error code
    """
    quotes = Quote.objects.all()
    serializer = QuoteSerializer(quotes, many=True)
    return Response(serializer.data, status=200)

  @csrf_exempt
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
class QuoteDetail(APIView):
  @csrf_exempt
  def get(request, pk):
    """
    Retrieve a quote
    """
    try:
      quote = Quote.objects.get(pk=pk)
    except Quote.DoesNotExist:
      return HttpResponse(status=404)

    serializer = QuoteSerializer(quote)
    return Response(serializer.data)

class UploadFile(APIView):
  @csrf_exempt
  def post(self, request, format="multipart"):
    params = {**request.GET}
    print(params)

    if not all(key in params for key in ('quoteId', 'nonce', 'signature')):
      return Response("Missing query parameters.", status=400)  

    if not request.FILES and not request.FILES['file']:
      return Response("No file sent alongside the request.", status=400)

    if request.FILES:
      print(params['quoteId'])
      quote = Quote.objects.get(quoteId= params['quoteId'][0])
      if not quote:
        return Response("No quote associated with the request found.", status=400)

      #TODO: Need to check:
      #- nonce
      #- signature
      #- if duration of the quote since it has been created is still ok
      #- Upload status to see if files have not been already uploaded
      for file in request.FILES:
        #TODO: Forward the files to IPFS, retrieve whatever they provide us (the hash), mocked in the test
        print(file)
        file_saved = File.objects.create(quote=quote, file=file)
        print("File after save", file_saved, file_saved.quote)

      quote.upload_status = UPLOAD_CODE[2]
      quote.save()

    return Response("Everything's fine", status=200)