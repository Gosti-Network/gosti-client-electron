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

from data import Media


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


	def get_owned_media(self):
		return asyncio.run(self.__get_owned_media())

	async def __get_owned_media(self):
		dl_client = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.config)
		wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
		wallets = await wallet_client.get_wallets(wallet_type=WalletType.NFT)
		media = {}
		for wallet in wallets:
			did = await wallet_client.get_nft_wallet_did(wallet['id'])
			nftlist = await wallet_client.list_nfts(wallet["id"])
			nfts = nftlist["nft_list"]
			loaded = {}
			for nft in nfts:
				try:
					if nft["metadata_uris"][0] in loaded.keys():
						metadata = loaded[nft["metadata_uris"][0]]
					else:
						response = urlopen(nft["metadata_uris"][0])
						x = response.read().decode("utf-8")
						metadata = json.loads(x)
						loaded[nft["metadata_uris"][0]] = metadata

					for attr in metadata["collection"]["attributes"]:
						if attr["type"] == "datastore id":
							try:
								store_id=hexstr_to_bytes(attr["value"])
								root = await dl_client.get_root(store_id)
								products = await dl_client.get_keys_values(store_id=store_id, root_hash=hexstr_to_bytes(root["hash"]))
								for p in products["keys_values"]:
									info = json.loads(str(bytes.fromhex(p["value"][2:]).decode()))
									if info["productid"] == metadata['collection']['id']:
										if metadata['collection']['id'] in media.keys():
											media[metadata['collection']['id']].add_copy()
										else:
											media[metadata['collection']['id']] = Media.from_json(info)
							except Exception as e:
								print(e)
								dl_client.subscribe(hexstr_to_bytes(attr["value"]))

				except Exception as e:
					print(f"__get_owned_media: {e}")


		wallet_client.close()
		dl_client.close()
		print(f"media:{media}")
		return media.values()
