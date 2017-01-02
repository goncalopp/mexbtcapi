'''Classes for Currency, ExchangeRate, Amount'''
import copy
from decimal import Decimal
from fractions import Fraction
from functools import total_ordering
import logging
import six

logger = logging.getLogger(__name__)

NUMBER_TYPES = six.integer_types + (float, Decimal, Fraction)


def convert_to_decimal(number, frac=False):
    bad_type = not isinstance(number, NUMBER_TYPES + six.string_types)
    if bad_type:
        message = "{}, of type {} is not suitable as a Decimal"
        logger.warning(message.format(number, type(number)))
    return Fraction(number) if frac else Decimal(number)


class Currency(object):
    """A currency (USD, EUR, ...)"""
    def __init__(self, name):
        if isinstance(name, Currency):
            name = name.name
        elif isinstance(name, six.string_types):
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
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __rmul__(self, other):
        try:
            return Amount(other, self)
        except ValueError:
            return NotImplemented

    def __div__(self, other):
        if isinstance(other, Currency):
            return ExchangeRate(other, self, 1)
        return NotImplemented

    def __truediv__(self, other):
        return self.__div__(other)

class CurrencyPair(object):
    '''A pair of currencies'''
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
        if not isinstance(other, CurrencyPair):
            return False
        return self.currencies == other.currencies

    def __hash__(self):
        return hash(self.currencies)

    def __ne__(self, other):
        return not self.__eq__(other)

@total_ordering
class ExchangeRate(object):
    """The proportion between two currencies' values"""
    def __init__(self, numerator_currency, denominator_currency, rate):
        '''Each DENOMINATOR is  worth RATE * NUMERATOR.
        Printed result is:  "RATE NUMERATOR/DENOMINATOR"'''
        assert isinstance(numerator_currency, Currency)
        assert isinstance(denominator_currency, Currency)
        assert numerator_currency != denominator_currency
        dec_rate = convert_to_decimal(rate, frac=True)
        if not 0 < dec_rate < float('inf'):
            raise ValueError("Rate must be strictly positive")
        self._currencies = CurrencyPair(numerator_currency, denominator_currency)
        self._rate = dec_rate

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
        exchange_rate = self if not self._is_denominator(currency) else self.reverse()
        return Amount(amount.value * exchange_rate.rate, currency)

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
        return ExchangeRate(er_a.currencies[0], er_b.currencies[1], er_b.rate * er_a.rate)

    def _is_denominator(self, currency):
        '''returns if currency is the denominator.
        Throws exception is the currency does not belong to this ExchangeRate'''
        return not self._currencies.is_first(currency)

    def inverse(self):
        '''returns the inverse exchange rate.
        The relative value of the currencies is swapped'''
        return ExchangeRate(self.denominator, self.numerator, self._rate)

    def per(self, currency):
        '''gives the ExchangeRate with currency as the denominator.'''
        return self if self._is_denominator(currency) else self.reverse()

    def by(self, currency):
        '''gives the ExchangeRate with currency as the numerator.'''
        return self if not self._is_denominator(currency) else self.reverse()

    def _cmp_checks(self, other):
        if not isinstance(other, ExchangeRate):
            raise TypeError("can't compare the two values: {}, {}".format(self, other))
        if self.currencies != other.currencies:
            other = other.reverse()
        if self.currencies != other.currencies:
            raise ValueError("Can't compare ExchangeRates with different currencies: {}, {}".format(self, other))
        return other

    def __cmp__(self, other):
        other = self._cmp_checks(other)
        return cmp(self.rate, other.rate)

    def __lt__(self, other):
        other = self._cmp_checks(other)
        return self.rate < other.rate

    def __eq__(self, other):
        other = self._cmp_checks(other)
        return self.rate == other.rate

    def __hash__(self):
        return hash((self._currencies, self._rate))

    def __repr__(self):
        return "<ExchangeRate({0:.5f} {1}/{2})>".format(float(self.rate), self.numerator.name, self.denominator.name)

    def __str__(self):
        return "{0:.5f} {1}/{2}".format(float(self.rate), self.numerator.name, self.denominator.name)

class Amount(object):
    """An amount of  a given currency"""

    def __init__(self, value, currency):
        self.value = convert_to_decimal(value, frac=True)
        self.currency = currency

    def __repr__(self):
        return "<Amount({0:.5f} {1})>".format(float(self.value), self.currency)

    def __str__(self):
        return "{0:.5f} {1}".format(float(self.value), self.currency)

    def __iadd__(self, other):
        if isinstance(other, NUMBER_TYPES):
            self.value += other
        elif isinstance(other, Amount):
            if self.currency != other.currency:
                raise ValueError("Can't add two amounts with different currencies")
            self.value += other.value
        else:
            return NotImplemented
        return self

    def __add__(self, other):
        return copy.copy(self).__iadd__(other)

    def __neg__(self):
        am = copy.copy(self)
        am.value = -am.value
        return am

    def __isub__(self, other):
        self += -other
        return self

    def __sub__(self, other):
        return copy.copy(self).__iadd__(-other)

    def __imul__(self, other):
        if not isinstance(other, NUMBER_TYPES):
            return NotImplemented
        self.value *= other
        return self

    def __mul__(self, other):
        return copy.copy(self).__imul__(other)

    def __div__(self, other):
        '''doubles as ExchangeRate constructor'''
        if isinstance(other, Currency):
            other = Amount(1, other)
        if isinstance(other, Amount):
            return ExchangeRate.from_amounts(self, other)
        else:
            return copy.copy(self).__idiv__(other)

    def __idiv__(self, other):
        if not isinstance(other, NUMBER_TYPES):
            return NotImplemented
        self.value /= other
        return self

    def __truediv__(self, other):
        return self.__div__(other)

    def __itruediv__(self, other):
        return self.__idiv__(other)

    def _cmp_checks(self, other):
        if not isinstance(other, Amount) or other.currency != self.currency:
            raise ValueError("can't compare the two amounts", str(self), str(other))
        return other

    def __cmp__(self, other):
        other = self._cmp_checks(other)
        return cmp(self.value, other.value)

    def __lt__(self, other):
        other = self._cmp_checks(other)
        return self.value < other.value

    def __eq__(self, other):
        other = self._cmp_checks(other)
        return self.value == other.value

    def __rshift__(self, other):
        '''constructor for Order'''
        if isinstance(other, Amount):
            other = self / other
            assert isinstance(other, ExchangeRate)
        if not other:
            other = None
        if other is None or isinstance(other, ExchangeRate):
            from mexbtcapi.market import Order
            return Order(self, other)
        return NotImplemented

    def __hash__(self):
        return hash((self.value, self.currency))
