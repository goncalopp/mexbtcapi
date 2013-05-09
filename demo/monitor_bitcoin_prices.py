'''This example gets the bitcoin ticker data of every available exchange
every 30 seconds and saves  it immediatelly to disk, keeping a different 
file for each hour''' 

import time
from functools import partial
from datetime import datetime
from multiprocessing.pool import ThreadPool

import mexbtcapi
from mexbtcapi.util.monitor import Monitor, each_interval_callback
from mexbtcapi.concepts.currencies import USD, BTC
from mexbtcapi.util.ticker_archive import TickerArchive


def save_to_file(monitor):
    '''this function will be called periodically'''
    print datetime.utcnow(),": Saving data"
    tickers={}
    for d in monitor.data:
        for market, ticker in d[1].items():
            try:
                l=tickers[market]
            except KeyError:
                tickers[market]=l=[]
            tickers[market].append(ticker)
    for market, tickers in tickers.items():
        m=archive.get_market(market)
        m.add_data(tickers)
    monitor.reset_data()

if __name__=="__main__":
    markets= [api.market(USD) for api in mexbtcapi.apis]
    threads= ThreadPool( len(markets) )
    def marketticker(market):
        try:
            return market.getTicker()
        except:
            print "failed to get data for "+market.name
            return None
    def prices():
        prices= threads.map( marketticker, markets )
        p={}
        for i,m in enumerate(markets):
            if prices[i]:
                p[m]=prices[i]
        return p

    archive= TickerArchive("archive")
    save_each_day= partial( each_interval_callback, save_to_file, 'minute' )
    m= Monitor( prices, 30, save_each_day) #call prices() every 30 seconds
    m.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print "Quitting bitcoin monitor"
        save_to_file(m)
        m.stop()
