__author__ = 'Dario'

import io

import wx
from wx.lib.mixins.listctrl import TextEditMixin
from ObjectListView import ObjectListView, ColumnDefn
import FrameMYR

from notebook.tabs.ConfigTabPanels import BaseConfigTab, HeaderPanel


POOLS_SCRYPT  = "poolsScrypt.conf"
POOLS_GROESTL = "poolsGroestl.conf"
POOLS_SKEIN   = "poolsSkein.conf"
POOLS_QUBIT   = "poolsQubit.conf"

class SimpleConfigTab(BaseConfigTab):
    def __init__(self, parent, parent_panel, configTab):
        BaseConfigTab.__init__(self, parent, parent_panel, configTab)

    def getRightPanel(self, parent):
        return RightPanelSimple(parent)

    def getHeaderPanel(self):
        return HeaderPanel(self, "Pools")

    def set_json(self, config_json):
        super(SimpleConfigTab, self).set_json(config_json)
        self.rightPanel.algo_panel_scrypt.set_pool(self.get_value(config_json, 'scryptPool') , self.get_value(config_json, 'scryptFactor'))
        self.rightPanel.algo_panel_groestl.set_pool(self.get_value(config_json, 'groestlPool'), self.get_value(config_json, 'groestlFactor'))
        self.rightPanel.algo_panel_skein.set_pool(self.get_value(config_json, 'skeinPool'), self.get_value(config_json, 'skeinFactor'))
        self.rightPanel.algo_panel_qubit.set_pool(self.get_value(config_json, 'qubitPool'), self.get_value(config_json, 'qubitFactor'))

    def get_json(self):
        json = super(SimpleConfigTab, self).get_json()

        json.update(self.rightPanel.get_json())

        return json

class RightPanelSimple(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.parent = parent

        sizer = wx.BoxSizer(wx.VERTICAL)

        #box = wx.StaticBoxSizer( wx.StaticBox( self, -1), wx.VERTICAL )

        self.algo_panel_scrypt = AlgoPanelSimple(self, BaseConfigTab.SCRYPT, POOLS_SCRYPT, size=(-1, 28))
        self.algo_panel_groestl = AlgoPanelSimple(self, BaseConfigTab.GROESTL, POOLS_GROESTL, size=(-1, 28))
        self.algo_panel_skein = AlgoPanelSimple(self, BaseConfigTab.SKEIN, POOLS_SKEIN, size=(-1, 28))
        self.algo_panel_qubit = AlgoPanelSimple(self, BaseConfigTab.QUBIT, POOLS_QUBIT, size=(-1, 28))
        sizer.Add(self.algo_panel_scrypt, 0, wx.EXPAND | wx.TOP, -3)
        sizer.Add(self.algo_panel_groestl, 0, wx.EXPAND | wx.TOP, 3)
        sizer.Add(self.algo_panel_skein, 0, wx.EXPAND | wx.TOP, 3)
        sizer.Add(self.algo_panel_qubit, 0, wx.EXPAND | wx.TOP, 3)

        self.SetSizer(sizer)

    def get_json(self):
        json = dict()

        try:
            json.update({'scryptPool': self.algo_panel_scrypt.get_pool()})

        except:
            print "Error: get_values - scryptPool"
            pass

        try:
            json.update({'groestlPool': self.algo_panel_groestl.get_pool()})

        except:
            print "Error: get_values - groestlPool"
            pass

        try:
            json.update({'skeinPool': self.algo_panel_skein.get_pool()})

        except:
            print "Error: get_values - skeinPool"
            pass

        try:
            json.update({'qubitPool': self.algo_panel_qubit.get_pool()})

        except:
            print "Error: get_values - qubitPool"
            pass

        return json

    def algoChecked(self, check):
        if BaseConfigTab.SCRYPT == str(check.LabelText):
            self.algo_panel_scrypt.poolsCombo.Enable(check.GetValue())

        if BaseConfigTab.GROESTL == str(check.LabelText):
            self.algo_panel_groestl.poolsCombo.Enable(check.GetValue())

        if BaseConfigTab.SKEIN == str(check.LabelText):
            self.algo_panel_skein.poolsCombo.Enable(check.GetValue())

        if BaseConfigTab.QUBIT == str(check.LabelText):
            self.algo_panel_qubit.poolsCombo.Enable(check.GetValue())

    def on_control_changed(self, event):
        self.parent.on_control_changed(event)


class AlgoPanelSimple(wx.Panel):
    def __init__(self, parent, algo, poolsFile, size=None):
        wx.Panel.__init__(self, parent=parent, size=size)

        self.algo = algo
        self.poolsFile = poolsFile

        self.poolList = self.readPoolsFile(poolsFile)
        boxWrapper = wx.BoxSizer(wx.HORIZONTAL)

        #text_browser = wx.StaticText(self, wx.ID_ANY, "Dev " + str(self.dev) + ":", style=wx.BOLD)
        self.poolsCombo = wx.ComboBox(self, size=(-1, -1), choices=self.poolList, style=wx.CB_READONLY)
        pool_editor = wx.Button(self, wx.ID_ANY, size=(36, -1))
        pool_editor.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH     + 'img/edit16.ico'))
        boxWrapper.Add( pool_editor, 0, wx.BOTTOM, -1)
        self.Bind(wx.EVT_BUTTON, self.onButton, pool_editor)
        #self.pool_editor = wx.ComboBox(self, size=(-1, 28), choices=pools, style=wx.CB_READONLY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        #sizer.AddF(wx.StaticText(self, wx.ID_ANY, size=(8, -1)), wx.SizerFlags().Border(wx.LEFT, 0))
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(8, -1)), 0, wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.poolsCombo, 1, wx.EXPAND | wx.TOP, 5)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(4, -1)), 0, wx.EXPAND | wx.TOP, 5)
        sizer.Add(boxWrapper, 0, wx.EXPAND | wx.TOP, 4)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(4, -1)), 0, wx.EXPAND | wx.TOP, 5)
        self.SetSizer(sizer)

    def readPoolsFile(self, poolsFile):
        f = open(poolsFile)
        self.poolList = f.read().splitlines()
        f.close()

        return self.poolList

    def onButton(self, event):
        dlg = PoolDialog(self, -1, "Edit " + self.algo + "pools...", self.poolList)
        res = dlg.ShowModal()
        scripts = dlg.scripts

        if res == 0 and scripts:
            f = io.open(self.poolsFile, 'wt', encoding='utf-8').write(unicode(scripts))

            self.poolsCombo.Clear()
            self.poolsCombo.AppendItems(self.readPoolsFile(self.poolsFile))

    #------------------------------------------------------------------------------------------
    #----------------------------         GETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def get_pool(self):
        return self.poolsCombo.GetValue()

    #------------------------------------------------------------------------------------------
    #----------------------------         SETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def set_pool(self, script, factor):
        try:
            if script and script != self.poolsCombo.GetValue():
                self.poolsCombo.SetValue(script)
        except:
            print "Error: set_pools + " + str(script)

        self.poolsCombo.Enable(factor)


