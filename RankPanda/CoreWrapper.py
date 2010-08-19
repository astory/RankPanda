import copy
import Song
import Move
import Rank
import Commands
import RankLocation
import Point
import cPickle


class CoreWrapper(object):
    # Call when a new song is created, pass in relevavnt information.
    # title is a string
    # numberMeasures is a number
    # countsPerMeasureList is of the form [(MeasureNumber, CountsPerMeasureValue)]
    # stepsPerMeasureList is of the form [(MeasureNumber, StepsPerCountValue)]
    # Note that the two lists CANNOT be empty.
    # CountsPerMeasureList[0][0]  MUST equal 1
    # StepsPerCountList[0][0]  MUST equal 1
    def __init__(self, title, numberMeasures, CountsPerMeasureList, StepsPerCountList):
        if (numberMeasures < 1):
            raise NameError("Number of measures can't be less than 1!")
        if (len(CountsPerMeasureList) == 0):
            raise NameError("You must input the initial number of counts per measure!")
        if (CountsPerMeasureList[0][0] != 1):
            raise NameError("You must input the initial number of counts per measure!")
        self._song = Song.Song(title, numberMeasures, CountsPerMeasureList[0][1])
        i = 1
        while (i < len(CountsPerMeasureList)):
            if (CountsPerMeasureList[i][0] < 1):
                raise NameError("Measure number can't be less than 1!")
            if (CountsPerMeasureList[i][1] < 0):
                raise NameError("Counts per Measure can't be less than 0!")
            self._song.AddCountsPerMeasureChange(CountsPerMeasureList[i][0], CountsPerMeasureList[i][1])
            i = i + 1
        i = 0
        while (i < len(StepsPerCountList)):
            if (StepsPerCountList[i][0] < 1):
                raise NameError("Measure number can't be less than 1!")
            if (StepsPerCountList[i][1] < 0):
                raise NameError("Steps per Count can't be less than 0!")
            self._song.AddStepsPerCountChange(StepsPerCountList[i][0], StepsPerCountList[i][1])
            i = i + 1
        self.AddingDTPInfo = None
