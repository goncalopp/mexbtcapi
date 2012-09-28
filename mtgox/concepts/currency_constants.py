def Currency( object ):
    def __init__(self, name):
        self.name= name



from constant_generator import constant_generator
constant_generator( map( Currency, ['BTC', 'USD', 'EUR', 'JPY', 'CAD', 'GBP', 'CHF', 'RUB', 'AUD', 'SEK', 'DKK', 'HKD', 'PLN', 'CNY', 'SGD', 'THB', 'NZD', 'NOK'], locals()))
