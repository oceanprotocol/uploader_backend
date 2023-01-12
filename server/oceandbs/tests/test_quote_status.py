from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase, RequestsClient
import responses

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestQuoteStatusEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  @responses.activate
  def test_quote_status_endpoint(self):
    responses.get(
      url= 'https://filecoin.org/quote/123565',
      json={
        'status': 200
      },
      status=200
    )

    response = self.client.get('/getStatus?quoteId=123565')
    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 1)

    self.assertEqual(response.data['status'], 200)
