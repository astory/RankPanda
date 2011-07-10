#!/usr/bin/env python
#GUI Field: contains controls for the field, as well as rendering field thumbnails

import wx
#import CoreWrapper
import RankLocation
import Point

# Debug constants
DEBUG = False
DEBUG_RANK_COLOUR = wx.Colour(127, 63, 0)

# print constants
PRINT_WIDTH = 880.0
PRINT_HEIGHT = 425.0

# field constants
FIELD_LENGTH_STEPS = 176.0
FIELD_WIDTH_STEPS = 85.0# + 1.0/3.0
FIELD_RATIO = FIELD_LENGTH_STEPS/FIELD_WIDTH_STEPS

RANK_COLOUR = wx.Colour(0, 0, 0)
RANK_DRAW_COLOUR = wx.Colour(0, 0, 255)
SELECTED_RANK_COLOUR = wx.Colour(255, 0, 0)
RANK_START_COLOUR = wx.Colour(0, 255, 0)
RANK_END_COLOUR = wx.Colour(255, 0, 255)
RANK_CALCULATED_COLOUR = wx.Colour(127, 127, 0)

MINI_FIELD_SIZE = (176, 85)

# field line constants
FIELD_HORIZONTAL_SPACING_STEPS = 4.0
FIELD_VERTICAL_SPACING_STEPS = 4.0
FIELD_FRONT_HASH = 32.0
FIELD_BACK_HASH = FIELD_WIDTH_STEPS - 32.0

FIELD_LINE_YARDLINE_COLOUR = wx.Colour(63, 63, 63)
FIELD_LINE_MAJOR_COLOUR = wx.Colour(95, 95, 95)
FIELD_LINE_MINOR_COLOUR = wx.Colour(127, 127, 127)
FIELD_LINE_HASH_COLOUR = wx.Colour(63, 63, 63)

FIELD_LINE_YARDLINE_WIDTH = 3.0
FIELD_LINE_MAJOR_WIDTH = 2.0
FIELD_LINE_MINOR_WIDTH = 1.0
FIELD_LINE_HASH_WIDTH = 3.0

MINI_FIELD_LINE_YARDLINE_WIDTH = 1.0
MINI_FIELD_LINE_MAJOR_WIDTH = 1.0
MINI_FIELD_LINE_MINOR_WIDTH = 0.0
MINI_FIELD_LINE_HASH_WIDTH = 1.0

# field number constants
FIELD_NUMBER_FRONT_FRONT = 11.0
FIELD_NUMBER_FRONT_BACK = 14.0
FIELD_NUMBER_BACK_FRONT = FIELD_WIDTH_STEPS - FIELD_NUMBER_FRONT_FRONT
FIELD_NUMBER_BACK_BACK = FIELD_WIDTH_STEPS - FIELD_NUMBER_FRONT_BACK

FIELD_NUMBER_HEIGHT = FIELD_NUMBER_FRONT_BACK - FIELD_NUMBER_FRONT_FRONT
FIELD_NUMBER_SPACE = 0.05

FIELD_NUMBER_COLOUR = wx.Colour(63, 63, 63)

# drawing constants
ENDPOINT_RADIUS = 6.0
SPLINEPOINT_RADIUS = 4.0
LINE_WIDTH = 4.0
LINEPOINT_RADIUS = 2.0
ARROW_SEPARATION = 6.0
ARROW_LENGTH = 12.0

MINI_ENDPOINT_RADIUS = 3.0
MINI_SPLINEPOINT_RADIUS = 2.0
MINI_LINE_WIDTH = 2.0
MINI_LINEPOINT_RADIUS = 1.0
MINI_ARROW_SEPARATION = 3.0
MINI_ARROW_LENGTH = 6.0

NAME_COLOUR = wx.Colour(0, 127, 127)
SELECTED_NAME_COLOUR = wx.Colour(255, 127, 0)
NAME_CALCULATED_COLOUR = wx.Colour(127, 127, 0)

NAME_RECT_WIDTH = 10.0
NAME_RECT_HEIGHT = 20.0
NAME_DIST = 8.0
MINI_NAME_DIST = 2.5 # this one is not used as names are not drawn in the minifields

# mode constants
RANK_OFF = 0.0
RANK_ADD = 1.0
RANK_DRAG_POINT = 2.0
RANK_DRAG_LINE = 3.0
FTA_DRAG_WAYPOINT = 4.0

# DTP constants
DTP_START_COLOUR = wx.Colour(0, 255, 0)
DTP_END_COLOUR = wx.Colour(255, 0, 255)

# FTA constants
FTA_START_COLOUR = wx.Colour(0, 255, 0)
FTA_END_COLOUR = wx.Colour(255, 0, 255)

FTA_WAYPOINT_COLOUR = wx.Colour(0, 127, 127)

FTA_WAYPOINT_RADIUS = 6.0

FTA_WAYPOINT_NUMBER_COLOUR = wx.Colour(0, 127, 127)

FTA_NUMBER_RECT_WIDTH = 10.0
FTA_NUMBER_RECT_HEIGHT = 20.0
FTA_NUMBER_DIST = 15.0


class Field(wx.Panel):

    def __init__(self, parent, id, style, main):
        wx.Panel.__init__(self, parent, id, style = style)
        self.main = main
        self.fieldNumbersFont = wx.Font(72,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD, False, u'DejaVuSans')
        self.rankNameFont = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.BOLD, False, u'DejaVuSansMono')

        # init field numbers
        self.InitNumbers()

        # mode variables
        self.rankMode = RANK_OFF
        self.rankOldPos = (0, 0)

        self.firstPoint = (0, 0)
        self.secondPoint = (0, 0)

        self.fieldRect = None

        # init stuff
        self.OnResize(None)

# DEBUG
        if DEBUG:
            self.DisplayRanksOn = False
# DEBUG

    def OnPaint(self, event):
        self.Draw()
        fielddc = wx.PaintDC(self)
        fielddc.DrawBitmap(self.paintBitmap, 0, 0, False) # manual double-buffering since nothing else seems to work...

    def Draw(self):
        self.paintBitmap = wx.EmptyBitmap(*self.GetSizeTuple())
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))
        dc.SelectObject(self.paintBitmap)

        dc.SetBrush(wx.Brush('black'))
        dc.DrawRectangle(0, 0, *self.GetSizeTuple())

        dc.SetClippingRect(self.fieldRect)

        dc.SetBrush(wx.Brush('white'))
