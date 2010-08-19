#!/usr/bin/env python
#GUI Time Bar: renders the song time bar

import wx
#import CoreWrapper

# TODO: maybe fix height and draw waypoints under moves and have 'status bar' at bottom?

# constants
TOTAL_HEIGHT = 50.0
MOVE_HEIGHT = 20.0
WAYPOINT_HEIGHT = 10.0
TEXT_HEIGHT = 20.0

MOVE_BORDER_WIDTH = 2.0
MOVE_BORDER_CORNER_RADIUS = 5.0

EMPTY_COLOUR = wx.Colour(0, 0, 0)

GAP_COLOUR = wx.Colour(127, 0, 0)
GAP_BORDER_COLOUR = wx.Colour(255, 0, 0)

MOVE_COLOUR = wx.Colour(0, 127, 127)
MOVE_BORDER_COLOUR = wx.Colour(127, 127, 0)
MOVE_NAME_COLOUR = wx.Colour(127, 127, 0)

SELECTED_MOVE_COLOUR = wx.Colour(0, 191, 191)
SELECTED_MOVE_BORDER_COLOUR = wx.Colour(255, 255, 0)
SELECTED_MOVE_NAME_COLOUR = wx.Colour(255, 255, 0)

WAYPOINT_WIDTH = 10.0
WAYPOINT_SELECT_RADIUS = 2.0

WAYPOINT_COLOUR = wx.Colour(0, 0, 255)
SELECTED_WAYPOINT_COLOUR = wx.Colour(255, 0, 0)
ANIMATE_COLOUR = wx.Colour(0, 255, 0)

TEXT_COLOUR = wx.Colour(255, 255, 255)

class TimeBar(wx.Panel):


    def __init__(self, parent, id, main):
        wx.Panel.__init__(self, parent, id, size = (-1, 50))
        self.main = main

        self.bgColour = self.main.panel.GetBackgroundColour()
        self.fgColour = self.main.panel.GetForegroundColour()

        self.gaps = []
# gaps will be stored in the format (beginMeasure, endMeasure, beginCount, endCount)
        self.animatePt = -1
        self.mouseX = -1

        self.OnResize(None)

    def OnPaint(self, event):
        self.Draw()
        bardc = wx.PaintDC(self)
        bardc.DrawBitmap(self.paintBitmap, 0, 0, False) # manual double-buffering since nothing else seems to work...

    def Draw(self):
        self.paintBitmap = wx.EmptyBitmap(*self.GetSizeTuple())
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))
        dc.SelectObject(self.paintBitmap)

#       dc.SetBackground(wx.Brush(EMPTY_COLOUR))
        dc.SetBackground(wx.Brush(self.bgColour))
        dc.Clear()

        self.DrawMoves(dc)
        self.DrawWaypoints(dc)
        self.DrawText(dc)

# TODO add in draw waypoint functionality

    def DrawMoves(self, dc):
        oldend = 0 # end of previous move (need this for gap detection)
        oldendm = 1 # end of previous move in measures (need this so we can display beginning/ending measures of gaps
        for i in self.main.core.GetMoves():
            (m1, m2, begin, end) = self.main.core.GetMoveInfo(i[0])
            begin -= 1 # since counts start at 1 not 0
            # we don't decrement end because we want the move to be drawn to the end of its last count
            if begin > oldend: # if there is a gap between this move and the previous one
                self.DrawMove(oldend, begin, "", GAP_BORDER_COLOUR, GAP_COLOUR, GAP_BORDER_COLOUR, dc)
                self.gaps.append((oldendm, m1 - 1, oldend, begin))
            self.DrawMove(begin, end, i[1], MOVE_BORDER_COLOUR, MOVE_COLOUR, MOVE_NAME_COLOUR, dc)
            oldend = end
            oldendm = m2 + 1

        i = self.main.core.GetCurrentMove()
        (m1, m2, begin, end) = self.main.core.GetMoveInfo(i[0])
        begin -= 1 # since counts start at 1 not 0
        # we don't decrement end because we want the move to be drawn to the end of its last count
        self.DrawMove(begin, end, i[1], SELECTED_MOVE_BORDER_COLOUR, SELECTED_MOVE_COLOUR, SELECTED_MOVE_NAME_COLOUR, dc)

    def DrawWaypoints(self, dc):
        for wp in self.main.core.GetListOfWayPoints():
            self.DrawWaypoint(wp, WAYPOINT_COLOUR, dc)

        if self.animatePt != -1:
            self.DrawWaypoint([self.animatePt], ANIMATE_COLOUR, dc)

    def DrawText(self, dc):
