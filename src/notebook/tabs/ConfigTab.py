from notebook.tabs import NotebookTab as nbt

__author__ = 'Dario'

import wx

from notebook.tabs.SimpleConfigTab import SimpleConfigTab
from notebook.tabs.MainConfigTab import MainConfigTab
from event.EventLib import EVT_CONFIG_TAB_EVENT


class ConfigTab(nbt.NotebookTab):
    def __init__(self, parent_panel):
        nbt.NotebookTab.__init__(self, parent_panel=parent_panel, id=wx.ID_ANY)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.resizable_panel = wx.SplitterWindow(self, wx.ID_ANY)
        self.resizable_panel.SetMinimumPaneSize(1)

        self.simpleConfig = SimpleConfigTab(self.resizable_panel, parent_panel, self)
        self.advancedConfig = MainConfigTab(self.resizable_panel, parent_panel, self)

        self.advancedConfig.Bind(EVT_CONFIG_TAB_EVENT, self.on_control_changed)
        self.simpleConfig.Bind(EVT_CONFIG_TAB_EVENT, self.on_control_changed)

        self.sizer.Add(self.resizable_panel, 0, wx.EXPAND | wx.ALL, 0)

        self.showSimple()

        self.SetSizer(self.sizer)

        self.Show()

    def onBroadcastedEvent(self, event):
        if "main_config" == event.event_id:
            #if event.broadcast_event.GetEventObject().GetValue():
            #if event.broadcast_obj.GetValue():
            #if event.broadcast_event:
            if event.event_value:
                self.showAdvanced()

            else:
                self.showSimple()

    def on_control_changed(self, event):
        self.parentNotebook.notebookControlChanged(event)

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

    def check_files_exist(self):
        return self.advancedConfig.check_files_exist()

    def set_json(self, config_json):
        self.advancedConfig.set_json(config_json)
        self.simpleConfig.set_json(config_json)

    def get_json(self):
        #json = {"mainMode" : frame_myr.getMainMode()}
        json = {}

        try:
            json.update(self.advancedConfig.get_json())
            json.update(self.simpleConfig.get_json())

        except:
            pass

        return json

        #def on_control_changed(self, event):
        #    frame_myr.notebookControlChanged()
