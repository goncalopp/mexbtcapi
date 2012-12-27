# -*- coding: utf-8 -*-

# Copyright © 2012 EM3RY <emery@vfemail.net>
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

import base64
import hashlib
import hmac
import time
import urllib
import urllib2
import json

from decimal import Decimal

_URL = "https://mtgox.com/api/1/"
CURRENCY = "USD"
RETURN_TYPE = int

class MtGoxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class _Multiplier(dict):
    def __getitem__(self, currency_):
        if self.has_key(currency_) is True:
            return self.get(currency_)
        else:
            info = currency(currency_)
            decimals = int(info['decimals'])
            value = pow(10, decimals)
            self.update({currency_ : value})
            return value
        
multiplier = _Multiplier()

def _value_hook(values):
    d = dict()
    ideal = None
    keep = None
    drop = None
    if RETURN_TYPE in (Decimal, float):
        value = 'value'
        keep = ('amount', 'price', 'value')
        drop = ('currency', 'display', 'item', 'price_currency',
                'amount_int', 'price_int', 'value_int')
    if RETURN_TYPE is int:
        value = 'value_int'
        keep = ('amount_int', 'price_int', 'value_int')
        drop = ('currency', 'display', 'item', 'price_currency',
                'amount', 'price', 'value')
    if RETURN_TYPE is str:
        value = 'display'
        keep = ()
        drop = ('currency',
                'amount', 'price', 'value', 'item', 'price_currency',
                'amount_int', 'price_int', 'value_int')
    for k,v in values.iteritems():
        if k in drop:
            continue
        elif k in keep:
            d[k] = RETURN_TYPE(v)
        elif k in ('stamp', 'tid'):
            d[k] = int(v)
        else:
            d[k] = v
    if len(d) is 1:
        return d.values()[0]
    else:
        return d
            
def _generic(name, data=None):
    url = _URL + 'generic/public/' + name
    return _json_request(url, data)

def _specific(name, currency, data=None):
    url = _URL + 'BTC' + currency + '/public/' + name
    return _json_request(url, data)        

def _json_request(url, data=None):
    if data is not None:
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)
    f = urllib2.urlopen(req)
    jdata = json.load(f, object_hook=_value_hook)

    if jdata['result'] == 'success':
        return jdata['return']
    else:
        raise MtGoxError(jdata['error'])

def currency(currency):
    """Return info for a given currency symbol (BTC, USD, EUR)."""
    data = {'currency' : currency}
    return _generic('currency', data=data)

def depth(currency=CURRENCY):
    """Return depth for a given currency."""
    if RETURN_TYPE is str:
        pass
    else:
        return _specific('depth', currency)

def depth_full(currency=CURRENCY):
    return _specific('fulldepth', currency)

def ticker(currency=CURRENCY):
    """Return ticker for a given currency."""
    return _specific('ticker', currency)

def trades(currency=CURRENCY):
    """Return trades for a given currency."""
    return _specific('trades', currency)

def cancelled_trades(currency=CURRENCY):
    """Return a list of all the cancelled trade ids this last month."""
    return _specific('cancelledtrades', currency)


class Private:
    """Interface to a MtGox account."""
    
    def __init__(self, key, secret):
        self._key = key
        self._secret = base64.b64decode(secret)

    def _generic(self, name, data=None):
        url = _URL + 'generic/private/' + name
        return self._json_request(url, data)

    def _specific(self, name, currency, data=None):
        url = _URL + 'BTC' + currency + '/private/' + name
        return self._json_request(url, data)        
        
    def _get_signature(self, data):
        h = hmac.new(self._secret, data, hashlib.sha512)
        return base64.b64encode(h.digest())

    def _request(self, url, data):
        if data is None:
            data = {'nonce' : time.time()}
        else:
            data.update({'nonce' : time.time()})
        data = urllib.urlencode(data)
        signature = self._get_signature(data)
        
        request = urllib2.Request(url, data)
        request.add_header('Rest-Key', self._key)
        request.add_header('Rest-Sign', signature)
        return request

    def _json_request(self, url, data=None):
        req = self._request(url, data)
        f = urllib2.urlopen(req)
        jdata = json.load(f)#, object_pairs_hook=_pairs_hook)
        if jdata['result'] == 'success':
            return jdata['return']
        else:
            raise MtGoxError(jdata['error'])

    def info(self):
        """Return account info"""
        return self._generic('info')
        
    def orders(self):
        """Return standing orders"""
        return self._generic('orders')

    def cancel_ask(self, oid):
        return self._cancel(oid, 1)
    def cancel_bid(self, oid):
        return self._cancel(oid, 2)

    def _cancel(self, oid, type):
        # MtGox doesn't have a method to cancel orders for API 1.
        # type: 1 for sell order or 2 for buy order
        url = "https://mtgox.com/api/0/cancelOrder.php"
        data = {'oid' : oid,
                'type' : type}
        req = self._request(url, data)
        f = urllib2.urlopen(req)
        data = json.load(f)
        return data

    def ask(self, amount, price, currency=CURRENCY):
        """Sell bitcoins

        If price is an int, it is assumed that it is in
        an expanded format. For example, int(12300000)BTC
        is interpreted as 1.23BTC.
        """
        self._order_add('ask', amount, price, currency)
        
    def bid(self, amount, price, currency=CURRENCY):
        """Buy bitcoins
        
        If price is an int, it is assumed that it is in
        an expanded format. For example, int(12300000)BTC
        is interpreted as 1.23BTC.
        """
        self._order_add('bid', amount, price, currency)

    def _order_add(self, order_type, amount, price, currency):
        if type(amount) in (Decimal, float):
            amount = int(amount * multiplier['BTC'])
        if type(price) in (Decimal, float):
            price = int(price * multiplier[currency])
        assert type(amount) == int
        assert type(price) == int
        data = {'type' : order_type,
                'amount_int' : amount,
                'price_int' : price}
        return self._specific('order/add', currency, data)

    def withdrawl_btc(self, address, amount):
        url = "https://mtgox.com/api/0/withdraw.php"
        if type(amount) in (Decimal, float):
            amount = int(amount * multiplier['BTC'])
        assert type(amount) == int
        data = {'group1' : "BTC",
                'btca' : address,
                'amount' : amount}
        req = self._request(url, data)
        f = urllib2.urlopen(req)
        data = json.load(f)
        return data

