'''This module implements publisher-subscriber functionality'''

from abc import ABCMeta, abstractmethod
import logging
import six
log = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class Publisher(object):
    '''This class emits events'''
    def __init__(self):
        self._inactive_subscriptions = set()
        self._active_subscriptions = set()

    def subscribe(self, callback, start=True):
        sub = Subscription(self, callback)
        self._inactive_subscriptions.add(sub)
        if start:
            sub.start()
        return sub

    def is_active(self, subscription):
        in_active = subscription in self._active_subscriptions
        in_inactive = subscription in self._inactive_subscriptions
        if (not in_active) and (not in_inactive):
            raise Exception("Unknown subscription: {}".format(subscription))
        return in_active

    def start_subscription(self, subscription):
        '''Starts a Subscription, making it active'''
        if self.is_active(subscription):
            raise Subscription.StateException("Subscription already started: {}".format(subscription))
        starting = len(self._active_subscriptions) == 0
        self._inactive_subscriptions.remove(subscription)
        self._active_subscriptions.add(subscription)
        if starting:
            self._start()

    def stop_subscription(self, subscription):
        '''Stops a Subscription, making it inactive'''
        if not self.is_active(subscription):
            raise Subscription.StateException("Subscription already stopped: {}".format(subscription))
        stopping = len(self._active_subscriptions) == 1
        self._active_subscriptions.remove(subscription)
        self._inactive_subscriptions.add(subscription)
        if stopping:
            self._stop()

    def send_message(self, message):
        '''Makes this publisher send a message to its subscribers'''
        subscriptions = set(self._active_subscriptions) # make a copy, as original might be modified while running
        for subscription in subscriptions:
            subscription.callback(message)

    @abstractmethod
    def _start(self):
        pass

    @abstractmethod
    def _stop(self):
        pass


class Subscription(object):
    '''This class represents an association between a Publisher and a callback function'''
    class StateException(Exception):
        pass

    def __init__(self, publisher, callback):
        assert isinstance(publisher, Publisher)
        assert callable(callback)
        self.publisher = publisher
        self.callback = callback
        self._active = False

    @property
    def active(self):
        return self.publisher.is_active(self)

    def start(self):
        self.publisher.start_subscription(self)

    def stop(self):
        self.publisher.stop_subscription(self)

