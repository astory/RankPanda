#!/usr/bin/env python
# GUI Dialogs: contains defs for all dialogs used by the GUI

import os
import wx
import GUIField

class SongCreationDialog(wx.Dialog):
    """ Dialog for getting data fields required to make a new song. Returns 0 on OK (get output in self.output), -1 on Cancel """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "New/Edit Song", size = (700, 375))

# begin layout code
        self.titleLabel = wx.StaticText(self, wx.ID_ANY, "Title: ")
        self.titleText = wx.TextCtrl(self, wx.ID_ANY, "", size = (480, 25))

        self.numberMeasuresLabel = wx.StaticText(self, wx.ID_ANY, "Total # Measures in Song: ")
        self.numberMeasuresText = wx.TextCtrl(self, wx.ID_ANY, "", size = (480, 25))

        self.titleSizer = wx.FlexGridSizer(2, 4, 10, 5)
        self.titleSizer.Add((15,1), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.titleSizer.Add(self.titleLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.titleSizer.Add(self.titleText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.titleSizer.Add((15,1), 0, wx.ALIGN_CENTRE)
        self.titleSizer.Add((15,1), 0, wx.ALIGN_CENTRE)
        self.titleSizer.Add(self.numberMeasuresLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.titleSizer.Add(self.numberMeasuresText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.titleSizer.Add((15,1), 0, wx.ALIGN_CENTRE)

        self.fromMeasureLabel = wx.StaticText(self, wx.ID_ANY, "From Measure: ")
        self.fromMeasureText = wx.TextCtrl(self, wx.ID_ANY, "1")
        self.countsPerMeasureLabel = wx.StaticText(self, wx.ID_ANY, "Counts/Measure: ")
        self.countsPerMeasureText = wx.TextCtrl(self, wx.ID_ANY, "4")
        self.countsPerStepLabel = wx.StaticText(self, wx.ID_ANY, "Counts/Step: ")
        self.countsPerStepText = wx.TextCtrl(self, wx.ID_ANY, "1")
        self.addButton = wx.Button(self, wx.ID_ANY, "Add >>")
        self.addButton.Bind(wx.EVT_BUTTON, self.OnAdd)

        self.inputLeftSizer = wx.FlexGridSizer(4, 2, 10, 5)
        self.inputLeftSizer.Add(self.fromMeasureLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputLeftSizer.Add(self.fromMeasureText, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputLeftSizer.Add(self.countsPerMeasureLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputLeftSizer.Add(self.countsPerMeasureText, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputLeftSizer.Add(self.countsPerStepLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputLeftSizer.Add(self.countsPerStepText, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputLeftSizer.Add((1,1))
        self.inputLeftSizer.Add(self.addButton, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)

        self.inputLeftBox = wx.StaticBox(self, wx.ID_ANY, "Set Count Information")
        self.inputLeftSizerOuter = wx.StaticBoxSizer(self.inputLeftBox, wx.VERTICAL)
        self.inputLeftSizerOuter.Add(self.inputLeftSizer, 1, wx.EXPAND)

        self.inputList = wx.ListCtrl(self, wx.ID_ANY, style = wx.LC_REPORT)
        self.inputList.InsertColumn(0, "Measure #")
        self.inputList.SetColumnWidth(0, 80)
        self.inputList.InsertColumn(1, "Counts/Measure")
        self.inputList.SetColumnWidth(1, 125)
        self.inputList.InsertColumn(2, "Counts/Step")
        self.inputList.SetColumnWidth(2, 100)
        self.inputList.Bind(wx.EVT_CHAR, self.OnKey)

        self.inputSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.inputSizer.Add((15,1), 0, wx.ALIGN_CENTRE)
        self.inputSizer.Add(self.inputLeftSizerOuter, 2, wx.EXPAND)
        self.inputSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.inputSizer.Add(self.inputList, 3, wx.EXPAND)
        self.inputSizer.Add((15,1), 0, wx.ALIGN_CENTRE)

        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((150,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.titleSizer, 0, wx.ALIGN_LEFT)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.inputSizer, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

        self.countsPerMeasureList = []
        self.countsPerStepList = []

    def OnKey(self, event):
        keyCode = event.GetUnicodeKey()
        if keyCode == 127: # delete
            while True: # loop thru all selected items
                index = self.inputList.GetNextItem(-1, state = wx.LIST_STATE_SELECTED)
                if index == -1:
                    break

                self.inputList.DeleteItem(index)
                self.countsPerMeasureList.pop(index)
                self.countsPerStepList.pop(index)

            self.Merge()

    def OnAdd(self, event):
        try:
            fromMeasure = int(self.fromMeasureText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for From Measure!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        try:
            countsPerMeasure = int(self.countsPerMeasureText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Counts/Measure!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        try:
            countsPerStep = float(self.countsPerStepText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Counts/Step!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        # search for correct insertion point in the list
        count = self.inputList.GetItemCount()
        i = 0
        while i < count:
            val = int(self.inputList.GetItemText(i))
            if val == fromMeasure: # found our measure
                self.countsPerMeasureList[i] = (fromMeasure, countsPerMeasure)
                self.countsPerStepList[i] = (fromMeasure, countsPerStep)
                self.inputList.SetStringItem(i, 1, str(countsPerMeasure))
                self.inputList.SetStringItem(i, 2, str(countsPerStep))

                self.Merge()
                return
            elif val > fromMeasure: # found insertion point
                numItems = i
                break
            i += 1
        else: # execute if loop condition becomes false
            numItems = count

        self.countsPerMeasureList.insert(numItems, (fromMeasure, countsPerMeasure))
        self.countsPerStepList.insert(numItems, (fromMeasure, countsPerStep))

        self.inputList.InsertStringItem(numItems, str(fromMeasure))
        self.inputList.SetStringItem(numItems, 1, str(countsPerMeasure))
        self.inputList.SetStringItem(numItems, 2, str(countsPerStep))

        self.Merge()

    def Merge(self):
        count = self.inputList.GetItemCount()
        i = 1
        currCountsPerMeasure = self.countsPerMeasureList[0][1]
        currStepsPerCount = self.countsPerStepList[0][1]
        while i < count:
            if self.countsPerMeasureList[i][1] == currCountsPerMeasure and self.countsPerStepList[i][1] == currStepsPerCount: # identical to previous one
                self.inputList.DeleteItem(i)
                self.countsPerMeasureList.pop(i)
                self.countsPerStepList.pop(i)
            else:
                currCountsPerMeasure = self.countsPerMeasureList[i][1]
                currStepsPerCount = self.countsPerStepList[i][1]
            i += 1

    def OnOK(self, event):
        try:
            numberMeasures = int(self.numberMeasuresText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Total # Measures in Song!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        if self.inputList.GetItemCount() == 0:
            d = wx.MessageDialog(self, "Need at least one entry!", "Input Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        if int(self.inputList.GetItemText(self.inputList.GetItemCount() - 1)) >= numberMeasures: # tried to assign to more measures than exist!
            d = wx.MessageDialog(self, "Exceeded Total # Measures in Song!", "Input Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        self.output = (self.titleText.GetValue(), numberMeasures, self.countsPerMeasureList, self.countsPerStepList)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)


class MoveCreationDialog(wx.Dialog):
    """ Dialog for getting data fields required to make a new move. Returns 0 on OK (get output in self.output), -1 on Cancel; returns move to import from or -1 if do not import in self.output2 """

    def __init__(self, parent, moveNames, startMeasure = "", endMeasure = ""):
#       wx.Dialog.__init__(self, parent, wx.ID_ANY, "New/Edit Move", size = (500, 300))
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "New Move", size = (500, 300))

# begin layout code
        self.nameLabel = wx.StaticText(self, wx.ID_ANY, "Name: ")
        self.nameText = wx.TextCtrl(self, wx.ID_ANY, "", size = (200, 25))

        self.startingMeasureLabel = wx.StaticText(self, wx.ID_ANY, "Starting Measure: ")
        self.startingMeasureText = wx.TextCtrl(self, wx.ID_ANY, startMeasure, size = (50, 25))

        self.endingMeasureLabel = wx.StaticText(self, wx.ID_ANY, "Ending Measure: ")
        self.endingMeasureText = wx.TextCtrl(self, wx.ID_ANY, endMeasure, size = (50, 25))

        self.inputSizer = wx.FlexGridSizer(3, 2, 10, 5)
        self.inputSizer.Add(self.nameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputSizer.Add(self.nameText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputSizer.Add(self.startingMeasureLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputSizer.Add(self.startingMeasureText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputSizer.Add(self.endingMeasureLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.inputSizer.Add(self.endingMeasureText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        self.importBox = wx.CheckBox(self, wx.ID_ANY, "Import ranks from move: ")
        self.importBox.Bind(wx.EVT_CHECKBOX, self.OnImportCheckbox)
        if len(moveNames) == 0:
            self.importBox.Disable()
        self.importList = wx.Choice(self, wx.ID_ANY, choices = moveNames)
        self.importList.SetSelection(len(moveNames) - 1)
        self.importList.Disable()

        self.importPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.importPanel.Add(self.importBox, 0, wx.ALIGN_CENTRE)
        self.importPanel.Add(self.importList, 1, wx.EXPAND)

        self.label1 = wx.StaticText(self, wx.ID_ANY, "(The move includes both the starting and ending measures)")
        self.label2 = wx.StaticText(self, wx.ID_ANY, "(Leave name blank for default name)")

        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((150,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.inputSizer, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,10), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.importPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.label1, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.label2, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnImportCheckbox(self, event):
        if event.IsChecked():
            self.importList.Enable()
        else:
            self.importList.Disable()

    def OnOK(self, event):
        try:
            startingMeasure = int(self.startingMeasureText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Starting Measure!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        try:
            endingMeasure = int(self.endingMeasureText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Ending Measure!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        name =  self.nameText.GetValue()
        if name == "":
            name = None

        self.output = (startingMeasure, endingMeasure, name)

        if self.importBox.IsChecked():
            self.output2 = self.importList.GetSelection()
        else:
            self.output2 = -1

        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)

 
class ImportRanksDialog(wx.Dialog):
    """ Dialog for importing ranks into current move. Returns 0 on OK (get output in self.output), -1 on Cancel; returns move to import from """

# we assume that moveNames has length > 0
    def __init__(self, parent, moveNames):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Import Ranks", size = (500, 150))

# begin layout code
        self.importText = wx.StaticText(self, wx.ID_ANY, "Import ranks from move: ")
        self.importList = wx.Choice(self, wx.ID_ANY, choices = moveNames)
        self.importList.SetSelection(0)

        self.importPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.importPanel.Add(self.importText, 0, wx.ALIGN_CENTRE)
        self.importPanel.Add(self.importList, 1, wx.EXPAND)

        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((150,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.importPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        self.output = self.importList.GetSelection()

        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)


class StatusAtCountDialog(wx.Dialog):
    """ Dialog for displaying the ranks at a given count """

    def __init__(self, parent, main, count):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Ranks at Count " + str(count), size = (800, 600), style = wx.CAPTION | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)

# begin layout code
        self.field = GUIField.StatusField(self, wx.ID_ANY, wx.BORDER_RAISED, main, count)
        self.field.Bind(wx.EVT_PAINT, self.field.OnPaint)
        self.field.Bind(wx.EVT_SIZE, self.field.OnResize)
        self.field.Bind(wx.EVT_LEFT_DOWN, self.field.OnLeftClick)
        self.field.Bind(wx.EVT_RIGHT_DOWN, self.field.OnRightClick)
        self.field.Bind(wx.EVT_LEFT_UP, self.field.OnLeftUnclick)
        self.field.Bind(wx.EVT_RIGHT_UP, self.field.OnRightUnclick)
        self.field.Bind(wx.EVT_MOTION, self.field.OnMouseMove)
        self.field.Bind(wx.EVT_LEAVE_WINDOW, self.field.OnMouseExit)
        self.field.Bind(wx.EVT_CHAR, self.OnKey)

        self.okButton = wx.Button(self, wx.ID_OK, "Close")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.field, 1, wx.EXPAND)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnKey(self, event):
        pass

    def OnOK(self, event):
        self.EndModal(0)


class AddDTPDialog(wx.Dialog):
    """ Dialog for adjusting a DTP when it is being added. There is no cancel option. """

    def __init__(self, parent, main, rankName, length, DTPranks):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add DTP", size = (800, 600), style = wx.CAPTION | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX | wx.RESIZE_BORDER)

        self.main = main

# begin layout code
        self.rankCaption = wx.StaticText(self, wx.ID_ANY, "Rank: ")
        self.rankText = wx.StaticText(self, wx.ID_ANY, rankName)

        self.lengthCaption = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.StaticText(self, wx.ID_ANY, str(length))

        self.startCaption = wx.StaticText(self, wx.ID_ANY, "DTP Start")
        self.startCaption.SetForegroundColour(GUIField.DTP_START_COLOUR)
        self.endCaption = wx.StaticText(self, wx.ID_ANY, "DTP End")
        self.endCaption.SetForegroundColour(GUIField.DTP_END_COLOUR)

        self.statusBar = wx.BoxSizer(wx.HORIZONTAL)
        self.statusBar.Add((1,1), 2, wx.EXPAND)
        self.statusBar.Add(self.rankCaption, 0, wx.ALIGN_RIGHT)
        self.statusBar.Add(self.rankText, 0, wx.ALIGN_LEFT)
        self.statusBar.Add((1,1), 2, wx.EXPAND)
        self.statusBar.Add(self.lengthCaption, 0, wx.ALIGN_RIGHT)
        self.statusBar.Add(self.lengthText, 0, wx.ALIGN_LEFT)
        self.statusBar.Add((1,1), 2, wx.EXPAND)
        self.statusBar.Add(self.startCaption, 0, wx.ALIGN_CENTRE)
        self.statusBar.Add((1,1), 1, wx.EXPAND)
        self.statusBar.Add(self.endCaption, 0, wx.ALIGN_CENTRE)
        self.statusBar.Add((1,1), 2, wx.EXPAND)

        self.field = GUIField.DTPField(self, wx.ID_ANY, wx.BORDER_RAISED, main, DTPranks)
        self.field.Bind(wx.EVT_PAINT, self.field.OnPaint)
        self.field.Bind(wx.EVT_SIZE, self.field.OnResize)
        self.field.Bind(wx.EVT_LEFT_DOWN, self.field.OnLeftClick)
        self.field.Bind(wx.EVT_RIGHT_DOWN, self.field.OnRightClick)
        self.field.Bind(wx.EVT_LEFT_UP, self.field.OnLeftUnclick)
        self.field.Bind(wx.EVT_RIGHT_UP, self.field.OnRightUnclick)
        self.field.Bind(wx.EVT_MOTION, self.field.OnMouseMove)
        self.field.Bind(wx.EVT_LEAVE_WINDOW, self.field.OnMouseExit)
        self.field.Bind(wx.EVT_CHAR, self.OnKey)

        self.okButton = wx.Button(self, wx.ID_OK, "Finish")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)

        self.straightButton = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap('icons/zigzagicon.png'))
        self.straightButton.SetDefault()
        self.straightButton.Bind(wx.EVT_BUTTON, self.OnStraight)

        self.curveButton = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap('icons/curveicon.png'))
        self.curveButton.SetDefault()
        self.curveButton.Bind(wx.EVT_BUTTON, self.OnCurve)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.straightButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.curveButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((150,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.statusBar, 0, wx.EXPAND)
        self.panelSizer.Add(self.field, 1, wx.EXPAND)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnKey(self, event):
        pass
#       if event.GetModifiers() == wx.MOD_ALT: # if alt is down, skip it so menu shortcuts work
#           event.Skip()

    def OnStraight(self, event):
        self.main.core.DTPSetStraight()

    def OnCurve(self, event):
        self.main.core.DTPSetCurved()

    def OnOK(self, event):
        self.EndModal(0)


class AddFTADialog(wx.Dialog):
    """ Dialog for adjusting an FTA when it is being added. There is no cancel option. """

    def __init__(self, parent, main, endpoint, rankName, length, FTAranks): # endpoint is True (1) or False (0)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add FTA", size = (800, 600), style = wx.CAPTION | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CLOSE_BOX | wx.RESIZE_BORDER)

        self.main = main
        self.endpoint = endpoint

# begin layout code
        self.rankCaption = wx.StaticText(self, wx.ID_ANY, "Rank: ")
        self.rankText = wx.StaticText(self, wx.ID_ANY, rankName)

        self.lengthCaption = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.StaticText(self, wx.ID_ANY, str(length))

        self.startCaption = wx.StaticText(self, wx.ID_ANY, "FTA Start")
        self.startCaption.SetForegroundColour(GUIField.FTA_START_COLOUR)
        self.endCaption = wx.StaticText(self, wx.ID_ANY, "FTA End")
        self.endCaption.SetForegroundColour(GUIField.FTA_END_COLOUR)

        self.statusBar = wx.BoxSizer(wx.HORIZONTAL)
        self.statusBar.Add((1,1), 2, wx.EXPAND)
        self.statusBar.Add(self.rankCaption, 0, wx.ALIGN_RIGHT)
        self.statusBar.Add(self.rankText, 0, wx.ALIGN_LEFT)
        self.statusBar.Add((1,1), 2, wx.EXPAND)
        self.statusBar.Add(self.lengthCaption, 0, wx.ALIGN_RIGHT)
        self.statusBar.Add(self.lengthText, 0, wx.ALIGN_LEFT)
        self.statusBar.Add((1,1), 2, wx.EXPAND)
        self.statusBar.Add(self.startCaption, 0, wx.ALIGN_CENTRE)
        self.statusBar.Add((1,1), 1, wx.EXPAND)
        self.statusBar.Add(self.endCaption, 0, wx.ALIGN_CENTRE)
        self.statusBar.Add((1,1), 2, wx.EXPAND)

        self.field = GUIField.FTAField(self, wx.ID_ANY, wx.BORDER_RAISED, main, endpoint, FTAranks)
        self.field.Bind(wx.EVT_PAINT, self.field.OnPaint)
        self.field.Bind(wx.EVT_SIZE, self.field.OnResize)
        self.field.Bind(wx.EVT_LEFT_DOWN, self.field.OnLeftClick)
        self.field.Bind(wx.EVT_RIGHT_DOWN, self.field.OnRightClick)
        self.field.Bind(wx.EVT_LEFT_UP, self.field.OnLeftUnclick)
        self.field.Bind(wx.EVT_RIGHT_UP, self.field.OnRightUnclick)
        self.field.Bind(wx.EVT_MOTION, self.field.OnMouseMove)
        self.field.Bind(wx.EVT_LEAVE_WINDOW, self.field.OnMouseExit)
        self.field.Bind(wx.EVT_CHAR, self.OnKey)

        self.okButton = wx.Button(self, wx.ID_OK, "Finish")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)

        self.straightButton = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap('icons/zigzagicon.png'))
        self.straightButton.SetDefault()
        self.straightButton.Bind(wx.EVT_BUTTON, self.OnStraight)

        self.curveButton = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap('icons/curveicon.png'))
        self.curveButton.SetDefault()
        self.curveButton.Bind(wx.EVT_BUTTON, self.OnCurve)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.straightButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.curveButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((150,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.statusBar, 0, wx.EXPAND)
        self.panelSizer.Add(self.field, 1, wx.EXPAND)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnKey(self, event):
        pass
#       if event.GetModifiers() == wx.MOD_ALT: # if alt is down, skip it so menu shortcuts work
#           event.Skip()

    def OnStraight(self, event):
        if self.endpoint:
            self.main.core.FTA1SetStraight()
        else:
            self.main.core.FTA0SetStraight()

    def OnCurve(self, event):
        if self.endpoint:
            self.main.core.FTA1SetCurved()
        else:
            self.main.core.FTA0SetCurved()

    def OnOK(self, event):
        self.EndModal(0)


class RankUnicodeNameDialog(wx.Dialog):
    """ Dialog for getting unicode character for rank name. Returns unicode integer in base 10, or -1 on cancel """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Rank Unicode Name", size = (400, 275))

# begin layout code
        self.instructions = wx.StaticText(self, wx.ID_ANY, "Enter unicode character directly into box,\nor pick a base and enter unicode value.")

        self.charLabel = wx.StaticText(self, wx.ID_ANY, "Unicode character: ")
        self.charText = wx.TextCtrl(self, wx.ID_ANY, "", size = (25, 25))
        self.charText.SetMaxLength(1)

        self.charPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.charPanel.Add(self.charLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.charPanel.Add(self.charText, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        self.valueLabel = wx.StaticText(self, wx.ID_ANY, "Unicode value: ")
        self.valueText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.enterButton = wx.Button(self, wx.ID_ANY, "Enter")
        self.enterButton.Bind(wx.EVT_BUTTON, self.OnEnter)

        self.valuePanel = wx.BoxSizer(wx.HORIZONTAL)
        self.valuePanel.Add(self.valueLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.valuePanel.Add(self.valueText, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.valuePanel.Add(self.enterButton, 0, wx.ALIGN_CENTRE)

        self.baseChoices = ['2', '8', '10', '16']
        self.baseChoicesValues = [2, 8, 10, 16]
        self.baseRadioBox = wx.RadioBox(self, wx.ID_ANY, "Base", choices = self.baseChoices, majorDimension = 4, style = wx.RA_SPECIFY_COLS)
        self.baseRadioBox.SetSelection(2) # base 10 selected by default

        self.inputPanel = wx.BoxSizer(wx.VERTICAL)
        self.inputPanel.Add(self.valuePanel, 0, wx.ALIGN_CENTRE)
        self.inputPanel.Add(self.baseRadioBox, 0, wx.ALIGN_CENTRE)

        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((150,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.instructions, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.charPanel, 0, wx.ALIGN_CENTER)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.inputPanel, 0, wx.ALIGN_CENTER)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnEnter(self, event):
        base = self.baseChoicesValues[self.baseRadioBox.GetSelection()]

        try:
            code = int(self.valueText.GetValue(), base)
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for unicode value!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        self.charText.SetValue(unichr(code))

    def OnOK(self, event):
        char = self.charText.GetValue()

        if char == "":
            d = wx.MessageDialog(self, "No unicode character selected!", "Input Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        self.EndModal(ord(char[0]))

    def OnCancel(self, event):
        self.EndModal(-1)


class AddWaypointDialog(wx.Dialog):
    """ Dialog for getting required info for adding a waypoint  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add Waypoint", size = (400, 250))

# begin layout code
   
        self.measureLabel = wx.StaticText(self, wx.ID_ANY, "Measure: ")
        self.measureText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))

        self.measureSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.measureSizer.Add(self.measureLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.measureSizer.Add(self.measureText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        self.minLabel = wx.StaticText(self, wx.ID_ANY, "min: ")
        self.minText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.secLabel = wx.StaticText(self, wx.ID_ANY, "sec: ")
        self.secText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.msecLabel = wx.StaticText(self, wx.ID_ANY, "ms:  ")
        self.msecText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))

        self.minSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.minSizer.Add(self.minLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.minSizer.Add(self.minText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.secSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.secSizer.Add(self.secLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.secSizer.Add(self.secText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.msecSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.msecSizer.Add(self.msecLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.msecSizer.Add(self.msecText, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)

        self.timeBox = wx.StaticBox(self, wx.ID_ANY, "Time")
        self.timeSizer = wx.StaticBoxSizer(self.timeBox, wx.VERTICAL)
        self.timeSizer.Add(self.minSizer, 0, wx.ALIGN_CENTRE)
        self.timeSizer.Add(self.secSizer, 0, wx.ALIGN_CENTRE)
        self.timeSizer.Add(self.msecSizer, 0, wx.ALIGN_CENTRE)
       
        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.measureSizer, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,5), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.timeSizer, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            measure = int(self.measureText.GetValue())
            if measure < 0:
                raise Exception # so we trigger the dialog below
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Measure!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        try:
            min = int(self.minText.GetValue())
            if min < 0:
                raise Exception # so we trigger the dialog below
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Minutes!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        try:
            sec = int(self.secText.GetValue())
            if sec < 0:
                raise Exception # so we trigger the dialog below
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Seconds!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        try:
            msec = int(self.msecText.GetValue())
            if msec < 0:
                raise Exception # so we trigger the dialog below
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Milliseconds!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        time = 60000 * min + 1000 * sec + msec

        self.output = (measure, time)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)

class AddText(wx.Dialog):
    """ Dialog for adding text in a wx.TextCtrl  """

    def __init__(self, parent, text, title):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size = (400, 300))

# begin layout code
        self.textCtrl = wx.TextCtrl(self, wx.ID_OK, "", style = wx.TE_MULTILINE)
        self.textCtrl.SetValue(text)
		
        self.okButton = wx.Button(self, wx.ID_OK, "OK")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.textCtrl, 1, wx.EXPAND)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        self.output = self.textCtrl.GetValue()
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)		

		
		
		
class GateTurnDialog(wx.Dialog):
    """ Dialog for specifying Gate Turn details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add Gate Turn Command", size = (400, 275))

# begin layout code
        self.directionPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.directionChoices = ['Clockwise', 'Counter-clockwise']
        self.directionChoicesValues = [0, 1]
        self.directionRadioBox = wx.RadioBox(self, wx.ID_ANY, "Direction", choices = self.directionChoices, majorDimension = 2, style = wx.RA_SPECIFY_COLS)
        self.directionRadioBox.SetSelection(0) # clockwise selected by default
        self.directionPanel.Add(self.directionRadioBox, 1)
		
        self.pivotPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.pivotChoices = ['At arrow               ', 'At point']
        self.pivotChoicesValues = [0, 1]
        self.pivotRadioBox = wx.RadioBox(self, wx.ID_ANY, "Non-Pivot Point", choices = self.pivotChoices, majorDimension = 2, style = wx.RA_SPECIFY_COLS)
        self.pivotRadioBox.SetSelection(0) # arrow selected by default
        self.pivotPanel.Add(self.pivotRadioBox, 1)	
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Add Command")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.wholePanel = wx.BoxSizer(wx.HORIZONTAL)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_LEFT)
        self.panelSizer.Add(self.directionPanel, 0, wx.ALIGN_LEFT)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_LEFT)
        self.panelSizer.Add(self.pivotPanel, 0, wx.ALIGN_LEFT)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_LEFT)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_LEFT)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_LEFT)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_LEFT)
		
        self.wholePanel.Add((100,25), 0, wx.ALIGN_LEFT)
        self.wholePanel.Add(self.panelSizer)

        self.SetSizer(self.wholePanel)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return   
        self.output = (self.directionChoicesValues[self.directionRadioBox.GetSelection()], self.pivotChoicesValues[self.pivotRadioBox.GetSelection()] , length)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)		
		
		




class PinwheelDialog(wx.Dialog):
    """ Dialog for specifying Pinwheel details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add Pinwheel Command", size = (400, 225))

# begin layout code
        self.directionPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.directionChoices = ['Clockwise', 'Counter-clockwise']
        self.directionChoicesValues = [0, 1]
        self.directionRadioBox = wx.RadioBox(self, wx.ID_ANY, "Direction", choices = self.directionChoices, majorDimension = 2, style = wx.RA_SPECIFY_COLS)
        self.directionRadioBox.SetSelection(0) # clockwise selected by default
        self.directionPanel.Add(self.directionRadioBox, 1)
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Add Command")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.directionPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return   
        self.output = (self.directionChoicesValues[self.directionRadioBox.GetSelection()], length)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	





class FTADialog(wx.Dialog):
    """ Dialog for specifying FTA details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add FTA Command", size = (400, 225))

# begin layout code
        self.pivotPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.pivotChoices = ['At arrow       ', 'At point']
        self.pivotChoicesValues = [0, 1]
        self.pivotRadioBox = wx.RadioBox(self, wx.ID_ANY, "Leading Point", choices = self.pivotChoices, majorDimension = 2, style = wx.RA_SPECIFY_COLS)
        self.pivotRadioBox.SetSelection(0) # arrow selected by default
        self.pivotPanel.Add(self.pivotRadioBox, 1)	
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Add Command")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.pivotPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return   
        self.output = (self.pivotChoicesValues[self.pivotRadioBox.GetSelection()] , length)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	



		


class ExpandDialog(wx.Dialog):
    """ Dialog for specifying Expand details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add Expand Command", size = (400, 225))

# begin layout code
        self.pivotPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.pivotChoices = ['At arrow       ', 'At point']
        self.pivotChoicesValues = [0, 1]
        self.pivotRadioBox = wx.RadioBox(self, wx.ID_ANY, "Moving Point", choices = self.pivotChoices, majorDimension = 2, style = wx.RA_SPECIFY_COLS)
        self.pivotRadioBox.SetSelection(0) # arrow selected by default
        self.pivotPanel.Add(self.pivotRadioBox, 1)	
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Add Command")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.pivotPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return   
        self.output = (self.pivotChoicesValues[self.pivotRadioBox.GetSelection()] , length)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	

		
		


class CondenseDialog(wx.Dialog):
    """ Dialog for specifying Expand details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add Condense Command", size = (400, 225))

# begin layout code
        self.pivotPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.pivotChoices = ['At arrow       ', 'At point']
        self.pivotChoicesValues = [0, 1]
        self.pivotRadioBox = wx.RadioBox(self, wx.ID_ANY, "Moving Point", choices = self.pivotChoices, majorDimension = 2, style = wx.RA_SPECIFY_COLS)
        self.pivotRadioBox.SetSelection(0) # arrow selected by default
        self.pivotPanel.Add(self.pivotRadioBox, 1)	
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Add Command")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.pivotPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return   
        self.output = (self.pivotChoicesValues[self.pivotRadioBox.GetSelection()] , length)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	





class DTPDialog(wx.Dialog):
    """ Dialog for specifying DTP details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add DTP Command", size = (400, 150))

# begin layout code
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Continue")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return        
        self.output = length
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	


	


class CurveDialog(wx.Dialog):
    """ Dialog for specifying Curve details.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Add Curve Command", size = (400, 150))

# begin layout code
	
        self.lengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.lengthLabel = wx.StaticText(self, wx.ID_ANY, "Length: ")
        self.lengthText = wx.TextCtrl(self, wx.ID_ANY, "", size = (100, 25))
        self.lengthPanel.Add(self.lengthLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.lengthPanel.Add(self.lengthText)

		
        self.okButton = wx.Button(self, wx.ID_OK, "Continue")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.lengthPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            length = int(self.lengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (length < 0):
            d = wx.MessageDialog(self, "Invalid entry for Length!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return        
        self.output = length
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	
	
class ExportPDFDialog(wx.Dialog):
    """ Dialog for Exporting to PDF  """

    def __init__(self, parent, moveNames):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Export to PDF", size = (600, 300))

# begin layout code


        self.moveNames = moveNames

        self.columnPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.columnLabel = wx.StaticText(self, wx.ID_ANY, "# of Columns for Rank/Commands: ")
        self.columnPanel.Add(self.columnLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.columnInput = wx.SpinCtrl(self, wx.ID_ANY, size=(100,20), min = 1, max = 10, initial = 3)
        self.columnPanel.Add(self.columnInput)
        self.forLabel = wx.StaticText(self, wx.ID_ANY, " for ")
        self.columnPanel.Add(self.forLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)

        self.importList = wx.Choice(self, wx.ID_ANY, choices = moveNames)
        self.importList.SetSelection(len(moveNames) - 1)
        self.columnPanel.Add(self.importList)

        self.columnList = wx.ListCtrl(self, wx.ID_ANY, style = wx.LC_REPORT, size=(400,100))
        self.columnList.InsertColumn(0, "Move #")
        self.columnList.InsertColumn(1, "# of Columns")
        self.columnList.SetColumnWidth(0, 247)
        self.columnList.SetColumnWidth(1, 147)


        for i in range(len(moveNames)):
            self.columnList.InsertStringItem(i, moveNames[i])
            self.columnList.SetStringItem(i, 1, "3")


        self.columnInput.Bind(wx.EVT_SPINCTRL, self.OnNumChange)
        self.importList.Bind(wx.EVT_CHOICE, self.OnSelectionChange)

        self.fontPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.fontLabel = wx.StaticText(self, wx.ID_ANY, "Font Size: ")
        self.fontText = wx.TextCtrl(self, wx.ID_ANY, "", size = (60, 20))
        self.fontPanel.Add(self.fontLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.fontPanel.Add(self.fontText)

        self.okButton = wx.Button(self, wx.ID_OK, "Export to PDF")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.columnList, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.columnPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.fontPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnNumChange(self, event):
        self.columnList.SetStringItem(self.importList.GetSelection(), 0, self.moveNames[self.importList.GetSelection()])
        self.columnList.SetStringItem(self.importList.GetSelection(), 1, str(self.columnInput.GetValue()))

    def OnSelectionChange(self, event):
        self.columnInput.SetValue(int(self.columnList.GetItem(self.importList.GetSelection(), 1).GetText()))

    def OnOK(self, event):
        try:
            fontsize = int(self.fontText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Font Size!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        try:
            columns = int(self.columnInput.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for # of Columns!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (fontsize < 1):
            d = wx.MessageDialog(self, "Invalid entry for Font Size!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        #min 13 characters per column
        if (13>((1080/fontsize)/columns)):
            d = wx.MessageDialog(self, "Incompatible Font Size and # of Columns!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        self.columnCount = []
        for i in range(len(self.moveNames)):
            self.columnCount.append(int(self.columnList.GetItem(i, 1).GetText()))

        self.output = (self.moveNames, self.columnCount)
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)

        
#Lauren change
class ExportIndDialog(wx.Dialog):
    """ Dialog for exporting individual rank command lists.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Export Individual Ranks to PDF", size = (400, 200))

# begin layout code

        self.fontPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.fontLabel = wx.StaticText(self, wx.ID_ANY, "Font Size: ")
        self.fontText = wx.TextCtrl(self, wx.ID_ANY, "", size = (60, 25))
        self.fontPanel.Add(self.fontLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.fontPanel.Add(self.fontText)

		
        self.columnPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.columnLabel = wx.StaticText(self, wx.ID_ANY, "# of Columns per Page: ")
        self.columnPanel.Add(self.columnLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.columnInput = wx.SpinCtrl(self, wx.ID_ANY, size=(100,25), min = 1, max = 10, initial = 3)		
        self.columnPanel.Add(self.columnInput)
		
        self.okButton = wx.Button(self, wx.ID_OK, "Export to PDF")
        self.okButton.SetDefault()
        self.okButton.Bind(wx.EVT_BUTTON, self.OnOK)
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.cancelButton.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)
        self.buttonSizer.Add(self.okButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((50,1), 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE)
        self.buttonSizer.Add((1,1), 1, wx.EXPAND)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.fontPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.columnPanel, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.buttonSizer, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)
# end layout code

    def OnOK(self, event):
        try:
            fontsize = int(self.fontText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Font Size!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        try:
            columns = int(self.columnInput.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for # of Columns!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        if (fontsize < 1):
            d = wx.MessageDialog(self, "Invalid entry for Font Size!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        #min 13 characters per column
        if (13>((1080/fontsize)/columns)):
            d = wx.MessageDialog(self, "Incompatible Font Size and # of Columns!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return
        self.EndModal(0)

    def OnCancel(self, event):
        self.EndModal(-1)	
        
        
class ProgramOptionsDialog(wx.Dialog):
    """ Dialog for options upon opening the program.  """

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Welcome to RankPanda!", size = (180, 180))

# begin layout code

        self.newButton = wx.Button(self, wx.ID_ANY, "New")
        self.newButton.SetDefault()
        self.newButton.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(0))
       
        self.openButton = wx.Button(self, wx.ID_ANY, "Open")
        self.openButton.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(1))

        self.exitButton = wx.Button(self, wx.ID_ANY, "Exit")
        self.exitButton.Bind(wx.EVT_BUTTON, lambda event: self.EndModal(-1))

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.newButton, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.openButton, 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add((1,25), 0, wx.ALIGN_CENTRE)
        self.panelSizer.Add(self.exitButton, 0, wx.ALIGN_CENTRE)

        self.SetSizer(self.panelSizer)

#app = wx.App()
#s = AddFTADialog(None, None, True, " ", 0, [])
#ret = s.ShowModal()
#s.Destroy()
#app.MainLoop()
