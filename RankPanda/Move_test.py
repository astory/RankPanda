#!/usr/bin/env python
import unittest

from Move import Move

class TestMove(unittest.TestCase):

    def testSetNumber(self):
        m = Move(0, 4, None, None, None)
        self.assertEquals(m._name, None)
        m.SetNumber(7)
        self.assertEquals(m._number, 7)
        self.assertEquals(m._name, 'Move 7')

if __name__ == '__main__':
    unittest.main()