#       dc.DrawRectangleRect(self.fieldRect)
        dc.Clear()

        self.DrawFieldNumbers(self.fieldRect, dc)
        self.DrawFieldLines(self.fieldRect, dc)

        dc.DestroyClippingRegion()

        additional = self.main.core.GetAdditionalRanks()
        self.additionalStart = []
        self.additionalEnd = []

        for r in additional:
            if r[3] == 'Begin':
                self.additionalStart.append(r)
            elif r[3] == 'End':
                self.additionalEnd.append(r)

        self.DrawRanks(self.fieldRect, self.additionalStart, RANK_START_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.additionalEnd, RANK_END_COLOUR, dc)
        if self.main.animranks == None:
# not animating
            self.DrawRanks(self.fieldRect, self.main.core.GetCalculatedRanks(), RANK_CALCULATED_COLOUR, dc)
            self.DrawRanks(self.fieldRect, self.main.core.GetRanks(), RANK_COLOUR, dc)
            self.DrawRanks(self.fieldRect, self.main.core.GetSelectedRanks(), SELECTED_RANK_COLOUR, dc)

            self.DrawRankNames(self.fieldRect, self.main.core.GetCalculatedRanks(), NAME_CALCULATED_COLOUR, dc)
            self.DrawRankNames(self.fieldRect, self.main.core.GetRanks(), NAME_COLOUR, dc)
            self.DrawRankNames(self.fieldRect, self.main.core.GetSelectedRanks(), SELECTED_NAME_COLOUR, dc)

        else:
# is animating
            self.DrawRanks(self.fieldRect, self.main.animranks, RANK_COLOUR, dc)
            self.DrawRankNames(self.fieldRect, self.main.animranks, NAME_COLOUR, dc)

# draw initial point if user is adding a rank

        if self.rankMode == RANK_ADD:
            dc.SetPen(wx.Pen(RANK_DRAW_COLOUR, 0))
            dc.SetBrush(wx.Brush(RANK_DRAW_COLOUR))
            x1, y1 = self.firstPoint
            x2, y2 = self.secondPoint
            dc.DrawCircle(x1, y1, ENDPOINT_RADIUS)
            dc.DrawCircle(x2, y2, ENDPOINT_RADIUS)
            dc.SetPen(wx.Pen(RANK_DRAW_COLOUR, LINE_WIDTH))
            dc.DrawLine(x1, y1, x2, y2)

# DEBUG
        if DEBUG:
            if self.DisplayRanksOn:
                for l in self.main.core.DisplayRanks():
                    self.DrawLocation(self.fieldRect, l, dc, DEBUG_RANK_COLOUR)
# DEBUG

    def OnResize(self, event):
        self.fieldRect = self.AspectRatioRect(self.GetRect())
        self.ScaleNumbers(self.fieldRect)

        self.Refresh(False)

    def OnLeftClick(self, event):
        self.SetFocus()
        if not self.InFieldRect(event.m_x, event.m_y):
            return

        if event.ControlDown():
            self.rankMode = RANK_ADD
#           self.firstPoint = (event.m_x, event.m_y)
# snap to grid
            self.firstPoint = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
            self.secondPoint = self.firstPoint
        else:
            id = self.PickSpline(self.main.core.GetSelectedRanks(), event.m_x, event.m_y)
            if id is not None:
                self.rankMode = RANK_DRAG_POINT
                self.draggedPoint = id
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
                self.main.core.PointGrabbed(*id)
            else:
                id = self.PickRank(self.main.core.GetSelectedRanks(), event.m_x, event.m_y)
                if id is not None:
                    self.rankMode = RANK_DRAG_LINE
#                   self.rankPos = (event.m_x, event.m_y)
# snap to grid
                    self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
                    self.main.core.RanksGrabbed()
                else:
                    self.rankMode = RANK_OFF
                    id = self.PickSpline(self.main.core.GetRanks(), event.m_x, event.m_y)
                    if id is not None:
                        self.main.core.RankClicked(id[0], event.ShiftDown()) # deselect all ranks if shift isn't down
                    else:
                        id = self.PickRank(self.main.core.GetRanks(), event.m_x, event.m_y)
                        if id is not None:
                            self.main.core.RankClicked(id, event.ShiftDown()) # deselect all ranks if shift isn't down
                        elif not event.ShiftDown():
                            self.main.core.FieldClicked() # deselect all ranks if shift isn't down

        self.main.RefreshRankList()
        self.main.RefreshCommandList()

        # need to repaint field after a click
        self.Refresh(False)

    def OnRightClick(self, event):
        self.SetFocus()
        self.OnLeftUnclick(event) # simulate left release to avoid weirdness such as deleting a spline point while it is being dragged

        if self.rankMode != RANK_OFF:
            return

        spline = self.PickSpline(self.main.core.GetSelectedRanks(), event.m_x, event.m_y)
        if spline is not None:
            if event.ShiftDown():
                self.main.core.RankDeleteSpline(*spline)
            else:
                self.main.core.RankAddSpline(*spline)

        self.Refresh(False)
        self.main.RefreshCurrentMove()

    def OnLeftUnclick(self, event):
        if self.rankMode == RANK_ADD:
            x, y = self.firstPoint

#           firstPt = Point.Point(self.RX(self.fieldRect, x), self.RY(self.fieldRect, y))
#           secondPt = Point.Point(self.RX(self.fieldRect, event.m_x), self.RY(self.fieldRect, event.m_y))
# snap to grid
            firstPt = Point.Point(round(self.RX(self.fieldRect, x)), round(self.RY(self.fieldRect, y)))
            secondPt = Point.Point(round(self.RX(self.fieldRect, event.m_x)), round(self.RY(self.fieldRect, event.m_y)))

            self.main.core.RankDrawn([firstPt, secondPt])

        elif self.rankMode == RANK_DRAG_POINT:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            self.main.core.PointDragged(self.draggedPoint[0], self.draggedPoint[1], delta[0], delta[1])
            self.main.core.PointDropped(*self.draggedPoint)
            self.main.RefreshCommandList()
        elif self.rankMode == RANK_DRAG_LINE:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            self.main.core.RanksDragged(*delta)
            self.main.core.RanksDropped()
            self.main.RefreshCommandList()

        self.rankMode = RANK_OFF
        self.Refresh(False)
        self.main.RefreshCurrentMove()

    def OnRightUnclick(self, event):
        pass

    def OnMouseMove(self, event):
        if not self.InFieldRect(event.m_x, event.m_y):
            self.OnMouseExit(event)
        else:
            if self.rankMode == RANK_ADD:
