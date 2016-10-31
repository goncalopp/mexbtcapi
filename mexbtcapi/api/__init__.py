'''This module contains the several exchange apis to make available'''

# import mtgox          #closed in 2013
# import bitcoin24      #closed in april 2013
from . import bitstamp
from . import poloniex

apis = [
    bitstamp,
    poloniex,
    ]
