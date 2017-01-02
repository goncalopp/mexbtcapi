from __future__ import print_function
import mexbtcapi
from mexbtcapi.currencies import BTC
from mexbtcapi.currency import Amount


bitcoins = 3 * BTC
for market in mexbtcapi.markets.find(BTC):
    try:
        exchange_rate= market.get_ticker().ask
        got = exchange_rate.convert( bitcoins )
        print("At", market.exchange, "I can get", got, "for my", bitcoins, "(that's ", exchange_rate, ")")
    except NotImplementedError as e:
        print("Failed to use", market.full_name) 
        print(e)
