import FrameMYR
from notebook.tabs import NotebookTab as nbt

__author__ = 'Dario'

import wx
import os

try:
    from agw import multidirdialog as MDD
except ImportError:
    import wx.lib.agw.multidirdialog as MDD

class MiscellaneousTab(nbt.NotebookTab):
    #----------------------------------------------------------------------
    def __init__(self, parentNotebook):
        nbt.NotebookTab.__init__(self, parentNotebook=parentNotebook, id=wx.ID_ANY)

        #self.Bind(EVT_CONFIG_MODE_EVENT, self.onMainModeToggle)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.timings_panel = TimingsPanel(self)
        self.log_panel = LogsExchangePanel(self)

        sizer.Add(self.timings_panel, 0, wx.EXPAND | wx.ALL, 3)
        sizer.Add(self.log_panel, 1, wx.EXPAND | wx.ALL, 3)

        #self.SetBackgroundColour("White")

        self.SetSizer(sizer)
        self.Show()

    def get_json(self):
        json = {}
        #json["logActive"] = 0
        #json["logPath"] = "\"C:\\Dropbox\\Public\\Myriad_log\""
        #json["sleepSHORT"] = 3
        #json["sleepLONG"] = 5
        #json["hysteresis"] = 1.05
        #json["minTimeNoHysteresis"] = 99999
        #json["rampUptime"] = 10
        #json["exchange"] = "\"poloniex\""
        #json["monitor"] = True
        #json["reboot"] = False
        #json["maxErrors"] = 1
        #json["rebootIf"] = "freezes or crashes"
        json["sleepSHORTDebug"] = 30
        json["sleepLONGDebug"] = 50
        json["debug"] = 0
        #json["timeout"] = 30000

        json.update(self.timings_panel.get_values())
        json.update(self.log_panel.get_values())

        return json

    def set_json(self, config_json):
        self.timings_panel.set_values(config_json, "sleepSHORT", "sleepLONG", "hysteresis", "minTimeNoHysteresis", "rampUptime", "timeout")
        self.log_panel.set_values(config_json, "logActive", "logPath", "exchange", "monitor", "reboot", "maxErrors", "rebootIf" )

    def on_control_changed(self, event):
        self.parentNotebook.notebookControlChanged(event)

    def check_files_exist(self):
        return self.log_panel.checkFileExists()

    def onMainModeToggle(self, event):
        self.log_panel.errors_box.loadErrorCombo(event.advanced)