class MyListCtrl(wx.ListCtrl, TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.ListCtrl.__init__(self, parent, ID, pos, size)
        TextEditMixin.__init__(self)

class PoolDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, poolList, size=wx.DefaultSize, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
            ):

        self.scripts = None

        # Instead of calling wx.Dialog.__init__ we precreate the dialog
        # so we can set an extra style that must be set before
        # creation, and then we create the GUI object using the Create
        # method.
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        # This next step is the most important, it turns this Python
        # object into the real wrapper of the dialog (instead of pre)
        # as far as the wxPython extension is concerned.
        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizerVertical = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.HORIZONTAL)

        #poolsPanel = MyListCtrl(self, wx.ID_ANY, size=(350, 500))
        #poolsPanel = wx.ListBox(self, wx.ID_ANY, size=(500, 500))
        #poolsPanel = dv.DataViewListCtrl(self)
        self.poolsPanel = ObjectListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.DOUBLE_BORDER, size=(540, 520))
        #poolsPanel.AppendTextColumn('Pool', width=500)
        self.poolsPanel.cellEditMode = ObjectListView.CELLEDIT_DOUBLECLICK
        #self.poolsPanel.Bind(EVT_SORT, lambda event: event.Skip())
        self.poolsPanel.Bind(wx.EVT_LIST_COL_CLICK, lambda : None)
        self.poolsPanel.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
        self.poolsPanel.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)
        #self.poolsPanel.Bind(wx.EVT_KILL_FOCUS, self.onPoolsListKillFocus)
        #self.poolsPanel.EnableSorting()

        self.poolsPanel.SetColumns([
            ColumnDefn("Pool URL", "left", 520, "pool")
        ])

        self.poolsPanel.SetFont(wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False))

        boxTextAdd = wx.BoxSizer(wx.HORIZONTAL)
        textAddLabel = wx.StaticText(self, wx.ID_ANY, "New pool: ")
        self.textAdd = wx.TextCtrl(self, wx.ID_ANY, size=(-1, 24))
        self.textAdd.Bind(wx.EVT_TEXT, self.onTextEnter)
        self.textAdd.Bind(wx.EVT_SET_FOCUS, self.onTextAddFocus)
        #self.textAdd.Bind(wx.EVT_KILL_FOCUS, self.onTextAddKillFocus)

        boxTextAdd.Add(textAddLabel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
        boxTextAdd.Add(self.textAdd, 1, wx.EXPAND | wx.ALL, 0)

        #poolsPanel = wx.RearrangeList(self, wx.ID_ANY, size=(350, 500))

        for pool in poolList:
            #poolsPanel.AddObjects(Pool(pool))
            self.poolsPanel.AddObjects([{"pool": pool}])
            #poolsPanel.AppendItem((pool,))

        box.Add(self.poolsPanel, 1, wx.EXPAND | wx.ALL, 3)

        sizerVertical.Add(box, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)

        #box = wx.BoxSizer(wx.HORIZONTAL)
        #
        #sizer.Add(box, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line1 = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        line2 = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        line3 = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizerVertical.Add(line1, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)

        #btnsizer = wx.StdDialogButtonSizer()
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        btnsizerAddRemove = wx.BoxSizer(wx.HORIZONTAL)
        btnsizerUpDown = wx.BoxSizer(wx.HORIZONTAL)
        btnsizerSaveCancel = wx.BoxSizer(wx.HORIZONTAL)

        #if wx.Platform != "__WXMSW__":
        #    btn = wx.ContextHelpButton(self)
        #    btnsizer.Add(btn)

        buttonWidth = 75
        self.btnAdd = wx.Button(self, wx.ID_ADD, size=FrameMYR.BUTTON_SIZE)
        self.btnRemove = wx.Button(self, wx.ID_REMOVE, size=FrameMYR.BUTTON_SIZE)
        self.btnMoveUp = wx.Button(self, wx.ID_UP, size=FrameMYR.BUTTON_SIZE)
        self.btnMoveDown = wx.Button(self, wx.ID_DOWN, size=FrameMYR.BUTTON_SIZE)
        self.btnSave = wx.Button(self, wx.ID_SAVE, size=FrameMYR.BUTTON_SIZE)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, size=FrameMYR.BUTTON_SIZE)

        self.btnAdd.Enable(False)
        self.btnRemove.Enable(False)
        self.btnMoveUp.Enable(False)
        self.btnMoveDown.Enable(False)

        self.btnAdd.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH      + 'img/add16.ico'), wx.LEFT)
        self.btnRemove.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/remove16.ico'), wx.LEFT)
        self.btnMoveUp.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/up16.ico'), wx.LEFT)
        self.btnMoveDown.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH + 'img/down16.ico'), wx.LEFT)
        self.btnSave.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH     + 'img/save16.ico'), wx.LEFT)
        self.btnCancel.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/cancel16.ico'), wx.LEFT)

        self.Bind(wx.EVT_BUTTON, self.onButtonAdd, self.btnAdd)
        self.Bind(wx.EVT_BUTTON, self.onButtonRemove, self.btnRemove)
        self.Bind(wx.EVT_BUTTON, self.onButtonUp, self.btnMoveUp)
        self.Bind(wx.EVT_BUTTON, self.onButtonDown, self.btnMoveDown)
        self.Bind(wx.EVT_BUTTON, self.onButtonSave, self.btnSave)

        #btnAdd.SetBitmapMargins((14,0))
        #btnRemove.SetBitmapMargins((14,0))
        #btnMoveUp.SetBitmapMargins((14,0))
        #btnMoveDown.SetBitmapMargins((14,0))
        #btnSave.SetBitmapMargins((14,0))
        #btnCancel.SetBitmapMargins((14,0))

        btnsizerAddRemove.Add(self.btnAdd, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, 2)
        btnsizerAddRemove.Add(self.btnRemove, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, 2)
        btnsizerUpDown.Add(self.btnMoveUp, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 2)
        btnsizerUpDown.Add(self.btnMoveDown, 0, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 2)
        btnsizerSaveCancel.Add(self.btnSave, 0, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL, 2)
        btnsizerSaveCancel.Add(self.btnCancel, 0, wx.ALIGN_RIGHT | wx.EXPAND | wx.ALL, 2)

        self.btnCancel.SetDefault()
        #btnsizer.Realize()

        sizerLine1 = wx.BoxSizer(wx.HORIZONTAL)
        sizerLine2 = wx.BoxSizer(wx.HORIZONTAL)
        sizerLine1.Add(wx.StaticText(self, wx.ID_ANY), 1, wx.ALIGN_CENTER | wx.ALL, 0)
        sizerLine1.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 32), style=wx.LI_VERTICAL), 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizerLine1.Add(wx.StaticText(self, wx.ID_ANY), 1, wx.ALIGN_CENTER | wx.ALL, 0)

        #sizerLine1.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 24), style=wx.LI_VERTICAL), 1, wx.ALIGN_CENTER | wx.ALL, 0)

        sizerLine2.Add(wx.StaticText(self, wx.ID_ANY), 1, wx.ALIGN_CENTER | wx.ALL, 0)
        sizerLine2.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 32), style=wx.LI_VERTICAL), 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizerLine2.Add(wx.StaticText(self, wx.ID_ANY), 1, wx.ALIGN_CENTER | wx.ALL, 0)

        #btnsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 24), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        btnsizer.Add(btnsizerAddRemove, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 2)
        btnsizer.Add(sizerLine1, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 0)
        btnsizer.Add(btnsizerUpDown, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 2)
        btnsizer.Add(sizerLine2, 1, wx.ALIGN_CENTER | wx.EXPAND | wx.ALL, 0)
        #btnsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 24), style=wx.LI_VERTICAL), 1, wx.EXPAND | wx.ALIGN_CENTER)
        btnsizer.Add(btnsizerSaveCancel, 0, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, 2)
        #btnsizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(-1, 24), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)

        sizerVertical.Add(boxTextAdd, 0, wx.EXPAND | wx.ALL, 3)
        sizerVertical.Add(line2, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)
        sizerVertical.Add(btnsizer, 0, wx.EXPAND | wx.ALL, 2)
        sizerVertical.Add(line3, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT)

        self.SetSizer(sizerVertical)
        sizerVertical.Fit(self)

    def onButtonAdd(self, event):
        index = self.poolsPanel.GetFirstSelected()
        object = {"pool": self.textAdd.GetValue()}

        if index >= 0:
            objects = self.poolsPanel.GetObjects()
            objects.insert(index, object)
            self.poolsPanel.SetObjects(objects)

            self.poolsPanel.SelectObjects([self.poolsPanel.GetObjects()[index]])

        else:
            self.poolsPanel.AddObjects([object])

        event.Skip()

    def onButtonRemove(self, event):
        self.poolsPanel.RemoveObjects(self.poolsPanel.GetSelectedObjects())
        self.btnRemove.Enable(False)
        self.btnMoveUp.Enable(False)
        self.btnMoveDown.Enable(False)

        event.Skip()

    def onButtonUp(self, event):
        objects = self.poolsPanel.GetObjects()

        oldIndex = self.poolsPanel.GetFirstSelected()

        if oldIndex >= 0:
            newIndex = oldIndex - 1

            objects.insert(newIndex, objects.pop(oldIndex))

            self.poolsPanel.SetObjects(objects)
            self.poolsPanel.SetFocus()
            self.poolsPanel.SelectObjects([self.poolsPanel.GetObjects()[newIndex]])

        event.Skip()

    def onButtonDown(self, event):
        objects = self.poolsPanel.GetObjects()

        oldIndex = self.poolsPanel.GetFirstSelected()

        if oldIndex >= 0:
            newIndex = oldIndex + 1

            objects.insert(newIndex, objects.pop(oldIndex))

            self.poolsPanel.SetObjects(objects)
            self.poolsPanel.SetFocus()
            self.poolsPanel.SelectObjects([self.poolsPanel.GetObjects()[newIndex]])

        event.Skip()

    def onButtonSave(self, event):
        objects = self.poolsPanel.GetObjects()
        self.scripts = ""

        for obj in objects:
            self.scripts += obj["pool"] + "\n"

        self.Destroy()

        event.Skip()

    def onTextEnter(self, event):
        textIsNotNull = self.textAdd.GetValue() != ""

        self.btnAdd.Enable(textIsNotNull)

        event.Skip()

    def onItemSelected(self, event):
        singleSelection = len(self.poolsPanel.GetSelectedObjects()) == 1
        multiSelection  = len(self.poolsPanel.GetSelectedObjects()) > 0

        firstSelected = self.poolsPanel.GetFirstSelected() == 0
        lastSelected = self.poolsPanel.GetFirstSelected() == len(self.poolsPanel.GetObjects()) - 1

        #hasFocusPoolsPanel = self.poolsPanel.HasFocus()

        self.btnRemove.Enable(multiSelection)
        self.btnMoveUp.Enable(singleSelection and not firstSelected)
        self.btnMoveDown.Enable(singleSelection and not lastSelected)

        event.Skip()

    def onPoolsListKillFocus(self, event):
        #hasFocusPoolsPanel = self.poolsPanel.HasFocus()

        self.btnRemove.Enable(False)
        self.btnMoveUp.Enable(False)
        self.btnMoveDown.Enable(False)

        event.Skip()

    def onTextAddFocus(self, event):
        #hasFocusTextAdd = self.textAdd.HasFocus()
        #textIsNotNull = self.textAdd.GetValue() != ""

        self.btnRemove.Enable(False)
        self.btnMoveUp.Enable(False)
        self.btnMoveDown.Enable(False)

        event.Skip()

    #def onTextAddKillFocus(self, event):
    #    self.btnAdd.SetFocus(True)


class Pool(object):
    """
    Simple minded object that represents a song in a music library
    """
    def __init__(self, pool):
        self.title = pool

    def __getitem__(self):
        return self.title

