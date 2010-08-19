import math


# This class simply represents a point.  It's often an x,y coordinate on-screen,
# thought it's also sometimes a pair of slopes (dx/dt and dy/dt).
# Possible modification:  Get rid of this and convert to all wx.Point perhaps?
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

# CompareTo tests to see if two are close to each other, if not exactly the same.
    def CompareTo(self, p1):
        return ((math.sqrt((self.x - p1.x)*(self.x - p1.x) + (self.y - p1.y)*(self.y - p1.y))) < 0.5)

    def Clone(self):
        return Point(self.x, self.y)

# Helpful for debugging purposes.
    def __repr__(self):
        return ('Point with x = ' + str(self.x) + ', y = ' + str(self.y))