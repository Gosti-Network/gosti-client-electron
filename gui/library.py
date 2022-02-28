from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

import requests
import os
import glob
import shutil
from threading import Thread
from zipfile import ZipFile
from packaging import version

from db import DatabaseConnector

LIBRARY_PATH = './Library'

NOT_INSTALLED = 0
UP_TO_DATE = 1
PENDING_UPDATE = 2
UPDATING = 3

class LibraryView(ScrollView):
	def __init__(self, **kwargs):
		super(LibraryView, self).__init__(**kwargs)
		list = LibraryList()
		list.bind(minimum_height=list.setter('height'))
		self.bar_width = 6
		self.scroll_type = ['content', 'bars']
		self.add_widget(list)
		try:
			os.mkdir(self.librarypath)
		except:
			pass # library already exists


class LibraryList(GridLayout):
	def __init__(self, **kwargs):
		super(LibraryList, self).__init__(**kwargs)
		con = DatabaseConnector("bolt://10.0.0.3:7687", "Gaerax", "password")
		self.games = con.get_games()
		con.close()
		for game in self.games:
			self.add_widget(LibraryGame(self.games[game]))


class LibraryGame(BoxLayout):
	def __init__(self, game):
		super(LibraryGame, self).__init__(size_hint=(1, None))
		self.game = game
		self.ids['title'].text = self.game.title
		self.downloadthreads = []
		self.installstate = NOT_INSTALLED
		self.check_install_state()

	def check_install_state(self):
		installs = glob.glob(LIBRARY_PATH + '/' + self.game.title + '*')
		if len(installs) > 0:
			self.installstate = UP_TO_DATE
			if (version.parse(installs[0].split('-v-')[-1]) < version.parse(self.game.version)):
				self.installstate = PENDING_UPDATE
		for thread in self.downloadthreads:
			try:
				if thread.is_alive():
					self.installstate = UPDATING
			except Exception as e:
				print(e)
		self.update_install_state(self.installstate)

	def update_install_state(self, state):
		self.installstate = state
		if state == NOT_INSTALLED:
			self.ids.activateButton.text = 'Install'
			self.ids.activateButton.disabled = False
		elif state == UP_TO_DATE:
			self.ids.activateButton.text = 'Play'
			self.ids.activateButton.disabled = False
		elif state == PENDING_UPDATE:
			self.ids.activateButton.text = 'Update'
			self.ids.activateButton.disabled = False
		elif state == UPDATING:
			self.ids.activateButton.text = ''
			self.ids.activateButton.disabled = True


	def activate(self):
		self.check_install_state()
		if self.installstate == NOT_INSTALLED or self.installstate == PENDING_UPDATE:
			self.downloadthreads.append(Thread(target=self._install).start())
		elif self.installstate == UP_TO_DATE:
			try:
				os.startfile(os.getcwd() + LIBRARY_PATH + '/' + self.game.get_filename() + '/' + self.game.executables['windows'])
			except Exception as e:
				print(e)

	def _install(self):
		existingfiles = glob.glob(LIBRARY_PATH + '/' + self.game.title + '*')
		for file in existingfiles:
			shutil.rmtree(file, ignore_errors=True)
		url = self.game.downloads['windows']
		local_filename = LIBRARY_PATH + '/' + self.game.get_filename()
		with requests.get(url, stream=True) as r:
			r.raise_for_status()
			with open(local_filename + '.zip', 'wb') as f:
				self.update_install_state(UPDATING)
				total_length = r.headers.get('content-length')
				written = 0

				for chunk in r.iter_content(chunk_size=16384):
					f.write(chunk)
					written += len(chunk)
					self.ids.progress.value = written / int(total_length)
		with ZipFile(local_filename + '.zip', 'r') as zip:
			zip.extractall(local_filename)
		os.remove(local_filename + '.zip')
		self.update_install_state(UP_TO_DATE)
