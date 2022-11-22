from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
# Create your tests here.

# Using the standard RequestFactory API to create a form POST request
class TestGetQuoteEndpoint(APITestCase):
  fixtures = ['storages.json']

  def setUp(self):
    self.factory = APIRequestFactory()
    self.client = APIClient()

  def test_get_info_endpoint(self):
    response = self.client.get('/quotes/')

    # Assert proper HTTP status code
    self.assertEqual(response.status_code, 200)

    # Assert content of the response itself, pure JSON
    self.assertEqual(len(response.data), 1)
    
    # Assert content of the response itself, pure JSON
    # self.assertEqual(response.data['content'], '')

