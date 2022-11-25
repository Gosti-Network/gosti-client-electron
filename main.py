import asyncio
from kivy.app import App
from kivy.app import async_runTouchApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy import resources

from datalayer import DataLayerConnector

from gui import *

class MainView(FloatLayout):
	def __init__(self, **kwargs):
		super(MainView, self).__init__(**kwargs)
		config = ConfigParser()
		config.read('config.ini')
		print(config.get("publishing", "enabled"))
		if config.get("publishing", "enabled") == "1":
			self.add_widget(ContentViewPublisher(size_hint=(.8, 1), pos_hint={'x': .2, 'y': 0}))
		else:
			self.add_widget(ContentViewNormal(size_hint=(.8, 1), pos_hint={'x': .2, 'y': 0}))
		Clock.schedule_once(self.checkconfig, 0)

	def checkconfig(self, time):
		config = ConfigParser()
		config.read('config.ini')

		fingerprint = config.get("wallet", "fingerprint")
		print(f"fingerprint: {fingerprint}")

		if fingerprint == "":
			self.open_settings()

	def open_settings(self):
		popup = Popup(
			title='Settings',
			content=SettingsPage()
		)
		popup.open()


class ContentViewNormal(TabbedPanel):
	pass

class ContentViewPublisher(TabbedPanel):
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


class ContentList(StackLayout):
	pass

class ConfirmPopup(Popup):
	__events__ = ('on_ok', 'on_cancel')
	text = 'Confirm'

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
		Window.minimum_width = 1000
		Window.minimum_height = 600
		return MainView()


if __name__ == '__main__':
	Spriggan().run()
