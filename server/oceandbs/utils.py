from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import hashlib
from web3.auto import w3
from eth_account.messages import encode_defunct

def generate_signature(quoteId, nonce, pkey):
  message = "0x" + hashlib.sha256((str(quoteId) + str(nonce)).encode('utf-8')).hexdigest()
  message = encode_defunct(text=message)
  
  # Use signMessage from web3 library and etheurem decode_funct to generate the signature
  signed_message = w3.eth.account.sign_message(message, private_key=pkey)
  return signed_message


def check_params_validity(params, quote):
  if not all(key in params for key in ('nonce', 'signature')):
    return Response("Missing query parameters.", status=400)

  # Check expiration date of the quote vs current date
  if quote.expiration < timezone.now():
    return Response("Quote already expired, please create a new one.", status=400)

  # Check nonce
  if str(round(quote.nonce.timestamp())) > params['nonce'][0]:
    return Response("Nonce value invalid.", status=400)

  message = "0x" + hashlib.sha256((str(quote.quoteId) + str(params['nonce'][0])).encode('utf-8')).hexdigest()
  message = encode_defunct(text=message)
  
  # Use verifyMessage from web3/ethereum API
  check_signature = w3.eth.account.recover_message(message, signature=params['signature'][0])

  if check_signature:
    quote.nonce = datetime.fromtimestamp(int(params['nonce'][0]), timezone.utc)
    quote.save()

    return True

  return False
