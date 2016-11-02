import mexbtcapi
from mexbtcapi.currencies import BTC
from mexbtcapi.currency import Amount


bitcoins = 3 * BTC
for market in mexbtcapi.markets.find(BTC):
    try:
        exchange_rate= market.get_ticker().ask
        got = exchange_rate.convert( bitcoins )
        print "At %s I can get %s for my %s (that's %s)"%(market.exchange, got, bitcoins, exchange_rate)
    except Exception as e:
        print "Failed to use "+market.full_name 
        print e
