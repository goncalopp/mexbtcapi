from mexbtcapi.api.poloniex.rest import PoloniexMarket, client as rest_client
from mexbtcapi.currency import Currency, CurrencyPair

def get_currency_pairs_from_poloniex_service(rest_client):
    '''returns in order (counter_currency, base_currency).'''
    tickers = rest_client.marketTicker()
    pair_strs = tickers.keys()
    tuples = [s.split("_") for s in pair_strs]
    assert all(len(t) == 2 for t in tuples)
    pairs = [CurrencyPair(Currency(t[0]), Currency(t[1])) for t in tuples]
    return pairs

def currency_pairs_to_currencies(pairs, string=True):
    import itertools
    all_currencies = set(itertools.chain(*pairs))
    if string:
        return sorted([c.name for c in all_currencies])
    else:
        return all_currencies


currency_pairs = get_currency_pairs_from_poloniex_service(rest_client)
currencies = currency_pairs_to_currencies(currency_pairs)


markets = [PoloniexMarket(*cp) for cp in currency_pairs]
