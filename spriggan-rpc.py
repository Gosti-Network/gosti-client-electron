import json
import platform
from jsonrpclib.SimpleJSONRPCServer import (
    SimpleJSONRPCServer,
    SimpleJSONRPCRequestHandler,
)
from base64 import b64decode, b64encode

import os
import shutil

from datalayer.connector import DataLayerConnector
from torrents.torrents import TorrentHandler

from minting.minter import SprigganMinter
import pyzipper
import subprocess


class RequestHandler(SimpleJSONRPCRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def end_headers(self):
        self.send_header(
            "Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept",
        )
        self.send_header("Access-Control-Allow-Origin", "localhost")
        self.send_header("Max-Http-Header-Size", "1000000000")
        SimpleJSONRPCRequestHandler.end_headers(self)


class SprigganRPC:
    def __init__(self, host, port) -> None:
        self.server = SimpleJSONRPCServer(
            (host, port), requestHandler=RequestHandler, bind_and_activate=True
        )

        self.config = self.get_config()["config"]
        print(self.config)
        os.makedirs(os.path.dirname(self.config["mediaDataPath"]), exist_ok=True)
        os.makedirs(os.path.dirname(self.config["torrentsPath"]), exist_ok=True)
        os.makedirs(os.path.dirname(self.config["installsPath"]), exist_ok=True)

        self.torrent_handler = TorrentHandler()
        self.server.register_function(self.ping, "ping")
        self.server.register_function(self.download_media, "downloadMedia")
        self.server.register_function(self.delete_media, "deleteMedia")
        self.server.register_function(self.install_media, "installMedia")
        self.server.register_function(self.uninstall_media, "uninstallMedia")
        self.server.register_function(self.play_media, "playMedia")
        self.server.register_function(self.get_install_status, "getInstallStatus")
        self.server.register_function(self.get_local_data, "getLocalData")
        self.server.register_function(self.save_local_data, "saveLocalData")
        self.server.register_function(self.load_all_local_data, "loadAllLocalData")
        self.server.register_function(self.get_owned_datastores, "getOwnedDataStores")
        self.server.register_function(self.get_published_media, "getPublishedMedia")
        self.server.register_function(self.publish_media, "publishMedia")
        self.server.register_function(self.create_datastore, "createDatastore")
        self.server.register_function(self.generate_torrents, "generateTorrents")
        self.server.register_function(self.get_torrent_status, "getTorrentStatus")
        self.server.register_function(self.mint_nft_copies, "mintNftCopies")
        self.server.register_function(self.get_operating_system, "getOperatingSystem")
        self.server.register_function(self.get_config, "getConfig")
        self.server.register_function(self.save_config, "saveConfig")
        self.server.register_function(self.kill, "kill")

    def serve(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            print(e)

    def kill(self):
        print("kill")
        self.server.shutdown()

    def ping(self):
        print("ping")
        return {"message", "pong"}

    def download_media(self, media):
        try:
            print("Downloading: " + media["title"])
            filename = get_filename(media, get_operating_system())
            with open(
                self.config["torrentsPath"] + filename + ".torrent",
                "wb",
            ) as f:
                f.write(b64decode(s=media["torrents"][get_operating_system()]))
                f.close()

            self.torrent_handler.add_torrent(
                torrentpath=self.config["torrentsPath"], filename=filename + ".torrent"
            )
            return {"status": "Downloading"}
        except Exception as e:
            print("Error in download_media" + str(e))
            return {"status": "error", "message": "Error in download_media: " + str(e)}

    def delete_media(self, media):
        try:
            print("Deleting: " + media["title"])
            filename = get_filename(media, get_operating_system())
            os.remove(self.config["torrentsPath"] + filename + ".torrent")
            os.remove(self.config["torrentsPath"] + filename + ".zip")
            os.remove(self.config["installsPath"] + filename + ".zip")
            self.torrent_handler.remove_torrent(filename + ".torrent")
            return {"status": "Deleted"}
        except Exception as e:
            print("Error in delete_media" + str(e))
            return {"status": "error", "message": "Error in delete_media: " + str(e)}

    def install_media(self, media):
        try:
            print("Installing: " + media["title"])

            with pyzipper.AESZipFile(
                self.config["torrentsPath"]
                + "/"
                + get_filename(media, get_operating_system())
                + ".zip",
                "r",
                compression=pyzipper.ZIP_DEFLATED,
                encryption=pyzipper.WZ_AES,
            ) as zip:
                zip.extractall(
                    self.config["installsPath"]
                    + get_filename(media, get_operating_system()),
                    pwd=str.encode(media["password"]),
                )

            return {"status": "complete"}
        except Exception as e:
            print("Error in install_media" + str(e))
            return {"status": "error", "message": "Error in install_media: " + str(e)}

    def uninstall_media(self, media):
        try:
            print("Uninstalling: " + media["title"])
            filename = get_filename(media, get_operating_system())
            shutil.rmtree(self.config["installsPath"] + filename)
            return {"status": "Uninstalled"}
        except Exception as e:
            print("Error in uninstall_media" + str(e))
            return {"status": "error", "message": "Error in uninstall_media: " + str(e)}

    def play_media(self, media):
        try:
            print("Playing: " + media["title"])
            # print current working directory
            print(
                os.path.join(
                    self.config["installsPath"],
                    get_filename(media, get_operating_system()),
                    media["executables"][get_operating_system()],
                )
            )

            subprocess.Popen(
                os.path.join(
                    self.config["installsPath"],
                    get_filename(media, get_operating_system()),
                    media["executables"][get_operating_system()],
                ),
                cwd=os.path.join(
                    self.config["installsPath"],
                    get_filename(media, get_operating_system()),
                ),
            )

            return {"status": "Playing"}
        except Exception as e:
            print("Error in play_media" + str(e))
            return {"message": "Error in play_media: " + str(e), "status": "error"}

    def get_install_status(self, media):
        try:
            print("get_install_status")
            status = self.torrent_handler.get_status(
                get_filename(media, "windows") + ".zip"
            )
            print(
                f"{status.name}-> {status.state}: {status.progress}% - {status.download_rate}v | ^{status.upload_rate}"
            )

            return {
                "status": {
                    "isDownloaded": os.path.exists(
                        self.config["torrentsPath"]
                        + get_filename(media, get_operating_system())
                        + ".zip"
                    ),
                    "isDownloading": (str(status.state) == "downloading"),
                    "isInstalled": os.path.exists(
                        self.config["installsPath"]
                        + get_filename(media, get_operating_system())
                    ),
                    "isInstalling": False,
                    "hasPendingUpdate": False,
                    "isSeeding": (str(status.state) == "seeding"),
                    "progress": status.progress,
                    "downloadRate": status.download_rate,
                    "uploadRate": status.upload_rate,
                },
                "message": "Status retrieved",
            }
        except Exception as e:
            print("Error in get_install_status" + str(e))
            return {
                "status": "error",
                "message": "Error in get_install_status: " + str(e),
            }

    def get_local_data(self, productId):
        try:
            with open(self.config["mediaDataPath"] + productId + ".json", "r") as f:
                media = json.load(f)
                return {"media": media}
        except Exception as e:
            print("Error in get_local_data" + str(e))
            return {"message": "Error in get_local_data: " + str(e)}

    def save_local_data(self, media):
        try:
            with open(
                self.config["mediaDataPath"] + media["productId"] + ".json", "w"
            ) as f:
                json.dump(obj=media, fp=f)
                f.close()
                return {"status": "saved"}
        except Exception as e:
            print("Error in save_local_data" + str(e))
            return {"status": "error", "message": "Error in save_local_data: " + str(e)}

    def load_all_local_data(self):
        try:
            data = []
            for filename in os.listdir(self.config["mediaDataPath"]):
                if filename.endswith(".json"):
                    with open(self.config["mediaDataPath"] + filename, "r") as f:
                        media = json.load(f)
                        data.append(media)
            return {
                "media": data,
            }
        except Exception as e:
            print("Error in load_all_local_data" + str(e))
            return {"message": "Error in load_all_local_data: " + str(e)}

    def get_owned_datastores(self):
        try:
            dl = DataLayerConnector()
            print("getOwnedDatastores")
            result = dl.get_owned_datastores()
            return {"dataStoreIds": result}
        except Exception as e:
            print("Error in get_owned_datastores" + str(e))
            return {"message": "Error in get_owned_datastores: " + str(e)}

    def get_published_media(self, dataStoreId):
        try:
            dl = DataLayerConnector()
            print("getPublishedMedia")
            result = dl.get_published_media(dataStoreId)
            return {"media": result}
        except Exception as e:
            print("Error in get_published_media" + str(e))
            return {"message": "Error in get_published_media: " + str(e)}

    def publish_media(self, dataStoreId: str, media: dict, fee: int):
        try:
            dl = DataLayerConnector()
            print("publishMedia")
            self.save_local_data(media)
            result = dl.publish_media(datastore_id=dataStoreId, media=media, fee=fee)
            return {"message": result}
        except Exception as e:
            print("Error in publish_media" + str(e))
            return {"message": "Error in publish_media: " + str(e)}

    def create_datastore(self, fee):
        try:
            dl = DataLayerConnector()
            print("createDatastore")
            result = dl.create_datastore(fee=fee)
            return {"result": result, "success": True}
        except Exception as e:
            print(e)
            return {"result": str(e), "success": False}

    def mint_nft_copies(self, mintingConfig):
        try:
            print(mintingConfig)
            self.minter = SprigganMinter(mintingConfig)
            self.minter.start_minting()
            print("Minting Started")
            return {"status": "Minting"}
        except Exception as e:
            print("Error in mint_nft_copies" + str(e))
            return {"status": "error", "message": "Error in mint_nft_copies: " + str(e)}

    def generate_torrents(self, sourcePaths, media):
        try:
            print(self.config)
            print(sourcePaths)

            result = {}
            for operatingSystem, sourcePath in sourcePaths.items():
                if len(sourcePath) > 5:
                    desired_name = get_filename(media, operatingSystem)
                    # parent_folder = os.path.dirname(sourcePath)
                    contents = os.walk(sourcePath)
                    compressed_filename = (
                        self.config["torrentsPath"] + "/" + desired_name + ".zip"
                    )
                    with pyzipper.AESZipFile(
                        compressed_filename,
                        "w",
                        compression=pyzipper.ZIP_DEFLATED,
                        encryption=pyzipper.WZ_AES,
                    ) as zf:
                        zf.setpassword(bytes(media["password"], "utf-8"))
                        for root, folders, files in contents:
                            for folder_name in folders:
                                absolute_path = os.path.join(root, folder_name)
                                relative_path = absolute_path.replace(
                                    sourcePath + "\\", ""
                                )
                                print("Adding '%s' to archive." % absolute_path)
                                zf.write(absolute_path, relative_path)
                            for file_name in files:
                                absolute_path = os.path.join(root, file_name)
                                relative_path = absolute_path.replace(
                                    sourcePath + "\\", ""
                                )
                                print("Adding '%s' to archive." % absolute_path)
                                zf.write(absolute_path, relative_path)

                    result[operatingSystem] = b64encode(
                        self.torrent_handler.make_torrent(
                            compressed_filename, self.config["torrentsPath"]
                        )
                    ).decode("utf-8")

            return {"torrents": result}
        except Exception as e:
            print("Error in generate_torrents" + str(e))
            return {"message": "Error in generate_torrents: " + str(e)}

    def get_torrent_status(self, media):
        try:
            result = self.torrent_handler.get_status(
                get_filename(media, get_operating_system()) + ".zip"
            )
            print(result)
            return {"status": result}
        except Exception as e:
            print("Error in get_torrent_status" + str(e))
            return {
                "status": "error",
                "message": "Error in get_torrent_status: " + str(e),
            }

    def get_config(self):
        print("get_config")
        try:
            with open("./spriggan-config.json", "r") as f:
                config = json.load(f)
                return {"config": config, "message": "Config loaded from " + f.name}
        except Exception as e:
            print(e)
            return {
                "config": {
                    "marketplaces": [
                        {"url": "http://localhost:5233", "displayName": "Localhost"},
                        {
                            "url": "http://api.spriggan.club",
                            "displayName": "Spriggan Marketplace",
                        },
                    ],
                    "activeMarketplace": "Spriggan Marketplace",
                    "mintingDataPath": "./spriggan-data/minting/",
                    "mediaDataPath": "./spriggan-data/media/",
                    "torrentsPath": "./spriggan-data/torrents/",
                    "installsPath": "./spriggan-data/installs/",
                },
                "message": "Error in get_config: " + str(e),
            }

    def save_config(self, config):
        print("save_config")
        self.config = config
        try:
            with open("./spriggan-config.json", "w") as f:
                json.dump(obj=config, fp=f)
                f.close()
            return {"message": "Config saved to " + f.name}
        except Exception as e:
            print("Error in save_config" + str(e))
            return {"message": "Error in save_config: " + str(e)}

    def get_operating_system(self):
        try:
            print("get_operating_system")
            return {"os": get_operating_system()}
        except Exception as e:
            print("Error in get_operating_system" + str(e))
            return {"message": "Error in get_operating_system: " + str(e)}


def get_filename(media, operatingSystem):
    return media["productId"].replace(" ", "-") + "-" + operatingSystem


def get_operating_system():
    if platform.system() == "Windows":
        return "windows"
    elif platform.system() == "Darwin":
        return "mac"
    elif platform.system() == "Linux":
        return "linux"
    else:
        return "unknown"


if __name__ == "__main__":
    spriggan = SprigganRPC("localhost", 5235)
    TorrentHandler()
    spriggan.serve()
