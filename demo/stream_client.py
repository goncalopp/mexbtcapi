from __future__ import print_function
import mexbtcapi

def my_callback(ticker):
    print("got a ticker:", ticker)

market = mexbtcapi.markets.find('BTC', 'ETH')[0]
print("subscribing to ticker on", market)
subscription = market.ticker_stream.subscribe(my_callback)
import time ; time.sleep(10)
print("terminating")
