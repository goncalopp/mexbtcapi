from datetime import datetime, timedelta
from currency import ExchangeRate, Amount


class Trade(object):
    """Represents an exchange of two currency amounts.
    May include the entities between which the trade is made
    """
    def __init__(self, market, timestamp, from_amount, exchange_rate,
                 from_entity=None, to_entity=None):
        assert isinstance(market, Market)  # must not be null
        assert isinstance(timestamp, datetime)  # must not be null
        assert isinstance(from_amount, Amount)
        assert isinstance(exchange_rate, ExchangeRate)
        assert all([x is None or isinstance(x, Participant) for x
                                            in (from_entity, to_entity)])
        self.market = market
        self.timestamp = timestamp
        self.from_amount = from_amount
        self.exchange_rate = exchange_rate
        self.from_entity = from_entity
        self.to_entity = to_entity

    def __str__(self):
        return "{0} -> {1}".format(self.from_amount, self.exchange_rate)

    def __repr__(self):
        return "<Trade({0}, {1}, {2}, {3}>".format(self.market, self.timestamp,
                    self.from_amount, self.exchange_rate)


class Order(object):
    """Represents an order to buy or sell a number of from_amount for
    exchange_rate.

    For now, more specific properties can be set through the properties
    parameter of the constructor.
    """

    BUY = 'BUY'
    SELL = 'SELL'

    def __init__(self, market, timestamp,
                 buy_or_sell, from_amount, exchange_rate, properties=""):
        assert isinstance(market, Market)  # must not be null
        assert isinstance(timestamp, datetime)  # must not be null
        assert buy_or_sell in [self.BUY, self.SELL]
        assert isinstance(from_amount, Amount)
        assert isinstance(exchange_rate, ExchangeRate)
        assert isinstance(properties, str)

        self.market = market
        self.timestamp = timestamp
        self.buy_or_sell = buy_or_sell
        self.from_amount = from_amount
        self.exchange_rate = exchange_rate
        self.properties = properties

    def is_buy_order(self):
        return self.buy_or_sell == self.BUY

    def is_sell_order(self):
        return self.buy_or_sell == self.SELL

    def __str__(self):
        return "{0} -> {1}".format(self.from_amount, self.exchange_rate)

    def __repr__(self):
        return "<Order({0}, {1}, {2}, {3}>".format(self.market, self.timestamp,
                    self.from_amount, self.exchange_rate)


class Market(object):
    """Represents a market - where Trade's are made
    """

    def __init__(self, market_name, c1, c2):
        """c1 is the "buy" currency"""
        self.name = market_name
        self.c1, self.c2 = c1, c2

    def getTicker(self):
        """returns the most recent ticker"""
        raise NotImplementedError()

    def getOpenTrades(self):
        """returns a list with all the open Trade's in the market"""
        raise NotImplementedError()

    def getClosedTrades(self):
        """returns all completed trades"""
        raise NotImplementedError()

    def __str__(self):
        return self.name


class Participant(Market):
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

    def placeTrade(trade):
        """places a trade in the market"""
        raise NotImplementedError()

    def cancelTrade(trade):
        raise NotImplementedError()

    class TradeAlreadyClosed(Exception):
        """occurs when trying to cancel a already-closed trade"""
        pass

    class NotAuthorized(Exception):
        """Occurs when the user is not authorized to do the requested
        operation"""
        pass


class Ticker(object):
    """Ticker datapoint
    """

    # time period (in seconds) associated with the
    # returned results: high, low, average,
    # last, sell, buy, volume
    TIME_PERIOD = timedelta(days=1)

    def __init__(self, market, time, high=None, low=None, average=None,
                    last=None, sell=None, buy=None, volume=None):
        """
        market: the market this ticker is associated with
        time:   the time at which this ticker was retrieved. This is preferably
                the server time, if available.
        high, low, average, last, sell, buy: ExchangeRate.
        """
        assert isinstance(market, Market)
        assert all([x is None or isinstance(x, ExchangeRate) for x in
                        (high, low, average, last, sell, buy)])
        assert (volume is None) or (type(volume) == long)
        assert (buy is None and sell is None) or (buy <= sell)
        assert isinstance(time, datetime)
        self.market, self.time, self.volume = market, time, volume
        self.high, self.low, self.average, self.last, self.sell, self.buy = \
            high, low, average, last, sell, buy
