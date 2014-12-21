from notebook.tabs import NotebookTab as nbt

__author__ = 'Dario'

import wx

from notebook.tabs.SimpleConfigTab import SimpleConfigTab
from notebook.tabs.MainConfigTab import MainConfigTab
from event.EventLib import EVT_CONFIG_TAB_EVENT


class ConfigTab(nbt.NotebookTab):
    def __init__(self, parentNotebook):
        nbt.NotebookTab.__init__(self, parentNotebook=parentNotebook, id=wx.ID_ANY)

        self.parentNotebook = parentNotebook

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.simpleConfig = SimpleConfigTab(self, parentNotebook)
        self.advancedConfig = MainConfigTab(self, parentNotebook)

        self.advancedConfig.Bind(EVT_CONFIG_TAB_EVENT, self.on_control_changed)
        self.simpleConfig.Bind(EVT_CONFIG_TAB_EVENT, self.on_control_changed)

        self.sizer.Add(self.simpleConfig, 0, wx.EXPAND | wx.ALL, 0)
        self.sizer.Add(self.advancedConfig, 0, wx.EXPAND | wx.ALL, 0)

        self.mainMode = "simple"
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

        if "start_mining" == event.event_id:
            self.simpleConfig.leftPanel.algoButtonColorsMining(algo=event.event_value)
            self.advancedConfig.leftPanel.algoButtonColorsMining(algo=event.event_value)

        if "stop_mining" == event.event_id:
            self.simpleConfig.leftPanel.algoButtonColorsStopped()
            self.advancedConfig.leftPanel.algoButtonColorsStopped()

    def on_control_changed(self, event):
        self.parentNotebook.notebookControlChanged(event)

        try:
            self.simpleConfig.rightPanel.algoChecked(event.GetEventObject())
            self.advancedConfig.rightPanel.algoChecked(event.GetEventObject())

        except AttributeError:
            pass

    def showSimple(self):
        self.simpleConfig.set_json(self.advancedConfig.get_json())

        self.advancedConfig.Hide()
        self.simpleConfig.Show()

        self.Layout()
        self.parentNotebook.Layout()

        self.mainMode = "simple"

    def showAdvanced(self):
        self.advancedConfig.set_json(self.simpleConfig.get_json())

        self.simpleConfig.Hide()
        self.advancedConfig.Show()

        self.Layout()
        self.parentNotebook.Layout()

        self.mainMode = "advanced"

    def check_files_exist(self):
        return self.mainMode == "simple" or self.advancedConfig.check_files_exist()

    def set_json(self, config_json):
        self.advancedConfig.set_json(config_json)
        self.simpleConfig.set_json(config_json)

    def get_json(self):
        #json = {"mainMode" : frame_myr.getMainMode()}
        json = {}

        try:
            #The last panel to update the config dict must be the active one
            #in order to not overwrite common fields with invalid data
            if (self.mainMode == "simple"):
                json.update(self.advancedConfig.get_json())
                json.update(self.simpleConfig.get_json())

            else:
                json.update(self.simpleConfig.get_json())
                json.update(self.advancedConfig.get_json())

        except:
            pass

        return json
