MExBtcAPI
=========

Welcome to the Multi-Exchange Bitcoin API!

This project aims to:  

* provide a set of well developed interfaces useful in representing useful concepts like  
    * currency
    * money
    * exchange rate
    * currency market
* promote their use
* provide API implementations of various bitcoin exchanges using them


This is an example of typical usage:

    import mexbtcapi
    from mexbtcapi.concepts.currencies import USD
    from mexbtcapi.concepts.currency import Amount


    ten_dollars= Amount(10, USD)
    for api in mexbtcapi.apis:
        exchange_rate= api.market(USD).getTicker().sell
        print "At %s I can get %s for my %s (that's %s)"%(api.name, exchange_rate.convert( ten_dollars ), ten_dollars, exchange_rate)

At the moment, this code returns this output:

    At MtGox I can get 1.25 BTC for my 10.00 USD (that's 12.45 USD/BTC)


Obtaining the latest source
===========================
This project is currently developed at github:
https://github.com/goncalopp/mexbtcapi


Adding suport for a new market
===========================
Please consult the add_market file
