'''
This module exposes several classes related to currency markets
'''

from datetime import datetime, timedelta
from decimal import Decimal
from abc import ABCMeta, abstractmethod
from collections import defaultdict
import copy
import six

from mexbtcapi.currency import ExchangeRate, Amount, Currency, CurrencyPair
from mexbtcapi import pubsub
from mexbtcapi.util import group_by


class Order(object):
    """Represents an order to sell a number of from_amount for exchange_rate.
    If exchange_rate is not defined, this represents a market order (i.e.: to be executed
    at any available rate)
    """
    class ExecutionError(Exception):
        '''Raised when there's a problem executing a order'''
        pass
    def __init__(self, from_amount, exchange_rate=None, market=None, entity=None, timestamp=None):
        assert isinstance(from_amount, Amount)
        assert exchange_rate is None or isinstance(exchange_rate, ExchangeRate)
        assert market is None or isinstance(market, Market)
        assert entity is None or isinstance(entity, Participant)
        assert timestamp is None or isinstance(timestamp, datetime)

        self.from_amount = from_amount
        self.exchange_rate = exchange_rate
        self.entity = entity
        self._market = market
        self.timestamp = timestamp
        self._sanity_check()


    def _sanity_check(self):
        assert self.from_amount.value >= 0
        if self._market is not None:
            self._market.check_order_valid(self)

    @property
    def to_amount(self):
        return self.exchange_rate.convert(self.from_amount)

    @property
    def rate(self):
        return self.exchange_rate

    @property
    def market(self):
        if self._market is not None:
            return self._market
        else:
            raise Exception("Market is not set on order {}".format(self))

    def with_market(self, market):
        '''Returns a new Order, with market set to the specified one'''
        # pylint: disable=protected-access
        assert isinstance(market, Market)
        self_copy = copy.copy(self)
        self_copy._market = market
        self_copy._sanity_check()
        return self_copy


    def with_from_amount(self, from_amount):
        '''Returns a new Order, with amount set to the specified one'''
        # pylint: disable=protected-access
        assert isinstance(from_amount, Amount)
        self_copy = copy.copy(self)
        self_copy.from_amount = from_amount
        self_copy._sanity_check()
        return self_copy

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

    @property
    def is_market_order(self):
        return self.exchange_rate is None

    def __str__(self):
        try:
            to_amount = self.to_amount
        except AttributeError:
            to_amount = "?"
        return "{0} >> {1}".format(self.from_amount, to_amount)

    def __repr__(self):
        return "<{0}({1}, {2}, {3}, {4}>".format(self.__class__.__name__, self.from_amount, self.exchange_rate, self._market, self.timestamp)

    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other #pylint: disable=unneeded-not

    def __hash__(self):
        return hash((self.from_amount, self.exchange_rate, self._market))



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

    def __init__(self, exchange, counter_currency, base_currency, ticker_stream=None):
        assert isinstance(exchange, Exchange)
        assert isinstance(counter_currency, Currency)
        assert isinstance(base_currency, Currency)
        if ticker_stream is not None:
            assert isinstance(ticker_stream, pubsub.Publisher)
        self.exchange = exchange
        self.base_currency = base_currency
        self.counter_currency = counter_currency
        self._ticker_stream = ticker_stream

    @property
    def currencies(self):
        return CurrencyPair(self.base_currency, self.counter_currency)

    @property
    def full_name(self):
        '''The full name of this market. Includes the currencies'''
        full_name = "{exchange} {base_currency}/{counter_currency}".format(**vars(self))
        return full_name

    @abstractmethod
    def get_ticker(self):
        """Returns the most recent ticker"""
        raise NotImplementedError()

    @property
    def ticker_stream(self):
        if self._ticker_stream is None:
            raise NotImplementedError("This market doesn't provide a ticker stream api")
        return self._ticker_stream

    @abstractmethod
    def get_orderbook(self):
        """Returns the order book"""
        raise NotImplementedError()

    @abstractmethod
    def authenticate(self, *args, **kwargs):
        """returns a ActiveParticipant in this market"""
        raise NotImplementedError

    def check_order_valid(self, order):
        '''checks if an order is adequate in this market'''
        er = order.exchange_rate
        if order.market and order.market != self:
            raise self.InvalidOrder("Order on different market")
        if er is not None:
            try:
                assert set(er.currencies) == set(self.currencies)
            except AssertionError:
                raise self.InvalidOrder("Invalid order exchange rate")

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return "<{0}({1}, {2}, {3})>".format(self.__class__.__name__, self.exchange, self.counter_currency, self.base_currency)