class TimingsPanel(wx.Panel):
    def __init__( self, parent ):
        self.parent = parent

        wx.Panel.__init__( self, parent, -1)

        vs = wx.BoxSizer( wx.VERTICAL )

        box1_title = wx.StaticBox( self, -1, "Timings" )
        box1 = wx.StaticBoxSizer( box1_title, wx.VERTICAL )

        self.sleepSHORT = TimingElement(self, "Normal Sleep time (minutes)", min=1, max=9999)
        self.sleepLONG = TimingElement(self, "Sleep time after miner starts (minutes)", 1, 9999)
        #self.hysteresis = self.create_timing_element("Switching Hysteresis (%)", 0, 50)
        self.hysteresis = ComboElement(self, "Switching Hysteresis (%)")
        self.minTimeNoHysteresis = TimingElement(self, "Maximum hysteresis time (minutes)", 0, 9999)
        self.rampUptime = TimingElement(self, "Miner ramp up time (seconds)", 0, 9999)
        self.timeout = TimingElement(self, "HTTP timeout (seconds)", 1, 9999)

        box1.Add( self.sleepSHORT, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.sleepLONG, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.hysteresis, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.minTimeNoHysteresis, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.rampUptime, 0, wx.ALIGN_LEFT | wx.ALL, 5 )
        box1.Add( self.timeout, 0, wx.ALIGN_LEFT | wx.ALL, 5 )

        vs.Add( box1, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL | wx.EXPAND, 2 )

        self.SetSizer(vs)

        #self.SetBackgroundColour("White")

    def set_values(self, config_json, sleepSHORT, sleepLONG, hysteresis, minTimeNoHysteresis, rampUptime, timeout):
        p = self.GetParent()
        self.set_sleepSHORT(p.get_value(config_json, sleepSHORT))
        self.set_sleepLONG(p.get_value(config_json, sleepLONG))
        self.set_hysteresis(p.get_value(config_json, hysteresis))
        self.set_minTimeNoHysteresis(p.get_value(config_json, minTimeNoHysteresis))
        self.set_rampUptime(p.get_value(config_json, rampUptime))
        self.set_timeout(p.get_value(config_json, timeout))


    def set_sleepSHORT(self, sleepSHORT):
        try:
            self.sleepSHORT.timing_elem.SetValue(sleepSHORT)
        except:
            print "Error: set_sleepSHORT"

    def set_sleepLONG(self, sleepLONG):
        try:
            self.sleepLONG.timing_elem.SetValue(sleepLONG)
        except:
            print "Error: set_sleepLONG"

    def set_hysteresis(self, hysteresis):
        try:
            self.hysteresis.combo_hys.Select(int(hysteresis))
        except:
            print "Error: set_hysteresis"

    def set_minTimeNoHysteresis(self, minTimeNoHysteresis):
        try:
            self.minTimeNoHysteresis.timing_elem.SetValue(minTimeNoHysteresis)
        except:
            print "Error: set_minTimeNoHysteresis"

    def set_rampUptime(self, rampUptime):
        try:
            self.rampUptime.timing_elem.SetValue(rampUptime)
        except:
            print "Error: set_rampUptime"

    def set_timeout(self, timeout):
        try:
            self.timeout.timing_elem.SetValue(timeout)
        except:
            print "Error: set_timeout"


    def get_values(self):
        values = dict()

        try:
            values["sleepSHORT"] = self.sleepSHORT.timing_elem.GetValue()
        except:
            print "Error: get_values - sleepSHORT"
            pass
        try:
            values["sleepLONG"] = self.sleepLONG.timing_elem.GetValue()
        except:
            print "Error: get_values - sleepLONG"
            pass
        try:
            try:
                values["hysteresis"] = int(self.hysteresis.combo_hys.GetValue()[:-1])
            except ValueError:
                values["hysteresis"] = self.parent.get_default_value("hysteresis")
        except:
            print "Error: get_values - hysteresis"
            pass
        try:
            values["minTimeNoHysteresis"] = self.minTimeNoHysteresis.timing_elem.GetValue()
        except:
            print "Error: get_values - minTimeNoHysteresis"
            pass
        try:
            values["rampUptime"] = self.rampUptime.timing_elem.GetValue()
        except:
            print "Error: get_values - rampUptime"
            pass
        try:
            values["timeout"] = self.timeout.timing_elem.GetValue()
        except:
            print "Error: get_values - timeout"
            pass

        return values


