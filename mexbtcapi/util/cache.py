import datetime
import sqlite3


cache_storage={}
'''cache_storage is a dicionary.
example key: (function_name, args)
example value: (datetime, data)
where args is a tuple of the function call arguments'''

class CacheBackend(object):
    '''abstract class'''
    def __init__(self):
        pass
    def put(self, key, value):
        raise NotImplementedError()
    def get(self, key):
        raise NotImplementedError()

class DictinaryCacheBackend(CacheBackend):
    def __init__(self):
        self.d= {}
    def put(self, k, v):
        self.d[k]=v
    def get(self, k):
        return self.d.get(k)
        
class Cache:
    def __init__(self, backend,  timeout=1000):
        assert isinstance(backend, CacheBackend)
        self.backend=backend
        self.timeout= timeout

    def call(self, f, args, key_override=None, timeout= None):
        '''caches a function call with given argument. If the last call was
        executed less than TIMEOUT ms ago, returns the cached value, else
        executes function, caches the result, and returns it.'''
        def datetime_to_str(d):
            return d.isoformat()
        def str_to_datetime(s):
            return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
        def key_to_str(f, args):
            return (key_override or f.__name__) + str(args)
        def value_to_str(datetime, v):
            return datetime_to_str(datetime)+"|"+str(v)
        def str_to_value(s):
            i = s.index("|")
            d= str_to_datetime(s[:i])
            return d, s[i+1:]
        timeout= timeout or self.timeout
        k= key_to_str(f, args)
        now= datetime.datetime.now()
        ms= datetime.timedelta(microseconds=1000*timeout)
        
        cached_value= self.backend.get( k )
        
        if cached_value:
            last_execution, value= str_to_value(cached_value)
            delta= now - last_execution

        if not cached_value or delta>ms:
            result= f(*args)
            self.backend.put(k, value_to_str(now, result))
        else:
            result= value
        return result

def create_cache(timeout= 1000):
    '''creates a cache with a DictionaryCacheBackend'''
    return Cache(DictinaryCacheBackend(), timeout= timeout)


#demonstration
if __name__=="__main__":
    import random
    import time
    def f():
        print "CALL!"
        return random.randint(0,1000)
    c= Cache(DictinaryCacheBackend())
    print c.call(f,())
    time.sleep(0.99)
    print c.call(f,())
