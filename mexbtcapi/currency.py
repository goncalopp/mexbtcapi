'''Classes for Currency, ExchangeRate, Amount'''
from decimal import Decimal
from fractions import Fraction
import logging
import types

logger = logging.getLogger(__name__)


def convert_to_decimal(number, frac=False):
    bad_type = not isinstance(number, (int, long, str, unicode, Decimal, Fraction))
    if bad_type:
        message = "{}, of type {} is not suitable as a Decimal"
        logger.warning(message.format(number, type(number)))
    return Fraction(number) if frac else Decimal(number)


class Currency(object):
    """A currency (USD, EUR, ...)"""
    def __init__(self, name):
        if isinstance(name, Currency):
            name = name.name
        elif isinstance(name, types.StringTypes):
            name = name
        else:
            raise Exception("Can't create a Currency from {}".format(name))
        self.name = name

    def __repr__(self):
        return "<Currency({0})>".format(self.name)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if not isinstance(other, Currency):
            return False
        return self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)

    def __rmul__(self, other):
        try:
            return Amount(other, self)
        except ValueError:
            raise ValueError("Can't multiply currency with {0}".format(other))

    def __div__(self, other):
        if isinstance(other, Currency):
            return ExchangeRate(other, self, 1)
        raise TypeError("Can't divide a Currency by a "+str(type(other)))

    def __rdiv__(self, other):
        if isinstance(other, Amount):
            return ExchangeRate(self, other.currency, other.value)
        raise TypeError("Can't divide a "++str(type(other))+" by a Currency")

class CurrencyPair(object):
    class WrongCurrency(Exception):
        '''Raised when a CurrencyPair was asked to handle a currency it can't'''
        def __init__(self, currency_pair, other_currency, message=None):
            message = message or "{0} cannot handle currency {1}".format(currency_pair, other_currency)
            Exception.__init__(self, message)
            self.currency_pair = currency_pair
            self.currency = other_currency

    def __init__(self, currency1, currency2):
        currency1 = Currency(currency1)
        currency2 = Currency(currency2)
        if currency1 == currency2:
            raise self.WrongCurrency(None, currency1, "Can't create a pair with the same currency: {}".format(currency1))
        self.currencies = (currency1, currency2)

    def __getitem__(self, i):
        return self.currencies[i]

    def is_first(self, currency):
        try:
            return self.currencies.index(currency) == 0
        except ValueError: #currency not in tuple
            raise self.WrongCurrency(self, currency)

    def other_currency(self, currency):
        return self.currencies[1] if self.is_first(currency) else self.currencies[0]

    def common_currency(self, other_pair):
        '''Get the common currency between two pairs (i.e.: the only currency
        that belongs to both.
        Raises exception if there is none, or more that one'''
        assert isinstance(other_pair, CurrencyPair)
        common_currencies = set(self.currencies) & set(other_pair.currencies)
        if len(common_currencies) >= 2:
            raise self.WrongCurrency(self, None, "Both pairs have the same two currencies ({})".format(self.currencies))
        if len(common_currencies) != 1:
            raise self.WrongCurrency(self, None, "The pairs have no common currencies ({}, {})".format(self.currencies, other_pair.currencies))
        common_currency = common_currencies.pop()
        return common_currency

    def __repr__(self):
        return "<CurrencyPair({},{})>".format(self.currencies[0], self.currencies[1])

    def __str__(self):
        return "({}, {})".format(*self.currencies)

    def reverse(self):
        return CurrencyPair(self.currencies[1], self.currencies[0])

    def __eq__(self, other):
        e = ValueError("can't compare the two values: {}, {}".format(self, other))
        if not isinstance(other, CurrencyPair):
            raise e
        return self.currencies == other.currencies

    def __hash__(self):
        return hash(self.currencies)

    def __ne__(self, other):
        return not (self == other)


