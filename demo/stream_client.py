import mexbtcapi

def my_callback(ticker):
    print "got a ticker:", ticker

market = mexbtcapi.markets.find('BTC', 'XMR')[0]
subscription = market.ticker_stream.subscribe(my_callback)
import time ; time.sleep(5)
