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
        '''returns the reverse exchange rate'''
        return ExchangeRate(self._c[1], self._c[0], self._er )

    def __cmp__(self, other):
        e=ValueError("can't compare the two values:", str(self), 
                     str(other))
        if not isinstance(other, ExchangeRate):
            raise e
        if self._c[0]!=other._c[0] or self._c[1]!=other._c[1]:
            raise e
        return cmp(self._er, other._er)
        

    def __repr__(self):
        return "<ExchangeRate({:.2f} {}/{})>".format( self._er, 
                                                      self._c[1].name, 
                                                      self._c[0].name)

    def __str__(self):
        return "{:.2f} {}/{}".format( self._er, self._c[1].name, 
                                    self._c[0].name)


class Amount(object):
    """An amount of a given currency"""

    def __init__(self, value, currency):
        check_number_for_decimal_conversion(value)

        self.value = Decimal(value)
        self.currency = currency

    def convert(self, currencyequivalence, to_currency):
        if self.currency != to_currency:
            currencyequivalence.convert(self)

    def clone(self):
        # returns a copy of this amount
        return Amount(self.value, self.currency)

    def __repr__(self):
        return "<Amount({:.2f} {})>".format(self.value, self.currency)

    def __str__(self):
        return "{:.2f} {}".format(self.value, self.currency)

    def __iadd__(self, other):
        if type(other) in (int, float):
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

    def __cmp__(self, other):
        if not isinstance(other, Amount) or other.currency != self.currency:
            raise ValueError("can't compare the two amounts",
                             str(self), str(other))
        return cmp(self.value, other.value)