#               self.secondPoint = (event.m_x, event.m_y)
# snap to grid
                self.secondPoint = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

            elif self.rankMode == RANK_DRAG_POINT:
                x, y = self.rankPos
#               delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                self.main.core.PointDragged(self.draggedPoint[0], self.draggedPoint[1], delta[0], delta[1])
            elif self.rankMode == RANK_DRAG_LINE:
                x, y = self.rankPos
#               delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                self.main.core.RanksDragged(*delta)

            self.Refresh(False)
# don't refresh every frame...
#           self.main.RefreshCurrentMove()

    def OnMouseExit(self, event):
        if self.rankMode == RANK_DRAG_POINT:
            self.main.core.PointDropped(*self.draggedPoint)
            self.main.RefreshCommandList()
        elif self.rankMode == RANK_DRAG_LINE:
            self.main.core.RanksDropped()
            self.main.RefreshCommandList()

        self.rankMode = RANK_OFF
        self.Refresh(False)
        self.main.RefreshCurrentMove()


    def RenderSet(self, ranks):
        bitmap = wx.EmptyBitmap(*MINI_FIELD_SIZE)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)

        rect = self.AspectRatioRect(wx.Rect(0, 0, *MINI_FIELD_SIZE))

        dc.SetBrush(wx.Brush('black'))
        dc.DrawRectangle(0, 0, *MINI_FIELD_SIZE)

# now, we make the background white
        dc.SetClippingRect(rect)

        dc.SetBrush(wx.Brush('white'))
        dc.DrawRectangleRect(rect)
#       dc.Clear() # we use the old line so that we get a thin black border

        self.DrawFieldLines(rect, dc, True)

        dc.DestroyClippingRegion()

        self.DrawRanks(self.fieldRect, self.main.core.GetCalculatedRanks(), RANK_CALCULATED_COLOUR, dc, True)
        self.DrawRanks(rect, ranks, RANK_COLOUR, dc, True)