@six.add_metaclass(ABCMeta)
class Exchange(object):
    '''A currency exchange.
    It can expose several markets'''
    def __init__(self, name, market_list):
        self.name = name
        self.markets = MarketList(market_list)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{0}({1})>".format(self.__class__.__name__, self.name)

class MarketList(tuple):
    '''A searchable list of markets'''
    def __init__(self, list_of_markets):
        tuple.__init__(self, list_of_markets)
        assert all(isinstance(m, Market) for m in self)
        self._all = set(self)
        self._by_currency = group_by(self, lambda market: (market.base_currency, market.counter_currency), multi=True)
        self._by_exchange = group_by(self, lambda market: market.exchange.name.lower())

    def find(self, currency1=None, currency2=None, exchange=None):
        '''Returns a sublist of contained markets, filtered by the given criteria'''
        exchange_name = exchange.name if isinstance(exchange, Exchange) else exchange
        results = set(self._all) # make copy
        if currency1:
            currency1 = Currency(currency1)
            results &= self._by_currency[currency1]
        if currency2:
            currency2 = Currency(currency2)
            results &= self._by_currency[currency2]
        if exchange_name:
            exchange_name_lower = exchange_name.lower() if exchange_name else None
            results &= self._by_exchange[exchange_name_lower]
        return MarketList(results)

    def find_one(self, *args, **kwargs):
        '''Calls find() with the same arguments, and returns one result.
        Raises IndexError if find() doesn't return exactly one result'''
        results = self.find(*args, **kwargs)
        if len(results) == 0:
            raise IndexError("No markets found for {} {}".format(args, kwargs))
        if len(results) > 1:
            raise IndexError("More than one market found for {} {}".format(args, kwargs))
        assert len(results) == 1
        return results[0]

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
    def place_order(self, order):
        """places an Order in the market"""
        pass

    @abstractmethod
    def cancel_order(self, order):
        """Cancel an existing order"""
        pass

    @abstractmethod
    def get_open_orders(self):
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
        self.data = kwargs
        vars(self).update(kwargs)
        assert self.bid < self.ask # pylint: disable=no-member

    def __str__(self):
        data_str = ", ".join("{}: {}".format(k, v) for k, v in self.data.items())
        return "<{cname}({time}, {data}>".format(cname=self.__class__.__name__, time=self.time, data=data_str)

    def __repr__(self):
        return "<{cname}({time}, {dict}>".format(cname=self.__class__.__name__, time=self.time, dict=vars(self))

class Orderbook(object):
    '''The list of open orders on a market'''
    def __init__(self, market, bid_orders, ask_orders):
        assert isinstance(market, Market)
        assert all(isinstance(x, Order) for x in bid_orders)
        assert all(isinstance(x, Order) for x in ask_orders)
        assert all(x.is_bid for x in bid_orders)
        assert all(x.is_ask for x in ask_orders)
        if len(bid_orders):
            #bid rates are sorted in descending order
            rates = [bid.exchange_rate.rate for bid in bid_orders]
            assert rates == sorted(rates, reverse=True)
        if len(ask_orders):
            #ask rates are sorted in ascending order
            rates = [ask.exchange_rate.rate for ask in ask_orders]
            assert rates == sorted(rates)
        if bid_orders and ask_orders:
            assert bid_orders[0].exchange_rate < ask_orders[0].exchange_rate
        self.market = market
        self.bids = tuple(bid_orders)
        self.asks = tuple(ask_orders)

