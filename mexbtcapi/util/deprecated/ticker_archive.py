import time
import os
from datetime import datetime
import numpy as np
import bisect

import mexbtcapi
from mexbtcapi.currencies import BTC
from mexbtcapi.market import Market
from mexbtcapi.numpy_conversions import numpy_to_ticker_list, ticker_list_to_numpy

class TickerArchive(object):
    '''A directory on disk with saved ticker data. 
    Each subdirectory is a market.'''
    def __init__( self, basepath ):
        self.basepath= basepath
        self.basepath= basepath
        if not os.path.isdir(self.basepath):
            os.mkdir(self.basepath)

    def get_market( self, market ):
        assert isinstance(market, Market)
        return TickerArchiveMarket( self, market )
    
    def list_markets(self):
        return os.listdir(self.basepath)

class TickerArchiveMarket(object):
    '''A directory on disk with saved ticker data.
    Each file contains the ticker data that starts at 
    UNIX_EPOCH + (BASE_TIME seconds) 
    and ends in  
    UNIX_EPOCH + (BASE_TIME seconds) + (INTERVAL seconds)'''
    BASE_TIME= 0    #unix timestamp. Defines
    INTERVAL= 60*60 #number of seconds each file stores
    def __init__( self, archive, market ):
        assert isinstance(archive, TickerArchive)
        assert isinstance(market, Market)
        self.archive= archive
        self.market= market
        self.basepath= os.path.join( archive.basepath, market.full_name )
        if not os.path.isdir(self.basepath):
            os.mkdir(self.basepath)
    
    def get_data( self, start_datetime, end_datetime ):
        '''get all the ticker data from start_datetime until end_datetime'''
        assert end_datetime > start_datetime
        intervals= self._get_interval_files( start_datetime, end_datetime )
        data=[]
        for i, interval in enumerate(intervals):
            i_data= self._getFile(interval[2]).get_data()
            if i!=0:
                start=0
            else:
                times= [x.time for x in i_data]
                start= bisect.bisect_left(times, start_datetime)
            if i!=len(intervals)-1:
                end=len(i_data)
            else:
                times= [x.time for x in i_data]
                end=bisect.bisect_left(times, end_datetime)
            data.extend( i_data[start:end] )
        return data

    def _all_files( self ):
        return sorted(os.listdir(self.basepath))
        
    def get_latest( self ):
        '''gets the latest ticker available'''
        f= self._getFile( int(self._all_files()[-1]) )
        return f.get_data()[-1]
    
    def get_nearest( self, date, fail_interval=None):
        file_n= self._datetime_to_filenumber(date)
        files= map(int,self._all_files())
        file_i= bisect.bisect_left(files, file_n)
        if file_i==len(files):
            file_i-=1
        file_n= files[file_i]
        f= self._getFile( file_n )
        data= f.get_data()
        if len(data)==0:
            raise Exception("No data")
        times= [ticker.time for ticker in data]
        i=bisect.bisect_left(times, date)
        if i==len(data):
            i-=1
        d= data[i]
        if fail_interval and abs(d.time-date)>fail_interval:
            raise Exception("interval is greater than fail_interval")
        return d
        
    def add_data( self, ticker_list ):
        '''add ticker data to disk'''
        ticker_list= sorted(ticker_list, key=lambda x:x.time)
        intervals= self._get_interval_files( ticker_list[0].time, ticker_list[-1].time )
        interval_i=0
        times= [x.time for x in ticker_list]
        while len(ticker_list)>0:
            point= bisect.bisect_left( times, intervals[interval_i][1] )
            f= self._getFile( intervals[interval_i][2] )
            f.add_data( ticker_list[0:point] )
            ticker_list= ticker_list[point:]
            times= times[point:]
            interval_i+=1

    def _get_interval_files( self, start_datetime, end_datetime ):
        '''returns a list of tuples of the following form:
        (file_start_datetime, file_end_datetime, file).'''
        f1,f2=  self._datetime_to_filenumber(start_datetime), self._datetime_to_filenumber(end_datetime)
        return [ (  self._filenumber_to_datetime(i), 
                    self._filenumber_to_datetime(i+1), 
                    i) for i in range(f1,f2+1) ]
    
    def _datetime_to_filenumber(self, datetime):
        '''calculates the filenumber that a datetime should be stored on'''
        return (int(time.mktime(datetime.timetuple())) - self.BASE_TIME) / self.INTERVAL
    
    def _filenumber_to_datetime(self, filenumber):
        '''calculates the first datetime that a filenumber should store'''
        return datetime.fromtimestamp(self.BASE_TIME+(filenumber*self.INTERVAL) )
    
    def _getFile(self, filenumber):
        assert isinstance(filenumber, (int, long))
        p= os.path.join(self.basepath, str(filenumber))
        return TickerArchiveMarketFile( p, self, filenumber)

class TickerArchiveMarketFile(object):
    def __init__( self, path, market, number ):
        assert isinstance(market, TickerArchiveMarket)
        self.market=market
        self.basepath= path
        self.number= number
    
    def _data_storage_verification(self, data):
        '''checks that present datetimes really should be stored on this
        file (and not another). Useful to detect mindless 
        TickerArchiveMarket.INTERVAL or BASE_TIME changes...'''
        if len(data):
            n1= self.market._datetime_to_filenumber(data[0].time)
            n2= self.market._datetime_to_filenumber(data[-1].time)
            assert n1==n2==self.number

    def _read_data(self):
        data= numpy_to_ticker_list(self.market.market, np.load( self.basepath ))
        self._data_storage_verification(data)
        return data
    
    def _write_data(self, data):
        self._data_storage_verification(data)
        np.save(open(self.basepath,'wb'), ticker_list_to_numpy(data, BTC))
    
    def get_data( self ):
        '''returns all the data from the file'''
        if not os.path.exists(self.basepath):
            return []
        data= self._read_data()
        return data
    
    def _merge(self, data1, data2):
        data= data1+data2
        data= sorted(data, key=lambda x:x.time)
        return data
    
    def add_data( self, data ):
        if not os.path.exists(self.basepath):
            all_data= data
        else:
            all_data= self._merge(data, self.get_data())
        self._write_data(all_data)
