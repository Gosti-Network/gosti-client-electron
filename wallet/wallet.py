from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.config import load_config_cli, load_config
from chia.util.ints import uint16

import asyncio


class SprigganWallet():

	def __init__(self):
		self.config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
		self.wallet_rpc_port = self.config["wallet"]["rpc_port"]


	def get_balances(self):
		return asyncio.run(self._get_balances())

	async def _get_balances(self):
		balances = {}
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			wallets = await wallet_client.get_wallets()
			for wallet in wallets:
				balance = await wallet_client.get_wallet_balance(wallet['id'])
				balances[wallet['name']] = balance
		finally:
			wallet_client.close()
			await wallet_client.await_closed()
		return balances


	def get_address(self):
		return asyncio.run(self._get_address())

	async def _get_address(self):
		try:
			wallet_client = await WalletRpcClient.create('localhost', uint16(self.wallet_rpc_port), DEFAULT_ROOT_PATH, self.config)
			wallets = await wallet_client.get_wallets()
			address = await wallet_client.get_next_address(wallets[0]['id'], new_address=False)
		finally:
			wallet_client.close()
			await wallet_client.await_closed()
		return address
