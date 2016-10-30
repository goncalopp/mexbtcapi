#from api import mtgox
#from api import bitcoin24

from api import bitstamp
from concepts.market import MarketList
import logging

logging.basicConfig()
logging.getLogger(__name__)

def _generate_markets(apis):
    for api in apis:
        for market in api.markets:
            yield market
apis = [
    #mtgox,       #closed in 2013
    #bitcoin24,   #closed in april 2013
    bitstamp,
    ]

markets = MarketList(list(_generate_markets(apis)))
