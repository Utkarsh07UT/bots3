import json
import os
from app.config import settings

try:
    from web3 import Web3
    from web3.exceptions import Web3Exception
    WEB3_AVAILABLE = True
except ImportError:
    Web3 = None
    Web3Exception = Exception
    WEB3_AVAILABLE = False

# A minimal ABI for the AlertLog contract
ALERT_LOG_ABI = json.loads("""
[
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "internalType": "bytes32", "name": "alertHash", "type": "bytes32"},
            {"indexed": false, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"indexed": false, "internalType": "address", "name": "sender", "type": "address"}
        ],
        "name": "AlertLogged",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "alertHash", "type": "bytes32"}],
        "name": "logAlert",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "alertHash", "type": "bytes32"}],
        "name": "verifyAlert",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
""")

class BlockchainClient:
    def __init__(self):
        self.enabled = settings.BLOCKCHAIN_ENABLED
        self.rpc_url = settings.WEB3_RPC_URL
        self.contract_address = settings.SMART_CONTRACT_ADDRESS
        self.private_key = settings.SIGNER_PRIVATE_KEY
        
        if self.enabled and WEB3_AVAILABLE and self.rpc_url and self.private_key and Web3 is not None:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self.account = self.w3.eth.account.from_key(self.private_key)
            self.contract_address = self.w3.to_checksum_address(self.contract_address)
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=ALERT_LOG_ABI)
        else:
            self.w3 = None

    def log_alert_on_chain(self, alert_hash_hex: str) -> dict:
        if not self.enabled or not self.w3:
            return {"status": "disabled", "error": "Blockchain is not enabled or properly configured"}

        try:
            alert_hash_bytes = Web3.to_bytes(hexstr=alert_hash_hex)
            
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.logAlert(alert_hash_bytes).build_transaction({
                'chainId': self.w3.eth.chain_id,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                "status": "success",
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "sender": self.account.address,
                "contract": self.contract_address
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def verify_alert_on_chain(self, alert_hash_hex: str) -> dict:
        if not self.enabled or not self.w3:
            return {"status": "disabled", "error": "Blockchain is not enabled or properly configured"}

        try:
            alert_hash_bytes = Web3.to_bytes(hexstr=alert_hash_hex)
            exists, timestamp, sender = self.contract.functions.verifyAlert(alert_hash_bytes).call()
            return {
                "status": "success",
                "verified": exists,
                "timestamp": timestamp,
                "sender": sender
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

blockchain_client = BlockchainClient()
