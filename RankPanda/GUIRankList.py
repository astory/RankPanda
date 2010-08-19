#!/usr/bin/env python
#GUI Rank List: renders the list of ranks

import wx
#import CoreWrapper
import RankLocation
import Point

# constants

RANK_COLOUR = wx.Colour(0, 0, 0)
SELECTED_RANK_COLOUR = wx.Colour(255, 0, 0)

class RankList(wx.Panel):


    def __init__(self, parent, id, main):
        wx.Panel.__init__(self, parent, id)
        self.main = main

        self.bgColour = self.main.panel.GetBackgroundColour()
        self.fgColour = self.main.panel.GetForegroundColour()

        # mode variables
        self.currRect = wx.Rect(0, 0, *self.GetSizeTuple())

        self.ranks = []
        self.selectedRanks = []

    def OnPaint(self, event):
        self.Draw()
        fielddc = wx.PaintDC(self)
        fielddc.DrawBitmap(self.paintBitmap, 0, 0, False) # manual double-buffering since nothing else seems to work...

    def Draw(self):
        self.paintBitmap = wx.EmptyBitmap(*self.GetSizeTuple())
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))
        dc.SelectObject(self.paintBitmap)

        dc.SetBackground(wx.Brush(self.bgColour))
        dc.Clear()

        self.currRect.SetX(0)
        rect = dc.DrawImageLabel(' ', wx.NullBitmap, self.currRect, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        self.currRect.SetX(rect.GetX() + rect.GetWidth())

        i = 0

        for r in self.ranks: 
#           dc.SetTextForeground(RANK_COLOUR)
            dc.SetTextForeground(self.fgColour)

            if i in self.selectedRanks:
                dc.SetTextForeground(SELECTED_RANK_COLOUR)

            rect = dc.DrawImageLabel(r, wx.NullBitmap, self.currRect, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
            self.currRect.SetX(rect.GetX() + rect.GetWidth())

            i += 1

    def OnResize(self, event):
        self.currRect.SetWidth(self.GetSizeTuple()[0])

        self.Refresh(False)


# ranks is a list of rank labels; selectedRanks is a list of indices of ranks that should be selected
    def SetRanks(self, ranks, selectedRanks):
        self.ranks = ranks
        self.selectedRanks = selectedRanks

        self.Refresh(False)
