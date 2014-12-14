__author__ = 'Dario'


import wx
import sys
import NotebookTab as nbt

SLIDER_MAX = 1000


class SwitchingModesTab(nbt.NotebookTab):
    def __init__(self, parent, frame_myr_p, tab=None):
        nbt.NotebookTab.__init__(self, parent=parent, id=wx.ID_ANY)

        global frame_myr
        frame_myr = frame_myr_p

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.modes_panel = ModesPanel(self)
        self.data_panel = DataPanel(self)

        sizer.Add(self.modes_panel, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.data_panel, 1, wx.EXPAND | wx.ALL, 5)

        #self.SetBackgroundColour("White")

        self.SetSizer(sizer)
        self.Show()

        # Internal variables
        self.base = float()
        self.config_json = {}
        self.att_watts = float()

    def get_json(self):
        json = self.modes_panel.get_values()

        return json

    def set_json(self, config_json):
        self.modes_panel.set_values(config_json, "mode", "attenuation", "minCoins")
        try:
            self.config_json = config_json
            self.calculateExpected()
        except:
            print "Error: calculateExpected"


    def calculateExpected(self):
        if not self.config_json:
            return
        #min_coins = int(config_json["minCoins"])
        #self.config_json = config_json

        attenuation = self.modes_panel.slider.GetValue()
        min_coins = self.modes_panel.min_v.GetValue()

        mode = self.modes_panel.getActiveMode()

        w_scrypt  = float(self.config_json["scryptWatts"])
        w_groestl = float(self.config_json["groestlWatts"])
        w_skein   = float(self.config_json["skeinWatts"])
        w_qubit   = float(self.config_json["qubitWatts"])

        avg_watts = self.average([w_scrypt, w_groestl, w_skein, w_qubit])

        self.base = avg_watts ** (2 / float(SLIDER_MAX))

        if mode == 1:
            self.att_watts = sys.maxint
        else:
            if mode == 2:
                self.att_watts = 0
            else:
                self.att_watts = self.base ** long(attenuation)

        self.att_w_scrypt  = w_scrypt  + self.att_watts
        self.att_w_groestl = w_groestl + self.att_watts
        self.att_w_skein   = w_skein   + self.att_watts
        self.att_w_qubit   = w_qubit   + self.att_watts

        avg_att_watts = self.average([self.att_w_scrypt, self.att_w_groestl, self.att_w_skein, self.att_w_qubit])

        weight_format_s = "{:3.1f}%"
        mins_format_s = "{:6.0f}"
        per_w_format_s = "{:4.2f}"

        weight_scrypt = weight_format_s.format((avg_att_watts / self.att_w_scrypt) * 100)
        mins_scrypt_n   = (min_coins / avg_att_watts) * self.att_w_scrypt
        mins_scrypt   = mins_format_s.format(mins_scrypt_n)
        per_w_scrypt_n  = float(mins_scrypt) / w_scrypt
        per_w_scrypt  = per_w_format_s.format(per_w_scrypt_n)

        weight_groestl = weight_format_s.format((avg_att_watts / self.att_w_groestl) * 100)
        mins_groestl_n   = (min_coins / avg_att_watts) * self.att_w_groestl
        mins_groestl   = mins_format_s.format(mins_groestl_n)
        per_w_groestl_n  = float(mins_groestl) / w_groestl
        per_w_groestl  = per_w_format_s.format(per_w_groestl_n)

        weight_skein = weight_format_s.format((avg_att_watts / self.att_w_skein) * 100)
        mins_skein_n   = (min_coins / avg_att_watts) * self.att_w_skein
        mins_skein   = mins_format_s.format(mins_skein_n)
        per_w_skein_n  = float(mins_skein) / w_skein
        per_w_skein  = per_w_format_s.format(per_w_skein_n)

        weight_qubit = weight_format_s.format((avg_att_watts / self.att_w_qubit) * 100)
        mins_qubit_n   = (min_coins / avg_att_watts) * self.att_w_qubit
        mins_qubit   = mins_format_s.format(mins_qubit_n)
        per_w_qubit_n  = float(mins_qubit) / w_qubit
        per_w_qubit  = per_w_format_s.format(per_w_qubit_n)

        self.data_panel.algo_panel_scrypt.set_values( weight_scrypt, mins_scrypt, per_w_scrypt )
        self.data_panel.algo_panel_groestl.set_values( weight_groestl, mins_groestl, per_w_groestl )
        self.data_panel.algo_panel_skein.set_values( weight_skein, mins_skein, per_w_skein )
        self.data_panel.algo_panel_qubit.set_values( weight_qubit, mins_qubit, per_w_qubit )

        avg_mins  = mins_format_s.format(self.average([mins_scrypt_n, mins_groestl_n, mins_skein_n, mins_qubit_n]))
        avg_per_w = per_w_format_s.format(self.average([per_w_scrypt_n, per_w_groestl_n, per_w_skein_n, per_w_qubit_n]))

        self.data_panel.avg_panel.set_values( avg_mins, avg_per_w )

    def average(self, vals):
        return sum(vals) / float(len(vals))

    def on_control_changed(self, event):
        frame_myr.notebookControlChanged()
        self.calculateExpected()


