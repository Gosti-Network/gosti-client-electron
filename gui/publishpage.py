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
from chia.types.blockchain_format.sized_bytes import bytes32

import os
import shutil
import pyzipper
import json


class PublishPage(FloatLayout):
	def __init__(self, **kwargs):
		self.color_bg = COLOR_BG_DARK
		super(PublishPage, self).__init__(**kwargs)
		self.torrenthandler = TorrentHandler()
		self.games = []
		Clock.schedule_once(self.load_games, 0)

	def load_games(self, time):
		self.games = []
		self.ids.contentview.content.clear_widgets()
		self.ids['resetbtnimg'].source = "img/ResetIcon.png"
		config = ConfigParser()
		config.read('config.ini')
		self.ids.datastoreidlabel.text = config.get("publishing", "datastore_id")

		con = DataLayerConnector()
		self.games = con.get_published_games()
		for game in self.games:
			self.ids.contentview.content.add_widget(GamePublishEdit(game))

	def reset(self):
		self.load_games(0)

	def create_game(self):
		con = DataLayerConnector()
		id = con.get_datastore_id()
		self.ids.contentview.content.add_widget(GamePublishEdit())

	def create_datastore(self):
		config = ConfigParser()
		config.read('config.ini')
		con = DataLayerConnector()
		store = con.create_datastore()
		print(store)
		config.set("publishing", "datastore_id", store["id"])
		config.write()
		self.ids.datastoreidlabel.text = store["id"]
		self.load_games(0)


