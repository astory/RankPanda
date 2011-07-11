import math
import Point


# This class handles the creation of splines.
# A Cubic Hermite Spline can be defined by a list of points and their slopes.
# Once all these points and slopes are had, a smooth spline is defined between
# each consecutive two points.
# Let x(t) be a spline between two points, xi and xj (j = i + 1).
# Let the slope at xi be mi and the slope at xj be mj.
# Then, x(t) is defined as:
# x(t) = (2t^3 - 3t^2 + 1)xi + (t^3 - 2t^2 + t)mi + (-2t^3 + 3t^2)xj + (t^3 - t^2)mj
# Repeat to get y(t).
# When you shift t from 0 to 1, x(t) and y(t) will generate a smooth curve
# between each pair of points.  Further, the curves will all be smooth with
# the one next to them, as the slopes are equal.
# The splines are saved in a simple format; see below.

# TODO(astory): convert to module level functions.  None of these actually take
# advantage of, or have any reason for, being in a class.

class SplineGenerator:

    # This calculated what the slopes at the points should be for the splines.
    # The method we use simply draws a straight line between the point before
    # and the point after, and this becomes the slope of the point.
    # Note that the slopes are dx/dt and dy/dt, not dx/dy.
    @classmethod
    def _GetSlope(cls, PointTriple):
        p0 = PointTriple[0]
        p1 = PointTriple[1]
        p2 = PointTriple[2]
        pFirst = None
        pSecond = None
        n = 1
        if (p0 is None):
            pFirst = p1
            pSecond = p2
            n = 2
        elif (p2 is None):
            pFirst = p0
            pSecond = p1
            n = 2
        else:
            pFirst = p0
            pSecond = p2
        slopex = (n/float(2))*(pSecond.x - pFirst.x)
        slopey = (n/float(2))*(pSecond.y - pFirst.y)
        return Point.Point(slopex, slopey)

    # The main splining method.  Takes in a list of points and their slopes,
    # and calculates the splines connecting them.  Farily straightforward, once
    # you know how it works, as described above.
    # Note that is any slope is None, it'll automatically be calculated.
    # This should often be the case, except when doing something like
    # intermediate DTP locations or something.
    # A given spline is stored as a list of four elements:
    # [constantTerm, linearTerm, quadraticTerm, cubicTerm]
    # The spline lists are then saved as [xsplines, ysplines]
    # Each one is saved in order.
    @classmethod
    def GetSplines(cls, pointList, oldSlopeList):
        slopeList = []
        l = len(pointList)
        i = 0
        while (i < l):
            if (oldSlopeList[i] is None):
                if (i == 0):
                  slopeList.append(SplineGenerator._GetSlope([None, pointList[0], pointList[1]]))
                elif (i == (l - 1)):
                    slopeList.append(SplineGenerator._GetSlope([pointList[i - 1], pointList[i], None]))
                else:
                    slopeList.append(SplineGenerator._GetSlope([pointList[i - 1], pointList[i], pointList[i + 1]]))
            else:
                slopeList.append(oldSlopeList[i])
            i = i + 1
        splineList = []
        i = 0
        while (i < (l - 1)):
            xfn = [0, 0, 0, 0]
            yfn = [0, 0, 0, 0]
            xfn[0] = pointList[i].x
            yfn[0] = pointList[i].y
            xfn[1] = slopeList[i].x
            yfn[1] = slopeList[i].y
            xfn[2] = (-3*pointList[i].x) + (-2*slopeList[i].x) + (3*pointList[i+1].x) + (-1*slopeList[i+1].x)
            yfn[2] = (-3*pointList[i].y) + (-2*slopeList[i].y) + (3*pointList[i+1].y) + (-1*slopeList[i+1].y)
            xfn[3] = (2*pointList[i].x) + (slopeList[i].x) + (-2*pointList[i+1].x) + (slopeList[i+1].x)
            yfn[3] = (2*pointList[i].y) + (slopeList[i].y) + (-2*pointList[i+1].y) + (slopeList[i+1].y)
            splineList.append([xfn,yfn])
            i = i + 1
        return splineList


    # Algorithm here:  Find the length between the two end points.  Then,
    # find the length from point 0 to the midpoint of the spline, and then
    # from the midpoint to point 1.  If the sum of these two lengths is close
    # to the length of the first one, return the length.  If not, recurse
    # and add the lengths together.
    @classmethod
    def GetLength(cls, fnList, tol):
        return SplineGenerator._GetLengthHelper(fnList, 0, 1, tol)

    # TODO:  Make iterative!  It'll help.
    @classmethod
    def _GetLengthHelper(cls, fnList, ti, tf, tol):
        xi = SplineGenerator.EvalCubic(ti, fnList[0])
        yi = SplineGenerator.EvalCubic(ti, fnList[1])
        xf = SplineGenerator.EvalCubic(tf, fnList[0])
        yf = SplineGenerator.EvalCubic(tf, fnList[1])
        tm = (ti + tf)/float(2)
        xm = SplineGenerator.EvalCubic(tm, fnList[0])
        ym = SplineGenerator.EvalCubic(tm, fnList[1])
        side3 = math.sqrt((xf - xi)*(xf - xi) + (yf - yi)*(yf - yi))
        side1 = math.sqrt((xm - xi)*(xm - xi) + (ym - yi)*(ym - yi))
        side2 = math.sqrt((xf - xm)*(xf - xm) + (yf - ym)*(yf - ym))
        try:
            if ((math.fabs(((side1 + side2)/float(side3)) - 1)) <= tol):
                return math.fabs(side1 + side2)
            else:
                return (SplineGenerator._GetLengthHelper(fnList, ti, tm, tol)) + (SplineGenerator._GetLengthHelper(fnList, tm, tf, tol))
        except:
            if ((math.fabs(((side1 + side2)/float(side3)) - 1)) <= tol):
                return math.fabs(side1 + side2)
            else:
                return (SplineGenerator._GetLengthHelper(fnList, ti, tm, tol)) + (SplineGenerator._GetLengthHelper(fnList, tm, tf, tol))

    # Simply find the value of the spline function at the point.
    @classmethod
    def EvalCubic(cls, t, fn):
        return (fn[0] + fn[1]*t + fn[2]*t*t + fn[3]*t*t*t)

    @classmethod
    def EvalSlopeOfCubic(cls, t, fn):
        return (fn[1] + 2*fn[2]*t + 3*fn[3]*t*t)

    # This method takes in a splineList and figures out all the points to draw
    # along the spline.
    # Increase the value of NUMBERPERSTEP to draw more points.  Decrease to draw fewer.
    # I return a list of lists - each inner list contains all the points to be
    # drawn.

    @classmethod
    def GetPoints(cls, splineList):
        NUMBERPERSTEP = 8
        lengths = SplineGenerator.GetLengths(splineList)
        i = 0
