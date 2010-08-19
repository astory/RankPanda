#!/usr/bin/env python
# GUI Main: RankPanda main window

import os
import wx
import GUIDialogs
import GUIField
import GUIRankList
import GUITimeBar
import CoreWrapper
#import RankLocation
#import Point
import Printer

DEBUG = False
# Idea: instead of displaying * for locked rank, how about use different colour?

default_size = (800,600)

ID_EXIT = 0
ID_NEW = 1
ID_OPEN = 2
ID_CLOSE = 3
ID_SAVE = 4
ID_SAVE_AS = 5
ID_HELP = 6
ID_ABOUT = 7
ID_UNDO = 8
ID_REDO = 9
ID_CUT = 10
ID_COPY = 11
ID_PASTE = 12
ID_FIND = 13
ID_FIND_REPLACE = 14
ID_EXPORT_PDF = 15
ID_SETTINGS = 16
ID_FIELD = 17
ID_COMMAND_LIST = 18
ID_COMMAND_BUTTON_MOVE_UP = 19
ID_COMMAND_BUTTON_MOVE_DOWN = 20
ID_COMMAND_BUTTON_SPLIT = 21
ID_COMMAND_BUTTON_MERGE = 22
ID_COMMAND_BUTTON_DELETE = 23
ID_MOVE_LIST = 24
ID_MOVE_NEW = 25
ID_MOVE_IMPORT = 26
ID_MOVE_SPLIT = 27
ID_MOVE_MERGE = 28
ID_MOVE_SHIFT = 29
ID_ANIM_TIMER = 30
ID_EDIT = 31
ID_EXPORT_IND = 32
ID_MOVE_TEXT = 33
ID_MOVE_TEXT_OVERWRITE = 34

class MainWindow(wx.Frame):
    """ Main Window; derived from wx.Frame """

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, wx.ID_ANY, "Rank Panda", size = default_size)

        self.SetFont(wx.Font(10,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL, faceName="DejaVu Sans"))


# DEBUG
        if DEBUG:
            self.core = CoreWrapper.CoreWrapper("Debug", 128, [(1, 4)], [(1, 1)])
            self.filename = None
        else:
            d = GUIDialogs.ProgramOptionsDialog(self)
            while True:
                start = d.ShowModal()

                if start == 0: # user requested new
                    self.filename = None
                    f = GUIDialogs.SongCreationDialog(self)
                    if f.ShowModal() == 0:
                        try:
                            self.core = CoreWrapper.CoreWrapper(*f.output)
                            break
                        except NameError as exception:
                            e = wx.MessageDialog(self, "Exception thrown while creating song!\nRank Panda will now close", "Song Creation Exception", wx.OK)
                            e.ShowModal()
                            e.Destroy()
                            self.Close(True) # exit since we couldn't create a song
                            return
                    else:
                        pass
                    f.Destroy()
                elif start == 1: # user requested open
                    loop = True
                    loopOuter = True
                    self.core = CoreWrapper.CoreWrapper("Dummy", 10, [(1, 4)], [(1, 1)])

                    while loop:
                        self.dirname = ''
                        e = wx.FileDialog(self, "Open File", self.dirname, "", "*.panda", wx.OPEN)
                        if e.ShowModal() == wx.ID_OK:
                            self.filename = os.path.join(e.GetDirectory(), e.GetFilename())
                            if self.core.Load(self.filename) == -1: # load failed
                                f = wx.MessageDialog(self, "Unable to open file!", "File Access Exception", wx.OK)
                                f.ShowModal()
                                f.Destroy()
                            else:
                                loop = False
                                loopOuter = False
                        else:
                            loop = False
                        e.Destroy()
                    if not loopOuter:
                        break
#           if start == -1: # user requested exit
                else:
                    self.Close(True)
                    return
                
            d.Destroy()
# DEBUG

# hopefully this will fix our flickering problems...
#self.SetDoubleBuffered(True)

#self.CreateStatusBar(2)
#self.SetStatusText("Try these: Exit, Open, Help, About", 1)

        # begin menubar code
        filemenu = wx.Menu()
        filemenu.Append(ID_OPEN, "&Open...", "Open something")
        filemenu.Append(ID_NEW, "&New...", "Create a new whatsit")
        filemenu.Append(ID_EDIT, "E&dit...", "Edit current whatsit")
        filemenu.Append(ID_CLOSE, "&Close", "Close current whatsit")
        filemenu.AppendSeparator()
        filemenu.Append(ID_SAVE, "&Save", "Save current whatsit")
        filemenu.Append(ID_SAVE_AS, "Save &As...", "Save current whatsit as something else")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXPORT_PDF, "&Export to PDF...", "Export current whatsit to PDF")
        filemenu.Append(ID_EXPORT_IND, "Export &Individual Ranks", "Export ranks to PDF")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT, "E&xit", "Click to exit")

#       editmenu = wx.Menu()
#       editmenu.Append(ID_UNDO, "&Undo", "Undo something")
#       editmenu.Append(ID_REDO, "&Redo", "Undo an undo")
#       editmenu.AppendSeparator()
#       editmenu.Append(ID_CUT, "Cut", "Cut something")
#       editmenu.Append(ID_COPY, "&Copy", "Copy something")
#       editmenu.Append(ID_PASTE, "&Paste", "Paste something")
#       editmenu.AppendSeparator()
#       editmenu.Append(ID_FIND, "&Find...", "Find something")
#       editmenu.Append(ID_FIND_REPLACE, "Find and Rep&lace...", "Find and replace something")
#       editmenu.AppendSeparator()
#       settingsmenu = wx.Menu()
#       settingsmenu.Append(wx.ID_ANY, "Settings go here!", "Indeed they do!")
#       editmenu.AppendSubMenu(settingsmenu, "&Settings", "Settings menu")

        helpmenu = wx.Menu()
        helpmenu.Append(ID_HELP, "&Help", "No help for you!")
        helpmenu.AppendSeparator()
        helpmenu.Append(ID_ABOUT, "&About", "About this program")

        movemenu = wx.Menu()
        movemenu.Append(ID_MOVE_NEW, "&New...", "Create a new whatsit")
        movemenu.Append(ID_MOVE_IMPORT, "&Import ranks...", "Import ranks")
        movemenu.AppendSeparator()
        movemenu.Append(ID_MOVE_SPLIT, "&Split...", "...")
        movemenu.Append(ID_MOVE_MERGE, "&Merge with next...", "...")
        movemenu.Append(ID_MOVE_SHIFT, "S&hift...", "...")
        movemenu.AppendSeparator()
        movemenu.Append(ID_MOVE_TEXT, "Set &Text...", "...")
        movemenu.Append(ID_MOVE_TEXT_OVERWRITE, "Set Text &Overwrite...", "...")

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")
#       menubar.Append(editmenu, "&Edit")
        menubar.Append(helpmenu, "&Help")
        menubar.Append(movemenu, "&Move")

        self.SetMenuBar(menubar)
        # end menubar code

        # begin event code
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        wx.EVT_MENU(self, ID_EDIT, self.EditSong)
        wx.EVT_MENU(self, ID_SAVE, self.OnSave)
        wx.EVT_MENU(self, ID_SAVE_AS, self.OnSaveAs)
        wx.EVT_MENU(self, ID_OPEN, self.OnOpen)
        wx.EVT_MENU(self, ID_HELP, self.OnHelp)
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_NEW, self.CreateSong)
        wx.EVT_MENU(self, ID_MOVE_NEW, self.CreateMove)
        wx.EVT_MENU(self, ID_MOVE_IMPORT, self.OnMoveImport)
        wx.EVT_MENU(self, ID_MOVE_SPLIT, self.OnMoveSplit)
        wx.EVT_MENU(self, ID_MOVE_MERGE, self.OnMoveMerge)
        wx.EVT_MENU(self, ID_MOVE_SHIFT, self.OnMoveShift)
        wx.EVT_MENU(self, ID_MOVE_TEXT, self.OnMoveText)
        wx.EVT_MENU(self, ID_MOVE_TEXT_OVERWRITE, self.OnMoveTextOverwrite)
        wx.EVT_MENU(self, ID_EXPORT_PDF, self.OnExport)
        wx.EVT_MENU(self, ID_EXPORT_IND, self.OnIndividualExport)
        # end event code

        # begin main window code
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.Bind(wx.EVT_CHAR, self.OnKey)

        self.field = GUIField.Field(self.panel, ID_FIELD, wx.BORDER_RAISED, self)
        self.field.Bind(wx.EVT_PAINT, self.field.OnPaint)
        self.field.Bind(wx.EVT_SIZE, self.field.OnResize)
        self.field.Bind(wx.EVT_LEFT_DOWN, self.field.OnLeftClick)
        self.field.Bind(wx.EVT_RIGHT_DOWN, self.field.OnRightClick)
        self.field.Bind(wx.EVT_LEFT_UP, self.field.OnLeftUnclick)
        self.field.Bind(wx.EVT_RIGHT_UP, self.field.OnRightUnclick)
        self.field.Bind(wx.EVT_MOTION, self.field.OnMouseMove)
        self.field.Bind(wx.EVT_LEAVE_WINDOW, self.field.OnMouseExit)
        self.field.Bind(wx.EVT_CHAR, self.OnKey)
