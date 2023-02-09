import hashlib
import sys, getopt
# from web3.auto import w3
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

def main(argv):
  print("Script running")
  #  try:
  #     opts, args = getopt.getopt(argv,"hq:n:k:",["quoteId=","nonce=", "pkey="])
  #  except getopt.GetoptError:
  #     print ('signature.py -q <quoteId> -n <nonce> -k <pkey>')
  #     sys.exit(2)

  #  for opt, arg in opts:
  #     if opt == '-h':
  #        print ('signature.py -q <quoteId> -n <nonce> -k <pkey>')
  #        sys.exit()
  #     elif opt in ("-q", "--quoteId"):
  #        quoteId = arg
  #     elif opt in ("-n", "--nonce"):
  #        nonce = arg
  #     elif opt in ("-k", "--pkey"):
  #        pkey = arg
  my_provider = Web3.HTTPProvider("https://rpc-mumbai.maticvigil.com/")
  w3 = Web3(my_provider)
  w3.middleware_onion.inject(geth_poa_middleware, layer=0)

  print(w3.isConnected())
  # Creating allowance for funds transfer from my user address to the quote paymentAddress
  print("ApproveAddress:" + '0xAFcE990754C38Be5E0C341707B2A162C4e67547B')
  approvalAddress = '0xAFcE990754C38Be5E0C341707B2A162C4e67547B'
  tokenAddress = '0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889'
  userAddress = '0xCC866199C810B216710A3F3714d35920C343a8CD'
  print("TokenAddress:" + tokenAddress)
  abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]'
  abi = json.loads(abi)
  contractAddress = w3.toChecksumAddress(tokenAddress)
  contract = w3.eth.contract(contractAddress, abi=abi)
  
  print(contract.functions.totalSupply().call())

  userAddress = w3.toChecksumAddress(userAddress)
  print('userAddress', userAddress)
  approvalAddress = w3.toChecksumAddress(approvalAddress)
  print('approvalAddress', approvalAddress)
  print("Contract Instanciated:" + str(contract))
  print('Balance of contractAddress:' + str(contract.functions.balanceOf(tokenAddress).call()))
  print('Balance of apporvalAddress:' + str(contract.functions.balanceOf(approvalAddress).call()))
  print('Balance of userAddress:' + str(contract.functions.balanceOf(userAddress).call()))
  nonce = w3.eth.getTransactionCount(userAddress)
  # w3.eth.accounts.signTransaction(tx, privateKey).then(signed => {
  tx_hash = contract.functions.approve(approvalAddress, 123456).buildTransaction({'from': userAddress, 'nonce': nonce})
    # tx = token.functions.approve(spender, max_amount).buildTransaction({
    #   'from': wallet_address, 
    #   'nonce': nonce
    #   })
  signed_tx = w3.eth.account.signTransaction(tx_hash, 'bbb5a2d50f3956e72dd8f38096270d8d951e44da623b1e31422d724e5841c93f')
  tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

  print("Approval:" + str(tx_hash))
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
  print("TransactionReceipt:" + str(tx_receipt))
  print("ContractAllowance:" + str(contract.functions.allowance(userAddress, approvalAddress).call()))

if __name__ == "__main__":
   main(sys.argv[1:])