class ModesPanel(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__( self, parent, -1)

        vs = wx.BoxSizer( wx.VERTICAL )

        box1_title = wx.StaticBox( self, -1, "Switching Mode" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )
        grid1 = wx.FlexGridSizer( cols=2 )

        self.text_hybrid = "Hybrid Mode (0: Max/Watt, " + str(SLIDER_MAX) + ": Max/Day)"

        # 1st group of controls:
        self.group1_ctrls = []
        self.radioPerDay = wx.RadioButton( self, -1, label=str(), style = wx.RB_GROUP )
        self.radioPerWatt = wx.RadioButton( self, -1, label=str() )
        self.radioHybrid = wx.RadioButton( self, -1, label=str() )
        self.textPerDay = wx.StaticText( self, -1, "Maximize coins per Day" )
        self.textPerWatt = wx.StaticText( self, -1, "Maximize coins per Watt" )
        self.textHybrid = wx.StaticText( self, -1, self.text_hybrid )
        self.group1_ctrls.append((self.radioPerDay, self.textPerDay))
        self.group1_ctrls.append((self.radioPerWatt, self.textPerWatt))
        self.group1_ctrls.append((self.radioHybrid, self.textHybrid))

        for radio, text in self.group1_ctrls:
            grid1.Add( radio, 0, wx.ALIGN_RIGHT|wx.LEFT | wx.TOP, 5 )
            grid1.Add( text, 0, wx.ALIGN_LEFT|wx.LEFT | wx.TOP, 5 )

        wx.StaticText(self, -1, "", (40, 15))

        self.slider = wx.Slider(
            self, wx.ID_ANY, SLIDER_MAX / 2, 0, SLIDER_MAX, (30, 60), (254, -1),
            wx.SL_HORIZONTAL | wx.SL_LABELS
        )

        self.slider.SetTickFreq(5, 1)
        self.Bind(wx.EVT_SLIDER, parent.on_control_changed, self.slider)

        box1.Add( grid1, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.slider, 0, wx.ALIGN_LEFT | wx.ALL, 5 )

        mins_box = self.create_mins_sizer(parent)
        vs.Add( box1, 0, wx.ALIGN_CENTRE_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        vs.Add( mins_box, 1, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 2 )

        self.SetSizer(vs)
        vs.Fit( self )
        self.Move((11, 11))
        self.panel = self

        #self.SetBackgroundColour("White")

        for radio, text in self.group1_ctrls:
            self.Bind(wx.EVT_RADIOBUTTON, self.OnModeSelect, radio )

        for radio, text in self.group1_ctrls:
            radio.SetValue(0)
            text.Enable(False)

    def set_values(self, config_json, mode, attenuation, minCoins):
        p = self.GetParent()
        self.set_mode(p.get_value(config_json, mode))
        self.set_attenuation(p.get_value(config_json, attenuation))
        self.set_min_coins(p.get_value(config_json, minCoins))

    def set_mode(self, mode):
        try:
            for i in range (0, len(self.group1_ctrls)):
                if mode == i + 1:
                    self.group1_ctrls[i][0].SetValue(1)
                    self.group1_ctrls[i][1].Enable(True)
                else:
                    self.group1_ctrls[i][0].SetValue(0)
                    self.group1_ctrls[i][1].Enable(False)

            if mode == 3:
                self.slider.Enable(True)
            else:
                self.slider.Enable(False)

        except:
            print "Error: set_mode + " + str(mode)

    def set_attenuation(self, attenuation):
        try:
           self.slider.SetValue(attenuation)

        except:
            print "Error: set_attenuation + " + str(attenuation)

    def set_min_coins(self, min_coins):
        try:
            self.min_v.SetValue(min_coins)

        except:
            print "Error: set_min_coins + " + str(min_coins)

    def get_values(self):
        values = dict()

        try:
            values["mode"] = self.getActiveMode()

        except:
            print "Error: get_values - mode"
            pass
        try:
            values["attenuation"] = self.slider.GetValue()

        except:
            print "Error: get_values - attenuation"
            pass
        try:
            values["minCoins"] = self.min_v.GetValue()

        except:
            print "Error: get_values - minCoins"
            pass

        return values

    def getActiveMode(self):
        for i in range (0, len(self.group1_ctrls)):
            if self.group1_ctrls[i][0].GetValue():
                return i + 1

    def OnModeSelect( self, event ):
        radio_selected = event.GetEventObject()

        for radio, text in self.group1_ctrls:
            if radio is radio_selected:
                text.Enable(True)
                if text.Label == self.text_hybrid:
                    self.slider.Enable(True)
                else:
                    self.slider.Enable(False)
            else:
                text.Enable(False)

        frame_myr.notebookControlChanged()
        parent = self.GetParent()
        parent.calculateExpected()


    def create_mins_sizer(self, parent):
        mins = wx.StaticBox(self, -1, "Minimum Coins")
        mins_box = wx.StaticBoxSizer( mins, wx.HORIZONTAL )
        mins_spin = self.create_mins_spin(parent, "Minimum number of coins per day.\nBelow this many, the miner stops.")
        mins_box.Add(mins_spin, 1, wx.ALL, 5)

        return mins_box

    def create_mins_spin(self, parent, text):
        self.min_v = wx.SpinCtrl(self, -1, '0', min=0, max=9999999, size=(70, -1))
        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.min_v)
        self.Bind(wx.EVT_TEXT,     parent.on_control_changed, self.min_v)
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, -1, text)
        text.SetFont(font)
        sizer.Add(self.min_v, wx.ID_ANY, wx.ALL, 2)
        sizer.AddSpacer(10)
        sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL)

        return sizer


