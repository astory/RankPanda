import math

"""A simple point module.

Exported Methods:

Distance -- Euclidian distance between two points

Exported Classes:

Point -- a simple point class with an x and y position.
"""

def Distance(p1, p2):
    """Get the Euclidean distance between two points"""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

# TODO(astory): differentiate slopes and points.  They shouldn't be represented
# with the same class because not all of the functions make sense.
class Point(object):
    """ A simple point class with an x and y position.

    This class simply represents a point.  It's often an x,y coordinate
    on-screen, thought it's also sometimes a pair of slopes (dx/dt and dy/dt).

    Possible modification:  Get rid of this and convert to all wx.Point perhaps?

    Public functions:
    CompareTo -- sees if two points are within epsilon of each other
    Clone -- produce a deep copy.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def CompareTo(self, p1, epsilon=0.5):
        """Compare two points, and return if they are within epsilon

        Args:
            p1:  the other point to which to compare
            epsilon:  the minimum distance for equality.

        Returns:
            A boolean, whether the points are within epsilon of each other or
            not.
        """
        return Distance(self, p1) < epsilon

    def __eq__(self, other):
        return self.CompareTo(other, epsilon=0.00001)

    def __ne__(self, other):
        return not self.__eq__(other)

    def Clone(self):
        """Produce a deep copy of this point"""
        return Point(self.x, self.y)

    def __repr__(self):
        return ('Point with x = ' + str(self.x) + ', y = ' + str(self.y))

    def __str__(self):
        return self.__repr__()
