__author__ = 'Dario'

import wx
from notebook.ExpandableNotebook import EVT_NOTEBOOK_BROADCAST_EVENT

class ExpandableNotebookTab(wx.Panel):
    def __init__(self, parent_panel, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent=parent_panel, id=wx.ID_ANY)
        self.parentNotebook = parent_panel
        self.id = id

        self.Bind(EVT_NOTEBOOK_BROADCAST_EVENT, self.onBroadcastedEvent)

    def get_value(self, json, field_name):
        value = None
        try:
            value = json[field_name]

        except KeyError:
            #print(str(self) + " Error: get_value(" + field_name + ") - Not Found in json")
            pass

        return value

    def set_value(self, json, field_name, value):
        try:
            json[field_name] = value

        except:
            print(str(self) + " Error: set_value(" + field_name + ")")

    def check_files_exist(self):
        return True

    def set_json(self, config_json):
        pass

    def get_json(self):
        pass

    def loadDefaults(self):
        pass

    def onBroadcastedEvent(self, event):
        pass