from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.config import ConfigParser

from kivy.clock import Clock

from kivy.graphics import Color

from util import *
from torrents import TorrentHandler
from functools import partial

import requests
import os
import glob
import time
from threading import Thread
from packaging import version
from base64 import b64encode, b64decode

from datalayer import DataLayerConnector
from wallet import *
import asyncio
import glob
import pyzipper

NOT_DOWNLOADED = 0
DOWNLOADED = 1
INSTALLED = 2
PENDING_UPDATE = 3
UPDATING = 4

class GamesPage(FloatLayout):
	def __init__(self, **kwargs):
		super(GamesPage, self).__init__(**kwargs)
		self.wallet = SprigganWallet()
		self.games = []
		Clock.schedule_once(self.load_games, 0)

	def load_games(self, time):
		con = DataLayerConnector()
		self.ids['resetbtnimg'].source = "img/ResetIcon.png"
		self.ids.contentview.content.clear_widgets()
		self.games = self.wallet.get_owned_games()
		for game in self.games:
			self.ids.contentview.content.add_widget(GameCapsule(game))

	def reset(self):
		self.load_games(0)


class GameCapsule(BoxLayout):
	def __init__(self, game):
		self.color_dev_status = get_status_color(game.info["status"])
		super(GameCapsule, self).__init__(size_hint=(1, None))
		self.game = game
		if self.game.copies == 1:
			self.ids['copies'].text = f"{self.game.copies} copy"
		else:
			self.ids['copies'].text = f"{self.game.copies} copies"
		self.ids['title'].text = self.game.info["title"]
		self.downloadthreads = []
		self.isinstalled = False
		self.isinstalling = False
		self.isdownloaded = False
		self.isdownloading = False
		self.hasupdate = False
		self.auto_install = True
		self.config = ConfigParser()
		self.config.read('config.ini')
		self.check_install_state()

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

	def check_install_state(self):
		self.ids['downloadbtnimg'].source = "img/SeedIcon.png"
		name = self.game.info["title"].replace(" ", "")
		print(self.config["files"]["install_path"] + '/' + name + '/version.json')
		if os.path.exists(self.config["files"]["install_path"] + '/' + name + '/version.json'):
			self.ids['playbtnimg'].source = "img/PlayIcon.png"
			with open(self.config["files"]["install_path"] + '/' + name + '/version.json') as f:
				installed_version = json.load(f)
				self.isinstalled = True
				if version.parse(installed_version["version"]) < version.parse(self.game.info["version"]):
					self.hasupdate = True
					status = TorrentHandler().get_status(self.game.get_filename_with_version() + '.torrent')
					if status is not None:
						if status.state == "downloading":
							self.isdownloading = True
							self.ids['downloadbtnimg'].source = "img/DownloadIcon.png"
						else:
							self.isdownloading = False
							self.ids['downloadbtnimg'].source = "img/DownloadIcon.png"
				else:
					self.hasupdate = False
					self.ids['downloadbtnimg'].source = "img/DownloadIcon.png"
		else:
			self.isinstalled = False
			self.ids['playbtnimg'].source = "img/InstallIcon.png"
			self.ids['downloadbtnimg'].source = "img/DownloadIcon.png"

		if os.path.exists(self.config["files"]["torrents_data_path"] + '/' + self.game.get_filename() +'.zip'):
			self.isdownloaded = True
			self.ids['downloadbtnimg'].source = "img/SeedIcon.png"



	def activate_download(self):
		self.check_install_state()

		print(f"isdownloaded: {self.isdownloaded}")
		print(f"isdownloading: {self.isdownloading}")
		print(f"hasupdate: {self.hasupdate}")

		if not self.isdownloaded or self.hasupdate:
			if not self.isdownloading:
				t = Thread(target=self.download)
				t.daemon = True
				t.start()
				self.downloadthreads.append(t)
		else:
			print("dropdown")
			dropdown = DropDown()
			deletefilesbtn = Button(text='Delete Torrent Data', size_hint_y=None, height=100, width=100)
			deletefilesbtn.bind(on_realease=self.delete_files)
			dropdown.add_widget(deletefilesbtn)
			dropdown.open(self.ids["downloadbtn"])


	def delete_files(self):
		print("delete")


	def activate_play(self):
		self.check_install_state()

		print(f"isinstalled: {self.isinstalled}")
		print(f"isinstalling: {self.isinstalling}")
		print(f"isdownloaded: {self.isdownloaded}")
		print(f"isdownloading: {self.isdownloading}")
		print(f"hasupdate: {self.hasupdate}")

		if self.isdownloaded and not self.isinstalled:
			t = Thread(target=self.install)
			t.daemon = True
			t.start()
			self.downloadthreads.append(t)
		elif self.isinstalled:
			try:
				os.startfile(os.getcwd() + self.config["files"]["install_path"] + '/' + self.game.info["title"].replace(" ", "") + '/' + self.game.get_executable())
			except Exception as e:
				print(e)



	def download(self):
		torrenthandler = TorrentHandler()
		tor = self.game.get_torrent()
		if tor != "":
			torrent_name = self.config["files"]["torrents_path"] + '/' + self.game.get_filename_with_version() + ".zip.torrent"
			f = open(torrent_name, "wb")
			torrent = b64decode(tor)
			print(f"torrent: {torrent}")
			f.write(torrent)
			f.close()
			torrenthandler.add_torrent(torrent_name)

		state = "downloading"
		while(state != "seeding"):
			status = torrenthandler.get_status(self.game.get_filename_with_version() + '.zip.torrent')
			if status is not None:
				print(f"{status.name}-> {status.state}: {status.progress}% - {status.download_rate}v | ^{status.upload_rate}")
				self.ids.progress.value = status.progress
				state = str(status.state)
			time.sleep(1)

		if self.auto_install:
			self.install()

	def install(self):
		with pyzipper.AESZipFile(self.config["files"]["torrents_data_path"] + '/' + self.game.get_filename() + '.zip', 'r', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zip:
			installdir = self.config["files"]["install_path"]
			zip.extractall(installdir, pwd=str.encode(self.game.info["password"]))
