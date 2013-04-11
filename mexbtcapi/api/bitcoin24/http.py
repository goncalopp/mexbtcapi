import json
import urllib
import urllib2

USER_URL= 'https://bitcoin-24.com/api/user_api.php'
TICKER_EUR_URL='https://bitcoin-24.com/api/EUR/ticker.json'
TICKER_USD_URL='https://bitcoin-24.com/api/USD/ticker.json'

class Bitcoin24Exception( Exception ):
    pass

def _main_base_request( url, parameters={}):

    parameters = urllib.urlencode(parameters)
    request = urllib2.Request(url, parameters)
    data = urllib2.urlopen(request).read()
    try:
        data = json.loads(data)
    except ValueError:
        raise Bitcoin24Exception('received non-json result: "'+data+'"')
    if 'message' in data:
        raise Bitcoin24Exception('API returned an error: "'+data['message']+'"')
    return data
    
class Bitcoin24User(object):
    def __init__(self, username, key):
        self.username=username
        self.key=key
    
    def _base_request(self, url, parameters):
        parameters.update( {'user': self.username, 'key':self.key} )
        return _main_base_request(url, parameters)
    
    def get_account_balance(self):
        return api._base_request(USER_URL, {'api':'get_balance'})
    
    def get_bitcoin_address(self):
        return api._base_request(USER_URL, {'api':'get_addr'})
    
    def get_open_orders(self):
        return api._base_request(USER_URL, {'api':'open_orders'})
    
    def cancel_order(self, order_id ):
        return api._base_request(USER_URL, {'api':'cancel_order', 'id':order_id})
    
    def get_trades(self):
            return api._base_request(USER_URL, {'api':'trades_json'})

    def buy_bitcoin(self, amount, price, currency):
        assert currency in ('EUR', 'USD')
        return api._base_request(USER_URL, {'api':'buy_btc', 'amount':amount, 'price':price, 'cur':currency})
    
    def sell_bitcoin(self, amount, price, currency):
        assert currency in ('EUR', 'USD')
        return api._base_request(USER_URL, {'api':'sell_btc', 'amount':amount, 'price':price, 'cur':currency})
    
    def withdraw_bitcoin(self, amount, address):
        return api._base_request(USER_URL, {'api':'withdraw_btc', 'amount':amount, 'address':address})

def get_ticker_EUR():
    return _main_base_request( TICKER_EUR_URL ) 

def get_ticker_USD():
    return _main_base_request( TICKER_USD_URL )