class GamePublishEdit(BoxLayout):
	def __init__(self, game=None):
		self.color_bg = COLOR_BG_MAIN
		super(GamePublishEdit, self).__init__(size_hint=(1, None))
		self.orientation = "vertical"
		if game is None:
			self.game = Game()
			self.editdisabled = False
		else:
			self.game = game
			self.editdisabled = True
		self.old_game = self.game
		Clock.schedule_once(self.publish_edit_update_ui, 0)

		self.revert()

		self.previewCapsule = GameCapsule(self.game)
		self.previewCapsule.pos_hint = {'x': 0, 'y': 0}
		self.ids.capsulecontainer.add_widget(self.previewCapsule)

	def publish_edit_update_ui(self, delay=0):
		print("Enable ui: " + str(self.editdisabled))
		self.ids.productid.disabled = self.editdisabled
		self.ids.title.disabled = self.editdisabled
		self.ids.description.disabled = self.editdisabled
		self.ids.longdescription.disabled = self.editdisabled
		self.ids.contentrating.disabled = self.editdisabled
		self.ids.developer.disabled = self.editdisabled
		self.ids.publisher.disabled = self.editdisabled
		self.ids.website.disabled = self.editdisabled
		self.ids.twitter.disabled = self.editdisabled
		self.ids.discord.disabled = self.editdisabled
		self.ids.instagram.disabled = self.editdisabled
		self.ids.facebook.disabled = self.editdisabled

		self.ids.capsuleimage.disabled = self.editdisabled
		self.ids.icon.disabled = self.editdisabled
		self.ids.tags.disabled = self.editdisabled
		self.ids.version.disabled = self.editdisabled
		self.ids.trailer.disabled = self.editdisabled
		self.ids.screenshots.disabled = self.editdisabled
		self.ids.fileslocationwindows.disabled = self.editdisabled
		self.ids.fileslocationmac.disabled = self.editdisabled
		self.ids.fileslocationlinux.disabled = self.editdisabled
		self.ids.fileselectbuttonwindows.disabled = self.editdisabled
		self.ids.fileselectbuttonmac.disabled = self.editdisabled
		self.ids.fileselectbuttonlinux.disabled = self.editdisabled
		self.ids.executables.disabled = self.editdisabled
		self.ids.paymentaddress.disabled = self.editdisabled
		self.ids.status.disabled = self.editdisabled
		if self.editdisabled:
			self.ids.publishbutton.text = 'Edit'
		else:
			self.ids.publishbutton.text = 'Publish'

	def publish_edit(self):
		if self.editdisabled:
			pass # start edit
		else:
			self.update_game()
			self.update_torrents()
			self.old_game = self.game
			con = DataLayerConnector()
			con.publish_game(self.game)
			# warning = ConfirmPublishPopup(self.game)
			# warning.open()

		self.editdisabled = not self.editdisabled # start edit
		self.publish_edit_update_ui()

	def update_game(self, delay=0):
		self.game.info["productid"] = self.ids['productid'].text
		self.game.info["title"] = self.ids['title'].text
		self.game.info["description"] = self.ids['description'].text
		self.game.info["longdescription"] = self.ids['longdescription'].text
		self.game.info["contentrating"] = self.ids['contentrating'].text
		self.game.info["developer"] = self.ids['developer'].text
		self.game.info["publisher"] = self.ids['publisher'].text
		self.game.info["capsuleimage"] = self.ids['capsuleimage'].text
		self.game.info["icon"] = self.ids['icon'].text
		self.game.info["tags"] = csv_to_list(self.ids['tags'].text)
		self.game.info["status"] = self.ids['status'].text
		self.game.info["version"] = self.ids['version'].text
		self.game.info["trailer"] = self.ids['trailer'].text
		self.game.info["screenshots"] = csv_to_list(self.ids['screenshots'].text)
		self.game.info["executables"] = string_to_object(self.ids['executables'].text)
		self.game.info["paymentaddress"] = self.ids['paymentaddress'].text
		self.previewCapsule.update_ui(self.game)

	def update_torrents(self, delay=0):
		config = ConfigParser()
		config.read('config.ini')
		data_path = config["files"]["torrents_data_path"]
		print("updating torrents")
		# try:
		selected = self.ids['fileslocationwindows'].text
		desired_name = self.game.get_filename()

		with open(selected + '/version.json', 'w') as f:
			v = json.dumps({'version': self.game.info["version"]})
			f.write(v)
			f.close()

		parent_folder = os.path.dirname(selected)
		contents = os.walk(selected)
		with pyzipper.AESZipFile(data_path + '/' + desired_name + '.zip', 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
			zf.setpassword(bytes(self.game.info["password"], 'utf-8'))
			for root, folders, files in contents:
				for folder_name in folders:
					absolute_path = os.path.join(root, folder_name)
					relative_path = absolute_path.replace(parent_folder + '\\', '')
					print ("Adding '%s' to archive." % absolute_path)
					zf.write(absolute_path, relative_path)
				for file_name in files:
					absolute_path = os.path.join(root, file_name)
					relative_path = absolute_path.replace(parent_folder + '\\', '')
					print ("Adding '%s' to archive." % absolute_path)
					zf.write(absolute_path, relative_path)

		self.ids['fileslocationwindows'].text = data_path + "/" + desired_name + ".zip"
		windows_torrent = self.create_torrent(self.ids['fileslocationwindows'].text)
		# except Exception as e:
		# 	print(e)
		# 	windows_torrent = self.game.info["torrents"]["Windows"]
		# 	print("Windows torrent was duplicate")
		try:
			selected = self.ids['fileslocationmac'].text
			desired_name = self.game.get_filename() + "-Mac.zip"
			if os.path.samefile(os.path.split(selected)[0], data_path):
				os.rename(selected, desired_name)
			else:
				shutil.copyfile(selected, data_path + desired_name)
			self.ids['fileslocationmac'].text = data_path + "/" + desired_name
			mac_torrent = self.create_torrent(self.ids['fileslocationmac'].text)
		except Exception as e:
			print(e)
			mac_torrent = self.game.info["torrents"]["Mac"]
			print("Mac torrent was duplicate")
		try:
			selected = self.ids['fileslocationlinux'].text
			desired_name = self.game.get_filename() + "-Linux.zip"
			if os.path.samefile(os.path.split(selected)[0], data_path):
				os.rename(selected, desired_name)
			else:
				shutil.copyfile(selected, data_path + desired_name)
			self.ids['fileslocationlinux'].text = data_path + "/" + desired_name
			linux_torrent = self.create_torrent(self.ids['fileslocationlinux'].text)
		except Exception as e:
			print(e)
			linux_torrent = self.game.info["torrents"]["Linux"]
			print("Linux torrent was duplicate")

		self.game.set_torrents({
			"Windows": windows_torrent,
			"Mac": mac_torrent,
			"Linux": linux_torrent
		})

	def revert(self):
		print(self.game.info)
		self.game = self.old_game
		self.ids['productid'].text = self.game.info["productid"]
		self.ids['title'].text = self.game.info["title"]
		self.ids['description'].text = self.game.info["description"]
		self.ids['longdescription'].text = self.game.info["longdescription"]
		self.ids['contentrating'].text = self.game.info["contentrating"]
		self.ids['developer'].text = self.game.info["developer"]
		self.ids['publisher'].text = self.game.info["publisher"]
		self.ids['capsuleimage'].text = self.game.info["capsuleimage"]
		self.ids['icon'].text = self.game.info["icon"]
		self.ids['tags'].text = list_to_csv(self.game.info["tags"])
		self.ids['status'].text = self.game.info["status"]
		self.ids['version'].text = self.game.info["version"]
		self.ids['trailer'].text = self.game.info["trailer"]
		self.ids['screenshots'].text = list_to_csv(self.game.info["screenshots"])
		try:
			self.ids['fileslocationwindows'].text = str(self.game.info["fileslocation"]["Windows"])
			self.ids['fileslocationmac'].text = str(self.game.info["fileslocation"]["Mac"])
			self.ids['fileslocationlinux'].text = str(self.game.info["fileslocation"]["Linux"])
		except:
			pass
		self.ids['executables'].text = str(self.game.info["executables"])
		self.ids['paymentaddress'].text = self.game.info["paymentaddress"]


	def show_store(self):
		page = StorePage(self.game)
		page.open()

	def select_file_location(self, platform):
		if platform == "Windows":
			page = SelectFilesPopup(self.ids['fileslocationwindows'])
		elif platform == "Mac":
			page = SelectFilesPopup(self.ids['fileslocationmac'])
		elif platform == "Linux":
			page = SelectFilesPopup(self.ids['fileslocationlinux'])
		page.open()

	def create_torrent(self, fileslocation):
		if os.path.exists(fileslocation):
			tor = TorrentHandler().make_torrent(fileslocation)
			print(tor)
		else:
			tor = b''
		return b64encode(tor).decode('utf-8')

class SelectFilesPopup(ConfirmPopup):
	def __init__(self, locationresult):
		config = ConfigParser()
		config.read('config.ini')
		super(SelectFilesPopup, self).__init__()
		self.locationresult = locationresult
		self.filechooser = FileChooserListView()
		self.filechooser.dirselect = True
		self.filechooser.path = os.getcwd() + config["files"]["install_path"]
		self.ids['layout'].add_widget(self.filechooser)

	def on_ok(self):
		try:
			self.locationresult.text = self.filechooser.selection[0]
			print("file selected: " + self.filechooser.selection)
		except:
			pass

	def on_cancel(self):
		print("cancel file select")

class ConfirmPublishPopup(ConfirmPopup):
	def __init__(self, game):
		super(ConfirmPublishPopup, self).__init__()
		self.game = game

	def on_ok(self):
		con = DataLayerConnector()
		con.publish_game(self.game)

	def on_cancel(self):
		pass
