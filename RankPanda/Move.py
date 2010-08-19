import RankIDGen
import Rank
import pprint


class Move(object):
    def __init__(self, startCount, length, song, prior, following, number):
        self._startCount = startCount
        self._length = length
        self._song = song
        self._idRankIndex = dict()
        self._nameRankIndex = dict()
        self._RankIDGen = RankIDGen.RankIDGen()
        self._name = None
        self._number = None
        self.SetNumber(number)
        self._prior = prior
        self._following = following
        self._listOfActiveRanks = []
        self._listOfActiveCommands = []
        self._moveText = None
        self._moveTextOverwrite = None



    def GetNameRankIndex(self):
        return self._nameRankIndex

    # Simple - return the count at which the move starts.
    def GetStartCount(self):
        return self._startCount
    # Also striaghtforward.
    def SetStartCount(self, startCount):
        self._startCount = startCount

    def GetListOfActiveCommands(self):
        return self._listOfActiveCommands

    def GetSelectedRanks(self):
        return self._listOfActiveRanks

    def SetSelectedRanks(self, newList):
        self._listOfActiveRanks = newList
    # Simple
    def GetLength(self):
        return self._length

    # Not as simple.  If the length has increased, any command lists that
    # are being auto-generated need to be padded out with MT.  If the length
    # has decreased, this will need a flag somewhere.
    def SetLength(self, newLength):
        self._length = newLength
        self.UpdateAllRanksCommandList()

    def GetRankIDGen(self):
        return self._RankIDGen

    def GetNumber(self):
        return self._number

    def SetNumber(self, number):
        if ((self._name is None) or (self._name == ('Move ' + str(self._number)))):
            self._name = ('Move ' + str(number))
        self._number = number

    def GetName(self):
        return self._name

    def SetName(self, name):
        self._name = name

    # Return what's in the current self._prior field.
    def GetPrior(self):
        return self._prior

    # Sets the self._prior field.  Goes through both self and _prior's
    # namrRankIndex.  If any ranks have a name in both, auto-generate the
    # commands.
    def SetPrior(self, newPrior):
        self._prior = newPrior
        self.UpdateAllRanksCommandList()


    # Returns a list of all Ranks
    def GetAllRanks(self):
        allRanks = []
        i = 0
        items = self._idRankIndex.items()
        while (i < len(items)):
            allRanks.append(items[i][1])
            i = i + 1
        return allRanks


    def GetAllNamedRanks(self):
        allNamedRanks = []
        i = 0
        items = self._nameRankIndex.items()
        while (i < len(items)):
            allNamedRanks.append(items[i][1])
            i = i + 1
        return allNamedRanks

    # Shortcut
    def UpdateAllRanksCommandList(self):
        i = 0
        items = self._nameRankIndex.items()
        while (i < len(items)):
            items[i][1].UpdateCommandList()
            i = i + 1


    # Return what's in the self._following field.
    def GetFollowing(self):
        return self._following

    # Sets the self._following field.  Unlike setting self._prior, this one
    # doesn't really matter.
    def SetFollowing(self, following):
        self._following = following

    # Returns the current song.  Possibly useful for a rank to call.
    def GetSong(self):
        return self._song

    #Should never be called.