# Ignore and feel free to remove the next lines, I think they're repetitiions of the GetLengths() function.
#        while (i < len(splineList)):
#            lengths.append(SplineGenerator.GetLength(splineList[i], 0.001))
#            i = i + 1
#        i = 0
        listOfPointLists = []
        while (i < len(splineList)):
            total = NUMBERPERSTEP*lengths[i]
            t = 0
            listOfPointLists.append([])
            xfn = splineList[i][0]
            yfn = splineList[i][1]
            while (t <= 1):
                listOfPointLists[i].append(Point.Point(SplineGenerator.EvalCubic(t, xfn), SplineGenerator.EvalCubic(t, yfn)))
                t = t + (1/float(total))
            i = i + 1
        return listOfPointLists


    # Pass in a fraction along the spline (as a whole) that you want
    # information about.  For example, pass in 0.5 to get exactly halfway along.
    # Returns a point, a slope, and an index at the given fractional length
    # along a spline.
    # The index is which spline part the point in question lies along.

    # First, I get the lengths of each spline part.  I then go through and find
    # the total lenght along the splines needed, and find which spline part the
    # fraction will lie on.
    # I then find the t value at which we need, and then just find the point
    # and slope at tha t value.
    # Note: Not designed for repeated use in real time, because the finding of
    # the t value recurses a recursive method until it's found.
    @classmethod
    def GetInformationAtLengthFraction(cls, splineList, lengthFraction):
        lengths = SplineGenerator.GetLengths(splineList)
        totalLength = sum(lengths)
        lengthNeeded = lengthFraction * totalLength
        i = 0
        if (lengthNeeded > 0.1):
            while (lengthNeeded > 0.1):
                lengthNeeded = lengthNeeded - lengths[i]
                i = i + 1
            i = i - 1
            lengthNeeded = lengthNeeded + lengths[i]
        if lengthNeeded <= 0.1:
            t = 0
        else:
            t = SplineGenerator._GetTValueAtLengthHelper(splineList[i], lengthNeeded, 0, 1, 0.001, 0.001)
        x = SplineGenerator.EvalCubic(t, splineList[i][0])
        y = SplineGenerator.EvalCubic(t, splineList[i][1])
        dx = SplineGenerator.EvalSlopeOfCubic(t, splineList[i][0])
        dy = SplineGenerator.EvalSlopeOfCubic(t, splineList[i][1])
        return [(Point.Point(x, y)),(Point.Point(dx, dy)), i]

    # Finds the length of each spline part in the list
    @classmethod
    def GetLengths(cls, splineList):
        lengths = []
        i = 0
        while (i < len(splineList)):
            lengths.append(SplineGenerator.GetLength(splineList[i], 0.001))
            i = i + 1
        return lengths

    # A simple recursive method.  Finds the midpoint of the current section
    # of the spline and zeros in until the length desired is found.
    # Note that while it's a recursive method, every call calls
    # GetLengthHelper(), another recursive method, which is why this shouldn't
    # be used in real time, if possible.
    # TODO:  make it iterative!  Should sav both space (for obvious
    # recursion-related reasons) and time (Python's not great with method calls,
    # I believe.)
    @classmethod
    def _GetTValueAtLengthHelper(cls, fnList, length, tinit, tfinal, lengthCalcTol, lengthCompareTol):
        tmid = (tinit + tfinal) / float(2)
        curLength = SplineGenerator._GetLengthHelper(fnList, 0, tmid, lengthCalcTol)
        if (math.fabs((curLength / float(length)) - 1) < lengthCompareTol):
            return tmid
        else:
            if (curLength > length):
                return SplineGenerator._GetTValueAtLengthHelper(fnList, length, tinit, tmid, lengthCalcTol, lengthCompareTol)
            else:
                return SplineGenerator._GetTValueAtLengthHelper(fnList, length, tmid, tfinal, lengthCalcTol, lengthCompareTol)
