from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.config import ConfigParser

from kivy.clock import Clock

from .storepage import StorePage
from .gamespage import GameCapsule

from data import Game
from main import ConfirmPopup

from datalayer import DataLayerConnector
from util import *
from base64 import b64encode, b64decode

from torrents import TorrentHandler

from chia.types.spend_bundle import SpendBundle
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint16
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.byte_types import hexstr_to_bytes
from chia.util.config import load_config_cli, load_config
from chia.util.bech32m import encode_puzzle_hash
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.wallet.util.wallet_types import WalletType
from chianft.util.mint import Minter

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os
import asyncio
from threading import Thread
import shutil
from urllib.request import urlopen
import hashlib
import pickle
import json
import datetime


class MintingPage(FloatLayout):
	def __init__(self, **kwargs):
		self.color_bg = COLOR_BG_DARK
		super(MintingPage, self).__init__(**kwargs)
		self.games = []
		Clock.schedule_once(self.load_games, 0)

	def load_games(self, time):
		self.games = []
		self.ids.contentview.content.clear_widgets()
		self.ids['resetbtnimg'].source = "img/ResetIcon.png"
		con = DataLayerConnector()
		self.games = con.get_published_games()
		for game in self.games:
			self.ids.contentview.content.add_widget(GameMintingPanel(game))

	def reset(self):
		self.ids.contentview.content.clear_widgets()
		self.load_games(0)


