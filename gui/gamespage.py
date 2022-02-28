from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

from kivy.clock import Clock

from db import DatabaseConnector


class GamesPage(FloatLayout):
	def __init__(self, **kwargs):
		super(GamesPage, self).__init__(**kwargs)
		self.games = []
		Clock.schedule_once(self.load_games, 0)

	def load_games(self, time):
		con = DatabaseConnector("bolt://10.0.0.3:7687", "Gaerax", "password")
		self.games = con.get_games()
		for game in self.games:
			self.ids.contentview.content.add_widget(GameCapsule(self.games[game]))


class GameCapsule(BoxLayout):
	def __init__(self, game):
		super(GameCapsule, self).__init__(size_hint=(1, None))
		self.update_ui(game)

	def update_ui(self, game):
		self.ids['title'].text = game.title
		self.ids['description'].text = game.description
		try:
			if game.capsuleimage is not '':
				self.ids['capsuleimage'].source = game.capsuleimage
			self.ids['capsuleimage'].reload()
		except:
			pass
		self.ids['status'].text = game.status
		self.ids['version'].text = game.version
		self.ids['author'].text = game.author
		try:
			self.ids['price'].text = str(game.prices['USDS']) + ' USDS'
		except:
			self.ids['price'].text = "Free"


class GamesSearch(FloatLayout):
	pass