#       self.DrawRankNames(self.fieldRect, self.main.core.GetCalculatedRanks(), NAME_CALCULATED_COLOUR, dc, True)
#       self.DrawRankNames(rect, ranks, NAME_COLOUR, dc, True)

        return bitmap

    def PrintBitmap(self):
        bitmap = wx.EmptyBitmap(PRINT_WIDTH, PRINT_HEIGHT)
        dc = wx.MemoryDC()
        dc.SelectObject(bitmap)

        dc.SetBrush(wx.Brush('white'))
        dc.Clear()

        tempRect = wx.Rect(0, 0, PRINT_WIDTH, PRINT_HEIGHT)

        self.ScaleNumbers(tempRect)
        self.DrawFieldNumbers(tempRect, dc)
        self.DrawFieldLines(tempRect, dc)

        dc.DestroyClippingRegion()

        self.DrawRanks(tempRect, self.main.core.GetRanks(), wx.Colour(0,0,0), dc)
        self.DrawRankNames(tempRect, self.main.core.GetRanks(), wx.Colour(0,0,0), dc)

        self.OnResize(None) # re-scale the numbers back to normal

        return bitmap

    def DrawFieldLines(self, rect, dc, mini = False):
        if mini:
            field_line_yardline_width = MINI_FIELD_LINE_YARDLINE_WIDTH
            field_line_hash_width = MINI_FIELD_LINE_HASH_WIDTH
            field_line_major_width = MINI_FIELD_LINE_MAJOR_WIDTH
            field_line_minor_width = MINI_FIELD_LINE_MINOR_WIDTH
        else:
            field_line_yardline_width = FIELD_LINE_YARDLINE_WIDTH
            field_line_hash_width = FIELD_LINE_HASH_WIDTH
            field_line_major_width = FIELD_LINE_MAJOR_WIDTH
            field_line_minor_width = FIELD_LINE_MINOR_WIDTH

        horizontalStep = self.T(rect, FIELD_HORIZONTAL_SPACING_STEPS)
        verticalStep = self.T(rect, FIELD_VERTICAL_SPACING_STEPS)

        horizontalStart = rect.GetX() + rect.GetWidth() / 2.0
        fieldBottom = rect.GetY()
        fieldTop = rect.GetY() + rect.GetHeight()

        verticalStart = rect.GetY() + rect.GetHeight() # we start from the front, and should DECREMENT y-pos per line
        fieldLeft = rect.GetX()
        fieldRight = rect.GetX() + rect.GetWidth()

        isMajor = False
        isAugmented = False

        for i in range(1, int((FIELD_LENGTH_STEPS / (2.0 * FIELD_HORIZONTAL_SPACING_STEPS)) + 1)):
            if isMajor:
                if isAugmented:
                    dc.SetPen(wx.Pen(FIELD_LINE_YARDLINE_COLOUR, field_line_yardline_width))
                    isAugmented = False
                else:
                    dc.SetPen(wx.Pen(FIELD_LINE_MAJOR_COLOUR, field_line_major_width))
                    isAugmented = True
                isMajor = False
            else:
                dc.SetPen(wx.Pen(FIELD_LINE_MINOR_COLOUR, field_line_minor_width))
                isMajor = True

            if dc.GetPen().GetWidth() > 0 :
                dc.DrawLine(horizontalStart + i * horizontalStep, fieldBottom, horizontalStart + i * horizontalStep, fieldTop)
                dc.DrawLine(horizontalStart - i * horizontalStep, fieldBottom, horizontalStart - i * horizontalStep, fieldTop)

        isMajor = True

        for i in range(0, int((FIELD_WIDTH_STEPS / FIELD_VERTICAL_SPACING_STEPS) + 1)):
            if isMajor:
                dc.SetPen(wx.Pen(FIELD_LINE_MAJOR_COLOUR, field_line_major_width))
                isMajor = False
            else:
                dc.SetPen(wx.Pen(FIELD_LINE_MINOR_COLOUR, field_line_minor_width))
                isMajor = True

            # Note: Need to SUBTRACT from vertical position to move toward the back of the field!
            if dc.GetPen().GetWidth() > 0 :
                dc.DrawLine(fieldLeft, verticalStart - i * verticalStep, fieldRight, verticalStart - i * verticalStep)

        dc.SetPen(wx.Pen(FIELD_LINE_YARDLINE_COLOUR, field_line_yardline_width))
        dc.DrawLine(horizontalStart, fieldBottom, horizontalStart, fieldTop)

        dc.SetPen(wx.Pen(FIELD_LINE_HASH_COLOUR, field_line_hash_width, wx.LONG_DASH))
        dc.DrawLine(fieldLeft, self.TY(rect, FIELD_FRONT_HASH), fieldRight, self.TY(rect, FIELD_FRONT_HASH))
        dc.DrawLine(fieldLeft, self.TY(rect, FIELD_BACK_HASH), fieldRight, self.TY(rect, FIELD_BACK_HASH))

    def InitNumbers(self):
        self.fixednumbers = []
        for i in range(10):
            dc = wx.MemoryDC()
            dc.SetFont(self.fieldNumbersFont)
            textdim = dc.GetTextExtent(str(i))
            textdim = (textdim[0], textdim[1])
            bitmap = wx.EmptyBitmap(*textdim)
            dc.SelectObject(bitmap)
            dc.SetBrush(wx.Brush('white'))
            dc.Clear()
            dc.SetTextForeground(FIELD_NUMBER_COLOUR)
            textrect = wx.Rect(0, 0, *textdim)
            dc.DrawImageLabel(str(i), wx.NullBitmap, textrect, wx.ALIGN_CENTRE)
            self.fixednumbers.append((bitmap.ConvertToImage(), textdim[0], textdim[1]))

    def ScaleNumbers(self, rect):
        self.numbers = []
        self.numbersheight = self.T(rect, FIELD_NUMBER_HEIGHT) + 2 # + self.T(rect, 10.0)
        for i in range(20): # we store 180-rotated images at index i + 10
            if i < 10:
                w = self.fixednumbers[i][1] * float(self.numbersheight) / self.fixednumbers[i][2]
                self.numbers.append((self.fixednumbers[i][0].Scale(w, self.numbersheight, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap(), w))
            else: # store the 180-rotated one
                w = self.fixednumbers[i - 10][1] * float(self.numbersheight) / self.fixednumbers[i - 10][2]
                self.numbers.append((self.fixednumbers[i - 10][0].Scale(w, self.numbersheight, wx.IMAGE_QUALITY_HIGH).Rotate90().Rotate90().ConvertToBitmap(), w))

    def DrawFieldNumbers(self, rect, dc, mini = False):
        horizontalStep = 2 * self.T(rect, FIELD_HORIZONTAL_SPACING_STEPS)

        horizontalStart = rect.GetX() + rect.GetWidth() / 2.0
        fieldBottom = rect.GetY()
        fieldTop = rect.GetY() + rect.GetHeight()

        fronty = self.TY(rect, FIELD_NUMBER_FRONT_FRONT) - self.numbersheight
        backy = self.TY(rect, FIELD_NUMBER_BACK_BACK) - self.numbersheight
        space = self.T(rect, FIELD_NUMBER_SPACE) + (self.numbers[5][1] / 2.0)

        dc.DrawBitmap(self.numbers[5][0], horizontalStart - self.numbers[5][1] - space, fronty, False)
        dc.DrawBitmap(self.numbers[0][0], horizontalStart + space, fronty, False)
        dc.DrawBitmap(self.numbers[10][0], horizontalStart - self.numbers[5][1] - space, backy, False)
        dc.DrawBitmap(self.numbers[15][0], horizontalStart + space, backy, False)

        number1 = 4
        number0 = 5

#       self.ScaleNumbers(rect) # since we only call this when drawing the field proper, we scale the images in OnResize to save computations

        for i in range(1, int((FIELD_LENGTH_STEPS / (4.0 * FIELD_HORIZONTAL_SPACING_STEPS)) + 1)):
                dc.DrawBitmap(self.numbers[number1][0], horizontalStart + i * horizontalStep - self.numbers[number1][1] - space, fronty, False)
                dc.DrawBitmap(self.numbers[number1][0], horizontalStart - i * horizontalStep - self.numbers[number1][1] - space, fronty, False)
                dc.DrawBitmap(self.numbers[number0][0], horizontalStart + i * horizontalStep + space, fronty, False)
                dc.DrawBitmap(self.numbers[number0][0], horizontalStart - i * horizontalStep + space, fronty, False)
                dc.DrawBitmap(self.numbers[number0 + 10][0], horizontalStart + i * horizontalStep - self.numbers[number1][1] - space, backy, False)
                dc.DrawBitmap(self.numbers[number0 + 10][0], horizontalStart - i * horizontalStep - self.numbers[number1][1] - space, backy, False)
                dc.DrawBitmap(self.numbers[number1 + 10][0], horizontalStart + i * horizontalStep + space, backy, False)
                dc.DrawBitmap(self.numbers[number1 + 10][0], horizontalStart - i * horizontalStep + space, backy, False)

                number0 -= 5
                if number0 < 0:
                    number0 += 10
                    number1 -= 1
                if number1 < 0:
                    break

    def DrawRanks(self, rect, ranks, colour, dc, mini = False):
        if ranks is not None:
            for r in ranks:
                self.DrawLocation(rect, r[2], dc, colour, mini)

    def DrawLocation(self, rect, loc, dc, colour, mini = False):
        if mini:
            endpoint_radius = MINI_ENDPOINT_RADIUS
            splinepoint_radius = MINI_SPLINEPOINT_RADIUS
            line_width = MINI_LINE_WIDTH
            linepoint_radius = MINI_LINEPOINT_RADIUS
            arrow_separation = MINI_ARROW_SEPARATION
            arrow_length = MINI_ARROW_LENGTH
        else:
            endpoint_radius = ENDPOINT_RADIUS
            splinepoint_radius = SPLINEPOINT_RADIUS
            line_width = LINE_WIDTH
            linepoint_radius = LINEPOINT_RADIUS
            arrow_separation = ARROW_SEPARATION
            arrow_length = ARROW_LENGTH

        if loc.IsStraight():
            pts = self.TList(rect, loc.GetListOfPoints())

            dc.SetPen(wx.Pen(colour, 0))
            dc.SetBrush(wx.Brush(colour))
            dc.DrawCircle(pts[0].x, pts[0].y, endpoint_radius)
            dc.DrawCircle(pts[1].x, pts[1].y, endpoint_radius)

            dc.SetPen(wx.Pen(colour, line_width))
            dc.DrawLine(pts[0].x, pts[0].y, pts[1].x, pts[1].y)

            dx = pts[1].x - pts[0].x
            dy = pts[1].y - pts[0].y
            dist = (dx ** 2 + dy ** 2) ** .5

            newpt = (pts[0].x + dx * arrow_length / dist, pts[0].y + dy * arrow_length / dist)

            arr = (-dy * arrow_separation / dist, dx * arrow_separation / dist)

            dc.SetPen(wx.Pen(colour, line_width))
            dc.DrawLine(pts[0].x, pts[0].y, newpt[0] + arr[0], newpt[1] + arr[1])
            dc.DrawLine(pts[0].x, pts[0].y, newpt[0] - arr[0], newpt[1] - arr[1])
        elif loc.curved:
            pts = self.TList(rect, loc.GetListOfPoints())
            plen = len(pts)

            dc.SetPen(wx.Pen(colour, 0))
            dc.SetBrush(wx.Brush(colour))
            dc.DrawCircle(pts[0].x, pts[0].y, endpoint_radius)
            dc.DrawCircle(pts[plen - 1].x, pts[plen - 1].y, endpoint_radius)

            for i in range(1, plen - 1):
                dc.DrawCircle(pts[i].x, pts[i].y, splinepoint_radius)

            pts = self.TList2(rect, loc.GetListOfDrawingPoints())
            for p in pts:
                dc.DrawCircle(p.x, p.y, linepoint_radius)

            dx = pts[1].x - pts[0].x
            dy = pts[1].y - pts[0].y
            dist = (dx ** 2 + dy ** 2) ** .5

            newpt = (pts[0].x + dx * arrow_length / dist, pts[0].y + dy * arrow_length / dist)

            arr = (-dy * arrow_separation / dist, dx * arrow_separation / dist)

            dc.SetPen(wx.Pen(colour, line_width))
            dc.DrawLine(pts[0].x, pts[0].y, newpt[0] + arr[0], newpt[1] + arr[1])
            dc.DrawLine(pts[0].x, pts[0].y, newpt[0] - arr[0], newpt[1] - arr[1])
        else: # connect-the-dots
            pts = self.TList(rect, loc.GetListOfPoints())
            plen = len(pts)

            dc.SetPen(wx.Pen(colour, 0))
            dc.SetBrush(wx.Brush(colour))
            dc.DrawCircle(pts[0].x, pts[0].y, endpoint_radius)
            dc.DrawCircle(pts[plen - 1].x, pts[plen - 1].y, endpoint_radius)

            for i in range(1, plen):
                dc.SetPen(wx.Pen(colour, 0))
                dc.DrawCircle(pts[i].x, pts[i].y, splinepoint_radius)
                dc.SetPen(wx.Pen(colour, line_width))
                dc.DrawLine(pts[i - 1].x, pts[i - 1].y, pts[i].x, pts[i].y)

            dx = pts[1].x - pts[0].x
            dy = pts[1].y - pts[0].y
            dist = (dx ** 2 + dy ** 2) ** .5

            newpt = (pts[0].x + dx * arrow_length / dist, pts[0].y + dy * arrow_length / dist)

            arr = (-dy * arrow_separation / dist, dx * arrow_separation / dist)

            dc.SetPen(wx.Pen(colour, line_width))
            dc.DrawLine(pts[0].x, pts[0].y, newpt[0] + arr[0], newpt[1] + arr[1])
            dc.DrawLine(pts[0].x, pts[0].y, newpt[0] - arr[0], newpt[1] - arr[1])

    def DrawRankNames(self, rect, ranks, colour, dc, mini = False):
        dc.SetTextForeground(colour)

        if mini:
            name_separation = MINI_NAME_DIST
        else:
            name_separation = NAME_DIST

        dc.SetFont(self.rankNameFont)
        for r in ranks:
            if r[-1]:
                inner_name_separation = name_separation
            else:
                inner_name_separation = -name_separation

            if r[1] is not None:
                pts = self.TList(rect, r[2].GetListOfPoints())
                if len(pts) % 2 == 1:
                    middlei = int((len(pts) - 1) / 2)
                    middle = pts[middlei]
                    middle1 = pts[middlei - 1]
                    middle2 = pts[middlei - 2]

                    (dx, dy) = (middle1.x - middle2.x, middle1.y - middle2.y)
                    dist = (dx ** 2 + dy ** 2) ** .5

                    newpt = (middle.x - dy * inner_name_separation / dist, middle.y + dx * inner_name_separation / dist)

                    textrect = wx.Rect(newpt[0] - NAME_RECT_WIDTH / 2, newpt[1] - NAME_RECT_HEIGHT / 2, NAME_RECT_WIDTH, NAME_RECT_HEIGHT)
                else:
                    middle1 = pts[int((len(pts) - 1) / 2)]
                    middle2 = pts[int((len(pts) + 1) / 2)]
                    middle = (round((middle1.x + middle2.x) / 2.0), round((middle1.y + middle2.y) / 2.0))

                    (dx, dy) = (middle1.x - middle2.x, middle1.y - middle2.y)
                    dist = (dx ** 2 + dy ** 2) ** .5

                    newpt = (middle[0] - dy * inner_name_separation / dist, middle[1] + dx * inner_name_separation / dist)

                    textrect = wx.Rect(newpt[0] - NAME_RECT_WIDTH / 2, newpt[1] - NAME_RECT_HEIGHT / 2, NAME_RECT_WIDTH, NAME_RECT_HEIGHT)

                dc.DrawImageLabel(r[1], wx.NullBitmap, textrect, wx.ALIGN_CENTRE)


# converts distance d in steps to pixels
    def T(self, rect, d):
        return d * rect.GetWidth() / FIELD_LENGTH_STEPS

#def TranslateXStepsToPixel(x): # converts x in steps to pixels
    def TX(self, rect, x):
        return x * rect.GetWidth() / FIELD_LENGTH_STEPS + rect.GetX()
#def TranslateYStepsToPixel(y): # converts y in steps to pixels
    def TY(self, rect, y):
        return (FIELD_WIDTH_STEPS - y) * rect.GetHeight() / FIELD_WIDTH_STEPS + rect.GetY()

    def TList(self, rect, l): # converts from steps to counts for an entire list of points
        l2 = []
        for i in l:
            l2.append(Point.Point(self.TX(rect, i.x), self.TY(rect, i.y)))
        return l2

    def TList2(self, rect, l): # converts from steps to counts for an entire list of lists of points
        l2 = []
        for i in l:
            for j in i:
                l2.append(Point.Point(self.TX(rect, j.x), self.TY(rect, j.y)))
        return l2

# converts distance d in pixels to steps
    def R(self, rect, d):
        return d * FIELD_LENGTH_STEPS / rect.GetWidth()

# converts x in pixels to steps
    def RX(self, rect, x):
            return (x - rect.GetX()) * FIELD_LENGTH_STEPS / rect.GetWidth()
# converts y in pixels to steps
    def RY(self, rect, y):
            return (rect.GetHeight() - y + rect.GetY()) * FIELD_WIDTH_STEPS / rect.GetHeight()


# returns rank id or None
    def PickRank(self, ranks, mx, my):
        x = self.RX(self.fieldRect, mx)
        y = self.RY(self.fieldRect, my)

        for r in ranks:
            loc = r[2]

            if loc.IsStraight():
                pts = loc.GetListOfPoints()
                if self.PickLine(((pts[0].x, pts[0].y), (pts[1].x, pts[1].y)), (x, y), self.R(self.fieldRect, LINE_WIDTH)):
                    return r[0]
            elif loc.curved:
                pts = loc.GetListOfDrawingPoints()
                for i in pts:
                    for j in i:
                        if self.PickCircle((j.x, j.y), (x, y), self.R(self.fieldRect, LINEPOINT_RADIUS)):
                            return r[0]
            else:
                pts = loc.GetListOfPoints()
                for i in range(0, len(pts) - 1):
                    if self.PickLine(((pts[i].x, pts[i].y), (pts[i + 1].x, pts[i + 1].y)), (x, y), self.R(self.fieldRect, LINE_WIDTH)):
                        return r[0]
        # failed to find a rank
        return None

# returns (rank id, spline pt index) or None
    def PickSpline(self, ranks, mx, my):
        x = self.RX(self.fieldRect, mx)
        y = self.RY(self.fieldRect, my)

        for r in ranks:
            loc = r[2]
            pts = loc.GetListOfPoints()

            if loc.IsStraight():
                if self.PickCircle((pts[0].x, pts[0].y), (x, y), self.R(self.fieldRect, ENDPOINT_RADIUS)):
                    return (r[0], 0)
                if self.PickCircle((pts[1].x, pts[1].y), (x, y), self.R(self.fieldRect, ENDPOINT_RADIUS)):
                    return (r[0], 1)
            else:
                plen = len(pts) - 1
                if self.PickCircle((pts[0].x, pts[0].y), (x, y), self.R(self.fieldRect, ENDPOINT_RADIUS)):
                    return (r[0], 0)
                if self.PickCircle((pts[plen].x, pts[plen].y), (x, y), self.R(self.fieldRect, ENDPOINT_RADIUS)):
                    return (r[0], plen)

                for i in range(1, plen):
                    if self.PickCircle((pts[i].x, pts[i].y), (x, y), self.R(self.fieldRect, SPLINEPOINT_RADIUS)):
                        return (r[0], i)
        # failed to find a pt
        return None

    def PickLine(self, endpts, pt, d):
        """ True if pt lies within distance d of the line defined by endpts """
        p1, p2 = endpts
        x1, y1 = p1
        x2, y2 = p2
        x, y = pt

        if x1 == x2 and y1 == y2:
            return False

        dist = ((x2 - x1)**2 + (y2 - y1)**2)**.5
        dx, dy = x2 - x1, y2 - y1
        dxt, dyt = x - x1, y - y1

        proj = (dxt * dx + dyt * dy) / float(dist)

        # if projection extends beyond endpoint:
        if proj > dist or proj < 0:
            return False
        else:
            x1p, y1p = x1 + (dx * proj / float(dist)), y1 + (dy * proj / float(dist))
            return (x - x1p)**2 + (y - y1p)**2 <= d**2

    def PickCircle(self, centre, pt, r):
        """ True if pt lies within distance r of centre """
        xc, yc = centre
        x, y = pt
        return (x - xc)**2 + (y - yc)**2 <= r**2

    def InFieldRect(self, x, y):
        """ True if pt lies within the field rect """
        leftBound = self.fieldRect.GetX()
        rightBound = leftBound + self.fieldRect.GetWidth()
        lowerBound = self.fieldRect.GetY()
        upperBound = lowerBound + self.fieldRect.GetHeight()
        return x >= leftBound and x <= rightBound and y >= lowerBound and y <= upperBound

    def AspectRatioRect(self, rect):
        newRect = wx.Rect(0, 0, rect.GetWidth(), rect.GetHeight())
        if float(newRect.GetWidth()) / newRect.GetHeight() < FIELD_RATIO:
            newHeight = newRect.GetWidth() / FIELD_RATIO
            diff = newRect.GetHeight() - newHeight
            newRect.SetY(diff / 2.0)
            newRect.SetHeight(newHeight)
        else:
            newWidth = newRect.GetHeight() * FIELD_RATIO
            diff = newRect.GetWidth() - newWidth
            newRect.SetX(diff / 2.0)
            newRect.SetWidth(newWidth)

        return newRect


class DTPField(Field):
    ''' Used for DTP Add dialog '''

    def __init__(self, parent, id, style, main, DTPranks):
        Field.__init__(self, parent, id, style, main)

        # init field numbers
        self.InitNumbers()

        self.DTPranks = DTPranks
        self.DTPstaticranks = []
        self.DTPeditranks = []

        for r in self.DTPranks:
            if r[3] == 'End':
                self.DTPeditranks.append(r)
            elif r[3] == 'Begin':
                self.DTPstaticranks.append(r)

        self.point = 0

    def Draw(self):
        self.paintBitmap = wx.EmptyBitmap(*self.GetSizeTuple())
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))
        dc.SelectObject(self.paintBitmap)

        dc.SetBrush(wx.Brush('black'))
        dc.DrawRectangle(0, 0, *self.GetSizeTuple())

        dc.SetClippingRect(self.fieldRect)

        dc.SetBrush(wx.Brush('white'))
