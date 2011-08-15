import Move
import copy
import pprint
import math
import pygame
from pygame.locals import *


class Song(object):
    def __init__(self, title, numberMeasures, defaultCountsPerMeasure):
        self.InitMusicPlayer()
        self._moveList = []
        self.title = title
        self._numberMeasures = numberMeasures
        self._countsPerMeasureIndex = dict()
        self._stepsPerCountIndex = dict()
        self.currentMove = None
        self._stepsPerCountIndex[1] = 1
        self._countsPerMeasureIndex[1] = defaultCountsPerMeasure
        self._wayPointList = dict()
        self._wayPointListItems = []
        self.AddMoveByCount(0,1)
        self.animating = False
        self.curAnimatingCount = 0
        self.songLoaded = False


    # Add in a new change in the time signature.  Note that this may change
    # the length of the song, making it shorter than before.  What to do
    # about this if a move hangs off the end?
    def AddCountsPerMeasureChange(self, measureNumber, newCountsPerMeasure):
        self._countsPerMeasureIndex[measureNumber] = newCountsPerMeasure

    # Add in a new change to the number of steps per count.  Same problem as
    # above.  Note that we should really work in 'steps' but so far the whole
    # program thinks in terms of 'counts'
    def AddStepsPerCountChange(self, measureNumber, newStepsPerMeasure):
        self._stepsPerCountIndex[measureNumber] = newStepsPerMeasure

    # Resets the entire index to be the default.
    def ResetCountsPerMeasure(self, defaultCountsPerMeasure):
        self._countsPerMeasureIndex = dict()
        self._countsPerMeasureIndex[1] = defualtCountsPerMeasure

    def ResetStepsPerCount(self):
        self._stepsPerCountIndex = dict()
        self._stepsPerCountIndex[1] = 1

    # Straightforward.
    def GetNumberMeasures(self):
        return self._numberMeasures

    # Same problem as above - what if you have a move hanging off the end?
    def SetNumberMeasures(self, numberMeasures):
        self._numberMeasures = numberMeasures

    def SetTitle(self, newTitle):
        self.title = newTitle

    def GetTitle(self):
        return self.title

    def GetCountsPerMeasureIndex():
        return self._countsPerMeasureIndex

    def GetStepsPerCountIndex():
        return self._stepsPerCountIndex

    def GetCurrentMove(self):
        return self.currentMove

    def SetCurrentMove(self, number):
        self.currentMove = self._moveList[number]

    def GetMoveList(self):
        return (self._moveList)

    # This chould call the constructor of Move.Move, passing in the necessary
    # information.  Use own helper methods to determine steps.
    def AddMove(self, beginningMeasure, endMeasure):
        startCount = self.ConvertMeasureToCount(beginningMeasure)
        endCount = self.ConvertMeasureToCount(endMeasure + 1)
        return self.AddMoveByCount(startCount, endCount)

    def AddMoveByCount(self, startCount, endCount):
        length = startCount - endCount
        i = 0
        stop = False
        while ((i < len(self._moveList)) and (not stop)):
            if (self._moveList[i].GetStartCount() > startCount):
                stop = True
            else:
                i = i + 1
        if (i > 0):
            if ((self._moveList[i - 1].GetStartCount() + self._moveList[i - 1].GetLength()) > startCount):
                return None

        if (i < len(self._moveList)):
            if (self._moveList[i].GetStartCount() < endCount):
                return None
        prior = None
        following = None
        settingPrior = False
        settingFollowing = False
        if (i != (len(self._moveList))):
            if (self._moveList[i].GetStartCount() == endCount):
                following = self._moveList[i]
                settingFollowing = True
        if (i != 0):
            if ((self._moveList[i - 1].GetStartCount() + self._moveList[i - 1].GetLength()) == (startCount)):
                prior = self._moveList[i - 1]
                settingPrior = True
        newMove = Move.Move(startCount, (endCount - startCount), prior, following, i)
        self._moveList.insert(i, newMove)
        if (settingFollowing):
            self._moveList[i + 1].SetPrior(newMove)
        if (settingPrior):
            self._moveList[i - 1].SetFollowing(newMove)
        i = i + 1
        while (i < len(self._moveList)):
            self._moveList[i].SetNumber(i)
            i = i + 1
        self.currentMove = newMove
        return newMove



    # Utility method.  Note that this is count 1 of the measure.
    def ConvertMeasureToCount(self, measureNumber):
        changeList = sorted(self._countsPerMeasureIndex)
        i = 0
        curMeasure = 0
        accum = 0
        while (curMeasure < measureNumber):
            if ((len(changeList) > i + 1) and (changeList[i + 1] < measureNumber)):
                accum += (changeList[i + 1] - changeList[i]) * self._countsPerMeasureIndex[changeList[i]]
                curMeasure = changeList[i + 1]
            else:
                accum += (measureNumber - changeList[i]) * self._countsPerMeasureIndex[changeList[i]]
                curMeasure = measureNumber
            i += 1
        return (accum + 1)


    # Utility method  Returns which measure the count is in.
    # May be broken
    def ConvertCountToMeasure(self, countNumber):
        changeList = sorted(self._countsPerMeasureIndex)
        i = 0
        curCount = 0
        measureNumber = 0
        while (curCount < countNumber):
            if ((len(changeList) > (i + 1)) and ((curCount + ((changeList[i + 1] - changeList[i])*self._countsPerMeasureIndex[changeList[i]])) < countNumber)):
                curCount = curCount + ((changeList[i + 1] - changeList[i])*self._countsPerMeasureIndex[changeList[i]])
            else:
                measureNumber = changeList[i] + ((countNumber - curCount) / (self._countsPerMeasureIndex[changeList[i]]))
                curCount = countNumber
        return math.floor(measureNumber)


    # From the move with the number sourceNumber, read in every Rank.
    # For each one, create a new Rank in the move numbered recieveNumber
    # with that rank's location and name.
    def ImportRanks(self, sourceNumber, recieveNumber):
        self._moveList[recieveNumber].DeleteAllRanks()
        i = 0
        allRanks = self._moveList[sourceNumber].GetAllRanks()
        while (i < len(allRanks)):
            self._moveList[recieveNumber].CreateRank(
                    copy.deepcopy(allRanks[i].GetEndLocation()),
                    name=allRanks[i].GetName())
            i = i + 1


    # Delete the move given.  This entails removing all relevant prior/following
    # markers AND resetting the command lists for the ranks of the following
    # move.
    # Use Move.DeleteRank()
    def DeleteMove(self, moveNumber):
        relevantMove = self._moveList[moveNumber]
        if (relevantMove.GetPrior() is not None):
            relevantMove.GetPrior().SetFollowing(None)
        if (relevantMove.GetFollowing() is not None):
            relevantMove.GetFollowing.SetPrior(None)
        self._moveList.pop(moveNumber)
        while (moveNumber < len(self._moveList)):
            self._moveList[moveNumber].SetNumber(moveNumber)
            moveNumber = moveNumber + 1


    # Merge the move at firstMoveNumber and the move right after.
    # Precondition:  The two moves are adjacent.
    # To determine what to do with ranks, here's an example.  You're merging
    # moves currently numbered 3 and 4.  Rank A exists in move 2, 3, 4, and 5.
    # Merge Rank A's command lists for moves 3 and 4.
    # Rank B exists in moves 3, 4, and 5, but not in move 2.
    # ?????  Do we delete the command list from move 4?
    # Rank C exists in moves 2, 4, and 5, but not 3.
    # Neither move 3 nor 4 can have a command list yet.  When merging the
    # two moves, however, auto-generate the commands.
    # Rank D exists in moves 2, 3, and 5, but not 4.
    # Keep move 3's old commands, auto-generale the next ones (can we do this?)
    # to finish out that move, and in the move formerly known as move 5,
    # auto-generate the commands.
    # Use the similar methods of the lower classes.
    def MergeMoves(self, firstMoveNumber):
        if (firstMoveNumber >= (len(self._moveList) - 1)):
            return
        firstMove = self._moveList[firstMoveNumber]
        secondMove = self._moveList[firstMoveNumber + 1]
        if ((firstMove.GetStartCount() + firstMove.GetLength()) != secondMove.GetStartCount()):
            return
        newMove = secondMove.MergeWithPrior()
        self._moveList.pop(firstMoveNumber)
        self._moveList.pop(firstMoveNumber)
        self._moveList.insert(firstMoveNumber, newMove)
        while (firstMoveNumber < len(self._moveList)):
            self._moveList[firstMoveNumber].SetNumber(firstMoveNumber)
            firstMoveNumber = firstMoveNumber + 1






    # Much more straightforward.  Simply split a move at the given count.
    # Split everything - command lists, positions, etc.
    # Use the similar methods of the lower classes.
    def SplitMove(self, moveNumber, count):
        curSelMoveNumber = self.currentMove.GetNumber()
        if (moveNumber >= len(self._moveList)):
            return
        moveToSplit = self._moveList[moveNumber]
        newMoves = moveToSplit.Split(count)
        self._moveList[moveNumber] = newMoves[0]
        self._moveList.insert((moveNumber + 1), newMoves[1])
        while (moveNumber < len(self._moveList)):
            self._moveList[moveNumber].SetNumber(moveNumber)
            moveNumber = moveNumber + 1
        self.currentMove = self._moveList[curSelMoveNumber]


    # Change the startcount for a series of moves.  Move order shouldn't change.
    def ShiftMoveBlock(self, firstMoveNumber, counts):
        if (firstMoveNumber >= len(self._moveList)):
            return
        firstMove = self._moveList[firstMoveNumber]
        startCount = firstMove.GetStartCount()
        curMove = firstMove
        while (curMove.GetFollowing() is not None):
            curMove = curMove.GetFollowing
        endCount = curMove.GetStartCount() + curMove.GetLength()
        finalMoveNumber = curMove.GetNumber()
        if (counts > 0):
            if (finalMoveNumber + 1 < len(self._moveList)):
                if ((endCount + counts) > self._moveList[finalMoveNumber + 1].GetStartCount()):
                    return
                if ((endCount + counts) == self._moveList[finalMoveNumber + 1].GetStartCount()):
                    curMove.SetFollowing(self._moveList[finalMoveNumber + 1])
                    self._moveList[finalMoveNumber + 1].SetPrior(curMove)
            curMove = firstMove
            while (curMove.GetFollowing() is not None):
                curMove.SetStartCount(curMove.GetStartCount() + counts)
                curMove = curMove.GetFollowing()
        else:
            if (startCount + counts <= 0):
                return
            if (firstMoveNumber > 0):
                if ((startCount + counts) < (self._moveList[firstMoveNumber - 1].GetStartCount() + self._moveList[firstMoveNumber - 1].GetLength())):
                    return
                if ((startCount + counts) == (self._moveList[firstMoveNumber - 1].GetStartCount() + self._moveList[firstMoveNumber - 1].GetLength())):
                    firstMove.SetPrior(self._moveList[firstMoveNumber - 1])
                    self._moveList[firstMoveNumber - 1].SetFollowing(firstMove)
            curMove = firstMove
            while (curMove.GetFollowing() is not None):
                curMove.SetStartCount(curMove.GetStartCount() + counts)
                curMove = curMove.GetFollowing()
        self.currentMove = self._moveList[firstMoveNumber]


    def GetWayPointList(self):
        return self._wayPointListItems

    def AddWayPoint(self, measureNumber, timeInMilliseconds):
        self._wayPointList[self.ConvertMeasureToCount(measureNumber)] = timeInMilliseconds
        self._wayPointListItems = sorted(self._wayPointList.items())

    def RemoveWayPoint(self, measureNumber):
        count = self.ConvertMeasureToCount(measureNumber)
        if (count in self._wayPointList):
            del self._wayPointList[count]
        self._wayPointListItems = sorted(self._wayPointList.items())

    def GetTimeDifferenceAtCount(self, count):
        sortedWayPoints = self._wayPointListItems
        i = 0
        searching = True
        found = False
        while (searching):
            if ((i + 1) >= len(sortedWayPoints)):
                searching = False
            else:
                if (sortedWayPoints[i][0] > count):
                    searching = False
                else:
                    if (sortedWayPoints[i + 1][0] > count):
                        searching = False
                        found = True
                    else:
                        i = i + 1

        if (found):
            finalcount = sortedWayPoints[i][0]
            finaltime = sortedWayPoints[i][1]
            begincount = sortedWayPoints[i - 1][0]
            begintime = sortedWayPoints[i - 1][1]
            return (finaltime - begintime)/float(finalcount - begincount)
        else:
            return 1


    def GetRankLocationsAtCount(self, count):
        i = 0
        searching = True
        found = False
        while (searching):
            if (i < len(self._moveList)):
                if (self._moveList[i].GetStartCount() <= count):
                    if (self._moveList[i].GetStartCount() + self._moveList[i].GetLength() > count):
                        searching = False
                        found = True
                    else:
                        i = i + 1
                else:
                    searching = False
            else:
                searching = False
        if (found):
            ranks = self._moveList[i].GetAllRanks()
            rankList = []
            j = 0
            while (j < len(ranks)):
                rankList.append((ranks[j].GetID(), ranks[j].GetName(), ranks[j].GetLocationAtCount(count - self._moveList[i].GetStartCount())))
                j = j + 1
            return rankList
        else:
            return None



    def CanAnimate(self, count):
        if (len(self._wayPointList) < 2):
            return False
        if (count < self._wayPointListItems[0][0]):
            return False
        if (count >= self._wayPointListItems[-1][0]):
            return False
        return True


    def AnimationBegin(self, count):
        if self.CanAnimate(count):
            self.animating = True
            self.curAnimatingCount = count
            self.StartMusicPlayingAtCount(count)
            return self.AnimationStep()
        else:
            return None

    def AnimationStep(self):
        if (not self.animating):
            return (None, 0)
        if (self.songLoaded):
            time = self.timeOffset + pygame.mixer.music.get_pos()
            count = self.ConvertTimeToCount(time)
            if (count is not None):
                self.curAnimatingCount = count
            else:
                self.curAnimatingCount = self.curAnimatingCount + 1
            locs = self.GetRankLocationsAtCount(self.curAnimatingCount)
            time = self.GetTimeDifferenceAtCount(self.curAnimatingCount) / float(8)
        else:
            locs = self.GetRankLocationsAtCount(self.curAnimatingCount)
            time = self.GetTimeDifferenceAtCount(self.curAnimatingCount)
            self.curAnimatingCount = self.curAnimatingCount + 1
        return (locs, time, self.curAnimatingCount)

    def AnimationStop(self):
        self.animating = False
        self.curAnimatingCount = 0
        pygame.mixer.music.stop()

    def StartMusicPlayingAtCount(self, count):
        if (self.songLoaded):
            sortedWayPoints = self._wayPointListItems
            i = 0
            searching = True
            found = False
            timeSoFar = 0
            countsSoFar = 0
            while (searching):
                if ((i + 1) >= len(sortedWayPoints)):
                    searching = False
                else:
                    if (sortedWayPoints[i][0] > count):
                        searching = False
                    else:
                        if (sortedWayPoints[i + 1][0] > count):
                            searching = False
                            found = True
                        else:
                            i = i + 1
            if (found):
                finalcount = sortedWayPoints[i][0]
                finaltime = sortedWayPoints[i][1]
                begincount = sortedWayPoints[i - 1][0]
                begintime = sortedWayPoints[i - 1][1]
                timediff = (finaltime - begintime)/float(finalcount - begincount)
                totaltime = begintime + ((count - begincount) * timediff)
            else:
                totaltime = 1.0
            self.timeOffset = totaltime
            pygame.mixer.music.play(1, totaltime/1000)


    def ConvertTimeToCount(self, time):
        sortedWayPoints = self._wayPointListItems
        i = 0
        while (time <= sortedWayPoints[i][1]):
            i = i + 1
        if (i + 1 >= len(sortedWayPoints)):
            return None
        else:
            frac = ((time - sortedWayPoints[i][1]) / (float(sortedWayPoints[i + 1][1] - sortedWayPoints[i][1])))
            delta = sortedWayPoints[i + 1][0] - sortedWayPoints[i][0]
            return (math.floor(delta*(frac)))


    def InitMusicPlayer(self):
        pygame.mixer.init()

    def GetTotalCounts(self):
        return (self.ConvertMeasureToCount(self._numberMeasures + 1) - 1)

    def LoadSong(self, fileName):
        pygame.mixer.music.load(fileName)
        self.songLoaded = True

    def UnloadSong(self):
        self.songLoaded = False

    def GetMoveInfo(self, moveNumber):
        move = self._moveList[moveNumber]
        startCount = move.GetStartCount()
        endCount = startCount + move.GetLength() - 1
        info = (self.ConvertCountToMeasure(startCount), self.ConvertCountToMeasure(endCount - 1), startCount, endCount)
        return (info)

