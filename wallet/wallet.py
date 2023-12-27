from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config
from chia.util.ints import uint16
from chia.wallet.util.wallet_types import WalletType

import asyncio


class GostiWallet:
    def __init__(self):
        self.config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self.wallet_rpc_port = self.config["wallet"]["rpc_port"]
        self.datalayer_rpc_port = self.config["data_layer"]["rpc_port"]

    def get_balances(self):
        return asyncio.run(self.__get_balances())

    async def __get_balances(self):
        balances = {}
        try:
            wallet_client = await WalletRpcClient.create(
                "localhost",
                uint16(self.wallet_rpc_port),
                DEFAULT_ROOT_PATH,
                self.config,
            )
            wallets = await wallet_client.get_wallets()
            for wallet in wallets:
                balance = await wallet_client.get_wallet_balance(wallet["id"])
                balances[wallet["name"]] = balance
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
        return balances

    def get_address(self):
        return asyncio.run(self.__get_address())

    async def __get_address(self):
        try:
            wallet_client = await WalletRpcClient.create(
                "localhost",
                uint16(self.wallet_rpc_port),
                DEFAULT_ROOT_PATH,
                self.config,
            )
            wallets = await wallet_client.get_wallets()
            address = await wallet_client.get_next_address(
                wallets[0]["id"], new_address=False
            )
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
        return address

    def get_fingerprints(self):
        return asyncio.run(self.__get_fingerprints())

    async def __get_fingerprints(self):
        try:
            wallet_client = await WalletRpcClient.create(
                "localhost",
                uint16(self.wallet_rpc_port),
                DEFAULT_ROOT_PATH,
                self.config,
            )
            fingerprints_i = await wallet_client.get_public_keys()
            fingerprints = []
            for fp in fingerprints_i:
                fingerprints.append(str(fp))

        finally:
            wallet_client.close()
            await wallet_client.await_closed()
        return fingerprints

    def get_dids(self, fingerprint):
        return asyncio.run(self.__get_dids(fingerprint))

    async def __get_dids(self, fingerprint):
        try:
            wallet_client = await WalletRpcClient.create(
                "localhost",
                uint16(self.wallet_rpc_port),
                DEFAULT_ROOT_PATH,
                self.config,
            )
            wallets = await wallet_client.get_wallets(
                wallet_type=WalletType.DECENTRALIZED_ID
            )
            dids = []
            for wallet in wallets:
                did = await wallet_client.get_did_id(wallet["id"])
                dids.append(str(did["my_did"]))
        finally:
            wallet_client.close()
            await wallet_client.await_closed()
        return dids
