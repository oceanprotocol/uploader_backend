import os

from eth_account import Account
from rest_framework.test import APIRequestFactory, APIClient, APITestCase
import responses

from server.oceandbs.utils import generate_signature
from django.conf import settings


# Create your tests here.
# Using the standard RequestFactory API to create a form POST request
class TestGetHistoryEndpoint(APITestCase):
    fixtures = ["storages.json"]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

    @responses.activate
    def test_get_history_endpoint(self):
        private_key = os.environ.get("TEST_PRIVATE_KEY")
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key

        account = Account.from_key(private_key)
        signature = generate_signature(123565, 1768214571, getattr(settings, 'TEST_PRIVATE_KEY', ''))
        responses.add_passthru('https://rpc-mumbai.maticvigil.com/')

        # For arweave it would be a transaction ID so the tests should be different
        response = self.client.get(
            f'http://localhost:8000/getHistory?userAddress={account.address}&nonce=1768214571&signature=' + str(signature.signature.hex()))

        print(response)
