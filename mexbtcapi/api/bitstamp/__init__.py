from mexbtcapi.market import Exchange, MarketList
from mexbtcapi.api.bitstamp.rest import CURRENCIES, BitstampMarket

class BitstampExchange(Exchange):
    def __init__(self):
        market_list = MarketList([BitstampMarket(currency) for currency in CURRENCIES])
        Exchange.__init__(self, "Bitstamp", market_list)

exchange = BitstampExchange()
