from neo4j import GraphDatabase

from data import Game
from util import *

class DatabaseConnector:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def publish_game(self, game):
		with self.driver.session() as session:
			title = session.write_transaction(self._publish_game, game)

	def update_game(self, title, game):
		with self.driver.session() as session:
			title = session.write_transaction(self._update_game, title, game)

	def get_games(self):
		with self.driver.session() as session:
			games = session.write_transaction(self._get_games)
			return games

	@staticmethod
	def _publish_game(tx, game):
		print("Attempting Update")
		result = tx.run("Merge (g:Game {title: $title}) "
						"ON MATCH "
						"SET g.title = $title "
						"SET g.description = $description "
						"SET g.longdescription = $longdescription "
						"SET g.author = $author "
						"SET g.capsuleimage = $capsuleimage "
						"SET g.trailer = $trailer "
						"SET g.tags = $tags "
						"SET g.status = $status "
						"SET g.version = $version "
						"SET g.screenshots = $screenshots "
						"SET g.prices = $prices "
						"SET g.fileslocation = $fileslocation "
						"SET g.executables = $executables "
						"SET g.paymentaddress = $paymentaddress "
						"RETURN g.title",
						title=game.title,
						description=game.description,
						longdescription=game.longdescription,
						author=game.author,
						capsuleimage=game.capsuleimage,
						trailer=game.trailer,
						tags=game.tags,
						status=game.status,
						version=game.version,
						screenshots=game.screenshots,
						prices=str(game.prices),
						fileslocation=str(game.fileslocation),
						executables=str(game.executables),
						paymentaddress=game.paymentaddress)
		return result.single()[0]


	@staticmethod
	def _get_games(tx):
		result = tx.run("MATCH (g:Game) "
						"RETURN g.title, g.description, g.longdescription, "
						"g.author, g.capsuleimage, g.trailer, g.tags, g.status, "
						"g.version, g.screenshots, g.prices, g.fileslocation, g.executables, g.paymentaddress")

		games = {}
		for idx, record in enumerate(result):
			games[idx] = Game(title=record['g.title'],
							  description=record['g.description'],
							  longdescription=record['g.longdescription'],
							  author=record['g.author'],
							  capsuleimage=record['g.capsuleimage'],
							  trailer=record['g.trailer'],
							  tags=record['g.tags'],
							  status=record['g.status'],
							  version=record['g.version'],
							  screenshots=record['g.screenshots'],
							  prices=string_to_object(record['g.prices']),
							  fileslocation=string_to_object(record['g.fileslocation']),
							  executables=string_to_object(record['g.executables']),
							  paymentaddress=record['g.paymentaddress'])
		return games


	@staticmethod
	def _create_user(tx, user):
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
	def _update_user(tx, username, user):
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
	def _get_users(tx):
		result = tx.run("MATCH (u:User) "
						"RETURN u.username, u.profilepicture, u.recieveaddress")

		games = {}
		for idx, record in enumerate(result):
			games[idx] = User(username=record['u.username'],
							  profilepicture=record['u.profilepicture'],
							  recieveaddress=record['u.recieveaddress'])
		return games

	@staticmethod
	def _get_user(tx, username):
		result = tx.run("MATCH (u:User {username: $username}) "
						"RETURN u.username, u.profilepicture, u.recieveaddress")

		users = {}
		for idx, record in enumerate(result):
			users[idx] = User(username=record['u.username'],
							  profilepicture=record['u.profilepicture'],
							  recieveaddress=record['u.recieveaddress'])
		return users
