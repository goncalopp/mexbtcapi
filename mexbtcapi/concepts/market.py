from datetime import datetime, timedelta
from decimal import Decimal
from abc import ABCMeta, abstractmethod
import six

from mexbtcapi.concepts.currency import ExchangeRate, Amount


class Order(object):
    """Represents an order to sell a number of from_amount for exchange_rate.
    """
    TYPES = ('market', 'limit')
    def __init__(self, from_amount, exchange_rate=None, otype=None, market=None, entity=None, timestamp=None):
        assert isinstance(from_amount, Amount)
        assert exchange_rate is None or isinstance(exchange_rate, ExchangeRate)
        assert otype is None or (otype in self.TYPES)
        assert market is None or isinstance(market, Market)
        assert entity is None or isinstance(entity, Participant)
        assert timestamp is None or isinstance(timestamp, datetime)

        self.from_amount = from_amount
        self.exchange_rate = exchange_rate
        self.entity = entity
        self.otype = otype if otype else 'market' if not exchange_rate else 'limit'
        self.market = market
        self.timestamp = timestamp

        if market:
            market._order_sanity_check(self)

    @property
    def to_amount(self):
        return self.exchange_rate.convert(self.from_amount)

    @property
    def is_bid(self):
        '''returns True iff this order is buying the market's base currency
        (and selling the counter currency)'''
        return self.from_amount.currency == self.market.counter_currency

    @property
    def is_ask(self):
        '''returns True iff this order is selling the market's base currency
        (and buying the counter currency)'''
        return self.from_amount.currency == self.market.base_currency

    def __str__(self):
        try:
            to_amount = self.to_amount
        except AttributeError:
            to_amount = "?"
        return "{0} >> {1}".format(self.from_amount, to_amount)

    def __repr__(self):
        return "<{0}({1}, {2}, {3}, {4}>".format(self.__class__.__name__, self.market, self.timestamp, self.from_amount, self.exchange_rate)

@six.add_metaclass(ABCMeta)
class Market(object):
    """Represents a market.
    On a market, exactly two currencies are exchanged.
    The two currencies are known as base and counter.
    The base currency is the one around whose unit the prices are quoted.
    The counter currency is the one that varies on price quotes.

    Example: let's say a market quotes the current price as being 500 USD/BTC.
    BTC would be the base currency, and USD the counter currency"""
    class InvalidOrder(Exception):
        '''raised when there's something wrong with an order, in this
        market's context'''

    def __init__(self, market_name, base_currency, counter_currency):
        self._name = market_name
        self.base_currency = base_currency
        self.counter_currency = counter_currency

    @property
    def name(self):
        '''The name of this market. Doesn't include the currencies'''
        return self._name

    @property
    def currencies(self):
        return (self.base_currency, self.counter_currency)

    @property
    def full_name(self):
        '''The full name of this market. Includes the currencies'''
        full_name = "{_name} {base_currency}/{counter_currency}".format(**vars(self))
        return full_name

    @abstractmethod
    def get_ticker(self):
        """Returns the most recent ticker"""
        raise NotImplementedError()

    @abstractmethod
    def get_orderbook(self):
        """Returns the order book"""
        raise NotImplementedError()

    @abstractmethod
    def authenticate(self, *args, **kwargs):
        """returns a ActiveParticipant in this market"""
        raise NotImplementedError

    def _order_sanity_check(self, order):
        '''checks if an order is adequate in this market'''
        er = order.exchange_rate
        if order.market and order.market != self:
            raise self.InvalidOrder("Order on different market")
        try:
            assert set(er.currencies) == set(self.currencies)
        except AssertionError:
            raise self.InvalidOrder("Invalid order exchange rate")

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return "<{0}({1}, {2}, {3})>".format(self.__class__.__name__, self.name, self.base_currency, self.counter_currency)

class MarketList(list):
    '''A searchable list of markets'''
    def __init__(self, list_of_markets):
        assert all(isinstance(m, Market) for m in list_of_markets)
        list.__init__(self, list_of_markets)

    def find(self, currency1=None, currency2=None, exchange_name=None):
        exchange_name_lower = exchange_name.lower() if exchange_name else None
        matches = [m for m in self if
                   (currency1 is None or currency1 in m.currencies) and
                   (currency2 is None or currency2 in m.currencies) and
                   (exchange_name_lower is None or exchange_name_lower in m.name.lower())]
        return matches

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, list.__repr__(self))


@six.add_metaclass(ABCMeta)
class Participant(object):
    """Represents a participant in a market
    """
    def __init__(self, market):
        assert isinstance(market, Market)
        self.market = market


class PassiveParticipant(Participant):
    """A participant over which the user has no control
    """
    pass


@six.add_metaclass(ABCMeta)
class ActiveParticipant(Participant):
    """A participant under user control (may be the user itself)
    """
    class ActiveParticipantError(Exception):
        """Base ActiveParticipant error"""
        pass

    class OrderAlreadyClosedError(ActiveParticipantError):
        """Occurs when trying to cancel a already-closed Order"""
        pass

    class NotAuthorizedError(ActiveParticipantError):
        """Occurs when the user is not authorized to do the requested operation
        """
        pass

    @abstractmethod
    def placeOrder(self, order):
        """places an Order in the market"""
        pass

    @abstractmethod
    def cancelOrder(self, order):
        """Cancel an existing order"""
        pass

    @abstractmethod
    def getOpenOrders(self):
        """Gets all the open orders for this participant"""
        pass


class Ticker(object):
    """Ticker datapoint
    """
    # time period (in seconds) associated with aggregated fields (high, low, volume, ...)
    TIME_PERIOD = timedelta(days=1)
    RATE_FIELDS = ('bid', 'ask')
    NUMBER_FIELDS = ()

    def __init__(self, market, time, **kwargs):
        """
        market: the market this ticker is associated with
        time:   the time at which this ticker was retrieved. This is preferably
                the server time, if  available; otherwise, the local time.
                The time should always be in UTC
        kwargs: must contain all the fields defined by RATE_FIELDS and NUMBER_FIELDS
        """
        assert isinstance(market, Market)
        assert isinstance(time, datetime)
        assert all(isinstance(kwargs[k], ExchangeRate) for k in self.RATE_FIELDS)
        assert all(isinstance(kwargs[k], (int, long, float, Decimal)) for k in self.NUMBER_FIELDS)
        different_fields = set(self.RATE_FIELDS + self.NUMBER_FIELDS) ^ set(kwargs.keys())
        if different_fields:
            raise Exception("Missing/extra fields: {}".format(different_fields))
        self.market, self.time = market, time
        vars(self).update(kwargs)
        assert self.bid < self.ask

    def __repr__(self):
        return "<{cname}({time}, {dict}>".format(cname=self.__class__.__name__, time=self.time, dict=vars(self))

class OrderBook(object):
    def __init__(self, market, bid_orders, ask_orders):
        assert isinstance(market, Market)
        assert all(isinstance(x, Order) for x in bid_orders)
        assert all(isinstance(x, Order) for x in ask_orders)
        assert all(x.is_bid for x in bid_orders)
        assert all(x.is_ask for x in ask_orders)
        self.market = market
        self.bid_orders =  bid_orders
        self.ask_orders = ask_orders
