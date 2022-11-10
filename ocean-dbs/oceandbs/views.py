from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from requests.exceptions import Timeout, ConnectionError
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import StorageSerializer, QuoteSerializer
from .models import Quote, Storage

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
  def get(self, request, format=None):
    """
    POST a quote, handle different error code
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
    serializer = QuoteSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


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