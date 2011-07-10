import copy
import math
import Commands
import Point
import pprint

class Rank(object):
    def __init__(self, endLocation, move):
        self._endLocation = endLocation
        self._id = move.GetRankIDGen().GetID()
        self._name = None
        self._commandList = []
        self._move = move
        # TODO(astory): why isn't this called 'locked'?
        self.hold = False
        self.grabbed = False
        self.grabbedPoint = None
        self.instrument = None
        self.listOfSelectedCommandNumbers = []
        self._labelLocation = True

    
    def GetName(self):
        """Simply returns the name of the rank."""
        return self._name

    
    def SetName(self, name):
        """Sets this rank's _name field.  Also, auto-generates the command list
        (if applicable)."""
        self._name = name
        self.UpdateCommandList()
        if (self.GetFollowing() is not None):
            self.GetFollowing().UpdateCommandList()


    
    def GetID(self):
        """Returns the rank's _id."""
        return self._id

    def GetCommandList(self):
        """Returns a copy of the rank's Command List."""
        return copy.deepcopy(self._commandList)

    def SetCommandList(self, commandList):
        """Set the rank's command list"""
        self._commandList = commandList


    # The next few methods are used for grabbing a rank and moving it.
    # Necessary because although a rank's _endLocation will be changing as you
    # drag it around (so that it can be seen to move), there's no need to
    # re-generate the command list every time.
    def RankGrabbed(self):
        """Start grabbing a rank"""
        self.grabbed = True
    def RankDragged(self, dx, dy):
        """Move the rank by dx and dy and update the list of points, but don't
        update the command list"""
        i = 0
        listOfPoints = self._endLocation.GetListOfPoints()
        newPoints = []
        l = len(listOfPoints)
        while (i < l):
            newPoints.append(\
                Point.Point(listOfPoints[i].x + dx, listOfPoints[i].y + dy))
            i = i + 1
        self._endLocation.SetListOfPoints(\
            newPoints, self._endLocation.GetListOfSlopes())
    def RankDropped(self):
        """Stop grabbing a rank and update the command list for its new
        location"""
        self.grabbed = False
        self.UpdateCommandList()
        if (self.GetFollowing() is not None):
            self.GetFollowing().UpdateCommandList()

    # Similar to above.  However, unless the rank is a straight line, it will
    # need to be re-splined every timestep (again for drawing purposes.)
    # This should be ok; the spline algorithm takes time linear in the number
    # of spline points.
    # TODO(astory): storing the grabbed point in Rank seems like bad design, it
    # would be better to have the user of these functions store the point and
    # manipulate them that way; grabbed would need to be a counter
    def PointGrabbed(self, number):
        """Start grabbing a (spline) point"""
        self.grabbed = True
        self.grabbedPoint = number
    def PointDragged(self, dx, dy):
        """Move a point by dx and dy, but don't update the command list for its
        rank"""
        listOfPoints = self._endLocation.GetListOfPoints()
        listOfPoints[self.grabbedPoint] =\
            Point.Point(listOfPoints[self.grabbedPoint].x + dx,\
            listOfPoints[self.grabbedPoint].y + dy)
        self._endLocation.SetListOfPoints(\
            listOfPoints, self._endLocation.GetListOfSlopes())
    def PointDropped(self):
        """Stop dragging a point and update the command list for the new
        location"""
        self.grabbed = False
        self.grabbedPoint = None
        self.UpdateCommandList()
        if (self.GetFollowing() is not None):
            self.GetFollowing().UpdateCommandList()

    # When this is called, check to see if Rank.hold == true and if the
    # prior move has a rank of the same name.  If not, go ahead
    # and auto-generate the command list.
    def UpdateCommandList(self):
        """If this rank is in the previous move, and the rank is not locked,
        regenerate the command list.  If it is locked, update the command list
        for the new location, but don't change the commands."""
        if (self.GetPrior() is not None):
            if (self.hold):
                i = 0
                l = len(self._commandList)
                priorLocation = self.GetPrior().GetEndLocation()
                while (i < l):
                    self._commandList[i].SnapEndLocation(priorLocation)
                    priorLocation = self._commandList[i].GetEndLocation()
                    i = i + 1
                self.FixTrailingMT()
            else:
                self._commandList =\
                    self._GenerateCommandList(self.GetPrior().GetEndLocation(),\
                    self._endLocation, self._move.GetLength())
        else:
            self._commandList = []

    def FixTrailingMT(self):
        """Merge duplicate trailing mark times, and fill in space to end of move
        with a single mark time"""
        # TODO(astory): this method is written poorly.  Fix.
        # TODO(astory): make general so that we can use whatever end-move
        # command we want
        l = len(self._commandList)
        # if there are commands
        if l > 0:
            # if the last one is MT
            if (self._commandList[l - 1].GetName() == 'MT'):
                i = l - 1
                # go backwards until you run out of commands or it's not a MT
                while ((i >= 0) and (self._commandList[i].GetName() == 'MT')):
                    i = i - 1
                # if you didn't reach the beginning
                if (i >= 0):
                    # reset to the first end MT
                    i = i + 1
                    # remove all the trailing MTs
                    while (len(self._commandList) > i):
                        self._commandList.pop()
                else: # we reached the beginning
                    # slap on a mark time for the right length
                    self._commandList =\
                        [Commands.MarkTime(self._move.GetLength(),\
                        self._commandList[-1].GetEndLocation())]
        # Add a marktime to the end to fill in the gaps
        total = self.CalculateTotalCountsOfCommands()
        if (total < self._move.GetLength()):
            self._commandList.append(\
                Commands.MarkTime(\
                    self._move.GetLength() - total,\
                    self._commandList[-1].GetEndLocation()))

    def GetPrior(self):
        """Returns this rank from the previous move if it exists, else, None"""
        if (self._name is None):
            return None
        p = self._move.GetPrior()
        if (p is None):
            return None
        return (p.LookUpName(self._name))

    def GetFollowing(self):
        """Returns this rank from the next move if it exists, else, None"""
        if (self._name is None):
            return None
        p = self._move.GetFollowing()
        if (p is None):
            return None
        return (p.LookUpName(self._name))


    # Starting from the prior Rank's _endLocation, go through each Command in
    # the Command List, generating the end location of each, until you've used
    # up enough counts to hit the given count value.  Note that this may not be
    # the entire command list.  This doesn't actually make any permanent
    # changes.

    # Return None if you can't calcuclate the location (because of no
    # command list)
    def GetCalculatedLocation(self, count):
        """Returns this rank's location at count count of the move, which may
        not be the end location if count < the number of counts of commands"""
        priorRank = self.GetPrior()
        if (priorRank is None):
            return self.GetEndLocation()
        # TODO(astory): this should be condensible, do so after writing tests
        if (len(self._commandList) == 0):
            return self.GetEndLocation()
        if (count > self.CalculateTotalCountsOfCommands()):
            return self.GetEndLocation()
        curLocation = priorRank.GetEndLocation()
        i = 0
        countsLeft = count
        while (countsLeft > 0):
            curCommand = self._commandList[i]
            # TODO(astory): consider speeding up by adding whole length of
            # command if it fits in our count total
            if (countsLeft >= curCommand.GetLength()):
                curLocation = curCommand.CalcLocation(curCommand.GetLength(), curLocation)
            else:
                curLocation = curCommand.CalcLocation(countsLeft, curLocation)
            countsLeft = countsLeft - curCommand.GetLength()
            i = i + 1
        return curLocation

    def GetEndLocation(self):
        """Returns the rank's final location"""
        return copy.deepcopy(self._endLocation)

    # TODO(astory): this might be superfluous since GetCalculatedLocation never
    # returns none AFAICT
    def GetLocationAtCount(self, count):
        """Returns the rank's location at a the given count"""
        loc = self.GetCalculatedLocation(count)
        if (loc is None):
            loc = self.GetEndLocation()
        return loc


    # TODO(astory): clean
    # Used when a rank is moved around.  If self.hold == false and
    # self.grabbed == false, re-generate the command list.

    # Should never be called!
