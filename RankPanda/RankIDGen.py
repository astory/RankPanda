class RankIDGen(object):

    def __init__(self):
        self.nextID = 0

    def GetID(self):
        self.nextID = self.nextID + 1
        return self.nextID

