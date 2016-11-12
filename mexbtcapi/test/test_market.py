'''Tests for market.py'''
import unittest
from mexbtcapi.market import Market, Exchange, Orderbook, Order, MarketList
from mexbtcapi.currency import Currency


class TestExchange(Exchange):
    '''A simple exchange class'''
    def __init__(self):
        Exchange.__init__(self, "TestExchange", MarketList([]))

class TestMarket(Market):
    '''A simple market class'''
    def __init__(self, counter_currency, base_currency):
        Market.__init__(self, test_exchange, counter_currency, base_currency)

    def authenticate(self, *args, **kwargs):
        raise NotImplementedError

    def get_ticker(self):
        raise NotImplementedError

    def get_orderbook(self):
        raise NotImplementedError

test_exchange = TestExchange()
c1, c2 = Currency("c1"), Currency("c2")
m = TestMarket(c1, c2)

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

def craft_state(bids_list, asks_list):
    return MarketSimulationState(craft_orderbook(bids_list, asks_list))

class OrderbookTest(unittest.TestCase):
    def test_create(self):
        orderbook = craft_orderbook([], [])
        self.assertIsInstance(orderbook, Orderbook)
        craft_orderbook([(3, 3), (3, 2)], [(3, 4), (3, 5)])
        self.assertIsInstance(orderbook, Orderbook)


if __name__ == '__main__':
    unittest.main()
