from neo4j import GraphDatabase

from data import Game
from util import *
from base64 import b64encode, b64decode


class DatabaseConnector(metaclass=Singleton):
	def __init__(self):
		uri = "bolt://10.0.0.9:7687"
		user = "Gaerax"
		password = "password"
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def publish_game(self, game):
		with self.driver.session() as session:
			title = session.write_transaction(self.__publish_game, game)

	def update_game(self, title, game):
		with self.driver.session() as session:
			title = session.write_transaction(self._update_game, title, game)

	def get_games(self):
		with self.driver.session() as session:
			games = session.write_transaction(self.__get_games)
			return games

	@staticmethod
	def __publish_game(tx, game):
		print("Attempting Update")
		result = tx.run("Merge (g:Game {title: $title}) "
						"ON MATCH "
						"SET g.title = $title "
						"SET g.description = $description "
						"SET g.longdescription = $longdescription "
						"SET g.author = $author "
						"SET g.capsuleimage = $capsuleimage "
						"SET g.icon = $icon "
						"SET g.trailer = $trailer "
						"SET g.tags = $tags "
						"SET g.status = $status "
						"SET g.version = $version "
						"SET g.screenshots = $screenshots "
						"SET g.prices = $prices "
						"SET g.torrents = $torrents "
						"SET g.executables = $executables "
						"SET g.paymentaddress = $paymentaddress "
						"RETURN g.title",
						title=game.title,
						description=game.description,
						longdescription=game.longdescription,
						author=game.author,
						capsuleimage=game.capsuleimage,
						icon=game.icon,
						trailer=game.trailer,
						tags=game.tags,
						status=game.status,
						version=game.version,
						screenshots=game.screenshots,
						prices=str(game.prices),
						torrents=str(game.torrents),
						executables=str(game.executables),
						paymentaddress=game.paymentaddress)
		return result.single()[0]


	@staticmethod
	def __get_games(tx):
		result = tx.run("MATCH (g:Game) "
						"RETURN g.title, g.description, g.longdescription, "
						"g.author, g.capsuleimage, g.icon, g.trailer, g.tags, g.status, "
						"g.version, g.screenshots, g.prices, g.torrents, g.executables, g.paymentaddress")

		games = {}
		for idx, record in enumerate(result):
			games[idx] = Game(title=record['g.title'],
							  description=record['g.description'],
							  longdescription=record['g.longdescription'],
							  author=record['g.author'],
							  capsuleimage=record['g.capsuleimage'],
							  icon=record['g.icon'],
							  trailer=record['g.trailer'],
							  tags=record['g.tags'],
							  status=record['g.status'],
							  version=record['g.version'],
							  screenshots=record['g.screenshots'],
							  prices=string_to_object(record['g.prices']),
							  torrents=string_to_object(record['g.torrents']),
							  executables=string_to_object(record['g.executables']),
							  paymentaddress=record['g.paymentaddress'])
		return games


	@staticmethod
	def __create_user(tx, user):
		result = tx.run("CREATE (g:User) "
						"SET g.username = $username "
						"SET g.profilepicture = $profilepicture "
						"SET g.recieveaddress = $recieveaddress "
						"RETURN g.username",
						username=game.username,
						profilepicture=game.profilepicture,
						recieveaddress=game.recieveaddress)
		return result.single()[0]

	@staticmethod
	def __update_user(tx, username, user):
		result = tx.run("MATCH (u:User {username: $oldUsername}) "
						"SET u.username = $username "
						"SET u.profilepicture = $profilepicture "
						"SET u.recieveaddress = $recieveaddress "
						"RETURN g.username",
						oldUsername=username,
						username=game.username,
						profilepicture=game.profilepicture,
						recieveaddress=game.recieveaddress)
		return result.single()[0]

	@staticmethod
	def __get_users(tx):
		result = tx.run("MATCH (u:User) "
						"RETURN u.username, u.profilepicture, u.recieveaddress")

		games = {}
		for idx, record in enumerate(result):
			games[idx] = User(username=record['u.username'],
							  profilepicture=record['u.profilepicture'],
							  recieveaddress=record['u.recieveaddress'])
		return games

	@staticmethod
	def __get_user(tx, username):
		result = tx.run("MATCH (u:User {username: $username}) "
						"RETURN u.username, u.profilepicture, u.recieveaddress")

		users = {}
		for idx, record in enumerate(result):
			users[idx] = User(username=record['u.username'],
							  profilepicture=record['u.profilepicture'],
							  recieveaddress=record['u.recieveaddress'])
		return users
