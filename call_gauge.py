from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Infura URL from environment variable
infura_url = f'https://mainnet.infura.io/v3/{os.getenv("INFURA_API_KEY")}'
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if the connection is successful
print("Is Connected:", web3.is_connected())

# Gauge contract address
gauge_address = '0x740ba8aa0052e07b925908b380248cb03f3de5cb'

# ABI for the working_supply function
# Minimal ABI to get the working supply. You might need the full ABI if you want to call more functions.
abi = '[{"constant":true,"inputs":[],"name":"working_supply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'

# Use the to_checksum_address method to convert the address
checksummed_address = web3.to_checksum_address(gauge_address)

# Now use the checksummed address to create the contract
contract = web3.eth.contract(address=checksummed_address, abi=abi)

# Call the working_supply function
working_supply = contract.functions.working_supply().call()

print("Working Supply:", working_supply)