class GameMintingPanel(BoxLayout):
	def __init__(self, game=None):
		self.color_bg = COLOR_BG_MAIN
		super(GameMintingPanel, self).__init__(size_hint=(1, None))
		self.chia_config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
		self.wallet_rpc_port = self.chia_config['wallet']['rpc_port']
		self.node_rpc_port = self.chia_config['full_node']['rpc_port']
		self.config = ConfigParser()
		self.config.read('config.ini')

		self.orientation = "vertical"
		if game is None:
			self.game = Game()
			self.editdisabled = False
		else:
			self.game = game
			self.editdisabled = True
		self.old_game = self.game
		Clock.schedule_once(self.load_minting_data, 0)

	def load_minting_data(self, time):
		self.ids['data_uri'].text = self.game.info["capsuleimage"]
		self.ids['productname'].text = self.game.info["title"]
		self.ids['did'].text = self.config["wallet"]["did"]
		try:
			with open(self.config['publishing']['minting_data_path'] + '/' + self.game.info["productid"] + '_mint_data.json', 'r') as f:
				data = json.load(f)
				self.ids['productname'].text = data["productname"]
				self.ids['did'].text = data["did"]
				self.ids['data_uri'].text = data["data_uri"]
				self.ids['metadata_uri'].text = data["metadata_uri"]
				self.ids['license_uri'].text = data["license_uri"]
				self.ids['fee_amount'].text = data["fee_amount"]
				self.ids['royalty_percentage'].text = data["royalty_percentage"]
				self.ids['royalty_address'].text = data["royalty_address"]
				self.ids['mint_quantity'].text = data["mint_quantity"]
				self.ids['sell_amount'].text = data["sell_amount"]
		except Exception as e:
			print(e)

	def save_minting_data(self):
		filename = self.config['publishing']['minting_data_path'] + '/' + self.game.info["productid"] + '_mint_data.json'
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		with open(filename, 'w') as f:
			data = {}
			data['productname'] = self.ids['productname'].text
			data['did'] = self.ids['did'].text
			data['data_uri'] = self.ids['data_uri'].text
			data['metadata_uri'] = self.ids['metadata_uri'].text
			data['license_uri'] = self.ids['license_uri'].text
			data['fee_amount'] = self.ids['fee_amount'].text
			data['royalty_percentage'] = self.ids['royalty_percentage'].text
			data['royalty_address'] = self.ids['royalty_address'].text
			data['mint_quantity'] = self.ids['mint_quantity'].text
			data['sell_amount'] = self.ids['sell_amount'].text
			json.dump(data, f)

	def start_minting(self):
		self.create_mint_spend_bundles()
		self.minting_popup = MintingPopup()
		time = str(datetime.timedelta(seconds=int(min(float(self.ids['mint_quantity'].text) / 25.0, 1) * 52)))
		self.minting_popup.ids['mintingmessage'].text = f"Minting {int(self.ids['mint_quantity'].text)} copies of {self.ids['productname'].text} in chunks of 25 per block with a fee of {float(self.ids['fee_amount'].text)} XCH\nMinting should take ~{time} depending on fee and mempool."
		self.minting_popup.open()

		self.minter_daemon = Thread(target=self.submit_spend_bundles)
		self.minter_daemon.daemon = True
		self.minter_daemon.start()

	def stop_minting(self):
		self.minter_daemon.stop()

	def create_mint_spend_bundles(self, delay=0):
		self.save_minting_data()
		return asyncio.run(self.__create_mint_spend_bundles())

	async def __create_mint_spend_bundles(self):
		print("create_mint_spend_bundles")
		wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		wallets = await wallet_client.get_wallets()

		mintwallet = None
		for wallet in wallets:
			print(wallet)
			if wallet["type"] == WalletType.NFT:
				if "did_id" in wallet["data"]:
					did = json.loads(wallet["data"])
					if did['did_id']:
						did = encode_puzzle_hash(hexstr_to_bytes(did['did_id']), "did:chia:")
					if did == self.ids['did'].text:
						mintwallet = wallet["id"]
		print(f"mint wallet: {mintwallet}")

		if mintwallet == None:
			print("Failed to find DID NFT wallet")
			response = await wallet_client.create_new_nft_wallet(self.ids['did'].text, name='Spriggan Mint')
			print(response)
			wallets = await wallet_client.get_wallets()
			for wallet in wallets:
				if wallet['id'] == response['wallet_id']:
					mintwallet = wallet["id"]

		print(f"mint wallet: {mintwallet}")


		node_client = await FullNodeRpcClient.create('localhost', uint16(self.node_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		try:
			filename = self.config['publishing']['minting_data_path'] + '/' + "minting_metadata.csv"
			os.makedirs(os.path.dirname(filename), exist_ok=True)
			with open(filename, 'w') as f:
				f.write("hash,uris,meta_hash,meta_uris,license_hash,license_uris,edition_number,edition_total\n")

				data_uri = self.ids['data_uri'].text
				response = urlopen(data_uri)
				data_hash = hashlib.sha256(response.read()).hexdigest()
				metadata_uri = self.ids['metadata_uri'].text
				response = urlopen(metadata_uri)
				metadata_hash = hashlib.sha256(response.read()).hexdigest()
				license_uri = self.ids['license_uri'].text
				response = urlopen(license_uri)
				license_hash = hashlib.sha256(response.read()).hexdigest()
				mint_quantity = int(self.ids['mint_quantity'].text)
				royalty_percentage = int(float(self.ids['royalty_percentage'].text)*100)
				royalty_address = self.ids['royalty_address'].text

				for i in range(0, mint_quantity):
					f.write(f"{data_hash},{data_uri},{metadata_hash},{metadata_uri},{license_hash},{license_uri},{0},{0}\n")

				f.close()

			minter = Minter(wallet_client=wallet_client, node_client=node_client)

			spend_bundles = await minter.create_spend_bundles(
				metadata_input=self.config['publishing']['minting_data_path'] + '/' + "minting_metadata.csv",
				bundle_output=self.config['publishing']['minting_data_path'] + '/' + "minting_spend_bundles_output.pkl",
				wallet_id=mintwallet,
				mint_from_did=True,
				royalty_address=royalty_address,
				royalty_percentage=royalty_percentage,
				has_targets=False,
				chunk=25,
			)
			with open(self.config['publishing']['minting_data_path'] + '/' + "minting_spend_bundles_output.pkl", "wb") as f:
				pickle.dump(spend_bundles, f)
				print("Successfully created {} spend bundles".format(len(spend_bundles)))
		except Exception as e:
			print(f"__create_mint_spend_bundles: {e}")
		finally:
			node_client.close()
			wallet_client.close()
			await node_client.await_closed()
			await wallet_client.await_closed()


	def submit_spend_bundles(self, delay=0):
		return asyncio.run(self.__submit_spend_bundles())

	async def __submit_spend_bundles(self):
		print("__submit_spend_bundles")

		wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		node_client = await FullNodeRpcClient.create('localhost', uint16(self.node_rpc_port), DEFAULT_ROOT_PATH, self.chia_config)
		try:
			error = None
			spends = []
			with open(self.config['publishing']['minting_data_path'] + '/' + "minting_spend_bundles_output.pkl", "rb") as f:
				spends_bytes = pickle.load(f)

			for spend_bytes in spends_bytes:
				spends.append(SpendBundle.from_bytes(spend_bytes))

			minter = Minter(wallet_client, node_client)

			fee_amount = int(float(self.ids['fee_amount'].text)*1000000000000)
			print(fee_amount)
			print(int(fee_amount))
			sell_amount = int(float(self.ids['sell_amount'].text)*1000000000000)
			print(sell_amount)
			await minter.submit_spend_bundles(
				spends, fee_amount
			)
		except Exception as e:
			print(f"__submit_spend_bundles error: {e}")
			error = e

		finally:
			node_client.close()
			wallet_client.close()
			await node_client.await_closed()
			await wallet_client.await_closed()
			if error:
				self.minting_popup.ids['mintingmessage'].text = f"Error"
				self.minting_popup.ids['mintingmessage2'].text = f"{error}"
			else:
				self.minting_popup.ids['mintingmessage'].text = f"Minting Complete!"
				self.minting_popup.ids['mintingmessage2'].text = f""

	def generate_metadata_template(self):
		config = ConfigParser()
		config.read('config.ini')
		metadata = {
			"format": "CHIP-0007",
			"name": f"{self.game.info['title']}",
			"description": f"A copy of {self.game.info['title']} by {self.game.info['publisher']}",
			"sensitive_content": (self.game.info['contentrating'] == '18+'),
			"collection": {
				"name": f"{self.game.info['title']}",
				"id": f"{self.game.info['productid']}",
				"attributes": [
					{
						"type": "game metadata format",
						"value": "Spriggan-1.0"
					},
					{
						"type": "description",
						"value": f"{self.game.info['description']}"
					},
					{
						"type": "icon",
						"value": ""
					},
					{
						"type": "banner",
						"value": ""
					},
					{
						"type": "content rating",
						"value": f"{self.game.info['contentrating']}"
					},
					{
						"type": "content tags",
						"value": self.game.info['tags']
					},
					{
						"type": "publisher",
						"value": f"{self.game.info['publisher']}"
					},
					{
						"type": "developer",
						"value": f"{self.game.info['developer']}"
					},
					{
						"type": "datastore id",
						"value": config["publishing"]["datastore_id"]
					},
					{
						"type": "website",
						"value": ""
					},
					{
						"type": "twitter",
						"value": ""
					},
					{
						"type": "discord",
						"value": ""
					}
				]
			},
			"attributes": [
				{
					"trait_type": "Edition",
					"value": "Standard"
				}
			],
			"minting_tool": "Spriggan-1.0"
		}


		pretty = json.dumps(metadata, indent=4)
		print(pretty)
		popup = SaveMetadataPopup(pretty)
		popup.open()


class SaveMetadataPopup(ConfirmPopup):
	def __init__(self, metadata):
		config = ConfigParser()
		config.read('config.ini')
		super(SaveMetadataPopup, self).__init__()
		self.metadata = metadata
		self.filechooser = FileChooserListView()
		self.filechooser.dirselect = False
		self.filechooser.path = os.getcwd() + config["files"]["install_path"]
		self.ids['layout'].add_widget(self.filechooser)

	def on_ok(self):
		print(self.filechooser.files)
		with open(self.filechooser.files[len(self.filechooser.files)-1], 'w') as f:
			f.write(self.metadata)
			f.close()

	def on_cancel(self):
		print("cancel file select")



class MintingPopup(Popup):
	def __init__(self):
		super(MintingPopup, self).__init__(title='Minting')

	def close_minting_popup(self):
		self.dismiss()
