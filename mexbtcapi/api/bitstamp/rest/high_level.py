# -*- coding: utf-8 -*-

# Copyright © 2012 Petter Reinholdtsen <pere@hungry.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from decimal import Decimal
import functools
import datetime

import mexbtcapi
from mexbtcapi import concepts
from mexbtcapi.concepts.currencies import BTC, USD
from mexbtcapi.concepts.currency import Amount
from mexbtcapi.concepts.market import Market as BaseMarket, PassiveParticipant

import urllib
import urllib2
import json

MARKET_NAME= "Bitstamp"
_URL = "https://www.bitstamp.net/api/"

class BitStampTicker( concepts.market.Ticker):
    TIME_PERIOD= 24*60*60

class Market(BaseMarket):
    def __init__( self, currency ):
        mexbtcapi.concepts.market.Market.__init__(self, MARKET_NAME, BTC, currency)

    def json_request(self, url, data=None):
        if data is not None:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
        else:
            req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        jdata = json.load(f)
#        print jdata
        return jdata

    def getTicker(self):
        curname = self.c2.name
        if "USD" != curname:
            raise BitstampError("Unknown currency: " + currency)
#GET https://www.bitstamp.net/api/ticker/
# Returns JSON dictionary: 
#last - last BTC price
#high - last 24 hours price high
#low - last 24 hours price low
#volume - last 24 hours volume
#bid - highest buy order
#ask - lowest sell order
        url = _URL + "ticker"
        data = self.json_request(url)
        data['avg'] = 0 # FIXME - not available from API
        data2 = {}
        for name in ('high', 'low', 'avg', 'last', 'ask', 'bid'):
            data2[name] = concepts.currency.ExchangeRate(BTC, USD, data[name])
        time= datetime.datetime.now()
        return BitStampTicker( market=self, time=time, high=data2['high'],
                               low=data2['low'], average=data2['avg'],
                               last=data2['last'], sell=data2['ask'],
                               buy=data2['bid'] ) 

    def getOpenTrades(self):
        url = _URL + "order_book/"
        data = self.json_request(url)
#        print data
        trades = []
        # FIXME Figure out how to represent and differenciate bids and asks
        for type in ('bids', 'asks'):
            for offer in data[type]:
                rate = Decimal(offer[0])
                amount = Decimal(offer[1])
                from_amount = Amount(rate * amount, USD)
                to_amount = Amount(1 * amount, BTC)
                from_entity = None
                to_entity = None
                if 'bids' == type:
                    from_entity = PassiveParticipant(self)
                else:
                    to_entity = PassiveParticipant(self)
                trades.append(concepts.market.Trade(from_amount = from_amount,
                                                    to_amount = to_amount,
                                                    from_entity = from_entity,
                                                    to_entity = to_entity,
                                                    market=self))
        return trades
