from datetime import datetime, timedelta
from decimal import Decimal
from functools import partial
import logging

from mexbtcapi import concepts
from mexbtcapi.concepts.currencies import BTC
from mexbtcapi.concepts.currency import Amount, Currency, ExchangeRate
from mexbtcapi.concepts.market import ActiveParticipant, Market as BaseMarket, Order, Trade
import mtgox as low_level


logger = logging.getLogger(__name__)


class MtgoxTicker(concepts.market.Ticker):
    TIME_PERIOD = timedelta(days=1)

    def __repr__(self):
        return \
            "<MtgoxTicker({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})" \
            .format(self.market, self.time, self.high, self.high, self.last,
            self.volume, self.average, self.buy, self.sell)


class MtGoxOrder(Order):

    def __init__(self, oid, *args, **kwargs):
        super(MtGoxOrder, self).__init__(*args, **kwargs)
        self.oid = oid

    def __repr__(self):
        return \
            "<MtGoxOrder({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}>" \
            .format(self.market, self.timestamp, self.oid, self.buy_or_sell,
            self.from_amount, self.exchange_rate, self.properties, self.entity)


class MtGoxMarket(BaseMarket):
    MARKET_NAME = "MtGox"

    def __init__(self, currency):
        super(MtGoxMarket, self).__init__(self.MARKET_NAME, currency, BTC)

        # to convert low level data
        self.multiplier = low_level.multiplier
        self.xchg_factory = partial(concepts.currency.ExchangeRate,
                                    currency, BTC)

    def _multiplier(self, currency):
        return self.multiplier[currency.name]

    def getTicker(self):
        logger.debug("getting ticker")

        time = datetime.now()
        data = low_level.ticker(self.currency1.name)

        data2 = [Decimal(data[name]['value_int']) /
                 self._multiplier(self.currency1)
                 for name in ('high', 'low', 'avg', 'last', 'sell', 'buy')]
        high, low, avg, last, sell, buy = map(self.xchg_factory, data2)

        volume = Decimal(data['vol']['value_int']) / self._multiplier(BTC)
        ticker = MtgoxTicker(market=self, time=time, high=high, low=low,
                             average=avg, last=last, sell=sell, buy=buy,
                             volume=volume)
        return ticker

    def getDepth(self):
        logger.debug("getting depth")

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
        logger.debug("getting trades")

        low_level_trades = low_level.trades()

        # convert tradres to array of Trades
        trades = []
        for trade in low_level_trades:
            price = Decimal(trade['price_int']) / \
                self._multiplier(self.currency1)
            amount = Decimal(trade['amount_int']) / \
                self._multiplier(BTC)
            timestamp = datetime.fromtimestamp(trade['date'])

            btc_amount = Amount(amount, BTC)
            exchange_rate = ExchangeRate(self.currency1, BTC, price)

            t = Trade(self, timestamp, btc_amount, exchange_rate)
            t.tid = ['tid']

            trades.append(t)

        return trades


class MtGoxParticipant(ActiveParticipant):

    def __init__(self, market, key, secret):
        super(MtGoxParticipant, self).__init__(market)
        self.private = low_level.Private(key, secret)

    def placeOrder(self, order):
        """places an Order in the market for price/amount"""
        now = datetime.now()
        if order.is_buy_order():
            logger.debug("placing buy order")
            oid = self.private.bid(order.from_amount.value, order.exchange_rate)
            return MtGoxOrder(oid, self.market, now, Order.BID, amount, price, entity=self)
        else:
            logger.debug("placing ask order")
            oid = self.private.ask(amount, price)
            return MtGoxOrder(oid, self.market, now, Order.ASK, amount, price, entity=self)

    def cancelOrder(self, order):
        """Cancel an existing order"""
        assert(isinstance(order, MtGoxOrder))

        logger.debug("cancelling order {0}".format(order.oid))

        oid = order.oid
        if order.is_buy_order():
            result = self.private.cancel_bid(oid)
        else:
            result = self.private.cancel_ask(oid)

        if not result:
            raise ActiveParticipant.ActiveParticipantError()

    def getOpenOrders(self):
        """Gets all the open orders"""

        logger.debug("getting open orders")

        low_level_orders = self.private.orders()
        orders = []

        for o in low_level_orders:
            currency = Currency(o['currency'])
            oid = o['oid']
            timestamp = datetime.fromtimestamp(o['date'])
            order_type = Order.BID if o['type'] else Order.ASK
            amount = Amount(Decimal(o['amount']['value_int']) / self.market._multiplier(BTC), BTC)
            price = ExchangeRate(currency, BTC, Decimal(o['price']['value_int']) / self.market._multiplier(currency))
            order = MtGoxOrder( oid, self.market, timestamp, order_type, amount, price, entity=self)

            # add additional status from MtGox
            order.status = o['status']

            orders.append(order)

        return orders

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<MtGoxParticipant({0})>".format(self.currency1)