#    def SetEndLocation(self, newEndLocation):
#        pass



    # Adds the given command to the command list in the desired location
    # Number should be the number in the command list that the new command
    # will occupy.  So, if you're inserting before the fourth command,
    # number should be 3 (because it's 0-indexed.)
    def AddBasicCommand(self, commandName, number, length, name):
        """Insert a command of type commandName at index number of the command
        list, for length counts with name name, but only if the rank is locked,
        and this rank is represented in a previous command"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        if (number == 0):
            beginLocation = self.GetPrior().GetEndLocation()
        else:
            beginLocation = self._commandList[number - 1].GetEndLocation()
        # TODO(astory): this should be done with a hash defined once
        if ((commandName == "MarkTime") or (commandName == "MT")):
            newCommand = Commands.MarkTime(length, beginLocation)
        elif ((commandName == "ForwardMarch") or (commandName == "FM")):
            newCommand = Commands.ForwardMarch(length, beginLocation)
        elif ((commandName == "BackMarch") or (commandName == "BM")):
            newCommand = Commands.BackMarch(length, beginLocation)
        elif ((commandName == "RightSlide") or (commandName == "RS")):
            newCommand = Commands.RightSlide(length, beginLocation)
        elif ((commandName == "LeftSlide") or (commandName == "LS")):
            newCommand = Commands.LeftSlide(length, beginLocation)
        elif (commandName == "GTCCW0"):
            newCommand = Commands.GTCCW0(length, beginLocation)
        elif (commandName == "GTCW0"):
            newCommand = Commands.GTCW0(length, beginLocation)
        elif (commandName == "GTCCW1"):
            newCommand = Commands.GTCCW1(length, beginLocation)
        elif (commandName == "GTCW1"):
            newCommand = Commands.GTCW1(length, beginLocation)
        elif (commandName == "PWCCW"):
            newCommand = Commands.PWCCW(length, beginLocation)
        elif (commandName == "PWCW"):
            newCommand = Commands.PWCW(length, beginLocation)
        elif ((commandName == "Expand0") or (commandName == "Exp0")):
            newCommand = Commands.Expand0(length, beginLocation)
        elif ((commandName == "Expand1") or (commandName == "Exp1")):
            newCommand = Commands.Expand1(length, beginLocation)
        elif ((commandName == "Condense0") or (commandName == "Cond0")):
            newCommand = Commands.Condense0(length, beginLocation)
        elif ((commandName == "Condense1") or (commandName == "Cond1")):
            newCommand = Commands.Condense1(length, beginLocation)
        elif ((commandName == "Flatten") or (commandName == "Flat")):
            newCommand = Commands.Flatten(length, beginLocation)

        self._commandList.insert(number, newCommand)
        if (name is not None):
            newCommand.SetName(name)
        self.UpdateCommandList()

    # TODO(astory): merge into the previous with optional arguments
    def AddDTP(self, number, length, name, endLocation):
        """Add a DTP, which requires an end location as well"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        if (number == 0):
            beginLocation = self.GetPrior().GetEndLocation()
        else:
            beginLocation = self._commandList[number - 1].GetEndLocation()
        newCommand = Commands.DTP(length, beginLocation, endLocation)
        self._commandList.insert(number, newCommand)
        if (name is not None):
            newCommand.SetName(name)
        self.UpdateCommandList()

    # TODO(astory): merge into the previous with optional arguments
    def AddCurve(self, number, length, name, endLocation):
        """Add a curve, which requires an end location"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        if (number == 0):
            beginLocation = self.GetPrior().GetEndLocation()
        else:
            beginLocation = self._commandList[number - 1].GetEndLocation()
        newCommand = Commands.Curve(length, beginLocation, endLocation)
        self._commandList.insert(number, newCommand)
        if (name is not None):
            newCommand.SetName(name)
        self.UpdateCommandList()

    # TODO(astory): merge into the previous with optional arguments
    def AddFTA1(self, number, length, name, endLocation, listOfFTAPoints):
        """Add an FTA at 1"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        if (number == 0):
            beginLocation = self.GetPrior().GetEndLocation()
        else:
            beginLocation = self._commandList[number - 1].GetEndLocation()
        newCommand = Commands.FTA1(length, beginLocation, endLocation, listOfFTAPoints)
        self._commandList.insert(number, newCommand)
        if (name is not None):
            newCommand.SetName(name)
        self.UpdateCommandList()

    # TODO(astory): merge into the previous with optional arguments
    def AddFTA0(self, number, length, name, endLocation, listOfFTAPoints):
        """Add an FTA at 0"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        if (number == 0):
            beginLocation = self.GetPrior().GetEndLocation()
        else:
            beginLocation = self._commandList[number - 1].GetEndLocation()
        newCommand = Commands.FTA0(length, beginLocation, endLocation, listOfFTAPoints)
        self._commandList.insert(number, newCommand)
        if (name is not None):
            newCommand.SetName(name)
        self.UpdateCommandList()

    def MoveCommandUp(self, commandNumber):
        """Move commandNumber command up the command list"""
        if ((not self.hold) or (self.GetPrior() is None) or (commandNumber == 0)):
            return
        command = self._commandList.pop(commandNumber)
        self._commandList.insert(commandNumber - 1, command)
        self.UpdateCommandList()

    def MoveCommandDown(self, commandNumber):
        """Move commandNumber command down the command list"""
        if ((not self.hold) or (self.GetPrior() is None)\
                or (commandNumber == (len(self._commandList) - 1))):
            return
        command = self._commandList.pop(commandNumber)
        self._commandList.insert(commandNumber + 1, command)
        self.UpdateCommandList()

    def DeleteCommand(self, commandNumber):
        """Remove commandNumber command"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        self._commandList.pop(commandNumber)
        tot = 0
        i = 0
        while (i < len(self._commandList)):
            tot = tot + self._commandList[i].GetLength()
            i = i + 1
        self.UpdateCommandList()
        # TODO(astory): clean up
