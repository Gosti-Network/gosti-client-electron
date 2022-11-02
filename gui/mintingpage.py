from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView
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
from chia.util.config import load_config_cli, load_config
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chianft.util.mint import Minter

import os
import asyncio
import shutil
from urllib.request import urlopen
import hashlib
import pickle


class MintingPage(FloatLayout):
	def __init__(self, **kwargs):
		self.color_bg = COLOR_BG_DARK
		super(MintingPage, self).__init__(**kwargs)
		self.games = []
		Clock.schedule_once(self.load_games, 0)

	def load_games(self, time):
		self.games = []
		self.ids.contentview.content.clear_widgets()
		config = ConfigParser()
		config.read('config.ini')

		con = DataLayerConnector()
		self.games = con.get_published_games()
		for game in self.games:
			self.ids.contentview.content.add_widget(GameMintingPanel(game))


class GameMintingPanel(BoxLayout):
	def __init__(self, game=None):
		self.color_bg = COLOR_BG_MAIN
		super(GameMintingPanel, self).__init__(size_hint=(1, None))
		self.config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
		self.wallet_rpc_port = self.config['wallet']['rpc_port']
		self.node_rpc_port = self.config['full_node']['rpc_port']

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
		pass


	def create_mint_spend_bundles(self, delay=0):
		return asyncio.run(self.__create_mint_spend_bundles())

	async def __create_mint_spend_bundles(self):
		print("create_mint_spend_bundles")
		wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
		node_client = await FullNodeRpcClient.create('localhost', uint16(self.node_rpc_port), DEFAULT_ROOT_PATH, self.config)
		try:
			with open("minting_metadata.csv", 'w') as f:
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
				metadata_input="minting_metadata.csv",
				bundle_output="minting_spend_bundles_output.pkl",
				wallet_id=7,
				mint_from_did=True,
				royalty_address=royalty_address,
				royalty_percentage=royalty_percentage,
				has_targets=False,
				chunk=25,
			)
			with open("minting_spend_bundles_output.pkl", "wb") as f:
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
		print("create_mint_spend_bundles")
		wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
		node_client = await FullNodeRpcClient.create('localhost', uint16(self.node_rpc_port), DEFAULT_ROOT_PATH, self.config)
		try:
			spends = []
			with open("minting_spend_bundles_output.pkl", "rb") as f:
				spends_bytes = pickle.load(f)
			for spend_bytes in spends_bytes:
				spends.append(SpendBundle.from_bytes(spend_bytes))

			minter = Minter(wallet_client, node_client)

			fee_amount = int(float(self.ids['fee_amount'].text)*1000000000000)

			await minter.submit_spend_bundles(
				spends, int(fee_amount), create_sell_offer=True
			)
		except Exception as e:
			print(f"__submit_spend_bundles: {e}")
		finally:
			node_client.close()
			wallet_client.close()
			await node_client.await_closed()
			await wallet_client.await_closed()


class ConfirmMintingPopup(ConfirmPopup):
	def __init__(self, game):
		super(ConfirmMintingPopup, self).__init__()
		self.game = game

	def on_ok(self):
		con = DataLayerConnector()
		con.minting_game(self.game)

	def on_cancel(self):
		pass