#        self.LoadSong('01 Star Wars Theme.mp3')
#        self.LoadSong('01 Star Wars Theme.m4a')


    # Returns the NAME of the song
    def GetSong(self):
        return self._song.title

    # Returns a list of move names and numbers associated with them
    # [(0, 'Move 0'), (1, 'Move 1'), ...]
    def GetMoves(self):
        listOfMoves = self._song.GetMoveList()
        i = 0
        moveInfo = []
        while (i < len(listOfMoves)):
            curmove = listOfMoves[i]
            moveInfo.append((curmove.GetNumber(), curmove.GetName()))
            i = i + 1
        return moveInfo

    # Returns (current move number, current move name, current length of move in counts)
    # Returns None is there is no current move
    def GetCurrentMove(self):
        if (self._song.currentMove is None):
            return None
        else:
            if (self._song.currentMove.GetNumber() == 0):
                return (0, 'Preset', 0)
            else:
                return (self._song.currentMove.GetNumber(),self._song.currentMove.GetName(),self._song.currentMove.GetLength())

    # ?
    # List of all ranks in current move
    # [(id0, name0, location0), (id1, name1, location1)]
    def GetRanks(self):
        if (self._song.currentMove is None):
            return None
        allRanks = self._song.currentMove.GetAllRanks()
        i = 0
        allRankInfo = []
        while (i < len(allRanks)):
            allRankInfo.append((allRanks[i].GetID(), allRanks[i].GetName(), allRanks[i].GetEndLocation(), allRanks[i].GetLabelLocation()))
            i = i + 1
        return allRankInfo


    # Same as above but now you input the move number.
    def GetRanksGivenMove(self, moveNumber):
        if (self._song.currentMove is None):
            return None
        allRanks = self._song.GetMoveList()[moveNumber].GetAllRanks()
        i = 0
        allRankInfo = []
        while (i < len(allRanks)):
            allRankInfo.append((allRanks[i].GetID(), allRanks[i].GetName(), allRanks[i].GetEndLocation(), allRanks[i].GetLabelLocation()))
            i = i + 1
        return allRankInfo


    def IsRankHeld(self, ID):
        if (self._song.currentMove is None):
            return None
        return self._song.currentMove.LookUpID(ID).hold

    # Returns list of currently selected ranks
    # Better to keep track of in GUI?
    # [(id0, name0, location0), (id1, name1, location1)]
    def GetSelectedRanks(self):
        if (self._song.currentMove is None):
            return None
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        allSelectedRankInfo = []
        while (i < len(allSelectedRanks)):
            allSelectedRankInfo.append((allSelectedRanks[i].GetID(), allSelectedRanks[i].GetName(), allSelectedRanks[i].GetEndLocation(), allSelectedRanks[i].GetLabelLocation()))
            i = i + 1
        return allSelectedRankInfo

    def GetAdditionalRanks(self):
        curList = []
        if (self._song.currentMove is None):
            return None
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        while (i < len(allSelectedRanks)):
            curRank = allSelectedRanks[i]
            if (len(curRank.listOfSelectedCommandNumbers) > 0):
                if (curRank.listOfSelectedCommandNumbers[0] == 0):
                    curList.append([curRank.GetID(), curRank.GetName(), curRank.GetPrior().GetEndLocation(), 'Begin', curRank.GetLabelLocation()])
                else:
                    curList.append([curRank.GetID(), curRank.GetName(), curRank.GetCommandList()[curRank.listOfSelectedCommandNumbers[0] - 1].GetEndLocation(), 'Begin', curRank.GetLabelLocation()])
                curList.append([curRank.GetID(), curRank.GetName(), curRank.GetCommandList()[curRank.listOfSelectedCommandNumbers[-1]].GetEndLocation(), 'End', curRank.GetLabelLocation()])
            i = i + 1
        return curList

    def GetCalculatedRanks(self):
        if (self._song.currentMove is None):
            return None
        allNamedRanks = self._song.currentMove.GetAllNamedRanks()
        i = 0
        allRankInfo = []
        length = self._song.currentMove.GetLength()
        while (i < len(allNamedRanks)):
            loc = allNamedRanks[i].GetCalculatedLocation(length)
            if (loc is not None):
                allRankInfo.append((allNamedRanks[i].GetID(), allNamedRanks[i].GetName(), loc, allNamedRanks[i].GetLabelLocation()))
            i = i + 1
        return allRankInfo


    def SetListOfSelectedCommandNumbers(self, commandNumberList):
        if (self._song.currentMove is None):
            return curList
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        while (i < len(allSelectedRanks)):
            curRank = allSelectedRanks[i]
            if (curRank.GetPrior() is not None):
                curRank.listOfSelectedCommandNumbers = commandNumberList
            i = i + 1


    def BeginAddingDTP(self, commandToAddBefore, length, name, isCurve = False):
        if (not (self._AllHold())):
            return None
        curList = []
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        if (commandToAddBefore is None):
            commandToAddBefore = len(allSelectedRanks[0].GetCommandList())
        while (i < len(allSelectedRanks)):
            curRank = allSelectedRanks[i]
            curRank.AddBasicCommand('MT', commandToAddBefore, length, 'temp')
            beginCount = curRank.CalculateCountFromCommandNumber(commandToAddBefore)
            curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedLocation(beginCount)), 'Begin', commandToAddBefore, length, name])
            if ((beginCount + length) > self._song.currentMove.GetLength()):
                curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetEndLocation()), 'End', commandToAddBefore, length, name])
            else:
                curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedBeginLocation(beginCount + length)), 'End', commandToAddBefore, length, name])
            curRank.DeleteCommand(commandToAddBefore)
            i = i + 1
        self.AddingDTPInfo = curList
        self.isCurve = isCurve
        return curList

