from . import rest, stream
from .currencies import CURRENCY_PAIRS
from mexbtcapi.market import Credentials, Exchange, MarketList, Market, Wallet
from mexbtcapi.currency import ExchangeRate

class PoloniexCredentials(Credentials):
    def __init__(self, api_key, api_secret):
        self.api_key, self.api_secret = api_key, api_secret

class PoloniexWallet(Wallet):
    def get_balance(self):
        curr_code = self.currency.name

class PoloniexMarket(Market):
    def __init__(self, exchange, counter_currency, base_currency):
        Market.__init__(self, exchange, counter_currency, base_currency)

    @property
    def curr_code(self):
        return "{}_{}".format(self.counter_currency.name, self.base_currency.name)

    def create_er(self, rate):
        return ExchangeRate(numerator_currency=self.counter_currency, denominator_currency=self.base_currency, rate=rate)

    def get_ticker(self):
        return rest.get_ticker(self)

    @property
    def ticker_stream(self):
        return stream.get_ticker_stream_for_market(self.curr_code)

    def get_orderbook(self):
        return rest.get_orderbook(self)

    def authenticate(self, api_key, api_secret):
        creds = PoloniexCredentials(api_key, api_secret)
        return rest.PoloniexActiveParticipant(self, creds)

class PoloniexExchange(Exchange):
    def __init__(self):
        Exchange.__init__(self, 'Poloniex')

    @property
    def markets(self):
        return _markets

    def authenticate(self, api_key, api_secret):
        creds = PoloniexCredentials(api_key, api_secret)
        return rest.PoloniexUser(self, creds)

exchange = PoloniexExchange()
_markets = MarketList(PoloniexMarket(exchange, *cp) for cp in CURRENCY_PAIRS)
stream.CURRENCY_PAIR_CODE_TO_MARKET = {m.curr_code:m for m in exchange.markets}
