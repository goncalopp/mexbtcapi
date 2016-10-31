import datetime
import importlib
import os

#dynamically load the python-poloniex module
import sys
this_module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_module_dir, 'python-poloniex'))
import poloniex

import mexbtcapi
from mexbtcapi.concepts.currency import Amount, ExchangeRate
from mexbtcapi.concepts.market import Market as Market, PassiveParticipant, Ticker

TICKER_CACHE_TIMEOUT = datetime.timedelta(seconds=1)

client = poloniex.Poloniex()
ticker_cache = None
ticker_cache_updated = datetime.datetime(year=1970, month=1, day=1)

def get_global_ticker():
    '''Poloniex only method for getting a ticker returns it for all currencies.
    In order to avoid wasting resources, this acts as a cache'''
    global ticker_cache, ticker_cache_updated
    now = datetime.datetime.now()
    if ticker_cache is None or (now-ticker_cache_updated) > TICKER_CACHE_TIMEOUT:
        ticker_cache = client.marketTicker()
        ticker_cache_updated = datetime.datetime.now()
    return ticker_cache, ticker_cache_updated

def rename_dict_keys(d, key_map):
    '''renames dictionary keys of d according to key_map'''
    d2 = {}
    for k,v in d.items():
        k = key_map.get(k, k)
        d2[k] = v
    return d2



class PoloniexTicker(Ticker):
    TIME_PERIOD = datetime.timedelta(days=1)
    RATE_FIELDS = Ticker.RATE_FIELDS + ('last', 'high', 'low')
    NUMBER_FIELDS = Ticker.NUMBER_FIELDS + ()
    POLONIEX_FIELD_MAP = {'high24hr':'high', 'highestBid':'bid', 'low24hr':'low', 'lowestAsk':'ask'}
    # TODO : support all poloniex ticker fields

class PoloniexMarket(Market):
    def __init__(self, counter_currency, base_currency):
        mexbtcapi.concepts.market.Market.__init__(self, 'Poloniex', counter_currency, base_currency)

    @property
    def curr_code(self):
        return "{}_{}".format(self.counter_currency.name, self.base_currency.name)

    def create_er(self, rate):
        return ExchangeRate(numerator_currency=self.counter_currency, denominator_currency=self.base_currency, rate=rate)

    def get_ticker(self):
        ticker, update_time = get_global_ticker()
        cticker = ticker[self.curr_code]
        data = rename_dict_keys(cticker, PoloniexTicker.POLONIEX_FIELD_MAP)
        time = update_time #no datetime on response, unfortunately
        rates = {k: self.create_er(data[k]) for k in PoloniexTicker.RATE_FIELDS}
        numbers = {k: Decimal((data[k])) for k in PoloniexTicker.NUMBER_FIELDS}
        d = {} ; d.update(rates) ; d.update(numbers)
        return PoloniexTicker(market=self, time=time, **d)

    def get_orderbook(self):
        raise NotImplementedError

    def authenticate(self):
        raise NotImplementedError
