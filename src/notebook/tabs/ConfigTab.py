__author__ = 'Dario'

import wx

from notebook.tabs import NotebookTab as nbt
from notebook.tabs.SimpleConfigTab import SimpleConfigTab
from notebook.tabs.MainConfigTab import MainConfigTab
from event.EventLib import EVT_CONFIG_TAB_EVENT, EVT_CONFIG_MODE_EVENT


class ConfigTab(nbt.NotebookTab):
    def __init__(self, parent, frame_myr_p):
        nbt.NotebookTab.__init__(self, parent=parent, id=wx.ID_ANY)

        global frame_myr
        frame_myr = frame_myr_p
        self.parent = parent

        self.Bind(EVT_CONFIG_MODE_EVENT, self.onMainModeToggle)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.resizable_panel = wx.SplitterWindow(self, wx.ID_ANY)
        self.resizable_panel.SetMinimumPaneSize(1)

        self.simpleConfig = SimpleConfigTab(self.resizable_panel, self)
        self.advancedConfig = MainConfigTab(self.resizable_panel, self)

        self.advancedConfig.Bind(EVT_CONFIG_TAB_EVENT, self.on_control_changed)
        self.simpleConfig.Bind(EVT_CONFIG_TAB_EVENT, self.on_control_changed)

        self.sizer.Add(self.resizable_panel, 0, wx.EXPAND | wx.ALL, 0)

        self.showSimple()

        self.SetSizer(self.sizer)

        self.Show()

    def onMainModeToggle(self, event):
        if event.advanced:
            self.showAdvanced()
            #frame_myr.showAdvanced()
        else:
            self.showSimple()
            #frame_myr.showSimple()

    def on_control_changed(self, event):
        self.parent.notebookControlChanged(event)

        try:
            self.simpleConfig.rightPanel.algoChecked(event.EventObject)
            self.advancedConfig.rightPanel.algoChecked(event.EventObject)

        except AttributeError:
            pass

    def showSimple(self):
        self.simpleConfig.set_json(self.advancedConfig.get_json())
        self.resizable_panel.SplitHorizontally(self.simpleConfig, self.advancedConfig)
        self.resizable_panel.Unsplit(self.advancedConfig)

    def showAdvanced(self):
        self.advancedConfig.set_json(self.simpleConfig.get_json())
        self.resizable_panel.SplitHorizontally(self.simpleConfig, self.advancedConfig)
        self.resizable_panel.Unsplit(self.simpleConfig)

    def checkFilesExist(self):
        return self.advancedConfig.checkFilesExist()

    def set_json(self, config_json):
        try:
            mainMode = config_json['mainMode']

            if mainMode == "simple":
                self.showSimple()
            else:
                self.showAdvanced()

        except KeyError:
            pass

        self.advancedConfig.set_json(config_json)
        self.simpleConfig.set_json(config_json)

    def get_json(self):
        json = {}

        try:
            json.update(self.advancedConfig.get_json())
            json.update(self.simpleConfig.get_json())

        except:
            pass

        return json

    #def on_control_changed(self, event):
    #    frame_myr.notebookControlChanged()