#        if (tot < self._move.GetLength()):
#            if (self._commandList[-1].GetName() == "MarkTime"):
#                tempLength = self._commandList[-1].GetLength()
#                self._commandList.pop(len(self._commandList) - 1)
#                self.AddBasicCommand("MarkTime", len(self._commandList), (self._move.GetLength() - tot + tempLength), "MarkTime")
#           else:
#               self.AddBasicCommand("MarkTime", len(self._commandList), (self._move.GetLength() - tot), "MarkTime")

    def ReNameCommand(self, commandNumber, newName):
        """Change the name of commandNumber command to newName"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        self._commandList[commandNumber].SetName(newName)

    def SplitCommand(self, commandNumber, count):
        """Split commandNumber command at count"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        commandToSplit = self._commandList.pop(commandNumber)
        if (commandNumber == 0):
            newCommands = commandToSplit.Split(\
                count, self.GetPrior().GetEndLocation())
        else:
            newCommands = commandToSplit.Split(\
                count, self._commandList[commandNumber - 1].GetEndLocation())
        self._commandList.insert(commandNumber, newCommands[1])
        self._commandList.insert(commandNumber, newCommands[0])

    def MergeCommands(self, firstCommandNumber):
        """Merge firstCommandNumber and the following command together"""
        if ((not self.hold) or (self.GetPrior() is None)):
            return
        if ((len(self._commandList)) > firstCommandNumber + 1):
            return
        firstCommand = self._commandList[firstCommandNumber]
        secondCommand = self._commandList[secondCommandNumber]
        newCommand = firstCommand.MergeWithFollowing(secondCommand)
        if (newCommand is not None):
            self._commandList.pop(firstCommandNumber)
            self._commandList[firstCommandNumber] = newCommand

    # TODO(astory): why do we need this?
    def GetCalculatedBeginLocation(self, frontCount):
        """Calculate the beginning location from the end location and the
        commands"""
        count = self._move.GetLength() - frontCount
        tot = 0
        i = 0
        resid = 0
        while (tot < count):
            curLength = self._commandList[i].GetLength()
            if (curLength + tot >= count):
                resid = count - tot
            else:
                i = i + 1
            tot = tot + curLength
        curLocation = self._endLocation
        curLocation = self._commandList[i].CalcBeginLocation(resid, curLocation)
        i = i - 1
        while (i >= 0):
            curLocation =\
                self._commandList[i].CalcBeginLocation(\
                    self._commandList[i].GetLength(), curLocation)
            i = i - 1
        return curLocation

    def AddSplinePoint(self, number):
        """Add a spline point to the rank after point number.  Does not add a
        spline point after the final point"""
        listOfPoints = self._endLocation.GetListOfPoints()
        if (number == len(listOfPoints) - 1):
            return
        p = self._endLocation.GetPointAtT(0.5, number)
        listOfPoints.insert(number + 1, p)
        self._endLocation.SetListOfPoints(listOfPoints, None)

    def DeleteSplinePoint(self, number):
        """Removes number point if it is not one of the last two"""
        listOfPoints = self._endLocation.GetListOfPoints()
        if (len(listOfPoints) > 2):
            listOfPoints.pop(number)
            self._endLocation.SetListOfPoints(listOfPoints, None)

    # TODO(astory): this is never used
    def DeleteAllSplinePoints(self):
        """Removes all points except the two end points"""
        listOfPoints = self._endLocation.GetListOfPoints()
        newList = (listOfPoints[0], listOfPoints[-1])
        self._endLocation.SetListOfPoints(newList, None)

    def SnapEndLocation(self):
        """Set each command's end location and the rank's end location to as
        calculated based on the command and the previous move"""
        if (self.GetPrior() is None):
            return
        self._endLocation = self.GetCalculatedLocation(self._move.GetLength())
        self.UpdateCommandList()

    # Starting from self._endLocation, work backwards through the command list.
    # Snap each command to the requisite beginning location, and snap the
    # _endLocation of the rank of the prior move as well.
    def SnapBeginLocation(self):
        """Set each command's beginning location and the rank's end location to
        as calculated based on the command and the previous move"""
        prior = self.GetPrior()
        if (self.GetPrior() is None):
            return
        prior._endLocation = self.GetCalculatedBeginLocation(0)
        prior.UpdateCommandList()

    # TODO(astory): convert to wrappers to a parameterized function
    def SetStraight(self):
        """Set the rank and all of its commands to be non-curved"""
        self._endLocation.SetCurved(False)
        i = 0
        while (i < len(self._commandList)):
            self._commandList[i].GetEndLocation().SetCurved(False)
            i = i + 1

    def SetCurved(self):
        """Set the rank and all of its commands to be curved"""
        self._endLocation.SetCurved(True)
        i = 0
        while (i < len(self._commandList)):
            self._commandList[i].GetEndLocation().SetCurved(True)
            i = i + 1

    # TODO(astory): rewrite as a list comprehension
    def CalculateCountFromCommandNumber(self, commandNumber):
        """Returns the count at which commandNumber command starts"""
        if (commandNumber == 0):
            return 0
        i = 0
        accum = 0
        while (i < commandNumber):
            accum = accum + self._commandList[i].GetLength()
            i = i + 1
        return accum

    # TODO(astory): rewrite as a list comprehension
    def CalculateTotalCountsOfCommands(self):
        """Return the sum of lengths of the commands"""
        i = 0
        accum = 0
        while (i < len(self._commandList)):
            accum = accum + self._commandList[i].GetLength()
            i = i + 1
        return accum

    # TODO(astory): break into own file?
    def _GenerateCommandList(self, beginLocation, endLocation, length):
        """Generate a list of commands to take the rank from beginLocation to
        endLocation in length counts"""
        # The algorithm:
        # First, check to see if this is a 'special case'.  If so, even if the
        # rank is curved, it can be treated as a straight line.  Otherwise,
        # flatten the rank.  The number of counts taken is equal to the length
        # of the furthest spline point from that straight line.  Then, use the
        # straight line generator to get form one straight line to another, and
        # then recurve, if nececssary.  As a final step, append a MarkTime.
        # This step may be able to be skipped, as the UpdateCommandList
        # function, the only thing calling this, should append it automatically
        # if necessary.
        if (self._IsSpecialCaseCMDGen(beginLocation, endLocation)):
            return self._GenerateCommandListStraightLine(\
                beginLocation, endLocation, length, [])[0]
        commandListSoFar = []
        beginPointList = beginLocation.GetListOfPoints()
        endPointList = endLocation.GetListOfPoints()
        if (not beginLocation.IsStraight()):
            i = 1
            lengthsBeginMax = 0
            while (i < (len(beginPointList) - 1)):
                valsBegin = self._CalcLengthsHelper(beginLocation, i)
                lengthsBeginMax = max(lengthsBeginMax, valsBegin[0])
                i = i + 1
            newCommand = Commands.Flatten(lengthsBeginMax, beginLocation)
            commandListSoFar.append(newCommand)
            length = length - newCommand.GetLength()
            beginLocation = newCommand.GetEndLocation()

        # TODO(astory): assign into tuple
        commandListSoFarTuple =\
            self._GenerateCommandListStraightLine(\
                beginLocation,\
                endLocation,\
                length,\
                commandListSoFar)
        commandListSoFar = commandListSoFarTuple[0]
        length = commandListSoFarTuple[1]
        beginLocation = commandListSoFarTuple[2]

        if (not endLocation.IsStraight()):
            i = 1
            lengthsEndMax = 0
            while (i < (len(endPointList) - 1)):
                valsEnd = self._CalcLengthsHelper(endLocation, i)
                lengthsEndMax = max(lengthsEndMax, valsEnd[0])
                i = i + 1
            newCommand = Commands.Curve(lengthsEndMax, beginLocation, endLocation)
            commandListSoFar.append(newCommand)
            length = length - newCommand.GetLength()
            beginLocation = newCommand.GetEndLocation()

        if (length > 0):
            newCommand = Commands.MarkTime(length, endLocation)
            commandListSoFar.append(newCommand)
            length = length - newCommand.GetLength()

        return commandListSoFar

    def _IsSpecialCaseCMDGen(self, beginLocation, endLocation):
        """Return true if expand, condense, GT, PW, and slides are enough to
        perform the relocation"""
        # The purpose of this method is to determine if a rank can be gotten
        # from one RankLocation to another with just Expand, Condense, GT, PW,
        # RS/LS, and FM/BM.  I find the length from each spline point to the
        # straight line connecting the first and last point.  If these lengths
        # are the same, then it is this special case and return True.
        beginPointList = beginLocation.GetListOfPoints()
        endPointList = endLocation.GetListOfPoints()
        if ((len(beginPointList) == 2)\
                or (len(endPointList) == 2)\
                or (len(beginPointList) != len(endPointList))):
            return False
        i = 1
        while (i < (len(beginPointList) - 1)):
            valsBegin = self._CalcLengthsHelper(beginLocation, i)
            valsEnd = self._CalcLengthsHelper(endLocation, i)
            if ((valsBegin[0] != valsEnd[0]) or (valsBegin[1] != valsEnd[1])):
                return False
            i = i + 1
        return True

    # Takes in a RankLocation and a number, namely the point number of which
    # you wish to learn the length of.  Assume that the RankLocation looks
    # like:
    #     .
    #    / \
    #   /   \
    #  .     \     .
    #         \   /
    #          \ /
    #           .

    # This method should calculate the following lengths:  (the added lines):

    #     .
    #    /|\
    #   / | \
    #  .  -  \  -  .
    #         \ | /
    #          \|/
    #           .

    # This helps to determine if one (possibly curved) RankLocation is a
    # translation of another, meaning you can get from one to another
    # using just Expand, Condense, GT, PW, RS/LS, FM/BM

    # TODO(astory): should be moved to a util since it doesn't use self.
    # TODO(astory): figure out what t is
    def _CalcLengthsHelper(self, location, number):
        """Calculates the length between the endpoints of the location"""
        pointList = location.GetListOfPoints()
        x0 = pointList[0].x
        y0 = pointList[0].y
        x1 = pointList[-1].x
        y1 = pointList[-1].y
        xp = pointList[number].x
        yp = pointList[number].y
        t = (((xp - x0)*(x1 - x0))\
            + ((yp - y0)*(y1 - y0)))/(((y1 - y0)*(y1 - y0))\
            + ((x1 - x0)*(x1 - x0)))
        yt = y0 + t*(y1 - y0)
        xt = x0 + t*(x1 - x0)
        pointLineLength = math.sqrt(((xp - xt)*(xp - xt))\
            + ((yp - yt)*(yp - yt)))
        return[pointLineLength, t]

    # Algorithm:
    # If you go from straight rank to straight rank, do the following:
    #       Expand/Condense to be the correct length
    #       GT/PW to be the correct orientation
    #       RS/LS
    #       FM/BM
    # Use a heuristic to figure out whether to Condense0 or Condense1,
    # Same with GT/PW.
    def _GenerateCommandListStraightLine(self, beginLocation, endLocation,\
            length, commandListSoFar):
        begin0 = beginLocation.GetListOfPoints()[0]
        begin1 = beginLocation.GetListOfPoints()[-1]
        end0 = endLocation.GetListOfPoints()[0]
        end1 = endLocation.GetListOfPoints()[-1]
        endMid = endLocation.GetMidPoint()
        beginMid = beginLocation.GetMidPoint()
        #LMD change to round
        beginLength = int(round(math.sqrt(\
            (begin1.x - begin0.x)*(begin1.x - begin0.x)\
            + (begin1.y - begin0.y)*(begin1.y - begin0.y))))
        #LMD change to round
        endLength = int(round(math.sqrt(\
            (end1.x - end0.x)*(end1.x - end0.x)\
            + (end1.y - end0.y)*(end1.y - end0.y))))
        if (beginLength != 16):
            newMid1x = (begin1.x - begin0.x)*(8/beginLength) + begin0.x
            newMid1y = (begin1.y - begin0.y)*(8/beginLength) + begin0.y
            newMid0x = (begin0.x - begin1.x)*(8/beginLength) + begin1.x
            newMid0y = (begin0.y - begin1.y)*(8/beginLength) + begin1.y
            length0 = math.sqrt((endMid.x - newMid0x)*(endMid.x - newMid0x)\
                + (endMid.y - newMid0y)*(endMid.y - newMid0y))
            length1 = math.sqrt((endMid.x - newMid1x)*(endMid.x - newMid1x)\
                + (endMid.y - newMid1y)*(endMid.y - newMid1y))
            if (beginLength > 16):
                if (length0 > length1):
                    newCommand = Commands.Condense1((beginLength - 16),\
                        beginLocation)
                else:
                    newCommand = Commands.Condense0((beginLength - 16),\
                        beginLocation)
            else:
                if (length0 > length1):
                    newCommand = Commands.Expand1((16 - beginLength),\
                        beginLocation)
                else:
                    newCommand = Commands.Expand0((16 - beginLength),\
                        beginLocation)
            commandListSoFar.append(newCommand)
            length = length - newCommand.GetLength()
            beginLocation = newCommand.GetEndLocation()
            begin0 = beginLocation.GetListOfPoints()[0]
            begin1 = beginLocation.GetListOfPoints()[-1]
            beginMid = beginLocation.GetMidPoint()
            beginLength = 16

        beginAng = math.atan2((begin1.y - begin0.y),(begin1.x - begin0.x))
        endAng = math.atan2((end1.y - end0.y),(end1.x - end0.x))
        if (beginAng != endAng):
            c = math.cos(endAng - beginAng)
            s = math.sin(endAng - beginAng)
            newMid1x = (c*(beginMid.x - begin0.x) - s*(beginMid.y - begin0.y))\
                + begin0.x
            newMid1y = (s*(beginMid.x - begin0.x) + c*(beginMid.y - begin0.y))\
                + begin0.y
            newMid0x = (c*(beginMid.x - begin1.x) - s*(beginMid.y - begin1.y))\
                + begin1.x
            newMid0y = (s*(beginMid.x - begin1.x) + c*(beginMid.y - begin1.y))\
                + begin1.y
