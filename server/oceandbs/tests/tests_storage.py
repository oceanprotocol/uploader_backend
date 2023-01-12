from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, APITestCase, RequestsClient

# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestInfoEndpoint(APITestCase):
  fixtures = ["storages.json"]

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  def test_get_info_endpoint(self):
    response = self.client.get('/storages/')
    # Assert proper HTTP status code
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 1)

    self.assertEqual(response.data[0]['type'], 'filecoin')
    self.assertEqual(response.data[0]['description'], 'The file coin storage description.')
