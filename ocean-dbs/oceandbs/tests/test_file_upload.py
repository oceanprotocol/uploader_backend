from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from django.core.files import File
from oceandbs.models import File as DBSFile, Quote
from pathlib import Path
import tempfile
import mock
import json
import random
from django.utils.encoding import force_str
import responses

image_mock = mock.MagicMock(spec=File)
image_mock.name = 'image.png'

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestFileUploadEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()
  
  @responses.activate
  def test_file_upload(self):
    #TODO: Mock call to IPFS for temporary file storage
    responses.post(
      url= 'http://localhost:5001/api/v0/',
      body="ipfs://superfilewithhashstoredonipfs" + str(random.randint(0,1523)),
      status=200
    )

    #TODO: Mock call to Storage Service for actual file storage
    responses.post(
      url= 'https://filecoin.org/upload/',
      status=200
    )

    response = self.client.post(
      '/quote/123565/upload?nonce=1669286323&signature=ffcdc15308e195bbf3d9eb9af1a6a4f37dc9aba72e620dbbd1dffa634e897d46',
      {'file1':image_mock, 'file2':image_mock},
      format="multipart"
    )
    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(response.data, "File upload succeeded")

    self.assertEqual(len(DBSFile.objects.all()), 2)
    self.assertEqual(len(Quote.objects.all()), 1)

    quote = Quote.objects.first()
    files = DBSFile.objects.filter(quote=quote)
    self.assertEqual(len(files), 2)
