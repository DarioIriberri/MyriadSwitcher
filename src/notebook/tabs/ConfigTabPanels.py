from notebook.tabs import NotebookTab as nbt

__author__ = 'Dario'

import wx
import time
import threading
import  FrameMYR
from console.switcher import HTMLBuilder as clr
from event.EventLib import StatusBarEvent


class BaseConfigTab(nbt.NotebookTab):
    SCRYPT  = "Scrypt "
    GROESTL = "Groestl "
    SKEIN   = "Skein "
    QUBIT   = "Qubit "

    def __init__(self, parent, parentNotebook):
        nbt.NotebookTab.__init__(self, parent, id=wx.ID_ANY)

        self.parentNotebook = parentNotebook

        self.configTab = parent
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

        #self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

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

        sizer.AddF(wx.StaticText(self, wx.ID_ANY, size=(50, -1)), wx.SizerFlags().Border(wx.LEFT, 6))
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

    def algoButtonColorsMining(self, algo):
        self.algo_panel_scrypt.activeAlgoColorsRunningBlink(algo)
        self.algo_panel_groestl.activeAlgoColorsRunningBlink(algo)
        self.algo_panel_skein.activeAlgoColorsRunningBlink(algo)
        self.algo_panel_qubit.activeAlgoColorsRunningBlink(algo)

    def algoButtonColorsStopped(self):
        self.algo_panel_scrypt.algoButtonColors(stopped=True)
        self.algo_panel_groestl.algoButtonColors(stopped=True)
        self.algo_panel_skein.algoButtonColors(stopped=True)
        self.algo_panel_qubit.algoButtonColors(stopped=True)


