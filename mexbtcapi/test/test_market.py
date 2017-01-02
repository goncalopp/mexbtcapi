'''Tests for market.py'''
import datetime
import unittest
import six
from mexbtcapi.market import Credentials, Exchange, Market, MarketList, Orderbook, Order, Ticker, User, Wallet, ActiveParticipant
from mexbtcapi.currency import Currency


class SimpleExchange(Exchange):
    '''A simple exchange class'''
    def __init__(self, name="SimpleExchange"):
        Exchange.__init__(self, name)

    @property
    def markets(self):
        return MarketList(())

    def create_credentials(self, *args, **kwargs):
        return SimpleCredentials(*args, **kwargs)

    def authenticate_with_credentials(self, credentials):
        return SimpleUser(self, credentials)

class SimpleMarket(Market):
    '''A simple market class'''
    def __init__(self, counter_currency, base_currency, exchange=None):
        exchange = exchange or test_exchange
        Market.__init__(self, exchange, counter_currency, base_currency)

    def get_ticker(self):
        raise NotImplementedError

    def get_orderbook(self):
        raise NotImplementedError

    def authenticate_with_credentials(self, credentials):
        return SimpleActiveParticipant(self, credentials)



class SimpleWallet(Wallet):
    def __init__(self, currency=None):
        currency = currency or c1
        Wallet.__init__(self, currency)

    def get_balance(self):
        return 1 * self.currency

class SimpleCredentials(Credentials):
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

class SimpleUser(User):
    '''A simple User class for testing'''
    def __init__(self, exchange=None, credentials=None):
        exchange = exchange or test_exchange
        credentials = credentials or test_credentials
        User.__init__(self, exchange, credentials)

    def get_wallets(self):
        return {c1: SimpleWallet(c1)}

class SimpleActiveParticipant(ActiveParticipant):
    def cancel_order(self, order):
        raise NotImplementedError

    def get_open_orders(self):
        raise NotImplementedError

    def place_order(self, order):
        raise NotImplementedError


#GLOBALS
test_exchange = SimpleExchange()
test_credentials = SimpleCredentials()
c1, c2 = Currency("c1"), Currency("c2")
test_market = SimpleMarket(c1, c2)

def craft_orderbook(bids_list, asks_list):
    '''create orderbook from two lists of tuples (amount, rate)'''
    bids_list = [Order(l[0] * c1, l[1] * c1/c2, market=test_market) for l in bids_list]
    asks_list = [Order(l[0] * c2, l[1] * c1/c2, market=test_market) for l in asks_list]
    return Orderbook(test_market, bids_list, asks_list)

def craft_order(amount, rate, bid=True, market=test_market):
    from_c = market.counter_currency if bid else market.base_currency
    return Order(amount * from_c, rate * c1 / c2, market=market)

def craft_market_order(amount, bid=True, market=test_market):
    from_c = market.counter_currency if bid else market.base_currency
    return Order(amount * from_c, market=market)

def craft_ticker(bid=1, ask=2):
    ticker = Ticker(test_market, datetime.datetime.now(), bid=bid*c1/c2, ask=ask*c1/c2)
    return ticker

def assert_items_equal(testcase, iterable_a, iterable_b):
    if hasattr(testcase, 'assertItemsEqual'):
        testcase.assertItemsEqual(iterable_a, iterable_b)
    else:
        testcase.assertCountEqual(iterable_a, iterable_b)

class OrderTest(unittest.TestCase):
    def test_reverse(self):
        order = craft_order(2, 4)
        self.assertEqual(order.from_amount.value, 2)
        self.assertEqual(order.from_amount.currency, c1)
        self.assertEqual(order.to_amount.value, 0.5)
        self.assertEqual(order.to_amount.currency, c2)
        self.assertEqual(order.rate.rate, 4)
        rev = order.reverse()
        self.assertEqual(rev.from_amount.value, 0.5)
        self.assertEqual(rev.from_amount.currency, c2)
        self.assertEqual(rev.to_amount.value, 2)
        self.assertEqual(rev.to_amount.currency, c1)
        self.assertEqual(rev.rate.rate, 4)

    def test_str_repr(self):
        order = craft_order(2, 4)
        self.assertIsInstance(str(order), str)
        self.assertIsInstance(repr(order), str)
        order = Order(1*c1, None)
        self.assertIsInstance(str(order), str)
        self.assertIsInstance(repr(order), str)

    def test_eq(self):
        o1 = craft_order(2, 4)
        o2 = craft_order(2, 4)
        o3 = craft_order(2, 5)
        self.assertEqual(o1, o2)
        self.assertNotEqual(o1, o3)
        self.assertNotEqual(o1, "")

