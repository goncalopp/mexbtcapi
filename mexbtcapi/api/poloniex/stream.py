from mexbtcapi import pubsub
import datetime
from time import sleep
from autobahn_sync import AutobahnSync
from .currencies import CURRENCY_PAIRS
from .common import PoloniexTicker
import logging
log = logging.getLogger(__name__)

#this variable needs to be set correctly from another module
CURRENCY_PAIR_CODE_TO_MARKET = None

WEBSOCKET_URL = u"wss://api.poloniex.com:443"
TICKER_STREAM = 'ticker'
SUBSTREAMS = (TICKER_STREAM,)


class PoloniexCombinedStream(object):
    def __init__(self, url):
        self.app = AutobahnSync()
        self.url = url
        # each ticker_stream topic is a currency pair
        self.ticker_stream = pubsub.TopicPublisher()
        self.ticker_stream.add_start_callback( lambda : self.start_substream('ticker') )
        self.ticker_stream.add_stop_callback( lambda : self.stop_substream('ticker') )

    def start_transport(self):
        log.info('starting transport')
        self.app.run(url=self.url)

    def stop_transport(self):
        log.info('stopping transport')
        self.app.stop()

    def start_substream(self, substream):
        assert substream in SUBSTREAMS
        self.start_transport()
        if substream == TICKER_STREAM:
            self.ticker_subscription = self.app.session.subscribe(handler=self.ticker_callback, topic=TICKER_STREAM)

    def stop_substream(self, substream):
        assert substream in SUBSTREAMS
        if substream == TICKER_STREAM:
            self.app.session.unsubscribe(self.ticker_subscription)
            self.ticker_subscription = None
        self.stop_transport()

    def ticker_callback(self, *data):
        try:
            currency_pair_code, last, ask, bid, percent_change, base_volume, quote_volume, is_frozen, high, low = data
            market = get_market_from_curr_pair_code(currency_pair_code)
            time = datetime.datetime.now()
            ticker_data={"bid":bid, "ask":ask, "last":last, "high":high, "low":low}
            ticker = PoloniexTicker.from_data(ticker_data, market)
            self.ticker_stream.send(ticker, currency_pair_code)
        except Exception as e:
            import traceback
            traceback.print_exc()



poloniex_stream = PoloniexCombinedStream(WEBSOCKET_URL)
ticker_stream = poloniex_stream.ticker_stream

def get_market_from_curr_pair_code(curr_pair_code):
    if CURRENCY_PAIR_CODE_TO_MARKET is None:
        raise Exception("You need to set CURRENCY_PAIR_CODE_TO_MARKET")
    market = CURRENCY_PAIR_CODE_TO_MARKET.get(curr_pair_code, None)
    if market is None:
        raise Exception("Can't find market for {}. You may want to refresh the market list".format(curr_pair_code))
    return market

def get_ticker_stream_for_market(currency_pair_code):
    pub = pubsub.ChildPublisher(ticker_stream, topic=currency_pair_code)
    return pub

