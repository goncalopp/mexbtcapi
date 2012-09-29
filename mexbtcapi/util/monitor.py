import datetime
import threading
import time
from collections import deque


class MonitorThread(threading.Thread):
    '''executes a function f with sleep_time intervals in between'''
    def __init__(self, sleep_time, callback):
        threading.Thread.__init__(self)
        self.sleep_time= sleep_time
        self.callback= callback
        self.stop_signal=False
    
    def run(self):
        start_time= datetime.datetime.now()
        while True:
            self.callback()
            d=(datetime.datetime.now()-start_time)
            seconds=  (d.microseconds + (d.seconds + d.days * 24 * 3600) * 10**6) / float(10**6)
            duration= seconds % self.sleep_time #method execution time
            sleep_time= max(0, self.sleep_time - duration)
            if self.stop_signal:
                break
            time.sleep( sleep_time )

    def stop(self):
        self.stop_signal= True
        self.join()
        return

    @staticmethod
    def new_thread(sleep_time, callback):
        t = MonitorThread(sleep_time, callback)
        t.setDaemon(True)
        t.start()
        return t

class Monitor(object):
    '''calls a function periodically, saves its output on a list, together with the
    call datetime. optionally flushes results to disk'''
    def __init__(self, f, memory=100, sleep_time=10, callback=None, filename=None, flush_number=10, dont_repeat=True, to_text= lambda a: str(a), keep_datetime=True):
        '''
        f: the function whose output to monitor
        memory: capacity of Monitor instance, in number of data entries
        sleep_time: time between calls to f
        callback: function to call for every call to f
        filename: the file where to flush data to, if any
        flush_number: flush every flush_number entries
        dont_repeat: if the return from the call was the same as last, don't save it
        to_text: function to use to convert an entry to text for flushing to file
        '''
        self.f= f
        self.memory= memory
        self.sleep_time= sleep_time
        self.external_callback= callback
        self.filename= filename
        self.flush_number= flush_number
        self.dont_repeat= dont_repeat
        self.to_text= to_text
        self.keep_datetime= keep_datetime

        
        self.data= deque()
        self.flushed_to=0  #index of last flushed entry +1

    def _remove_entry(self):
        if self.filename:
            assert self.flushed_to>0
            self.flushed_to-=1
        self.data.popleft()

    def flush(self, always=True):
        if self.filename:
            not_flushed= len(self.data)-self.flushed_to
            if not_flushed>=self.flush_number or always:
                entries= [self.data[i] for i in xrange(self.flushed_to,len(self.data))]
                if self.keep_datetime:
                    result= []
                    for date,data in entries:
                        timestr= str(int(time.mktime(date.timetuple())))
                        valuestr= self.to_text(data)
                        result.append(timestr+","+valuestr)
                    entries= result
                else:
                    entries= map(self.to_text, entries)
                
                f= open(self.filename, "a")
                f.write("\n".join(entries)+"\n")
                f.close()
                self.flushed_to+=not_flushed
    
    def add_entry(self, data):
        different= True if not self.data else (data!=self.data[-1] if not self.keep_datetime else data!=self.data[-1][1])
        if different:
            if len(self.data)>=self.memory:
                self._remove_entry()
            d= (datetime.datetime.now(), data) if self.keep_datetime else data
            self.data.append(d)
            self.flush(always=False)

    def callback(self):
        d= self.f()
        if d:
            self.add_entry(d)
            if self.external_callback:
                self.external_callback(self)

    def start(self):
        self.thread= MonitorThread.new_thread(self.sleep_time, self.callback)
    def stop(self):
        assert self.thread
        self.thread.stop()