#       dc.DrawRectangleRect(self.fieldRect)
        dc.Clear()

        self.DrawFieldNumbers(self.fieldRect, dc)
        self.DrawFieldLines(self.fieldRect, dc)

        dc.DestroyClippingRegion()

        self.DrawRanks(self.fieldRect, self.main.core.GetCalculatedRanks(), RANK_CALCULATED_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.main.core.GetRanks(), RANK_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.main.core.GetSelectedRanks(), SELECTED_RANK_COLOUR, dc)

        self.DrawRankNames(self.fieldRect, self.main.core.GetCalculatedRanks(), NAME_CALCULATED_COLOUR, dc)
        self.DrawRankNames(self.fieldRect, self.main.core.GetRanks(), NAME_COLOUR, dc)
        self.DrawRankNames(self.fieldRect, self.main.core.GetSelectedRanks(), SELECTED_NAME_COLOUR, dc)

        self.DrawRanks(self.fieldRect, self.DTPstaticranks, DTP_START_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.DTPeditranks, DTP_END_COLOUR, dc)

    def OnLeftClick(self, event):
        self.SetFocus()
        if not self.InFieldRect(event.m_x, event.m_y):
            return

        id = self.PickSpline(self.DTPeditranks, event.m_x, event.m_y)
        if id is not None:
            self.rankMode = RANK_DRAG_POINT
            self.draggedPoint = id
