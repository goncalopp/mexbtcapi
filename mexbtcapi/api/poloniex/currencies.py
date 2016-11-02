from . import rest
from rest import get_all_currency_pairs
from mexbtcapi.currency import CurrencyPair

#refreshed 2016-10-31
CURRENCY_PAIRS = [CurrencyPair(*pair) for pair in
     [ ('BTC', 'RBY'),  ('USDT', 'REP'),  ('BTC', 'MMNXT'),  ('BTC', 'XVC'),  ('BTC', 'PINK'),  ('BTC', 'SYS'),  ('BTC', 'EMC2'),  ('BTC', 'C2'),  ('BTC', 'RADS'),  ('BTC', 'NOTE'),  ('BTC', 'MAID'),  ('BTC', 'SYNC'),  ('BTC', 'BCN'),  ('BTC', 'REP'),  ('BTC', 'BCY'),  ('XMR', 'NXT'),  ('USDT', 'ZEC'),  ('BTC', 'FCT'),  ('BTC', 'POT'),  ('BTC', 'NBT'),  ('USDT', 'ETH'),  ('USDT', 'BTC'),  ('BTC', 'LBC'),  ('BTC', 'EXP'),  ('BTC', 'DCR'),  ('USDT', 'ETC'),  ('BTC', 'LTBC'),  ('BTC', 'XPM'),  ('BTC', 'NOBL'),  ('BTC', 'NXT'),  ('BTC', 'VTC'),  ('ETH', 'STEEM'),  ('XMR', 'BLK'),  ('XMR', 'ZEC'),  ('BTC', 'GRC'),  ('BTC', 'BTCD'),  ('BTC', 'LTC'),  ('BTC', 'DASH'),  ('BTC', 'NAUT'),  ('ETH', 'ZEC'),  ('BTC', 'ZEC'),  ('BTC', 'BURST'),  ('BTC', 'BITCNY'),  ('BTC', 'UNITY'),  ('XMR', 'QORA'),  ('BTC', 'BELA'),  ('BTC', 'STEEM'),  ('BTC', 'ETC'),  ('BTC', 'ETH'),  ('BTC', 'CURE'),  ('BTC', 'HUC'),  ('BTC', 'LSK'),  ('BTC', 'BLOCK'),  ('BTC', 'CLAM'),  ('ETH', 'REP'),  ('BTC', 'QORA'),  ('BTC', 'QTL'),  ('XMR', 'DASH'),  ('USDT', 'DASH'),  ('BTC', 'BLK'),  ('BTC', 'XRP'),  ('USDT', 'NXT'),  ('BTC', 'NEOS'),  ('BTC', 'QBK'),  ('BTC', 'BTS'),  ('BTC', 'DOGE'),  ('BTC', 'XCN'),  ('XMR', 'BBR'),  ('BTC', 'SBD'),  ('BTC', 'XCP'),  ('USDT', 'LTC'),  ('BTC', 'BTM'),  ('USDT', 'XMR'),  ('ETH', 'LSK'),  ('BTC', 'VOX'),  ('BTC', 'OMNI'),  ('BTC', 'NAV'),  ('BTC', 'FLDC'),  ('BTC', 'XBC'),  ('BTC', 'DGB'),  ('BTC', 'SC'),  ('XMR', 'BTCD'),  ('BTC', 'BITS'),  ('BTC', 'VRC'),  ('BTC', 'GEO'),  ('BTC', 'RIC'),  ('XMR', 'MAID'),  ('BTC', 'XMG'),  ('BTC', 'STR'),  ('BTC', 'RDD'),  ('BTC', 'BBR'),  ('BTC', 'XMR'),  ('BTC', 'DIEM'),  ('BTC', 'SJCX'),  ('BTC', '1CR'),  ('BTC', 'VIA'),  ('BTC', 'XEM'),  ('BTC', 'NMC'),  ('BTC', 'SDC'),  ('ETH', 'ETC'),  ('XMR', 'LTC'),  ('BTC', 'ARDR'),  ('BTC', 'XST'),  ('BTC', 'HZ'),  ('XMR', 'XDN'),  ('BTC', 'FLO'),  ('USDT', 'XRP'),  ('BTC', 'GAME'),  ('BTC', 'PPC'),  ('BTC', 'CGA'),  ('BTC', 'XDN'),  ('XMR', 'BCN'),  ('BTC', 'MYR'),  ('XMR', 'DIEM'),  ('USDT', 'STR'),  ('BTC', 'NSR'),  ('BTC', 'IOC'),  ('BTC', 'AMP'),
     ]]

def refresh_currency_pairs():
    '''Gets the up-to-date list of currency pairs from the poloniex service'''
    global CURRENCY_PAIRS
    CURRENCY_PAIRS = get_all_currency_pairs()

def print_currency_pairs():
    print "[",
    for pair in CURRENCY_PAIRS:
        print """('{}', '{}'), """.format(*pair),
    print "]"
 
