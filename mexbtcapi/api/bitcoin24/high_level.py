from datetime import datetime, timedelta
from decimal import Decimal
from functools import partial
import logging

from mexbtcapi import concepts
from mexbtcapi.concepts.currencies import BTC, EUR, USD
from mexbtcapi.concepts.currency import Amount, Currency, ExchangeRate
from mexbtcapi.concepts.market import ActiveParticipant, Market as BaseMarket, Order, Trade
import http as low_level


logger = logging.getLogger(__name__)


class Bitcoin24Ticker(concepts.market.Ticker):
    TIME_PERIOD = timedelta(days=1)


class Bitcoin24Order(Order):
    def __init__(self, oid, *args, **kwargs):
        super(Bitcoin24Order, self).__init__(*args, **kwargs)
        self.oid = oid


class Bitcoin24Market(BaseMarket):
    MARKET_NAME = "Bitcoin-24"

    def __init__(self, currency):
        if not currency in (EUR, USD):
            raise Exception("Currency not supported on bitcoin-24:"+currency.name)
        super(Bitcoin24Market, self).__init__(self.MARKET_NAME, BTC, currency )
        self.xchg_factory = partial(concepts.currency.ExchangeRate, BTC, currency)
    

    def getTicker(self):
        logger.debug("getting ticker")
        time = datetime.utcnow()
        if self.sell_currency==EUR:
            data= low_level.get_ticker_EUR()
        elif self.sell_currency==USD:
            data= low_level.get_ticker_USD()
        else:
            raise Exception
        
        
        data2 = [Decimal(data[name])
                for name in ('high', 'low', 'avg', 'last', 'ask', 'bid')]
        high, low, avg, last, sell, buy = map(self.xchg_factory, data2)
        volume = None
        ticker = Bitcoin24Ticker(market=self, time=time, high=high, low=low,
                             average=avg, last=last, sell=sell, buy=buy,
                             volume=volume)
        return ticker


class Bitcoin24Participant(ActiveParticipant):
    def __init__(self, market, key, secret):
        super(MtGoxParticipant, self).__init__(market)
        self.private = low_level.Bitcoin24User(key, secret)

    def placeOrder(self, order):
        raise NotImplementedError

    def cancelOrder(self, order):
        raise NotImplementedError