#    def SetSong(self):
#        pass

    # Creates a new rank and adds it to the IDRankIndex.
    # If name is not None, call self.NameRank(name).
    def CreateRank(self, location, name):
        r = Rank.Rank(location, self)
        self._idRankIndex[r.GetID()] = r
        if (name is not None):
            self.NameRank(r.GetID(), name)
        r.UpdateCommandList()
        return r

    # Sets the name field of a rank.
    def NameRank(self, ID, name):
        if (self.LookUpName(name) is None):
            r = self._idRankIndex[ID]
            if (r.GetName() in self._nameRankIndex):
                del self._nameRankIndex[r.GetName()]
            r.SetName(name)
            self._nameRankIndex[name] = r

    # Deletes a rank.  Note that this will also need to reset the command list
    # for the rank in the following move, if applicable.
    def DeleteRank(self, id):
        r = self._idRankIndex[id]
        if (self._listOfActiveRanks.count(r) != 0):
            self._listOfActiveRanks.remove(r)
        del self._idRankIndex[id]
        name = r.GetName()
        if (name is not None):
            del self._nameRankIndex[name]
            if (self._following is not None):
                if (self._following.LookUpName(name) is not None):
                    self._following.LookUpName(name).UpdateCommandList()

    # Should be self-explanatory.
    def DeleteAllRanks(self):
        i = 0
        items = self._idRankIndex.items()
        while (i < len(items)):
            ID = items[i][0]
            self.DeleteRank(ID)
            i = i + 1


    # See song.MergeMoves() for relevant documentation.
    # Returns the new move created.  Also resets the prior and following
    # references of the moves before and after the set being merged.
    # Does not do anything to any data structures in Song.
    def MergeWithPrior(self):
        prior = self.GetPrior()
        priorprior = prior.GetPrior()
        following = self.GetFollowing()
        newMove = Move(prior._startCount, (prior._length + self._length), self._song, priorprior, following, prior.GetNumber())
        if (priorprior is not None):
            priorprior.SetFollowing(newMove)
        if (following is not None):
            following.SetPrior(newMove)
        PriorIDMarkedIndex = dict()
        i = 0
        Iterator = prior._idRankIndex.items()
        l = len(Iterator)
        while (i < l):
            PriorIDMarkedIndex[Iterator[i][0]] = False
            i = i + 1
        i = 0
        Iterator = self._idRankIndex.items()
        l = len(Iterator)
        while (i < l):
            rank = Iterator[i][1]
            name = rank.GetName()
            newMove.CreateRank(rank.GetEndLocation(), name)
            if (name is not None):
                oldRank = prior.LookUpName(name)
                if (priorprior is not None):
                    oldoldRank = priorprior.LookUpName(name)
                else:
                    oldoldRank = None
                newRank = newMove.LookUpName(name)
                newRank.hold = rank.hold
                if (oldRank is not None):
                    newRank.hold = (rank.hold or oldRank.hold)
                    oldID = oldRank.GetID()
                    PriorIDMarkedIndex[oldID] = True
                    if (oldoldRank is not None):
                        if (newRank.hold):
                            newRank.SetCommandList(oldRank.GetCommandList().extend(rank.GetCommandList()))
                        else:
                            newRank.UpdateCommandList()
            i = i + 1
        i = 0
        Iterator = PriorIDMarkedIndex.items()
        l = len(Iterator)
        while (i < l):
            if (Iterator[i][1]):
                pass
            else:
                ID = Iterator[i][0]
                rank = prior.LookUpID(ID)
                name = rank.GetName()
                newMove.CreateRank(rank.GetEndLocation(), name)
                newRank = newMove.LookUpName(name)
                newRank.hold = rank.hold
                if (name is not None):
                    if (priorprior is not None):
                        oldoldRank = priorprior.LookUpName(name)
                        if (oldoldRank is not None):
                            commandList = rank.GetCommantList()
                            commandList.append(Command.MarkTime(self._length, rank.GetEndLocation()))
                            newRank.SetCommandList(commandList)
                    if (following is not None):
                        followingRank = following.LookUpName(name)
                        if (followingRank is not None):
                            followingRank.UpdateCommandList()
                newRank.UpdateCommandList()
            i = i + 1
        return newMove


    # Same as Merge() but for splitting
    def Split(self, count):
        newMoveFirst = Move(self._startCount, count, self._song, self._prior, None, self.GetNumber())
        newMoveSecond = Move((self._startCount + count), (self._length - count), self._song, newMoveFirst, self._following, (self.GetNumber() + 1))
        newMoveFirst.SetFollowing(newMoveSecond)
        if (self._prior is not None):
            self._prior.SetFollowing(newMoveFirst)
        if (self._following is not None):
            self._following.SetPrior(newMoveSecond)
        i = 0
        Iterator = self._idRankIndex.items()
        l = len(Iterator)
        while (i < l):
            rank = Iterator[i][1]
            name = rank.GetName()
            newMoveFirst.CreateRank(rank.GetCalculatedLocation(count), name)
            newMoveSecond.CreateRank(rank.GetEndLocation(), name)
            if ((rank.hold) and (rank.GetName() is not None) and (self._prior.LookUpName(name) is not None)):
                newRank1 = newMoveFirst.LookUpName(name)
                newRank2 = newMoveSecond.LookUpName(name)
                newRank1.hold = rank.hold
                newRank2.hold = rank.hold
                i = 0
                tot = count
                while (tot > 0):
                    tot = tot - rank.GetCommandList()[i].GetLength()
                    i = i + 1
                i = i - 1
                tot = tot + rank.GetCommandList()[i].GetLength()
                beginLoc = rank.GetCommandList()[i - 1].GetEndLocation()
                splitCommand = rank.GetCommandList()[i].Split(tot, beginLoc)
                firstCommandList = rank.GetCommandList()[0:(i - 1)]
                firstCommandList.append(splitCommand[0])
                secondCommandList = [splitCommand[1]]
                secondCommandList.extend(rank.GetCommandList()[(i + 1):-1])
                newRank1.SetCommandList(firstCommandList)
                newRank2.SetCommandList(secondCommandList)
            i = i + 1
        return [newMoveFirst, newMoveSecond]


    # Passed in a name, returns the Rank object associated with it in the
    # current move.  Returns None if this does not exist.
    def LookUpName(self, name):
        if (name in self._nameRankIndex):
            return self._nameRankIndex[name]
        else:
            return None

    # Passed in an ID, returns the Rank object associated with it in the
    # current move.  Returns None if this does not exist.

    def LookUpID(self, ID):
        if (ID in self._idRankIndex):
            return self._idRankIndex[ID]
        else:
            return None

    def GetMoveText(self):
        return self._moveText

    def SetMoveText(self, moveText):
        self._moveText = moveText

    def GetMoveTextOverwrite(self):
        return self._moveTextOverwrite

    def SetMoveTextOverwrite(self, moveTextOverwrite):
        self._moveTextOverwrite = moveTextOverwrite

