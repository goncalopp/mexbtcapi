'''This is a separate file because these classes are used for both rest and stream APIs'''

from mexbtcapi.market import Ticker
import datetime

class PoloniexTicker(Ticker):
    TIME_PERIOD = datetime.timedelta(days=1)
    RATE_FIELDS = Ticker.RATE_FIELDS + ('last', 'high', 'low')
    NUMBER_FIELDS = Ticker.NUMBER_FIELDS + ()
    # TODO : support all poloniex ticker fields

    @classmethod
    def from_data(cls, data, market, time=None):
        time = time or datetime.datetime.now()
        rates = {k: market.create_er(data[k]) for k in PoloniexTicker.RATE_FIELDS}
        numbers = {k: Decimal((data[k])) for k in PoloniexTicker.NUMBER_FIELDS}
        d = {} ; d.update(rates) ; d.update(numbers)
        return PoloniexTicker(market=market, time=time, **d)


def rename_dict_keys(d, key_map):
    '''renames dictionary keys of d according to key_map'''
    d2 = {}
    for k,v in d.items():
        k = key_map.get(k, k)
        d2[k] = v
    return d2
