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
      url= 'https://filecoin.org/quote/123565/link?nonce=1669286323&signature=ffcdc15308e195bbf3d9eb9af1a6a4f37dc9aba72e620dbbd1dffa634e897d46',
      json=[
        {
          "type": "filecoin",
          "CID": "xxxx",
        }
      ],
      status=200
    )

    # For arweave it would be a transaction ID so the tests should be different
    response = self.client.get('/quote/123565/link?nonce=1669286323&signature=ffcdc15308e195bbf3d9eb9af1a6a4f37dc9aba72e620dbbd1dffa634e897d46')

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 2)
    self.assertIsNotNone(response.data['type'])
    self.assertEqual(response.data['type'], 'filecoin')
    self.assertIsNotNone(response.data['CID'])
    self.assertEqual(response.data['CID'], 'xxxx')
