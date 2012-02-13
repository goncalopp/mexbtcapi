# -*- coding: utf-8 -*-

# mtgox/arrays.py

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


import time

import numpy as np

import mtgox

def depth(currency=mtgox.CURRENCY):
    """Return limited array for ask and bid depths."""
    return _depth(currency, False)

def depth_full(currency=mtgox.CURRENCY):
    """Return limited array for ask and bid depths."""
    return _depth(currency, True)

def _depth(currency, full):
    mtgox.RETURN_TYPE=int
    if full is True:
        depth = mtgox.depth(currency)
    else:
        depth = mtgox.depth_full(currency)
    order_types = ('asks', 'bids')
    lists = [[],[]]
    for order_type in (0,1):
        for order in depth[order_types[order_type]]:
            lists[order_type].append((order['stamp'],
                                     order['price_int'],
                                     order['amount_int']
                                     ))
    asks = np.array(lists[0])
    bids = np.array(lists[1])
    return asks, bids
        
def trades(currency=mtgox.CURRENCY):
    mtgox.RETURN_TYPE=int
    list = []
    for trade in mtgox.trades(currency):
        list.append((trade['date'],
                     trade['price_int'],
                     trade['amount_int']))
    return np.array(list)
