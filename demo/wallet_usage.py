from __future__ import print_function
import mexbtcapi
from mexbtcapi.currencies import BTC

exchange = mexbtcapi.exchanges['Poloniex']
user = exchange.authenticate("API_KEY", "API_SECRET")
btc_wallet = user.get_wallets()[BTC]
balance = btc_wallet.get_balance()
print("The BTC balance on {} is {}".format(exchange, balance))
