from . import currencies, rest, stream
from mexbtcapi.market import Exchange, MarketList, Market, Wallet
from mexbtcapi.currency import ExchangeRate

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

    def create_credentials(self, api_key, api_secret):
        raise NotImplementedError("Please use User.for_market instead")
        # Unfortunately we can't simply create new PoloniexCredentials here.
        # See PoloniexCredentials.client

    def authenticate_with_credentials(self, credentials):
        return rest.PoloniexActiveParticipant(self, credentials)

class PoloniexExchange(Exchange):
    def __init__(self):
        Exchange.__init__(self, 'Poloniex')

    @property
    def markets(self):
        global _markets
        return _markets

    def create_credentials(self, api_key, api_secret):
        creds = rest.PoloniexCredentials(api_key, api_secret)
        return creds

    def authenticate_with_credentials(self, credentials):
        return rest.PoloniexUser(self, credentials)

    def refresh(_):
        create_markets(refresh=True)

def create_markets(refresh=False):
    global _markets, currency_pair_code_to_market, exchange
    if refresh:
        currencies.refresh_currency_pairs()
    _markets = MarketList(PoloniexMarket(exchange, *cp) for cp in currencies.CURRENCY_PAIRS)
    stream.CURRENCY_PAIR_CODE_TO_MARKET = {m.curr_code:m for m in _markets}

_markets = MarketList([])
exchange = PoloniexExchange()
create_markets()