class LogsExchangePanel(wx.Panel):
    POLONIEX = "poloniex"
    CRYPTSY  = "cryptsy"

    CRASHES  = "crashes"
    FREEZES  = "freezes"
    CRASHES_OR_FREEZES  = "crashes or freezes"

    def __init__(self, parent):
        wx.Panel.__init__( self, parent, -1)

        self.parent = parent

        #self.logs_box = self.create_logs_sizer()
        self.logs_box = LogElement(self, wx.StaticBox(self, -1, "Log configuration"))
        self.exchange_box = ExchangeElement(self, wx.StaticBox(self, -1, "Exchange source"))
        self.errors_box = ErrorsElement(self, wx.StaticBox(self, -1, "Miner error handling"))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add( self.logs_box, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        sizer.Add( self.errors_box, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL | wx.EXPAND, 2 )
        sizer.Add( self.exchange_box, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 2 )

        self.SetSizer(sizer)

        #self.SetBackgroundColour("White")

    def enable_disable_controls(self, event, trigger_to_frame=True):
        self.logs_box.txtDir.Enable(self.logs_box.active_log.GetValue())
        self.logs_box.buttonDir.Enable(self.logs_box.active_log.GetValue())
        self.errors_box.enable_disable_controls(event, trigger_to_frame)

        if trigger_to_frame:
            self.parent.parentNotebook.notebookControlChanged()

    def get_values(self):
        exchange_selection = self.exchange_box.combo_exchange.GetSelection()
        rebootIf = self.errors_box.rebootIf.GetSelection()

        values = dict()
        try:
            values["logActive"] = int(self.logs_box.active_log.GetValue())
        except:
            print "Error: get_values - logActive"

        try:
            values["logPath"] = self.logs_box.txtDir.GetValue()
        except:
            print "Error: get_values - logPath"

        try:
            values["exchange"] = self.CRYPTSY if exchange_selection == 1 else self.POLONIEX
        except:
            print "Error: get_values - exchange"

        try:
            values["monitor"] = self.errors_box.monitor.GetValue()
        except:
            print "Error: get_values - monitor"

        try:
            values["reboot"] = self.errors_box.reboot.GetValue()
        except:
            print "Error: get_values - reboot"

        try:
            values["maxErrors"] = self.errors_box.maxErrors.GetValue()
        except:
            print "Error: get_values - maxErrors"

        try:
            values["rebootIf"] = self.CRASHES if rebootIf == 0 else self.FREEZES if rebootIf == 1 else self.CRASHES_OR_FREEZES
        except:
            print "Error: get_values - rebootIf"

        return values

    def set_values(self, config_json, logActive, logPath, exchange, monitor, reboot, maxErrors, rebootIf):
        p = self.GetParent()
        self.set_logActive(p.get_value(config_json, logActive))
        self.set_logPath(p.get_value(config_json, logPath))
        self.set_exchange(p.get_value(config_json, exchange))

        self.set_monitor(p.get_value(config_json, monitor))
        self.set_reboot(p.get_value(config_json, reboot))
        self.set_maxErrors(p.get_value(config_json, maxErrors))
        self.set_rebootIf(p.get_value(config_json, rebootIf))

        self.enable_disable_controls(self, False)

    def set_logActive(self, logActive):
        try:
           self.logs_box.active_log.SetValue(logActive)

        except:
            print "Error: set_logActive"

    def set_logPath(self, logPath):
        try:
            #if logPath:
            #
            #    if not os.path.isdir(logPath):
            #        dlg = wx.MessageDialog(self, 'The directory ' + logPath + " does not exist",
            #                               'Configuration Warning',
            #                               wx.OK | wx.ICON_WARNING
            #        )
            #
            #        dlg.ShowModal()
            #        dlg.Destroy()
            #
            #    else:
            #        if logPath != self.logs_box.fbb.GetValue():
            #            self.logs_box.fbb.SetValue(logPath)

            if logPath != self.logs_box.txtDir.GetValue():
                self.logs_box.txtDir.SetValue(logPath)

        except:
            print "Error: set_logPath"

    def set_exchange(self, exchange):
        try:
           self.exchange_box.combo_exchange.Select( 1 if exchange == self.CRYPTSY else 0 )

        except:
            print "Error: set_exchange "


    def set_monitor(self, monitor):
        try:
            self.errors_box.monitor.SetValue(monitor)

        except:
            print "Error: set_monitor"


    def set_reboot(self, reboot):
        try:
           self.errors_box.reboot.SetValue(reboot)

        except:
            print "Error: set_reboot"


    def set_maxErrors(self, maxErrors):
        try:
           self.errors_box.maxErrors.SetValue(maxErrors)

        except:
            print "Error: set_maxErrors"


    def set_rebootIf(self, rebootIf):
        try:
           self.errors_box.rebootIf.Select( 0 if rebootIf == self.CRASHES else 1 if rebootIf == self.FREEZES else 2 )

        except:
            print "Error: set_rebootIf"

    def checkFileExists(self):
        active_log = self.logs_box.active_log.GetValue()
        logPath = self.logs_box.txtDir.GetValue()

        if active_log and not os.path.isdir(logPath):
            dlg = wx.MessageDialog(self, 'The logging directory ' + logPath + " does not exist",
                                       'Configuration Error',
                                       wx.OK | wx.ICON_ERROR
            )

            dlg.ShowModal()
            dlg.Destroy()

            return False

        else:
            self.parent.parentNotebook.notebookControlChanged()

            return True


    def OnChanged(self, event):
        self.parent.parentNotebook.notebookControlChanged()


class TimingElement(wx.BoxSizer):
    def __init__(self, parent, text, min, max):
        wx.BoxSizer.__init__(self)
        self.SetOrientation(wx.HORIZONTAL)
        txt = wx.StaticText(parent, wx.ID_ANY, text, size=(-1, -1), style=wx.BOLD)
        #font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #txt.SetFont(font)
        self.timing_elem = wx.SpinCtrl(parent, -1, '0', min=min, max=max, size=(54, -1))
        parent.Bind(wx.EVT_SPINCTRL, parent.GetParent().on_control_changed, self.timing_elem)
        self.Add(self.timing_elem, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 3)
        self.Add(txt, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)


class ComboElement(wx.BoxSizer):
    def __init__(self, parent, text):
        wx.BoxSizer.__init__(self)

        txt = wx.StaticText(parent, wx.ID_ANY, text, size=(-1, -1), style=wx.BOLD)
        #font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #txt.SetFont(font)

        hys = []
        for i in range(0, 100):
            hys.append(str(i) + "%")

        self.combo_hys = wx.ComboBox(parent, -1, size=(54, -1), choices=hys, style=wx.CB_READONLY | wx.ALIGN_RIGHT)
        parent.Bind(wx.EVT_COMBOBOX, parent.GetParent().on_control_changed, self.combo_hys)
        self.SetOrientation(wx.HORIZONTAL)
        self.Add(self.combo_hys, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 3)
        self.Add(txt, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 10)


class ExchangeElement(wx.StaticBoxSizer):
    def __init__(self, parent, static_box):
        wx.StaticBoxSizer.__init__(self, static_box, wx.HORIZONTAL)

        self.combo_exchange = wx.ComboBox(parent, -1, size=(154, -1), choices=["poloniex", "cryptsy"], style=wx.CB_READONLY)
        parent.Bind(wx.EVT_COMBOBOX, parent.GetParent().on_control_changed, self.combo_exchange)
        self.Add(self.combo_exchange, 0, wx.BOTTOM | wx.LEFT, 5)

class LogElement(wx.StaticBoxSizer):
    def __init__(self, parent, static_box):
        wx.StaticBoxSizer.__init__(self, static_box, wx.HORIZONTAL)
        self.parent = parent

        self.SetOrientation( wx.VERTICAL)
        self.active_log = wx.CheckBox(parent, -1, label="Log to file... choose log path", size=(-1, -1))
        parent.Bind(wx.EVT_CHECKBOX, parent.enable_disable_controls, self.active_log)
        #font = wx.Font(-1, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        #self.active_log.SetFont(font)
        self.active_log.SetValue(True)
        self.Add((-1, 2), 0)
        self.Add(self.active_log, 0, wx.BOTTOM | wx.LEFT, 6)

        #self.fbb = DirBrowserMYR(
        #    parent, -1, labelText="", changeCallback = parent.OnChanged
        #    #parent, id=wx.ID_ANY, labelText=""
        #)

        boxWrapper = wx.BoxSizer(wx.HORIZONTAL)

        sizerLog = wx.BoxSizer(wx.HORIZONTAL)
        self.txtDir = wx.TextCtrl(parent, -1, size=(-1, 23))
        self.buttonDir = wx.Button(parent, -1, size=(32, 25))
        self.buttonDir.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH     + 'img/browse16.ico'))
        boxWrapper.Add( self.buttonDir, 0, wx.TOP, -1)
        parent.Bind(wx.EVT_BUTTON, self.onShowDialog, self.buttonDir)
        parent.Bind(wx.EVT_TEXT, parent.GetParent().on_control_changed, self.txtDir)

        sizerLog.Add(self.txtDir, 1, wx.LEFT, 5)
        sizerLog.Add(boxWrapper, 0, wx.LEFT | wx.RIGHT, 5)

        self.Add(sizerLog, 0, wx.TOP | wx.EXPAND, 9)

    def onShowDialog(self, event):
        currentLogDir = self.txtDir.GetValue()
        directory = os.getcwd() if not currentLogDir or not os.path.isdir(currentLogDir) else currentLogDir
        #self.fbb = MDD.MultiDirDialog(self.parent, title="Pick a directory for your logs...", defaultPath="", agwStyle=wx.DD_NEW_DIR_BUTTON)
        self.fbb = wx.DirDialog(self.parent, "Pick a directory for your logs...", defaultPath=directory, style=wx.DD_DEFAULT_STYLE)
        #self.fbb = wx.DirDialog(self.parent, "Pick a directory for your logs...", style=wx.DD_NEW_DIR_BUTTON)

        if self.fbb.ShowModal() != wx.ID_OK:
            self.fbb.Destroy()
            return

        self.txtDir.SetValue(self.fbb.GetPath())
        self.fbb.Destroy()

        self.parent.parent.parentNotebook.notebookControlChanged()

