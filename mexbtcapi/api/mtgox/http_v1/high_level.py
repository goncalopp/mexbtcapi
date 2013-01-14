from datetime import datetime
from decimal import Decimal
from functools import partial

from mexbtcapi import concepts
from mexbtcapi.concepts.currencies import BTC
from mexbtcapi.concepts.market import Market as BaseMarket
import mtgox as low_level


class MtgoxTicker(concepts.market.Ticker):
    TIME_PERIOD = 24 * 60 * 60


class Market(BaseMarket):
    MARKET_NAME = "MtGox"

    def __init__(self, currency):
        BaseMarket.__init__(self, self.MARKET_NAME, BTC, currency)
        # to convert low level data
        self.multiplier = low_level.multiplier[currency.name]
        self.xchg_factory = partial(concepts.currency.ExchangeRate,
                                    BTC, currency)

    def getTicker(self):
        time = datetime.now()
        data = low_level.ticker(self.c2.name)

        data2 = [(Decimal(data[name]['value_int']) / self.multiplier)
                    for name in ('high', 'low', 'avg', 'last', 'sell', 'buy')]
        hi, lo, av, la, se, bu = map(self.xchg_factory, data2)

        volume = long(data['vol']['value_int'])
        ticket = MtgoxTicker(market=self, time=time, high=hi, low=lo,
                             average=av, last=la, sell=se, buy=bu,
                             volume=volume)
        return ticket
