from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from django.core.files import File
from oceandbs.models import File as DBSFile, Quote
from pathlib import Path
import tempfile
import mock
import responses
import json
import random
from django.utils.encoding import force_str

image_mock = mock.MagicMock(spec=File)
image_mock.name = 'image.png'

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestFileUploadEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  def test_file_upload(self):
    #TODO: Mock call to IPFS for actual file storage
    responses.post(
      url= 'http://localhost:5001/api/v0/',
      body="ipfs://superfilewithhashstoredonipfs" + str(random.randint(0,1523)),
      status=200
    )

    response = self.client.post(
      '/upload/?quoteId=123565&nonce=1&signature=xxxxx',
      {'file1':image_mock, 'file2':image_mock},
      format="multipart"
    )
    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(response.data, "Everything's fine")

    self.assertEqual(len(DBSFile.objects.all()), 2)
    self.assertEqual(len(Quote.objects.all()), 1)

    quote = Quote.objects.first()
    files = DBSFile.objects.filter(quote=quote)
    print("Given quote", quote, quote.quoteId)
    print(files)
    self.assertEqual(len(files), 2)
