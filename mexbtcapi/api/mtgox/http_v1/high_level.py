from datetime import datetime, timedelta
from decimal import Decimal
from functools import partial

from mexbtcapi import concepts
from mexbtcapi.concepts.currencies import BTC
from mexbtcapi.concepts.currency import Amount, ExchangeRate
from mexbtcapi.concepts.market import Market as BaseMarket, Order, Trade
import mtgox as low_level


class MtgoxTicker(concepts.market.Ticker):
    TIME_PERIOD = timedelta(days=1)


class Market(BaseMarket):
    MARKET_NAME = "MtGox"

    def __init__(self, currency):
        BaseMarket.__init__(self, self.MARKET_NAME, currency, BTC)

        # to convert low level data
        self.multiplier = low_level.multiplier
        self.xchg_factory = partial(concepts.currency.ExchangeRate,
                                    BTC, currency)

    def _multiplier(self, currency):
        return self.multiplier[currency.name]

    def getTicker(self):
        time = datetime.now()
        data = low_level.ticker(self.currency2.name)

        data2 = [Decimal(data[name]['value_int']) /
                 self._multiplier(self.currency1)
                 for name in ('high', 'low', 'avg', 'last', 'sell', 'buy')]
        high, low, avg, last, sell, buy = map(self.xchg_factory, data2)

        volume = long(data['vol']['value_int']) / self._multiplier(BTC)
        ticker = MtgoxTicker(market=self, time=time, high=high, low=low,
                             average=avg, last=last, sell=sell, buy=buy,
                             volume=volume)
        return ticker

    def getDepth(self):
        low_level_depth = low_level.depth()

        return {
            'asks': self._depthToOrders(low_level_depth['asks'], Order.ASK),
            'bids': self._depthToOrders(low_level_depth['bids'], Order.BID),
        }

    def _depthToOrders(self, depth, order_type):
        orders = []

        for d in depth:
            timestamp = datetime.fromtimestamp(d['stamp'] / 1000 / 1000)
            amount = Amount(
                Decimal(d['amount_int']) / self._multiplier(BTC), BTC)
            price = ExchangeRate(
                self.currency1, BTC,
                Decimal(d['price_int']) / self._multiplier(self.currency1))
            order = Order(self, timestamp, order_type, amount, price)
            orders.append(order)

        return orders

    def getTrades(self):
        low_level_trades = low_level.trades()

        # convert tradres to array of Trades
        trades = []
        for trade in low_level_trades:
            price = Decimal(trade['price_int']) / \
                self._multiplier(self.currency1)
            amount = Decimal(trade['amount_int']) / \
                self._multiplier(BTC)
            timestamp = datetime.fromtimestamp(trade['date'])

            btc_amount = Amount(amount, self.currency2)
            exchange_rate = ExchangeRate(self.currency1, self.currency2, price)

            t = Trade(self, timestamp, btc_amount, exchange_rate)
            t.tid = ['tid']

            trades.append(t)

        return trades
