import hashlib
import sys, getopt
# from web3.auto import w3
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

def main(argv):
  approvalAddress = ''
  tokenAddress = ''
  userAddress = ''

  print("Script running")
  try:
    opts, args = getopt.getopt(argv,"ha:t:u:",["approvalAddress=","tokenAddress=", "userAddress="])
  except getopt.GetoptError:
    print ('signature.py -a <approvalAddress> -t <tokenAddress> -u <userAddress>')
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
        print ('signature.py -a <approvalAddress> -t <tokenAddress> -u <userAddress>')
        sys.exit()
    elif opt in ("-a", "--approvalAddress"):
        approvalAddress = arg
    elif opt in ("-t", "--tokenAddress"):
        tokenAddress = arg
    elif opt in ("-u", "--userAddress"):
        userAddress = arg

  my_provider = Web3.HTTPProvider("https://rpc-mumbai.maticvigil.com/")
  w3 = Web3(my_provider)
  w3.middleware_onion.inject(geth_poa_middleware, layer=0)

  # Creating allowance for funds transfer from my user address to the quote paymentAddress
  abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'
  abi = json.loads(abi)
  contractAddress = w3.toChecksumAddress(tokenAddress)
  contract = w3.eth.contract(contractAddress, abi=abi)
  print("Contract total supply:", contract.functions.totalSupply().call())

  userAddress = w3.toChecksumAddress(userAddress)
  approvalAddress = w3.toChecksumAddress(approvalAddress)
  print("Contract Instanciated:" + str(contract))
  nonce = w3.eth.getTransactionCount(userAddress)
  tx_hash = contract.functions.approve(approvalAddress, 123456).buildTransaction({'from': userAddress, 'nonce': nonce})
  signed_tx = w3.eth.account.signTransaction(tx_hash, 'bbb5a2d50f3956e72dd8f38096270d8d951e44da623b1e31422d724e5841c93f')
  tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

  print("Approval transaction hash:" + str(tx_hash))
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
  print("Transaction receipt:" + str(tx_receipt))
  print("Contract allowance:" + str(contract.functions.allowance(userAddress, approvalAddress).call()))

if __name__ == "__main__":
   main(sys.argv[1:])
