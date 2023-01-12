from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase, RequestsClient
import responses

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestLinkEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  @responses.activate
  def test_get_link_endpoint(self):
    responses.get(
      url= 'https://filecoin.org/getLink?quoteId=123565&nonce=1768214571&signature=0ee382b39a39e05500d99233cdca83cd9959be4ff557ce7f3f29c9ce99d3b5de',
      json=[
        {
          "type": "filecoin",
          "CID": "xxxx",
        }
      ],
      status=200
    )

    # For arweave it would be a transaction ID so the tests should be different
    response = self.client.get('/getLink?quoteId=123565&nonce=1768214571&signature=0ee382b39a39e05500d99233cdca83cd9959be4ff557ce7f3f29c9ce99d3b5de')

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 2)
    self.assertIsNotNone(response.data['type'])
    self.assertEqual(response.data['type'], 'filecoin')
    self.assertIsNotNone(response.data['CID'])
    self.assertEqual(response.data['CID'], 'xxxx')
