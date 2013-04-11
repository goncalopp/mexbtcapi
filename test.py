import mexbtcapi
from mexbtcapi.concepts.currencies import USD
from mexbtcapi.concepts.currency import Amount


ten_dollars= Amount(10, USD)
for api in mexbtcapi.apis:
    exchange_rate= api.market(USD).getTicker().sell
    print "At %s I can get %s for my %s (that's %s)"%(api.name, exchange_rate.convert( ten_dollars ), ten_dollars, exchange_rate)
