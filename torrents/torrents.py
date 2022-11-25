import libtorrent
import pathlib
import sys
import os
import time
from threading import Thread
from kivy.config import ConfigParser

from util import UI_UPDATE_FREQUENCY, Singleton


class TorrentHandler(metaclass=Singleton):

	def __init__(self):
		self.session = libtorrent.session({'listen_interfaces': '0.0.0.0:6881',
										   'user_agent': 'Spriggan_Client'})
		self.session.start_dht()

		print("starting torrent handler")
		self.update_ui_callback = None
		self.seeder_daemon = Thread(target=self.seeder)
		self.seeder_daemon.daemon = True
		self.seeder_daemon.start()

	def set_update_ui_callback(self, callback):
		self.update_ui_callback = callback

	def seeder(self):
		self.load_torrents()
		while (True):
			try:
				statuses = {}
				for torrent in self.session.get_torrents():
					s = torrent.status()
					statuses[s.name] = s
					print(f"{s.name}-> {s.state}: {s.progress}% - {s.download_rate}v | ^{s.upload_rate}")


				alerts = self.session.pop_alerts()
				for a in alerts:
					if a.category() & libtorrent.alert.category_t.error_notification:
						print("error: " + str(a))
				if self.update_ui_callback is not None:
					self.update_ui_callback(statuses)
				time.sleep(UI_UPDATE_FREQUENCY)

			except Exception as e:
				print(e)
				self.load_torrents()

	def get_status(self, file):
		for torrent in self.session.get_torrents():
			status = torrent.status()
			if status.name == file:
				return status

	def load_torrents(self):
		config = ConfigParser()
		config.read('config.ini')
		files = os.listdir(config.get("files", "torrents_path"))
		print("files: " + str(files))

		for file in files:
			self.add_torrent(os.path.join(config.get("files", "torrents_path"), file))

	def add_torrent(self, filename):
		config = ConfigParser()
		config.read('config.ini')
		params = libtorrent.add_torrent_params()
		if filename.startswith('magnet:'):
			params = libtorrent.parse_magnet_uri(filename)
		else:
			print("filename: " + filename)
			info = libtorrent.torrent_info(filename)
			print("name:" + info.name())
			resume_file = os.path.join(config.get("files", "torrents_path"), info.name() + '.fastresume')
			try:
				params = libtorrent.read_resume_data(open(resume_file, 'rb').read())
			except Exception as e:
				print('failed to open resume file "%s": %s' % (resume_file, e))
			params.ti = info

		params.save_path = config.get("files", "torrents_data_path")
		params.storage_mode = libtorrent.storage_mode_t.storage_mode_sparse
		params.flags |= libtorrent.torrent_flags.duplicate_is_error \
			| libtorrent.torrent_flags.auto_managed \
			| libtorrent.torrent_flags.duplicate_is_error
		# self.session.async_add_torrent(params)
		try:
			t = self.session.add_torrent(params)
		except Exception as e:
			print(e)
			print("Torrent already exists.")



	def make_torrent(self, datapath):
		config = ConfigParser()
		config.read('config.ini')
		input = os.path.abspath(datapath)
		fs = libtorrent.file_storage()

		parent_input = os.path.split(input)[0]

		libtorrent.add_files(fs, input)

		t = libtorrent.create_torrent(fs, 0, 4 * 1024 * 1024)

		t.add_tracker("udp://tracker.torrent.eu.org:451/announce")
		t.add_tracker("udp://opentor.org:2710/announce")
		t.set_creator('libtorrent (Spriggan) %s' % libtorrent.__version__)
		t.name = os.path.basename(datapath)

		libtorrent.set_piece_hashes(t, parent_input, lambda x: sys.stdout.write('.'))
		sys.stdout.write('\n')
		torrent = t.generate()
		try:
			os.mkdir(config.get("files", "torrents_path"))
		except:
			pass
		filename = config.get("files", "torrents_path") + "/" + os.path.basename(datapath) + '.torrent'
		torrent_code = libtorrent.bencode(torrent)
		f = open(filename, 'wb')
		f.write(torrent_code)
		f.close()
		self.add_torrent(filename)
		return torrent_code
