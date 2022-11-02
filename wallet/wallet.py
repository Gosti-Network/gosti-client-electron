from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.rpc.data_layer_rpc_client import DataLayerRpcClient
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config_cli, load_config
from chia.util.ints import uint16
from chia.wallet.util.wallet_types import WalletType
from chia.util.byte_types import hexstr_to_bytes

import asyncio
from urllib.request import urlopen
import json

from data import Game


class SprigganWallet():

	def __init__(self):
		self.config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
		self.wallet_rpc_port = self.config['wallet']['rpc_port']
		self.datalayer_rpc_port = self.config['data_layer']['rpc_port']

	def get_balances(self):
		return asyncio.run(self.__get_balances())

	async def __get_balances(self):
		balances = {}
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			wallets = await wallet_client.get_wallets()
			for wallet in wallets:
				balance = await wallet_client.get_wallet_balance(wallet['id'])
				balances[wallet['name']] = balance
		finally:
			wallet_client.close()
			await wallet_client.await_closed()
		return balances

	def get_address(self):
		return asyncio.run(self.__get_address())

	async def __get_address(self):
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			wallets = await wallet_client.get_wallets()
			address = await wallet_client.get_next_address(wallets[0]['id'], new_address=False)
		finally:
			wallet_client.close()
			await wallet_client.await_closed()
		return address

	def get_fingerprints(self):
		return asyncio.run(self.__get_fingerprints())

	async def __get_fingerprints(self):
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			fingerprints_i = await wallet_client.get_public_keys()
			fingerprints = []
			for fp in fingerprints_i:
				fingerprints.append(str(fp))

		finally:
			wallet_client.close()
			await wallet_client.await_closed()
		return fingerprints

	def get_dids(self, fingerprint):
		return asyncio.run(self.__get_dids(fingerprint))

	async def __get_dids(self, fingerprint):
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			wallets = await wallet_client.get_wallets(wallet_type=WalletType.DECENTRALIZED_ID)
			dids = []
			for wallet in wallets:
				did = await wallet_client.get_did_id(wallet["id"])
				dids.append(str(did["my_did"]))
		finally:
			wallet_client.close()
			await wallet_client.await_closed()
		return dids

	def get_founder_status(self):
		return asyncio.run(self.__get_founder_status())

	async def __get_founder_status(self):
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			wallets = await wallet_client.get_wallets()
			founder_wallet = next(w for w in wallets if w['data'] == '2e40312dabfe3ae1e8f961a3d27694956e14cd71bc8a064fbb4feb10fa4b3a9100')
			if founder_wallet != None:
				balance = await wallet_client.get_balance(w['id'])
			else:
				balance = 0
		finally:
			wallet_client.close()
			await wallet_client.await_closed()

		if balance >= 1:
			return True
		else:
			return False


	def get_owned_games(self):
		return asyncio.run(self.__get_owned_games())

	async def __get_owned_games(self):
		dl_client = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.config)
		wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
		wallets = await wallet_client.get_wallets(wallet_type=WalletType.NFT)
		games = {}
		for wallet in wallets:
			did = await wallet_client.get_nft_wallet_did(wallet['id'])
			nftlist = await wallet_client.list_nfts(wallet["id"])
			nfts = nftlist["nft_list"]
			nfts.append({"fake": True})
			for nft in nfts:
				try:
					if "fake" in nft.keys():
						metadata = json.loads('''{"format": "CHIP-0007","name": "Pong - Standard Edition","description": "A copy of Pong by Gaerax","sensitive_content": false,"collection": {"name": "Pong","id": "**Game ID**","attributes": [{"type": "game metadata format","value": "Spriggan-1.0"},{"type": "description","value": ""},{"type": "icon","value": ""},{"type": "banner","value": ""},{"type": "content rating","value": ""},{"type": "content tags","value": ""},{"type": "publisher","value": ""},{"type": "developer","value": ""},{"type": "datastore id","value": "b25474a73f8f529710d4ecc497de9a472b93efea0b7d43281ee1657a68979657"},{"type": "website","value": ""},{"type": "twitter","value": ""},{"type": "discord","value": ""}]},"attributes": [{"trait_type": "Edition","value": "Standard"}],"minting_tool": "Spriggan-1.0"}''')
					else:
						response = urlopen(nft["metadata_uris"][0])
						x = response.read().decode("utf-8")
						metadata = json.loads(x)
					for attr in metadata["collection"]["attributes"]:
						if attr["type"] == "datastore id":
							root = await dl_client.get_root(store_id=hexstr_to_bytes(id))
							products = await dl_client.get_keys_values(store_id=hexstr_to_bytes(attr["value"]), root_hash=root["hash"])
							print(products)
							for p in products["keys_values"]:
								info = json.loads(str(bytes.fromhex(p["value"][2:]).decode()))
								if info["title"] == metadata["name"]:
									games[metadata['title']] = Game.from_json(info)
				except Exception as e:
					print(f"__get_owned_games: {e}")


		wallet_client.close()
		dl_client.close()
		print(f"games:{games}")
		return games.values()