#    def CommandAdded(self, ID, commandType, number, length, name, data):
#            rank.AddDTP(number, length, name, endLocation)

    def BeginAddingFTA1(self, commandToAddBefore, length, name):
        if (not(self._AllHold())):
            return None
        curList = []
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        if (commandToAddBefore is None):
            commandToAddBefore = len(allSelectedRanks[0].GetCommandList())
        while (i < len(allSelectedRanks)):
            curRank = allSelectedRanks[i]
            curRank.AddBasicCommand('MT', commandToAddBefore, length, 'temp')
            beginCount = curRank.CalculateCountFromCommandNumber(commandToAddBefore)
            curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedLocation(beginCount)), 'Begin', commandToAddBefore, length, name])
            curList.append([])
            if ((beginCount + length) > self._song.currentMove.GetLength()):
                curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetEndLocation()), 'End', commandToAddBefore, length, name])
            else:
                curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedBeginLocation(beginCount + length)), 'End', commandToAddBefore, length, name])
            curRank.DeleteCommand(commandToAddBefore)
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def BeginAddingFTA0(self, commandToAddBefore, length, name):
        if (not(self._AllHold())):
            return None
        curList = []
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        if (commandToAddBefore is None):
            commandToAddBefore = len(allSelectedRanks[0].GetCommandList())
        while (i < len(allSelectedRanks)):
            curRank = allSelectedRanks[i]
            curRank.AddBasicCommand('MT', commandToAddBefore, length, 'temp')
            beginCount = curRank.CalculateCountFromCommandNumber(commandToAddBefore)
            curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedLocation(beginCount)), 'Begin', commandToAddBefore, length, name])
            curList.append([])
            if ((beginCount + length) > self._song.currentMove.GetLength()):
                curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetEndLocation()), 'End', commandToAddBefore, length, name])
            else:
                curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedBeginLocation(beginCount + length)), 'End', commandToAddBefore, length, name])
            curRank.DeleteCommand(commandToAddBefore)
            i = i + 1
        self.AddingFTA0Info = curList
        return curList


    def AdjustDTPWhole(self, dx, dy):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            j = 0
            listOfPoints = curLoc.GetListOfPoints()
            newPoints = []
            l = len(listOfPoints)
            while (j < l):
                newPoints.append(Point.Point(listOfPoints[j].x + dx, listOfPoints[j].y + dy))
                j = j + 1
            curLoc.SetListOfPoints(newPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingDTPInfo = curList
        return curList

    def AdjustFTA1Whole(self, dx, dy):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            j = 0
            listOfPoints = curLoc.GetListOfPoints()
            newPoints = []
            l = len(listOfPoints)
            while (j < l):
                newPoints.append(Point.Point(listOfPoints[j].x + dx, listOfPoints[j].y + dy))
                j = j + 1
            curLoc.SetListOfPoints(newPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def AdjustFTA0Whole(self, dx, dy):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            j = 0
            listOfPoints = curLoc.GetListOfPoints()
            newPoints = []
            l = len(listOfPoints)
            while (j < l):
                newPoints.append(Point.Point(listOfPoints[j].x + dx, listOfPoints[j].y + dy))
                j = j + 1
            curLoc.SetListOfPoints(newPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA0Info = curList
        return curList

    def AdjustDTPPoint(self, PointNumber, dx, dy):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            listOfPoints[PointNumber] = Point.Point(listOfPoints[PointNumber].x + dx, listOfPoints[PointNumber].y + dy)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingDTPInfo = curList
        return curList

    def AdjustFTA1EndLocationPoint(self, PointNumber, dx, dy):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            listOfPoints[PointNumber] = Point.Point(listOfPoints[PointNumber].x + dx, listOfPoints[PointNumber].y + dy)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def AdjustFTA0EndLocationPoint(self, PointNumber, dx, dy):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            listOfPoints[PointNumber] = Point.Point(listOfPoints[PointNumber].x + dx, listOfPoints[PointNumber].y + dy)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA0Info = curList
        return curList

    def DTPAddingSplinePoint(self, PointNumber):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            newPoint = curLoc.GetPointAtT(0.5, PointNumber)
            listOfPoints.insert(PointNumber + 1, newPoint)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingDTPInfo = curList
        return curList

    def FTA1AddingSplinePoint(self, PointNumber):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            newPoint = curLoc.GetPointAtT(0.5, PointNumber)
            listOfPoints.insert(PointNumber + 1, newPoint)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def FTA0AddingSplinePoint(self, PointNumber):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            newPoint = curLoc.GetPointAtT(0.5, PointNumber)
            listOfPoints.insert(PointNumber + 1, newPoint)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA0Info = curList
        return curList

    def DTPDeletingSplinePoint(self, PointNumber):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            listOfPoints.pop(PointNumber)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingDTPInfo = curList
        return curList

    def FTA1DeletingSplinePoint(self, PointNumber):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            listOfPoints.pop(PointNumber)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def FTA0DeletingSplinePoint(self, PointNumber):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            listOfPoints = curLoc.GetListOfPoints()
            listOfPoints.pop(PointNumber)
            curLoc.SetListOfPoints(listOfPoints, curLoc.GetListOfSlopes())
            i = i + 1
        self.AddingFTA0Info = curList
        return curList

    def FTA1AddingWayPoint(self, x, y):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 1
            listOfPoints = curList[i]
            listOfPoints.append(Point.Point(x, y))
            i = i + 2
        self.AddingFTA1Info = curList
        return curList

    def FTA0AddingWayPoint(self, x, y):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 1
            listOfPoints = curList[i]
            listOfPoints.append(Point.Point(x, y))
            i = i + 2
        self.AddingFTA0Info = curList
        return curList

    def FTA1AdjustWayPoint(self, pointNumber, dx, dy):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 1
            listOfPoints = curList[i]
            listOfPoints[pointNumber] = Point.Point(listOfPoints[pointNumber].x, listOfPoints[pointNumber].y)
            i = i + 2
        self.AddingFTA1Info = curList
        return curList

    def FTA0AdjustWayPoint(self, pointNumber, dx, dy):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 1
            listOfPoints = curList[i]
            listOfPoints[pointNumber] = Point.Point(listOfPoints[pointNumber].x, listOfPoints[pointNumber].y)
            i = i + 2
        self.AddingFTA0Info = curList
        return curList

    def FTA1DeleteWayPoint(self, pointNumber):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 1
            listOfPoints = curList[i]
            listOfPoints.pop(pointNumber)
            i = i + 2
        self.AddingFTA1Info = curList
        return curList

    def FTA0DeleteWayPoint(self, pointNumber):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 1
            listOfPoints = curList[i]
            listOfPoints.pop(pointNumber)
            i = i + 2
        self.AddingFTA0Info = curList
        return curList

    def DTPSetCurved(self):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            curLoc.SetCurved(True)
            i = i + 1
        self.AddingDTPInfo = curList
        return curList

    def FTA1SetCurved(self):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            curLoc.SetCurved(True)
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def FTA0SetCurved(self):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            curLoc.SetCurved(True)
            i = i + 1
        self.AddingFTA0Info = curList
        return curList

    def DTPSetStraight(self):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            curLoc.SetCurved(False)
            i = i + 1
        self.AddingDTPInfo = curList
        return curList

    def FTA1SetStraight(self):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            curLoc.SetCurved(False)
            i = i + 1
        self.AddingFTA1Info = curList
        return curList

    def FTA0SetStraight(self):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            curLoc.SetCurved(False)
            i = i + 1
        self.AddingFTA0Info = curList
        return curList

    def FinalizeAddingDTP(self):
        i = 0
        curList = self.AddingDTPInfo
        while (i < len(curList)):
            i = i + 1
            curLoc = curList[i][2]
            curID = curList[i][0]
            if (self.isCurve):
                self._song.currentMove.LookUpID(curID).AddCurve(curList[i][4], curList[i][5], curList[i][6], curLoc)
            else:
                self._song.currentMove.LookUpID(curID).AddDTP(curList[i][4], curList[i][5], curList[i][6], curLoc)
            i = i + 1
        curList = []

    def FinalizeAddingFTA1(self):
        i = 0
        curList = self.AddingFTA1Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            curID = curList[i][0]
            self._song.currentMove.LookUpID(curID).AddFTA1(curList[i][4], curList[i][5], curList[i][6], curLoc, curList[i - 1])
            i = i + 1
        curList = []

    def FinalizeAddingFTA0(self):
        i = 0
        curList = self.AddingFTA0Info
        while (i < len(curList)):
            i = i + 2
            curLoc = curList[i][2]
            curID = curList[i][0]
            self._song.currentMove.LookUpID(curID).AddFTA0(curList[i][4], curList[i][5], curList[i][6], curLoc, curList[i - 1])
            i = i + 1
        curList = []

#    def AddDTP(self, number, length, name, endLocation):

#    curList.append([curRank.GetID(), curRank.GetName(), copy.deepcopy(curRank.GetCalculatedBeginLocation(beginCount + length)), 'End', commandToAddBefore, length, name])



    def MakeSelectedRanksStraight(self):
        if (self._song.currentMove is None):
            return
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        for r in allSelectedRanks:
            r.SetStraight()


    def MakeSelectedRanksCurved(self):
        if (self._song.currentMove is None):
            return
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        for r in allSelectedRanks:
            r.SetCurved()


#    def AddComplexCommandInfo(self, commandToAddBefore):
#        if (self._song.currentMove is None):
#            return curList
#        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
#        if (commandToAddBefore is not None):




    # Returns list of Commands for currently-selected rank
    # [('CommandName', length)]
    def GetCommands(self):
        if (self._song.currentMove is None):
            return None
        listOfCommandLists = []
        allSelectedRanks = self._song.currentMove.GetSelectedRanks()
        i = 0
        while (i < len(allSelectedRanks)):
            listOfCommandLists.append([])
            j = 0
            cmdLst = allSelectedRanks[i].GetCommandList()
            while(j < len(cmdLst)):
                listOfCommandLists[i].append(((cmdLst[j].GetName()),(cmdLst[j].GetLength())))
                j = j + 1
            i = i + 1
        i = 0
        while(i < len(listOfCommandLists)):
            if (len(listOfCommandLists[i]) != len(listOfCommandLists[0])):
                return []
            j = 0
            while (j < len(listOfCommandLists[i])):
                if (listOfCommandLists[i][j] != listOfCommandLists[0][j]):
                    return []
                j = j + 1
            i = i + 1
        if (len(listOfCommandLists) > 0):
            return listOfCommandLists[0]
        else:
            return []



    # ?  Who keeps track?
    def GetSelectedCommands(self):
        if (self._song.currentMove is None):
            return None
        return self._song.currentMove.GetListOfActiveCommands()

    def MoveAdded(self, beginningMeasure, endMeasure, name):
        if ((beginningMeasure < 1) or (endMeasure < beginningMeasure)):
            return None
        newMove = self._song.AddMove(beginningMeasure, endMeasure)
        if (name is not None):
            self._song.currentMove.SetName(name)
        return newMove.GetNumber()


    def MoveDeleted(self, moveNumber):
        if (self._song.currentMove is None):
            return None
        self._song.DeleteMove(moveNumber)

    # How to pass in how it's edited?  Lots of functions, I'm guessing...

    # code = 'Split', 'Merge', 'Shift'
    # details = [MoveToSplit#, countAtWhichToSplit] | [FirstOfTwoMovesToMerge#] | [FirstMoveToShift#,numberOfCounts]
    # number of counts should be positive for shifting later, negative for shifting earlier.
    def MoveEdited(self, code, details):
        if (self._song.currentMove is None):
            return None
        if (code == 'Split'):
            self._song.SplitMove(details[0], details[1])
        if (code == 'Merge'):
            self._song.MergeMoves(details[0])
        if (code == 'Shift'):
            self._song.ShiftMoveBlock(details[0], details[1])


    # Changes selected Move
    def ChangeMove(self, number):
        self._song.SetCurrentMove(number)
#        self._song.currentMove = (self._song.GetMoveList())[number]

    # Pass in a list of Points (both), in order.
    def RankDrawn(self, listOfPoints):
        if (self._song.currentMove is None):
            return None
        if (not RankLocation.RankLocation.IsListOfPointsLengthZero(listOfPoints)):  #((((listOfPoints[1].x - listOfPoints[0].x)*(listOfPoints[1].x - listOfPoints[0].x)) + ((listOfPoints[1].y - listOfPoints[0].y)*(listOfPoints[1].y - listOfPoints[0].y))) > 0):
            r = self._song.currentMove.CreateRank(RankLocation.RankLocation(listOfPoints), None)
        else:
            return None

    # Pass in the ID of the rank to be deleted (in the current move)
    def RankDeleted(self, ID):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.DeleteRank(ID)

    # Call when a rank is grabbed to be dragged.
    # Assumes that every rank in the list of active ranks has been grabbed!
    def RanksGrabbed(self):
        if (self._song.currentMove is None):
            return None
        i = 0
        selectedRanks = self._song.currentMove.GetSelectedRanks()
        while (i < len(selectedRanks)):
            selectedRanks[i].RankGrabbed()
            i = i + 1

    # Call whenever a rank is dragged.
    # dx and dy should be the length that the ranks have been dragged since
    # the last time RanksDragged() was called.
    def RanksDragged(self, dx, dy):
        if (self._song.currentMove is None):
            return None
        i = 0
        selectedRanks = self._song.currentMove.GetSelectedRanks()
        while (i < len(selectedRanks)):
            selectedRanks[i].RankDragged(dx, dy)
            i = i + 1

    # Call when the ranks have been dropped (when the user lifts the left
    # mouse button)
    def RanksDropped(self):
        if (self._song.currentMove is None):
            return None
        i = 0
        selectedRanks = self._song.currentMove.GetSelectedRanks()
        while (i < len(selectedRanks)):
            selectedRanks[i].RankDropped()
            i = i + 1


    def PointGrabbed(self, rankID, number):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(rankID).PointGrabbed(number)

    # Same deal as RanksDragged()
    def PointDragged(self, rankID, number, dx, dy):
        if (self._song.currentMove is None):
            return None
        pointList = copy.deepcopy(self._song.currentMove.LookUpID(rankID).GetEndLocation().GetListOfPoints())
        pointList[number] = Point.Point(pointList[number].x + dx, pointList[number].y + dy)
        if (not RankLocation.RankLocation.IsListOfPointsLengthZero(pointList)):
            self._song.currentMove.LookUpID(rankID).PointDragged(dx, dy)
        else:
            self.RankDeleted(rankID)


    def PointDropped(self, rankID, number):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(rankID).PointDropped()


    # Pass in the ID of the rank at which you're adding the spline point, and
    # the number of the point after which you're adding the new point.
    # Thus, for example, if the rank is straight, this should always
    # be 0.
    # Note that the end points are included in this list, so endpoint0 has
    # number 0, and endpoint 1 has number len(listofpoints) - 1.
    def RankAddSpline(self, rankID, number):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(rankID).AddSplinePoint(number)

    # Pass in the ID of the rank and the number of the spline point to delete.

    def RankDeleteSpline(self, rankID, number):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(rankID).DeleteSplinePoint(number)

    # Pass in the ID of the rank to name, and its new name.
    def NameRank(self, name):
        if (self._song.currentMove is None):
            return None
        if ((len(self._song.currentMove.GetSelectedRanks())) == 1):
            self._song.currentMove.NameRank(self._song.currentMove.GetSelectedRanks()[0].GetID(), name)

    # Pass in the ID of the rank to be locked.
    def RankLocked(self, ID):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(ID).hold = True
        self._song.currentMove.LookUpID(ID).UpdateCommandList()

    def RankUnlocked(self, ID):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(ID).hold = False
        self._song.currentMove.LookUpID(ID).UpdateCommandList()

    # ID is the ID of the rank.
    # add is a boolean.  Is if's true, the rank clicked should be added to the
    # list of active ranks.  If it's false, the rank clicked should become
    # the list of active ranks, by itself.
    def RankClicked(self, ID, add):
        if (self._song.currentMove is None):
            return None
        rank = self._song.currentMove.LookUpID(ID)
        curList = self._song.currentMove.GetSelectedRanks()
        if (add):
            if (not (rank in curList)):
                curList.append(rank)
                self._song.currentMove.SetSelectedRanks(curList)
        else:
            self._song.currentMove.SetSelectedRanks([rank])

    def FieldClicked(self):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.SetSelectedRanks([])


    # This will add the command to each rank in the list of selected ranks.

    # ID is the ID of the rank to add the command to.

    # commandType is a string with the name of the command in it.
    # this must be properly formatted.

    # number is the number that the command should have once it's been added
    # 0 - indexed.

    # length is the number of counts of the command.

    # name will be None unless the command has a different name.

    # data will be None unless the command is a DTP or an FTA.
    # If it's a DTP, then data should contain an ordered list of the points
    # defining the rank's ending location (beginning location will be the
    # end location of the prior command).  This list must be of length at least
    # 2 b/c a rank's gotta have endpoints.

    # If it's an FTA, data should be TWO lists.  (PointsForEndLocation,
    # Points of PathInOrder)

    # Options of strings for commandType:
    # "MarkTime", "ForwardMarch", "BackMarch", "RightSlide", "LeftSlide",
    # "GTCCW0", "GTCCW1", "GTCW0", "GTCW1", "PWCW", "PWCCW",
    # "Expand0", "Expand1", "Condense0", "Condense1", "DTP", "FTA1", "FTA0"
    def CommandAdded(self, ID, commandType, number, length, name, data):
        if (self._song.currentMove is None):
            return None
        rank = self._song.currentMove.LookUpID(ID)
        if (commandType == 'DTP'):
            endLocation = RankLocation.RankLocation(data)
            rank.AddDTP(number, length, name, endLocation)
        else:
            rank.AddBasicCommand(commandType, number, length, name)


    def CommandDeleted(self, ID, commandNumber):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(ID).DeleteCommand(commandNumber)

    # all you can do is rename the command, I think
    def CommandEdited(self, ID, commandNumber, newName):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(ID).ReNameCommand(commandNumber, newName)

    # up is true if the command has been moved up, false if moved down.
    def CommandRearranged(self, ID, commandNumber, up):
        if (self._song.currentMove is None):
            return None
        if (up):
            self._song.currentMove.LookUpID(ID).MoveCommandUp(commandNumber)
        else:
            self._song.currentMove.LookUpID(ID).MoveCommandDown(commandNumber)

    def CommandSplit(self, ID, commandNumber, count):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(ID).SplitCommand(commandNumber, count)

    def CommandMerge(self, ID, firstCommandNumber):
        if (self._song.currentMove is None):
            return None
        self._song.currentMove.LookUpID(ID).MergeCommands(firstCommandNumber)

    def DisplayStatusAtCount(self, count):
        return self._song.GetRankLocationsAtCount(count + self._song.GetCurrentMove().GetStartCount())

    def ImportRankLocation(self, source, recieve):
        if (self._song.currentMove is None):
            return
        self._song.ImportRanks(source, recieve)


    def _AllHold(self):
        if (self._song.currentMove is None):
            return False
        i = 0
        listOfSelectedRanks = self._song.currentMove.GetSelectedRanks()
        while (i < len(listOfSelectedRanks)):
            if (not (listOfSelectedRanks[i].hold)):
                return False
            i = i + 1
        return True


    def GetSlopeAtPoint(self, location, pointNumber):
        lengths = location.GetLengths()
        i = 0
        tot = 0
        lengthNeeded = 2
        while (i < len(lengths)):
            if (i == pointNumber):
                lengthNeeded = tot
            tot = tot + lengths[i]
            i = i + 1
        lengthfrac = lengthNeeded/ float(tot)
        info = location.GetInformationAtLengthFraction(lengthfrac)
        return info[1]

    def Save(self, fileName):
        try:
            outFile = open(fileName, 'wb')
            cPickle.dump(self._song, outFile, -1)
            outFile.close()
            return 0
        except:
            return -1


    def Load(self, fileName):
        try:
            inFile = open(fileName, 'rb')
            self._song = cPickle.load(inFile)
            inFile.close()
            self._song.InitMusicPlayer()
            return 0
        except:
            return -1


    def AddWayPoint(self, measureNumber, timeInMilliseconds):
        self._song.AddWayPoint(measureNumber, timeInMilliseconds)

    def RemoveWayPoint(self, measureNumber):
        self._song.RemoveWayPoint(measureNumber)

    def SnapEndLocations(self):
        activeRankList = self._song.currentMove.GetSelectedRanks()
        i = 0
        while (i < len(activeRankList)):
            activeRankList[i].SnapEndLocation()
            i = i + 1

    def SnapBeginLocations(self):
        activeRankList = self._song.currentMove.GetSelectedRanks()
        i = 0
        while (i < len(activeRankList)):
            activeRankList[i].SnapBeginLocation()
            i = i + 1

    def AnimationBegin(self, count):
        return self._song.AnimationBegin(count)

    def AnimationStep(self):
        return self._song.AnimationStep()

    def AnimationStop(self):
        return self._song.AnimationStop()

    #Lauren change
    #returns a list of strings each of which has a rank's full song command list
    def GetRankStrings(self):
        self.ChangeMove(0)
        if(self._song.currentMove is None):
            return None
        allNamedRanks = self._song.currentMove.GetAllNamedRanks()
        i=0
        rankStrings=[]
        while(i<len(allNamedRanks)):
            strAcc=allNamedRanks[i].GetName().strip()+" ("+ self.GetSong() +"): "#change remove comma
            j=1
            currentRank=allNamedRanks[i].GetFollowing()
            while(currentRank is not None):
                self.ChangeMove(j)
                strAcc="    "+strAcc+self.GetCurrentMove()[1]+"-, "
                commList=currentRank.GetCommandList()
                k=0
                while(k<len(commList)):
                    strAcc=strAcc + commList[k].GetName() + " " + str(int(commList[k].GetLength())) + ", "
                    k=k+1
                currentRank=currentRank.GetFollowing()
                j=j+1
            rankStrings.append(strAcc)
            i=i+1

        return rankStrings
    
    #returns a list of strings for the current move each of which displays rank(s) and commands
    def GetCommandStrings(self):
        if (self._song.currentMove is None):
            return None
        allNamedRanks = self._song.currentMove.GetAllNamedRanks()#(id, name, location)
        i = 0
        commandStrings = []

        written=[]
        names=[]
        a=0
        while(a<len(allNamedRanks)):
            written.append(False)
            a=a+1

        while (i < len(allNamedRanks)):
            if(not written[i]):
                cmdLst = allNamedRanks[i].GetCommandList()
                rankNames=allNamedRanks[i].GetName()
                written[i]=True
                k=0
                while (k < len(allNamedRanks)):
                    same=True
                    if (len(cmdLst) != len(allNamedRanks[k].GetCommandList())):
                        same = False
                    else:
                        j = 0
                        while (j < len(cmdLst)):
                            if (cmdLst[j].GetName()!= allNamedRanks[k].GetCommandList()[j].GetName()):
                                same = False
                            if (cmdLst[j].GetLength()!= allNamedRanks[k].GetCommandList()[j].GetLength()):
                                same = False
                            j = j + 1

                    if ((not written[k]) and  same):
                        rankNames=rankNames + "," + allNamedRanks[k].GetName()
                        written[k]=True
                    k=k+1
                strAcc = rankNames +": "
                j=0
                while(j<len(cmdLst)):
                    counts = str(int(round(cmdLst[j].GetLength())))
                    if (j == len(cmdLst)-1):
                        strAcc= strAcc + cmdLst[j].GetName() + " " + counts
                    else:
                        strAcc= strAcc + cmdLst[j].GetName() + " " + counts + ", "
                    j=j+1
                if(cmdLst !=  []):
                    commandStrings.append(strAcc)
            i = i + 1
        return commandStrings


    def GetMoveText(self):
        return self._song.GetCurrentMove().GetMoveText()

    def SetMoveText(self, moveText):
        self._song.GetCurrentMove().SetMoveText(moveText)

    def GetMoveTextOverwrite(self):
        return self._song.GetCurrentMove().GetMoveTextOverwrite()

    def SetMoveTextOverwrite(self, moveTextOverwrite):
        self._song.GetCurrentMove().SetMoveTextOverwrite(moveTextOverwrite)

    def SwitchLabelLocations(self):
        ranks = self._song.GetCurrentMove().GetSelectedRanks()
        i = 0
        while (i < len(ranks)):
            ranks[i].SwitchLabelLocation()
            i = i + 1


    # Returns a possibly empty [loc1, loc2, ...]
    def DisplayRanks(self):
#        loca = RankLocation.RankLocation([Point.Point(40, 24), Point.Point(56, 24)])
#        locb = RankLocation.RankLocation([Point.Point(72, 24), Point.Point(88, 24)])
#        temp = Commands.FTA1(48, loca, locb, [])
#        return [temp.CalcLocation(48, loca)]
        LoadSong('01 Star Wars Theme.m4a')



#        loc1 = RankLocation.RankLocation([Point.Point(40, 24), Point.Point(56, 24)])
#        loc2 = RankLocation.RankLocation([Point.Point(88, 56), Point.Point(88, 72)])
#        temp = Commands.FTA0(48, loc2, loc1, [])
#        temp2 = Commands.DTP(48, loc1, loc2)
#        newloc1 = copy.deepcopy(loc1)
#        newloc2 = copy.deepcopy(loc2)
#        return [temp.b(), temp.e(), temp.t()]
#        return [temp.t()]
#        return [temp.CalcLocation(10, newloc2)]
        return []


    def LoadSong(self, fileName):
        try:
            self._song.LoadSong(fileName)
            return 0
        except:
            self._song.LoadSong(fileName)
            return -1

    def GetMoveInfo(self, moveNumber):
        return self._song.GetMoveInfo(moveNumber)


    def SetNumberMeasures(self, numberMeasures):
        self._song.SetNumberMeasures(numberMeasures)

    def GetNumberMeasures(self):
        return self._song.GetNumberMeasures()

    def GetTotalCounts(self):
        return self._song.GetTotalCounts()


    # Return a tuple (countsPerMeasureList, stepsPerCountList)
    # countsPerMeasureList is of the form [(MeasureNumber, CountsPerMeasureValue)]
    # stepsPerMeasureList is of the form [(MeasureNumber, StepsPerCountValue)]
    def GetLists(self):
        countsPerMeasureItems = self._song.GetCountsPerMeasureIndex().items()
        stepsPerMeasureItems = self._song.GetStepsPerCountIndex().items()
        curList1 = []
        i = 0
        while (i < len(countsPerMeasureItems)):
            curList1.append(countsPerMeasureItems[i][0], countsPerMeasureItems[i][1])
            i = i + 1
        curList2 = []
        i = 0
        while (i < len(stepsPerCountItems)):
            curList2.append(stepsPerCountIndex[i][0], stepsPerCountIndex[i][1])
            i = i + 1
        return (curList1, curList2)


    # returns a list of [(countInSong, timeInMilliseconds)]
    def GetListOfWayPoints(self):
        return self._song.GetWayPointList()

    # Change the basic info for a song.  Pass in the same thing you would for making a new song.  Should retain all the old move info, etc.
    def EditSongInfo(self, newTitle, newNumberMeasures, newCountsPerMeasureList, newStepsPerCountList):
        if (numberMeasures < 1):
            raise NameError("Number of measures can't be less than 1!")
        if (len(CountsPerMeasureList) == 0):
            raise NameError("You must input the initial number of counts per measure!")
        if (CountsPerMeasureList[0][0] != 1):
            raise NameError("You must input the initial number of counts per measure!")
        self._song.SetTitle(newTitle)
        self._song.SetNumberMeasures(newNumberMeasures)
        self._song.ResetCountsPerMeasure(newCountsPerMeasureList[0][1])
        self._song.ResetStepsPerCount()
        i = 1
        while (i < len(CountsPerMeasureList)):
            if (CountsPerMeasureList[i][0] < 1):
                raise NameError("Measure number can't be less than 1!")
            if (CountsPerMeasureList[i][1] < 0):
                raise NameError("Counts per Measure can't be less than 0!")
            self._song.AddCountsPerMeasureChange(newCountsPerMeasureList[i][0], newCountsPerMeasureList[i][1])
            i = i + 1
        i = 0
        while (i < len(StepsPerCountList)):
            if (StepsPerCountList[i][0] < 1):
                raise NameError("Measure number can't be less than 1!")
            if (StepsPerCountList[i][1] < 0):
                raise NameError("Steps per Count can't be less than 0!")
            self._song.AddStepsPerCountChange(newStepsPerCountList[i][0], newStepsPerCountList[i][1])
            i = i + 1

    # Switch the endpoints of all currently-selected ranks
    def SwitchEndpoints(self):
        if (self._song.currentMove is None):
            return

        for r in self._song.currentMove.GetSelectedRanks():
            r.SwitchEndpoints()
