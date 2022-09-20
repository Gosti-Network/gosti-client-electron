from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter import Scatter

from kivy.graphics import Color, Rectangle

from kivy.clock import Clock
from functools import partial

import requests
import os
import glob
import time
from threading import Thread
from zipfile import ZipFile
from packaging import version

from util import *
from db import DatabaseConnector

from torrents import TorrentHandler

NOT_DOWNLOADED = 0
DOWNLOADED = 1
INSTALLED = 2
PENDING_UPDATE = 3
UPDATING = 4


class LibraryView(ScrollView):
	def __init__(self, **kwargs):
		super(LibraryView, self).__init__(**kwargs)
		list = LibraryList()
		list.bind(minimum_height=list.setter('height'))
		self.bar_width = 6
		self.scroll_type = ['content', 'bars']
		self.add_widget(list)

		TorrentHandler().set_update_ui_callback(self.update_torrent_ui)

	def update_torrent_ui(self, statuses):
		print("update torrent ui")

class LibraryList(GridLayout):
	def __init__(self, **kwargs):
		super(LibraryList, self).__init__(**kwargs)
		con = DatabaseConnector()
		self.games = con.get_games()
		con.close()
		for game in self.games:
			self.add_widget(LibraryGame(self.games[game]))


class LibraryGame(BoxLayout):
	def __init__(self, game):
		super(LibraryGame, self).__init__(size_hint=(1, None))
		self.game = game
		self.ids['title'].text = self.game.title
		self.ids['icon'].source = self.game.icon
		self.downloadthreads = []
		self.installstate = NOT_DOWNLOADED
		self.auto_install = True
		self.check_install_state()

	def check_install_state(self):
		installs = glob.glob(INSTALL_PATH + '/' + self.game.title + '*')
		if len(installs) > 0:
			self.installstate = INSTALLED
			if (version.parse(installs[0].split('-v-')[-1]) < version.parse(self.game.version)):
				self.installstate = PENDING_UPDATE

		status = TorrentHandler().get_status(self.game.get_torrent_data_filename())
		if status is not None:
			if status.state == "downloading":
				self.installstate = UPDATING


		self.update_install_state(self.installstate)
		Clock.schedule_once(partial(self.update_install_state, self.installstate), 2)

	def update_install_state(self, state, *args):
		print("Update State: " + str(state))
		self.installstate = state
		if state == NOT_DOWNLOADED:
			# self.ids.activateButton.background_normal = 'img/ActivateButton-Download-Normal.png'
			# self.ids.activateButton.background_down = 'img/ActivateButton-Download-Down.png'
			self.ids.activateButton.disabled = False
		if state == DOWNLOADED:
			# self.ids.activateButton.background_normal = 'img/ActivateButton-Install-Normal.png'
			# self.ids.activateButton.background_down = 'img/ActivateButton-Install-Down.png'
			self.ids.activateButton.disabled = False
		elif state == INSTALLED:
			# self.ids.activateButton.background_normal = 'img/ActivateButton-Play-Normal.png'
			# self.ids.activateButton.background_down = 'img/ActivateButton-Play-Down.png'
			self.ids.activateButton.disabled = False
		elif state == PENDING_UPDATE:
			# self.ids.activateButton.background_normal = 'img/ActivateButton-Update-Normal.png'
			# self.ids.activateButton.background_down = 'img/ActivateButton-Update-Down.png'
			self.ids.activateButton.disabled = False
		elif state == UPDATING:
			# self.ids.activateButton.background_normal = 'img/ActivateButton-Updating-Normal.png'
			# self.ids.activateButton.background_down = 'img/ActivateButton-Updating-Down.png'
			self.ids.activateButton.disabled = True

	def activate(self):
		self.check_install_state()
		if self.installstate == NOT_DOWNLOADED or self.installstate == PENDING_UPDATE:
			t = Thread(target=self.download)
			t.daemon = True
			t.start()
			self.downloadthreads.append(t)
			self.update_install_state(UPDATING)
		elif self.installstate == DOWNLOADED:
			t = Thread(target=self.install)
			t.daemon = True
			t.start()
			self.downloadthreads.append(t)
			self.update_install_state(UPDATING)
		elif self.installstate == INSTALLED:
			self.update_install_state(INSTALLED)
			try:
				os.startfile(os.getcwd() + INSTALL_PATH + '/' + self.game.get_filename() + '/' + self.game.get_executable())
			except Exception as e:
				print(e)


	def download(self):
		torrenthandler = TorrentHandler()
		tor = self.game.get_torrent()
		if tor != "":
			torrent_name = TORRENTS_PATH + self.game.get_filename() + ".torrent"
			f = open(torrent_name, "wb")
			f.write(tor)
			f.close()
			torrenthandler.add_torrent(torrent_name)

		state = "downloading"
		while(state != "seeding"):
			status = torrenthandler.get_status(self.game.get_torrent_data_filename())
			if status is not None:
				print("status: ", str(status.progress) + " : " + str(status.state))
				self.ids.progress.value = status.progress
				state = str(status.state)
			time.sleep(1)

		if self.auto_install:
			self.install()

	def install(self):
		with ZipFile(self.game.get_fileslocation(), 'r') as zip:
			print(INSTALL_PATH + self.game.get_filename())
			zip.extractall(INSTALL_PATH + self.game.get_filename())
