import hashlib
import sys, getopt

def main(argv):
    quoteId = ''
    nonce = ''
    try:
      opts, args = getopt.getopt(argv,"hq:n:",["quoteId=","nonce="])
    except getopt.GetoptError:
      print ('signature.py -q <quoteId> -n <nonce>')
      sys.exit(2)
    
    for opt, arg in opts:
      if opt == '-h':
         print ('signature.py -q <quoteId> -n <nonce>')
         sys.exit()
      elif opt in ("-q", "--quoteId"):
         quoteId = arg 
      elif opt in ("-n", "--nonce"):
         nonce = arg

    sha256_hash = hashlib.sha256((quoteId + nonce).encode('utf-8')).hexdigest()
    print(sha256_hash)

if __name__ == "__main__":
   main(sys.argv[1:])
