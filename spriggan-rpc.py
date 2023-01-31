from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer

from torrents import TorrentHandler

server = SimpleJSONRPCServer(('localhost', 5235), bind_and_activate=False)
server.server_bind()
server.server_activate()

torrent_handler = TorrentHandler()

def load_games():


server.register_function(lambda x,y: x-y, 'subtract')
server.serve_forever()
