import sys, getopt
sys.path.append('..')
from utils import generate_signature

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
