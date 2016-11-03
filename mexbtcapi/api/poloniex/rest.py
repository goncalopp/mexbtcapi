import datetime
import importlib
import os

#dynamically load the python-poloniex module
import sys
this_module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(this_module_dir, 'python-poloniex'))
import poloniex

import mexbtcapi
from .common import PoloniexTicker, rename_dict_keys
from mexbtcapi.currency import Amount, CurrencyPair
from mexbtcapi.market import Order, Orderbook

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

def get_global_ticker():
    '''Poloniex only method for getting a ticker returns it for all currencies.
    In order to avoid wasting resources, this acts as a cache'''
    global ticker_cache, ticker_cache_updated
    now = datetime.datetime.now()
    if ticker_cache is None or (now-ticker_cache_updated) > TICKER_CACHE_TIMEOUT:
        ticker_cache = client.returnTicker()
        ticker_cache_updated = datetime.datetime.now()
    return ticker_cache, ticker_cache_updated

def get_ticker(market):
    ticker, update_time = get_global_ticker()
    cticker = ticker[market.curr_code]
    data = rename_dict_keys(cticker, POLONIEX_FIELD_MAP)
    time = update_time #no datetime on response, unfortunately
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

