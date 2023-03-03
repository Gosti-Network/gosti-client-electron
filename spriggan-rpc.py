import datetime
import json
from threading import Thread
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
import http.server
from base64 import b64encode, b64decode
# from torrents import TorrentHandler

import os
import traceback

from datalayer.connector import DataLayerConnector
from torrents.torrents import TorrentHandler
from wallet.wallet import SprigganWallet
from minting.minter import SprigganMinter
import pyzipper

class RequestHandler(SimpleJSONRPCRequestHandler):

	def do_OPTIONS(self):
		self.send_response(200)
		self.end_headers()

	def end_headers(self):
		self.send_header("Access-Control-Allow-Headers", 
						 "Origin, X-Requested-With, Content-Type, Accept")
		self.send_header("Access-Control-Allow-Origin", "*")
		SimpleJSONRPCRequestHandler.end_headers(self)


class SprigganRPC:

	def __init__(self, host, port) -> None:
		self.server = SimpleJSONRPCServer((host, port), requestHandler=RequestHandler, bind_and_activate=True)
		self.server.register_function(self.ping, 'ping')
		self.server.register_function(self.downloadMedia, 'downloadMedia')
		self.server.register_function(self.getLocalData, 'getLocalData')
		self.server.register_function(self.saveLocalData, 'saveLocalData')
		self.server.register_function(self.getOwnedDatastores, 'getOwnedDatastores')
		self.server.register_function(self.getPublishedMedia, 'getPublishedMedia')
		self.server.register_function(self.publishMedia, 'publishMedia')
		self.server.register_function(self.createDatastore, 'createDatastore')
		self.server.register_function(self.generateTorrents, 'generateTorrents')
		self.server.register_function(self.mintNftCopies, 'mintNftCopies')

	def serve(self):
		self.server.serve_forever()

	def ping(self):
		print("ping")
		return True

	def downloadMedia(media):
		print("Downloading Media")
		print(media)

	def getLocalData(self, productId):
		try:
			with open("./mediaData/" + productId + ".json", 'r') as f:
				media = json.load(f)
				print(media)
				return {"result": media, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}

	def saveLocalData(self, media):
		try:
			os.makedirs(os.path.dirname("./mediaData/"), exist_ok=True)
			with open("./mediaData/" + media['productId'] + ".json", 'w') as f:
				json.dumps(media, f)	
				f.close()
				return {"result": {}, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}

	def getOwnedDatastores(self):
		try:
			dl = DataLayerConnector()
			print("getOwnedDatastores")
			result = dl.get_owned_datastores()
			return {"result": result, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}
	
	def getPublishedMedia(self, datastoreId):
		try:
			dl = DataLayerConnector()
			print("getPublishedMedia")
			result = dl.get_published_media(datastoreId)
			return {"result": result, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}
	
	def publishMedia(self, datastoreId, media):
		try:
			dl = DataLayerConnector()
			print("publishMedia")
			result = dl.publish_media(datastoreId, media)
			return {"result": result, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}
	
	def createDatastore(self):
		try:
			dl = DataLayerConnector()
			print("createDatastore")
			result = dl.create_datastore()
			return {"result": result, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}

	def mintNftCopies(self, mintingConfig):
		try:
			print(mintingConfig)
			self.minter = SprigganMinter(mintingConfig)
			time = str(datetime.timedelta(seconds=int(min(float(mintingConfig["quantity"]) / 25.0, 1) * 52)))
			val = self.minter.start_minting()
			print("Minting Started")
			print(val)
			return {"result": val, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}
	
	def generateTorrents(self, sourcePaths, media):
		print("generateTorrents")
		print("media v")
		print(media)
		try:
			config = self.getConfig()["result"]
			print(config)
			torrenthandler = TorrentHandler()
			result = {}
			for operatingSystem, sourcePath in sourcePaths.items():
				if len(sourcePath) > 5:
					desired_name = get_filename(media, operatingSystem)
					parent_folder = os.path.dirname(sourcePath)
					contents = os.walk(sourcePath)
					compressed_filename = config["torrentsPath"] + '/' + desired_name + '.zip'
					with pyzipper.AESZipFile(compressed_filename, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
						zf.setpassword(bytes(media["password"], 'utf-8'))
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

					result[operatingSystem] = b64encode(torrenthandler.make_torrent(compressed_filename, config["torrentsPath"])).decode('utf-8')

			return {"result": result, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}
	
	def getConfig(self):
		print("getConfig")
		try:
			with open("./spriggan-config.json", 'r') as f:
				config = json.load(f)
				return {"result": config, "success": True}
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}

	def saveConfig(self, config):
		print("getConfig")
		try:
			with open("./spriggan-config.json", 'w') as f:
				json.dumps(config, f)	
				f.close()
			return True
		except Exception as e:
			print(traceback.format_exc())
			return {"result": str(e), "success": False}


def get_filename(media, operatingSystem):
	return media["title"].replace(" ", "-") + '-v-' + media["version"] + '-' + operatingSystem

