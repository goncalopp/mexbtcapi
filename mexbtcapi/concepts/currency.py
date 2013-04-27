from decimal import Decimal
import logging


logger = logging.getLogger(__name__)


def check_number_for_decimal_conversion(number):
    a = type(number) in (int, long)
    b = isinstance(number, (str, unicode, Decimal))
    if not (a or b):
        logger.warning("You are using a number (" + str(number) +
                       ") that is not suitable to convert to Decimal!")


class Currency(object):
    """A currency (USD, EUR, ...)"""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Currency({0})>".format(self.name)

    def __str__(self):
        return self.name
    
    def __rmul__(self, other):
        try:
            return Amount(other, self)
        except ValueError:
            raise TypeError("Can't multiply currency with {0}".format(other))
    
    def __div__(self, other):
        if isinstance(other, Currency):
            return ExchangeRate(other, self, 1)
        raise TypeError("Can't divide a Currency by a "+str(type(other)))

    def __rdiv__(self, other):
        if isinstance(other, Amount):
            return ExchangeRate(self, other.currency, other.value)
        raise TypeError("Can't divide a "++str(type(other))+" by a Currency")
        
        


class ExchangeRate(object):
    """The proportion between two currencies' values"""
    class BadCurrency( Exception ):
        def __init__(self, exchange_rate, other_currency):
            self.er, self.oc= exchange_rate, other_currency
        def __str__(self):
            s= "A ExchangeRate of {0} cannot handle {1}"
            return s.format(self.er, self.oc)

    def __init__(self, c1, c2, exchange_rate):
        '''c2 = exchange_rate * c1'''
        assert all([isinstance(x, Currency) for x in (c1, c2)])
        assert c1 != c2
        check_number_for_decimal_conversion(exchange_rate)
        self._c= (c1,c2)
        self._er = Decimal(exchange_rate)

    def convert(self, amount, currency=None):
        '''if currency is not specified, converts amount to the other
        currency of this ExchangeRate. Otherwise, converts (if needed) 
        to the specified one'''
        if currency==amount.currency:
            return amount
        assert isinstance(amount, Amount)
        i= self._isFirst( amount.currency)
        c= self._c[1 if i else 0]
        if currency and c!=currency:
            i= not(i)
        er= self._er if i else 1 /  self._er
        if currency and c!=currency:
            raise self.BadCurrency(self, currency)
        return Amount(amount.value * er, c)
    
    def reverse( self ):
        '''returns a ExchangeRate with swapped currencies order. 
        The relative value of the currencies remains the same'''
        return ExchangeRate(self._c[1], self._c[0], 1/self._er )

    def convert_exchangerate( self, exchange_rate):
        '''Let (CA0,CA1) be the currencies of self, and (CB0,CB1) the 
        currencies of exchange_rate. If CA0==CB0, this method returns a 
        new ExchangeRate with currencies CA1, CB1, converting the 
        internal exchange rate to match.'''
        a,b= self, exchange_rate
        common_currency= set(a._c).intersection(b._c)
        if len(common_currency)!=1:
            raise Exception("Can't convert: currencies don't match")
        cc= common_currency.pop()
        if cc==a._c[1]:
            a=a.reverse()
        if cc==b._c[1]:
            b=b.reverse()
        return ExchangeRate( a._c[1], b._c[1], b._er/a._er )

    def _isFirst(self, currency):
        '''returns if currency is the first'''
        if self._c[0] == currency:
            return True
        elif self._c[1] == currency:
            return False
        else:
            raise self.BadCurrency(self, currency)
            
    def otherCurrency(self, currency):
        return self._c[ 1 if self._isFirst(currency) else 0 ]
    
    def inverse(self):
        '''returns the inverse exchange rate.
        The relative value of the currencies is swapped'''
        return ExchangeRate(self._c[1], self._c[0], self._er )
    
    def per(self, currency):
        '''gives the ExchangeRate with currency as the denominator.'''
        return self if self._c[0]==currency else self.reverse()
    
    def by(self, currency):
        '''gives the ExchangeRate with currency as the numerator.'''
        return self if self._c[1]==currency else self.reverse()

    def __cmp__(self, other):
        e=ValueError("can't compare the two values:", str(self), 
                     str(other))
        if not isinstance(other, ExchangeRate):
            raise e
        if self._c[0]!=other._c[0] or self._c[1]!=other._c[1]:
            raise e
        return cmp(self._er, other._er)
        

    def __repr__(self):
        return "<ExchangeRate({0:.2f} {1}/{2})>".format( self._er, 
                                                      self._c[1].name, 
                                                      self._c[0].name)

    def __str__(self):
        return "{0:.2f} {1}/{2}".format( self._er, self._c[1].name, 
                                    self._c[0].name)

    def clone(self):
        # returns a copy of this ExchangeRate
        return ExchangeRate(self._c[0], self._c[1], self._er)

    def __iadd__(self, other):
        if isinstance(other, ExchangeRate):
            if self._c!=other._c:
                raise ValueError("Can't sum two ExchangeRate with " + \
                             "different currencies")
            self._er += other._er
        else:
            raise ValueError("Can't sum ExchangeRate to ", type(other))
        return self

    def __add__(self, other):
        a = self.clone()
        a += other
        return a

    def __neg__(self):
        a = self.clone()
        a._er = -a._er
        return a

    def __isub__(self, other):
        self += -other
        return self

    def __sub__(self, other):
        a = self.clone() + (-other)
        return a


class Amount(object):
    """An amount of a given currency"""

    def __init__(self, value, currency):
        check_number_for_decimal_conversion(value)
        try:
            self.value = Decimal(value)
        except:
            raise ValueError("Can't convert {0} to decimal".format(value))
        self.currency = currency

    def convert(self, currencyequivalence, to_currency):
        if self.currency != to_currency:
            currencyequivalence.convert(self)

    def clone(self):
        # returns a copy of this amount
        return Amount(self.value, self.currency)

    def __repr__(self):
        return "<Amount({0:.2f} {1})>".format(self.value, self.currency)

    def __str__(self):
        return "{0:.2f} {1}".format(self.value, self.currency)

    def __iadd__(self, other):
        if type(other) in (int, float) or isinstance(other, Decimal):
            self.value += other
        elif isinstance(other, Amount):
            if self.currency != other.currency:
                raise ValueError("Can't sum two amounts in " + \
                                 "different currencies")
            self.value += other.value
        else:
            raise ValueError("Can't sum Amount to ", type(other))
        return self

    def __add__(self, other):
        a = self.clone()
        a += other
        return a

    def __neg__(self):
        a = self.clone()
        a.value = -a.value
        return a

    def __isub__(self, other):
        self += -other
        return self

    def __sub__(self, other):
        a = self.clone() + (-other)
        return a

    def __imul__(self, other):
        if type(other) in (int, float) or isinstance(other, Decimal):
            self.value *= other
        else:
            raise ValueError("Can't multiply Amount to ", type(other))
        return self

    def __mul__(self, other):
        a = self.clone()
        a *= other
        return a

    def __cmp__(self, other):
        if not isinstance(other, Amount) or other.currency != self.currency:
            raise ValueError("can't compare the two amounts",
                             str(self), str(other))
        return cmp(self.value, other.value)
