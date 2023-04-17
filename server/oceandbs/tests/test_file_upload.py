from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from django.core.files import File
from oceandbs.models import File as DBSFile, Quote, UPLOAD_CODE
from ..utils import generate_signature
import mock
import responses
from django.conf import settings

image_mock = mock.MagicMock(spec=File)
image_mock.name = 'image.png'

image2_mock = mock.MagicMock(spec=File)
image2_mock.name = 'image2.png'

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestFileUploadEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  @responses.activate
  def test_file_upload(self):
    signature = generate_signature(123565, 1768214571, getattr(settings, 'TEST_PRIVATE_KEY', ''))
    responses.add_passthru('https://rpc-mumbai.maticvigil.com/')
    
    # Mock call to IPFS for temporary file storage
    responses.post(
      url= 'http://127.0.0.1:5001/api/v0/add',
      body='{"Name":"image.png","Hash":"QmPmnyA8ZaYFJknPhVBE1u4hbGqvLGvu5cxCAPb1Nqb1aq","Size":"59"}\n{"Name":"image2.png","Hash":"QmUq54U3BVx9vSKRSNVoSCoLD9wBkeDXrzK7FqRgdgnCGK","Size":"59"}',
      status=200
    )

    # Mock call to Storage Service for actual file storage
    responses.post(
      url= 'https://filecoin.org/upload/',
      status=200
    )

    response = self.client.post(
      '/upload?quoteId=123565&nonce=1768214571&signature=' + str(signature.signature.hex()),
      {'file1':image_mock, 'file2':image2_mock},
      format="multipart"
    )

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(response.data, "File upload succeeded.")

    self.assertEqual(len(DBSFile.objects.all()), 2)
    self.assertEqual(len(Quote.objects.all()), 1)

    file = DBSFile.objects.first()
    self.assertIsNotNone(file.cid)
    self.assertIsNotNone(file.public_url)

    quote = Quote.objects.first()
    files = DBSFile.objects.filter(quote=quote)
    self.assertEqual(len(files), 2)
    self.assertEqual(quote.status, str(UPLOAD_CODE[5][0]))