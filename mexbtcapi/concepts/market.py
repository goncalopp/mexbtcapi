from currency import ExchangeRate, Amount
from datetime import datetime, timedelta
from decimal import Decimal


class Trade(object):
    """Represents an exchange of two currency amounts.
    May include the entities between which the trade is made
    """

    def __init__(self, market, timestamp, from_amount, exchange_rate):
        assert isinstance(market, Market)  # must not be null
        assert isinstance(timestamp, datetime)  # must not be null
        assert isinstance(from_amount, Amount)
        assert isinstance(exchange_rate, ExchangeRate)

        self.market = market
        self.timestamp = timestamp
        self.from_amount = from_amount
        self.exchange_rate = exchange_rate

    @property
    def to_amount(self):
        return self.exchange_rate.convert(self.from_amount)

    def __str__(self):
        return "{0} -> {1}".format(self.from_amount, self.exchange_rate)

    def __repr__(self):
        return "<{0}({1}, {2}, {3}, {4}>".format(self.__class__.__name__,
            self.market, self.timestamp, self.from_amount, self.exchange_rate)


class Order(object):
    """Represents an order to buy or sell a number of from_amount for
    exchange_rate.
    """
    TYPES=('market', 'limit')
    def __init__(self, from_amount, exchange_rate=None, otype=None, entity=None):
        assert isinstance(from_amount, Amount)
        assert (not exchange_rate) or isinstance(exchange_rate, ExchangeRate)
        assert (not otype) or (otype in self.TYPES)

        self.from_amount = from_amount
        self.exchange_rate = exchange_rate
        self.entity = entity
        self.otype= otype if otype else 'market' if not exchange_rate else 'limit'
    
    @property
    def to_amount(self):
        if self.exchange_rate:
            return self.exchange_rate.convert( self.from_amount )
        else:
            return "?"

    def __str__(self):
        return "{0} >> {1}".format(self.from_amount, self.to_amount)

    def __repr__(self):
        return "<{0}({1}, {2}, {3}, {4}>".format(self.__class__.__name__,
            self.market, self.timestamp, self.from_amount, self.exchange_rate)

class MarketOrder( Order ):
    '''A concrete order on a certain market'''
    def __init__(self, market, timestamp, entity, *args, **kwargs):
        assert isinstance(market, Market)       # must not be null
        assert isinstance(timestamp, datetime)  # must not be null
        assert entity is None or isinstance(entity, Participant)
        super(MarketOrder,self).__init__(*args, **kwargs)
        self.market = market
        self.timestamp = timestamp
    
    @property
    def is_buy_order(self):
        return self.from_amount.currency == self.market.sell_currency

    @property
    def is_sell_order(self):
        return self.from_amount.currency == self.market.buy_currency
        

class Market(object):
    """Represents a market - where Trades are made"""
    class InvalidOrder(Exception):
        '''raised when there's something wrong with an order, in this
        market's context'''

    def __init__(self, market_name, buy_currency, sell_currency):
        self._name = market_name
        self._currency1 = buy_currency
        self._currency2 = sell_currency
    
    @property
    def buy_currency(self):
        '''The currency that a participant on this market buys. 
        Should be the less common currency'''
        return self._currency1
    
    @property
    def sell_currency(self):
        '''The currency that a participant on this market sells. 
        Should be the more common currency'''
        return self._currency2
    
    @property
    def name(self):
        '''The name of this market. Doesn't include the currencies'''
        return self._name
    
    @property
    def full_name(self):
        '''The full name of this market. Includes the currencies'''
        return self.name+"_"+str(self.buy_currency)+"_"+str(self.sell_currency)

    def getTicker(self):
        """Returns the most recent ticker"""
        raise NotImplementedError()

    def getDepth(self):
        """Returns the depth book"""
        raise NotImplementedError()

    def getTrades(self):
        """Returns all completed trades"""
        raise NotImplementedError()

    def getParticipant(self, *args, **kwargs):
        """returns a ActiveParticipant in this market"""
        raise NotImplementedError

    def _orderSanityCheck(self, order):
        '''checks if an order is adequate in this market'''
        er= order.exchange_rate
        if order.market and order.market!=self:
            raise self.InvalidOrder("Order on different market")
        try:
            assert er.otherCurrency( self._currency1 ) == self._currency2
        except AssertionError, ExchangeRate.BadCurrency:
            raise self.InvalidOrder("Invalid order exchange rate")

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{0}({1}, {2}, {3})>".format(self.__class__.__name__, 
                    self.name, self.buy_currency, self.sell_currency)


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

    def placeOrder(self, order):
        """places an Order in the market"""
        raise NotImplementedError()

    def cancelOrder(self, order):
        """Cancel an existing order"""
        raise NotImplementedError()

    def getOpenOrders(self):
        """Gets all the open orders"""
        raise NotImplementedError()


class Ticker(object):
    """Ticker datapoint
    """
    # time period (in seconds) associated with the
    # returned results: high, low, average,
    # last, sell, buy, volume
    TIME_PERIOD = timedelta(days=1)
    RATE_FIELDS= ('high', 'low', 'average', 'last', 'sell', 'buy')
    OTHER_FIELDS= ('volume',)

    def __init__(self, market, time, high=None, low=None, average=None,
                    last=None, sell=None, buy=None, volume=None):
        """
        market: the market this ticker is associated with
        time:   the time at which this ticker was retrieved. This is preferably
                the server time, if available; otherwise, the local time.
                The time should always be in UTC
        high, low, average, last, sell, buy: ExchangeRate.
        """
        assert isinstance(market, Market)
        assert all([x is None or isinstance(x, ExchangeRate) 
            for x in map(locals().__getitem__,self.RATE_FIELDS)])
        assert (volume is None) or isinstance(volume, (long,Decimal))
        assert (buy is None and sell is None) or (buy <= sell)
        assert isinstance(time, datetime)
        self.market, self.time, self.volume = market, time, volume
        self.high, self.low, self.average, self.last, self.sell, self.buy = \
            high, low, average, last, sell, buy

    def __repr__(self):
        return \
            "<{0}({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9})" \
            .format(self.__class__.__name__, self.market, self.time, 
            self.high, self.high, self.last, self.volume, self.average, 
            self.buy, self.sell)

class Depth( object ):
    def __init__(self, market, buy_orders, sell_orders):
        assert isinstance(market, Market)
        assert all( (isinstance(x, MarketOrder) for x in buy_orders) )
        assert all( (isinstance(x, MarketOrder) for x in sell_orders) )
        assert all( (x.is_buy_order for x in buy_orders) )
        assert all( (x.is_sell_order for x in sell_orders) )
        self.market=market
        self.buy_orders=  buy_orders
        self.sell_orders= sell_orders
