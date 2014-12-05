__author__ = 'Dario'

from notebook.tabs import NotebookTab as nbt
import wx
import os.path
import wx.lib.filebrowsebutton as Filebrowser


class TabPanel(nbt.NotebookTab):
    def __init__(self, parent, frame_myr_p):
        nbt.NotebookTab.__init__(self, parent=parent, id=wx.ID_ANY)

        global frame_myr
        frame_myr = frame_myr_p

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.AddF(HeaderPanel(self), wx.SizerFlags().Expand().Border(wx.UP, 20))
        self.algo_panel_scrypt = AlgoPanel(self, "Scrypt ")
        self.algo_panel_groestl = AlgoPanel(self, "Groestl ")
        self.algo_panel_skein = AlgoPanel(self, "Skein ")
        self.algo_panel_qubit = AlgoPanel(self, "Qubit ")
        sizer.Add(self.algo_panel_scrypt, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.algo_panel_groestl, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.algo_panel_skein, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.algo_panel_qubit, 0, wx.EXPAND | wx.ALL, 0)

        self.idle_panel = IdlePanel(self)
        sizer.Add(self.idle_panel, 0, wx.EXPAND | wx.ALL, 0)

        panel_factor = wx.Panel(self)
        text_factor = wx.StaticText(panel_factor, wx.ID_ANY, "Efficiency (%)", size=(94, 28), style=wx.BOLD)
        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        text_factor.SetFont(font)
        sizer_factor = wx.BoxSizer(wx.HORIZONTAL)

        factors = []
        for i in range(100, 49, -1):
            factors.append(str(i) + "%")

        self.combo_factor = wx.ComboBox(panel_factor, -1, size=(52, 28), choices=factors, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.on_control_changed, self.combo_factor)
        sizer_factor.AddF(text_factor, wx.SizerFlags().Expand().Border(wx.LEFT | wx.TOP, 5))
        sizer_factor.Add(self.combo_factor, 0, 0)
        panel_factor.SetSizer(sizer_factor)
        sizer.AddF(panel_factor, wx.SizerFlags().Expand().Border(wx.UP, 0))

        #self.SetBackgroundColour("White")

        self.SetSizer(sizer)

        self.Show()

    def checkFilesExist(self):
        return ( self.algo_panel_scrypt.checkFileExists() and
                 self.algo_panel_groestl.checkFileExists() and
                 self.algo_panel_skein.checkFileExists() and
                 self.algo_panel_qubit.checkFileExists())

    def set_json(self, config_json):
        self.algo_panel_scrypt.set_values(config_json, "scryptFactor", "scryptBatchFile", "scryptHashRate", "scryptWatts")
        self.algo_panel_groestl.set_values(config_json, "groestlFactor", "groestlBatchFile","groestlHashRate", "groestlWatts")
        self.algo_panel_skein.set_values(config_json, "skeinFactor", "skeinBatchFile", "skeinHashRate", "skeinWatts")
        self.algo_panel_qubit.set_values(config_json, "qubitFactor", "qubitBatchFile", "qubitHashRate", "qubitWatts")
        self.idle_panel.set_idle_watts(config_json)
        self.set_global_factor(config_json)

    def set_global_factor(self, config_json):
        try:
            self.combo_factor.Select(100 - self.get_value(config_json, "globalCorrectionFactor"))
        except:
            print "Error: set_global_factor"

    def get_json(self):
        json = {}

        try:
            json.update(self.algo_panel_scrypt.get_values())
            json.update(self.algo_panel_groestl.get_values())
            json.update(self.algo_panel_skein.get_values())
            json.update(self.algo_panel_qubit.get_values())
            json.update(self.idle_panel.get_values())
            json.update(dict([("globalCorrectionFactor", float(self.combo_factor.GetValue()[:-1]))]))

        except:
            pass

        return json

    def on_control_changed(self, event):
        frame_myr.notebookControlChanged()


class HeaderPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)

        text_empty = wx.StaticText(self, wx.ID_ANY, size=(95, -1))
        text_browser = wx.StaticText(self, wx.ID_ANY, "Miner script", style=wx.BOLD)
        text_hr = wx.StaticText(self, wx.ID_ANY, "Mh/s", size=(53, 28), style=wx.BOLD)
        text_w = wx.StaticText(self, wx.ID_ANY, "Watts", size=(62, 28), style=wx.BOLD)

        text_browser.SetFont(font)
        text_hr.SetFont(font)
        text_w.SetFont(font)

        flags_browser = wx.SizerFlags(2)
        flags_browser.Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
        flags_browser.Expand().Border(wx.ALL, 1)

        sizer.AddF(text_empty, wx.SizerFlags().Border(wx.LEFT, 6))
        sizer.AddF(text_browser, flags_browser)
        sizer.AddF(text_hr, wx.SizerFlags().Expand().Border(wx.LEFT, 36))
        sizer.AddF(text_w, wx.SizerFlags().Expand().Border(wx.LEFT, 34))

        self.SetSizer(sizer)

        self.Show()


class AlgoPanel(wx.Panel):
    def __init__(self, parent, algo):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.algo = algo
        #self.status_bar = status_bar
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.active_algo = wx.CheckBox(self, -1, label=algo, size=(80, -1))
        #self.active_algo.Bind(wx.EVT_ENTER_WINDOW, frame_myr.on_mouse_over_active_algo)
        wx.EVT_ENTER_WINDOW(self.active_algo, self.on_mouse_over_active_algo)
        wx.EVT_LEAVE_WINDOW(self.active_algo, self.on_mouse_leave_active_algo)
        #wx.EVT_CHECKBOX(self.active_algo, self.on_control_changed)

        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self.active_algo.SetFont(font)
        self.active_algo.SetValue(True)

        self.fbb = FileBrowserMYR(
            self, size=(-1, 30), dialogTitle = 'Pick a script for ' + algo + " ...", fileMask='*.bat;*.sh', algoBrowser=self.algo
        )

        #self.hash_rate = masked.Ctrl(self, integerWidth=8, fractionWidth=0, controlType=masked.controlTypes.NUMBER)
        #self.watts = masked.Ctrl(self, integerWidth=6, fractionWidth=0, controlType=masked.controlTypes.NUMBER)
        self.hash_rate = wx.SpinCtrlDouble(self, value='0.00', size=(70,-1), min=0.0, max=9999.99, inc=0.01)
        self.hash_rate.SetDigits(2)
        #self.hash_rate = wx.SpinCtrl(self, -1, '0', min=0, max=999999, size=(70, -1))
        self.watts = wx.SpinCtrl(self, -1, '0', min=0, max=999999, size=(70, -1))
        #masked.EVT_NUM(self.hash_rate, self.on_control_changed)
        #masked.EVT_NUM(self.watts, self.on_control_changed)

        #self.Bind(wx.EVT_FILEPICKER_CHANGED, parent.on_control_changed, self.fbb.OnChanged(self))
        #self.fbb.OnChanged(self)

        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.hash_rate)
        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.hash_rate)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_CHECKBOX, self.enable_disable_controls, self.active_algo)

        sizer.Add(self.active_algo, 0, wx.ALL, 6)
        sizer.Add(self.fbb, 3, wx.ALL, 0)
        sizer.Add(self.hash_rate, 0, wx.ALL, 4)
        sizer.Add(self.watts, 0, wx.ALL, 4)
        self.SetSizer(sizer)

    #------------------------------------------------------------------------------------------
    #----------------------------         GETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def get_values(self):
        prefix = self.algo.strip().lower()

        values = dict()
        try:
            values[prefix + "Factor"] = self.active_algo.GetValue()
        except:
            print "Error: get_values - " + prefix + "Factor"
            pass
        try:
            values[prefix + "BatchFile"] = self.fbb.value
        except:
            print "Error: get_values - " + prefix + "BatchFile"
            pass
        try:
            #values[prefix + "HashRate"] = ( self.hash_rate.GetValue() ) / float(1000)
            values[prefix + "HashRate"] = self.hash_rate.GetValue()
        except:
            print "Error: get_values - " + prefix + "HashRate"
            pass
        try:
            values[prefix + "Watts"] = self.watts.GetValue()
        except:
            print "Error: get_values - " + prefix + "Watts"
            pass

        return values

    #------------------------------------------------------------------------------------------
    #----------------------------         SETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def set_values(self, config_json, factor, script, hash_rate, wats):
        p = self.GetParent()
        self.set_factor(p.get_value(config_json, factor))
        self.set_script(p.get_value(config_json, script))
        self.set_hash_rate(p.get_value(config_json, hash_rate))
        self.set_watts(p.get_value(config_json, wats))

        self.enable_disable_controls(self, False)

    def set_factor(self, factor):
        try:
            self.active_algo.SetValue(factor)
        except:
            print "Error: set_factor + " + str(factor)

    def set_script(self, script):
        try:
            if script and script != self.fbb.value:
                self.fbb.SetValue(script)
        except:
            print "Error: set_script + " + str(script)


    def set_hash_rate(self, hash_rate):
        try:
            #self.hash_rate.SetValue(hash_rate * 1000)
            self.hash_rate.SetValue(hash_rate)
        except:
            print "Error: set_hash_rate + " + str(hash_rate)

    def set_watts(self, watts):
        try:
            self.watts.SetValue(watts)
        except:
            print "Error: set_watts + " + str(watts)

    def enable_disable_controls(self, event, trigger_to_frame=True):
        self.fbb.Enable(self.active_algo.GetValue())
        self.hash_rate.Enable(self.active_algo.GetValue())
        self.watts.Enable(self.active_algo.GetValue())
        if trigger_to_frame:
            frame_myr.notebookControlChanged()

    def on_mouse_over_active_algo(self, event):
        evt = frame_myr.StatusBarEvent(message="Enable / Disable " + self.algo)
        wx.PostEvent(frame_myr, evt)

    def on_mouse_leave_active_algo(self, event):
        evt = frame_myr.StatusBarEvent(message="")
        wx.PostEvent(frame_myr, evt)

    def checkFileExists(self):
        active_algo = self.active_algo.GetValue()
        file_name = self.fbb.value

        if active_algo and not os.path.isfile(file_name):
            dlg = wx.MessageDialog(self, 'The file ' + file_name + "\nfor " + self.algo + " does not exist",
                                   self.algo + 'Configuration Error',
                                   wx.OK | wx.ICON_ERROR
            )

            dlg.ShowModal()
            dlg.Destroy()

            return False

        else:
            frame_myr.notebookControlChanged()

            return True


class IdlePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        text_factor = wx.StaticText(self, wx.ID_ANY, "Idle (W)", size=(54, 28), style=wx.BOLD)
        text_factor.SetFont(font)

        self.watts = wx.SpinCtrl(self, -1, '0', min=0, max=9999999, size=(70, -1))
        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.watts)

        sizer.Add((-1,-1), 0, wx.ALL, 6)
        sizer.Add((-1,-1), 3, wx.ALL, 0)
        sizer.AddF(text_factor, wx.SizerFlags().Expand().Border(wx.UP, 8))
        sizer.Add(self.watts, 0, wx.ALL, 4)
        self.SetSizer(sizer)

    def set_idle_watts(self, config_json):
        try:
            self.watts.SetValue(self.GetParent().get_value(config_json, "idleWatts"))
        except:
            print "Error: set_idle_watts"

    def get_values(self):
        values = dict()
        try:
            values ["idleWatts"] = self.watts.GetValue()
        except:
            print "Error: get_values - idleWatts"
            pass

        return values

class FileBrowserMYR(Filebrowser.FileBrowseButton):

    def __init__(self, parent, size, dialogTitle, fileMask, algoBrowser=None):
        self.algoBrowser = algoBrowser
        Filebrowser.FileBrowseButton.__init__(self, parent=parent, id=wx.ID_ANY, size=size, labelText="", dialogTitle=dialogTitle, fileMask=fileMask)
        #self.value = self.GetValue().replace("\\", "\\\\")
        self.value = self.GetValue()

    def OnChanged(self, event):
        self.value = self.GetValue()
        frame_myr.notebookControlChanged()
        event.Skip()