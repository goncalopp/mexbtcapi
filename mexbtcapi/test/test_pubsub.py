'''Tests for pubsub.py'''

import unittest
from mock import MagicMock
from mexbtcapi.pubsub import Publisher, Subscription

class SimplePublisher(Publisher):
    '''Implements abstract methods'''
    def _start(self):
        pass
    def _stop(self):
        pass


class PublisherTest(unittest.TestCase):
    @classmethod
    def _get_subscribed_and_send(cls, publisher=None, start=True, message='novalue'):
        p = publisher or SimplePublisher()
        subscriber = MagicMock()
        m = message if message != 'novalue' else cls._get_test_messages()[0]
        subscription = p.subscribe(subscriber, start=start)
        p.send_message(m)
        return p, subscriber, subscription

    @classmethod
    def _get_test_messages(cls):
        return "message1", 2, False

    def test_create(self): 
        p = SimplePublisher()

    def test_subscribe_simple(self):
        p, subscriber, subscription = self._get_subscribed_and_send()
        m1, m2, _= self._get_test_messages()
        subscriber.assert_called_with(m1)
        self.assertEqual(subscriber.call_count, 1)
        p.send_message(m2)
        subscriber.assert_called_with(m2)
        self.assertEqual(subscriber.call_count, 2)

    def test_subscribe_delayed_start(self):
        p, subscriber, subscription = self._get_subscribed_and_send(start=False)
        subscriber.assert_not_called()
        subscription.start()
        m1, _, _ = self._get_test_messages()
        p.send_message(m1)
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
        p.send_message(m1)
        self.assertEqual(subscriber1.call_count, 3)
        self.assertEqual(subscriber2.call_count, 3)
        self.assertEqual(subscriber3.call_count, 2)
        subscriber1.assert_called_with(m3)
        subscriber2.assert_called_with(m1)
        subscriber3.assert_called_with(m1)    
        #unsubscribe 2
        subscription2.stop()
        p.send_message(m2)
        self.assertEqual(subscriber1.call_count, 3)
        self.assertEqual(subscriber2.call_count, 3)
        self.assertEqual(subscriber3.call_count, 3)
        subscriber1.assert_called_with(m3)
        subscriber2.assert_called_with(m1)
        subscriber3.assert_called_with(m2) 
        #unsubscribe 3
        subscription3.stop()
        p.send_message(123)
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
        p.send_message(m1)
        self.assertEqual(subscriber.call_count, 2)
        subscription.stop()
        p.send_message(m1)
        self.assertEqual(subscriber.call_count, 2)






if __name__ == '__main__':
    unittest.main()
