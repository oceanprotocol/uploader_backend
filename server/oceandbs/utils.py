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
    content_types = {}  # New dictionary for content types

    for field_name, uploaded_file in request_files.items():
        print(f"Processing file '{uploaded_file}'.")
        content_type, _ = mimetypes.guess_type(uploaded_file.name)
        if content_type:
            print(f"Guessed MIME type '{content_type}' for file '{uploaded_file.name}'.")
            content_types[uploaded_file.name] = content_type  # Save the content type in the new dictionary
        else:
            print(f"Could not guess MIME type for file '{uploaded_file.name}'. Using default.")
        
        file_data[field_name] = uploaded_file  # Always store the uploaded_file in file_data

    try:
        response = requests.post(url, files=file_data)
        response.raise_for_status()  # This will raise an error for HTTP error responses
        
        print("Processing files from IPFS response...")
        print("Raw IPFS response:", response.text)  # Print the raw response

        files = response.text.splitlines()
        for file in files:
            added_file = {}
            try:
                json_version = json.loads(file)
                print(f"JSON response for file: {json_version}")  # Print the JSON response for each file

                # Check if 'Name' is in the json_version before proceeding
                if 'name' in json_version:
                    added_file['title'] = json_version['name']
                    print(f"File '{added_file['title']}' uploaded successfully to IPFS. {json_version['name']}")
                    added_file['cid'] = json_version['cid']
                    added_file['public_url'] = f"https://ipfs.io/ipfs/{added_file['cid']}?filename={added_file['title']}"
                    added_file['length'] = json_version['size']

                    content_type_retrieved = content_types.get(json_version['name'], None)
                    print(f"Content type for file '{added_file['title']}' is '{content_type_retrieved}'.")
                    print(f"Saving file '{added_file['title']}' to the database...")
                    File.objects.create(quote=quote, **added_file)
                    print(f"File '{added_file['title']}' saved successfully to the database.")

                    files_reference.append({
                        "ipfs_uri": "ipfs://" + str(added_file['cid']),
                        "content_type": content_type_retrieved
                    })
                else:
                    print("Warning: 'name' key not found in the IPFS response.")
            except json.JSONDecodeError:
                print(f"Error parsing IPFS response for file '{file}'. Invalid JSON received.")
                continue
            
    except requests.RequestException as e:
        print(f"HTTP error uploading to IPFS: {e}")
        raise ValueError(f"HTTP error uploading to IPFS: {e}")

    except Exception as e:
        print(f"Error processing the uploaded files: {e}")
        raise ValueError(f"Error processing the uploaded files: {e}")

    print(f"files_reference: {files_reference}")
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
        error_message = "Invalid quote object provided."
        print(error_message)
        raise ValueError(error_message)
    
    if not params or 'nonce' not in params or 'signature' not in params:
        error_message = "Invalid params provided."
        print(error_message)
        raise ValueError(error_message)
    
    data = {
        "quoteId": quote.quoteId,
        "nonce": params['nonce'][0],
        "signature": params['signature'][0],
        "files": files_reference
    }

    url = quote.storage.url + 'upload/?quoteId=' + str(quote.quoteId) + '&nonce=' + data['nonce'] + '&signature=' + data['signature']

    headers = {'Content-Type': 'application/json'}

    print(f"Preparing to send data to microservice: {data}")
    print(f"Sending request to microservice url: {url}")

    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()
    except RequestException as e:
        detailed_message = e.response.text if hasattr(e, 'response') and hasattr(e.response, 'text') else "No detailed message provided."
        error_message = f"Error occurred while making the request: {str(e)}. Detailed message: {detailed_message}"
        print(error_message)
        raise RuntimeError(error_message)
    except Exception as e:
        error_message = f"Unexpected error occurred: {str(e)}"
        print(error_message)
        raise RuntimeError(error_message)

    print(f"Received response from microservice with status code: {response.status_code}")
    if response.status_code != 200:
        print(f"Response content: {response.text}")

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
