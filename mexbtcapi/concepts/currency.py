from decimal import Decimal
from mexbtcapi import log



def check_number_for_decimal_conversion(number):
    a= type(number) in (int, long)
    b= isinstance(number, (str, unicode, Decimal))
    if not (a or b):
        log.warning("You are using a number ("+str(number)+") that is not suitable to convert to Decimal!")


class Currency( object ):
    def __init__(self, name):
        self.name= name
    def __repr__(self):
        return self.name

class ExchangeRate(object):
    def __init__(self, c1, c2, exchange_rate):
        assert all([isinstance(x, Currency) for x in (c1,c2)])
        '''c2 = exchange_rate * c1. If associated with a market, c2 is 
        the "buy" currency'''
        assert c1!=c2
        check_number_for_decimal_conversion( exchange_rate )
        self.c1, self.c2= c1, c2
        self.exchange_rate= Decimal( exchange_rate )

    def convert(self, amount):
        assert isinstance(amount, Amount)
        if self.c1==amount.currency:
            return Amount(amount.value*self.exchange_rate, self.c2)
        elif self.c2==amount.currency:
            return Amount((1/amount.value)*self.exchange_rate, self.c1)
        else:
            raise Exception("Can't exchange currencies with this ExchangeRate")

    def __cmp__(self, other):
        if not isinstance(other, ExchangeRate) or other.c1!=self.c1 or other.c2!=self.c2:
            raise ValueError("can't compare the two amounts", str(self), str(other))
        return cmp(self.exchange_rate,other.exchange_rate)

    def __repr__(self):
        return "%.2f %s/%s" % (self.exchange_rate, self.c2.name, self.c1.name)

class Amount(object):
    def __init__(self, value, currency):
        check_number_for_decimal_conversion( value )
        self.value, self.currency= Decimal(value), currency

    def convert(self, currencyequivalence, to_currency):
        if self.currency!=to_currency:
            currencyequivalence.convert(self)
    
    def clone():
        '''returns a copy of this amount'''
        return Amount( self.value, self.currency)
        
    def __repr__(self):
        return "%.2f %s" % (self.value, self.currency)

    def __iadd__(self, other):
        if type(other) in (int, float):
            self.value+=other
        elif isinstance(other, Amount):
            if self.currency!=other.currency:
                raise ValueError("Can't sum two amounts in different currencies")
            self.value+=other.value
        else:
            raise ValueError("Can't sum Amount to ", type(other))
        return self

    def __add__(self, other):
        a= self.clone()
        a+= other
        return a

    def __neg__(self):
        a= self.clone()
        a.value= -a.value
        return a

    def __isub__(self,other):
        self+= -other
        return self

    def __sub__(self, other):
        a= self.clone() + (-other)
        return a

    def __cmp__(self, other):
        if not isinstance(other, Amount) or other.currency!=self.currency:
            raise ValueError("can't compare the two amounts", str(self), str(other))
        return cmp(self.value,other.value)
