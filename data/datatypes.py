
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

class Media():

	def __init__(self, productId='', title='', shortDescription=',', description='', longDescription='', developer='', publisher='', publisherDid='',
				 website='', twitter='', discord='', instagram='', facebook='', contentRating='',
				 capsuleImage='', icon='', banner='', trailer='', tags=[], status='Coming Soon',
				 version='0.1', screenshots=[],
				 torrents={"Windows": "", "Mac": "", "Linux": ""},
				 executables={"Windows": "", "Mac": "", "Linux": ""},
				 paymentaddress='', password="temp",
				 ):
		self.copies = 1
		if productid == '':
			productid = str(uuid.uuid4())
		self.info = {
			"mediaType": "",
			"banner": banner,
			"capsuleImage": capsuleImage,
			"contentRating": contentRating,
			"description": description,
			"creator": "",
			"discord": discord,
			"executables": executables,
			"facebook": facebook,
			"icon": icon,
			"instagram": instagram,
			"longDescription": longDescription,
			"password": password,
			"paymentAddress": "",
			"productId": productId,
			"publisher": publisher,
			"publisherDid": publisherDid,
			"screenshots": screenshots,
			"shortDescription": shortDescription,
			"status": status,
			"tags": tags,
			"title": title,
			"torrents": torrents,
			"trailer": trailer,
			"trailerSource": "",
			"twitter": twitter,
			"version": version,
			"website": website,
		}

	def from_json(info):
		g = Media()
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

