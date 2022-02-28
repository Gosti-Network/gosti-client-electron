from kivy.uix.popup import Popup


class StorePage(Popup):
	def __init__(self, game):
		super(StorePage, self).__init__()
		self.game = game