#####################################################################LMD fix
            #angDiff is CCW angle change from beginning to end angle
            angDiff= endAng-beginAng
            if (endAng < beginAng): angDiff=angDiff+360 
            if (angDiff<180): stepsPW = angDiff*(16/math.pi)
            else: stepsPW = (360-angDiff)*(16/math.pi)
            
            length0 = math.fabs(endMid.x - newMid0x)\
                + math.fabs(endMid.y - newMid0y) + 2*stepsPW
            length1 = math.fabs(endMid.x - newMid1x)\
                + math.fabs(endMid.y - newMid1y) + 2*stepsPW
            lengthPW = math.fabs(endMid.x - beginMid.x)\
                + math.fabs(endMid.y - beginMid.y) + stepsPW

            if (angDiff<180):
                #CCW
                if (lengthPW <= length0):
                    if (lengthPW <= length1):
                        newCommand = Commands.PWCCW(stepsPW, beginLocation)
                    else:
                        newCommand = Commands.GTCCW1(2*stepsPW, beginLocation)
                else:
                    if (length0 <= length1):
                        newCommand = Commands.GTCCW0(2*stepsPW, beginLocation)
                    else:
                        newCommand = Commands.GTCCW1(2*stepsPW, beginLocation)
            else:
                #CW
                if (lengthPW <= length0):
                    if (lengthPW <= length1):
                        newCommand = Commands.PWCW(stepsPW, beginLocation)
                    else:
                        newCommand = Commands.GTCW1(2*stepsPW, beginLocation)
                else:
                    if (length0 <= length1):
                        newCommand = Commands.GTCW0(2*stepsPW, beginLocation)
                    else:
                        newCommand = Commands.GTCW1(2*stepsPW, beginLocation)