class AlgoPanelData(wx.Panel):
    def __init__(self, parent, algo):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.algo = algo
        self.parent = parent
        self.blinking = False

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizerW = wx.BoxSizer(wx.HORIZONTAL)

        #self.active_algo = wx.CheckBox(self, -1, label=algo, size=(80, -1))
        #self.active_algo = wx.ToggleButton(self, wx.ID_ANY, algo, size=(57, 25))
        self.active_algo = wx.ToggleButton(self, wx.ID_ANY, algo, size=(75, 25))
        self.active_algo.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_over_active_algo)
        self.active_algo.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave_active_algo)
        self.active_algo.Bind(wx.EVT_SET_CURSOR, self.algoButtonColors)
        self.active_algo.Bind(wx.EVT_PAINT, self.algoButtonColors)
        self.active_algo.Bind(wx.EVT_ERASE_BACKGROUND, self.algoButtonColors)
        self.active_algo.Bind(wx.EVT_TOGGLEBUTTON, self.on_control_changed)
        self.active_algo.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        #self.active_algo.Bind(wx.EVT_SET_FOCUS, self.onFocus)
        #wx.EVT_CHECKBOX(self.active_algo, self.on_control_changed)

        self.hash_rate = wx.SpinCtrlDouble(self, value='0.00', size=(70, -1), min=0.0, max=9999.99, inc=0.01)
        self.hash_rate.SetDigits(2)
        self.watts = wx.SpinCtrl(self, -1, '0', min=0, max=999999, size=(70, -1))

        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.hash_rate)
        self.Bind(wx.EVT_SPINCTRL, parent.on_control_changed, self.watts)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.hash_rate)
        self.Bind(wx.EVT_TEXT, parent.on_control_changed, self.watts)
        #self.Bind(wx.EVT_CHECKBOX, self.on_control_changed, self.active_algo)

        sizerW.Add(self.active_algo, 0, wx.LEFT | wx.RIGHT | wx.TOP, 3)
        self.sizer.Add(sizerW, 0, wx.LEFT | wx.RIGHT, 6)
        self.sizer.Add(self.hash_rate, 0, wx.ALL, 4)
        self.sizer.Add(self.watts, 0, wx.ALL, 4)
        self.SetSizer(self.sizer)

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

    def algoButtonColors(self, event=None, stopped=False):
        miningAlgo = self.parent.baseConfigTab.parentNotebook.getParentWindow().getMiningAlgo()
        miningThisAlgo = not stopped and miningAlgo and self.algo.strip() == miningAlgo.strip()

        if stopped and self.blinking:
            self.blinking = False
            #time.sleep(1)

        if self.blinking and not stopped:
            return

        if self.active_algo.GetValue():
            if  miningThisAlgo:
                #print self.algo + " running"
                self.activeAlgoColorsRunning()

                if event:
                    event.Skip()

                return

            #print self.algo + "Pressed"
            self.activeAlgoColorsPressed()

        else:
            if miningThisAlgo:
                #print self.algo + "Running disabled"
                self.activeAlgoColorsRunningDisabled()
                if event:
                    event.Skip()

                return

            #print self.algo + "disabled"
            self.activeAlgoColorsOff()

    def on_control_changed(self, event, trigger_to_frame=True):
        #self.fbb.Enable(self.active_algo.GetValue())
        self.hash_rate.Enable(self.active_algo.GetValue())
        self.watts.Enable(self.active_algo.GetValue())

        if trigger_to_frame:
            self.parent.on_control_changed(event)

    def on_mouse_over_active_algo(self, event):
        #self.onHover(event)
        wx.PostEvent(self.parent.baseConfigTab.parentNotebook.getParentWindow(),
                     StatusBarEvent(message="Enable / Disable " + self.algo + " - " + str(self.active_algo.GetValue())))

    def on_mouse_leave_active_algo(self, event):
        #self.onHover(event)
        self.active_algo.SetBackgroundColour(None)
        wx.PostEvent(self.parent.baseConfigTab.parentNotebook.getParentWindow(), StatusBarEvent(message=""))

    def activeAlgoDefaultColors(self):
        self.active_algo.SetBackgroundColour(None)
        self.active_algo.SetForegroundColour(None)

    def activeAlgoColorsRunning(self):
        self.active_algo.SetBackgroundColour(clr.COLOR_DARK_GREEN)
        self.active_algo.SetForegroundColour(clr.COLOR_WHITE)
        #self.active_algo.SetForegroundColour(clr.COLOR_BLACK)

    def activeAlgoColorsRunningDisabled(self):
        self.active_algo.SetBackgroundColour(clr.COLOR_DARK_GREEN_DISABLED)
        self.active_algo.SetForegroundColour(clr.COLOR_WHITE)
        #self.active_algo.SetForegroundColour(clr.COLOR_BLACK)

    def activeAlgoColorsOff(self):
        self.active_algo.SetBackgroundColour(clr.COLOR_LIGHTER_GRAY)
        self.active_algo.SetForegroundColour(clr.COLOR_DARK_GRAY)

    def activeAlgoColorsPressed(self):
        self.active_algo.SetBackgroundColour(clr.COLOR_BLUE_PRESSED)
        self.active_algo.SetForegroundColour(clr.COLOR_BLACK)

    def activeAlgoColorsRunningBlink(self, algo):
        if self.active_algo.GetValue() and algo.strip() == self.algo.strip():
            thread = threading.Thread(target=self.activeAlgoRunningColorsBlinkThread, args=[algo])
            thread.start()

        else:
            self.activeAlgoDefaultColors()

    def activeAlgoRunningColorsBlinkThread(self, algo):
        i = 0

        self.blinking = True

        while i < 8 and self.blinking:
            if i % 2:
                self.activeAlgoColorsRunning()
            else:
                self.activeAlgoDefaultColors()
                #self.activeAlgoRunningdColorsOff()

            i += 1

            time.sleep(0.5)

        self.activeAlgoColorsRunning()
        self.blinking = False

        #def __deviceReadyColors(self):
        #    self.active_algo.SetBackgroundColour(clr.COLOR_ORANGE)
        #    self.active_algo.SetForegroundColour(clr.COLOR_WHITE)


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


class AlgoToggleButton(wx.ToggleButton):
    def __init__(self, parent, id, algo, size):
        wx.ToggleButton.__init__(self, parent, id, algo, size)

