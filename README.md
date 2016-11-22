[![Build Status](https://travis-ci.org/goncalopp/mexbtcapi.svg?branch=master)](https://travis-ci.org/goncalopp/mexbtcapi)
[![PyPI version](https://badge.fury.io/py/mexbtcapi.svg)](https://badge.fury.io/py/mexbtcapi)
[![Coverage](https://coveralls.io/repos/github/goncalopp/mexbtcapi/badge.svg?branch=master)](https://coveralls.io/github/goncalopp/mexbtcapi)


MExBtcAPI
=========

The Multi-Exchange Bitcoin API

(actually, the multi-exchange multi-currency API)

Features
========

* Multi-currency support
* Multi-exchange support
* Seamless non-blocking streaming API support (websockets, WAMP)


Supported Exchanges
===================

* HTTP
    * ~~MtGox~~ (deprecated)
    * ~~Bitcoin-24~~ (deprecated)
    * Bitstamp
    * Poloniex
* Streaming
    * Poloniex

Project Goals
=============

* provide a set of well developed classes related to:
    * currencies (Amount, Currency, CurrencyPair, ExchangeRate)
    * currency exchanges (Order, Market, Exchange, Participant, Ticker)
* promote their use
* provide consistent APIs of various cryptocurrency exchanges

Donations
=========

Donations of bitcoin are kindly accepted at **1NBmTawDXqj8mNzGZSTzS1qmeyBhNideTM**

![Donation QR](donation_qrcode.png)

Usage / docs
============

Check the [demo](demo) directory for usage examples.

Development Status
==================

The ticker and orderbook APIs are stable.
The Order API is missing

Obtaining the latest source
===========================
https://github.com/goncalopp/mexbtcapi


Adding suport for a new exchange
================================
Please consult the doc/add_market file
