import RankIDGen
import Rank
import pprint


class Move(object):
    def __init__(self, startCount, length, prior, following, number):
        self._startCount = startCount
        self._length = length
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

    def GetStartCount(self):
        return self._startCount

    def SetStartCount(self, startCount):
        self._startCount = startCount

    def GetListOfActiveCommands(self):
        return self._listOfActiveCommands

    def GetSelectedRanks(self):
        return self._listOfActiveRanks

    def SetSelectedRanks(self, newList):
        self._listOfActiveRanks = newList

    def GetLength(self):
        return self._length

    def SetLength(self, newLength):
        """Set length of move to newLength and update all ranks' commands."""
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

    def GetPrior(self):
        return self._prior

    def SetPrior(self, newPrior):
        """Set the prior move to this move and update all ranks' commands."""
        self._prior = newPrior
        self.UpdateAllRanksCommandList()

    # TODO(astory): make sane
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

    def GetFollowing(self):
        return self._following

    def SetFollowing(self, following):
        self._following = following

    # TODO(astory): make name an optional argument
    def CreateRank(self, location, name):
        """Create a new rank for this move.

        Creates a new rank and adds it to the IDRankIndex.  Names the rank if a
        name is given.
        """

        r = Rank.Rank(location, self)
        self._idRankIndex[r.GetID()] = r
        if (name is not None):
            self.NameRank(r.GetID(), name)
        r.UpdateCommandList()
        return r

    def NameRank(self, ID, name):
        """Set the name of a rank in this move."""
        if (self.LookUpName(name) is None):
            r = self._idRankIndex[ID]
            if (r.GetName() in self._nameRankIndex):
                del self._nameRankIndex[r.GetName()]
            r.SetName(name)
            self._nameRankIndex[name] = r

    # Deletes a rank.  Note that this will also need to reset the command list
    # for the rank in the following move, if applicable.
    def DeleteRank(self, id):
        """Delete a rank, and update the following move's corresponding rank."""
        r = self._idRankIndex[id]
        # TODO(astory): if r in _listOfActiveRanks
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

    # TODO(astory): this is ugly, and also possibly crash-laden.  FIXME
    def MergeWithPrior(self):
        """Merge this move with the previous one.

        See song.MergeMoves() for more documentation.  Also resets the prior and
        following references of moves immediately before and after the merged
        moves.

        Returns:
            The new move created
        """
        prior = self.GetPrior()
        priorprior = prior.GetPrior()
        following = self.GetFollowing()
        newMove = Move(prior._startCount,
                       (prior._length + self._length),
                       priorprior,
                       following,
                       prior.GetNumber())
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
                            newRank.SetCommandList(
                                oldRank.GetCommandList().extend(
                                    rank.GetCommandList()))
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

    # TODO(astory): really?  return a list?  FIXME
    def Split(self, count):
        """Split this move at count.

        Also resets the prior and following references of moves immediately
        before and after the split move.

        Returns:
            A list of the two new moves created
        """
        newMoveFirst = Move(self._startCount, count, self._prior,
                            None, self.GetNumber())
        newMoveSecond = Move((self._startCount + count), (self._length - count),
                             newMoveFirst, self._following,
                             (self.GetNumber() + 1))
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
            if ((rank.hold) and (rank.GetName() is not None) and
                (self._prior.LookUpName(name) is not None)):
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

    def LookUpName(self, name):
        """Return the rank with name in this move, or None."""
        if (name in self._nameRankIndex):
            return self._nameRankIndex[name]
        else:
            return None

    def LookUpID(self, ID):
        """Return the rank with ID in this move, or None."""
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
