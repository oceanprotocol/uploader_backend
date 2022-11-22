from django.conf import settings
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.utils import json
import responses

# Using the standard RequestFactory API to create a form POST request
class TestGetQuoteEndpoint(APITestCase):
  fixtures = ['storages.json']

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  def test_get_quotes_endpoint(self):
    response = self.client.get('/quotes/')

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, 200)

    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 1)
    
    # Assert content of the response itself, pure JSON
    # self.assertEqual(response.data['content'], '')
  
  @responses.activate
  def test_quote_creation(self):
    body = {
      "type": "filecoin",
      "files": [
        {"length":2343545},
        {"length":2343545}
      ],
      "duration": 4353545453,
      "payment": {
          "payment_method": {
            "chain_id": 1,
          },
          "wallet_address": "0xOCEAN_on_MAINNET"
      },
      "userAddress": "0x456"
    }

    responses.post(
        url=settings.FILECOIN_SERVICE_URL + '/getQuote/',
        json={
        'tokenAmount': 500,
        'approveAddress': '0x123',
        'chainId': 1,
        'tokenAddress': '0xOCEAN_on_MAINNET',
        'quoteId': 'xxxx'
      },
      status=200
    )

    response = self.client.post(
      '/quotes/',
      data=json.dumps(body),
      content_type='application/json'
    )

    self.assertEqual(response.status_code, 200)
    self.assertNotEqual(response.status_code, 400)

    # print(response.data)

    self.assertEqual(len(response.data), 5)
    self.assertExists(response.data['tokenAmount'])
    self.assertExists(response.data['approveAddress'])
    self.assertExists(response.data['chainId'])
    self.assertExists(response.data['tokenAddress'])
    self.assertExists(response.data['quoteId'])