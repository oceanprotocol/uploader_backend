import hashlib
import sys, getopt
from web3.auto import w3
from eth_account.messages import encode_defunct

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

   message = "0x" + hashlib.sha256((str(quoteId) + str(nonce)).encode('utf-8')).hexdigest()
   print(message)
   message = encode_defunct(text=message)
   print(message)
   # Use signMessage from web3 library and etheurem decode_funct to generate the signature
   signed_message = w3.eth.account.sign_message(message, private_key=pkey)

   # sha256_hash = hashlib.sha256((quoteId + nonce).encode('utf-8')).hexdigest()
   print(signed_message)

if __name__ == "__main__":
   main(sys.argv[1:])
