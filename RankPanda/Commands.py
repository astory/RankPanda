import Point
import RankLocation
import math
import copy

class Command(object):

    # Overwrite this in each Command, changing the self._name field.
    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'Command'


    # Given the beginning location, calculates the location that the
    # rank should be in after count counts.  Uses information such as
    # self._delta and the command type, but does NOT use
    # self.endLocation.

    # Be sure to overwrite this in each Command!
    def CalcLocation(self, count, beginLocation):
        return beginLocation

    # Splits the command in two, at the specified count.  Changes this command
    # to be the appropriate length, and returns this command as well as the
    # new one.

    # Be sure to overwrite this in each Command!
    def Split(self, count, beginLocation):
        pass

    # Returns the current value of the self._name field.
    def GetName(self):
        return self._name

    # Sets the value of the self._name field.
    def SetName(self, name):
        self._name = name

    # Returns the number of counts this command spans.  If you want to change
    # this value, make a new command instead.
    def GetLength(self):
        return round(self._length)

    # Simple getter, in case the beginning location isn't readily available.
    def GetEndLocation(self):
        return self._endLocation

    def SnapEndLocation(self, newBeginLocation):
        self._endLocation = self.CalcLocation(self.GetLength(), newBeginLocation)

    # From the ending location, calculate the beginning location.  Will require
    # basically the same implementation as CalcLocation(), but in reverse.
    # count should be the location in the whole command you want it to be
    # returned.  So, pass in 0 to run the whole command.

    # Be sure to overwrite this in each Command!
    def CalcBeginLocation(self, count, endLocation):
        return None

    # Checks following to see if it's a command of the same name.  If so,
    # return the merged commands.

    def MergeWithFollowing(self, following):
        if ((following._name == self._name) and (isinstance(following, self))):
            self._length = self._length + following._length
            self._endLocation = following._endLocation
            return self
        else:
            return None


