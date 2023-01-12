from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from oceandbs.models import Storage, PaymentMethod, AcceptedToken
import json

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestStorageRegistrationEndpoint(APITestCase):
  # fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  def test_post_storage(self):
    body = {
      "type": "filecoin",
      "description":  "File storage on FileCoin",
      "url": "http://microservice.url",
      "paymentMethods":[
        {
          "chainId": "1",
          "acceptedTokens": [
            {
              "OCEAN": "0xOCEAN_on_MAINNET"
            },
            {
              "DAI": "0xDAI_ON_MAINNET"
            }
          ]
        },
        {
          "chainId": "polygon_chain_id",
          "acceptedTokens": [
            {
              "OCEAN": "0xOCEAN_on_POLYGON" 
            },
            {
              "DAI": "0xDAI_ON_POLYGON"
            }
          ]
        }
      ]
    }

    # The actual request to create a new storage service
    response = self.client.post(  
      '/register', 
      data=json.dumps(body),
      content_type='application/json'
    )

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    # Assert content of the response itself, pure JSON
    self.assertEqual(response.data, 'Desired storage created.')

    storage = Storage.objects.first()
    self.assertEqual(storage.type, 'filecoin')

    payment_methods = PaymentMethod.objects.filter(storage=storage)
    self.assertEqual(len(payment_methods), 2)

    accepted_tokens = AcceptedToken.objects.all()
    self.assertEqual(len(accepted_tokens), 4)

    self.assertEqual(payment_methods[0].chainId, "1")

    accepted_tokens = AcceptedToken.objects.filter(paymentMethod=payment_methods[0])
    self.assertEqual(len(accepted_tokens), 2)
    self.assertEqual(accepted_tokens[0].title, 'OCEAN')
    self.assertEqual(accepted_tokens[0].value, '0xOCEAN_on_MAINNET')

    self.assertEqual(accepted_tokens[1].title, 'DAI')
    self.assertEqual(accepted_tokens[1].value, '0xDAI_ON_MAINNET')

    self.assertEqual(payment_methods[1].chainId, "polygon_chain_id")
    accepted_tokens = AcceptedToken.objects.filter(paymentMethod=payment_methods[1])
    self.assertEqual(len(accepted_tokens), 2)
    self.assertEqual(accepted_tokens[0].title, 'OCEAN')
    self.assertEqual(accepted_tokens[0].value, '0xOCEAN_on_POLYGON')

    self.assertEqual(accepted_tokens[1].title, 'DAI')
    self.assertEqual(accepted_tokens[1].value, '0xDAI_ON_POLYGON')
    