#       dc.SetTextForeground(TEXT_COLOUR)
        dc.SetTextForeground(self.fgColour)

        textRect = wx.Rect(0, MOVE_HEIGHT + WAYPOINT_HEIGHT, self.GetRect().GetWidth(), TEXT_HEIGHT)

        if self.animatePt != -1:
            dc.DrawImageLabel("Animating @ Count: " + str(self.animatePt), wx.NullBitmap, textRect, wx.ALIGN_CENTRE)

        if self.mouseX != -1:
            count = self.mouseX / self.step
            dc.DrawImageLabel("Count: " + str(int(round(count))), wx.NullBitmap, textRect, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

            if self.mouseY > -1 and self.mouseY <= MOVE_HEIGHT:
                ret = self.PickMove(count)
                if ret is not None:
                    (m, m1, m2, begin, end, i) = ret
                    if begin == end:
                        count = "Count"
                    else:
                        count = "Counts"

                    if int(m1) == int(m2):
                        measure = "Measure"
                    else:
                        measure = "Measures"

                    dc.DrawImageLabel(m[1] + " [" + count + ": " + str(begin) + u"\u2013" + str(end) + ", " + measure + ": " + str(int(m1)) + u"\u2013" + str(int(m2)) + "]", wx.NullBitmap, textRect, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
                else:
                    gap = self.PickGap(count)
                    if gap is not None:
                        (m1, m2, begin, end) = gap
                        if begin == end:
                            count = "Count"
                        else:
                            count = "Counts"

                        if int(m1) == int(m2):
                            measure = "Measure"
                        else:
                            measure = "Measures"

                        dc.DrawImageLabel("[" + count + ": " + str(begin) + u"\u2013" + str(end) + ", " + measure + ": " + str(int(m1)) + u"\u2013" + str(int(m2)) + "]", wx.NullBitmap, textRect, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)

            elif self.mouseY > MOVE_HEIGHT and self.mouseY <= MOVE_HEIGHT + WAYPOINT_HEIGHT:
                wp = self.PickWaypoint(count)
                if wp is not None:
                    dc.DrawImageLabel("Waypoint[Count: " + str(wp[0]) + ", Time: " + str(wp[1]) + "]", wx.NullBitmap, textRect, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)

    def DrawMove(self, begin, end, name, borderColour, moveColour, nameColour, dc):
        dc.SetPen(wx.Pen(borderColour, MOVE_BORDER_WIDTH))
        dc.SetBrush(wx.Brush(moveColour))
        dc.SetTextForeground(nameColour)

        moveRect = wx.Rect(begin * self.step, 0, (end - begin) * self.step, MOVE_HEIGHT)
        dc.DrawRoundedRectangleRect(moveRect, MOVE_BORDER_CORNER_RADIUS)
        if name != "" and moveRect.GetWidth() >= dc.GetFullTextExtent(name)[0]:
            dc.DrawImageLabel(name, wx.NullBitmap, moveRect, wx.ALIGN_CENTRE)

    def DrawWaypoint(self, wp, colour, dc):
        dc.SetPen(wx.Pen(colour, 0))
        dc.SetBrush(wx.Brush(colour))

        x = wp[0] * self.step;
        list = []
        list.append(wx.Point(x - WAYPOINT_WIDTH / 2.0, MOVE_HEIGHT + WAYPOINT_HEIGHT))
        list.append(wx.Point(x + WAYPOINT_WIDTH / 2.0, MOVE_HEIGHT + WAYPOINT_HEIGHT))
        list.append(wx.Point(x, MOVE_HEIGHT))

        dc.DrawPolygon(list)

    def PickMove(self, count):
        i = 0
        for m in self.main.core.GetMoves():
            (m1, m2, begin, end) = self.main.core.GetMoveInfo(m[0])
            if count >= begin and count <= end:
                return (m, m1, m2, begin, end, i)
            i += 1

        return None

    def PickGap(self, count):
        for m in self.gaps:
            (m1, m2, begin, end) = m
            if count >= begin and count <= end:
                return (m1, m2, begin, end)

        return None

    def PickWaypoint(self, count):
        for wp in self.main.core.GetListOfWayPoints():
            if abs(wp[0] - count) <= WAYPOINT_SELECT_RADIUS:
                return wp

        return None

    def OnResize(self, event):
        (w, h) = self.GetSizeTuple()
        self.rect = wx.Rect(0, 0, w, h)
        self.step = float(w) / self.main.core.GetTotalCounts()

        self.Refresh(False)

    def AnimateCount(self, count): # tell the timebar that we are animating and are at the given count (-1 for stop animating)
        self.animatePt = count
        self.Refresh(False)

    def OnLeftClick(self, event):
        count = self.mouseX / self.step

        if self.mouseY > -1 and self.mouseY <= MOVE_HEIGHT:
            ret = self.PickMove(count)
            if ret is not None:
                self.main.moveList.SetItemState(ret[5], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            else:
                gap = self.PickGap(count)
                if gap is not None:
                    (m1, m2, begin, end) = gap
                    self.main.CreateMove(None, str(int(m1)), str(int(m2)))

        self.Refresh(False)

    def OnRightClick(self, event):
        pass

    def OnLeftUnclick(self, event):
        pass

    def OnRightUnclick(self, event):
        pass

    def OnMouseMove(self, event):
        self.mouseX = event.m_x
        self.mouseY = event.m_y
        self.Refresh(False)

    def OnMouseExit(self, event):
        self.mouseX = -1
        self.mouseY = -1
        self.Refresh(False)
