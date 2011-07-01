import copy
import Point
import CubicHermiteSpline
import RankLocation
import Commands
import math

class RankLocationError(Exception):
    """Base class for exceptions in this module"""
class InvalidLocationListError(Exception):
    """Exception raised for invalid location lists"""
    pass

class RankLocation(object):
    """Class to represent the location of a rank.
    
    This class represents the location of a rank that can be drawn on the
    screen.  In part, it serves as an object-oriented wrapper for the
    SplineGenerator class.  However, it also supports straight-line ranks (only
    two points) and ranks that aren't curved/splined (think a zigzag).
    """

    def __init__(self, listOfPoints):
        """Generate a rank location based on a list of points

        Pass in your list of points upon creation.  It'll auto-generate the
        slopes; if you'd like to artificially set the slopes list you can do it
        later with the SetListOfPoints() function.  self.curved is true by
        default.  self.straightLine is initialized here for organizational
        purposes; it's actually set in the call to self.SetListOfPoints().
        """
        self.curved = True
        self.straightLine = True
        self._drawingPoints = []
        self._splineFunctions = None
        self._listOfSlopes = None
        self.SetListOfPoints(listOfPoints, self._listOfSlopes)


    def SetCurved(self, val):
        """Sets if the rank is curved or zigzagged."""
        self.curved = val
        self.SetListOfPoints(self._listOfPoints, self._listOfSlopes)

    def GetListOfPoints(self):
        return copy.deepcopy(self._listOfPoints)

    def GetListOfDrawingPoints(self):
        return self._drawingPoints

    def GetListOfSlopes(self):
        return copy.deepcopy(self._listOfSlopes)

    def SetListOfPoints(self, listOfPoints, listOfSlopes):
        """Sets the list of points and list of slopes.

        First, we determine if it's a straight line or not, meaning only two
        points.

        If None was passed in for the slopes, we generate a slopelist consisting
        of Nones, because this is the interface expected by the SplineGenerator
        class.

        We then just get the spline functions and drawing points.

        If it's a straight line or a zig-zag, just store the list of points.
        The straight lines will be drawn on the GUI end.
        """
        if (len(listOfPoints) < 2):
            raise InvalidLocationListError("Tried to set a list of %d points" % len(listOfPoints))
        self._listOfPoints = listOfPoints

        #determine whether the rank is straight: iff there are two points
        # TODO(astory): make this be based on collinearity
        self.straightLine = (len(listOfPoints) == 2)

        if ((self.curved) and (not self.straightLine)):
            if (listOfSlopes is None):
                i = 0
                self._listOfSlopes = []
                while (i < len(listOfPoints)):
                    self._listOfSlopes.append(None)
                    i = i + 1
            else:
                self._listOfSlopes = listOfSlopes
            self._splineFunctions = CubicHermiteSpline.SplineGenerator.GetSplines(self._listOfPoints, self._listOfSlopes)
            self._drawingPoints = CubicHermiteSpline.SplineGenerator.GetPoints(self._splineFunctions)
        else:
            self._listOfSlopes = None
            self._splineFunctions = None
            self._drawingPoints = None


    def Clone(self):
        return copy.deepcopy(self)

    def CompareRankLocation(self, l2):
        """Figure out if two RankLocations represent the same location on the field.

        Simply compare each point of one to each point of the other.
        If the slopes are different, it'll still return true.
        Slopes should almost always be auto generated; which means that for all
        practical purposes this won't affect anything.
        """
        if (len(self._listOfPoints) != len(l2._listOfPoints)):
            return False
        result = True
        i = 0
        while ((result) and (i < len(self._listOfPoints))):
            result = self._listOfPoints[i].CompareTo(l2._listOfPoints[i])
            i = i + 1
        return result

    def GetMidPoint(self):
        """The midpoint of a line connecting the first and last points."""
        p0 = self._listOfPoints[0]
        p1 = self._listOfPoints[len(self._listOfPoints) - 1]
        xmid = (p0.x + p1.x)/2
        ymid = (p0.y + p1.y)/2
        return Point.Point(xmid, ymid)

    def _Respline(self):
        self._splineFunctions = \
            CubicHermiteSpline.SplineGenerator.GetSplines(self._listOfPoints,
                                                          self._listOfSlopes)

    def GetPointAtT(self, t, number):
        """Get the number-th point in the rank's location at time t
        
        A straightforward function - takes in a t value, and a number in the
        spline list.  Depending on what kind of RankLocation it is, finds the
        (x,y) point at that t value.
        """
        if (self.straightLine):
            x = self._listOfPoints[0].x + t*(self._listOfPoints[1].x - self._listOfPoints[0].x)
            y = self._listOfPoints[0].y + t*(self._listOfPoints[1].y - self._listOfPoints[0].y)
            return Point.Point(x,y)
        elif (not self.curved):
            pfirst = self._listOfPoints[number]
            psecond = self._listOfPoints[number + 1]
            x = pfirst.x + t*(psecond.x - pfirst.x)
            y = pfirst.y + t*(psecond.y - pfirst.y)
            return Point.Point(x,y)
        else:
            x = CubicHermiteSpline.SplineGenerator.EvalCubic(t, self._splineFunctions[number][0])
            y = CubicHermiteSpline.SplineGenerator.EvalCubic(t, self._splineFunctions[number][1])
            return Point.Point(x,y)


    def GetInformationAtLengthFraction(self, lengthFraction):
        """Return information at a fraction of the length of the rank

        Pass in a fraction of the total length at which you wish to get
        information.
        If the rank is curved, simply call the equivalent function in the
        SplineGenerator.
        If not, do basically the same thing that that function does, only it's
        easier because everything's a straight line.  Find between which two
        points the length fraction lies, and then find how far along is needed
        to get the requisite length.  From there, get x, y, dx, and dy.  Return
        the same thing that the equivalent function in the SplineGenerator does:
        [(x,y), (dx,dy), i].
        """

        if (not self.straightLine):
            if (self.curved):
                return CubicHermiteSpline.SplineGenerator.GetInformationAtLengthFraction(self._splineFunctions, lengthFraction)

        lengths = self.GetLengths()
        totalLength = sum(lengths)
        lengthNeeded = lengthFraction * totalLength

        i = 0
        if (lengthNeeded > 0.1):
            while (lengthNeeded > 0.1):
                lengthNeeded = lengthNeeded - lengths[i]
                i = i + 1
            i = i - 1
            lengthNeeded = lengthNeeded + lengths[i]
        if (lengthNeeded <= 0.1):
            t = 0
        else:
            t = lengthNeeded/float(lengths[i])
        x = t*(self._listOfPoints[i + 1].x - self._listOfPoints[i].x) + self._listOfPoints[i].x #SplineGenerator.EvalCubic(t, splineList[i][0])
        y = t*(self._listOfPoints[i + 1].y - self._listOfPoints[i].y) + self._listOfPoints[i].y
        dx = (self._listOfPoints[i + 1].x - self._listOfPoints[i].x)
        dy = (self._listOfPoints[i + 1].y - self._listOfPoints[i].y)
        return [(Point.Point(x, y)),(Point.Point(dx, dy)), i]

    def GetLengthFractions(self):
        """Returns the lengths fractions at each point. 
        
        The first point lies at lelngth fraction 0, and the last at length
        fraction 1.  If a point is exactly in the middle, it's at fraction 0.5.
        """
        fracs = []
        lengths = self.GetLengths()
        lengthtot = sum(lengths)
        i = 0
        fracs.append(0.0)
        while (i < len(lengths)):
            fracs.append(fracs[i] + lengths[i]/float(lengthtot))
            i = i + 1
        return fracs

    def GetLengths(self):
        """Returns the length of each part of the RankLocation.

        Behaves differently depending on RankLocation type.  If it's curved, call
        the equivalent function in the SplineGenerator.
        If not, use the Pythogoran Theorem to find out how long each part is.
        """
        if (not self.straightLine):
            if (self.curved):
                return CubicHermiteSpline.SplineGenerator.GetLengths(
                        self._splineFunctions)
        i = 1
        lengths = []
        while (i < len(self._listOfPoints)):
            lengths.append(
                math.sqrt(
                    (self._listOfPoints[i - 1].x - self._listOfPoints[i].x) *
                    (self._listOfPoints[i - 1].x - self._listOfPoints[i].x) +
                    (self._listOfPoints[i - 1].y - self._listOfPoints[i].y) *
                    (self._listOfPoints[i - 1].y - self._listOfPoints[i].y)))
            i += 1
        return lengths


    def IsTranslated(self, l2):
        """ If the input is a translated version of self, returns the amount
        it's been translated by as a Point.  Returns input - self.  Else,
        returns None.
        """
        myList = self._listOfPoints
        otherList = l2.GetListOfPoints()
        if (len(myList) != len(otherList)):
            return None
        else:
            same = True
            dx = otherList[0].x - myList[0].x
            dy = otherList[0].y - myList[0].y
            i = 1
            while ((i < len(myList)) and same):
                same = not (((otherList[i].x - myList[i].x) == dx) and ((otherList[i].y - myList[i].y) == dy))
                i = i + 1
            if (same):
                return Point.Point(dx, dy)
            else:
                return None

    def SwitchEndpoints(self):
        """Switch the endpoints by reversing the entire list"""
        self._listOfPoints.reverse()
        self.SetListOfPoints(self._listOfPoints, self._listOfSlopes)

    # TODO(astory):  make safe for empty lists
    @classmethod
    def IsListOfPointsLengthZero(cls, pointList):
        """Returns true if all the points are on top of each other and the rank
        is of length 0.
        """
        p0 = pointList[0]
        status = True
        i = 1
        while (status and (i < len(pointList))):
            status = status and p0.CompareTo(pointList[i])
            i = i + 1
        return status
