from datetime import datetime
import hashlib
import json
import requests

from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
import mimetypes

from web3.auto import w3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.messages import encode_defunct
from requests.exceptions import RequestException

from .models import File

# This function is used to upload the files temporarily to IPFS

def upload_files_to_ipfs(request_files, quote):
    files_reference = []
    url = getattr(settings, 'IPFS_SERVICE_ENDPOINT') or "http://127.0.0.1:5001/api/v0/add"
    print('IPFS URL: ', url)

    # Preparing files with appropriate content type
    file_data = {}
    for field_name, uploaded_file in request_files.items():
        print(f"Processing file '{uploaded_file}'.")
        content_type, _ = mimetypes.guess_type(uploaded_file.name)
        if content_type:
            print(f"Guessed MIME type '{content_type}' for file '{uploaded_file.name}'.")
            file_data[field_name] = (uploaded_file.name, uploaded_file, content_type)
        else:
            print(f"Could not guess MIME type for file '{uploaded_file.name}'. Using default.")
            file_data[field_name] = uploaded_file

    try:
        response = requests.post(url, files=file_data)
        response.raise_for_status()  # This will raise an error for HTTP error responses
        
        files = response.text.splitlines()
        for file in files:
            added_file = {}
            json_version = json.loads(file)
            added_file['title'] = json_version['Name']
            print(f"File '{added_file['title']}' uploaded successfully to IPFS. {json_version['Name']}")
            added_file['cid'] = json_version['Hash']
            added_file['public_url'] = f"https://ipfs.io/ipfs/{added_file['cid']}?filename={added_file['title']}"
            added_file['length'] = json_version['Size']
            added_file['content_type'] = file_data[json_version['Name']][2]  # Add the content type from file_data
            File.objects.create(quote=quote, **added_file)
            files_reference.append({
                "ipfs_uri": "ipfs://" + str(added_file['cid']),
                "content_type": added_file['content_type']
            })

    except requests.RequestException as e:
        print(f"HTTP error uploading to IPFS: {e}")
        raise ValueError(f"HTTP error uploading to IPFS: {e}")

    except Exception as e:
        print(f"Error processing the uploaded files: {e}")
        raise ValueError(f"Error processing the uploaded files: {e}")

    return files_reference

# The function below is used to generate an allowance for the file upload
def create_allowance(quote, user_private_key, abi):
    if not all([quote, user_private_key, abi]):
        missing_args = []
        if not quote:
            missing_args.append("quote")
        if not user_private_key:
            missing_args.append("user_private_key")
        if not abi:
            missing_args.append("abi")
        print(f"Missing or null arguments: {', '.join(missing_args)}")
        return Response(f"Error: Missing or null arguments: {', '.join(missing_args)}", status=400)
    
    try:
        rpcProvider = quote.payment.paymentMethod.rpcEndpointUrl
    except (ObjectDoesNotExist, AttributeError) as e:
        print("RPC endpoint not found, using default one.", e)
        rpcProvider = "https://rpc-mumbai.maticvigil.com"

    try:
        my_provider = Web3.HTTPProvider(rpcProvider)
        w3 = Web3(my_provider)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        abi = json.loads(abi)

        contractAddress = w3.toChecksumAddress(quote.tokenAddress)
        contract = w3.eth.contract(contractAddress, abi=abi)

        userAddress = w3.toChecksumAddress(quote.payment.userAddress)
        approvalAddress = w3.toChecksumAddress(quote.approveAddress)
        nonce = w3.eth.get_transaction_count(userAddress)
        tx_hash = contract.functions.approve(approvalAddress, quote.tokenAmount).buildTransaction({
            'from': userAddress, 'nonce': nonce})
        signed_tx = w3.eth.account.signTransaction(tx_hash, user_private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    except ValueError as e: # specific to Web3
        print(f"Web3 ValueError: {e}")
        return Response(f"Web3 Error: {e}", status=400)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return Response(f"Unexpected error: {e}", status=500)
    
    print(f"Transaction completed successfully")
    return Response("Transaction completed successfully.", status=200)


# This function is used to upload the files to the target microservice
def upload_files_to_microservice(quote, params, files_reference):
    
    # Initial data validations
    if not quote or not hasattr(quote, 'storage') or not hasattr(quote.storage, 'url') or not hasattr(quote, 'quoteId'):
        raise ValueError("Invalid quote object provided.")
    
    if not params or 'nonce' not in params or 'signature' not in params:
        raise ValueError("Invalid params provided.")
    
    data = {
        "quoteId": quote.quoteId,
        "nonce": params['nonce'][0],
        "signature": params['signature'][0],
        "files": files_reference
    }

    url = quote.storage.url + 'upload/?quoteId=' + str(quote.quoteId) + '&nonce=' + data['nonce'] + '&signature=' + data['signature']

    try:
        print(f"Sending request to microservice url: {url}")
        response = requests.post(url, data)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except RequestException as e:
    # Extract more detailed message from the response content, if available
        detailed_message = e.response.text if hasattr(e, 'response') and hasattr(e.response, 'text') else "No detailed message provided."
        raise RuntimeError(f"Error occurred while making the request: {str(e)}. Detailed message: {detailed_message}")
    except Exception as e:  # Catches any unforeseen exceptions
        raise RuntimeError(f"Unexpected error occurred: {str(e)}")

    return response

# This function is used to generate the signature for every request
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
  if quote.created > timezone.now() + timezone.timedelta(minutes=30):
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