class DataPanel(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__( self, parent, -1)

        box1_title = wx.StaticBox( self, -1, "Expected values" )
        sizer = wx.StaticBoxSizer( box1_title, wx.VERTICAL )

        sizer.AddF(HeaderPanel(self), wx.SizerFlags().Expand().Border(wx.UP, 5))

        self.algo_panel_scrypt = AlgoPanel(self,  "Scrypt  ")
        self.algo_panel_groestl = AlgoPanel(self, "Groestl ")
        self.algo_panel_skein = AlgoPanel(self,   "Skein   ")
        self.algo_panel_qubit = AlgoPanel(self,   "Qubit   ")
        sizer.Add((-1, 3), 0, wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.algo_panel_scrypt, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.algo_panel_groestl, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.algo_panel_skein, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.algo_panel_qubit, 0, wx.EXPAND | wx.ALL, 3)

        self.avg_panel = AvgPanel(self)
        sizer.Add(self.avg_panel, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(sizer)


class AlgoPanel(wx.Panel):
    def __init__(self, parent, algo):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.algo = algo
        #self.status_bar = status_bar
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        algo_text = wx.StaticText(self, -1, algo, size=(50, 18))
        algo_text.SetFont(font)
        self.weight = wx.TextCtrl(self, -1, "", size=(30, 18), style=wx.TE_CENTER)
        self.mins = wx.TextCtrl(self, -1, "", size=(30, 18), style=wx.TE_CENTER)
        self.per_w = wx.TextCtrl(self, -1, "", size=(30, 18), style=wx.TE_CENTER)
        self.weight.Enable(False)
        self.mins.Enable(False)
        self.per_w.Enable(False)

        #self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.hash_rate)
        #self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.watts)
        #self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.hash_rate)
        #self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.watts)
        #self.Bind(wx.EVT_CHECKBOX, self.enable_disable_controls, self.active_algo)

        sizer.Add(algo_text, 0, wx.TOP | wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer.Add(self.weight, 1, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 6)
        sizer.Add(self.mins, 1, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 6)
        sizer.Add(self.per_w, 1, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 6)
        self.SetSizer(sizer)

    def set_values(self, weight, mins, per_w):
        self.set_weight(weight)
        self.set_mins(mins)
        self.set_per_w(per_w)

    def set_weight(self, weight):
        try:
            self.weight.SetValue(weight)

        except:
            print "Error: set_weight + " + str(weight)

    def set_mins(self, mins):
        try:
            self.mins.SetValue(mins)

        except:
            print "Error: set_mins + " + str(mins)

    def set_per_w(self, per_w):
        try:
            self.per_w.SetValue(per_w)

        except:
            print "Error: set_per_w + " + str(per_w)


class HeaderPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        text_algo = wx.StaticText(self, wx.ID_ANY, "Algo    ", size=(50, -1), style=wx.BOLD)
        text_weight = wx.StaticText(self, wx.ID_ANY, "Weight", size=(30, -1), style=wx.BOLD)
        text_mins = wx.StaticText(self, wx.ID_ANY, "Min. Coins", size=(30, -1), style=wx.BOLD)
        text_perW = wx.StaticText(self, wx.ID_ANY, "Min. C/W", size=(30, -1), style=wx.BOLD)

        text_algo.SetFont(font)
        text_weight.SetFont(font)
        text_mins.SetFont(font)
        text_perW.SetFont(font)

        sizer.Add(text_algo, 0, wx.EXPAND | wx.LEFT, 8)
        sizer.Add(text_weight, 1, wx.EXPAND | wx.LEFT, 12)
        sizer.Add(text_mins, 1, wx.EXPAND | wx.LEFT, 8)
        sizer.Add(text_perW, 1, wx.EXPAND | wx.LEFT, 6)

        self.SetSizer(sizer)

class AvgPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        text_avg = wx.StaticText(self, wx.ID_ANY, "Averages", size=(40, -1), style=wx.BOLD)
        #self.weight = wx.TextCtrl(self, -1, "", size=(30, 18), style=wx.TE_CENTER)
        self.mins = wx.TextCtrl(self, -1, "", size=(30, 18), style=wx.TE_CENTER)
        self.per_w = wx.TextCtrl(self, -1, "", size=(30, 18), style=wx.TE_CENTER)
        self.mins.Enable(False)
        self.per_w.Enable(False)

        text_avg.SetFont(font)

        sizer.Add(text_avg, 1, wx.TOP | wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer.Add((54, -1), 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 2)
        sizer.Add(self.mins, 1, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 6)
        #sizer.Add((-1, -1), 1, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer.Add(self.per_w, 1, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 6)

        self.SetSizer(sizer)

    def set_values(self, avg_mins, avg_per_w):
        self.set_avg_mins(avg_mins)
        self.set_avg_per_w(avg_per_w)

    def set_avg_mins(self, avg_mins):
        try:
            self.mins.SetValue(avg_mins)

        except:
            print "Error: set_avg_mins + " + str(avg_mins)

    def set_avg_per_w(self, avg_per_w):
        try:
            self.per_w.SetValue(avg_per_w)

        except:
            print "Error: set_avg_per_w + " + str(avg_per_w)