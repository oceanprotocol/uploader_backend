from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
import hashlib


def check_params_validity(params, quote):
  if not all(key in params for key in ('nonce', 'signature')):
    return Response("Missing query parameters.", status=400)

  # Check expiration date of the quote vs current date
  if quote.expiration < timezone.now():
    return Response("Quote already expired, please create a new one.", status=400)

  # Check nonce
  if not str(round(quote.nonce.timestamp())) < params['nonce'][0]:
    return Response("Nonce value invalid.", status=400)

  # Check signature
  sha256_hash = hashlib.sha256((str(quote.quoteId) + str(params['nonce'][0])).encode('utf-8')).hexdigest()
  if not sha256_hash == params['signature'][0]:
    return Response("Invalid signature.", status=400)

  quote.nonce = datetime.fromtimestamp(int(params['nonce'][0]), timezone.utc)
  quote.save()

  return True
