#!/usr/bin/env python
import unittest

import Point as p
import RankLocation as rl

def MakePoints(points):
    return [p.Point(x,y) for (x,y) in points]

class Testrl(unittest.TestCase):
 
    def testInitWavy(self):
        points = MakePoints([(1,2), (3,4), (5,6), (7,8)])

        instance = rl.RankLocation(points, curved=True)
        self.assertEqual(instance._listOfPoints, points)
        self.assertTrue(instance.curved)

    def testInitZigZag(self):
        points = MakePoints([(1,2), (3,4), (5,6), (7,8)])

        instance = rl.RankLocation(points, curved=False)
        self.assertEqual(instance._listOfPoints, points)
        self.assertFalse(instance.curved)

    def testInitStraight(self):
        points = MakePoints([(1,2), (3,4)])

        instance = rl.RankLocation(points, curved=True)
        self.assertEqual(instance._listOfPoints, points)
        self.assertTrue(instance.curved)

    def testCompare(self):
        l1 = rl.RankLocation(MakePoints([(1,2), (3,4)]))
        l2 = rl.RankLocation(MakePoints([(1,2), (3,4)]))
        l3 = rl.RankLocation(MakePoints([(1,3), (3,4)]))
        l4 = rl.RankLocation(MakePoints([(1,2), (4,4)]))
        l5 = rl.RankLocation(MakePoints([(1,2), (3,4), (5,6)]))

        self.assertTrue(rl.Compare(l1, l2))
        self.assertFalse(rl.Compare(l1, l3))
        self.assertFalse(rl.Compare(l1, l4))
        self.assertFalse(rl.Compare(l1, l5))
        self.assertFalse(rl.Compare(l3, l4))

    def testGetMidPoint(self):
        p1 = p.Point(0,0)
        p2 = p.Point(0,10)
        p3 = p.Point(10,0)
        p4 = p.Point(10,10)

        self.assertEqual(rl.RankLocation([p1, p2]).GetMidPoint(), p.Point(0,5))
        self.assertEqual(rl.RankLocation([p1, p3]).GetMidPoint(), p.Point(5,0))
        self.assertEqual(rl.RankLocation([p1, p4]).GetMidPoint(), p.Point(5,5))

    def testIsListOfPointsLengthZero(self):
        f = rl.IsListOfPointsLengthZero
        self.assertTrue(f([]))
        self.assertTrue(f(MakePoints([(0,0), (0,0)])))
        self.assertFalse(f(MakePoints([(0,0), (0,1)])))
        self.assertFalse(f(MakePoints([(0,0), (0,1), (0,0)])))
	
	def testIsStraight(self):
		p1 = p.Point(0,0)
		p2 = p.Point(1,1)
		p3 = p.point(0,1)
		# TODO(astory): include collinearity

		self.assertTrue(rl.RankLocation([p1, p2]).IsStraight())
		self.assertFalse(rl.RankLocation([p1, p3, p2]).IsStraight())

if __name__ == '__main__':
    unittest.main()
