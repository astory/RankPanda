# Unit tests for Rank
# Copyright Alec Story, 2010

import mox
import unittest

import Move
import Rank
import RankIDGen
import RankLocation

m = mox.Mox()

class RankTest(unittest.TestCase):
    def setUp(self):
        self.move = m.CreateMock(Move.Move)
        self.idgen = m.CreateMock(RankIDGen.RankIDGen)
        self._id = 27
        self.idgen.GetID().AndReturn(self._id)
        self.move.GetRankIDGen().AndReturn(self.idgen)
        self.end_loc = m.CreateMock(RankLocation.RankLocation)
    
    def test_initialization(self):
        m.ReplayAll()
        r = Rank.Rank(self.end_loc, self.move)
        self.assertEqual(r._endLocation, self.end_loc)
        self.assertEqual(r._id, self._id)
        self.assertEqual(r._name, None)
        self.assertEqual(r._commandList, [])
        self.assertEqual(r._move, self.move)
        self.assertFalse(r.hold)
        self.assertFalse(r.grabbed)
        self.assertFalse(r.grabbedPoint)
        self.assertTrue(r._labelLocation)

        m.VerifyAll()
 
if __name__ == '__main__':
    unittest.main()