#        EVT_SIZE = wx.PyEventBinder( wxEVT_SIZE )
# = wx.PyEventBinder( wxEVT_SIZING )
#EVT_MOVE = wx.PyEventBinder( wxEVT_MOVE )
#EVT_MOVING = wx.PyEventBinder( wxEVT_MOVING )
#EVT_MOVE_START = wx.PyEventBinder( wxEVT_MOVE_START )
#EVT_MOVE_END = wx.PyEventBinder( wxEVT_MOVE_END )
#EVT_CLOSE = wx.PyEventBinder( wxEVT_CLOSE_WINDOW )
#EVT_END_SESSION = wx.PyEventBinder( wxEVT_END_SESSION )
#EVT_QUERY_END_SESSION = wx.PyEventBinder( wxEVT_QUERY_END_SESSION )
#EVT_PAINT = wx.PyEventBinder( wxEVT_PAINT )
#EVT_NC_PAINT = wx.PyEventBinder( wxEVT_NC_PAINT )
#EVT_ERASE_BACKGROUND = wx.PyEventBinder( wxEVT_ERASE_BACKGROUND )
#EVT_CHAR = wx.PyEventBinder( wxEVT_CHAR )
#EVT_KEY_DOWN = wx.PyEventBinder( wxEVT_KEY_DOWN )
#EVT_KEY_UP = wx.PyEventBinder( wxEVT_KEY_UP )
#EVT_HOTKEY = wx.PyEventBinder( wxEVT_HOTKEY, 1)
#EVT_CHAR_HOOK = wx.PyEventBinder( wxEVT_CHAR_HOOK )
#EVT_MENU_OPEN = wx.PyEventBinder( wxEVT_MENU_OPEN )
#EVT_MENU_CLOSE = wx.PyEventBinder( wxEVT_MENU_CLOSE )
#EVT_MENU_HIGHLIGHT = wx.PyEventBinder( wxEVT_MENU_HIGHLIGHT, 1)
#EVT_MENU_HIGHLIGHT_ALL = wx.PyEventBinder( wxEVT_MENU_HIGHLIGHT )
#EVT_SET_FOCUS = wx.PyEventBinder( wxEVT_SET_FOCUS )
#EVT_KILL_FOCUS = wx.PyEventBinder( wxEVT_KILL_FOCUS )
#EVT_CHILD_FOCUS = wx.PyEventBinder( wxEVT_CHILD_FOCUS )
#EVT_ACTIVATE = wx.PyEventBinder( wxEVT_ACTIVATE )
#EVT_ACTIVATE_APP = wx.PyEventBinder( wxEVT_ACTIVATE_APP )
#EVT_HIBERNATE = wx.PyEventBinder( wxEVT_HIBERNATE )
#EVT_END_SESSION = wx.PyEventBinder( wxEVT_END_SESSION )
#EVT_QUERY_END_SESSION = wx.PyEventBinder( wxEVT_QUERY_END_SESSION )
#EVT_DROP_FILES = wx.PyEventBinder( wxEVT_DROP_FILES )
#EVT_INIT_DIALOG = wx.PyEventBinder( wxEVT_INIT_DIALOG )
#EVT_SYS_COLOUR_CHANGED = wx.PyEventBinder( wxEVT_SYS_COLOUR_CHANGED )
#EVT_DISPLAY_CHANGED = wx.PyEventBinder( wxEVT_DISPLAY_CHANGED )
#EVT_SHOW = wx.PyEventBinder( wxEVT_SHOW )
#EVT_MAXIMIZE = wx.PyEventBinder( wxEVT_MAXIMIZE )
#EVT_ICONIZE = wx.PyEventBinder( wxEVT_ICONIZE )
#EVT_NAVIGATION_KEY = wx.PyEventBinder( wxEVT_NAVIGATION_KEY )
#EVT_PALETTE_CHANGED = wx.PyEventBinder( wxEVT_PALETTE_CHANGED )
#EVT_QUERY_NEW_PALETTE = wx.PyEventBinder( wxEVT_QUERY_NEW_PALETTE )
#EVT_WINDOW_CREATE = wx.PyEventBinder( wxEVT_CREATE )
#EVT_WINDOW_DESTROY = wx.PyEventBinder( wxEVT_DESTROY )
#EVT_SET_CURSOR = wx.PyEventBinder( wxEVT_SET_CURSOR )
#EVT_MOUSE_CAPTURE_CHANGED = wx.PyEventBinder( wxEVT_MOUSE_CAPTURE_CHANGED )
#EVT_MOUSE_CAPTURE_LOST = wx.PyEventBinder( wxEVT_MOUSE_CAPTURE_LOST )

        self.Bind(wx.EVT_SET_FOCUS, self.onFocus)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.onFocus)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onFocus)
        self.Bind(wx.EVT_SIZE, self.onFocus)
        self.Bind(wx.EVT_SIZING, self.onFocus)
        self.Bind(wx.EVT_PAINT, self.onFocus)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.onFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.onFocus)
        self.Bind(wx.EVT_CHILD_FOCUS, self.onFocus)
        self.Bind(wx.EVT_ACTIVATE, self.onFocus)
        self.Bind(wx.EVT_ACTIVATE_APP, self.onFocus)
        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.onFocus)
        self.Bind(wx.EVT_DISPLAY_CHANGED, self.onFocus)
        self.Bind(wx.EVT_PALETTE_CHANGED, self.onFocus)
        self.Bind(wx.EVT_SET_CURSOR, self.onFocus)
        self.Bind(wx.EVT_MOUSE_CAPTURE_CHANGED, self.onFocus)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.onFocus)
        self.Bind(wx.EVT_LEFT_DCLICK, self.onFocus)
        self.Bind(wx.EVT_MOUSE_AUX1_DOWN, self.onFocus)
        self.Bind(wx.EVT_MOUSE_AUX1_UP, self.onFocus)
        self.Bind(wx.EVT_MOUSE_AUX1_DCLICK, self.onFocus)
        self.Bind(wx.EVT_MOUSE_AUX2_DOWN, self.onFocus)
        self.Bind(wx.EVT_MOUSE_AUX2_UP, self.onFocus)
        self.Bind(wx.EVT_MOUSE_AUX2_DCLICK, self.onFocus)
