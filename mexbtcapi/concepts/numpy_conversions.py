import numpy as np
import time
from datetime import datetime
from decimal import Decimal

from mexbtcapi.concepts.market import Ticker
from mexbtcapi.concepts.currency import ExchangeRate


#this is the number that a Decimal will be multiplied by, in order to
#store it as a integer on numpy
DECIMAL_MULTIPLY= 1000000000 #largest 10^X less than 2**32
MISSING_DATA= -1

FIELD_NAMES= ('timestamp',)+Ticker.RATE_FIELDS+Ticker.OTHER_FIELDS
N_FIELDS=    1 + len(Ticker.RATE_FIELDS) + len( Ticker.OTHER_FIELDS )
FIELD_TYPES= ('int64',)*N_FIELDS

#make sure we don't potencially forget any new field
assert Ticker.RATE_FIELDS==('high', 'low', 'average', 'last', 'sell', 'buy')
assert Ticker.OTHER_FIELDS==('volume',)

def _er_to_np( x, per_currency ):
    if x is None:
        return MISSING_DATA
    else:
        return _decimal_to_np(x.per(per_currency).exchange_rate)

def _np_to_er( x, f ):
    if x==MISSING_DATA:
        return None
    else:
        return f(_np_to_decimal(x))
        
def _decimal_to_np( x ):
    if x is None:
        return MISSING_DATA
    else:
        return long( DECIMAL_MULTIPLY*x )

def _np_to_decimal(x):
    if x==MISSING_DATA:
        return None
    else:
        return Decimal(long(x)) / DECIMAL_MULTIPLY

def ticker_list_to_numpy( ticker_list ):
    assert all([isinstance(x, Ticker) for x in ticker_list])
    assert len(ticker_list)>0
    #all tickers have the same market
    assert all([ticker_list[0].market==x.market for x in ticker_list])
    return np.array( map(_ticker_to_numpy, ticker_list), dtype=zip(FIELD_NAMES, FIELD_TYPES))
    
def _ticker_to_numpy( ticker ):
    timestamp= time.mktime( ticker.time.timetuple() )
    rates= (_er_to_np(getattr(ticker, x)) for x in Ticker.RATE_FIELDS)
    other= (_decimal_to_np(getattr(ticker, x)) for x in Ticker.OTHER_FIELDS)
    return (timestamp,)+tuple(rates)+tuple(other)



def numpy_to_ticker_list( market, numpy_array ):
    factory= lambda x: ExchangeRate( market.buy_currency, market.sell_currency, x)
    return [_numpy_to_ticker(market, factory, x) for x in map( tuple, numpy_array)]

def _numpy_to_ticker( market, factory, array_row ):
    time= datetime.fromtimestamp( array_row[0] )
    rates= [_np_to_er(x, factory) for x in array_row[1:1+len(Ticker.RATE_FIELDS)]]
    other= [_np_to_decimal(x) for x in array_row[1+len(Ticker.RATE_FIELDS):len(Ticker.OTHER_FIELDS)]]
    return Ticker( market, *(time,)+tuple(rates)+tuple(other) )
