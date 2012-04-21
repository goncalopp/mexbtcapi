import currency as currencies

class ExchangeRate(object):
    def __init__(self, c1, c2, exchange_rate):
        '''c1 = exchange_rate * c2'''
        assert c1!=c2
        self.c1, self.c2, self.exchange_rate= c1, c2, float(exchange_rate)
        
    def convert(self, amount):
        assert isinstance(amount, Amount)
        if self.c1==amount.currency:
            amount.value*= self.exchange_rate
            amount.currency= self.c2
        elif self.c2==amount.currency:
            amount.value/= self.exchange_rate
            amount.currency= self.c1
        else:
            raise Exception("Can't exchange currencies with this ExchangeRate")
    def __repr__(self):
        return "%.3f %s/%s" % (self.exchange_rate, currency_dict[self.c1], currency_dict[self.c2])

class Amount(object):
    def __init__(self, value, currency):
        self.value, self.currency= float(value), currency

    def convert(self, currencyequivalence, to_currency):
        if self.currency!=to_currency:
            currencyequivalence.convert(self)
    
    def clone():
        '''returns a copy of this amount'''
        return Amount( self.value, self.currency)
        
    def __repr__(self):
        return str(self.value)+" "+currencies.list[self.currency]

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