class MarketTest(unittest.TestCase):
    def test_eq(self):
        m1 = SimpleMarket(c1, c2)
        m2 = SimpleMarket(c1, c2)
        m3 = SimpleMarket(c1, c2, exchange=SimpleExchange(name="x"))
        m4 = SimpleMarket(c2, c1)
        self.assertEqual(m1, m2)
        self.assertNotEqual(m1, m3)
        self.assertNotEqual(m1, m4)
        self.assertNotEqual(m1, None)

    def test_auth(self):
        #test authenticate()
        market = SimpleMarket(c1, c2)
        participant = market.authenticate(1,2,a=3)
        self.assertIsInstance(participant, ActiveParticipant)
        self.assertEqual(participant.credentials.args, (1,2))
        self.assertEqual(participant.credentials.kwargs, {'a': 3})
        #test authenticate_with_credentials()
        creds = test_exchange.create_credentials(1,2, a=3)
        participant = market.authenticate_with_credentials(creds)
        self.assertIsInstance(participant, ActiveParticipant)
        self.assertEqual(participant.credentials.args, (1,2))
        self.assertEqual(participant.credentials.kwargs, {'a': 3})


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
        assert_items_equal(self, ml.find(c5), [])
        # ---- single element
        ml = MarketList([m1])
        assert_items_equal(self, ml.find(c1), [m1])
        assert_items_equal(self, ml.find(c2), [m1])
        assert_items_equal(self, ml.find(c5), [])
        assert_items_equal(self, ml.find(c1, c2), [m1])
        assert_items_equal(self, ml.find(c2, c1), [m1])
        assert_items_equal(self, ml.find(c1, c5), [])
        assert_items_equal(self, ml.find(c5, c1), [])
        # ---- many elements
        ml = MarketList([m1, m2, m3])
        assert_items_equal(self, ml.find(c1), [m1])
        assert_items_equal(self, ml.find(c2), [m1, m2])
        assert_items_equal(self, ml.find(c3), [m2, m3])
        assert_items_equal(self, ml.find(c5), [])
        assert_items_equal(self, ml.find(c5, c4), [])
        assert_items_equal(self, ml.find(c1, c2), [m1])
        assert_items_equal(self, ml.find(c2, c1), [m1])
        assert_items_equal(self, ml.find(c2, c3), [m2])
        assert_items_equal(self, ml.find(c3, c2), [m2])
        assert_items_equal(self, ml.find(c1, c3), [])
        assert_items_equal(self, ml.find(), [m1, m2, m3])

    def test_find_double(self):
        c3, c4 = (Currency(c) for c in ('c3', 'c4'))
        market_currencies = (c1, c2, c3, c4)
        # each market has a successive pair of currencies
        m1, m2, m3 = (SimpleMarket(cx1, cx2) for cx1, cx2 in zip(market_currencies[:-1], market_currencies[1:]))
        # ---- empty
        ml = MarketList([])
        assert_items_equal(self, ml.find(c1).find(c1), [])
        assert_items_equal(self, ml.find(c1).find(c2), [])
        # ---- one element
        ml = MarketList([m1])
        assert_items_equal(self, ml.find(c1).find(c1), [m1])
        assert_items_equal(self, ml.find(c1).find(c2), [m1])
        assert_items_equal(self, ml.find(c2).find(c1), [m1])
        assert_items_equal(self, ml.find(c1, c2).find(c2, c1), [m1])
        assert_items_equal(self, ml.find(c1).find(c3), [])
        assert_items_equal(self, ml.find(c3).find(c1), [])
        # ---- many elements
        ml = MarketList([m1, m2, m3])
        assert_items_equal(self, ml.find(c1).find(c1), [m1])
        assert_items_equal(self, ml.find(c1).find(c2), [m1])
        assert_items_equal(self, ml.find(c2).find(c2), [m1, m2])
        assert_items_equal(self, ml.find(c2).find(c1), [m1])
        assert_items_equal(self, ml.find(c2).find(c2), [m1, m2])
        assert_items_equal(self, ml.find(c2).find(c3), [m2])
        assert_items_equal(self, ml.find(c3).find(c3), [m2, m3])
        assert_items_equal(self, ml.find(c3).find(c2), [m2])

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

    def test_find_by_exchange(self):
        e1, e2 = SimpleExchange("E1"), SimpleExchange("e2")
        c3 = Currency('c3')
        m1, m2 = SimpleMarket(c1, c2, e1), SimpleMarket(c1, c2, e2)
        ml = MarketList([m1, m2])
        #simple find
        assert_items_equal(self, ml.find(exchange="E1"), (m1,))
        #simple 2
        assert_items_equal(self, ml.find(exchange="E2"), (m2,))
        #lower case
        assert_items_equal(self, ml.find(exchange="e1"), (m1,))
        #with currency, 1 result
        assert_items_equal(self, ml.find(c1, exchange="E1"), (m1,))
        #with currency, 0 results
        assert_items_equal(self, ml.find(c3, exchange="E1"), ())

    def test_repr(self):
        ml = MarketList([test_market])
        self.assertIsInstance(repr(ml), six.string_types)

    def test_str(self):
        ml = MarketList([test_market])
        self.assertIsInstance(str(ml), six.string_types)

