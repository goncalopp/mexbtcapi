from mexbtcapi.market import Exchange, MarketList
from mexbtcapi.api.bitstamp.rest import CURRENCIES, BitstampMarket

class BitstampExchange(Exchange):
    def __init__(self):
        Exchange.__init__(self, 'Bitstamp')

    @property
    def markets(self):
        return _markets

    def create_credentials(self, *args, **kwargs):
        raise NotImplementedError

    def authenticate_with_credentials(self, credentials):
        raise NotImplementedError

exchange = BitstampExchange()
_markets = MarketList(BitstampMarket(exchange, currency) for currency in CURRENCIES)