#           self.rankPos = (event.m_x, event.m_y)
# snap to grid
            self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
        else:
            id = self.PickRank(self.DTPeditranks, event.m_x, event.m_y)
            if id is not None:
                self.rankMode = RANK_DRAG_LINE
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
            else:
                self.rankMode = RANK_OFF

        # need to repaint field after a click
        self.Refresh(False)

    def OnRightClick(self, event):
        self.SetFocus()
        self.OnLeftUnclick(event) # simulate left release to avoid weirdness such as deleting a spline point while it is being dragged

        spline = self.PickSpline(self.DTPeditranks, event.m_x, event.m_y)
        if spline is not None:
            if event.ShiftDown():
                self.main.core.DTPDeletingSplinePoint(spline[1])
            else:
                self.main.core.DTPAddingSplinePoint(spline[1])

        self.Refresh(False)

    def OnLeftUnclick(self, event):
        if self.rankMode == RANK_DRAG_POINT:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            self.main.core.AdjustDTPPoint(self.draggedPoint[1], delta[0], delta[1])
        elif self.rankMode == RANK_DRAG_LINE:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            self.main.core.AdjustDTPWhole(*delta)

        self.rankMode = RANK_OFF
        self.Refresh(False)

    def OnRightUnclick(self, event):
        pass

    def OnMouseMove(self, event):
        if not self.InFieldRect(event.m_x, event.m_y):
            self.OnMouseExit(event)
        else:
            if self.rankMode == RANK_DRAG_POINT:
                x, y = self.rankPos
