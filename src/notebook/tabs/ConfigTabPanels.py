from notebook.tabs import NotebookTab as nbt

__author__ = 'Dario'

import wx
from event.EventLib import StatusBarEvent


class BaseConfigTab(nbt.NotebookTab):
    SCRYPT  = "Scrypt "
    GROESTL = "Groestl "
    SKEIN   = "Skein "
    QUBIT   = "Qubit "

    def __init__(self, parent, parent_panel, configTab):
        nbt.NotebookTab.__init__(self, parent_panel=parent, id=wx.ID_ANY)

        self.parentNotebook = parent_panel

        self.configTab = configTab
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #self.sizer.AddF(HeaderPanel(self), wx.SizerFlags().Expand().Border(wx.UP, 20))
        self.sizer.AddF(self.getHeaderPanel(), wx.SizerFlags().Expand().Border(wx.UP, 20))

        dataPanel = wx.Panel(self)
        sizerData = wx.BoxSizer(wx.HORIZONTAL)

        self.leftPanel  = LeftPanel(self, dataPanel)
        #rightPanel = LeftPanel(dataPanel)
        self.rightPanel = self.getRightPanel(dataPanel)
        #rightPanel = wx.Panel(dataPanel)
        sizerData.Add(self.leftPanel, 0, wx.EXPAND | wx.ALL, 0)
        sizerData.Add(self.rightPanel, 1, wx.EXPAND | wx.TOP, 2)

        dataPanel.SetSizer(sizerData)

        self.sizer.Add(dataPanel, 1, wx.EXPAND | wx.RIGHT, 4)

        self.idle_panel = LowerConfigPanel(self)
        self.sizer.Add(self.idle_panel, 0, wx.EXPAND | wx.ALL, 0)

        self.SetBackgroundColour("White")

        self.SetSizer(self.sizer)

        self.Show()

    #overridden
    def getRightPanel(self, parent):
        pass

    def getHeaderPanel(self):
        pass

    def set_json(self, config_json):
        self.idle_panel.set_idle_watts(self.get_value(config_json, "idleWatts"))
        self.idle_panel.set_global_factor(self.get_value(config_json, "globalCorrectionFactor"))

        self.leftPanel.set_json(config_json)
        #self.rightPanel.set_json(config_json)

    def get_json(self):
        json = self.leftPanel.get_json()

        try:
            json.update(dict([("idleWatts", self.idle_panel.get_idle_watts())]))

        except:
            print "Error: get_json(idleWatts)"
            pass

        try:
            json.update(dict([("globalCorrectionFactor", self.idle_panel.get_global_factor()[:-1])]))

        except:
            print "Error: get_json(globalCorrectionFactor)"
            pass

        return json

    def on_control_changed(self, event=None):
        #self.on_control_changed(event)
        self.configTab.on_control_changed(event)


class HeaderPanel(wx.Panel):
    def __init__(self, parent, text):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)

        text_hashrate = wx.StaticText(self, wx.ID_ANY, "Mh/s", size=(53, 28), style=wx.BOLD)
        text_watts = wx.StaticText(self, wx.ID_ANY, "Watts", size=(62, 28), style=wx.BOLD)
        text_browser = wx.StaticText(self, wx.ID_ANY, text, style=wx.BOLD)

        text_browser.SetFont(font)
        text_hashrate.SetFont(font)
        text_watts.SetFont(font)

        flags_browser = wx.SizerFlags(2)
        flags_browser.Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
        flags_browser.Expand().Border(wx.ALL, 1)

        sizer.AddF(wx.StaticText(self, wx.ID_ANY, size=(55, -1)), wx.SizerFlags().Border(wx.LEFT, 6))
        sizer.AddF(text_hashrate, wx.SizerFlags().Expand().Border(wx.LEFT, 40))
        sizer.AddF(text_watts, wx.SizerFlags().Expand().Border(wx.LEFT, 24))
        sizer.AddF(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), wx.SizerFlags().Border(wx.LEFT, 6))
        sizer.AddF(text_browser, flags_browser)

        self.SetSizer(sizer)

        self.Show()


