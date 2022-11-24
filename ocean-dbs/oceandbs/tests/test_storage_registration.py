from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase, RequestsClient
import responses
import json

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestStorageRegistrationEndpoint(APITestCase):
  # fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  @responses.activate
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
    # For arweave it would be a transaction ID so the tests should be different
    response = self.client.post(  
      '/storages/', 
      data=json.dumps(body),
      content_type='application/json'
    )
    print(response.content)
    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    # Assert content of the response itself, pure JSON
    self.assertEqual(response.data, 'Desired storage created.')
    