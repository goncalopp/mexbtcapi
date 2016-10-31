from decimal import Decimal
import datetime

import mexbtcapi
from mexbtcapi.currencies import BTC, USD, EUR
from mexbtcapi.currency import Amount, ExchangeRate
from mexbtcapi.market import Market, Ticker

import urllib2
import json

CURRENCIES = {USD:'usd', EUR:'eur'}
BASE_URL = 'https://www.bitstamp.net/api/v2/{method}/btc{currency}/'

def request(url):
    r = urllib2.urlopen(url)
    data = json.load(r)
    return data

class BitstampTicker(Ticker):
    TIME_PERIOD = datetime.timedelta(days=1)
    RATE_FIELDS = Ticker.RATE_FIELDS + ('last', 'high', 'low', 'vwap', 'open')
    NUMBER_FIELDS = Ticker.NUMBER_FIELDS + ('volume',)

class BitstampMarket(Market):
    def __init__(self, exchange, currency):
        Market.__init__(self, exchange, currency, BTC)
        self.curr_code = CURRENCIES[currency]

    def create_er(self, rate):
        return ExchangeRate(numerator_currency=self.counter_currency, denominator_currency=self.base_currency, rate=rate)

    def get_ticker(self):
        url = BASE_URL.format(currency=self.curr_code, method='ticker')
        data = request(url)
        time = datetime.datetime.utcfromtimestamp(float(data['timestamp']))

        rates = {k: self.create_er(data[k]) for k in BitstampTicker.RATE_FIELDS}
        numbers = {k: Decimal((data[k])) for k in BitstampTicker.NUMBER_FIELDS}
        d = {} ; d.update(rates) ; d.update(numbers)
        return BitstampTicker(market=self, time=time, **d) 

    def get_orderbook(self):
        raise NotImplementedError

    def authenticate(self):
        raise NotImplementedError
