__author__ = 'Dario'

import os.path

import wx
import contrib.FileBrowseButton as Filebrowser
import wx.lib.agw.genericmessagedialog as GMD

import FrameMYR
from notebook.tabs.ConfigTabPanels import BaseConfigTab, HeaderPanel


class MainConfigTab(BaseConfigTab):
    def __init__(self, configTab, parentNotebook):
        BaseConfigTab.__init__(self, configTab, parentNotebook)

    def getRightPanel(self, parent, parentNotebook):
        self.rightPanel = RightPanelAdvanced(self, parent, parentNotebook)

        return self.rightPanel

    def getHeaderPanel(self):
        return HeaderPanel(self, "Miner Scripts")

    def check_files_exist(self):
        #return True
        return ( self.rightPanel.algo_panel_scrypt.checkFileExists() and
                 self.rightPanel.algo_panel_groestl.checkFileExists() and
                 self.rightPanel.algo_panel_skein.checkFileExists() and
                 self.rightPanel.algo_panel_qubit.checkFileExists())

    def set_json(self, config_json):
        super(MainConfigTab, self).set_json(config_json)
        self.rightPanel.algo_panel_scrypt.set_script(self.get_value(config_json, 'scryptBatchFile') , self.get_value(config_json, 'scryptFactor'))
        self.rightPanel.algo_panel_groestl.set_script(self.get_value(config_json, 'groestlBatchFile'), self.get_value(config_json, 'groestlFactor'))
        self.rightPanel.algo_panel_skein.set_script(self.get_value(config_json, 'skeinBatchFile'), self.get_value(config_json, 'skeinFactor'))
        self.rightPanel.algo_panel_qubit.set_script(self.get_value(config_json, 'qubitBatchFile'), self.get_value(config_json, 'qubitFactor'))

    def get_json(self):
        json = super(MainConfigTab, self).get_json()

        json.update(self.rightPanel.get_json())

        return json

class RightPanelAdvanced(wx.Panel):
    def __init__(self, parent, parentPanel, parentNotebook):
        wx.Panel.__init__(self, parent=parentPanel, id=wx.ID_ANY)

        self.parent = parent
        self.parentNotebook = parentNotebook

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.algo_panel_scrypt = AlgoPanelAdvanced(self, BaseConfigTab.SCRYPT)
        self.algo_panel_groestl = AlgoPanelAdvanced(self, BaseConfigTab.GROESTL)
        self.algo_panel_skein = AlgoPanelAdvanced(self, BaseConfigTab.SKEIN)
        self.algo_panel_qubit = AlgoPanelAdvanced(self, BaseConfigTab.QUBIT)
        sizer.Add(self.algo_panel_scrypt, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(self.algo_panel_groestl, 0, wx.EXPAND | wx.TOP, 1)
        sizer.Add(self.algo_panel_skein, 0, wx.EXPAND | wx.TOP, 1)
        sizer.Add(self.algo_panel_qubit, 0, wx.EXPAND | wx.TOP, 1)

        self.SetSizer(sizer)

    def get_json(self):
        json = dict()

        try:
            json.update({'scryptBatchFile': self.algo_panel_scrypt.get_script()})

        except:
            print "Error: get_values - scryptBatchFile"
            pass

        try:
            json.update({'groestlBatchFile': self.algo_panel_groestl.get_script()})

        except:
            print "Error: get_values - groestlBatchFile"
            pass

        try:
            json.update({'skeinBatchFile': self.algo_panel_skein.get_script()})

        except:
            print "Error: get_values - skeinBatchFile"
            pass

        try:
            json.update({'qubitBatchFile': self.algo_panel_qubit.get_script()})

        except:
            print "Error: get_values - qubitBatchFile"
            pass

        return json

    def algoChecked(self, check):
        if BaseConfigTab.SCRYPT == str(check.LabelText):
            self.algo_panel_scrypt.fbb.Enable(check.GetValue())

        if BaseConfigTab.GROESTL == str(check.LabelText):
            self.algo_panel_groestl.fbb.Enable(check.GetValue())

        if BaseConfigTab.SKEIN == str(check.LabelText):
            self.algo_panel_skein.fbb.Enable(check.GetValue())

        if BaseConfigTab.QUBIT == str(check.LabelText):
            self.algo_panel_qubit.fbb.Enable(check.GetValue())

    def on_control_changed(self, event):
        self.parent.on_control_changed(event)

class AlgoPanelAdvanced(wx.Panel):
    def __init__(self, parent, algo):
        wx.Panel.__init__(self, parent=parent)

        self.algo = algo
        self.parent = parent

        self.fbb = FileBrowserMYR(
            self, size=(-1, 30), dialogTitle = 'Pick a script for ' + algo + " ...", fileMask='*.bat;*.sh', algoBrowser=self.algo, buttonSize=(32, 30)
        )

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.fbb, 1, wx.ALL, 0)
        self.SetSizer(sizer)

    #------------------------------------------------------------------------------------------
    #----------------------------         GETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def get_script(self):
        return self.fbb.value

    #------------------------------------------------------------------------------------------
    #----------------------------         SETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def set_script(self, script, factor):
        try:
            if script and script != self.fbb.value:
                self.fbb.SetValue(script)
        except:
            print "Error: set_script + " + str(script)

        self.fbb.Enable(factor)


    def checkFileExists(self):
        #todo: active_algo
        #self.parent.parent.leftPanel.algo_panel_scrypt.active_algo.GetValue()

        active_algo = self.parent.parent.leftPanel.isActiveAlgo(self.algo)
        #active_algo = False

        file_name = self.fbb.value

        if active_algo and not os.path.isfile(file_name):
            dlg = GMD.GenericMessageDialog(self, 'The file ' + file_name + "\nfor " + self.algo + " does not exist",
                                   self.algo + 'Configuration Error',
                                   wx.OK | wx.ICON_ERROR
            )

            dlg.ShowModal()
            dlg.Destroy()

            return False

        else:
            self.parent.on_control_changed(None)

            return True


class FileBrowserMYR(Filebrowser.FileBrowseButton):

    def __init__(self, parent, size, dialogTitle, fileMask, algoBrowser=None, buttonSize=(-1, -1)):
        self.algoBrowser = algoBrowser
        self.parent = parent

        iconPath = FrameMYR.FrameMYRClass.RESOURCE_PATH     + 'img/browse16.ico'
        Filebrowser.FileBrowseButton.__init__(self, parent=parent, id=wx.ID_ANY, size=size, labelText="", buttonText="", dialogTitle=dialogTitle, fileMask=fileMask, iconPath=iconPath, buttonSize=buttonSize)
        #self.value = self.GetValue().replace("\\", "\\\\")
        self.value = self.GetValue()

    def OnChanged(self, event):
        self.value = self.GetValue()
        self.parent.parent.on_control_changed(event)
        event.Skip()