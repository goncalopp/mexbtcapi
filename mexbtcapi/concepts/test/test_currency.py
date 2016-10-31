'''Tests for currency.py'''
import unittest
from decimal import Decimal
from mexbtcapi.concepts.currency import Currency, ExchangeRate, Amount, CurrencyPair

class CurrencytTest(unittest.TestCase):
    def test_create(self): 
        c1 = Currency("c1")
        self.assertIsInstance(c1, Currency)

    def test_equality(self):
        c1, c1_, c2 = Currency("c1"), Currency("c1"), Currency("c2") 
        self.assertEqual(c1, c1_)
        self.assertNotEqual(c1, c2)

    def test_hash(self):
        c1, c1_, c2 = Currency("c1"), Currency("c1"), Currency("c2") 
        self.assertEqual(set((c1,c1_)), set((c1,)))
        self.assertEqual(len({c1:1, c1_:1}), 1)
        self.assertEqual(len({c1:1, c2:1}), 2)
        self.assertEqual(len({c1:1, "c1":1}), 2)

class CurrencyPairTest(unittest.TestCase):
    @staticmethod
    def create_pair():
        c1, c2, c3 = Currency("c1"), Currency("c2"), Currency("c3")
        p1, p1_, p2, p3= CurrencyPair(c1,c2), CurrencyPair(c1,c3)

    def test_equality(self):
        c1, c1_, c2, c3 = Currency("c1"), Currency("c1"), Currency("c2"), Currency("c3")
        p1, p1_, p2, p3= CurrencyPair(c1,c2), CurrencyPair(c1_,c2), CurrencyPair(c1,c3), CurrencyPair(c3,c2)
        self.assertEqual(p1,p1_)
        self.assertNotEqual(p1,p2)
        self.assertNotEqual(p1,p3)

    def test_equality_reversed(self):
        c1, c2 = Currency("c1"), Currency("c2")
        self.assertNotEqual(CurrencyPair(c1,c2), CurrencyPair(c2, c1))

    def test_hash(self):
        c1, c1_, c2 = Currency("c1"), Currency("c1"), Currency("c2")
        p1, p1_, p2 = CurrencyPair(c1,c2), CurrencyPair(c1_,c2), CurrencyPair(c2,c1)
        self.assertEqual(set((p1,p1_)), set((p1,)))
        self.assertEqual(len({p1:1, p1_:1}), 1)
        self.assertEqual(len({p1:1, p2:1}), 2)

# TODO: test all CurrencyPair methods



class AmountTest(unittest.TestCase):
    @staticmethod
    def create_amount():
        c1, c2 = Currency("C1"), Currency("C2")
        amount = Amount('1.0', c1)
        return c1, c2, amount

    def test_create(self):
        c1, _, amount = AmountTest.create_amount()
        self.assertIsInstance(amount, Amount)

        #multiplying a number by a currency should give an Amount
        self.assertIsInstance(1 * c1, Amount)
        self.assertIsInstance('1' * c1, Amount)
        self.assertIsInstance(1.0 * c1, Amount)

        #initializing with diferent types should have the same result
        self.assertEqual(amount, 1 * c1)
        self.assertEqual(amount, '1' * c1)
        self.assertEqual(amount, 1.0 * c1)

    def test_properties(self):
        c1, _, amount = AmountTest.create_amount()
        self.assertEqual(amount.value, 1.0)
        self.assertEqual(amount.currency, c1)

    def test_decimal_handling(self):
        c1, _, _ = AmountTest.create_amount()
        self.assertNotEqual(0.1 * c1, '0.1' * c1)
        small_decimal = Decimal('0.0001')
        small_float = float(small_decimal)
        small_amount = small_decimal * c1
        total_decimal, total_float, total_amount = Decimal(0), 0.0, 0*c1
        for _ in range(10000):
            total_decimal += small_decimal
            total_float += small_float
            total_amount += small_amount
        self.assertEqual(total_decimal, 1.0)
        self.assertNotEqual(total_float, 1.0)
        self.assertEqual(total_amount, 1*c1)


