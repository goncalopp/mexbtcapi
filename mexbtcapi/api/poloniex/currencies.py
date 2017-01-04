from . import rest
from .rest import get_all_currency_pairs
from mexbtcapi.currency import CurrencyPair

#refreshed 2016-10-31
CURRENCY_PAIRS = [CurrencyPair(*pair) for pair in
     [('BTC', 'RBY'), ('USDT', 'REP'), ('BTC', 'UNITY'), ('BTC', 'PINK'), ('BTC', 'SYS'), ('BTC', 'EMC2'), ('BTC', 'C2'), ('BTC', 'RADS'), ('BTC', 'SC'), ('BTC', 'MAID'), ('BTC', 'BCN'), ('BTC', 'REP'), ('BTC', 'BCY'), ('XMR', 'NXT'), ('USDT', 'ZEC'), ('BTC', 'FCT'), ('USDT', 'ETH'), ('USDT', 'BTC'), ('BTC', 'LBC'), ('BTC', 'DCR'), ('USDT', 'ETC'), ('BTC', 'AMP'), ('BTC', 'XPM'), ('BTC', 'NOBL'), ('BTC', 'NXT'), ('BTC', 'VTC'), ('ETH', 'STEEM'), ('XMR', 'BLK'), ('XMR', 'ZEC'), ('BTC', 'GRC'), ('BTC', 'NXC'), ('BTC', 'BTCD'), ('BTC', 'LTC'), ('BTC', 'DASH'), ('BTC', 'NAUT'), ('ETH', 'ZEC'), ('BTC', 'ZEC'), ('BTC', 'BURST'), ('BTC', 'XVC'), ('XMR', 'QORA'), ('BTC', 'BELA'), ('BTC', 'STEEM'), ('BTC', 'ETC'), ('BTC', 'ETH'), ('BTC', 'CURE'), ('BTC', 'HUC'), ('BTC', 'STRAT'), ('BTC', 'LSK'), ('BTC', 'EXP'), ('BTC', 'CLAM'), ('ETH', 'REP'), ('BTC', 'QORA'), ('BTC', 'QTL'), ('XMR', 'DASH'), ('USDT', 'DASH'), ('BTC', 'BLK'), ('BTC', 'XRP'), ('USDT', 'NXT'), ('BTC', 'NEOS'), ('BTC', 'QBK'), ('BTC', 'BTS'), ('BTC', 'DOGE'), ('XMR', 'BBR'), ('BTC', 'SBD'), ('BTC', 'XCP'), ('USDT', 'LTC'), ('BTC', 'BTM'), ('USDT', 'XMR'), ('ETH', 'LSK'), ('BTC', 'OMNI'), ('BTC', 'NAV'), ('BTC', 'VOX'), ('BTC', 'XBC'), ('BTC', 'DGB'), ('BTC', 'NOTE'), ('XMR', 'BTCD'), ('BTC', 'BITS'), ('BTC', 'VRC'), ('BTC', 'RIC'), ('XMR', 'MAID'), ('BTC', 'XMG'), ('BTC', 'STR'), ('BTC', 'POT'), ('BTC', 'BBR'), ('BTC', 'XMR'), ('BTC', 'SJCX'), ('BTC', 'VIA'), ('BTC', 'XEM'), ('BTC', 'NMC'), ('BTC', 'SDC'), ('ETH', 'ETC'), ('XMR', 'LTC'), ('BTC', 'ARDR'), ('BTC', 'HZ'), ('XMR', 'XDN'), ('BTC', 'FLO'), ('USDT', 'XRP'), ('BTC', 'GAME'), ('BTC', 'PPC'), ('BTC', 'FLDC'), ('XMR', 'BCN'), ('BTC', 'MYR'), ('USDT', 'STR'), ('BTC', 'NSR'), ('BTC', 'IOC'), ]
     ]

def refresh_currency_pairs():
    '''Gets the up-to-date list of currency pairs from the poloniex service'''
    global CURRENCY_PAIRS
    CURRENCY_PAIRS = get_all_currency_pairs()

def currency_pairs_repr():
    lines = []
    lines.append("[")
    for pair in CURRENCY_PAIRS:
        lines.append("""('{}', '{}'), """.format(*pair),)
    lines.append("]")
    return "".join(lines)
 