class OrderbookTest(unittest.TestCase):
    def test_create(self):
        orderbook = craft_orderbook([], [])
        self.assertIsInstance(orderbook, Orderbook)
        craft_orderbook([(3, 3), (3, 2)], [(3, 4), (3, 5)])
        self.assertIsInstance(orderbook, Orderbook)

class ExchangeTest(unittest.TestCase):
    def test_str(self):
        self.assertIsInstance(str(test_exchange), str)
        self.assertIsInstance(repr(test_exchange), str)

    def test_eq(self):
        e1 = SimpleExchange(name="a")
        e2 = SimpleExchange(name="a")
        e3 = SimpleExchange(name="b")
        self.assertEqual(e1, e2)
        self.assertNotEqual(e1, e3)
        self.assertNotEqual(e1, None)

    def test_auth(self):
        #test authenticate()
        exchange = SimpleExchange()
        user = exchange.authenticate(1,2,a=3)
        self.assertIsInstance(user, User)
        self.assertEqual(user.credentials.args, (1,2))
        self.assertEqual(user.credentials.kwargs, {'a': 3})
        #test authenticate_with_credentials()
        creds = test_exchange.create_credentials(1,2, a=3)
        user = exchange.authenticate_with_credentials(creds)
        self.assertIsInstance(user, User)
        self.assertEqual(user.credentials.args, (1,2))
        self.assertEqual(user.credentials.kwargs, {'a': 3})

class TickerTest(unittest.TestCase):
    def test_create(self):
        ticker = craft_ticker()
        self.assertIsInstance(ticker, Ticker)

    def test_str(self):
        ticker = craft_ticker()
        self.assertIsInstance(str(ticker), str)
        self.assertIsInstance(repr(ticker), str)

class UserTest(unittest.TestCase):
    def test_create(self):
        user = SimpleUser()
        self.assertIsInstance(user, User)

    def test_get_wallets(self):
        user = SimpleUser()
        wallets = user.get_wallets()
        wallet = wallets[c1]
        self.assertIsInstance(wallet, Wallet)

    def test_auth(self):
        #test for_market()
        user = SimpleUser()
        participant = user.for_market(test_market)
        self.assertIsInstance(participant, SimpleActiveParticipant)
        self.assertEqual(user.credentials, participant.credentials)

class WalletTest(unittest.TestCase):
    def test_create(self):
        wallet = SimpleWallet(c1)
        self.assertIsInstance(wallet, Wallet)

    def test_get_balance(self):
        wallet = SimpleWallet(c1)
        balance = wallet.get_balance()
        self.assertEqual(balance, 1*c1)

if __name__ == '__main__':
    unittest.main()
