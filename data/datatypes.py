

class Game():

	def __init__(self, title='', description='', longdescription='', author='',
				 rating=0, capsuleimage='', trailer='', tags=[], status='Coming Soon',
				 version='0.1', screenshots=[], prices={"USDS": 0.00},
				 fileslocation={"Windows": "", "Mac": "", "Linux": ""},
				 torrents={"Windows": "", "Mac": "", "Linux": ""},
				 executables={"Windows": "", "Mac": "", "Linux": ""},
				 paymentaddress=''):
		self.title = title
		self.description = description
		self.longdescription = longdescription
		self.author = author
		self.capsuleimage = capsuleimage
		self.trailer = trailer
		self.tags = tags
		self.status = status
		self.version = version
		self.screenshots = screenshots
		self.prices = prices
		self.fileslocation = fileslocation
		self.torrents = torrents
		self.executables = executables
		self.paymentaddress = paymentaddress

	def get_filename(self):
		return self.title + '-v-' + self.version


class User():

	def __init__(self, username='', profilepicture='', recieveaddress=''):
		self.username = username
		self.profilepicture = profilepicture
		self.recieveaddress = recieveaddress
