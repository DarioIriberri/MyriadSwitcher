__author__ = 'Dario'

import wx

class NotebookTab(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.id = id

    def get_value(self, json, field_name):
        value = None
        try:
            value = json[field_name]

        except:
            print("Error: get_value(" + field_name + ") - Not Found in json")
            pass

        return value

    def set_value(self, json, field_name, value):
        try:
            json[field_name] = value

        except:
            print("Error:  set_value(" + field_name + ")")
