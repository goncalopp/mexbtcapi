'''Tests for pubsub.py'''

from collections import defaultdict
import unittest
from mock import MagicMock
import random

from mexbtcapi.pubsub import Publisher, Subscription, MultitopicPublisher

#make tests deterministic
random.seed(0)


class PublisherTest(unittest.TestCase):
    @classmethod
    def _get_subscribed_and_send(cls, publisher=None, start=True, message='novalue'):
        p = publisher or Publisher()
        subscriber = MagicMock()
        m = message if message != 'novalue' else cls._get_test_messages()[0]
        subscription = p.subscribe(subscriber, start=start)
        p.send(m)
        return p, subscriber, subscription

    @classmethod
    def _get_test_messages(cls):
        return "message1", 2, False

    def test_create(self): 
        p = Publisher()

    def test_subscribe_simple(self):
        p, subscriber, subscription = self._get_subscribed_and_send()
        m1, m2, _= self._get_test_messages()
        subscriber.assert_called_with(m1)
        self.assertEqual(subscriber.call_count, 1)
        p.send(m2)
        subscriber.assert_called_with(m2)
        self.assertEqual(subscriber.call_count, 2)

    def test_subscribe_delayed_start(self):
        p, subscriber, subscription = self._get_subscribed_and_send(start=False)
        subscriber.assert_not_called()
        subscription.start()
        m1, _, _ = self._get_test_messages()
        p.send(m1)
        subscriber.assert_called_with(m1)

    def test_start_subscription_twice(self):
        p, subscriber, subscription = self._get_subscribed_and_send(start=False)
        subscription.start()
        with self.assertRaises(Exception):
            subscription.start()
 
    def test_stop_subscription_twice(self):
        p, subscriber, subscription = self._get_subscribed_and_send(start=False)
        with self.assertRaises(Exception):
            subscription.stop()
        subscription.start()
        subscription.stop()
        with self.assertRaises(Exception):
            subscription.stop()
 
    def test_subscribe_multiple(self):
        m1, m2, m3 = self._get_test_messages()
        #subscribe 1
        p, subscriber1, subscription1 = self._get_subscribed_and_send()
        self.assertEqual(subscriber1.call_count, 1)
        subscriber1.assert_called_with(m1)
        #subscribe 2
        _, subscriber2, subscription2 = self._get_subscribed_and_send(publisher=p, message=m2)
        self.assertEqual(subscriber1.call_count, 2)
        self.assertEqual(subscriber2.call_count, 1)
        subscriber1.assert_called_with(m2)
        subscriber2.assert_called_with(m2)
        #subscribe 3
        _, subscriber3, subscription3 = self._get_subscribed_and_send(publisher=p, message=m3)
        self.assertEqual(subscriber1.call_count, 3)
        self.assertEqual(subscriber2.call_count, 2)
        self.assertEqual(subscriber3.call_count, 1)
        subscriber1.assert_called_with(m3)
        subscriber2.assert_called_with(m3)
        subscriber3.assert_called_with(m3)
        #unsubscribe 1
        subscription1.stop()
        p.send(m1)
        self.assertEqual(subscriber1.call_count, 3)
        self.assertEqual(subscriber2.call_count, 3)
        self.assertEqual(subscriber3.call_count, 2)
        subscriber1.assert_called_with(m3)
        subscriber2.assert_called_with(m1)
        subscriber3.assert_called_with(m1)    
        #unsubscribe 2
        subscription2.stop()
        p.send(m2)
        self.assertEqual(subscriber1.call_count, 3)
        self.assertEqual(subscriber2.call_count, 3)
        self.assertEqual(subscriber3.call_count, 3)
        subscriber1.assert_called_with(m3)
        subscriber2.assert_called_with(m1)
        subscriber3.assert_called_with(m2) 
        #unsubscribe 3
        subscription3.stop()
        p.send(123)
        self.assertEqual(subscriber1.call_count, 3)
        self.assertEqual(subscriber2.call_count, 3)
        self.assertEqual(subscriber3.call_count, 3)
        subscriber1.assert_called_with(m3)
        subscriber2.assert_called_with(m1)
        subscriber3.assert_called_with(m2)   

    def test_unsubscribe(self):
        p, subscriber, subscription = self._get_subscribed_and_send()
        self.assertEqual(subscriber.call_count, 1)
        m1, _, _ = self._get_test_messages()
        p.send(m1)
        self.assertEqual(subscriber.call_count, 2)
        subscription.stop()
        p.send(m1)
        self.assertEqual(subscriber.call_count, 2)

    def test_start_stop_callbacks(self):
        p, subscriber1, subscription1 = self._get_subscribed_and_send(start=False)
        start_cb, stop_cb = MagicMock(), MagicMock()
        p.add_start_callback(start_cb)
        p.add_stop_callback(stop_cb)
        _, subscriber2, subscription2 = self._get_subscribed_and_send(publisher=p, start=False)
        self.assertEqual(start_cb.call_count, 0)
        self.assertEqual(stop_cb.call_count, 0)
        subscription1.start()
        self.assertEqual(start_cb.call_count, 1)
        self.assertEqual(stop_cb.call_count, 0)
        subscription2.start()
        self.assertEqual(start_cb.call_count, 1)
        self.assertEqual(stop_cb.call_count, 0)
        subscription1.stop()
        self.assertEqual(start_cb.call_count, 1)
        self.assertEqual(stop_cb.call_count, 0)
        subscription2.stop()
        self.assertEqual(start_cb.call_count, 1)
        self.assertEqual(stop_cb.call_count, 1)
        subscription2.start()
        self.assertEqual(start_cb.call_count, 2)
        self.assertEqual(stop_cb.call_count, 1)
        subscription2.stop()
        self.assertEqual(start_cb.call_count, 2)
        self.assertEqual(stop_cb.call_count, 2)

    def test_active(self):
        p, subscriber1, subscription1 = self._get_subscribed_and_send(start=False)
        _, subscriber2, subscription2 = self._get_subscribed_and_send(publisher=p, start=False)
        self.assertEqual(p.active, False)
        subscription1.start()
        self.assertEqual(p.active, True)
        subscription2.start()
        self.assertEqual(p.active, True)
        subscription1.stop()
        self.assertEqual(p.active, True)
        subscription2.stop()
        self.assertEqual(p.active, False)
        subscription2.start()
        self.assertEqual(p.active, True)
        subscription2.stop()
        self.assertEqual(p.active, False)

