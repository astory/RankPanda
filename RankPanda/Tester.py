'''

Created on Oct 13, 2009



@author: Adam

'''



import Song
import Move
import Rank
import Commands
import Point
import RankLocation
import RankIDGen
import CubicHermiteSpline
import CoreWrapper
import copy
import pprint
import pygame
from pygame.locals import *


class Tester(object):
    def TestPoint1(self):
        p1 = Point.Point(0,0)
        p2 = Point.Point(10,10)
        print(p1.x)
        print(p2.y)

    def TestCubicHermiteSpline1(self):
        p1 = Point.Point(0,0)
        p2 = Point.Point(8, 4)
        p3 = Point.Point(16, 0)
        splineList = CubicHermiteSpline.SplineGenerator.GetSplines([p1, p2, p3], [None, None, None])
        pointList = CubicHermiteSpline.SplineGenerator.GetPoints(splineList)
        print(pointList)


    def TestSong1(self):
        song = Song.Song("DefaultSong", 50, 4)
        song.AddMove(1,8)
        song.AddMove(9,16)
        song.AddMove(4, 12)
        Move1 = song.GetCurrentMove()
        song.SetCurrentMove(0)
        Move0 = song.GetCurrentMove()
        print(str(Move0.GetNumber()))
        print(str(Move1.GetNumber()))
        print(str(Move0.GetFollowing().GetNumber()))
        print(str(Move1.GetPrior().GetNumber()))

        location1 = RankLocation.RankLocation([Point.Point(100,100), Point.Point(116,100)])
        location3 = RankLocation.RankLocation([Point.Point(200,200), Point.Point(216, 200)])
        r1 = song.currentMove.CreateRank(location1)
        r3 = song.currentMove.CreateRank(location3)
        r3ID = r3.GetID()
        song.GetCurrentMove().NameRank(r1.GetID(), 'A')
        print('ID = ' + str(r1.GetID()))

        song.SetCurrentMove(1)
        location2 = RankLocation.RankLocation([Point.Point(100,100), Point.Point(100,116)])
        print("location2's midpoint = " + str(location2.GetMidPoint().x) + ', ' + str(location2.GetMidPoint().y))
        r2 = song.currentMove.CreateRank(location2)
        song.GetCurrentMove().NameRank(r1.GetID(), 'A')

        print('ID = ' + str(r2.GetID()))

        cmdLst = r2.GetCommandList()

        i = 0
        while (i < len(cmdLst)):
            print(cmdLst[i].GetName() + ' ' + str(cmdLst[i].GetLength()))
            i = i + 1
        song.SetCurrentMove(0)
        song.SetCurrentMove(1)
        newcmdlist = song.GetCurrentMove().LookUpName('A').GetCommandList()
        i = 0
        while (i < len(newcmdlist)):
            print(newcmdlist[i].GetName() + ' ' + str(newcmdlist[i].GetLength()))
            i = i + 1
        song.SetCurrentMove(0)
        newr3 = song.GetCurrentMove().LookUpID(r3ID)
        listOfPoints = newr3.GetEndLocation().GetListOfPoints()
        i = 0
        while (i < len(listOfPoints)):
            print(repr(listOfPoints[i]))
            i = i + 1



    def TestCoreWrapper(self):
        core = CoreWrapper.CoreWrapper("Test", 50, [(1,4)], [])
        core.MoveAdded(1, 4, None)
        core.MoveAdded(5, 8, None)
        core.RankDrawn([Point.Point(100, 100), Point.Point(116, 100)])
        rID = core.GetRanks()[0][0]
        core.RankAddSpline(rID, 0)
        rLoc = core.GetRanks()[0][2]
        rLoc2 = copy.deepcopy(rLoc)
        print(repr(rLoc.GetListOfPoints()))
        print(repr(rLoc.GetListOfDrawingPoints()))
        print(repr(rLoc2.GetListOfPoints()))
        print(repr(rLoc2.GetListOfDrawingPoints()))


    def TestCHS(self):
        splines = CubicHermiteSpline.SplineGenerator.GetSplines([Point.Point(0, 0), Point.Point(4, 4), Point.Point(8, 0)], [None, None, None])
        print(repr(splines))
        lengths = CubicHermiteSpline.SplineGenerator.GetLengths(splines)
        print(repr(lengths))
        points = CubicHermiteSpline.SplineGenerator.GetPoints(splines)
        i = 0
        while (i < len(points)):
            j = 0
            while (j < len(points[i])):
                print('x = ' + str(points[i][j].x) + ', y = ' + str(points[i][j].y))
                j = j + 1
            i = i + 1


    def TestSaving(self):
        cw = CoreWrapper.CoreWrapper('Seven', 50, [(1,4)], [(1,1)])
        cw.MoveAdded(1, 9, None)
        cw.Save('Heyla')
        print('Done!')

    def TestLoading(self):
        cw = CoreWrapper.CoreWrapper('Things', 50, [(1,4)], [(1,1)])
        cw.Load('Heyla')
        print(cw.GetSong())
        print(cw.GetMoves()[0][1])
        print('Done!')


    def TestGetLocationAtCount(self):
        song = Song.Song('title', 100, 4)
        song.AddMove(1, 8) #1 - 32
        song.AddMove(9, 16) #33 - 64
        move0 = song.GetMoveList()[0]
        move1 = song.GetMoveList()[1]
        loc0 = RankLocation.RankLocation([Point.Point(100, 100), Point.Point(116, 100)])
        loc1 = RankLocation.RankLocation([Point.Point(100, 116), Point.Point(116, 116)])
        r0 = move0.CreateRank(loc0, name='A')
        r1 = move1.CreateRank(loc1, name='A')

        rls = song.GetRankLocationsAtCount(8)
