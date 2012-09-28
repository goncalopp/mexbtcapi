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
    def __init__(self, market_name, currency1, currency2):
        self.name= market_name
        self.currency1, self.currency2= currency1, currency2
    
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

class NotAuthorized( Exception ):
    '''Occurs when the user is not authorized to do the requested 
    operation'''
    pass