class PublisherNestedTest(unittest.TestCase):
    def test_nested_simple(self):
        np1_sub1 = MagicMock()
        np1_sub2 = MagicMock()
        np2_sub1 = MagicMock()
        p = Publisher()
        np1 = Publisher()
        np2 = Publisher()
        np1_subs = p.subscribe(np1, start=False)
        np2_subs = p.subscribe(np2, start=False)
        self.assertEqual(p.active, False)
        self.assertEqual(np1.active, False)
        self.assertEqual(np2.active, False)
        #subscribe to np1
        np1.subscribe(np1_sub1, start=False)
        np1.subscribe(np1_sub2, start=False)
        self.assertEqual(p.active, False)
        self.assertEqual(np1.active, False)
        self.assertEqual(np2.active, False)
        np1_sub1_subs = np1.subscribe(np1_sub1)
        self.assertEqual(p.active, True)
        self.assertEqual(np1.active, True)
        self.assertEqual(np2.active, False)
        np1_sub2_subs = np1.subscribe(np1_sub2)
        self.assertEqual(p.active, True)
        self.assertEqual(np1.active, True)
        self.assertEqual(np2.active, False)
        #send message to p
        p.send(1)
        np1_sub1.assert_called_with(1)
        np1_sub2.assert_called_with(1)
        self.assertEqual(np2_sub1.call_count, 0)
        #subscribe to np2
        np2_sub1_subs = np2.subscribe(np2_sub1)
        self.assertEqual(p.active, True)
        self.assertEqual(np1.active, True)
        self.assertEqual(np2.active, True)
        #send message to p
        p.send(2)
        np1_sub1.assert_called_with(2)
        np1_sub2.assert_called_with(2)
        np2_sub1.assert_called_with(2)
        self.assertEqual(np1_sub1.call_count, 2)
        self.assertEqual(np1_sub2.call_count, 2)
        self.assertEqual(np2_sub1.call_count, 1)
        #unsubscribe to np2
        np2_sub1_subs.stop()
        self.assertEqual(p.active, True)
        self.assertEqual(np1.active, True)
        self.assertEqual(np2.active, False)
        #send message to p
        p.send(3)
        np1_sub1.assert_called_with(3)
        np1_sub2.assert_called_with(3)
        np2_sub1.assert_called_with(2)
        self.assertEqual(np1_sub1.call_count, 3)
        self.assertEqual(np1_sub2.call_count, 3)
        self.assertEqual(np2_sub1.call_count, 1)
        #unsubscribe to np1_sub2
        np1_sub2_subs.stop()
        self.assertEqual(p.active, True)
        self.assertEqual(np1.active, True)
        self.assertEqual(np2.active, False)
        #send message to p
        p.send(4)
        np1_sub1.assert_called_with(4)
        np1_sub2.assert_called_with(3)
        np2_sub1.assert_called_with(2)
        self.assertEqual(np1_sub1.call_count, 4)
        self.assertEqual(np1_sub2.call_count, 3)
        self.assertEqual(np2_sub1.call_count, 1)
        #unsubscribe to np1_sub1
        np1_sub1_subs.stop()
        self.assertEqual(p.active, False)
        self.assertEqual(np1.active, False)
        self.assertEqual(np2.active, False)
        #send message to p
        p.send(5)
        np1_sub1.assert_called_with(4)
        np1_sub2.assert_called_with(3)
        np2_sub1.assert_called_with(2)
        self.assertEqual(np1_sub1.call_count, 4)
        self.assertEqual(np1_sub2.call_count, 3)
        self.assertEqual(np2_sub1.call_count, 1)