###############################################################################
            commandListSoFar.append(newCommand)
            length = length - newCommand.GetLength()
            beginLocation = newCommand.GetEndLocation()
            begin0 = beginLocation.GetListOfPoints()[0]
            begin1 = beginLocation.GetListOfPoints()[-1]
            beginMid = beginLocation.GetMidPoint()

        movePoint0 = True
        NumSteps0 = math.fabs(end0.x - begin0.x) + math.fabs(end0.y - begin0.y)
        NumSteps1 = math.fabs(end1.x - begin1.x) + math.fabs(end1.y - begin1.y)
        if (NumSteps0 > NumSteps1):
            movePoint0 = False

        if(movePoint0):
            if (end0.x > begin0.x):
                newCommand = Commands.LeftSlide(\
                    end0.x - begin0.x, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
            elif (end0.x < begin0.x):
                newCommand = Commands.RightSlide(\
                    begin0.x - end0.x, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
            if (end0.y > begin0.y):
                newCommand = Commands.BackMarch(\
                    end0.y - begin0.y, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
            elif (end0.y < begin0.y):
                newCommand = Commands.ForwardMarch(\
                    begin0.y - end0.y, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
        else:
            if (end1.x > begin1.x):
                newCommand = Commands.LeftSlide(\
                    end1.x - begin1.x, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
            elif (end1.x < begin1.x):
                newCommand = Commands.RightSlide(\
                    begin1.x - end1.x, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
            if (end1.y > begin1.y):
                newCommand = Commands.BackMarch(\
                    end1.y - begin1.y, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()
            elif (end1.y < begin1.y):
                newCommand = Commands.ForwardMarch(\
                    begin1.y - end1.y, beginLocation)
                commandListSoFar.append(newCommand)
                length = length - newCommand.GetLength()
                beginLocation = newCommand.GetEndLocation()
                begin0 = beginLocation.GetListOfPoints()[0]
                begin1 = beginLocation.GetListOfPoints()[-1]
                beginMid = beginLocation.GetMidPoint()

        if (endLength != 16):
            if (endLength < 16):
                if (movePoint0):
                    newCommand = Commands.Condense1(\
                        (16 - endLength), beginLocation)
                else:
                    newCommand = Commands.Condense0(\
                        (16 - endLength), beginLocation)
            else:
                if (movePoint0):
                    newCommand = Commands.Expand1(\
                        (endLength - 16), beginLocation)
                else:
                    newCommand = Commands.Expand0(\
                        (endLength - 16), beginLocation)
            commandListSoFar.append(newCommand)
            length = length - newCommand.GetLength()
            beginLocation = newCommand.GetEndLocation()
            begin0 = beginLocation.GetListOfPoints()[0]
            begin1 = beginLocation.GetListOfPoints()[-1]
            beginMid = beginLocation.GetMidPoint()
            beginLength = 16

        return (commandListSoFar, length, beginLocation)

    def GetLabelLocation(self):
        """Returns the location of this rank's label"""
        return self._labelLocation

    def SwitchLabelLocation(self):
        """Twiddle the location of this rank's label"""
        self._labelLocation = not self._labelLocation

    def SwitchEndpoints(self):
        """Switch the endpoints"""
        self._endLocation.SwitchEndpoints()
        self.UpdateCommandList()
        if (self.GetFollowing() is not None):
            self.GetFollowing().UpdateCommandList()