class LeftPanel(wx.Panel):
    def __init__(self, baseConfigTab, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.baseConfigTab = baseConfigTab

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.algo_panel_dict = {}

        self.algo_panel_scrypt = AlgoPanelData(self, BaseConfigTab.SCRYPT)
        self.algo_panel_groestl = AlgoPanelData(self, BaseConfigTab.GROESTL)
        self.algo_panel_skein = AlgoPanelData(self, BaseConfigTab.SKEIN)
        self.algo_panel_qubit = AlgoPanelData(self, BaseConfigTab.QUBIT)
        sizer.Add(self.algo_panel_scrypt, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.algo_panel_groestl, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.algo_panel_skein, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.algo_panel_qubit, 0, wx.EXPAND | wx.ALL, 0)

        self.algo_panel_dict[BaseConfigTab.SCRYPT] = self.algo_panel_scrypt
        self.algo_panel_dict[BaseConfigTab.GROESTL] = self.algo_panel_groestl
        self.algo_panel_dict[BaseConfigTab.SKEIN] = self.algo_panel_skein
        self.algo_panel_dict[BaseConfigTab.QUBIT] = self.algo_panel_qubit

        self.SetSizer(sizer)

    def set_json(self, config_json):
        self.algo_panel_scrypt.set_values(config_json, factor='scryptFactor', hash_rate='scryptHashRate', wats='scryptWatts')
        self.algo_panel_groestl.set_values(config_json, factor='groestlFactor', hash_rate='groestlHashRate', wats='groestlWatts')
        self.algo_panel_skein.set_values(config_json, factor='skeinFactor', hash_rate='skeinHashRate', wats='skeinWatts')
        self.algo_panel_qubit.set_values(config_json, factor='qubitFactor', hash_rate='qubitHashRate', wats='qubitWatts')

    def get_json(self):
        json = {}

        json.update(self.algo_panel_scrypt.get_json())
        json.update(self.algo_panel_groestl.get_json())
        json.update(self.algo_panel_skein.get_json())
        json.update(self.algo_panel_qubit.get_json())

        return json

    def on_control_changed(self, event):
        self.baseConfigTab.on_control_changed(event)

    def isActiveAlgo(self, algo):
        return self.algo_panel_dict[algo].isActiveAlgo()
        #return self.algo_panel_scrypt.isActiveAlgo()


class AlgoPanelData(wx.Panel):
    def __init__(self, parent, algo):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.algo = algo
        self.parent = parent

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.active_algo = wx.CheckBox(self, -1, label=algo, size=(80, -1))
        #self.active_algo.Bind(wx.EVT_ENTER_WINDOW, frame_myr.on_mouse_over_active_algo)
        wx.EVT_ENTER_WINDOW(self.active_algo, self.on_mouse_over_active_algo)
        wx.EVT_LEAVE_WINDOW(self.active_algo, self.on_mouse_leave_active_algo)
        #wx.EVT_CHECKBOX(self.active_algo, self.on_control_changed)

        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        self.active_algo.SetFont(font)
        #self.active_algo.SetValue(True)

        self.hash_rate = wx.SpinCtrlDouble(self, value='0.00', size=(70,-1), min=0.0, max=9999.99, inc=0.01)
        self.hash_rate.SetDigits(2)
        self.watts = wx.SpinCtrl(self, -1, '0', min=0, max=999999, size=(70, -1))

        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.hash_rate)
        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.hash_rate)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_CHECKBOX, self.on_control_changed, self.active_algo)

        sizer.Add(self.active_algo, 0, wx.ALL, 6)
        sizer.Add(self.hash_rate, 0, wx.ALL, 4)
        sizer.Add(self.watts, 0, wx.ALL, 4)
        self.SetSizer(sizer)

    #------------------------------------------------------------------------------------------
    #----------------------------         GETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def get_json(self):
        prefix = self.algo.strip().lower()

        values = dict()
        try:
            values[prefix + "Factor"] = self.active_algo.GetValue()
        except:
            print "Error: get_values - " + prefix + "Factor"
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

    def set_values(self, config_json, **kwargs):
        p = self.parent.baseConfigTab
        self.set_factor(p.get_value(config_json, kwargs.pop('factor')))
        self.set_hash_rate(p.get_value(config_json, kwargs.pop('hash_rate')))
        self.set_watts(p.get_value(config_json, kwargs.pop('wats')))

        self.on_control_changed(self, False)

    def set_factor(self, factor):
        try:
            self.active_algo.SetValue(factor)
        except:
            print "Error: set_factor + " + str(factor)

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

    def isActiveAlgo(self):
        return self.active_algo.GetValue()

    def on_control_changed(self, event, trigger_to_frame=True):
        #self.fbb.Enable(self.active_algo.GetValue())
        self.hash_rate.Enable(self.active_algo.GetValue())
        self.watts.Enable(self.active_algo.GetValue())
        if trigger_to_frame:
            self.parent.on_control_changed(event)

    def on_mouse_over_active_algo(self, event):
        wx.PostEvent(self.parent.baseConfigTab.parentNotebook.getParentWindow(),
                     StatusBarEvent(message="Enable / Disable " + self.algo + " - " + str(self.active_algo.GetValue())))

    def on_mouse_leave_active_algo(self, event):
        wx.PostEvent(self.parent.baseConfigTab.parentNotebook.getParentWindow(), StatusBarEvent(message=""))


class LowerConfigPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.parent = parent

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #font = wx.Font(-1, wx.DECORATIVE, wx.ITALIC, wx.BOLD)
        text_idle = wx.StaticText(self, wx.ID_ANY, "Idle (W)", size=(54, 28), style=wx.BOLD)
        text_idle.SetFont(font)

        self.watts = wx.SpinCtrl(self, -1, '0', min=0, max=9999999, size=(70, -1))
        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.watts)

        #sizer.Add((-1,-1), 0, wx.ALL, 116)
        #sizer.Add((-1,-1), 3, wx.ALL, 0)
        sizer.AddF(wx.StaticText(self, wx.ID_ANY, size=(114, -1)), wx.SizerFlags().Border(wx.LEFT, 6))
        sizer.AddF(text_idle, wx.SizerFlags().Expand().Border(wx.TOP, 24))
        sizer.Add(self.watts, 0, wx.TOP, 20)

        #global factor

        text_factor = wx.StaticText(self, wx.ID_ANY, "Efficiency (%)", size=(90, 28), style=wx.BOLD)
        text_factor.SetFont(wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        factors = []
        for i in range(100, 49, -1):
            factors.append(str(i) + "%")

        self.combo_factor = wx.ComboBox(self, -1, size=(52, 28), choices=factors, style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.parent.on_control_changed, self.combo_factor)
        sizer.AddF(wx.StaticText(self, wx.ID_ANY, size=(194, -1)), wx.SizerFlags().Border(wx.LEFT, 6))
        #sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(194, -1)), 0, wx.EXPAND | wx.LEFT, 6)
        sizer.AddF(text_factor, wx.SizerFlags().Expand().Border(wx.TOP, 24))
        sizer.Add(self.combo_factor, 0, wx.TOP, 20)

        self.SetSizer(sizer)

    #------------------------------------------------------------------------------------------
    #----------------------------         GETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def get_idle_watts(self):
        return self.watts.GetValue()

    def get_global_factor(self):
        return self.combo_factor.GetValue()

    #------------------------------------------------------------------------------------------
    #----------------------------         SETTERS           -----------------------------------
    #------------------------------------------------------------------------------------------

    def set_idle_watts(self, idle_watts):
        try:
            self.watts.SetValue(idle_watts)
        except:
            print "Error: set_idle_watts"

    def set_global_factor(self, global_factor):
        try:
            if global_factor:
                self.combo_factor.Select(100 - int(global_factor))
            #self.combo_factor.Select(global_factor)
        except:
            print "Error: set_global_factor"