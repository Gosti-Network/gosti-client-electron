from util import *
from base64 import b64encode, b64decode

from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config as load_chia_config
from chia.util.ints import uint16
from chia.util.byte_types import hexstr_to_bytes
from chia.rpc.data_layer_rpc_client import DataLayerRpcClient
from chia.types.blockchain_format.sized_bytes import bytes32

import asyncio
import json


class DataLayerConnector():
	def __init__(self):
		self.chia_config = load_chia_config(DEFAULT_ROOT_PATH, "config.yaml")
		self.datalayer_rpc_port = self.chia_config['data_layer']['rpc_port']
		self.active_store_id = ""

	def create_datastore(self):
		return asyncio.run(self.__create_datastore())

	async def __create_datastore(self):
		dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		store = await dl.create_data_store(fee=5000000000)
		print(f"datastore: {store}")
		dl.close()
		return store

	def publish_media(self, datastore_id, media):
		return asyncio.run(self.__publish_media(datastore_id, media))

	async def __publish_media(self, datastore_id, media):
		try:
			print("attempting to publish")
			print(media)
			print("to: " + datastore_id)
			g = json.dumps(media)
			medias = await self.__get_published_media(datastore_id)
			print(medias)
			for gm in medias:
				if "productId" in gm and gm["productId"] == media["productId"]:
					print("2")
					dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
					update_status = await dl.update_data_store(
							store_id=hexstr_to_bytes(datastore_id),
							changelist=[
								{"action":"delete", "key":str.encode(media["productId"]).hex()},
								{"action":"insert", "key":str.encode(media["productId"]).hex(), "value":str.encode(g).hex()}
							],
							fee=5000000000
					)
					print(f"status: {update_status}")
					params = {"media": json.dumps(media)}
					print(params)

					dl.close()
					return update_status
			dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
			update_status = await dl.update_data_store(
				store_id=hexstr_to_bytes(datastore_id),
				changelist=[{"action":"insert", "key":str.encode(media["productId"]).hex(), "value":str.encode(g).hex()}],
				fee=5000000000
			)
			print(f"status: {update_status}")
			dl.close()
			return update_status
		except Exception as e:
			print(e)
			return False


	def get_owned_datastores(self):
		return asyncio.run(self.__get_owned_datastores())

	async def __get_owned_datastores(self):
		try:
			dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
			stores = await dl.get_owned_stores()
			dl.close()
			return stores["store_ids"]
		except Exception as e:
			print(f"__get_owned_datastores: {e}")
			return []

	def get_published_media(self, id):
		return asyncio.run(self.__get_published_media(id))

	async def __get_published_media(self, id):
		try:
			dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
			root = await dl.get_root(store_id=hexstr_to_bytes(id))
			medias = await dl.get_keys_values(store_id=hexstr_to_bytes(id), root_hash=hexstr_to_bytes(root["hash"]))
			dl.close()
			decoded = []
			for g in medias["keys_values"]:
				r = json.loads(str(bytes.fromhex(g["value"][2:]).decode()))
				if "productId" in r:
					decoded.append(r)
			print(decoded)
			return decoded
		except Exception as e:
			print(f"__get_published_media: {e}")
			return []
