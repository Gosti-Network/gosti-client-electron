from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.config import ConfigParser
from kivy.uix.settings import Settings

from kivy.clock import Clock

from kivy.graphics import Color

from util import *

from datalayer import DataLayerConnector
from wallet import *
import asyncio
import json


class SettingsPage(BoxLayout):
	def __init__(self, **kwargs):
		super(SettingsPage, self).__init__(**kwargs)
		config = ConfigParser()
		config.setdefaults('files', {
			"install_path": './UserData/InstalledGames/',
			"torrents_data_path": './UserData/Torrents/',
			"torrents_path": './UserData/TorrentData/'
		})
		config.read('config.ini')
		wallet = SprigganWallet()
		fingerprints = wallet.get_fingerprints()
		dids = wallet.get_dids(config.get("wallet", "fingerprint"))

		connector = DataLayerConnector()
		datastores = connector.get_owned_datastores()

		marketplacesettings = json.dumps([
			{
				"type": "options",
				"title": "fingerprint",
				"desc": "Your wallet fingerprint",
				"section": "wallet",
				"key": "fingerprint",
				"options": fingerprints
			},
			{
				"type": "options",
				"title": "DID",
				"desc": "Your DID",
				"section": "wallet",
				"key": "did",
				"options": dids
			}
		])


		walletsettings = json.dumps([
			{
				"type": "options",
				"title": "fingerprint",
				"desc": "Your wallet fingerprint",
				"section": "wallet",
				"key": "fingerprint",
				"options": fingerprints
			},
			{
				"type": "options",
				"title": "DID",
				"desc": "Your DID",
				"section": "wallet",
				"key": "did",
				"options": dids
			}
		])

		filesettings = json.dumps([
			{
				"type": "path",
				"title": "Install Path",
				"desc": "Where games will be installed",
				"section": "files",
				"key": "install_path"
			},
			{
				"type": "path",
				"title": "Torrent Data Path",
				"desc": "Where downloaded torrent data will be stored",
				"section": "files",
				"key": "torrents_data_path"
			},
			{
				"type": "path",
				"title": "Torrents Path",
				"desc": "Where torrent files will be stored",
				"section": "files",
				"key": "torrents_path"
			}
		])

		publishingsettings = json.dumps([
			{
				"type": "bool",
				"title": "Enable Publishing",
				"desc": "Enable publishing section (Must restart Spriggan to see changes)",
				"section": "publishing",
				"key": "enabled"
			},
			{
				"type": "options",
				"title": "Datastore ID",
				"desc": "Your DataLayer ID",
				"section": "publishing",
				"key": "datastore_id",
				"options": datastores
			},
			{
				"type": "path",
				"title": "Minting Data Path",
				"desc": "Where torrent files will be stored",
				"section": "publishing",
				"key": "minting_data_path"
			}
		])

		self.settings = Settings()
		self.settings.add_json_panel('Wallet', config, data=walletsettings)
		self.settings.add_json_panel('Files', config, data=filesettings)
		self.settings.add_json_panel('Publishing', config, data=publishingsettings)
		Clock.schedule_once(self.load_settings, 0)

	def load_settings(self, time):
		self.add_widget(self.settings)
		self.settings.on_close = self.parent.parent.parent.dismiss