class MarkTime(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'MT'

    def CalcLocation(self, count, beginLocation):
        return beginLocation.Clone()

    def Split(self, count, beginLocation):
        newCommand = MarkTime((self._length - count), beginLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        return self._endLocation


class ForwardMarch(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'FM'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        while (i < l):
            p = Point.Point(oldList[i].x, oldList[i].y - count)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = ForwardMarch((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)


    def CalcBeginLocation(self, count, endLocation):
        temp = BackMarch(self._length - count, endLocation)
        return temp.GetEndLocation()


class BackMarch(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'BM'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        while (i < l):
            p = Point.Point(oldList[i].x, oldList[i].y + count)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = BackMarch((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)


    def CalcBeginLocation(self, count, endLocation):
        temp = ForwardMarch(self._length - count, endLocation)
        return temp.GetEndLocation()


class LeftSlide(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'LS'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        while (i < l):
            p = Point.Point(oldList[i].x + count, oldList[i].y)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = LeftSlide((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)


    def CalcBeginLocation(self, count, endLocation):
        temp = RightSlide(self._length - count, endLocation)
        return temp.GetEndLocation()



class RightSlide(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'RS'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        while (i < l):
            p = Point.Point(oldList[i].x - count, oldList[i].y)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = RightSlide((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)


    def CalcBeginLocation(self, count, endLocation):
        temp = LeftSlide(self._length - count, endLocation)
        return temp.GetEndLocation()


class GTCCW1(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'GTCCW.'

    def CalcLocation(self, count, beginLocation):
        ang = (math.pi/32) * count
        s = math.sin(ang)
        c = math.cos(ang)
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 1
        newList = []
        point0 = oldList[0].Clone()
        newList.append(point0)
        while (i < l):

            newix = round((c*(oldList[i].x - point0.x))
                      + (-1*s*(oldList[i].y - point0.y)
                      + point0.x))
            newiy = round((s*(oldList[i].x - point0.x))
                      + (c*(oldList[i].y - point0.y)
                      + point0.y))
            p = Point.Point(newix, newiy)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = GTCCW1((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)


    def CalcBeginLocation(self, count, endLocation):
        temp = GTCW1(self._length - count, endLocation)
        return temp.GetEndLocation()


class GTCW1(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'GTCW.'

    def CalcLocation(self, count, beginLocation):
        ang = (math.pi/32) * count
        s = math.sin(ang)
        c = math.cos(ang)
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 1
        newList = []
        point0 = oldList[0].Clone()
        newList.append(point0)
        while (i < l):
            newix = round((c*(oldList[i].x - point0.x))
                      + (s*(oldList[i].y - point0.y)
                      + point0.x))
            newiy = round((-1*s*(oldList[i].x - point0.x))
                      + (c*(oldList[i].y - point0.y)
                      + point0.y))
            p = Point.Point(newix, newiy)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = GTCW1((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)


    def CalcBeginLocation(self, count, endLocation):
        temp = GTCCW1(self._length - count, endLocation)
        return temp.GetEndLocation()


class GTCCW0(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'GTCCW>'

    def CalcLocation(self, count, beginLocation):
        ang = (math.pi/32) * count
        s = math.sin(ang)
        c = math.cos(ang)
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        point1 = oldList[l - 1].Clone()
        while (i < (l - 1)):
            newix = round((c*(oldList[i].x - point1.x))
                  + (-1*s*(oldList[i].y - point1.y)
                  + point1.x))
            newiy = round((s*(oldList[i].x - point1.x))
                  + (c*(oldList[i].y - point1.y)
                  + point1.y))
            p = Point.Point(newix, newiy)
            newList.append(p)
            i = i + 1
        newList.append(point1)
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = GTCCW0((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = GTCW0(self._length - count, endLocation)
        return temp.GetEndLocation()


class GTCW0(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'GTCW>'

    def CalcLocation(self, count, beginLocation):
        ang = (math.pi/32) * count
        s = math.sin(ang)
        c = math.cos(ang)
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        point1 = oldList[l - 1].Clone()
        while (i < (l - 1)):
            newix = round((c*(oldList[i].x - point1.x))
                  + (s*(oldList[i].y - point1.y)
                  + point1.x))
            newiy = round((-1*s*(oldList[i].x - point1.x))
                  + (c*(oldList[i].y - point1.y)
                  + point1.y))
            p = Point.Point(newix, newiy)
            newList.append(p)
            i = i + 1
        newList.append(point1)
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = GTCW0((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = GTCCW0(self._length - count, endLocation)
        return temp.GetEndLocation()




class PWCCW(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'PWCCW'

    def CalcLocation(self, count, beginLocation):
        ang = (math.pi/16) * count
        s = math.sin(ang)
        c = math.cos(ang)
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        pivot = beginLocation.GetMidPoint()
        while (i < l):
            newix = round((c*(oldList[i].x - pivot.x))
                  + (-1*s*(oldList[i].y - pivot.y)
                  + pivot.x))
            newiy = round((s*(oldList[i].x - pivot.x))
                  + (c*(oldList[i].y - pivot.y)
                  + pivot.y))
            p = Point.Point(newix, newiy)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = PWCCW((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = PWCW(self._length - count, endLocation)
        return temp.GetEndLocation()



class PWCW(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'PWCW'

    def CalcLocation(self, count, beginLocation):
        ang = (math.pi/16) * count
        s = math.sin(ang)
        c = math.cos(ang)
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 0
        newList = []
        pivot = beginLocation.GetMidPoint()
        while (i < l):
            newix = round((c*(oldList[i].x - pivot.x))
                  + (s*(oldList[i].y - pivot.y)
                  + pivot.x))
            newiy = round((-1*s*(oldList[i].x - pivot.x))
                  + (c*(oldList[i].y - pivot.y)
                  + pivot.y))
            p = Point.Point(newix, newiy)
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = PWCW((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = PWCCW(self._length - count, endLocation)
        return temp.GetEndLocation()



class Expand1(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'Expand.'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 1
        newList = []
        p0 = oldList[0].Clone()
        p1 = oldList[l - 1].Clone()
        x1minusx0 = p1.x - p0.x
        y1minusy0 = p1.y - p0.y
        denominator = (x1minusx0 * x1minusx0) + (y1minusy0 * y1minusy0)
        deltaxtot = count * math.cos(math.atan2((y1minusy0),(x1minusx0)))
        deltaytot = count * math.sin(math.atan2((y1minusy0),(x1minusx0)))
        newList.append(p0.Clone())
        while (i < l):
            pToMove = oldList[i].Clone()
            t = (((pToMove.y - p0.y) * y1minusy0) + ((pToMove.x - p0.x) * x1minusx0))/denominator
            p = Point.Point(round(pToMove.x + (deltaxtot * t)), round(pToMove.y + (deltaytot * t)))
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = Expand1((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = Condense1(self._length - count, endLocation)
        return temp.GetEndLocation()



class Expand0(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'Expand>'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = l - 2
        newList = []
        p0 = oldList[l - 1].Clone()
        p1 = oldList[0].Clone()
        x1minusx0 = p1.x - p0.x
        y1minusy0 = p1.y - p0.y
        denominator = (x1minusx0 * x1minusx0) + (y1minusy0 * y1minusy0)
        deltaxtot = count * math.cos(math.atan2((y1minusy0),(x1minusx0)))
        deltaytot = count * math.sin(math.atan2((y1minusy0),(x1minusx0)))
        newList.append(p0.Clone())
        while (i >= 0):
            pToMove = oldList[i].Clone()
            t = (((pToMove.y - p0.y) * y1minusy0) + ((pToMove.x - p0.x) * x1minusx0))/denominator
            p = Point.Point(round(pToMove.x + (deltaxtot * t)), round(pToMove.y + (deltaytot * t)))
            newList.append(p)
            i = i - 1
        newList.reverse()
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = Expand0((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = Condense0(self._length - count, endLocation)
        return temp.GetEndLocation()




class Condense0(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'Condense>'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = l - 2
        newList = []
        p0 = oldList[l - 1].Clone()
        p1 = oldList[0].Clone()
        x1minusx0 = p1.x - p0.x
        y1minusy0 = p1.y - p0.y
        denominator = (x1minusx0 * x1minusx0) + (y1minusy0 * y1minusy0)
        deltaxtot = -1*count * math.cos(math.atan2((y1minusy0),(x1minusx0)))
        deltaytot = -1*count * math.sin(math.atan2((y1minusy0),(x1minusx0)))
        newList.append(p0.Clone())
        while (i >= 0):
            pToMove = oldList[i].Clone()
            t = (((pToMove.y - p0.y) * y1minusy0) + ((pToMove.x - p0.x) * x1minusx0))/denominator
            p = Point.Point(round(pToMove.x + (deltaxtot * t)), round(pToMove.y + (deltaytot * t)))
            newList.append(p)
            i = i - 1
        newList.reverse()
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = Condense0((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = Expand0(self._length - count, endLocation)
        return temp.GetEndLocation()



class Condense1(Command):

    def __init__(self, length, beginLocation):
        self._length = length
        self._endLocation = self.CalcLocation(length, beginLocation)
        self._name = 'Condense.'

    def CalcLocation(self, count, beginLocation):
        oldList = beginLocation.GetListOfPoints()
        l = len(oldList)
        i = 1
        newList = []
        p0 = oldList[0].Clone()
        p1 = oldList[l - 1].Clone()
        x1minusx0 = p1.x - p0.x
        y1minusy0 = p1.y - p0.y
        denominator = (x1minusx0 * x1minusx0) + (y1minusy0 * y1minusy0)
        deltaxtot = -1*count * math.cos(math.atan2((y1minusy0),(x1minusx0)))
        deltaytot = -1*count * math.sin(math.atan2((y1minusy0),(x1minusx0)))
        newList.append(p0.Clone())
        while (i < l):
            pToMove = oldList[i].Clone()
            t = (((pToMove.y - p0.y) * y1minusy0) + ((pToMove.x - p0.x) * x1minusx0))/denominator
            p = Point.Point(round(pToMove.x + (deltaxtot * t)), round(pToMove.y + (deltaytot * t)))
            newList.append(p)
            i = i + 1
        return RankLocation.RankLocation(newList)

    def Split(self, count, beginLocation):
        self._endLocation = self.CalcLocation(count, beginLocation)
        newCommand = Condense1((self._length - count), self._endLocation)
        newCommand.SetName(self._name)
        self._length = count
        return (self, newCommand)

    def CalcBeginLocation(self, count, endLocation):
        temp = Expand1(self._length - count, endLocation)
        return temp.GetEndLocation()


# DTP inplementation:
# Given the beginning location and the end location of the DTP, there must be
# some way of getting between the two.  What we do, in essence, is map
# points on the end location to points on the begin location, and vice versa.
# Once all points have been mapped, linearly extrapolate the intermediate
# RankLocations.
# Specifically, we create a new RankLocation, _endLocationPrime.  If the number
# of points (total) in the begin location is n, and the number of points (total)
# in the end location is m, _endlocationPrime will have m + n - 2 points in it.
# We assume that the end points map to the end points, and then we have one
# point for every middle point (spline point) in both endLocation and
# beginLocation.

# To determine the locaitons of the mapped points, we calculate the proportion
# of the length of the total curve on which a given point lies, and map this
# point to the location on the other curve of the same total proportion.
# (A point 1/3 of the way along beginLocation will map to 1/3 of the way along
# EndLocation)

# Note that adding all these points would change the spline.  Thus, we set the
# slope at each point to be what the slope is right there in the original
# spline.

#To animate, we linearly extrapolate both point locations and point slopes,
# craeting a new spline with said features at every step.
class DTP(Command):
    def __init__(self, length, beginLocation, endLocation):
        self._length = length
        self._endLocation = endLocation
        self._name = 'DTP'
        listOfEndLocPoints = endLocation.GetListOfPoints()
        #Following line is just a striaght-line placeholder, will be replaced later.
        self._endLocationPrime = RankLocation.RankLocation([listOfEndLocPoints[0], listOfEndLocPoints[-1]])
        listOfBeginLocPoints = beginLocation.GetListOfPoints()
        endLengths = endLocation.GetLengths()
        beginLengths = beginLocation.GetLengths()
        endLengthFractions = self.CalcLengthFractions(endLengths)
        beginLengthFractions = self.CalcLengthFractions(beginLengths)
        totalLengthFractions = [0]
        self._beginLocationMember = [True]
        i = 0
        j = 0
        while ((i < (len(endLengthFractions) - 1)) or (j < (len(beginLengthFractions) - 1))):
            if (endLengthFractions[i] < beginLengthFractions[j]):
                totalLengthFractions.append(endLengthFractions[i])
                self._beginLocationMember.append(False)
                i = i + 1
            else:
                totalLengthFractions.append(beginLengthFractions[j])
                self._beginLocationMember.append(True)
                j = j + 1
        self._beginLocationMember.append(True)
        totalLengthFractions.append(1)
        beginPointsInfo = []
        endPointsInfo = []
        i = 0
        while (i < len(totalLengthFractions)):
            beginPointsInfo.append(beginLocation.GetInformationAtLengthFraction(totalLengthFractions[i]))
            endPointsInfo.append(endLocation.GetInformationAtLengthFraction(totalLengthFractions[i]))
            i = i + 1

        listOfNewEndPoints = []
        listOfNewEndSlopes = []
        listOfNewBeginPoints = []
        listOfNewBeginSlopes = []
        i = 0
        while (i < len(totalLengthFractions)):
            listOfNewEndPoints.append(endPointsInfo[i][0])
            listOfNewEndSlopes.append(endPointsInfo[i][1])
            listOfNewBeginPoints.append(beginPointsInfo[i][0])
            listOfNewBeginSlopes.append(beginPointsInfo[i][1])
            i = i + 1
        self._endLocationPrime.SetListOfPoints(listOfNewEndPoints, listOfNewEndSlopes)
        self._deltaPoints = []
        self._deltaSlopes = []
        i = 0
        while (i < len(listOfNewEndPoints)):
            pointDeltax = listOfNewEndPoints[i].x - listOfNewBeginPoints[i].x
            pointDeltay = listOfNewEndPoints[i].y - listOfNewBeginPoints[i].y
            slopeDeltax = listOfNewEndSlopes[i].x - listOfNewBeginSlopes[i].x
            slopeDeltay = listOfNewEndSlopes[i].y - listOfNewBeginSlopes[i].y
            self._deltaPoints.append(Point.Point(pointDeltax, pointDeltay))
            self._deltaSlopes.append(Point.Point(slopeDeltax, slopeDeltay))
            i = i + 1

    def CalcLocation(self, count, beginLocation):
        if (count == 0):
            return self.CalcBeginLocation(count, self._endLocation)
        elif (count < self._length - 1):
            frac = count / float(self._length)
            newPoints = []
            newSlopes = []
            i = 0
            endPoints = self._endLocationPrime.GetListOfPoints()
            endSlopes = self._endLocationPrime.GetListOfSlopes()
            while (i < len(self._deltaPoints)):
                if (endSlopes is not None):
                    newPoints.append(self.LinExt(frac, self._deltaPoints[i], endPoints[i]))
                    newSlopes.append(self.LinExt(frac, self._deltaSlopes[i], endSlopes[i]))
                else:
                    newPoints.append(self.LinExt(frac, self._deltaPoints[i], endPoints[i]))
                i = i + 1
            loc = RankLocation.RankLocation(newPoints)
            loc.SetListOfPoints(newPoints, newSlopes)
            return loc
        else:
            return self._endLocation


    def Split(self, count, beginLocation):
        tempLocation = self.CalcLocation(count, beginLocation)
        newCommandSecond = Command.DTP(self._length - count, tempLocation, self._endLocation)
        newCommandFirst = Command.DTP(count, beginLocation, tempLocation)
        newCommandFirst.SetName(self._name)
        newCommandSecond.SetName(self._name)
        return (newCommandFirst, newCommandSecond)

    def CalcBeginLocation(self, count, endLocation):
        beginListOfPoints = []
        i = 0
        endListOfPoints = self._endLocationPrime.GetListOfPoints()
        if (count == 1):
            while (i < len(endListOfPoints)):
                if (self._beginLocationMember[i]):
                    newx = endListOfPoints[i].x - self._deltaPoints[i].x
                    newy = endListOfPoints[i].y - self._deltaPoints[i].y
                    beginListOfPoints.append(Point.Point(newx, newy))
                i = i + 1
            return RankLocation.RankLocation(beginListOfPoints)
        else:
            return self.CalcLocation(count, self.CalcBeginLocation(0, self._endLocation))

    def CalcLengthFractions(self, lengths):
        tot = 0
        i = 0
        while (i < len(lengths)):
            tot = tot + lengths[i]
            i = i + 1
        i = 1
        fractions = []
        fractions.append(lengths[0]/tot)
        while (i < len(lengths)):
            fractions.append(fractions[i - 1] + (lengths[i]/tot))
            i = i + 1
        return fractions

    def LinExt(self, frac, deltaPoint, endPoint):
        deltax = endPoint.x + (frac - 1)*deltaPoint.x
        deltay = endPoint.y + (frac - 1)*deltaPoint.y
        return Point.Point(deltax, deltay)

    def MergeWithFollowing(self, following):
        if ((following._name == self._name) and (isinstance(following, self))):
            newCommand = DTP((self._length + following.GetLength()), self.CalcBeginLocation(0, self._endLocation), following.GetEndLocation())
            newCommand.SetName(self._name)
            return newCommand
        else:
            return None

#   TODO:  Overwrite this!
#    def SnapEndLocation(self, location):

#    def __init__(self, length, beginLocation, endLocation):



class Flatten(Command):
    def __init__(self, length, beginLocation):
        beginListOfPoints = beginLocation.GetListOfPoints()
        endLocation = RankLocation.RankLocation([beginListOfPoints[0], beginListOfPoints[-1]])
        self._dtp = DTP(length, beginLocation, endLocation)
        self._length = length
        self._name = 'Flatten'
        self._endLocation = self._dtp.GetEndLocation()

    def CalcLocation(self, count, beginLocation):
        return self._dtp.CalcLocation(count, beginLocation)

    def Split(self, count, beginLocation):
        tempLocation = self.CalcLocation(count, beginLocation)
        newCommandSecond = Command.Flatten(self._length - count, tempLocation)
        newCommandFirst = Command.DTP(count, beginLocation, tempLocation)
        newCommandFirst.SetName(self._name)
        newCommandSecond.SetName(self._name)
        return (newCommandFirst, newCommandSecond)

    def CalcBeginLocation(self, count, endLocation):
        return self._dtp.CalcBeginLocation(count, endLocation)

    def MergeWithFollowing(self, following):
        if ((following._name == self._name) and (isinstance(following, self))):
            newCommand = Flatten((self._length + following.GetLength()), self.CalcBeginLocation(0, self._endLocation), following.GetEndLocation())
            newCommand.SetName(self._name)
            return newCommand
        else:
            return None


class Curve(Command):
    def __init__(self, length, beginLocation, endLocation):
        self._dtp = DTP(length, beginLocation, endLocation)
        self._length = length
        self._name = 'Curve'
        self._endLocation = self._dtp.GetEndLocation()

    def CalcLocation(self, count, beginLocation):
        return self._dtp.CalcLocation(count, beginLocation)

    def Split(self, count, beginLocation):
        tempLocation = self.CalcLocation(count, beginLocation)
        newCommandSecond = Command.DTP(self._length - count, tempLocation, self._endLocation)
        newCommandFirst = Command.Curve(count, beginLocation, tempLocation)
        newCommandFirst.SetName(self._name)
        newCommandSecond.SetName(self._name)
        return (newCommandFirst, newCommandSecond)

    def CalcBeginLocation(self, count, endLocation):
        return self._dtp.CalcBeginLocation(count, endLocation)

    def MergeWithFollowing(self, following):
        if ((following._name == self._name) and (isinstance(following, self))):
            newCommand = Curve((self._length + following.GetLength()), self.CalcBeginLocation(0, self._endLocation), following.GetEndLocation())
            newCommand.SetName(self._name)
            return newCommand
        else:
            return None


class FTA1(Command):
    def __init__(self, length, beginLocation, endLocation, listOfWayPoints):
        self._length = length
        self._name = "FTA."
        self._endLocation = endLocation
        self._beginLocation = beginLocation
        self._listOfWayPoints = listOfWayPoints
        beginPoints = beginLocation.GetListOfPoints()
        beginSlopes = beginLocation.GetListOfSlopes()
        endPoints = endLocation.GetListOfPoints()
        endSlopes = endLocation.GetListOfSlopes()
        self._newListOfPoints = []
        self._newListOfSlopes = []
        i = 0
        beginFracs = beginLocation.GetLengthFractions()
        endFracs = endLocation.GetLengthFractions()
        while (i < len(beginPoints)):
            info = beginLocation.GetInformationAtLengthFraction(beginFracs[i])
            self._newListOfPoints.append(info[0])
            self._newListOfSlopes.append(info[1])
#            if (beginSlopes is not None):
#                self._newListOfSlopes.append(beginSlopes[i])
#            else:
#                self._newListOfSlopes.append(None)
            i = i + 1
        i = 0
        while (i < len(listOfWayPoints)):
            self._newListOfPoints.append(listOfWayPoints[i])
            self._newListOfSlopes.append(None)
            i = i + 1
        i = 0
        while (i < len(endPoints)):
            info = endLocation.GetInformationAtLengthFraction(endFracs[i])
            self._newListOfPoints.append(info[0])
            self._newListOfSlopes.append(info[1])

#            self._newListOfPoints.append(endPoints[i])
#            if (endSlopes is not None):
#                self._newListOfSlopes.append(endSlopes[i])
#            else:
#                self._newListOfSlopes.append(None)
            i = i + 1
        self._beginRankLength = sum(beginLocation.GetLengths())
        self._endRankLength = sum(endLocation.GetLengths())
        self._totalLocation = RankLocation.RankLocation(self._newListOfPoints)
        self._totalLocation.SetListOfPoints(self._newListOfPoints, self._newListOfSlopes)

    def b(self):
        return self._beginLocation

    def e(self):
        return self._endLocation

    def t(self):
        return self._totalLocation

    def CalcLocation(self, count, beginLocation):
        if (beginLocation.CompareRankLocation(self._beginLocation)):
            endLocation = self._endLocation
            totalLocation = self._totalLocation
        else:
            distancePoint = self._beginLocation.IsTranslated(beginLocation)
            if (distancePoint is None):
                newFTA1 = FTA1(self._length, beginLocation, self._endLocation, self._listOfWayPoints)
                endLocation = self._endLocation
                totalLocation = newFTA1.GetTotalLocation()
            else:
                dx = distancePoint.x
                dy = distancePoint.y
                newListOfWayPoints = []
                i = 0
                while (i < len(self._listOfWayPoints)):
                    newListOfWayPoints.append(Point.Point(self._listOfWayPoints[i].x + dx, self._listOfWayPoints[i].y))
                    i = i + 1
                newListOfEndSlopes = []
                newListOfEndPoints = []
                oldListOfEndPoints = self._endLocation.GetListOfPoints()
                oldListOfEndSlopes = self._endLocation.GetListOfSlopes()
                i = 0
                while (i < len(self._endLocation.GetListOfPoints())):
                    newListOfEndPoints.append(Point.Point(oldListOfEndPoints[i].x + dx, oldListOfEndPoints[i].y + dy))
                    if (oldListOfEndSlopes is not None):
                        newListOfEndSlopes.append(oldListOfEndSlopes[i])
                    else:
                        newListOfEndSlopes.append(None)
                    i = i + 1
                newEndLocation = RankLocation.RankLocation(newListOfEndPoints)
                newEndLocation.SetListOfPoints(newListOfEndPoints, newListOfEndSlopes)
                newFTA1 = FTA1(self._length, beginLocation, newEndLocation, newListOfWayPoints)
                endLocation = newEndLocation
                totalLocation = newFTA1.GetTotalLocation()

        if (count == 0):
            return beginLocation
        elif (count >= self._length - 1):
            return endLocation
        totalLengths = totalLocation.GetLengths()
        beginLengths = beginLocation.GetLengths()
        endLengths = endLocation.GetLengths()

        beginFracTotal = ((sum(totalLengths) - sum(endLengths))*(count/float(self._length)))/float(sum(totalLengths))
        endFracTotal = (((sum(totalLengths) - sum(beginLengths))*(count/float(self._length))) + sum(beginLengths))/float(sum(totalLengths))
        begPointInfo = totalLocation.GetInformationAtLengthFraction(beginFracTotal)
        endPointInfo = totalLocation.GetInformationAtLengthFraction(endFracTotal)
        newPoints = []
        newSlopes = []
        newPoints.append(begPointInfo[0])
        newSlopes.append(None)#begPointInfo[1])
        i = begPointInfo[2] + 1
        totalFracs = totalLocation.GetLengthFractions()
        while (i <= endPointInfo[2]):
            info = totalLocation.GetInformationAtLengthFraction(totalFracs[i])
            if (not info[0].CompareTo(newPoints[-1])):
                newPoints.append(info[0])
                newSlopes.append(None)#info[1])
            i = i + 1
        if (len(newPoints) == 1):
            midFracTotal = (beginFracTotal + endFracTotal) / float(2)
            info = totalLocation.GetInformationAtLengthFraction(midFracTotal)
            newPoints.append(info[0])
            newSlopes.append(None)#info[1])
        newPoints.append(endPointInfo[0])
        newSlopes.append(None)#endPointInfo[1])
        newLoc = RankLocation.RankLocation(newPoints)
        newLoc.SetListOfPoints(newPoints, newSlopes)
        return newLoc

#    def Split(self, count, beginLocation):
#        tempLocation = self.CalcLocation(count, beginLocation)
#        newCommandSecond = Command.FTA1(self._length - count, tempLocation, self._endLocation)
#        newCommandFirst = Command.FTA1(count, beginLocation, tempLocation)
#        newCommandFirst.SetName(self._name)
#        newCommandSecond.SetName(self._name)
#        return (newCommandFirst, newCommandSecond)

    def CalcBeginLocation(self, count, endLocation):
        if (endLocation.CompareRankLocation(self._endLocation)):
            beginLocation = self._beginLocation
            totalLocation = self._totalLocation
        else:
            distancePoint = self._endLocation.IsTranslated(endLocation)
            if (distancePoint is None):
                newFTA1 = FTA1(self._length, self._beginLocation, endLocation, self._listOfWayPoints)
                endLocation = self._endLocation
                totalLocation = newFTA1.GetTotalLocation()
            else:
                dx = distancePoint.x
                dy = distancePoint.y
                newListOfWayPoints = []
                i = 0
                while (i < len(self._listOfWayPoints)):
                    newListOfWayPoints.append(Point.Point(self._listOfWayPoints[i].x + dx, self._listOfWayPoints[i].y))
                    i = i + 1
                newListOfBeginSlopes = []
                newListOfBeginPoints = []
                oldListOfBeginPoints = self._beginLocation.GetListOfPoints()
                oldListOfBeginSlopes = self._beginLocation.GetListOfSlopes()
                i = 0
                while (i < len(self._beginLocation.GetListOfPoints())):
                    newListOfBeginPoints.append(Point.Point(oldListOfBeginPoints[i].x + dx, oldListOfBeginPoints[i].y + dy))
                    if (oldListOfBeginSlopes is not None):
                        newListOfBeginSlopes.append(oldListOfBeginSlopes[i])
                    else:
                        newListOfBeginSlopes.append(None)
                    i = i + 1
                newBeginLocation = RankLocation.RankLocation(newListOfBeginPoints)
                newBeginLocation.SetListOfPoints(newListOfBeginPoints, newListOfBeginSlopes)
                newFTA1 = FTA1(self._length, newBeginLocation, endLocation, newListOfWayPoints)
                beginLocation = newBeginLocation
                totalLocation = newFTA1.GetTotalLocation()

        if (count == 0):
            return beginLocation
        elif (count >= self._length - 1):
            return endLocation

        totalLengths = totalLocation.GetLengths()
        beginLengths = beginLocation.GetLengths()
        endLengths = endLocation.GetLengths()
        beginFracTotal = ((sum(totalLengths) - sum(endLengths))*(count/float(self._length)))/float(sum(totalLengths))
        endFracTotal = (((sum(totalLengths) - sum(beginLengths))*(count/float(self._length))) + sum(beginLengths))/float(sum(totalLengths))
        begPointInfo = totalLocation.GetInformationAtLengthFraction(beginFracTotal)
        endPointInfo = totalLocation.GetInformationAtLengthFraction(endFracTotal)
        newPoints = []
        newSlopes = []
        newPoints.append(begPointInfo[0])
        newSlopes.append(None)#begPointInfo[1])
        i = begPointInfo[2] + 1
        totalFracs = totalLocation.GetLengthFractions()
        while (i <= endPointInfo[2]):
            info = totalLocation.GetInformationAtLengthFraction(totalFracs[i])
            newPoints.append(info[0])
            newSlopes.append(None)#info[1])
            i = i + 1
        if (len(newPoints) == 1):
            midFracTotal = (beginFracTotal + endFracTotal) / float(2)
            info = totalLocation.GetInformationAtLengthFraction(midFracTotal)
            newPoints.append(info[0])
            newSlopes.append(None)#info[1])
        newPoints.append(endPointInfo[0])
        newSlopes.append(None)#endPointInfo[1])
        newLoc = RankLocation.RankLocation(newPoints)
        newLoc.SetListOfPoints(newPoints, newSlopes)
        return newLoc


    def GetTotalLocation(self):
        return self._totalLocation


class FTA0(Command):
    def __init__(self, length, beginLocation, endLocation, listOfWayPoints):
        self._endLocation = endLocation
        self._beginLocation = beginLocation
        self._listOfWayPoints = listOfWayPoints
        reverseListOfWayPoints = (copy.deepcopy(listOfWayPoints))
        reverseListOfWayPoints.reverse()
        self._innerFTA1 = FTA1(length, copy.deepcopy(endLocation), copy.deepcopy(beginLocation), listOfWayPoints)#reverseListOfWayPoints)
        self._length = length
        self._name = 'FTA>'

    def CalcLocation(self, count, beginLocation):
        return self._innerFTA1.CalcBeginLocation((self._length - count), beginLocation)

    def CalcBeginLocation(self, count, endLocation):
        return self._innerFTA1.CalcLocation((self._length - count), endLocation)

    def GetTotalLocation(self):
        return self._innerFTA1.GetTotalLocation()

    def b(self):
        return self._innerFTA1.e()

    def e(self):
        return self._innerFTA1.b()

    def t(self):
        return self._innerFTA1.t()