class ExchangeRate(object):
    """The proportion between two currencies' values"""
    def __init__(self, numerator_currency, denominator_currency, rate):
        '''Each DENOMINATOR is  worth RATE * NUMERATOR.
        Printed result is:  "RATE NUMERATOR/DENOMINATOR"'''
        assert isinstance(numerator_currency, Currency)
        assert isinstance(denominator_currency, Currency)
        assert numerator_currency != denominator_currency
        self._currencies = CurrencyPair(numerator_currency, denominator_currency)
        self._rate = convert_to_decimal(rate, frac=True)

    @staticmethod
    def from_amounts(amount1, amount2):
        return ExchangeRate(amount1.currency, amount2.currency, Fraction(amount1.value, amount2.value))

    @property
    def numerator(self):
        '''each NUMERATOR is worth 1/RATE * DENOMINATOR'''
        return self._currencies[0]

    @property
    def denominator(self):
        '''each DENOMINATOR is worth RATE * NUMERATOR'''
        return self._currencies[1]

    @property
    def currencies(self):
        '''returns a CurrencyPair'''
        return self._currencies

    @property
    def rate(self):
        '''each DENOMINATOR is worth RATE NUMERATOR'''
        return self._rate

    def convert(self, amount, currency=None):
        '''Converts the given amount to the given currency.
        If currency is not specified, converts to the other currency of this
        ExchangeRate.'''
        assert isinstance(amount, Amount)
        if currency is None:
            currency = self._currencies.other_currency(amount.currency)
        if currency == amount.currency:
            return amount
        exchange_rate = self if not self._isDenominator(currency) else self.reverse()
        return Amount(amount.value * exchange_rate._rate, currency)

    def reverse(self):
        '''returns a ExchangeRate with swapped currencies order.
        The relative value of the currencies remains the same'''
        return ExchangeRate(self.denominator, self.numerator, Fraction(1, self._rate))

    def convert_exchangerate(self, exchange_rate):
        '''Let (CA0,CA1) be the currencies of self, and (CB0,CB1) the
        currencies of exchange_rate. If CA0==CB0, this method returns a
        new ExchangeRate with currencies CA1, CB1, converting the
        internal exchange rate to match.'''
        er_a, er_b = self, exchange_rate
        common_currency = self.currencies.common_currency(exchange_rate.currencies)
        if common_currency != er_a.denominator:
            er_a = er_a.reverse()
        if common_currency != er_b.numerator:
            er_b = er_b.reverse()
        return ExchangeRate(er_a._currencies[0], er_b._currencies[1], er_b._rate * er_a._rate)

    def _isDenominator(self, currency):
        '''returns if currency is the denominator.
        Throws exception is the currency does not belong to this ExchangeRate'''
        return not self._currencies.is_first(currency)

    def inverse(self):
        '''returns the inverse exchange rate.
        The relative value of the currencies is swapped'''
        return ExchangeRate(self.denominator, self.numerator, self._rate)

    def per(self, currency):
        '''gives the ExchangeRate with currency as the denominator.'''
        return self if self._isDenominator(currency) else self.reverse()

    def by(self, currency):
        '''gives the ExchangeRate with currency as the numerator.'''
        return self if not self._isDenominator(currency) else self.reverse()

    def __cmp__(self, other):
        e = ValueError("can't compare the two values: {}, {}".format(self, other))
        if not isinstance(other, ExchangeRate):
            raise e
        if self.currencies == other.currencies.reverse():
            other = other.reverse()
        if self.currencies != other.currencies:
            raise e
        return cmp(self.rate, other.rate)


    def __repr__(self):
        return "<ExchangeRate({0:.2f} {1}/{2})>".format(float(self.rate), self.numerator.name, self.denominator.name)

    def __str__(self):
        return "{0:.2f} {1}/{2}".format(float(self.rate), self.numerator.name, self.denominator.name)

    def clone(self):
        # returns a copy of this ExchangeRate
        return ExchangeRate(self._currencies[0], self._currencies[1], self._rate)

    def __iadd__(self, other):
        if isinstance(other, ExchangeRate):
            if self._currencies != other._currencies:
                raise ValueError("Can't sum two ExchangeRate with " + \
                             "different currencies")
            self._rate += other._rate
        else:
            raise ValueError("Can't sum ExchangeRate to ", type(other))
        return self

    def __add__(self, other):
        a = self.clone()
        a += other
        return a

    def __neg__(self):
        a = self.clone()
        a._rate = -a._rate
        return a

    def __isub__(self, other):
        self += -other
        return self

    def __sub__(self, other):
        a = self.clone() + (-other)
        return a


class Amount(object):
    """An amount of  a given currency"""

    def __init__(self, value, currency):
        self.value = convert_to_decimal(value, frac=True)
        self.currency = currency

    def convert(self, currencyequivalence, to_currency):
        if self.currency != to_currency:
            currencyequivalence.convert(self)

    def clone(self):
        # returns a copy of this amount
        return Amount(self.value, self.currency)

    def __repr__(self):
        return "<Amount({0:.2f} {1})>".format(float(self.value), self.currency)

    def __str__(self):
        return "{0:.2f} {1}".format(float(self.value), self.currency)

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
        if isinstance(other, (int, float, long, Decimal)):
            self.value *= other
        else:
            raise ValueError("Can't multiply Amount to ", type(other))
        return self

    def __mul__(self, other):
        a = self.clone()
        a *= other
        return a

    def __div__(self, other):
        '''doubles as ExchangeRate constructor'''
        if isinstance(other, Currency):
            other = Amount(1, other)
        if isinstance(other, Amount):
            return ExchangeRate.from_amounts(self, other)
        else:
            a = self.clone()
            a /= other
            return a

    def __idiv__(self, other):
        if isinstance(other, (int, float, long, Decimal)):
            self.value /= other
            return self
        else:
            raise ValueError("Can't divide Amount to ", type(other))

    def __cmp__(self, other):
        if not isinstance(other, Amount) or other.currency != self.currency:
            raise ValueError("can't compare the two amounts",
                             str(self), str(other))
        return cmp(self.value, other.value)

    def __rshift__(self, other):
        '''constructor for Order'''
        if isinstance(other, Amount):
            other = self / other
            assert isinstance(other, ExchangeRate)
        if not other:
            other = None
        if other is None or isinstance(other, ExchangeRate):
            from market import Order
            return Order(self, other)
        raise ValueError("Can't shift {0} by {1}".format(self, other))
