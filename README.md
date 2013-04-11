MExBtcAPI
=========


Project Goals
=============

* provide a set of well developed classes useful in representing concepts like  
    * currency
    * money
    * exchange rate
    * currency exchange
    * exchange order
* promote their use
* provide API implementations of various bitcoin exchanges using them

Donations
=========
Donations of bitcoin are kindly accepted at **1NBmTawDXqj8mNzGZSTzS1qmeyBhNideTM**

Small Demo
==========

    import mexbtcapi
    from mexbtcapi.concepts.currencies import USD
    from mexbtcapi.concepts.currency import Amount


    ten_dollars= Amount(10, USD)
    for api in mexbtcapi.apis:
        exchange_rate= api.market(USD).getTicker().sell
        print "At %s I can get %s for my %s (that's %s)"%(api.name, exchange_rate.convert( ten_dollars ), ten_dollars, exchange_rate)

At the moment, this code returns this output:

    At MtGox I can get 0.08 BTC for my 10.00 USD (that's 124.90 USD/BTC)
    At Bitcoin-24 I can get 0.15 BTC for my 10.00 USD (that's 65.00 USD/BTC)


Development Status
==================

Pre-alpha.
Discussion is in course in order to define the API features and interface.

If you're a potential user of this API - your opinion matters, so feel free to join the discussion.
Developers are welcome too, obviously

Obtaining the latest source
===========================
https://github.com/goncalopp/mexbtcapi


Adding suport for a new exchange
================================
Please consult the add_market file
