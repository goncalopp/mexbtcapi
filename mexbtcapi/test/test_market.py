'''Tests for market.py'''
import unittest
from mexbtcapi.market import Market, Exchange, Orderbook, Order, MarketList
from mexbtcapi.currency import Currency


class SimpleExchange(Exchange):
    '''A simple exchange class'''
    def __init__(self):
        Exchange.__init__(self, "SimpleExchange", MarketList([]))

class SimpleMarket(Market):
    '''A simple market class'''
    def __init__(self, counter_currency, base_currency, exchange=None):
        exchange = exchange or test_exchange
        Market.__init__(self, exchange, counter_currency, base_currency)

    def authenticate(self, *args, **kwargs):
        raise NotImplementedError

    def get_ticker(self):
        raise NotImplementedError

    def get_orderbook(self):
        raise NotImplementedError

#GLOBALS
test_exchange = SimpleExchange()
c1, c2 = Currency("c1"), Currency("c2")
m = SimpleMarket(c1, c2)

def craft_orderbook(bids_list, asks_list):
    '''create orderbook from two lists of tuples (amount, rate)'''
    bids_list = [Order(l[0] * c1, l[1] * c1/c2, market=m) for l in bids_list]
    asks_list = [Order(l[0] * c2, l[1] * c1/c2, market=m) for l in asks_list]
    return Orderbook(m, bids_list, asks_list)

def craft_order(amount, rate, bid=True, market=m):
    from_c = market.counter_currency if bid else market.base_currency
    return Order(amount * from_c, rate * c1 / c2, market=market)

def craft_market_order(amount, bid=True, market=m):
    from_c = market.counter_currency if bid else market.base_currency
    return Order(amount * from_c, market=market)

class MarketListTest(unittest.TestCase):
    def test_create(self):
        ml = MarketList([])
        self.assertIsInstance(ml, MarketList)

    def test_find(self):
        c3, c4, c5 = (Currency(c) for c in ('c3', 'c4', 'c5'))
        market_currencies = (c1, c2, c3, c4)
        # each market has a successive pair of currencies
        m1, m2, m3 = (SimpleMarket(cx1, cx2) for cx1, cx2 in zip(market_currencies[:-1], market_currencies[1:]))
        # ---- empty
        ml = MarketList([])
        self.assertItemsEqual(ml.find(c5), [])
        # ---- single element
        ml = MarketList([m1])
        self.assertItemsEqual(ml.find(c1), [m1])
        self.assertItemsEqual(ml.find(c2), [m1])
        self.assertItemsEqual(ml.find(c5), [])
        self.assertItemsEqual(ml.find(c1, c2), [m1])
        self.assertItemsEqual(ml.find(c2, c1), [m1])
        self.assertItemsEqual(ml.find(c1, c5), [])
        self.assertItemsEqual(ml.find(c5, c1), [])
        # ---- many elements
        ml = MarketList([m1, m2, m3])
        self.assertItemsEqual(ml.find(c1), [m1])
        self.assertItemsEqual(ml.find(c2), [m1, m2])
        self.assertItemsEqual(ml.find(c3), [m2, m3])
        self.assertItemsEqual(ml.find(c5), [])
        self.assertItemsEqual(ml.find(c5, c4), [])
        self.assertItemsEqual(ml.find(c1, c2), [m1])
        self.assertItemsEqual(ml.find(c2, c1), [m1])
        self.assertItemsEqual(ml.find(c2, c3), [m2])
        self.assertItemsEqual(ml.find(c3, c2), [m2])
        self.assertItemsEqual(ml.find(c1, c3), [])

    def test_find_double(self):
        c3, c4 = (Currency(c) for c in ('c3', 'c4'))
        market_currencies = (c1, c2, c3, c4)
        # each market has a successive pair of currencies
        m1, m2, m3 = (SimpleMarket(cx1, cx2) for cx1, cx2 in zip(market_currencies[:-1], market_currencies[1:]))
        # ---- empty
        ml = MarketList([])
        self.assertItemsEqual(ml.find(c1).find(c1), [])
        self.assertItemsEqual(ml.find(c1).find(c2), [])
        # ---- one element
        ml = MarketList([m1])
        self.assertItemsEqual(ml.find(c1).find(c1), [m1])
        self.assertItemsEqual(ml.find(c1).find(c2), [m1])
        self.assertItemsEqual(ml.find(c2).find(c1), [m1])
        self.assertItemsEqual(ml.find(c1, c2).find(c2, c1), [m1])
        self.assertItemsEqual(ml.find(c1).find(c3), [])
        self.assertItemsEqual(ml.find(c3).find(c1), [])
        # ---- many elements
        ml = MarketList([m1, m2, m3])
        self.assertItemsEqual(ml.find(c1).find(c1), [m1])
        self.assertItemsEqual(ml.find(c1).find(c2), [m1])
        self.assertItemsEqual(ml.find(c2).find(c2), [m1, m2])
        self.assertItemsEqual(ml.find(c2).find(c1), [m1])
        self.assertItemsEqual(ml.find(c2).find(c2), [m1, m2])
        self.assertItemsEqual(ml.find(c2).find(c3), [m2])
        self.assertItemsEqual(ml.find(c3).find(c3), [m2, m3])
        self.assertItemsEqual(ml.find(c3).find(c2), [m2])

    def test_find_one(self):
        c3, c4 = map(Currency, ('c3', 'c4'))
        m1, m2 = SimpleMarket(c1, c2), SimpleMarket(c2, c3)
        ml = MarketList([m1, m2])
        self.assertEqual(ml.find_one(c1), m1)
        #two results
        self.assertRaises(IndexError, lambda: ml.find_one(c2))
        self.assertEqual(ml.find_one(c3), m2)
        #zero results
        self.assertRaises(IndexError, lambda: ml.find_one(c4))

class OrderbookTest(unittest.TestCase):
    def test_create(self):
        orderbook = craft_orderbook([], [])
        self.assertIsInstance(orderbook, Orderbook)
        craft_orderbook([(3, 3), (3, 2)], [(3, 4), (3, 5)])
        self.assertIsInstance(orderbook, Orderbook)


if __name__ == '__main__':
    unittest.main()