#
#EVT_LEFT_DOWN = wx.PyEventBinder( wxEVT_LEFT_DOWN )
#EVT_LEFT_UP = wx.PyEventBinder( wxEVT_LEFT_UP )
#EVT_MIDDLE_DOWN = wx.PyEventBinder( wxEVT_MIDDLE_DOWN )
#EVT_MIDDLE_UP = wx.PyEventBinder( wxEVT_MIDDLE_UP )
#EVT_RIGHT_DOWN = wx.PyEventBinder( wxEVT_RIGHT_DOWN )
#EVT_RIGHT_UP = wx.PyEventBinder( wxEVT_RIGHT_UP )
#EVT_MOTION = wx.PyEventBinder( wxEVT_MOTION )
#EVT_LEFT_DCLICK = wx.PyEventBinder( wxEVT_LEFT_DCLICK )
#EVT_MIDDLE_DCLICK = wx.PyEventBinder( wxEVT_MIDDLE_DCLICK )
#EVT_RIGHT_DCLICK = wx.PyEventBinder( wxEVT_RIGHT_DCLICK )
#EVT_LEAVE_WINDOW = wx.PyEventBinder( wxEVT_LEAVE_WINDOW )
#EVT_ENTER_WINDOW = wx.PyEventBinder( wxEVT_ENTER_WINDOW )
#EVT_MOUSEWHEEL = wx.PyEventBinder( wxEVT_MOUSEWHEEL )
#EVT_MOUSE_AUX1_DOWN = wx.PyEventBinder( wxEVT_AUX1_DOWN )
#EVT_MOUSE_AUX1_UP = wx.PyEventBinder( wxEVT_AUX1_UP )
#EVT_MOUSE_AUX1_DCLICK = wx.PyEventBinder( wxEVT_AUX1_DCLICK )
#EVT_MOUSE_AUX2_DOWN = wx.PyEventBinder( wxEVT_AUX2_DOWN )
#EVT_MOUSE_AUX2_UP = wx.PyEventBinder( wxEVT_AUX2_UP )
#EVT_MOUSE_AUX2_DCLICK = wx.PyEventBinder( wxEVT_AUX2_DCLICK )

    def onFocus(self, event):
        print "derp = " + str(event)
        if not self.GetValue():
            event.Skip()

    def onHover(self, event):
        print "derp = " + str(event)
        #event.Skip(False)
        #if not self.GetValue():
        #    event.Skip()