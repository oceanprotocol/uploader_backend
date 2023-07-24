import sys, getopt
sys.path.append('..')
import hashlib

from web3.auto import w3
from web3.middleware import geth_poa_middleware
from eth_account.messages import encode_defunct

# This function is used to generate the signature for every request
def generate_signature(quoteId, nonce, pkey):
  message = "0x" + hashlib.sha256((str(quoteId) + str(nonce)).encode('utf-8')).hexdigest()
  message = encode_defunct(text=message)
  # Use signMessage from web3 library and etheurem decode_funct to generate the signature
  signed_message = w3.eth.account.sign_message(message, private_key=pkey)
  return signed_message

def main(argv):
   quoteId = ''
   nonce = ''
   pkey = ''
   print("Script running")
   try:
      opts, args = getopt.getopt(argv,"hq:n:k:",["quoteId=","nonce=", "pkey="])
   except getopt.GetoptError:
      print ('signature.py -q <quoteId> -n <nonce> -k <pkey>')
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print ('signature.py -q <quoteId> -n <nonce> -k <pkey>')
         sys.exit()
      elif opt in ("-q", "--quoteId"):
         quoteId = arg
      elif opt in ("-n", "--nonce"):
         nonce = arg
      elif opt in ("-k", "--pkey"):
         pkey = arg

   signature = generate_signature(quoteId, nonce, pkey)

   print("Signature:", signature.signature.hex())
   print("Nonce:", str(nonce))

if __name__ == "__main__":
   main(sys.argv[1:])
