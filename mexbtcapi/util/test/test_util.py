'''Tests for mexbtcapi.util.__init__.py'''
import unittest
from collections import namedtuple
from mexbtcapi.util import group_by

Holder = namedtuple('Holder', ('a', 'b'))

class GroupByTest(unittest.TestCase):
    def test_group_by_non_multi(self):
        h11, h12, h23 = (Holder(*x) for x in ((1, 1), (1, 2), (2, 3)))
        # empty
        grouped = group_by([], lambda x: x.a)
        self.assertEqual(dict(grouped), {})
        # single element
        grouped = group_by([h12], lambda x: x.a)
        self.assertEqual(dict(grouped), {1: set((h12,))})
        # single element (different key func)
        grouped = group_by([h12], lambda x: x.b)
        self.assertEqual(dict(grouped), {2: set((h12,))})
        # two elements, one group
        grouped = group_by([h11, h12], lambda x: x.a)
        self.assertEqual(dict(grouped), {1: set((h11, h12))})
        # two elements, two groups
        grouped = group_by([h11, h12], lambda x: x.b)
        self.assertEqual(dict(grouped), {1: set((h11,)), 2: set((h12,))})
        # three elements, one group
        grouped = group_by([h11, h12, h23], lambda x: 0)
        self.assertEqual(dict(grouped), {0: set((h11, h12, h23))})
        # three elements, two groups
        grouped = group_by([h11, h12, h23], lambda x: x.a)
        self.assertEqual(dict(grouped), {1: set((h11, h12)), 2: set((h23,))})
        # three elements, three groups
        grouped = group_by([h11, h12, h23], lambda x: x.b)
        self.assertEqual(dict(grouped), {1: set((h11,)), 2: set((h12,)), 3: set((h23,))})

    def test_group_by_multi(self):
        h11, h12, h23 = (Holder(*x) for x in ((1, 1), (1, 2), (2, 3)))
        h11_2 = Holder(1, 1)
        # empty
        grouped = group_by([], lambda x: x, multi=True)
        self.assertEqual(dict(grouped), {})
        # single element, one group
        grouped = group_by([h11], lambda x: x, multi=True)
        self.assertEqual(dict(grouped), {1: set([h11])})
        # single element, two groups
        grouped = group_by([h12], lambda x: x, multi=True)
        self.assertEqual(dict(grouped), {1: set([h12]), 2: set([h12])})
        # two elements, one group
        grouped = group_by([h11, h11_2], lambda x: x, multi=True)
        self.assertEqual(dict(grouped), {1: set((h11, h11_2))})
        # two elements, two groups
        grouped = group_by([h11, h12], lambda x: x, multi=True)
        self.assertEqual(dict(grouped), {1: set((h11, h12)), 2: set((h12,))})
        # two elements, three groups
        grouped = group_by([h11, h12], lambda x: [9, 8, 7], multi=True)
        self.assertEqual(dict(grouped), {9: set((h11, h12)), 7: set((h11, h12)), 8: set((h11, h12))})
        # three elements, one group
        grouped = group_by([h11, h12, h23], lambda x: [0], multi=True)
        self.assertEqual(dict(grouped), {0: set((h11, h12, h23))})
        # three elements, three groups
        grouped = group_by([h11, h12, h23], lambda x: x, multi=True)
        self.assertEqual(dict(grouped), {1: set((h11, h12)), 2: set((h12, h23)), 3: set([h23])})

if __name__ == '__main__':
    unittest.main()