if __name__ == "__main__":
	spriggan = SprigganRPC('localhost', 5235)
	TorrentHandler()
	spriggan.serve()

	# def update_torrents(self, delay=0):
	# 	data_path = config["torrentsPath"]
	# 	print("updating torrents")
	# 	# try:
	# 	selected = sourcePaths["windows"]
	# 	desired_name = self.game.get_filename()

	# 	with open(selected + '/version.json', 'w') as f:
	# 		v = json.dumps({'version': self.game.info["version"]})
	# 		f.write(v)
	# 		f.close()

	# 	parent_folder = os.path.dirname(selected)
	# 	contents = os.walk(selected)
	# 	with pyzipper.AESZipFile(data_path + '/' + desired_name + '.zip', 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
	# 		zf.setpassword(bytes(self.game.info["password"], 'utf-8'))
	# 		for root, folders, files in contents:
	# 			for folder_name in folders:
	# 				absolute_path = os.path.join(root, folder_name)
	# 				relative_path = absolute_path.replace(parent_folder + '\\', '')
	# 				print ("Adding '%s' to archive." % absolute_path)
	# 				zf.write(absolute_path, relative_path)
	# 			for file_name in files:
	# 				absolute_path = os.path.join(root, file_name)
	# 				relative_path = absolute_path.replace(parent_folder + '\\', '')
	# 				print ("Adding '%s' to archive." % absolute_path)
	# 				zf.write(absolute_path, relative_path)

	# 	self.ids['fileslocationwindows'].text = data_path + "/" + desired_name + ".zip"
	# 	windows_torrent = self.create_torrent(self.ids['fileslocationwindows'].text)
	# 	# except Exception as e:
	# 	# 	print(traceback.format_exc())
	# 	# 	windows_torrent = self.game.info["torrents"]["Windows"]
	# 	# 	print("Windows torrent was duplicate")
	# 	try:
	# 		selected = self.ids['fileslocationmac'].text
	# 		desired_name = self.game.get_filename() + "-Mac.zip"
	# 		if os.path.samefile(os.path.split(selected)[0], data_path):
	# 			os.rename(selected, desired_name)
	# 		else:
	# 			shutil.copyfile(selected, data_path + desired_name)
	# 		self.ids['fileslocationmac'].text = data_path + "/" + desired_name
	# 		mac_torrent = self.create_torrent(self.ids['fileslocationmac'].text)
	# 	except Exception as e:
	# 		print(traceback.format_exc())
	# 		mac_torrent = self.game.info["torrents"]["Mac"]
	# 		print("Mac torrent was duplicate")
	# 	try:
	# 		selected = self.ids['fileslocationlinux'].text
	# 		desired_name = self.game.get_filename() + "-Linux.zip"
	# 		if os.path.samefile(os.path.split(selected)[0], data_path):
	# 			os.rename(selected, desired_name)
	# 		else:
	# 			shutil.copyfile(selected, data_path + desired_name)
	# 		self.ids['fileslocationlinux'].text = data_path + "/" + desired_name
	# 		linux_torrent = self.create_torrent(self.ids['fileslocationlinux'].text)
	# 	except Exception as e:
	# 		print(traceback.format_exc())
	# 		linux_torrent = self.game.info["torrents"]["Linux"]
	# 		print("Linux torrent was duplicate")

	# 	self.game.set_torrents({
	# 		"Windows": windows_torrent,
	# 		"Mac": mac_torrent,
	# 		"Linux": linux_torrent
	# 	})

# def activate_play(self):
# 	self.check_install_state()

# 	print(f"isinstalled: {self.isinstalled}")
# 	print(f"isinstalling: {self.isinstalling}")
# 	print(f"isdownloaded: {self.isdownloaded}")
# 	print(f"isdownloading: {self.isdownloading}")
# 	print(f"hasupdate: {self.hasupdate}")

# 	if self.isdownloaded and not self.isinstalled:
# 		t = Thread(target=self.install)
# 		t.daemon = True
# 		t.start()
# 		self.downloadthreads.append(t)
# 	elif self.isinstalled:
# 		try:
# 			os.startfile(os.getcwd() + self.config["files"]["install_path"] + '/' + self.game.info["title"].replace(" ", "") + '/' + self.game.get_executable())
# 		except Exception as e:
# 			print(traceback.format_exc())


# torrenthandler = TorrentHandler()
# tor = game.get_torrent()
# if tor != "":
# 	torrent_name = self.config["files"]["torrents_path"] + '/' + self.game.get_filename_with_version() + ".zip.torrent"
# 	f = open(torrent_name, "wb")
# 	torrent = b64decode(tor)
# 	print(f"torrent: {torrent}")
# 	f.write(torrent)
# 	f.close()
# 	torrenthandler.add_torrent(torrent_name)

# state = "downloading"
# while(state != "seeding"):
# 	status = torrenthandler.get_status(self.game.get_filename_with_version() + '.zip.torrent')
# 	if status is not None:
# 		print(f"{status.name}-> {status.state}: {status.progress}% - {status.download_rate}v | ^{status.upload_rate}")
# 		self.ids.progress.value = status.progress
# 		state = str(status.state)
# 	time.sleep(1)

# if self.auto_install:
# 	self.install()

# def install(self):
# 	with pyzipper.AESZipFile(self.config["files"]["torrents_data_path"] + '/' + self.game.get_filename() + '.zip', 'r', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zip:
# 		installdir = self.config["files"]["install_path"]
# 		zip.extractall(installdir, pwd=str.encode(self.game.info["password"]))


# def launch():
# 	os.startfile(os.getcwd() + self.config["files"]["install_path"] + '/' + self.game.info["title"].replace(" ", "") + '/' + self.game.get_executable())