#               delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                self.main.core.AdjustDTPPoint(self.draggedPoint[1], delta[0], delta[1])
            elif self.rankMode == RANK_DRAG_LINE:
                x, y = self.rankPos
#               delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                self.main.core.AdjustDTPWhole(*delta)

            self.Refresh(False)
# don't refresh every frame...
#           self.main.RefreshCurrentMove()

    def OnMouseExit(self, event):
        self.rankMode = RANK_OFF
        self.Refresh(False)


class FTAField(Field):
    ''' Used for FTA Add dialog '''

    def __init__(self, parent, id, style, main, endpoint, FTAranks): # endpoint is True (1) or False (0)
        Field.__init__(self, parent, id, style, main)
        self.waypointFont = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.BOLD, False, u'DejaVuSansMono')

        # init field numbers
        self.InitNumbers()

        self.endpoint = endpoint
        self.FTAranks = FTAranks
        self.FTAstaticranks = []
        self.FTAwaypoints = []
        self.FTAeditranks = []

#       for r in self.FTAranks:
#           if r[3] == 'End':
#               self.FTAeditranks.append(r)
#           elif r[3] == 'Begin':
#               self.FTAstaticranks.append(r)

# we assume that FTAs will only ever be added for one rank at a time
        self.FTAeditranks.append(self.FTAranks[2])
        self.FTAwaypoints = self.FTAranks[1]
        self.FTAstaticranks.append(self.FTAranks[0])

        self.point = 0

    def Draw(self):
        self.paintBitmap = wx.EmptyBitmap(*self.GetSizeTuple())
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))
        dc.SelectObject(self.paintBitmap)

        dc.SetBrush(wx.Brush('black'))
        dc.DrawRectangle(0, 0, *self.GetSizeTuple())

        dc.SetClippingRect(self.fieldRect)

        dc.SetBrush(wx.Brush('white'))
#       dc.DrawRectangleRect(self.fieldRect)
        dc.Clear()

        self.DrawFieldNumbers(self.fieldRect, dc)
        self.DrawFieldLines(self.fieldRect, dc)

        dc.DestroyClippingRegion()

        self.DrawRanks(self.fieldRect, self.main.core.GetCalculatedRanks(), RANK_CALCULATED_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.main.core.GetRanks(), RANK_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.main.core.GetSelectedRanks(), SELECTED_RANK_COLOUR, dc)

        self.DrawRankNames(self.fieldRect, self.main.core.GetCalculatedRanks(), NAME_CALCULATED_COLOUR, dc)
        self.DrawRankNames(self.fieldRect, self.main.core.GetRanks(), NAME_COLOUR, dc)
        self.DrawRankNames(self.fieldRect, self.main.core.GetSelectedRanks(), SELECTED_NAME_COLOUR, dc)

        self.DrawRanks(self.fieldRect, self.FTAstaticranks, FTA_START_COLOUR, dc)
        self.DrawRanks(self.fieldRect, self.FTAeditranks, FTA_END_COLOUR, dc)
        self.DrawWaypoints(self.fieldRect, self.FTAwaypoints, FTA_WAYPOINT_COLOUR, FTA_WAYPOINT_NUMBER_COLOUR, dc)

    def OnLeftClick(self, event):
        self.SetFocus()
        if not self.InFieldRect(event.m_x, event.m_y):
            return

        if event.ControlDown():
#           self.firstPoint = (event.m_x, event.m_y)
# snap to grid
            point = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
            if self.endpoint:
                self.main.core.FTA1AddingWayPoint(self.RX(self.fieldRect, point[0]), self.RY(self.fieldRect, point[1]))
            else:
                self.main.core.FTA0AddingWayPoint(self.RX(self.fieldRect, point[0]), self.RY(self.fieldRect, point[1]))
        else:
            id = self.PickSpline(self.FTAeditranks, event.m_x, event.m_y)
            if id is not None:
                self.rankMode = RANK_DRAG_POINT
                self.draggedPoint = id
#           self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
            else:
                id = self.PickRank(self.FTAeditranks, event.m_x, event.m_y)
                if id is not None:
                    self.rankMode = RANK_DRAG_LINE
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                    self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
                else:
                    self.rankMode = RANK_OFF

                    i = 0
                    x = self.RX(self.fieldRect, event.m_x)
                    y = self.RY(self.fieldRect, event.m_y)
                    for w in self.FTAwaypoints:
                        if self.PickCircle((w.x, w.y), (x, y), self.R(self.fieldRect, FTA_WAYPOINT_RADIUS)):
                            self.rankMode = FTA_DRAG_WAYPOINT
                            self.draggedPoint = i