#        print(str(len(rls)))
#        pprint.pprint(r1.GetCommandList())
#        pprint.pprint(rls)
#        pointList = rls[0][2].GetListOfPoints()
#        print('x0 = ' + str(pointList[0].x) + ', y0 = ' + str(pointList[0].y) + ', x1 = ' + str(pointList[1].x) + ', y1 = ' + str(pointList[1].y))



    def TestGetTimeDifferenceAtCount(self):
        song = Song.Song('title', 100, 4)
        song.AddMove(1, 8) #Counts 1 - 32
        song.AddMove(9, 16) #Counts 33 - 64
        move0 = song.GetMoveList()[0]
        move1 = song.GetMoveList()[1]
        loc0 = RankLocation.RankLocation([Point.Point(100, 100), Point.Point(116, 100)])
        loc1 = RankLocation.RankLocation([Point.Point(100, 116), Point.Point(116, 116)])
        r0 = move0.CreateRank(loc0, name='A')
        r1 = move1.CreateRank(loc1, name='A')
        song.AddWayPoint(1, 0) #Count 1
        song.AddWayPoint(15, 10000) #Count 57
        print('song.GetTimeDifferenceAtCount(30) = ' + str(song.GetTimeDifferenceAtCount(30)))

    def TestMusic(self):
        try:
            print('line one:')
            pygame.mixer.init()
            print('line two:')
            pygame.mixer.music.load('21 - Guys and Dolls (Reprise).mp3')
            print('line three:')
            pygame.mixer.music.play(1, 10.0)
            print('Loop:')
            i = 0
            stop = True
            while (stop and (i < 100000000)):
                i = i + 1
#                if (pygame.key.get_pressed()[K_s]):
#                    stop = False
#               if ((i % 100000) == 0):
#                    print(str(pygame.key.get_focused()))

            print('Done!')
        except:
            j = 0
            while (i < 10000):
                print('j = ' + str(j))
                j = j + 1
        finally:
            print('finally!')
        return 0

    def TestStuff(self, a=3, b=4):
        print('a = ' + str(a))
        print('b = ' + str(b))


#Tester().TestStuff(b = 8, a = 15)
Tester().TestMusic()



