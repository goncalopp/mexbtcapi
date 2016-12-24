'''
Multi-exchange Bitcoin API
'''
import logging

from . import api
from . import market

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def _generate_markets(exchange_list):
    for exchange in exchange_list:
        log.debug("Loading markets on {}".format(exchange))
        for mkt in exchange.markets:
            log.debug("Loaded market {}".format(mkt))
            yield mkt

def _load_exchanges_from_modules(modules):
    exchange_d = {}
    for module in modules:
        try:
            exchange = module.exchange
            assert isinstance(exchange, market.Exchange)
            exchange_d[exchange.name] = exchange
            log.debug("Loaded exchange {} from {}".format(exchange, module))
        except Exception:
            log.error("Failed to load exchange from {}".format(module))
            raise
    return exchange_d

exchanges = _load_exchanges_from_modules(api.apis)
markets = market.MarketList(_generate_markets(exchanges.values()))