#                           self.rankPos = (event.m_x, event.m_y)
# snap to grid
                            self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))
                            break
                        i += 1

        # need to repaint field after a click
        self.Refresh(False)

    def OnRightClick(self, event):
        self.SetFocus()
        self.OnLeftUnclick(event) # simulate left release to avoid weirdness such as deleting a spline point while it is being dragged

        if event.ShiftDown():
            i = 0
            x = self.RX(self.fieldRect, event.m_x)
            y = self.RY(self.fieldRect, event.m_y)
            for w in self.FTAwaypoints:
                if self.PickCircle((w.x, w.y), (x, y), self.R(self.fieldRect, FTA_WAYPOINT_RADIUS)):
                    if self.endpoint:
                        self.main.core.FTA1DeleteWayPoint(i)
                        return
                    else:
                        self.main.core.FTA0DeleteWayPoint(i)
                        return
                i += 1

        spline = self.PickSpline(self.FTAeditranks, event.m_x, event.m_y)
        if spline is not None:
            if event.ShiftDown():
                if self.endpoint:
                    self.main.core.FTA1DeletingSplinePoint(spline[1])
                else:
                    self.main.core.FTA0DeletingSplinePoint(spline[1])
            else:
                if self.endpoint:
                    self.main.core.FTA1AddingSplinePoint(spline[1])
                else:
                    self.main.core.FTA0AddingSplinePoint(spline[1])

        self.Refresh(False)

    def OnLeftUnclick(self, event):
        if self.rankMode == RANK_DRAG_POINT:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            if self.endpoint:
                self.main.core.AdjustFTA1EndLocationPoint(self.draggedPoint[1], delta[0], delta[1])
            else:
                self.main.core.AdjustFTA0EndLocationPoint(self.draggedPoint[1], delta[0], delta[1])
        elif self.rankMode == RANK_DRAG_LINE:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            if self.endpoint:
                self.main.core.AdjustFTA1Whole(*delta)
            else:
                self.main.core.AdjustFTA0Whole(*delta)
        elif self.rankMode == FTA_DRAG_WAYPOINT:
            x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
            delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))

            if self.endpoint:
                self.main.core.FTA1AdjustWayPoint(self.draggedPoint, *delta)
            else:
                self.main.core.FTA0AdjustWayPoint(self.draggedPoint, *delta)

        self.rankMode = RANK_OFF
        self.Refresh(False)

    def OnRightUnclick(self, event):
        pass

    def OnMouseMove(self, event):
        if not self.InFieldRect(event.m_x, event.m_y):
            self.OnMouseExit(event)
        else:
            if self.rankMode == RANK_DRAG_POINT:
                x, y = self.rankPos
#               delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                if self.endpoint:
                    self.main.core.AdjustFTA1EndLocationPoint(self.draggedPoint[1], delta[0], delta[1])
                else:
                    self.main.core.AdjustFTA0EndLocationPoint(self.draggedPoint[1], delta[0], delta[1])
            elif self.rankMode == RANK_DRAG_LINE:
                x, y = self.rankPos
#               delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                if self.endpoint:
                    self.main.core.AdjustFTA1Whole(*delta)
                else:
                    self.main.core.AdjustFTA0Whole(*delta)
            elif self.rankMode == FTA_DRAG_WAYPOINT:
                x, y = self.rankPos
#           delta = (self.R(self.fieldRect, event.m_x - x), -self.R(self.fieldRect, event.m_y - y))
# snap to grid
                delta = (round(self.R(self.fieldRect, event.m_x - x)), round(-self.R(self.fieldRect, event.m_y - y)))
#               self.rankPos = (event.m_x, event.m_y)
# snap to grid
                self.rankPos = (self.TX(self.fieldRect, round(self.RX(self.fieldRect, event.m_x))), self.TY(self.fieldRect, round(self.RY(self.fieldRect, event.m_y))))

                if self.endpoint:
                    self.main.core.FTA1AdjustWayPoint(self.draggedPoint, *delta)
                else:
                    self.main.core.FTA0AdjustWayPoint(self.draggedPoint, *delta)

            self.Refresh(False)
# don't refresh every frame...
#           self.main.RefreshCurrentMove()

    def OnMouseExit(self, event):
        self.rankMode = RANK_OFF
        self.Refresh(False)

    def DrawWaypoints(self, rect, waypoints, colour, numbercolour, dc):
        dc.SetPen(wx.Pen(colour, 0))
        dc.SetBrush(wx.Brush(colour))
        dc.SetTextForeground(colour)
        i = 0

        dc.SetFont(self.waypointFont)
        for w in waypoints:
            (x, y) = (self.TX(self.fieldRect, w.x), self.TY(self.fieldRect, w.y))
            dc.DrawCircle(x, y, FTA_WAYPOINT_RADIUS)
            textrect = wx.Rect(x - FTA_NUMBER_RECT_WIDTH / 2, y - FTA_NUMBER_DIST - FTA_NUMBER_RECT_HEIGHT / 2, FTA_NUMBER_RECT_WIDTH, FTA_NUMBER_RECT_HEIGHT)
            dc.DrawImageLabel(str(i), wx.NullBitmap, textrect, wx.ALIGN_CENTRE)
            i += 1


class StatusField(Field):
    ''' Used for Ranks at Count dialog '''

    def __init__(self, parent, id, style, main, count):
        Field.__init__(self, parent, id, style, main)

        # init field numbers
        self.InitNumbers()

        self.count = count

    def Draw(self):
        self.paintBitmap = wx.EmptyBitmap(*self.GetSizeTuple())
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))
        dc.SelectObject(self.paintBitmap)

        dc.SetBrush(wx.Brush('black'))
        dc.DrawRectangle(0, 0, *self.GetSizeTuple())

        dc.SetClippingRect(self.fieldRect)

        dc.SetBrush(wx.Brush('white'))
#       dc.DrawRectangleRect(self.fieldRect)
        dc.Clear()

        self.DrawFieldNumbers(self.fieldRect, dc)
        self.DrawFieldLines(self.fieldRect, dc)

        dc.DestroyClippingRegion()

        self.DrawRanks(self.fieldRect, self.main.core.DisplayStatusAtCount(self.count), RANK_COLOUR, dc)

        self.DrawRankNames(self.fieldRect, self.main.core.DisplayStatusAtCount(self.count), NAME_COLOUR, dc)

    def OnLeftClick(self, event):
        pass

    def OnRightClick(self, event):
        pass

    def OnLeftUnclick(self, event):
        pass

    def OnRightUnclick(self, event):
        pass

    def OnMouseMove(self, event):
        pass

    def OnMouseExit(self, event):
        pass
