from mexbtcapi.api.bitstamp.rest import CURRENCIES, BitstampMarket


markets = [BitstampMarket(currency) for currency in CURRENCIES]
