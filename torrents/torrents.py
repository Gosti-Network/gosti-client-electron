import libtorrent
import pathlib
import sys
import os
import time
from threading import Thread

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        print("ccccccc")
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TorrentHandler(metaclass=Singleton):

    def __init__(self):
        self.session = libtorrent.session({'listen_interfaces': '0.0.0.0:6881',
                                           'user_agent': 'Spriggan_Client'})
        self.session.start_dht()

        print("starting torrent handler")
        self.seeder_daemon = Thread(target=self.seeder)
        self.seeder_daemon.daemon = True
        self.seeder_daemon.start()

    def seeder(self):
        self.load_torrents()
        while (True):
            try:
                for torrent in self.session.get_torrents():
                    s = torrent.status()

                    print('\r%s - %.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
                        s.name, s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
                        s.num_peers, s.state), end=' ')
                    print("")

                    alerts = self.session.pop_alerts()
                    for a in alerts:
                        if a.category() & libtorrent.alert.category_t.error_notification:
                            print("error: " + str(a))

                    time.sleep(1)
            except:
                self.load_torrents()

    def load_torrents(self):
        torrentdir = "UserData/Torrents/"
        files = os.listdir(torrentdir)
        print("files: " + str(files))

        for file in files:
            self.add_torrent(torrentdir + file)

    def add_torrent(self, filename):
        params = libtorrent.add_torrent_params()
        if filename.startswith('magnet:'):
            params = libtorrent.parse_magnet_uri(filename)
        else:
            print("filename: " + filename)
            info = libtorrent.torrent_info(filename)
            print("name:" + info.name())
            resume_file = os.path.join("UserData/TorrentData/", info.name() + '.fastresume')
            try:
                params = libtorrent.read_resume_data(open(resume_file, 'rb').read())
            except Exception as e:
                print('failed to open resume file "%s": %s' % (resume_file, e))
            params.ti = info

        params.save_path = ".\\UserData/TorrentData"
        params.storage_mode = libtorrent.storage_mode_t.storage_mode_sparse
        params.flags |= libtorrent.torrent_flags.duplicate_is_error \
            | libtorrent.torrent_flags.auto_managed \
            | libtorrent.torrent_flags.duplicate_is_error
        # self.session.async_add_torrent(params)
        t = self.session.add_torrent(params)


    def make_torrent(self, datapath):
        input = os.path.abspath(datapath)
        fs = libtorrent.file_storage()

        parent_input = os.path.split(input)[0]

        libtorrent.add_files(fs, input)

        t = libtorrent.create_torrent(fs, 0, 4 * 1024 * 1024)

        t.add_tracker("udp://tracker.openbittorrent.com:80/announce")
        t.add_tracker("http://10.0.0.3:8000/announce")
        t.set_creator('libtorrent (Spriggan) %s' % libtorrent.__version__)
        t.name = os.path.basename(datapath)

        libtorrent.set_piece_hashes(t, parent_input, lambda x: sys.stdout.write('.'))
        sys.stdout.write('\n')
        torrent = t.generate()
        try:
            os.mkdir("UserData/Torrents/")
        except:
            pass
        filename = 'UserData/Torrents/' + os.path.basename(datapath) + '.torrent'
        torrent_code = libtorrent.bencode(torrent)
        f = open(filename, 'wb')
        f.write(torrent_code)
        f.close()

        self.add_torrent(filename)
        return torrent_code
