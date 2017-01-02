'''This module implements publisher-subscriber functionality'''

from collections import defaultdict
import logging
log = logging.getLogger(__name__)

# Can be used as a topic on TopicPublisher.send/subscribe - represents all the publisher's topics
ALL_TOPICS = '[ALL TOPICS]'

class Publisher(object):
    '''This class emits messages and keeps track of subscriptions to it'''
    def __init__(self):
        self._active_subscriptions = set()
        self._start_callbacks = []
        self._stop_callbacks = []

    def subscribe(self, subscriber, start=True, **kwargs):
        '''Subscribe to this publisher.
        subscriber must be either a callable or (another) Publisher'''
        sub = Subscription(self, subscriber, options=kwargs)
        if start:
            sub.start()
        return sub

    def is_subscription_active(self, subscription):
        '''Checks whether a given subscription is active'''
        if subscription.publisher is not self:
            raise Exception("Subscription is for a different Publisher")
        in_active = subscription in self._active_subscriptions
        return in_active

    def _start_subscription(self, subscription):
        log.info("Started %s", subscription)
        self._active_subscriptions.add(subscription)

    def start_subscription(self, subscription):
        '''Starts a Subscription, making it active'''
        if self.is_subscription_active(subscription):
            raise Subscription.StateException("Subscription already started: {}".format(subscription))
        self._start_subscription(subscription)
        if self.num_subscriptions == 1:
            self._start()

    def _stop_subscription(self, subscription):
        log.info("Stopped %s", subscription)
        self._active_subscriptions.remove(subscription)

    def stop_subscription(self, subscription):
        '''Stops a Subscription, making it inactive'''
        if not self.is_subscription_active(subscription):
            raise Subscription.StateException("Subscription already stopped: {}".format(subscription))
        self._stop_subscription(subscription)
        if self.num_subscriptions == 0:
            self._stop()

    def add_start_callback(self, func):
        '''Makes this publisher call func when it starts'''
        self._start_callbacks.append(func)

    def add_stop_callback(self, func):
        '''Makes this publisher call func when it stops'''
        self._stop_callbacks.append(func)

    @property
    def num_subscriptions(self):
        '''Returns the number of active subscriptions to this publisher'''
        return len(self._active_subscriptions)

    def _get_send_subscriptions(self, **kwargs):
        '''Returns the subscriptions (to self) that we should send() to'''
        # pylint: disable=unused-argument
        return self._active_subscriptions

    def send(self, message, **kwargs):
        '''Sends a message to this publisher's subscribers'''
        subscriptions = tuple(self._get_send_subscriptions(**kwargs)) # make a copy, as original might be modified while running
        for subscription in subscriptions:
            subscriber = subscription.subscriber
            if isinstance(subscriber, Publisher):
                subscriber.send(message)
            else:
                subscriber(message)

    @property
    def active(self):
        '''Whether this Publisher is active'''
        return self.num_subscriptions > 0

    def _start(self):
        log.info("Started %s", self)
        for func in self._start_callbacks:
            func()

    def _stop(self):
        log.info("Stopped %s", self)
        for func in self._stop_callbacks:
            func()

    def __repr__(self):
        return "{}(id={})".format(self.__class__.__name__, id(self) % 10000)

class ChildPublisher(Publisher):
    '''A publisher that subscribers to another publisher'''
    def __init__(self, parent, func=None, **kwargs):
        '''parent: the parent publisher to subscribe to
        func: The function on this ChildPublisher that messages from the parent
          should be sent to. If None, messages get directly routed to self.send
          (thus passing through unchanged)
        '''
        Publisher.__init__(self)
        func = func or self.send
        self.subscription = parent.subscribe(func, start=False, **kwargs)
        # start/stop the subscription to the parent when self starts/stops
        self.add_start_callback(self.subscription.start)
        self.add_stop_callback(self.subscription.stop)

class Subscription(object):
    '''This class represents an association between a Publisher and a subscriber.
    The subscriber is a callback function'''
    class StateException(Exception):
        pass

    def __init__(self, publisher, subscriber, options):
        assert isinstance(publisher, Publisher)
        if not callable(subscriber):
            raise TypeError("A subscriber must be a callable")
        self.publisher = publisher
        self.subscriber = subscriber
        self.options = options
        log.info("Created %s", self)

    @property
    def active(self):
        '''Whether this subscription is active.
        An inactive subscription doesn't receive messages'''
        return self.publisher.is_subscription_active(self)

    def start(self):
        '''Starts a subscription, making it active'''
        self.publisher.start_subscription(self)

    def stop(self):
        '''Stops a subscription, making it inactive'''
        self.publisher.stop_subscription(self)

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.publisher, self.subscriber, self.options)

class TopicPublisher(Publisher):
    '''A Publisher that exposes several "topics".
    Each topic is a independent stream of messages'''
    def __init__(self):
        Publisher.__init__(self)
        self._topic_subs = defaultdict(set) # subscriptions for each topic

    def send(self, message, topic=ALL_TOPICS, **kwargs):
        Publisher.send(self, message, topic=topic, **kwargs)

    def subscribe(self, subscriber, topic=ALL_TOPICS, start=True, **kwargs):
        return Publisher.subscribe(self, subscriber, start=start, topic=topic, **kwargs)

    def _get_send_subscriptions(self, topic=ALL_TOPICS, **kwargs):
        if topic == ALL_TOPICS:
            return Publisher._get_send_subscriptions(self, **kwargs)
        else:
            return self._topic_subs[topic] | self._topic_subs[ALL_TOPICS]

    def _start_subscription(self, subscription):
        Publisher._start_subscription(self, subscription)
        self._topic_subs[subscription.options['topic']].add(subscription)

    def _stop_subscription(self, subscription):
        Publisher._stop_subscription(self, subscription)
        self._topic_subs[subscription.options['topic']].remove(subscription)
