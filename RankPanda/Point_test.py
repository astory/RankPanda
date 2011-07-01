#!/usr/bin/env python
import unittest

import Point

"""Unit tests for the Point module"""

class TestPoint(unittest.TestCase):

    def test_CompareTo(self):
        p1 = Point.Point(0.0, 0.0)
        p2 = Point.Point(0.0, 0.0)
        p3 = Point.Point(0.0, 1.0)
        p4 = Point.Point(1.0, 0.0)
        p5 = Point.Point(0.5, 0.5)
        p6 = Point.Point(0.1, 0.1)

        self.assertTrue(p1.CompareTo(p2))
        self.assertTrue(p2.CompareTo(p1))
        self.assertTrue(p1.CompareTo(p6))
        self.assertTrue(p6.CompareTo(p1))

        self.assertFalse(p1.CompareTo(p3))
        self.assertFalse(p3.CompareTo(p1))
        self.assertFalse(p1.CompareTo(p4))
        self.assertFalse(p4.CompareTo(p1))
        self.assertFalse(p1.CompareTo(p5))
        self.assertFalse(p5.CompareTo(p1))

if __name__ == '__main__':
    unittest.main()