class ExchangeRateTest(unittest.TestCase):
    @staticmethod
    def create_er():
        c1, c2 = Currency("C1"), Currency("C2")
        er = ExchangeRate(denominator_currency=c1, numerator_currency=c2, rate='2.0')
        return c1, c2, er

    def test_create(self):
        _, _, er = ExchangeRateTest.create_er()
        self.assertIsInstance(er, ExchangeRate)

    def test_create_by_division(self):
        c1, c2, _ = ExchangeRateTest.create_er()
        er1 = (2.0*c1) / c2 #2*c1 == 1*c2
        self.assertEqual(er1.denominator, c2)
        self.assertEqual(er1.numerator, c1)

    def test_properties(self):
        c1, c2, er = ExchangeRateTest.create_er()
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)

    def test_convert(self):
        c1, c2, er = ExchangeRateTest.create_er()
        self.assertEqual(er.convert(Amount(1, c1)), 2*c2)
        self.assertEqual(er.convert(Amount(1, c2)), 0.5*c1)
        self.assertEqual(er.convert(Amount(1, c1), c1), 1*c1)
        self.assertEqual(er.convert(Amount(1, c1), c2), 2*c2)
        self.assertRaises(CurrencyPair.WrongCurrency, lambda: er.convert(Amount(1, c1), Currency('c')))

    def test_reverse(self):
        _, _, er1 = ExchangeRateTest.create_er()
        er2 = er1.reverse()
        self.assertEqual(er1.denominator, er2.numerator)
        self.assertEqual(er1.numerator, er2.denominator)
        self.assertEqual(er1.rate, 1 / er2.rate)

    def test_convert_exchangerate(self):
        c1, c2, c3, c4 = map(Currency, ('c1', 'c2', 'c3', 'c4'))
        er1 = 2 * c1 / c2
        er2 = 3 * c2 / c3
        er3 = 3 * c3 / c4
        self.assertEqual(er1.convert_exchangerate(er2), 6 * c1 / c3)
        self.assertEqual(er1.reverse().convert_exchangerate(er2), 6 * c1 / c3)
        self.assertEqual(er1.convert_exchangerate(er2.reverse()), 6 * c1 / c3)
        self.assertRaises(CurrencyPair.WrongCurrency, lambda: er1.convert_exchangerate(er3))

#    def test_other_currency(self):
#        c1, c2, er = ExchangeRateTest.create_er()
#        self.assertEqual(er.other_currency(c1), c2)
#        self.assertEqual(er.other_currency(c2), c1)

    def test_inverse(self):
        c1, c2, er = ExchangeRateTest.create_er()
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)
        inverse = er.inverse()
        self.assertEqual(inverse.denominator, c2)
        self.assertEqual(inverse.numerator, c1)
        self.assertEqual(inverse.rate, 2.0)

    def test_per_by(self):
        c1, c2, _ = ExchangeRateTest.create_er()
        er = 2 * c2/c1
        #
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)
        er = er.by(c1)
        self.assertEqual(er.denominator, c2)
        self.assertEqual(er.numerator, c1)
        self.assertEqual(er.rate, 0.5)
        er = er.by(c1)
        self.assertEqual(er.denominator, c2)
        self.assertEqual(er.numerator, c1)
        self.assertEqual(er.rate, 0.5)
        er = er.per(c1)
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)
        er = er.per(c1)
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)
        #
        er = er.by(c2)
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)
        er = er.by(c2)
        self.assertEqual(er.denominator, c1)
        self.assertEqual(er.numerator, c2)
        self.assertEqual(er.rate, 2.0)
        er = er.per(c2)
        self.assertEqual(er.denominator, c2)
        self.assertEqual(er.numerator, c1)
        self.assertEqual(er.rate, 0.5)
        er = er.per(c2)
        self.assertEqual(er.denominator, c2)
        self.assertEqual(er.numerator, c1)
        self.assertEqual(er.rate, 0.5)

if __name__ == '__main__':
    unittest.main()