class ErrorsElement(wx.StaticBoxSizer):
    ERROR_OPTS = ["crashes", "freezes", "crashes or freezes"]

    def __init__(self, parent, static_box):
        wx.StaticBoxSizer.__init__(self, static_box, wx.HORIZONTAL)

        self.parent = parent

        self.SetOrientation( wx.VERTICAL)

        self.monitor = wx.CheckBox(parent, -1, label="Miner error monitoring", size=(-1, -1))
        parent.Bind(wx.EVT_CHECKBOX, self.enable_disable_controls, self.monitor)

        sizerReboot = wx.BoxSizer(wx.HORIZONTAL)
        self.reboot = wx.CheckBox(parent, -1, label="Reboot after", size=(-1, -1))
        parent.Bind(wx.EVT_CHECKBOX, self.enable_disable_sub_controls, self.reboot)

        self.maxErrors = wx.SpinCtrl(parent, -1, min=1, max=100, size=(48, -1))

        self.rebootIf = wx.ComboBox(parent, -1, size=(54, -1), choices=self.ERROR_OPTS, style=wx.CB_READONLY | wx.ALIGN_RIGHT)

        #self.loadErrorCombo(frame_myr.getMainMode() == "advanced")

        parent.Bind(wx.EVT_COMBOBOX, parent.GetParent().on_control_changed, self.rebootIf)

        sizerReboot.Add( self.reboot, 0, wx.ALIGN_CENTRE_VERTICAL | wx.BOTTOM | wx.EXPAND, 4 )
        sizerReboot.Add( self.maxErrors, 0, wx.ALIGN_CENTRE_VERTICAL | wx.BOTTOM | wx.EXPAND, 6 )
        sizerReboot.Add( wx.StaticText(parent, 0, " errors if "), 0, wx.ALIGN_CENTRE_VERTICAL | wx.TOP | wx.EXPAND, 4 )
        sizerReboot.Add( self.rebootIf, 1, wx.ALIGN_CENTRE_VERTICAL | wx.BOTTOM | wx.EXPAND, 6)

        self.Add( self.monitor, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.BOTTOM | wx.EXPAND, 4 )
        self.Add( (-1, 10), 0, wx.EXPAND, 4 )
        self.Add( sizerReboot, 0, wx.ALIGN_LEFT | wx.LEFT |  wx.EXPAND, 4 )

    def enable_disable_controls(self, event, trigger_to_frame=True):
        active_errors = self.monitor.GetValue()
        active_reboot = self.reboot.GetValue()

        self.reboot.Enable(active_errors)
        self.maxErrors.Enable(active_errors and active_reboot)
        self.rebootIf.Enable(active_errors and active_reboot)
        if trigger_to_frame:
            self.parent.parent.parentNotebook.notebookControlChanged()

    def enable_disable_sub_controls(self, event, trigger_to_frame=True):
        active_reboot = self.reboot.GetValue()
        self.maxErrors.Enable(active_reboot)
        self.rebootIf.Enable(active_reboot)
        if trigger_to_frame:
            self.parent.parent.parentNotebook.notebookControlChanged()

    def loadErrorCombo(self, isAdvancedMode):
        if isAdvancedMode:
            self.rebootIf.Clear()
            self.rebootIf.Append(ErrorsElement.ERROR_OPTS[0])
            self.rebootIf.Append(ErrorsElement.ERROR_OPTS[1])
            self.rebootIf.Append(ErrorsElement.ERROR_OPTS[2])

        else:
            self.rebootIf.Clear()
            self.rebootIf.Append(ErrorsElement.ERROR_OPTS[2])