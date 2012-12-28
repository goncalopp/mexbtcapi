from api import mtgox
from api import bitcoin24
from api import bitstamp
import logging

logging.basicConfig()
logging.getLogger(__name__)

apis = [mtgox,
		bitcoin24,
		bitstamp,
		]
