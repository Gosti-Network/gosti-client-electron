from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer, SimpleJSONRPCRequestHandler
# from base64 import b64encode, b64decode
# from torrents import TorrentHandler

import os
# import pyzipper

class RequestHandler(SimpleJSONRPCRequestHandler):

	def do_OPTIONS(self):
		self.send_response(200)
		self.end_headers()

	def end_headers(self):
		self.send_header("Access-Control-Allow-Headers", 
						 "Origin, X-Requested-With, Content-Type, Accept")
		self.send_header("Access-Control-Allow-Origin", "*")
		SimpleJSONRPCRequestHandler.end_headers(self)

def download(game):
		print("Downloading Game")
		print(game)

class SprigganRPC:

	def __init__(self, host, port) -> None:
		self.server = SimpleJSONRPCServer((host, port), requestHandler=RequestHandler)

	def serve(self):
		print("Starting Spriggan Python RPC")
		self.server.register_function(download)
		self.server.register_function(lambda x,y: x+y, 'add')
		print(self.server)
		self.server.serve_forever()

	
	

if __name__ == "__main__":
	SprigganRPC('localhost', 5235).serve()



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
# 			print(e)


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