#self.field.Bind(wx.EVT_KILL_FOCUS, lambda x: self.field.SetFocus())
#self.field.SetFocus()

#       self.statusBarShowLabel = wx.StaticText(self, wx.ID_ANY, "SHOW NAME")
        self.statusBarSongLabel = wx.StaticText(self.panel, wx.ID_ANY, "")
        self.statusBarMoveLabel = wx.StaticText(self.panel, wx.ID_ANY, "")
#       self.statusBarCountLabel = wx.StaticText(self.panel, wx.ID_ANY, "")

        self.statusBar = wx.BoxSizer(wx.HORIZONTAL)
        self.statusBar.Add((1,1), 1, wx.EXPAND)
#       self.statusBar.Add(statusBarShowLabel, 2, wx.EXPAND)
        self.statusBar.Add(self.statusBarSongLabel, 0, wx.ALIGN_CENTRE)
        self.statusBar.Add((100,1), 1, wx.EXPAND)
        self.statusBar.Add(self.statusBarMoveLabel, 0, wx.ALIGN_CENTRE)
#       self.statusBar.Add((150,1), 0, wx.EXPAND) # reserve 150px for statusBarMoveLabel
#       self.statusBar.Add(self.statusBarCountLabel, 2, wx.EXPAND)
        self.statusBar.Add((1,1), 1, wx.EXPAND)

        self.RefreshStatusBar()

        self.fieldpanel = wx.BoxSizer(wx.VERTICAL)
        self.fieldpanel.Add(self.statusBar, 0, wx.ALIGN_CENTER)
        self.fieldpanel.Add(self.field, 1, wx.EXPAND)

        self.rankNameUnicode = wx.Button(self.panel, wx.ID_ANY, "Unicode")
        self.rankNameUnicode.Bind(wx.EVT_BUTTON, self.OnRankNameUnicode)
        self.holdRankButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/holdicon.png'))
        self.holdRankButton.Bind(wx.EVT_BUTTON, self.OnHoldRank)
        self.curveRankButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/curveicon.png'))
        self.curveRankButton.Bind(wx.EVT_BUTTON, self.OnCurveRank)
        self.straightRankButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/zigzagicon.png'))
        self.straightRankButton.Bind(wx.EVT_BUTTON, self.OnStraightRank)
        self.switchEndpointsButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/switchendpointsicon.png'))
        self.switchEndpointsButton.Bind(wx.EVT_BUTTON, self.OnSwitchEndpoints)
        self.switchLabelButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/switchlabelicon.png'))
        self.switchLabelButton.Bind(wx.EVT_BUTTON, self.OnSwitchLabel)
        self.deleteRankButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/deleteicon.png'))
        self.deleteRankButton.Bind(wx.EVT_BUTTON, self.OnDeleteRank)
        self.snapEndButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/snaptoendicon.png'))
        self.snapEndButton.Bind(wx.EVT_BUTTON, self.OnSnapEnd)
        self.snapBeginButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/snaptobeginicon.png'))
        self.snapBeginButton.Bind(wx.EVT_BUTTON, self.OnSnapBegin)
        self.displayAtCountButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/displayicon.png'))
        self.displayAtCountButton.Bind(wx.EVT_BUTTON, self.OnDisplayAtCount)

        self.toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar.Add(self.rankNameUnicode, 0, wx.EXPAND)
        self.toolbar.Add(self.holdRankButton, 0, wx.EXPAND)
        self.toolbar.Add(self.curveRankButton, 0, wx.EXPAND)
        self.toolbar.Add(self.straightRankButton, 0, wx.EXPAND)
        self.toolbar.Add(self.switchEndpointsButton, 0, wx.EXPAND)
        self.toolbar.Add(self.switchLabelButton, 0, wx.EXPAND)
        self.toolbar.Add(self.deleteRankButton, 0, wx.EXPAND)
        self.toolbar.Add(self.snapEndButton, 0, wx.EXPAND)
        self.toolbar.Add(self.snapBeginButton, 0, wx.EXPAND)
        self.toolbar.Add(self.displayAtCountButton, 0, wx.EXPAND)

        self.fieldbar = GUITimeBar.TimeBar(self.panel, wx.ID_ANY, self)
        self.fieldbar.Bind(wx.EVT_PAINT, self.fieldbar.OnPaint)
        self.fieldbar.Bind(wx.EVT_SIZE, self.fieldbar.OnResize)
        self.fieldbar.Bind(wx.EVT_LEFT_DOWN, self.fieldbar.OnLeftClick)
        self.fieldbar.Bind(wx.EVT_RIGHT_DOWN, self.fieldbar.OnRightClick)
        self.fieldbar.Bind(wx.EVT_LEFT_UP, self.fieldbar.OnLeftUnclick)
        self.fieldbar.Bind(wx.EVT_RIGHT_UP, self.fieldbar.OnRightUnclick)
        self.fieldbar.Bind(wx.EVT_MOTION, self.fieldbar.OnMouseMove)
        self.fieldbar.Bind(wx.EVT_LEAVE_WINDOW, self.fieldbar.OnMouseExit)
