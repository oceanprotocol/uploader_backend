from django.conf import settings
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework.utils import json
import responses
from oceandbs.models import File, Quote, Payment, PaymentMethod

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
    self.assertEqual(response.data[0]['duration'], 2380293823)
    self.assertEqual(response.data[0]['tokenAddress'], '0xOCEAN_on_MAINNET')
    self.assertEqual(response.data[0]['approveAddress'], '0x123')

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
            "chainId": 1,
          },
          "wallet_address": "0xOCEAN_on_MAINNET"
      },
      "userAddress": "0x456"
    }

    responses.post(
        url= 'https://filecoin.org/getQuote/',
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

    print(response.data)
    self.assertEqual(response.status_code, 201)
    self.assertNotEqual(response.status_code, 400)

    self.assertEqual(len(response.data), 5)
    self.assertIsNotNone(response.data['tokenAmount'])
    self.assertIsNotNone(response.data['approveAddress'])
    self.assertIsNotNone(response.data['chainId'])
    self.assertIsNotNone(response.data['tokenAddress'])
    self.assertIsNotNone(response.data['quoteId'])

    self.assertEqual(len(File.objects.all()), 2)
    self.assertEqual(len(Quote.objects.all()), 2)

  @responses.activate
  def test_quote_creation_no_type(self):
    body = {
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

    response = self.client.post(
      '/quotes/',
      data=json.dumps(body),
      content_type='application/json'
    )

    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data, 'Invalid input data.')

  @responses.activate
  def test_quote_creation_type_mismatch(self):
    body = {
      "type": "totoro",
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

    response = self.client.post(
      '/quotes/',
      data=json.dumps(body),
      content_type='application/json'
    )

    self.assertEqual(response.status_code, 400)
    self.assertEqual(response.data, 'Chosen storage type does not exist.')