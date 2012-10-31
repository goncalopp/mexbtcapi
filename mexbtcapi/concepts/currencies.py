from mexbtcapi.util.constant_generator import constant_generator
from currency import Currency

names= ('BTC', 'USD', 'EUR', 'JPY', 'CAD', 'GBP', 'CHF', 'RUB', 'AUD',
    'SEK', 'DKK', 'HKD', 'PLN', 'CNY', 'SGD', 'THB', 'NZD', 'NOK')

currencies=  map( Currency, names )

constant_generator( locals(), names, currencies)
