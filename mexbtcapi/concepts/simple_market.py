from market import Order

class SimpleMarket(object):
    '''Wrapper class that offers simplified market api for the casual 
    user'''
    def __init__(self, market):
        self.market=market
    def __getattribute__(self, x):
        #expose existing market methods/attributes
        return self.market.__getattribute__(x)
    def placeAskOrder(self, amount, price):
        raise NotImplementedError #waiting to fix Order
    def placeBidOrder(self, amount, price):
        raise NotImplementedError #waiting to fix Order
    
