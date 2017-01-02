import datetime
import importlib
import os
import logging
log = logging.getLogger(__name__)

#dynamically load the python-poloniex module
import sys
this_module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_module_dir, 'python-poloniex'))
from cached_property import cached_property_with_ttl
import poloniex

import mexbtcapi
from .common import PoloniexTicker, rename_dict_keys
from mexbtcapi.currency import Amount, Currency, CurrencyPair
from mexbtcapi.market import ActiveParticipant, Order, Orderbook, User, Wallet

TICKER_CACHE_TIMEOUT = datetime.timedelta(seconds=1)
POLONIEX_FIELD_MAP = {'high24hr':'high', 'highestBid':'bid', 'low24hr':'low', 'lowestAsk':'ask'}

client = poloniex.Poloniex()
ticker_cache = None
ticker_cache_updated = datetime.datetime(year=1970, month=1, day=1)

def get_all_currency_pairs():
    '''returns in order (counter_currency, base_currency).'''
    tickers = client.returnTicker()
    pair_strs = tickers.keys()
    tuples = [s.split("_") for s in pair_strs]
    assert all(len(t) == 2 for t in tuples)
    pairs = [CurrencyPair(t[0], t[1]) for t in tuples]
    return pairs

class CachedRest(object):
    @cached_property_with_ttl(ttl=1.0)
    def global_ticker(self):
        '''Poloniex only method for getting a ticker returns it for all currencies.'''
        logging.info("Calling returnTicker")
        return client.returnTicker()



def get_ticker(market):
    ticker = cached_rest.global_ticker
    cticker = ticker[market.curr_code]
    data = rename_dict_keys(cticker, POLONIEX_FIELD_MAP)
    time = datetime.datetime.now() #no datetime on response, unfortunately
    return PoloniexTicker.from_data(data, market, time)

def get_orderbook(market):
    def row_to_order(row, bid=False):
        er_str, amount_str = row
        er = market.create_er(er_str)
        amount = Amount(amount_str, market.base_currency)
        from_amount = amount if not bid else er.convert(amount)
        order = Order(from_amount=from_amount, exchange_rate=er, market=market)
        return order
    data = client.returnOrderBook(market.curr_code)
    bids = [row_to_order(x, True)  for x in data['bids']]
    asks = [row_to_order(x, False) for x in data['asks']]
    return Orderbook(market, bids, asks)

class PoloniexWallet(Wallet):
    def __init__(self, currency, user):
        Wallet.__init__(self, currency)
        assert isinstance(user, PoloniexUser)
        self.user = user

    def get_balance(self):
        return self.user.all_balances[self.currency]

class PoloniexUser(User):
    def __init__(self, *args, **kwargs):
        User.__init__(self, *args, **kwargs)
        self.client = poloniex.Poloniex(self.credentials.api_key, self.credentials.api_secret)

    @cached_property_with_ttl(ttl=1.0)
    def all_balances(self):
        logging.info("Calling returnBalances")
        data = self.client.returnBalances()
        amounts = [Amount(v, Currency(k)) for k, v in data.items()]
        keyed_amounts = {a.currency : a for a in amounts}
        return keyed_amounts

    def get_wallets(self):
        currencies = self.all_balances.keys()
        return {c: PoloniexWallet(c, self) for c in currencies}

class PoloniexActiveParticipant(ActiveParticipant):
    def __init__(self, *args, **kwargs):
        ActiveParticipant.__init__(self, *args, **kwargs)
        self.client = poloniex.Poloniex(self.credentials.api_key, self.credentials.api_secret)

    def place_order(self, order):
        if order.rate is None:
            raise Exception("Poloniex doesn't support market orders, only limit orders")
        order = order.with_market(self.market)
        method = self.client.buy if order.is_bid else self.client.sell
        pair = order.market.curr_code
        rate = order.rate.per(order.market.base_currency)
        amount = rate.convert(order.from_amount, order.market.base_currency).value
        response = method(pair, float(rate.rate), float(amount)) 
        if 'error' in response:
            raise Exception(response['error'])
        return response

    def cancel_order(self, order):
        raise NotImplementedError

    def get_open_orders(self):
        raise NotImplementedError
 
cached_rest = CachedRest()
