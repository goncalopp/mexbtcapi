Python-MtGox
============

This is an interface to MtGox's API version 1.

All numbers are returned as integers by default, divide by 
the currency's multiplier to get a human readable value. Just
use the multiplier dict, mtgox.multiplier[three-letter-currency-symbol].

## INSTALL

$ python setup.py install


## EXAMPLE
```
import mtgox

mtgox.ticker("USD")
mtgox.multiplier["EUR"]

account = mtgox.Private(key, secret)
account.info()


import mtgox.arrays

numpy_array_of_trades = mtgox.arrays.trades()
```

Donations: 174fzBxiW2Eiqmdd64CGTdJwLbjU2fxHEY
