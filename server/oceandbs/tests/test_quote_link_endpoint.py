from django.conf import settings

from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase, RequestsClient
import responses
from ..utils import generate_signature

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestLinkEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  @responses.activate
  def test_get_link_endpoint(self):
    signature = generate_signature(123565, 1768214571, getattr(settings, 'TEST_PRIVATE_KEY', ''))
    responses.add_passthru('https://rpc-mumbai.maticvigil.com/')
    
    responses.get(
      url= 'https://filecoin.org/getLink?quoteId=123565&nonce=1768214571&signature=' + str(signature.signature.hex()),
      json=[
        {
          "type": "filecoin",
          "CID": "xxxx",
        }
      ],
      status=200
    )

    # For arweave it would be a transaction ID so the tests should be different
    response = self.client.get('/getLink?quoteId=123565&nonce=1768214571&signature=' + str(signature.signature.hex()))

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 2)
    self.assertIsNotNone(response.data['type'])
    self.assertEqual(response.data['type'], 'filecoin')
    self.assertIsNotNone(response.data['CID'])
    self.assertEqual(response.data['CID'], 'xxxx')
