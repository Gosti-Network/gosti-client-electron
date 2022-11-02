
from sys import platform
import uuid
import libtorrent

class Dev_Status:
	COMING_SOON = "Coming Soon"
	IN_DEVELOPMENT = "In Development"
	COMPLETE = "Complete"

class Game():

	def __init__(self, productid='', title='', description='', longdescription='', author='',
				 contentrating='', capsuleimage='', icon='', trailer='', tags=[], status='Coming Soon',
				 version='0.1', screenshots=[],
				 torrents={"Windows": "", "Mac": "", "Linux": ""},
				 executables={"Windows": "", "Mac": "", "Linux": ""},
				 paymentaddress=''):
		if productid == '':
			productid = str(uuid.uuid4())
		self.info = {
			"productid": productid,
			"title": title,
			"description": description,
			"longdescription": longdescription,
			"author": author,
			"contentrating": contentrating,
			"capsuleimage": capsuleimage,
			"icon": icon,
			"trailer": trailer,
			"tags": tags,
			"status": status,
			"version": version,
			"screenshots": screenshots,
			"torrents": torrents,
			"executables": executables,
			"paymentaddress": paymentaddress,
		}

	def from_json(info):
		g = Game()
		g.info = info
		if "productid" not in g.info:
			g.info["productid"] = str(uuid.uuid4())
		return g


	def get_filename(self):
		return self.info["title"] + '-v-' + self.info["version"]

	def get_torrent_data_filename(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"

		return self.get_filename() + "-" + p + ".zip"

	def get_torrent(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"

		return libtorrent.bencode(self.info["torrents"][p])

	def set_torrents(self, torrents):
		for p in torrents.keys():
			self.info["torrents"][p] = torrents[p]

	def get_executable(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"

		return self.info["executables"][p]


class User():

	def __init__(self, username='', profilepicture='', recieveaddress=''):
		self.username = username
		self.profilepicture = profilepicture
		self.recieveaddress = recieveaddress
