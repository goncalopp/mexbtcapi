'''This module implements publisher-subscriber functionality'''

from abc import ABCMeta, abstractmethod
import logging
import six
log = logging.getLogger(__name__)


class Publisher(object):
    '''This class emits events'''
    def __init__(self):
        self._inactive_subscriptions = set()
        self._active_subscriptions = set()
        self._start_callbacks = []
        self._stop_callbacks = []
        self._active = False

    def subscribe(self, subscriber, start=True):
        sub = Subscription(self, subscriber)
        self._inactive_subscriptions.add(sub)
        if start:
            sub.start()
        return sub

    def is_subscription_active(self, subscription):
        in_active = subscription in self._active_subscriptions
        in_inactive = subscription in self._inactive_subscriptions
        if (not in_active) and (not in_inactive):
            raise Exception("Unknown subscription: {}".format(subscription))
        return in_active

    def start_subscription(self, subscription):
        '''Starts a Subscription, making it active'''
        if self.is_subscription_active(subscription):
            raise Subscription.StateException("Subscription already started: {}".format(subscription))
        starting = len(self._active_subscriptions) == 0
        self._inactive_subscriptions.remove(subscription)
        self._active_subscriptions.add(subscription)
        if starting:
            self._start()

    def stop_subscription(self, subscription):
        '''Stops a Subscription, making it inactive'''
        if not self.is_subscription_active(subscription):
            raise Subscription.StateException("Subscription already stopped: {}".format(subscription))
        stopping = len(self._active_subscriptions) == 1
        self._active_subscriptions.remove(subscription)
        self._inactive_subscriptions.add(subscription)
        if stopping:
            self._stop()

    def add_start_callback(self, f):
        self._start_callbacks.append(f)

    def add_stop_callback(self, f):
        self._stop_callbacks.append(f)

    def send_message(self, message):
        '''Makes this publisher send a message to its subscribers'''
        subscriptions = tuple(self._active_subscriptions) # make a copy, as original might be modified while running
        for subscription in subscriptions:
            subscription.send_message(message)
    
    @property
    def active(self):
        return self._active

    def _start(self):
        self._active = True
        for f in self._start_callbacks:
            f()

    def _stop(self):
        self._active = False
        for f in self._stop_callbacks:
            f()


class Subscription(object):
    '''This class represents an association between a Publisher and a subscriber.
    The subscriber can be either a callback function or another publisher'''
    class StateException(Exception):
        pass

    def __init__(self, publisher, subscriber):
        assert isinstance(publisher, Publisher)
        assert callable(subscriber) or isinstance(subscriber, Publisher)
        self.publisher = publisher
        self.subscriber = subscriber
        if isinstance(subscriber, Publisher):
            subscriber.add_start_callback(self.start)
            subscriber.add_stop_callback(self.stop)

    @property
    def active(self):
        return self.publisher.is_subscription_active(self)

    def start(self):
        self.publisher.start_subscription(self)

    def stop(self):
        self.publisher.stop_subscription(self)

    def send_message(self, message):
        if isinstance(self.subscriber, Publisher):
            self.subscriber.send_message(message)
        else:
            self.subscriber(message)

class MultichannelPublisher(Publisher):
    def __init__(self):
        Publisher.__init__(self)
        self._channel_to_sub = {}

    def _get_or_create_channel_subscription(self, channel_name):
        if not channel_name in self._channel_to_sub:
            channel_pub = Publisher()
            channel_sub = Subscription(self, channel_pub)
            self._channel_to_sub[channel_name] = channel_sub
            self._inactive_subscriptions.add(channel_sub)
        return self._channel_to_sub[channel_name]

    def send_message(self, message, channel):
        sub = self._get_or_create_channel_subscription(channel)
        sub.send_message(message)

    def subscribe(self, subscriber, channel, start=True):
        sub = self._get_or_create_channel_subscription(channel)
        channel_pub = sub.subscriber
        assert isinstance(channel_pub, Publisher)
        return channel_pub.subscribe(subscriber, start=start)
