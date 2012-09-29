import datetime
from currency import ExchangeRate

class Trade(object):
    '''Represents an exchange of two currency amounts. May include the 
    entities between which the trade is made'''
    def __init__(self, from_amount, to_amount, from_entity=None, to_entity=None, opening_time=None, closing_time=None, market=None):
        self.from_amount=   from_amount
        self.to_amount=     to_amount
        self.from_entity=   from_entity
        self.to_entity=     to_entity
        self.opening_time=  opening_time
        self.closing_time=  closing_time
        self.market=market

class Market(object):
    '''Represents a market - where Trade's are made'''
    def __init__(self, market_name, c1, c2):
        '''c1 is the "buy" currency'''
        self.name= market_name
        self.c1, self.c2= c1, c2
    
    def getTicker(self):
        '''returns the most recent ticker'''
        raise NotImplementedError()
    
    def getOpenTrades(self):
        '''returns a list with all the open Trade's in the market'''
        raise NotImplementedError()
    
    def getClosedTrades(self):
        '''returns all completed trades'''
        raise NotImplementedError()

class Party( Market ):
    '''Represents a party in a market'''
    def __init__(self, market):
        assert isinstance( market, Market )
        self.market= market

class PassiveParty( Party ):
    '''A party over which the user has no control'''
    pass

class ActiveParty( Party ):
    '''A party under user control'''
    def placeTrade( trade ):
        '''places a trade in the market'''
        raise NotImplementedError()
    def cancelTrade( trade ):
        raise NotImplementedError()
    class TradeAlreadyClosed( Exception ):
        '''occurs when trying to cancel a already-closed trade'''
        pass

class Ticker( object ):
    '''A ticker datapoint.'''
    TIME_PERIOD= 24*60*60   #time period (in seconds) associated with the
                            #returned results: high, low, average, 
                            #last, sell, buy, volume
    def __init__(self, market, time, high=None, low=None, average=None, last=None, sell=None, buy=None, volume=None):
        '''market: the market this ticker is associated with
        time: the time at which this ticker was retrieved. This is preferably the server time, if available.
        high, low,average,last,sell,buy: ExchangeRate.
        '''
        assert isinstance(market, Market)
        assert all( [isinstance(x, ExchangeRate) for x in (high,low, average, last, sell, buy)] )
        assert (volume is None) or (type(volume)==long)
        assert all( [isinstance(x, ExchangeRate) for x in (high,low, average, last, sell, buy)] )
        assert (buy is None and sell is None) or (buy<=sell) #market invariant. The market always buys a currency cheaper than it sells it
        assert isinstance(time, datetime.datetime)
        self.market, self.time, self.volume= market, time, volume
        self.high, self.low,self.average,self.last, self.sell, self.buy= high, low, average, last, sell, buy

class NotAuthorized( Exception ):
    '''Occurs when the user is not authorized to do the requested 
    operation'''
    pass
