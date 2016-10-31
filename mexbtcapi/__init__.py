import logging
#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
 
from . import api
from . import market

def _generate_markets(exchanges):
    for exchange in exchanges:
        log.debug("Loading markets on {}".format(exchange))
        for market in exchange.market_list:
            log.debug("Loaded market {}".format(market))
            yield market

def _load_exchanges_from_modules(modules):
    exchanges = {}
    for module in modules:
        try:
            exchange = module.exchange
            assert isinstance(exchange, market.Exchange)
            exchanges[exchange.name] = exchange
            log.debug("Loaded exchange {} from {}".format(exchange, module))
        except Exception as e:
            log.error("Failed to load exchange from {}: {}".format(module, e))
    return exchanges


exchanges = _load_exchanges_from_modules(api.apis)
markets = market.MarketList(_generate_markets(exchanges.values()))
