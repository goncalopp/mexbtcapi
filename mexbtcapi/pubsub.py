'''This module implements publisher-subscriber functionality'''

from abc import ABCMeta, abstractmethod
import logging
import six
log = logging.getLogger(__name__)


class Publisher(object):
    '''This class emits events'''
    def __init__(self):
        self._active_subscriptions = set()
        self._start_callbacks = []
        self._stop_callbacks = []
        self._active = False

    def subscribe(self, subscriber, start=True):
        sub = Subscription(self, subscriber)
        log.info("{} has new subscription, id={}, subscriber={}, ".format(self, sub.id, subscriber))
        if start:
            sub.start()
        return sub

    def is_subscription_active(self, subscription):
        if subscription.publisher is not self:
            raise Exception("Subscription is for a different Publisher")
        in_active = subscription in self._active_subscriptions
        return in_active

    def start_subscription(self, subscription):
        '''Starts a Subscription, making it active'''
        if self.is_subscription_active(subscription):
            raise Subscription.StateException("Subscription already started: {}".format(subscription))
        starting = len(self._active_subscriptions) == 0
        self._active_subscriptions.add(subscription)
        if starting:
            self._start()

    def stop_subscription(self, subscription):
        '''Stops a Subscription, making it inactive'''
        if not self.is_subscription_active(subscription):
            raise Subscription.StateException("Subscription already stopped: {}".format(subscription))
        stopping = len(self._active_subscriptions) == 1
        self._active_subscriptions.remove(subscription)
        if stopping:
            self._stop()

    def add_start_callback(self, f):
        self._start_callbacks.append(f)

    def add_stop_callback(self, f):
        self._stop_callbacks.append(f)

    @property
    def num_subscriptions(self):
        '''Returns the number of active subscriptions to this publisher'''
        return len(self._active_subscriptions)

    def send(self, message):
        '''Makes this publisher send a message to its subscribers'''
        subscriptions = tuple(self._active_subscriptions) # make a copy, as original might be modified while running
        for subscription in subscriptions:
            subscription.send(message)
    
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

    def send(self, message):
        if isinstance(self.subscriber, Publisher):
            self.subscriber.send(message)
        else:
            self.subscriber(message)

    @property
    def id(self):
        return id(self)

class MultitopicPublisher(Publisher):
    def __init__(self):
        Publisher.__init__(self)
        self._topic_to_sub = {}

    def _get_or_create_topic_subscription(self, topic_name):
        if not topic_name in self._topic_to_sub:
            topic_pub = Publisher()
            topic_sub = Subscription(self, topic_pub)
            self._topic_to_sub[topic_name] = topic_sub
        return self._topic_to_sub[topic_name]

    def send(self, message, topic):
        sub = self._get_or_create_topic_subscription(topic)
        sub.send(message)

    def subscribe(self, subscriber, topic, start=True):
        sub = self._get_or_create_topic_subscription(topic)
        topic_pub = sub.subscriber
        assert isinstance(topic_pub, Publisher)
        return topic_pub.subscribe(subscriber, start=start)

    @property
    def num_subscriptions(self):
        return sum(sub.subscriber.num_subscriptions for sub in self._active_subscriptions)
