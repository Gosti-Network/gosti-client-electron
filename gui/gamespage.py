from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.clock import Clock

from kivy.graphics import Color

from util import *

from datalayer import DataLayerConnector
from wallet import *
import asyncio


class GamesPage(FloatLayout):
	def __init__(self, **kwargs):
		super(GamesPage, self).__init__(**kwargs)
		self.wallet = SprigganWallet()
		self.games = []
		Clock.schedule_once(self.load_games, 0)

	def load_games(self, time):
		con = DataLayerConnector()
		self.games = self.wallet.get_owned_games()
		for game in self.games:
			self.ids.contentview.content.add_widget(GameCapsule(game))


class GameCapsule(BoxLayout):
	def __init__(self, game):
		self.color_dev_status = get_status_color(game.info["status"])
		super(GameCapsule, self).__init__(size_hint=(1, None))
		self.update_ui(game)

	def update_ui(self, game):
		try:
			if game.info["capsuleimage"] != '':
				self.ids['capsuleimage'].source = game.info["capsuleimage"]
			self.ids['capsuleimage'].reload()
		except:
			pass
		self.ids['status'].text = game.info["status"]
		self.ids['version'].text = game.info["version"]


class GamesSearch(FloatLayout):
	pass
