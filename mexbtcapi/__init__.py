#from api import mtgox
#from api import bitcoin24
from api import bitstamp
import logging

logging.basicConfig()
logging.getLogger(__name__)

apis = [
    #mtgox,       #closed in 2013
    #bitcoin24,   #closed in april 2013
    bitstamp,
    ]