#       self.fieldbar.Bind(wx.EVT_CHAR, self.fieldbar.OnKey)

        self.moveSetList = wx.ImageList(GUIField.MINI_FIELD_SIZE[0], GUIField.MINI_FIELD_SIZE[1], False, 0)
        self.moveList = wx.ListCtrl(self.panel, ID_MOVE_LIST, style = wx.LC_SINGLE_SEL | wx.LC_ICON)
        self.moveList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMoveSelect)
        self.moveList.AssignImageList(self.moveSetList, wx.IMAGE_LIST_NORMAL)

        self.moveListCaption = wx.StaticText(self.panel, wx.ID_ANY, "Sets/Moves")

        self.sidepanel = wx.BoxSizer(wx.VERTICAL)
        self.sidepanel.Add(self.moveListCaption, 0, wx.ALIGN_CENTRE)
        self.sidepanel.Add(self.moveList, 1, wx.EXPAND)
        self.sidepanel.Add((GUIField.MINI_FIELD_SIZE[0] * 1.37, 1), 0, wx.ALIGN_CENTRE)

        self.toppanel = wx.BoxSizer(wx.HORIZONTAL)
        self.toppanel.Add(self.fieldpanel, 4, wx.EXPAND)
        self.toppanel.Add(wx.StaticLine(self.panel, style = wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND)
        self.toppanel.Add(self.sidepanel, 0, wx.EXPAND)

        self.commandListCaption = wx.StaticText(self.panel, wx.ID_ANY, "Ranks: ")
        self.commandListRankCaption = wx.StaticText(self.panel, wx.ID_ANY, "")

        self.commandListCaptionPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.commandListCaptionPanel.Add((1,1), 1, wx.EXPAND)
        self.commandListCaptionPanel.Add(self.commandListCaption, 20, wx.EXPAND)
        self.commandListCaptionPanel.Add(self.commandListRankCaption, 5, wx.EXPAND)
        self.commandListCaptionPanel.Add((1,1), 1, wx.EXPAND)

        self.commandList = wx.ListBox(self.panel, ID_COMMAND_LIST, style = wx.LB_SINGLE)
        self.commandList.Bind(wx.EVT_LISTBOX, self.OnCommandSelect)

        self.commandButtonMoveUp = wx.Button(self.panel, ID_COMMAND_BUTTON_MOVE_UP, u"\u2191")
        self.commandButtonMoveUp.Bind(wx.EVT_BUTTON, lambda event: self.OnCommandButtonMove(event, True))
        self.commandButtonMoveDown = wx.Button(self.panel, ID_COMMAND_BUTTON_MOVE_DOWN, u"\u2193")
        self.commandButtonMoveDown.Bind(wx.EVT_BUTTON, lambda event: self.OnCommandButtonMove(event, False))
        self.commandButtonRename = wx.Button(self.panel, ID_COMMAND_BUTTON_SPLIT, "Rename")
        self.commandButtonRename.Bind(wx.EVT_BUTTON, self.OnCommandButtonRename)
        self.commandButtonSplit = wx.Button(self.panel, ID_COMMAND_BUTTON_SPLIT, "Split")
        self.commandButtonSplit.Bind(wx.EVT_BUTTON, self.OnCommandButtonSplit)
        self.commandButtonMerge = wx.Button(self.panel, ID_COMMAND_BUTTON_MERGE, "Merge")
        self.commandButtonMerge.Bind(wx.EVT_BUTTON, self.OnCommandButtonMerge)
        self.commandButtonDelete = wx.Button(self.panel, ID_COMMAND_BUTTON_DELETE, "Delete")
        self.commandButtonDelete.Bind(wx.EVT_BUTTON, self.OnCommandButtonDelete)

        self.commandListButtonPanel = wx.BoxSizer(wx.VERTICAL)
        self.commandListButtonPanel.Add(self.commandButtonMoveUp, 5, wx.EXPAND)
        self.commandListButtonPanel.Add(self.commandButtonMoveDown, 5, wx.EXPAND)
        self.commandListButtonPanel.Add(self.commandButtonRename, 5, wx.EXPAND)
        self.commandListButtonPanel.Add(self.commandButtonSplit, 5, wx.EXPAND)
        self.commandListButtonPanel.Add(self.commandButtonMerge, 5, wx.EXPAND)
        self.commandListButtonPanel.Add(self.commandButtonDelete, 5, wx.EXPAND)

        self.commandListPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.commandListPanel.Add(self.commandList, 5, wx.EXPAND)
        self.commandListPanel.Add(self.commandListButtonPanel, 2, wx.EXPAND)

        self.bottompanelcentre = wx.BoxSizer(wx.VERTICAL)
        self.bottompanelcentre.Add(self.commandListCaptionPanel, 0, wx.ALIGN_CENTRE)
        self.bottompanelcentre.Add(self.commandListPanel, 20, wx.EXPAND)

#       self.rankNameListCaption = wx.StaticText(self.panel, wx.ID_ANY, "Ranks: ")
        self.rankNameList = GUIRankList.RankList(self.panel, wx.ID_ANY, self)
        self.rankNameList.Bind(wx.EVT_PAINT, self.rankNameList.OnPaint)
        self.rankNameList.Bind(wx.EVT_SIZE, self.rankNameList.OnResize)

#       self.rankNameListPanel = wx.BoxSizer(wx.HORIZONTAL)
#       self.rankNameListPanel.Add(self.rankNameListCaption, 0, wx.ALIGN_RIGHT)
#       self.rankNameListPanel.Add(self.rankNameList, 0, wx.ALIGN_LEFT)

        self.rankNameListBox = wx.StaticBox(self.panel, wx.ID_ANY, "Ranks")
        self.rankNameListPanel = wx.StaticBoxSizer(self.rankNameListBox, wx.HORIZONTAL)
        self.rankNameListPanel.Add(self.rankNameList, 1, wx.EXPAND)

        self.rankNamePanel = wx.BoxSizer(wx.HORIZONTAL)
        self.rankNamePanel.Add(self.rankNameListPanel, 1, wx.EXPAND)

        self.commandAddChoices = ['MT', 'Hlt', 'FM', 'BM', 'RS', 'LS', 'Flat']
        self.commandAddButtons = []

        self.commandAddSpecialChoices = ['GT', 'PW', 'Exp', 'Cond', 'DTP', 'FTA', 'Curv']
        self.commandAddSpecialButtons = []

        self.commandAddButtonsPanel = wx.BoxSizer(wx.HORIZONTAL)

        self.commandAddSpecialButtonsBox = wx.StaticBox(self.panel, wx.ID_ANY, "Special Commands")
        self.commandAddSpecialButtonsPanel = wx.StaticBoxSizer(self.commandAddSpecialButtonsBox, wx.HORIZONTAL)

        for i in range(len(self.commandAddChoices)):
            self.commandAddButtons.append(wx.ToggleButton(self.panel, wx.ID_ANY, self.commandAddChoices[i]))
# VERY HACKISH: we have the argument j and give it the default value of i instead of just doing
# lambda event: self.OnCommandAddButtons(event, i)
# because that way, we establish a link to the variable i, so every binding will be using the same value for i
# By setting j to a default value of i, we implicitly create a new variable and set it to the value of i at that time,
# thus circumventing this problem
            self.commandAddButtons[i].Bind(wx.EVT_TOGGLEBUTTON, lambda event, j = i: self.OnCommandAddButtons(event, j))
            self.commandAddButtonsPanel.Add(self.commandAddButtons[i], 1, wx.EXPAND)

        self.commandAddButtons[0].SetValue(True) # make sure at least one thing is always selected
        self.commandAddButtonSelected = 0 # keep track of which is selected

        for i in range(len(self.commandAddSpecialChoices)):
            self.commandAddSpecialButtons.append(wx.Button(self.panel, wx.ID_ANY, self.commandAddSpecialChoices[i]))
# VERY HACKISH: we have the argument j and give it the default value of i instead of just doing
# lambda event: self.OnCommandAddButtons(event, i)
# because that way, we establish a link to the variable i, so every binding will be using the same value for i
# By setting j to a default value of i, we implicitly create a new variable and set it to the value of i at that time,
# thus circumventing this problem
            self.commandAddSpecialButtons[i].Bind(wx.EVT_BUTTON, lambda event, j = i: self.OnCommandAddSpecialButtons(event, j))
            self.commandAddSpecialButtonsPanel.Add(self.commandAddSpecialButtons[i], 1, wx.EXPAND)

        self.commandLengthCaption = wx.StaticText(self.panel, wx.ID_ANY, "Steps: ")
        self.commandLengthText = wx.TextCtrl(self.panel, wx.ID_ANY, "", size = (35, -1))
        self.commandAddButton = wx.Button(self.panel, wx.ID_ANY, "Add >>", style = wx.BU_EXACTFIT)
        self.commandAddButton.Bind(wx.EVT_BUTTON, self.OnCommandAdd)

        self.commandLengthPanel = wx.BoxSizer(wx.HORIZONTAL)
        self.commandLengthPanel.Add(self.commandLengthCaption, 0, wx.ALIGN_CENTRE)
        self.commandLengthPanel.Add(self.commandLengthText, 0, wx.ALIGN_CENTRE)
        self.commandLengthPanel.Add((1,1), 1, wx.EXPAND)
        self.commandLengthPanel.Add(self.commandAddButton, 0, wx.ALIGN_CENTRE)

        self.commandAddButtonsBox = wx.StaticBox(self.panel, wx.ID_ANY, "Simple Commands")
        self.commandAddButtonsPanelPanel = wx.StaticBoxSizer(self.commandAddButtonsBox, wx.HORIZONTAL)
        self.commandAddButtonsPanelPanel.Add(self.commandAddButtonsPanel, 1, wx.EXPAND)
        self.commandAddButtonsPanelPanel.Add((5,1), 0, wx.ALIGN_CENTRE)
        self.commandAddButtonsPanelPanel.Add(wx.StaticLine(self.panel, style = wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND)
        self.commandAddButtonsPanelPanel.Add((5,1), 0, wx.ALIGN_CENTRE)
        self.commandAddButtonsPanelPanel.Add(self.commandLengthPanel, 0, wx.ALIGN_CENTRE)

        self.bottompanelleft = wx.BoxSizer(wx.VERTICAL)
        self.bottompanelleft.Add(self.rankNamePanel, 0, wx.EXPAND)
#       self.bottompanelleft.Add((1,1), 1, wx.EXPAND)
        self.bottompanelleft.Add(self.commandAddButtonsPanelPanel, 0, wx.ALL | wx.EXPAND)
        self.bottompanelleft.Add(self.commandAddSpecialButtonsPanel, 0, wx.ALL | wx.EXPAND)
        self.bottompanelleft.Add((1,1), 1, wx.EXPAND)

        self.animationCaption = wx.StaticText(self.panel, wx.ID_ANY, "Animation Controls")

        self.playButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/playicon.png'))
        self.playButton.Bind(wx.EVT_BUTTON, self.OnAnimationBegin)
        self.stopButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/stopicon.png'))
        self.stopButton.Bind(wx.EVT_BUTTON, self.OnAnimationEnd)
        self.addWaypointButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/addwaypointicon.png'))
        self.addWaypointButton.Bind(wx.EVT_BUTTON, self.OnAddWaypoint)
        self.removeWaypointButton = wx.BitmapButton(self.panel, wx.ID_ANY, wx.Bitmap('icons/removewaypointicon.png'))
        self.removeWaypointButton.Bind(wx.EVT_BUTTON, self.OnRemoveWaypoint)

        self.bottompanelrightbuttons = wx.FlexGridSizer(2, 2)
        self.bottompanelrightbuttons.Add(self.playButton, 0, wx.EXPAND)
        self.bottompanelrightbuttons.Add(self.stopButton, 0, wx.EXPAND)
        self.bottompanelrightbuttons.Add(self.addWaypointButton, 0, wx.EXPAND)
        self.bottompanelrightbuttons.Add(self.removeWaypointButton, 0, wx.EXPAND)

        self.bottompanelright = wx.BoxSizer(wx.VERTICAL)
        self.bottompanelright.Add(self.animationCaption, 0, wx.ALIGN_CENTRE)
        self.bottompanelright.Add(self.bottompanelrightbuttons, 0, wx.ALIGN_CENTRE)

        self.bottompanel = wx.BoxSizer(wx.HORIZONTAL)
#       self.bottompanel.Add((10,1), 0, wx.ALIGN_CENTRE)
        self.bottompanel.Add(self.bottompanelleft, 3, wx.EXPAND)
        self.bottompanel.Add(wx.StaticLine(self.panel, style = wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND)
        self.bottompanel.Add(self.bottompanelcentre, 2, wx.EXPAND)
        self.bottompanel.Add(wx.StaticLine(self.panel, style = wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND)
        self.bottompanel.Add(self.bottompanelright, 1, wx.EXPAND)
#       self.bottompanel.Add((1,1), 1, wx.EXPAND) # TODO
#       self.bottompanel.Add(self.bottomcontrolleft, 0, wx.ALIGN_CENTRE)
#       self.bottompanel.Add(self.bottomline, 0, wx.ALIGN_CENTRE)
#       self.bottompanel.Add(self.commandList, 2, wx.EXPAND)

        self.mainpanel = wx.BoxSizer(wx.VERTICAL)
        self.mainpanel.Add(self.toppanel, 15, wx.EXPAND)
        self.mainpanel.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND)
        self.mainpanel.Add(self.toolbar, 0, wx.EXPAND)
        self.mainpanel.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND)
        self.mainpanel.Add(self.fieldbar, 0, wx.EXPAND)
        self.mainpanel.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND)
        self.mainpanel.Add(self.bottompanel, 5, wx.EXPAND)

        self.panel.SetSizer(self.mainpanel)
#self.SetAutoLayout(1)
        # end main window code


# ensure that self intercepts all keypress events
#       self.field.Bind(wx.EVT_KILL_FOCUS, lambda x: self.field.SetFocus())
#       self.field.SetFocus()

# DEBUG
        if DEBUG:
            self.core.MoveAdded(1, 16, None)
            self.core.MoveAdded(17, 32, None)
# DEBUG

        self.RefreshTitleBar()
        self.RefreshMoveList()
        self.RefreshStatusBar()
        self.Show(True)

# begin variables

        self.filename = None # this is the name of the currently-open file; None if not yet saved
        self.animranks = None # list of animated rank locations when animating; None when not
        self.animtimer = wx.Timer(self, ID_ANIM_TIMER)
        wx.EVT_TIMER(self, ID_ANIM_TIMER, self.OnAnimationTimer)

    def RefreshTitleBar(self):
        if self.filename is None:
            self.SetTitle("Rank Panda")
        else:
            self.SetTitle("Rank Panda (" + self.filename + ")")

    def RefreshMoveList(self):
        self.moveList.Freeze()
        self.moveList.ClearAll()
        moves = self.core.GetMoves()
        self.moveSetList.RemoveAll()

        i = 0

        for m in moves:
            item = wx.ListItem()
            item.SetId(i)
            item.SetText(m[1])
            item.SetImage(i)

            self.moveSetList.Add(self.field.RenderSet(self.core.GetRanksGivenMove(i)))

            self.moveList.InsertItem(item)

            i += 1

        curr = self.core.GetCurrentMove()[0]
        self.moveList.SetItemState(curr, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.moveList.Thaw()

    def RefreshCurrentMove(self):
        curr = self.core.GetCurrentMove()[0]
        self.moveSetList.Replace(curr, self.field.RenderSet(self.core.GetRanksGivenMove(curr)))
        self.moveList.RefreshItem(curr)

    def RefreshRankList(self):
        ranks = self.core.GetRanks()
        selected = self.core.GetSelectedRanks()

        rankLabels = []
        selectedRankLabels = []

        i = 0

        for r in ranks:
            if r[1] is not None:
                isSelected = False

                for s in selected:
                    if r[0] == s[0]:
                        isSelected = True

                label = r[1]
                if self.core.IsRankHeld(r[0]):
                    label += '*'

                label += ' '

                rankLabels.append(label)

                if isSelected:
                    selectedRankLabels.append(i)

                i += 1

        self.rankNameList.SetRanks(rankLabels, selectedRankLabels)

    def RefreshCommandList(self):
        self.commandList.Clear()
        ranks = self.core.GetSelectedRanks()
        self.commandListRankCaption.SetLabel("")

        label = ""
        for r in ranks:
            if r[1] is not None:
                label += r[1]
                if self.core.IsRankHeld(r[0]):
                    label += '*'
                label += ' '

        self.commandListRankCaption.SetLabel(label)

        commands = self.core.GetCommands()
        for c in commands:
# DEBUG
            if DEBUG:
                self.commandList.Append(c[0] + " " + str(c[1]))
            else:
                self.commandList.Append(c[0] + " " + str(int(round(c[1]))))
# DEBUG
        selected = self.commandList.GetSelections()
        self.core.SetListOfSelectedCommandNumbers(selected)

    def RefreshStatusBar(self):
        self.statusBarSongLabel.SetLabel(self.core.GetSong())

        currMove = self.core.GetCurrentMove()
        info = self.core.GetMoveInfo(currMove[0])
        if currMove[2] == 1:
            count = "count"
        else:
            count = "counts"

        if int(info[0]) == int(info[1]):
            measure = "Measure"
        else:
            measure = "Measures"

        if currMove is not None:
            self.statusBarMoveLabel.SetLabel(currMove[1] + ": " + str(currMove[2]) + " " + count + " (" + measure + " " + str(int(info[0])) + u"\u2013" + str(int(info[1])) + ")")
#            self.statusBarCountLabel.SetLabel(str(currMove[2]))
        else:
            self.statusBarMoveLabel.SetLabel("")
#            self.statusBarCountLabel.SetLabel("")


    def CreateSong(self, event):
        d = GUIDialogs.SongCreationDialog(self)
        if d.ShowModal() == 0:
            try:
                core = CoreWrapper.CoreWrapper(*d.output)
            except NameError as exception:
                e = wx.MessageDialog(self, "Exception thrown while creating song!\nSong NOT created.\nException: " + str(exception), "Song Creation Exception", wx.OK)
                e.ShowModal()
                e.Destroy()
            else:
                self.core = core
                self.field.Refresh(False)
                self.fieldbar.Refresh(False)
                self.RefreshMoveList()
                self.RefreshRankList()
                self.RefreshCommandList()
                self.RefreshStatusBar()

    def EditSong(self, event):
        d = GUIDialogs.SongCreationDialog(self)
        if d.ShowModal() == 0:
            try:
                self.core.EditSongInfo(*d.output)
            except NameError as exception:
                e = wx.MessageDialog(self, "Exception thrown while creating song!\nSong NOT created.\nException: " + str(exception), "Song Edit Exception", wx.OK)
                e.ShowModal()
                e.Destroy()
            else:
                self.core = core
                self.field.Refresh(False)
                self.fieldbar.Refresh(False)
                self.RefreshMoveList()
                self.RefreshRankList()
                self.RefreshCommandList()
                self.RefreshStatusBar()

    def CreateMove(self, event, beginMeasure = "", endMeasure = ""):
        moves = self.core.GetMoves()
        moveNames = []

        for m in moves:
            moveNames.append(m[1])

        d = GUIDialogs.MoveCreationDialog(self, moveNames, beginMeasure, endMeasure)
        if d.ShowModal() == 0:
            m = self.core.MoveAdded(*d.output)
            importTarget = d.output2
            if importTarget >= m: # check if our insertion of a new move affected the index of the move to insert from, and correct
                importTarget += 1

            if m is None:
                e = wx.MessageDialog(self, "New move overlaps with pre-existing moves!\nMove NOT created.", "Move Creation Exception", wx.OK)
                e.ShowModal()
                e.Destroy()
            elif importTarget != -1:
                self.core.ImportRankLocation(importTarget, m)

            self.field.Refresh(False)
            self.fieldbar.Refresh(False)
            self.RefreshMoveList()
            self.RefreshRankList()
            self.RefreshCommandList()
            self.RefreshStatusBar()

        d.Destroy()

    def OnMoveSelect(self, event):
        index = event.m_itemIndex
        self.core.ChangeMove(index)
        self.field.Refresh(False)
        self.fieldbar.Refresh(False)
        self.RefreshRankList()
        self.RefreshCommandList()
        self.RefreshStatusBar()

    def OnMoveImport(self, event):
        move = self.core.GetCurrentMove()

        if move is None:
            return

        moves = self.core.GetMoves()
        moveNames = []

        for m in moves:
            moveNames.append(m[1])

        d = GUIDialogs.ImportRanksDialog(self, moveNames)
        if d.ShowModal() == 0:
            self.core.ImportRankLocation(d.output, move[0])

            self.field.Refresh(False)
            self.RefreshMoveList()
            self.RefreshRankList()
            self.RefreshCommandList()

        d.Destroy()

    def OnMoveSplit(self, event):
        move = self.core.GetCurrentMove()

        if move is None:
            return

        d = wx.GetNumberFromUser("", "At count:", "Split Move", 1, 1, move[2], self)
        if d != -1:
            self.core.MoveEdited('Split', [move[0], d])

        self.fieldbar.Refresh(False)
        self.RefreshMoveList()
        self.RefreshStatusBar()

    def OnMoveMerge(self, event):
        move = self.core.GetCurrentMove()

        if move is None:
            return

        self.core.MoveEdited('Merge', [move[0]])

        self.fieldbar.Refresh(False)
        self.RefreshMoveList()
        self.RefreshStatusBar()

    def OnMoveShift(self, event):
        move = self.core.GetCurrentMove()

        if move is None:
            return

        d = wx.GetTextFromUser("Shift by how many counts:", "Shift Move", "0", self)

        try:
            n = int(d)
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for number of counts to shift by!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        self.fieldbar.Refresh(False)
        self.RefreshMoveList()
        self.RefreshStatusBar()

#TODO
#self.core.MoveEdited('Shift', [move[0], n])
        self.RefreshMoveList()
        self.RefreshStatusBar()

    def OnMoveText(self, event):
        move = self.core.GetCurrentMove()

        if move is None:
            return

        text = self.core.GetMoveText()
        if text is None:
            text = ""

        d = GUIDialogs.AddText(self, text, "Entering Text for " + move[1])
        if d.ShowModal() == 0:
            if d.output == "":
                self.core.SetMoveText(None)
            else:
                self.core.SetMoveText(d.output)
        d.Destroy()

    def OnMoveTextOverwrite(self, event):
        move = self.core.GetCurrentMove()

        if move is None:
            return

        text = self.core.GetMoveTextOverwrite()
        if text is None:
            text = ""

        d = GUIDialogs.AddText(self, text, "Entering Overwrite Text for " + move[1])
        if d.ShowModal() == 0:
            if d.output == "":
                self.core.SetMoveTextOverwrite(None)
            else:
                self.core.SetMoveTextOverwrite(d.output)
        d.Destroy()

    def OnCommandSelect(self, event): # TODO allow handling multiple contiguous selections
        index = event.GetSelection()
        self.core.SetListOfSelectedCommandNumbers([index])
        self.field.Refresh(False)

    def OnCommandAddButtons(self, event, i):
# don't allow deselecting of selected button (just so something is selected at all times)
        self.commandAddButtons[i].SetValue(True)
        self.commandAddButtonSelected = i # keep track of which is selected
# set all of the other buttons to disabled
        for j in range(len(self.commandAddChoices)):
            if i != j:
                self.commandAddButtons[j].SetValue(False)

    def BitmapGet(self):
        return self.field.PrintBitmap()

    def OnCommandAddSpecialButtons(self, event, i):
        ranks = self.core.GetSelectedRanks()
        #if len(ranks) != 1:
            #d = wx.MessageDialog(self, "Currently, only adding commands to a single rank at a time is supported.", "Selection Error", wx.OK)
            #d.ShowModal()
            #d.Destroy()
            #return
        n=0
        while(n<len(ranks)):
            if not self.core.IsRankHeld(ranks[n][0]): # if selected rank is not locked, just silently don't do anything
                return
            n=n+1

# TODO check label and stuff
        type = self.commandAddSpecialChoices[i]

        selected = self.commandList.GetSelections()
        index = self.commandList.GetCount()
        if len(selected) == 1:
            index = selected[0]
 
        if type == "GT":
            f = GUIDialogs.GateTurnDialog(self)

            if f.ShowModal() == 0:
                (dir, pt, length) = f.output
                if dir == 0:
                    type = "GTCW"
                else:
                    type = "GTCCW"

                type += str(pt)
                n=0
                while(n<len(ranks)):
                    self.core.CommandAdded(ranks[n][0], type, index, length, None, None)
                    n=n+1

            f.Destroy()

        elif type == "PW":
            f = GUIDialogs.PinwheelDialog(self)

            if f.ShowModal() == 0:
                (dir, length) = f.output
                if dir == 0:
                    type = "PWCW"
                else:
                    type = "PWCCW"
                n=0
                while(n<len(ranks)):
                    self.core.CommandAdded(ranks[n][0], type, index, length, None, None)
                    n=n+1

            f.Destroy()

        elif type == "Exp":
            f = GUIDialogs.ExpandDialog(self)

            if f.ShowModal() == 0:
                (pt, length) = f.output
                type += str(pt)

                n=0
                while(n<len(ranks)):
                    self.core.CommandAdded(ranks[n][0], type, index, length, None, None)
                    n=n+1

            f.Destroy()

        elif type == "Cond":
            f = GUIDialogs.CondenseDialog(self)

            if f.ShowModal() == 0:
                (pt, length) = f.output
                type += str(pt)

                n=0
                while(n<len(ranks)):
                    self.core.CommandAdded(ranks[n][0], type, index, length, None, None)
                    n=n+1

            f.Destroy()

        elif type == "DTP" or type == "Curv":
            f = GUIDialogs.DTPDialog(self)

            if f.ShowModal() == 0:
                length = f.output

                DTPranks = self.core.BeginAddingDTP(index, length, None, type == "Curv")
                if DTPranks is not None:
                    d = GUIDialogs.AddDTPDialog(self, self, ranks[0][1], length, DTPranks)
                    d.ShowModal()
                    d.Destroy()
                    self.core.FinalizeAddingDTP()

            f.Destroy()

        elif type == "FTA":
            f = GUIDialogs.FTADialog(self)

            if f.ShowModal() == 0:
                endpoint = f.output[0] == 1
                length = f.output[1]

                if endpoint:
                    FTAranks = self.core.BeginAddingFTA1(index, length, None)
                else:
                    FTAranks = self.core.BeginAddingFTA0(index, length, None)

                if FTAranks is not None:
                    d = GUIDialogs.AddFTADialog(self, self, endpoint, ranks[0][1], length, FTAranks)
                    d.ShowModal()
                    d.Destroy()

                    if endpoint:
                        self.core.FinalizeAddingFTA1()
                    else:
                        self.core.FinalizeAddingFTA0()

            f.Destroy()

        else:
            pass

        self.field.Refresh(False)
        self.RefreshCommandList()

    def OnCommandAdd(self, event):
        ranks = self.core.GetSelectedRanks()
        #if len(ranks) != 1:
            #d = wx.MessageDialog(self, "Currently, only adding commands to a single rank at a time is supported.", "Selection Error", wx.OK)
            #d.ShowModal()
            #d.Destroy()
            #return

        n=0
        while(n<len(ranks)):
            if not self.core.IsRankHeld(ranks[n][0]): # if selected rank is not locked, just silently don't do anything
                return
            n=n+1

        try:
            length = int(self.commandLengthText.GetValue())
        except Exception:
            d = wx.MessageDialog(self, "Invalid entry for Command Steps!", "Parse Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

# we assume that at most one button will be selected at a time, which is reasonable
        type = self.commandAddChoices[self.commandAddButtonSelected]

        selected = self.commandList.GetSelections()
        index = self.commandList.GetCount()
        if len(selected) == 1:
            index = selected[0]

        if type == "Hlt":
            n=0
            while(n<len(ranks)):
                self.core.CommandAdded(ranks[n][0], "MT", index, length, "Halt", None)
                n=n+1
        else:
            n=0
            while(n<len(ranks)):
                self.core.CommandAdded(ranks[n][0], type, index, length, None, None)
                n=n+1

        self.field.Refresh(False)
        self.RefreshCommandList()

    def OnCommandButtonMove(self, event, dir):
        selected = self.commandList.GetSelections()
        if len(selected) != 1:
            return

        ranks = self.core.GetSelectedRanks()

        if not self.core.IsRankHeld(ranks[0][0]): # not held; can't move its commands    
            return

        if len(ranks) != 1:
            d = wx.MessageDialog(self, "Currently, only adding commands to a single rank at a time is supported.", "Selection Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return

        self.core.CommandRearranged(ranks[0][0], selected[0], dir)
        self.field.Refresh(False)

        if dir: # moved up
            if selected[0] > 0:
                self.RefreshCommandList()
                self.commandList.SetSelection(selected[0] - 1)
        elif not dir: # moved down
            if selected[0] < self.commandList.GetCount() - 1:
                self.RefreshCommandList()
                self.commandList.SetSelection(selected[0] + 1)

    def OnCommandButtonRename(self, event):
        selected = self.commandList.GetSelections()
        if len(selected) != 1:
            return

        label = self.core.GetCommands()[selected[0]][0]
        d = wx.GetTextFromUser("New name:", "Rename Command", label, self)
        if d != "":
            ranks = self.core.GetSelectedRanks()
            self.core.CommandEdited(ranks[0][0], selected[0], d)
        self.RefreshCommandList()

    def OnCommandButtonSplit(self, event):
        selected = self.commandList.GetSelections()
        if len(selected) != 1:
            return

        d = wx.GetNumberFromUser("", "At count:", "Split Command", 1, 1, self.core.GetCommands()[selected[0]][1], self)
        if d != -1:
            ranks = self.core.GetSelectedRanks()
            self.core.CommandSplit(ranks[0][0], selected[0], d)
        self.RefreshCommandList()

    def OnCommandButtonMerge(self, event):
        selected = self.commandList.GetSelections()
        if len(selected) != 1:
            return

        ranks = self.core.GetSelectedRanks()
        self.core.CommandMerge(ranks[0][0], selected[0])
        self.RefreshCommandList()

    def OnCommandButtonDelete(self, event):
        selected = self.commandList.GetSelections()
        if len(selected) != 1:
            return

#       d = wx.MessageBox("Are you sure?", "Delete Command", wx.YES_NO, self)
#       if d == wx.YES:
#           ranks = self.core.GetSelectedRanks()
#           if len(ranks) != 1:
#               c = wx.MessageBox("Deleting commands for multiple ranks not yet implemented...", "Delete Command", wx.OK, self)
#               c.ShowModal()
#               c.destroy()
#           else:
#               self.core.CommandDeleted(ranks[0][0], selected[0])

        ranks = self.core.GetSelectedRanks()
        if len(ranks) != 1:
            c = wx.MessageBox("Deleting commands for multiple ranks not yet implemented...", "Delete Command", wx.OK, self)
            c.ShowModal()
            c.destroy()
        else:
            self.core.CommandDeleted(ranks[0][0], selected[0])

        self.RefreshCommandList()

# TODO
    def OnExit(self, event):
        """ Exit menu item pressed """
        self.Close(True)

    def OnOpen(self, event):
        """ Load file """
        self.dirname = ''

        while True:
            d = wx.FileDialog(self, "Open File", self.dirname, "", "*.panda", wx.OPEN)
            if d.ShowModal() == wx.ID_OK:
                self.filename = os.path.join(d.GetDirectory(), d.GetFilename())
                if self.core.Load(self.filename) == -1: # load failed
                    e = wx.MessageDialog(self, "Unable to open file!", "File Access Exception", wx.OK)
                    e.ShowModal()
                    e.Destroy()
                else:
                    self.RefreshTitleBar()
                    self.field.Refresh(False)
                    self.fieldbar.Refresh(False)
                    self.RefreshMoveList()
                    self.RefreshRankList()
                    self.RefreshCommandList()
                    self.RefreshStatusBar()

                    break
            else:
                break
            d.Destroy()

    def OnSave(self, event):
        """ Save current file under same name (same as Save As if no current file) """
        if self.filename == None:
            self.OnSaveAs(event)
        else:
            self.core.Save(self.filename)

    def OnSaveAs(self, event):
        """ Save current file under new name """
        self.dirname = ''
        d = wx.FileDialog(self, "Save File", self.dirname, "", "*.panda", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            self.filename = os.path.join(d.GetDirectory(), d.GetFilename())
            self.core.Save(self.filename)
# TODO check for and strip off .panda?
        d.Destroy()

        self.RefreshTitleBar()

    def OnSavePdf(self, event):
        """ Save current file under new name """
        self.dirname = ''
        d = wx.FileDialog(self, "Save File", self.dirname, "", "*.pdf", wx.SAVE)
        if d.ShowModal() == wx.ID_OK:
            self.filename = os.path.join(d.GetDirectory(), d.GetFilename())
        d.Destroy()
        return self.filename

    def OnExport(self, event):
        moveNames=[]
        i=0
        while(i<len(self.core.GetMoves())):
            moveNames.append(self.core.GetMoves()[i][1])
            i=i+1
        d = GUIDialogs.ExportPDFDialog(self, moveNames)
        if d.ShowModal() == 0:

            filename = self.OnSavePdf(event)
            moveList = self.core.GetMoves()
            #columnsArr = [] #User input
            moveNames = []
            commandStrings = []
            measureInfo = []
	    movetexts=[]#[text, overwrite? boolean] tuple list
            i=0
            while (i < len(moveList)):
                self.core.ChangeMove(i)
                self.BitmapGet().SaveFile("fieldPic"+ moveList[i][1] +".bmp", wx.BITMAP_TYPE_BMP)
                commandStrings.append(self.core.GetCommandStrings())
                moveNames.append(moveList[i][1])
                measureInfo.append(self.core.GetMoveInfo(i))
		if (self.core.GetMoveTextOverwrite() is None):
		    movetexts.append([self.core.GetMoveText(),False])
		else:
		    movetexts.append([self.core.GetMoveTextOverwrite(),True])
                #columnsArr.append(int(d.columnInput.GetValue()))
                i= i+1
            #try:
	    Printer.printDrill(self.core.GetSong(), filename, moveNames, commandStrings,
                                   int(d.fontText.GetValue()), d.output[1], measureInfo, movetexts)
            #except Exception:
            #    d = wx.MessageDialog(self, "File Error!", "File Error", wx.OK)
            #    d.ShowModal()
            #    d.Destroy()
            #    return

        d.Destroy()
        
    def OnIndividualExport(self, event):
        moveNames=[]
	measureInfo=[]
        i=0
        while(i<len(self.core.GetMoves())):
            moveNames.append(self.core.GetMoves()[i][1])
	    measureInfo.append(self.core.GetMoveInfo(i))
            i=i+1
        d = GUIDialogs.ExportIndDialog(self)
        if d.ShowModal() == 0:

            filename = self.OnSavePdf(event)
            rankStrings = self.core.GetRankStrings()

            try:
		Printer.printInd(self.core.GetSong(), filename, moveNames, rankStrings, 
	                     int(d.fontText.GetValue()), int(d.columnInput.GetValue()), measureInfo)

            except Exception:
                d = wx.MessageDialog(self, "File Error!", "File Error", wx.OK)
                d.ShowModal()
                d.Destroy()
                return

        d.Destroy()

    def OnHelp(self, event):
        """ Help menu item pressed """
        d = wx.MessageDialog(self, "... ... ... ... ... ... ... ... ...", "No help for you!", wx.OK)
        d.ShowModal()
        d.Destroy()

    def OnAbout(self, event):
        """ About menu item pressed """
        d = wx.MessageDialog(self, "This program was created by REAL PANDAS (Adam Sorrin '10, Lauren DiCristofaro '10, Norris Xu '11, Mark Broomfield '11, Sally Tao '10", "About", wx.OK)
        d.ShowModal()
        d.Destroy()

    def OnAnimationBegin(self, event):
# HACK HACK HACK
        if len(self.core.GetListOfWayPoints()) < 2: # if we don't have any waypoints, don't do anything
            d = wx.MessageDialog(self, "Need at least two waypoints to animate!", "Animation Error", wx.OK)
            d.ShowModal()
            d.Destroy()
            return # we do this until it can be implemented in the core
# HACK HACK HACK
        d = wx.GetNumberFromUser("", "Start Count:", "Begin Animation", 1, 1, 1000, self)
        if d == -1:
            return
        (self.animranks, time, count) = self.core.AnimationBegin(d)

        self.fieldbar.AnimateCount(count)
        self.animtimer.Start(time, wx.TIMER_ONE_SHOT)

    def OnAnimationEnd(self, event):
        self.core.AnimationStop()
        self.fieldbar.AnimateCount(-1)

    def OnAnimationTimer(self, event):
        (self.animranks, time, count) = self.core.AnimationStep()
        if self.animranks is None: # done animating...
            self.OnAnimationEnd(event)
        else:
            self.animtimer.Start(time, wx.TIMER_ONE_SHOT)

            self.fieldbar.AnimateCount(count)
            self.field.Refresh(False)

    def OnHoldRank(self, event):
        ranks = self.core.GetSelectedRanks()

        for r in ranks:
            if self.core.IsRankHeld(r[0]):
                d = wx.MessageBox("Are you sure you want to unlock rank " + r[1] + "?", "Unlock Rank", wx.YES_NO, self)
                if d == wx.YES:
                    self.core.RankUnlocked(r[0])
            else:
                self.core.RankLocked(r[0])

        self.RefreshRankList()
        self.RefreshCommandList()

    def OnCurveRank(self, event):
        self.core.MakeSelectedRanksCurved()
        self.field.Refresh(False)
        self.RefreshMoveList()
        self.RefreshCommandList()

    def OnStraightRank(self, event):
        self.core.MakeSelectedRanksStraight()
        self.field.Refresh(False)
        self.RefreshMoveList()
        self.RefreshCommandList()

    def OnSwitchEndpoints(self, event):
        self.core.SwitchEndpoints()
        self.RefreshCommandList()
        self.field.Refresh(False)

    def OnSwitchLabel(self, event):
        self.core.SwitchLabelLocations()
        self.field.Refresh(False)

    def OnDeleteRank(self, event):
        ranks = self.core.GetSelectedRanks()

        for r in ranks:
            self.core.RankDeleted(r[0])

        self.field.Refresh(False)
        self.RefreshRankList()
        self.RefreshCommandList()

    def OnSnapEnd(self, event):
        self.core.SnapEndLocations()
        self.field.Refresh(False)
        self.RefreshMoveList()
        self.RefreshCommandList()

    def OnSnapBegin(self, event):
        self.core.SnapBeginLocations()
        self.field.Refresh(False)
        self.RefreshMoveList()
        self.RefreshCommandList()

    def OnDisplayAtCount(self, event):
        e = wx.GetNumberFromUser("", "Count:", "Display Status at Count", 1, 1, 1000, self)
        if e == -1:
            return
        d = GUIDialogs.StatusAtCountDialog(self, self, e)
        d.ShowModal()
        d.Destroy()

    def OnAddWaypoint(self, event):
#       d = wx.GetNumberFromUser("", "Measure:", "Add Waypoint", 1, 1, 1000, self)
#       if d == -1:
#           return
#       e = wx.GetNumberFromUser("", "Time (ms):", "Add Waypoint", 1, 1, 1000000, self)
#       if e == -1:
#           return
#       self.core.AddWayPoint(d, e)

        d = GUIDialogs.AddWaypointDialog(self)
        if d.ShowModal() == 0:
            self.core.AddWayPoint(d.output[0], d.output[1])

        self.fieldbar.Refresh(False)

    def OnRemoveWaypoint(self, event):
        d = wx.GetNumberFromUser("", "Measure:", "Remove Waypoint", 1, 1, 1000, self)
        if d == -1:
            return
        self.core.RemoveWayPoint(d)

        self.fieldbar.Refresh(False)

    def OnKey(self, event):
        if event.GetModifiers() == wx.MOD_ALT: # if alt is down, skip it so menu shortcuts work
            event.Skip()

        keyCode = event.GetUnicodeKey()
        if keyCode == 127: # delete
            ranks = self.core.GetSelectedRanks()

            for r in ranks:
                self.core.RankDeleted(r[0])

# DEBUG
#       elif keyCode == 111: # 'o'
#           self.core.RankSwitchEndpoints()
#           self.field.Refresh()
#           return
#       elif keyCode == 112: # 'p'
#           self.OnAnimationBegin(event)
#           return
#       elif keyCode == 113: # 'q'
#           self.OnAnimationEnd(event)
#           return
#       elif keyCode == 114: # 'r'
#           d = wx.GetNumberFromUser("", "Measure:", "Remove Waypoint", 1, 1, 1000, self)
#           self.core.RemoveWayPoint(d)
#           return
#       elif keyCode == 115: # 's'
#           d = wx.GetNumberFromUser("", "Measure:", "Add Waypoint", 1, 1, 1000, self)
#           e = wx.GetNumberFromUser("", "Time (ms):", "Add Waypoint", 1, 1, 1000000, self)
#           self.core.AddWayPoint(d, e)
#           return
#       elif keyCode == 116: # 't'
#           e = wx.GetNumberFromUser("", "Count:", "Display Status at Count", 1, 1, 1000, self)
#           d = GUIDialogs.StatusAtCountDialog(self, self, e)
#           d.ShowModal()
#           d.Destroy()
#           return
#       elif keyCode == 117: # 'u'
#           self.core.SnapEndLocations()
#           self.field.Refresh(False)
#           self.RefreshMoveList()
#           return
#       elif keyCode == 118: # 'v'
#           self.core.SnapBeginLocations()
#           self.field.Refresh(False)
#           self.RefreshMoveList()
#           return
#       elif keyCode == 119: # 'w'
#           #change to not overwrite
#           moveList = self.core.GetMoves()
#           columnsArr = [] #User input
#           moveNames = []
#           commandStrings = []
#           i=0
#           while (i < len(moveList)):
#               self.core.ChangeMove(i)
#               self.BitmapGet().SaveFile("fieldPic"+ moveList[i][1] +".bmp", wx.BITMAP_TYPE_BMP)
#               commandStrings.append(self.core.GetCommandStrings())
#               moveNames.append(moveList[i][1])
#               columnsArr.append(4)
#               i= i+1

#           Printer.printDrill(self.core.GetSong(), "test.pdf", moveNames, commandStrings, 10, columnsArr)
        elif DEBUG and keyCode == 121: # 'y'
            self.field.DisplayRanksOn = not self.field.DisplayRanksOn
# DEBUG

#       elif keyCode == 42: # '*'
#           ranks = self.core.GetSelectedRanks()

#           for r in ranks:
#               if self.core.IsRankHeld(r[0]):
#                   self.core.RankUnlocked(r[0])
#               else:
#                   self.core.RankLocked(r[0])

#       elif keyCode == 43: # '+'
#           self.core.MakeSelectedRanksCurved()

#       elif keyCode == 45: # '-'
#           self.core.MakeSelectedRanksStraight()

        else:
            self.core.NameRank(unichr(keyCode))

        self.RefreshRankList()
        self.field.Refresh(False)
        self.RefreshMoveList()
        self.RefreshCommandList()
        self.RefreshStatusBar()

    def OnRankNameUnicode(self, event):
        d = GUIDialogs.RankUnicodeNameDialog(self)
        code = d.ShowModal()
        if code != -1:
            self.core.NameRank(unichr(code))

        self.RefreshRankList()
        self.RefreshCommandList()



app = wx.PySimpleApp()

frame = MainWindow(None)
app.MainLoop()
