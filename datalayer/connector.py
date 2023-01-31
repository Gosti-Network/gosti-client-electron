from data import Game
from util import *
from base64 import b64encode, b64decode

from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config as load_chia_config
from chia.util.ints import uint16
from chia.util.byte_types import hexstr_to_bytes
from chia.rpc.data_layer_rpc_client import DataLayerRpcClient
from chia.types.blockchain_format.sized_bytes import bytes32

from kivy.config import ConfigParser

import asyncio
import json
import requests


class DataLayerConnector():
	def __init__(self):
		self.chia_config = load_chia_config(DEFAULT_ROOT_PATH, "config.yaml")
		self.datalayer_rpc_port = self.chia_config['data_layer']['rpc_port']
		self.active_store_id = ""

	def get_datastore_id(self):
		config = ConfigParser()
		config.read('config.ini')
		# if config["publishing"]["datastore_id"] == "":
		# 	store = asyncio.run(self.__create_datastore())
		# 	print("was going to make dl")
		# 	config["publishing"]["datastore_id"] = store["id"]
		# 	save_config(config)
		# else:
		return config["publishing"]["datastore_id"]

	def create_datastore(self):
		return asyncio.run(self.__create_datastore())

	async def __create_datastore(self):
		dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		store = await dl.create_data_store(fee=500000000000)
		print(f"datastore: {store}")
		dl.close()
		return store

	def publish_game(self, game):
		asyncio.run(self.__publish_game(game))

	async def __publish_game(self, game):
		id = self.get_datastore_id()
		g = json.dumps(game.info)
		games = await self.__get_published_games(id)
		for gm in games:
			if gm.info["productid"] == game.info["productid"]:
				dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
				# update_status = await dl.update_data_store(
				# 		store_id=hexstr_to_bytes(id),
				# 		changelist=[
				# 			{"action":"delete", "key":str.encode(game.info["productid"]).hex()},
				# 			{"action":"insert", "key":str.encode(game.info["productid"]).hex(), "value":str.encode(g).hex()}
				# 		],
				# 		fee=500000000000
				# )
				# print(f"status: {update_status}")
				params = {"game": json.dumps(game.info)}
				print(params)
				response = requests.put(f"http://localhost:3000/requestlisting", params=params)
				if response.status_code == 200:
					print("sucessfully fetched the data")
					print(response.json())
				else:
					print(f"Hello person, there's a {response.status_code} error with your request")


				dl.close()
				return update_status

		dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		update_status = await dl.update_data_store(
				store_id=hexstr_to_bytes(id),
				changelist=[{"action":"insert", "key":str.encode(game.info["productid"]).hex(), "value":str.encode(g).hex()}],
				fee=500000000000
		)
		print(f"status: {update_status}")
		dl.close()
		return update_status

	def get_owned_datastores(self):
		id = self.get_datastore_id()
		return asyncio.run(self.__get_owned_datastores(id))

	async def __get_owned_datastores(self, id):
		try:
			dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
			stores = await dl.get_owned_stores()
			dl.close()
			return stores["store_ids"]
		except Exception as e:
			print(f"__get_owned_datastores: {e}")
			return []

	def get_published_games(self):
		id = self.get_datastore_id()
		return asyncio.run(self.__get_published_games(id))

	async def __get_published_games(self, id):
		try:
			dl = await DataLayerRpcClient.create('localhost', uint16(self.datalayer_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
			root = await dl.get_root(store_id=hexstr_to_bytes(id))
			games = await dl.get_keys_values(store_id=hexstr_to_bytes(id), root_hash=hexstr_to_bytes(root["hash"]))
			dl.close()
			decoded = []
			for g in games["keys_values"]:
				decoded.append(Game.from_json(json.loads(str(bytes.fromhex(g["value"][2:]).decode()))))
			print(decoded)
			return decoded
		except Exception as e:
			print(f"__get_published_games: {e}")
			return []
