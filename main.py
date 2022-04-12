from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.popup import Popup
from kivy.core.window import Window

from data import Game
from db import DatabaseConnector

from gui import *

class MainView(FloatLayout):
	pass


class ContentView(TabbedPanel):
	pass


class SideBar(FloatLayout):
	pass


class ContentScrollView(ScrollView):
	def __init__(self, **kwargs):
		super(ContentScrollView, self).__init__(**kwargs)
		self.content = ContentList()
		self.content.bind(minimum_height=self.content.setter('height'))
		self.bar_width = 6
		self.scroll_type = ['content', 'bars']
		self.add_widget(self.content)


class ContentList(GridLayout):
	def __init__(self, **kwargs):
		super(ContentList, self).__init__(**kwargs)


class ConfirmPopup(Popup):
	__events__ = ('on_ok', 'on_cancel')
	text = ''

	def ok(self):
		self.dispatch('on_ok')
		self.dismiss()

	def cancel(self):
		self.dispatch('on_cancel')
		self.dismiss()

	def on_ok(self):
		pass

	def on_cancel(self):
		pass


class Spriggan(App):
	def build(self):
		Window.size = (1400, 800)
		Window.minimum_width = 1300
		Window.minimum_height = 600
		return MainView()


if __name__ == '__main__':
	Spriggan().run()
