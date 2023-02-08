from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import hashlib
from web3.auto import w3
from eth_account.messages import encode_defunct

def check_params_validity(params, quote):
  if not all(key in params for key in ('nonce', 'signature')):
    return Response("Missing query parameters.", status=400)

  # Check expiration date of the quote vs current date
  if quote.expiration < timezone.now():
    return Response("Quote already expired, please create a new one.", status=400)

  # Check nonce
  if str(round(quote.nonce.timestamp())) > params['nonce'][0]:
    return Response("Nonce value invalid.", status=400)

  message = str(quote.quoteId) + str(params['nonce'][0])
  message = encode_defunct(text=message)
  # Use verifyMessage from web3/ethereum API
  check_signature = w3.eth.account.recover_message(message, signature=params['signature'][0])

  if check_signature:
    quote.nonce = datetime.fromtimestamp(int(params['nonce'][0]), timezone.utc)
    quote.save()

    return True
  # Then decode message and
  # Check signature
  # sha256_hash = hashlib.sha256(str(quote.quoteId) + str(params['nonce'][0]))
  # if not sha256_hash == params['signature'][0]:
  #   return Response("Invalid signature.", status=400)
  return False
