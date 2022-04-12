from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

from wallet import SprigganWallet

class Wallet(BoxLayout):

	state = BooleanProperty(False)
	def __init__(self, **kwargs):
		super(Wallet, self).__init__(**kwargs)
		self.wallet = SprigganWallet()
		Clock.schedule_once(self.load, 0)

	def load(self, delay=0):
		self.address = self.wallet.get_address()
		self.balances = self.wallet.get_balances()

	def show_wallet(self):
		wallet = WalletDropDown(self.address, self.balances)
		wallet.open(self.ids.walletbutton)


class WalletDropDown(DropDown):

	def __init__(self, address, balances, **kwargs):
		super(WalletDropDown, self).__init__(**kwargs)
		self.ids.address.set_address(address)
		self.ids.address.set_owner('Your address')
		self.ids['balances'] = GridLayout(cols=1, size_hint_y=None, row_default_height=30)
		self.ids.balances.bind(minimum_height=self.ids.balances.setter('height'))
		for wallet in balances:
			self.ids.balances.add_widget(BalanceBox(wallet, balances[wallet]))

		self.ids.scroll.add_widget(self.ids.balances)


class BalanceBox(FloatLayout):

	def __init__(self, name, data, **kwargs):
		super(BalanceBox, self).__init__(**kwargs)
		if name == 'Chia Wallet':
			self.multiplier = 0.000000000001
		else:
			self.multiplier = 0.001

		self.ids.name.text = name
		self.ids.balance.text = str(data['confirmed_wallet_balance'] * self.multiplier)


class AddressBox(FloatLayout):

	def __init__(self, **kwargs):
		super(AddressBox, self).__init__(**kwargs)

	def set_address(self, address):
		self.address = address
		self.ids.address.text = address[0:6] + '...' + address[-3:len(address)]

	def set_owner(self, name):
		self.ids.owner.text = name + ':'

	def copy(self):
		Clipboard.copy(self.address)
