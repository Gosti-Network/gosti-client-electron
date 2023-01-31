
from sys import platform
import uuid
import libtorrent
from kivy.config import ConfigParser
import random
import string

class Dev_Status:
	COMING_SOON = "Coming Soon"
	IN_DEVELOPMENT = "In Development"
	COMPLETE = "Complete"

class Game():

	def __init__(self, productid='', title='', shortdescription=',', description='', longdescription='', developer='', publisher='', publisherdid='',
				 website='', twitter='', discord='', instagram='', facebook='', contentrating='',
				 capsuleimage='', icon='', banner='', trailer='', tags=[], status='Coming Soon',
				 version='0.1', screenshots=[],
				 torrents={"Windows": "", "Mac": "", "Linux": ""},
				 executables={"Windows": "", "Mac": "", "Linux": ""},
				 paymentaddress='', password="temp",
				 ):
		self.copies = 1
		if productid == '':
			productid = str(uuid.uuid4())
		self.info = {
			"banner": banner,
			"capsuleimage": capsuleimage,
			"contentrating": contentrating,
			"description": description,
			"developer": developer,
			"discord": discord,
			"executables": executables,
			"facebook": facebook,
			"icon": icon,
			"instagram": instagram,
			"longdescription": longdescription,
			"password": password,
			"paymentaddress": paymentaddress,
			"productid": productid,
			"publisher": publisher,
			"publisherdid": publisherdid,
			"screenshots": screenshots,
			"shortdescription": shortdescription,
			"status": status,
			"tags": tags,
			"title": title,
			"torrents": torrents,
			"trailer": trailer,
			"twitter": twitter,
			"version": version,
			"website": website,
		}
		if password != "temp":
			self.reset_password()

	def add_copy(self):
		self.copies += 1

	def reset_password(self):
		self.info["password"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

	def from_json(info):
		g = Game()
		empty = g.info
		g.info = info
		if "productid" not in g.info:
			g.info["productid"] = str(uuid.uuid4())
		if "password" not in g.info:
			g.reset_password()

		for key in empty.keys():
			if key not in g.info:
				g.info[key] = empty[key]

		return g


	def get_filename(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"
		return self.info["title"].replace(" ", "") + '-' + p

	def get_filename_with_version(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"
		return self.info["title"].replace(" ", "") + '-v-' + self.info["version"] + '-' + p

	def get_torrent(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"

		return self.info["torrents"][p]

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
