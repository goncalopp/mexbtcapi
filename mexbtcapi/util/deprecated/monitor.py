from datetime import datetime
import threading
import time
from collections import deque

import logging
logger = logging.getLogger(__name__)


class MonitorThread(threading.Thread):
    """executes a function f with sleep_time intervals in between
    """

    def __init__(self, sleep_time, callback):
        threading.Thread.__init__(self)
        self.sleep_time = sleep_time
        self.callback = callback
        self.stop_signal = False

    def run(self):
        start_time = datetime.utcnow()
        while True:
            self.callback()
            d = datetime.utcnow() - start_time
            seconds = (d.microseconds + (d.seconds + d.days * 24 * 3600) * \
                       (10 ** 6)) / float(10 ** 6)
            duration = seconds % self.sleep_time  # method execution time
            sleep_time = max(0, self.sleep_time - duration)
            if self.stop_signal:
                break
            time.sleep(sleep_time)

    def stop(self):
        self.stop_signal = True
        self.join()
        return

    @staticmethod
    def new_thread(sleep_time, callback):
        t = MonitorThread(sleep_time, callback)
        t.setDaemon(True)
        t.start()
        return t


class Monitor(object):
    """Calls a function periodically, saves its output on a list,
    together with the call datetime.
    Optionally flushes results to disk
    """

    def __init__(self, f, sleep_time=10, callback=None):
        """
        f: the function whose output to monitor
        memory: capacity of Monitor instance, in number of data entries
        sleep_time: time between calls to f, in seconds
        callback: function to call after every call to f
        """
        self.f = f
        self.sleep_time = sleep_time
        self.external_callback = callback
        self.reset_data()

    def reset_data(self):
        logger.debug("data reset")
        self.data = deque()

    def add_entry(self, data):
        logger.debug("entry added")
        d = (datetime.utcnow(), data)
        self.data.append(d)

    def callback(self):
        logger.debug("callback")
        if self.external_callback:
            self.external_callback(self)
        d = self.f()
        self.add_entry(d)

    def start(self):
        logger.debug("starting")
        self.thread = MonitorThread.new_thread(self.sleep_time, self.callback)

    def stop(self):
        logger.debug("stopping")
        assert self.thread
        self.thread.stop()

def limit_memory_callback( n_cells, monitor):
    '''make a partial of this function with the desired n_cells and set
    it as a callback of Monitor to limit memory capacity'''
    logger.debug("limit_memory_callback called")
    extra= len(monitor.data)-n_cells
    if extra>0:
        monitor.data= monitor.data[extra:]

def each_interval_callback( other_callback, interval_name, monitor ):
    '''make a partial of this function with a function and a 
    interval_name (that is a property of datetime) and set
    it (the partial) as a callback of Monitor to have it called once 
    each interval_name'''
    logger.debug("each_interval_callback called")
    if len(monitor.data)>1:
        a=getattr(monitor.data[-2][0], interval_name)
        b=getattr(monitor.data[-1][0], interval_name)
        if a!=b:
            other_callback( monitor )
