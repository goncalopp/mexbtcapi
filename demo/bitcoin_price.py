import mexbtcapi
from mexbtcapi.concepts.currencies import USD
from mexbtcapi.concepts.currency import Amount


dollars= "100"*USD
for api in mexbtcapi.apis:
    try:
        exchange_rate= api.market(USD).getTicker().sell
        got = exchange_rate.convert( dollars )
        print "At %s I can get %s for my %s (that's %s)"%(api.name, got, dollars, exchange_rate)
    except:
        print "Failed to use "+api.name 
