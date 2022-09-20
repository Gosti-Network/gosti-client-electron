
from sys import platform

class Dev_Status:
	COMING_SOON = "Coming Soon"
	IN_DEVELOPMENT = "In Development"
	COMPLETE = "Complete"

class Game():

	def __init__(self, title='', description='', longdescription='', author='',
				 rating=0, capsuleimage='', icon='', trailer='', tags=[], status='Coming Soon',
				 version='0.1', screenshots=[], prices={"USDS": 0.00},
				 torrents={"Windows": "", "Mac": "", "Linux": ""},
				 executables={"Windows": "", "Mac": "", "Linux": ""},
				 paymentaddress=''):
		self.title = title
		self.description = description
		self.longdescription = longdescription
		self.author = author
		self.capsuleimage = capsuleimage
		self.icon = icon
		self.trailer = trailer
		self.tags = tags
		self.status = status
		self.version = version
		self.screenshots = screenshots
		self.prices = prices
		self.torrents = torrents
		self.executables = executables
		self.paymentaddress = paymentaddress

	def get_filename(self):
		return self.title + '-v-' + self.version

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

		return self.torrents[p]

	def get_executable(self):
		p = ""
		if platform == "linux" or platform == "linux2":
			p = "Linux"
		elif platform == "darwin":
			p = "Mac"
		elif platform == "win32":
			p = "Windows"

		return self.executables[p]


class User():

	def __init__(self, username='', profilepicture='', recieveaddress=''):
		self.username = username
		self.profilepicture = profilepicture
		self.recieveaddress = recieveaddress