class MultitopicPublisherTest(unittest.TestCase):
    def test_simple(self):
        c1_sub1 = MagicMock()
        c1_sub2 = MagicMock()
        c2_sub1 = MagicMock()
        p = MultitopicPublisher()
        self.assertEqual(p.active, False)
        #send messages to random topics
        p.send(9, "c1")
        p.send(9, "c2")
        p.send(9, "something")
        p.send(9, "mytopic")
        #subscribe to c1
        c1_sub1_subs = p.subscribe(c1_sub1, "c1")
        self.assertEqual(p.active, True)
        c1_sub2_subs = p.subscribe(c1_sub2, "c1")
        #send message to c1
        p.send(1, "c1")
        c1_sub1.assert_called_with(1)
        c1_sub2.assert_called_with(1)
        self.assertEqual(c2_sub1.call_count, 0)
        #subscribe to c2
        c2_sub1_subs = p.subscribe(c2_sub1, "c2")
        #send message to c2
        p.send(2, "c2")
        c1_sub1.assert_called_with(1)
        c1_sub2.assert_called_with(1)
        c2_sub1.assert_called_with(2)
        self.assertEqual(c1_sub1.call_count, 1)
        self.assertEqual(c1_sub2.call_count, 1)
        self.assertEqual(c2_sub1.call_count, 1)
        #unsubscribe to c2
        c2_sub1_subs.stop()
        self.assertEqual(p.active, True)
        #send message to c2
        p.send(3, "c2")
        c1_sub1.assert_called_with(1)
        c1_sub2.assert_called_with(1)
        c2_sub1.assert_called_with(2)
        self.assertEqual(c1_sub1.call_count, 1)
        self.assertEqual(c1_sub2.call_count, 1)
        self.assertEqual(c2_sub1.call_count, 1)
        #unsubscribe to c1_sub2
        c1_sub2_subs.stop()
        self.assertEqual(p.active, True)
        #send message to c1
        p.send(4, "c1")
        c1_sub1.assert_called_with(4)
        c1_sub2.assert_called_with(1)
        c2_sub1.assert_called_with(2)
        self.assertEqual(c1_sub1.call_count, 2)
        self.assertEqual(c1_sub2.call_count, 1)
        self.assertEqual(c2_sub1.call_count, 1)
        #unsubscribe to c1_sub1
        c1_sub1_subs.stop()
        self.assertEqual(p.active, False)
        #send message to c1
        p.send(5, "c1")
        c1_sub1.assert_called_with(4)
        c1_sub2.assert_called_with(1)
        c2_sub1.assert_called_with(2)
        self.assertEqual(c1_sub1.call_count, 2)
        self.assertEqual(c1_sub2.call_count, 1)
        self.assertEqual(c2_sub1.call_count, 1)
        self.assertEqual(p.active, False)

    def test_random(self):
        iterations = 100
        n_subscribers = 100
        n_topics = 10
        def join_prob_iter(i):
            '''probability of a subscriber joining, vs leaving, for a given iteration number'''
            return max(0.0, min(1.0, 1 - i / float(iterations) )) #start at 100%, end at 0%

        topics = ["c_"+str(n) for n in range(10)]
        messages = ["m_"+str(n) for n in range(100)]
        subscribers = [MagicMock() for x in range(n_subscribers)]
        unjoined = set(subscribers)
        joined = set()
        p = MultitopicPublisher()
        topic_subs = defaultdict(set)
        sub_topic = {}
        subscriptions = {} #keyed by subscriber
        n_received_messages = defaultdict(lambda:0) # keyed by subscriber

        for iteration in range(iterations):
            self.assertEqual(p.num_subscriptions, len(joined))
            join = random.random() < join_prob_iter(iteration)
            leave = not join
            if join and len(unjoined)>0:
                join_topic = random.choice(topics)
                join_sub = random.choice(tuple(unjoined))
                assert not join_sub in joined
                assert not join_sub in subscriptions
                subscription = p.subscribe(join_sub, join_topic)
                subscriptions[join_sub] = subscription
                topic_subs[join_topic].add(join_sub)
                sub_topic[join_sub] = join_topic
                unjoined.remove(join_sub)
                joined.add(join_sub)
            if leave and len(joined)>0:
                leave_sub = random.choice(tuple(joined))
                leave_topic = sub_topic[leave_sub]
                subscriptions[leave_sub].stop()
                subscriptions.pop(leave_sub)
                sub_topic[leave_sub] = None
                unjoined.add(leave_sub)
                joined.remove(leave_sub)
                topic_subs[leave_topic].remove(leave_sub)
            topic = random.choice(topics)
            message = random.choice(messages)
            p.send(message, topic)
            current_topic_subs = topic_subs[topic]
            for subscribed_sub in current_topic_subs:
                n_received_messages[subscribed_sub]+=1
                subscribed_sub.assert_called_with(message)
            for sub in subscribers:
                self.assertEqual(sub.call_count, n_received_messages[sub])




if __name__ == '__main__':
    unittest.main()
