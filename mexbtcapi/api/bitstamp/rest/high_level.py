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
from functools import partial
import datetime

import mexbtcapi
from mexbtcapi import concepts
from mexbtcapi.concepts.currencies import BTC, USD
from mexbtcapi.concepts.currency import Amount, ExchangeRate
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
        if currency != USD:
            raise Exception("Currency not supported on Bitstamp: " + str(currency))
        self.xchg_factory = partial(ExchangeRate, BTC, USD)

    def json_request(self, url, data=None):
        if data is not None:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
        else:
            req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        jdata = json.load(f)
        return jdata

    def getTicker(self):
        url = _URL + "ticker"
        data = self.json_request(url)
        for x,y in [('bid','buy'),('ask','sell')]:
            data[y]= data[x]
        fields= list(BitStampTicker.RATE_FIELDS)
        fields.remove('average') #not present on Bitstamp API
        data2 = dict( [ (x, self.xchg_factory(data[x])) for x in fields] )
        data2['time']= datetime.datetime.now()
        return BitStampTicker( market=self, **data2 ) 

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
