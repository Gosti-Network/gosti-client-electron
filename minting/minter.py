import traceback

from chia.types.spend_bundle import SpendBundle
from chia.util.ints import uint16
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.byte_types import hexstr_to_bytes
from chia.util.config import load_config
from chia.util.bech32m import encode_puzzle_hash
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.wallet.util.wallet_types import WalletType
from chianft.util.mint import Minter

import os
import asyncio
from threading import Thread
from urllib.request import urlopen
import hashlib
import pickle
import json

MINTING_DATA_ROOT = "./mintingdata/"


class SprigganMinter:
    def __init__(self, mintingConfig):
        self.chia_config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self.mintingConfig = mintingConfig
        self.wallet_rpc_port = self.chia_config["wallet"]["rpc_port"]
        self.node_rpc_port = self.chia_config["full_node"]["rpc_port"]

    def start_minting(self):
        self.create_mint_spend_bundles()
        self.minter_daemon = Thread(target=self.submit_spend_bundles)
        self.minter_daemon.daemon = True
        self.minter_daemon.start()

    def stop_minting(self):
        self.minter_daemon = None

    def create_mint_spend_bundles(self):
        return asyncio.run(self.__create_mint_spend_bundles())

    async def __create_mint_spend_bundles(self):
        try:
            print("create_mint_spend_bundles")
            wallet_client = await WalletRpcClient.create(
                "localhost",
                uint16(self.wallet_rpc_port),
                DEFAULT_ROOT_PATH,
                self.chia_config,
            )
            wallets = await wallet_client.get_wallets()

            mint_wallet = None
            for wallet in wallets:
                if wallet["type"] == WalletType.NFT:
                    if "did_id" in wallet["data"]:
                        did = json.loads(wallet["data"])
                        if did["did_id"]:
                            did = encode_puzzle_hash(
                                hexstr_to_bytes(did["did_id"]), "did:chia:"
                            )
                        if did == self.mintingConfig["publisherDid"]:
                            mint_wallet = wallet["id"]
            print(f"mint wallet: {mint_wallet}")

            if mint_wallet is None:
                print("Failed to find DID NFT wallet")
                response = await wallet_client.create_new_nft_wallet(
                    self.mintingConfig["publisherDid"], name="Spriggan Mint"
                )
                print(response)
                wallets = await wallet_client.get_wallets()
                for wallet in wallets:
                    if wallet["id"] == response["wallet_id"]:
                        mint_wallet = wallet["id"]

            print(f"mint wallet: {mint_wallet}")

            node_client = await FullNodeRpcClient.create(
                "localhost",
                uint16(self.node_rpc_port),
                DEFAULT_ROOT_PATH,
                self.chia_config,
            )

            filename = MINTING_DATA_ROOT + "minting_metadata.csv"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(
                    "hash,uris,meta_hash,meta_uris,license_hash,"
                    + "license_uris,edition_number,edition_total\n"
                )

                data_uris = self.mintingConfig["imageUris"]
                response = urlopen(data_uris[0])
                data_hash = hashlib.sha256(response.read()).hexdigest()
                metadata_uris = self.mintingConfig["metadataUris"]
                response = urlopen(metadata_uris[0])
                metadata_hash = hashlib.sha256(response.read()).hexdigest()
                license_uris = self.mintingConfig["licenseUris"]
                response = urlopen(license_uris[0])
                license_hash = hashlib.sha256(response.read()).hexdigest()
                mint_quantity = int(self.mintingConfig["quantity"])
                royalty_percentage = int(
                    float(self.mintingConfig["royaltyPercentage"]) * 100
                )
                royalty_address = self.mintingConfig["royaltyAddress"]
                batch_size = self.mintingConfig["batchSize"]

                print("here: " + str(mint_quantity))

                for i in range(0, mint_quantity):
                    f.write(
                        f"{data_hash},{data_uris[0]},{metadata_hash},"
                        + f"{metadata_uris[0]},{license_hash},{license_uris[0]},{0},{0}\n"
                    )

                f.close()

            minter = Minter(wallet_client=wallet_client, node_client=node_client)

            spend_bundles = await minter.create_spend_bundles(
                metadata_input=filename,
                bundle_output=MINTING_DATA_ROOT + "minting_spend_bundles_output.pkl",
                wallet_id=mint_wallet,
                mint_from_did=True,
                royalty_address=royalty_address,
                royalty_percentage=royalty_percentage,
                has_targets=False,
                chunk=batch_size,
            )
            with open(
                MINTING_DATA_ROOT + "minting_spend_bundles_output.pkl", "wb"
            ) as f:
                pickle.dump(spend_bundles, f)
                print(
                    "Successfully created {} spend bundles".format(len(spend_bundles))
                )
        except Exception as e:
            print(traceback.format_exc())
            return e
        finally:
            node_client.close()
            wallet_client.close()
            await node_client.await_closed()
            await wallet_client.await_closed()

    def submit_spend_bundles(self):
        return asyncio.run(self.__submit_spend_bundles())

    async def __submit_spend_bundles(self):
        print("__submit_spend_bundles")
        error = None
        try:
            wallet_client = await WalletRpcClient.create(
                "localhost",
                uint16(self.wallet_rpc_port),
                DEFAULT_ROOT_PATH,
                self.chia_config,
            )
            node_client = await FullNodeRpcClient.create(
                "localhost",
                uint16(self.node_rpc_port),
                DEFAULT_ROOT_PATH,
                self.chia_config,
            )
            spends = []
            with open(
                MINTING_DATA_ROOT + "minting_spend_bundles_output.pkl", "rb"
            ) as f:
                spends_bytes = pickle.load(f)

            for spend_bytes in spends_bytes:
                spends.append(SpendBundle.from_bytes(spend_bytes))

            minter = Minter(wallet_client, node_client)

            fee_amount = int(self.mintingConfig["fee"])
            print(fee_amount)
            sell_amount = int(float(self.mintingConfig["salePrice"]) * 1000000000000)
            print(sell_amount)
            print(spends)
            await minter.submit_spend_bundles(spends, fee_amount)
        except Exception as e:
            print(traceback.format_exc())
            error = e

        finally:
            node_client.close()
            wallet_client.close()
            await node_client.await_closed()
            await wallet_client.await_closed()
            if error:
                return error
            else:
                return "success"
