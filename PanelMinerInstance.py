__author__ = 'Dario'

import wx
import os
import time
import psutil
import subprocess
import threading
import signal
import HTMLBuilder as clr
from wx._core import PyDeadObjectError
import wx.richtext as rt

DEVICE_NONE_SELECTED = "Pick a device..."
ALL_DEVICES          = "All"

STATUS_DISABLED             = "DISABLED"
STATUS_ENABLED              = "ENABLED"
STATUS_ENABLED_PENDING      = "ENABLED_PENDING"
STATUS_RUNNING              = "RUNNING"
STATUS_RUNNING_PENDING      = "STATUS_RUNNING_PENDING"

MIN_TIME_THREAD_PROBED = 60

WAIT_FOR_STREAMS = True
#WAIT_FOR_STREAMS = False


class PanelMinerInstance(wx.Panel):
    def __init__(self, parent, deviceLabel):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.deviceLabel = deviceLabel
        self.process = None

        self.threadStreams = None
        self.threadErr = None
        self.threadErr = None

        self.previousCPUUsage = None
        self.currentCPUUsage  = None

        self.resizable_panel = wx.SplitterWindow(self, wx.ID_ANY)
        self.resizable_panel.SetMinimumPaneSize(1)
        self.resizable_panel.SetSashGravity(0.65)

        self.shellStdout = wx.TextCtrl(self.resizable_panel, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.shellStderr = wx.TextCtrl(self.resizable_panel, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.shellStdout.SetDefaultStyle(wx.TextAttr(wx.BLACK, wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))
        self.shellStderr.SetDefaultStyle(wx.TextAttr(wx.RED,   wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))

        self.shellStdout.SetEditable(False)
        self.shellStderr.SetEditable(False)

        #self.shell = rt.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        #self.textAttr = rt.RichTextAttr()
        #self.textAttr.SetTextColour(wx.BLACK)
        #self.textAttr.SetBackgroundColour(wx.NullColour)
        #self.textAttr.SetFontFaceName("Courier")
        #self.textAttr.SetFontSize(6)
        #self.textAttr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        #self.textAttr.SetFontStyle(wx.FONTSTYLE_NORMAL)
        #self.textAttr.SetFontUnderlined(False)
        #self.shell.SetDefaultStyle(self.textAttr)

        #self.shell = wx.PyOnDemandOutputWindow(self)
        #self.SetDefaultStyle(wx.TextAttr("BLACK", wx.NullColour, wx.Font(10, wx.SCRIPT, wx.ITALIC, wx.BOLD, True)))

        self.killed = False

        self.handler = PanelMinerInstanceHandler(self, size=(-1, 24))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.handler, 0, wx.EXPAND | wx.TOP, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(-1, 4)), 0, wx.EXPAND | wx.TOP, 0)
        sizer.Add(self.resizable_panel, 1, wx.EXPAND | wx.BOTTOM, 0)
        #sizer.Add(self.shellStderr, 1, wx.EXPAND | wx.BOTTOM, 0)

        self.resizable_panel.SplitHorizontally(self.shellStdout, self.shellStderr)

        self.SetSizer(sizer)

    def execute(self, command, waitForStreams = False):
        #print "execute"
        self.__kill()

        self.waitForStreams = waitForStreams

        self.process = psutil.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #self.process = psutil.Popen(command, stdout=subprocess.PIPE, shell=True)
        #self.process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

        self.killed = False

        self.threadStreams = threading.Thread(target=self.__runStreamThreads, args = [waitForStreams])
        self.threadStreams.start()

        #self.killed = False

    def killProcess(self, forcibly = False):
        if self.__isProcessRunning():
            self.killed = True

        if not self.waitForStreams or forcibly:
            self.__obliterate()
            self.handler.moveOn()

    def isMinerRunning(self):
        if not self.__isProcessRunning():
            return False

        children = self.process.children()

        if not children or len(children) == 0:
            return False

        for childProcess in children:
            if not childProcess.is_running():
                return False

        return not self.__minerFreezed()

    def clearAll(self):
        self.shellStdout.Clear()
        self.shellStderr.Clear()

    def printMessage(self, text):
        #if clear:
        #    self.shell.Clear()

        self.__appendText(self.shellStdout, text + os.linesep + os.linesep)

    def __runStreamThreads(self, waitForStreams):
        self.threadOut = threading.Thread(target=self.__outputThread, args=[self.shellStdout, self.process.stdout, waitForStreams])
        self.threadErr = threading.Thread(target=self.__outputThread, args=(self.shellStderr, self.process.stderr, waitForStreams))

        self.threadOut.start()
        self.threadErr.start()

        if waitForStreams:
            self.threadOut.join()
            self.threadErr.join()

            self.__kill()

        #Check Miners...
        while self.isMinerRunning():
            time.sleep(10)

        #if the kill signal is set, the miner was stopped by the user
        if not self.killed:
            self.handler.minerFailed()

    def __outputThread(self, shell, stream, waitForStreams):
        for line in iter(stream.readline, b''):
            if self.killed:
                break

            try:
                self.__appendText(shell, line.rstrip())
                self.__appendText(shell, os.linesep)

            except PyDeadObjectError:
                break

        #if not waitForStreams:
        #    print("__outputThread")
        #    self.__kill(stream)

    def __isProcessRunning(self):
        try:
            return self.process.is_running()

        except (psutil.NoSuchProcess, AttributeError) as ex:
            #print ex
            return False

        #return self.process and not self.process.returncode

    def __kill(self, stream = None):
        if self.__isProcessRunning():
            #self.WriteText(os.linesep + "Killing... " + str(self.p))
            #self.p.terminate()
            ret = self.__obliterate()
            #time.sleep(4)
            self.printMessage(os.linesep + "Killed... " + ("" if not stream else str(stream)))

        #self.killed = False
        self.handler.moveOn()

    def __obliterate(self):
        try:
            for childProcess in self.process.children():
                ret = childProcess.kill()
                ret = ret

            ret = self.process.kill()

            return ret

        except psutil.NoSuchProcess:
            return 0

    def __getCPUUsage(self):
        try:
            miner = self.process.children()[0]
        except:
            return None

        return CPUUsage(miner.pid, miner.get_cpu_times().user, time.time())

    def __minerFreezed(self):
        freezed = False
        #if config_json["debug"] or not config_json["monitor"]:
        #    return None

        self.currentCPUUsage = self.__getCPUUsage()

        if not self.currentCPUUsage:
            return True

        if self.previousCPUUsage:
            if (self.currentCPUUsage.timeCPUProbed - self.previousCPUUsage.timeCPUProbed) < MIN_TIME_THREAD_PROBED:
                return False

            if self.previousCPUUsage:
                freezed = self.currentCPUUsage.cpuTime == self.previousCPUUsage.cpuTime

        self.previousCPUUsage = self.currentCPUUsage

        return freezed

    def __appendText(self, shell, text):
        try:
            shell.AppendText(text)

        except Exception as ex:
            print "PanelMinerInstance.__appendText()" + str(ex)

        #self.shell.BeginTextColour(textColor)
        #try:
        #    self.shell.SetFocus()
        #    self.shell.WriteText(text)
        #except Exception as ex:
        #    print "oops!"
        ##self.shell.AppendText(text)
        #self.shell.EndTextColour()

        #wx.PyOnDemandOutputWindow.write(self.shell, text)


class CPUUsage():
    def __init__(self, pid, cpuTime, timeCPUProbed):
        self.pid = pid
        self.timeCPUProbed = timeCPUProbed
        self.cpuTime = cpuTime


class PanelMinerInstanceHandler(wx.Panel):
    def __init__(self, parent, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, size=size)

        self.parent = parent

        self.status = STATUS_DISABLED
        self.killedAlreadyFlag = False
        self.command = None

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.devices = [
                            DEVICE_NONE_SELECTED,
                            "AMD Radeon HD5770",
                            "AMD Radeon HD5850",
                            "AMD Radeon HD5870",
                            "AMD Radeon HD6950",
                            "AMD Radeon HD6970",
                            "AMD Radeon HD7950",
                            "AMD Radeon HD7970",
                            "AMD Radeon R9 280",
                            "AMD Radeon R9 280X",
                            "AMD Radeon R9 290",
                            "AMD Radeon R9 290X",
                            "Nvidia GeForce GTX 280",
                            "Nvidia GeForce GTX 460",
                            "Nvidia GeForce GTX 470",
                            "Nvidia GeForce GTX 480",
                            "Nvidia GeForce GTX 560",
                            "Nvidia GeForce GTX 560 Ti",
                            "Nvidia GeForce GTX 570",
                            "Nvidia GeForce GTX 580",
                            "Nvidia GeForce GTX 670",
                            "Nvidia GeForce GTX 680",
                            "Nvidia GeForce GTX 770",
                            "Nvidia GeForce GTX 780",
                            "Nvidia GeForce GTX 780 Ti",
                            "Nvidia GeForce Titan"
                       ]

        self.numDevices = [
                            ALL_DEVICES,
                            "x 1",
                            "x 2",
                            "x 3",
                            "x 4"
                          ]

        self.deviceLabel = wx.ToggleButton(self, -1, label=parent.deviceLabel, size=(68, -1))
        self.deviceLabel.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        #self.deviceLabel.SetDefaultStyle(wx.TextAttr("BLACK", wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))

        self.deviceLabel.Bind(wx.EVT_TOGGLEBUTTON, self.onDeviceToggle)

        self.deviceCombo = wx.ComboBox(self, size=(200, 26), choices=self.devices, style=wx.CB_READONLY)
        self.deviceCombo.Bind(wx.EVT_COMBOBOX, self.onDeviceSelected)
        self.deviceNum = wx.ComboBox(self, size=(50, 26), choices=self.numDevices, style=wx.CB_READONLY)

        self.deviceCombo.SetValue(DEVICE_NONE_SELECTED)
        self.deviceNum.SetValue("All")

        devEditor = wx.Button(self, wx.ID_ANY, "Edit", size=(40, -1))
        devEditor.Bind(wx.EVT_BUTTON, self.onDeviceEdit)

        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 0, wx.EXPAND, 0)
        sizer.Add(self.deviceCombo, 2, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(6, -1)), 0, wx.EXPAND, 0)
        sizer.Add(self.deviceNum, 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 0, wx.EXPAND, 0)
        sizer.Add(devEditor, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(80, -1)), 1, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.enableDevice(False)

    def onDeviceSelected(self, event):
        selection = self.deviceCombo.GetValue()

        if (selection == DEVICE_NONE_SELECTED):
            self.enableDevice(False)
        else:
            self.enableDevice(True)

        event.Skip()

    def onDeviceToggle(self, event):
        if self.status == STATUS_RUNNING:
            self.statusEnabledPending(self.parent.deviceLabel)
        else:
            self.statusDisabled(self.parent.deviceLabel)

        event.Skip()

    def enableDevice(self, enable):
        label = self.parent.deviceLabel

        if enable:
            self.statusEnabled(label)
        else:
            #if self.parent.process.returncode
            self.statusDisabled(label)

    def onDeviceEdit(self, event):
        #if not self.status == STATUS_RUNNING:
        self.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRQ.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)

        event.Skip()

    def execute(self, command, waitForStreams):
        self.command = command

        if not self.parent.isMinerRunning():
            self.parent.execute(command, waitForStreams)
            #self.parent.execute('"E:/sgminer v5/sgminer.exe" --config "E:/sgminer v5/cgminer-MYRQ.conf" --text-only', waitForStreams = True)
            #self.parent.execute('"E:/Skein - Single/cgminer.exe" --config "E:/Skein - Single/cgminer-MYR.conf" --text-only')

            self.statusRunningPending()

    #def setRunningDevice(self, running):
    #    label = self.parent.deviceLabel
    #
    #    if running:
    #        self.statusRunning(label)
    #
    #
    #    else:
    #        self.statusEnabled(label)

    def statusRunning(self, label = None):
        self.status = STATUS_RUNNING

        self.deviceLabel.SetBackgroundColour(clr.COLOR_GREEN)
        self.deviceLabel.SetForegroundColour(clr.COLOR_BLACK)

        self.deviceLabel.Enable(True)
        self.parent.clearAll()

        self.deviceCombo.Enable(False)
        self.deviceNum.Enable(False)

        self.Layout()

    def statusDisabled(self, label):
        self.status = STATUS_DISABLED

        self.deviceCombo.SetValue(DEVICE_NONE_SELECTED)
        self.deviceNum.SetValue(ALL_DEVICES)

        self.deviceLabel.SetBackgroundColour(clr.COLOR_LIGHT_GRAY)
        self.deviceLabel.SetForegroundColour((0, 0, 0))
        self.deviceLabel.Enable(False)
        self.parent.printMessage(label + " is disabled. Pick a device to enable it.")

        self.deviceCombo.Enable(True)
        self.deviceNum.Enable(True)


        self.Layout()

    def statusEnabled(self, label = None):
        self.status = STATUS_ENABLED

        self.deviceLabel.SetBackgroundColour(clr.COLOR_RED)
        self.deviceLabel.SetForegroundColour(clr.COLOR_WHITE)

        self.deviceLabel.Enable(True)

        self.parent.printMessage(self.deviceCombo.GetValue() + " is now ready to mine!")

        self.deviceCombo.Enable(True)
        self.deviceNum.Enable(True)

        self.Layout()

    def statusEnabledPending(self, label = None):
        self.status = STATUS_ENABLED_PENDING

        self.parent.killProcess()

        thread = threading.Thread(target=self.statusEnabledPendingThread)
        thread.start()

        self.Layout()

    def statusEnabledPendingThread(self):
        i = 0

        MAX_ITERATIONS = 60

        while not self.killedAlreadyFlag and i < MAX_ITERATIONS:
            if i % 2:
                self.deviceLabel.SetBackgroundColour(clr.COLOR_RED)
                self.deviceLabel.SetForegroundColour(clr.COLOR_WHITE)
            else:
                self.deviceLabel.SetBackgroundColour(clr.COLOR_LIGHT_GRAY)
                self.deviceLabel.SetForegroundColour(clr.COLOR_BLACK)

            self.Layout()

            i += 1

            time.sleep(0.5)

        if i >= MAX_ITERATIONS:
            #print "Fuck, kill timeouuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuut!!!!!!"
            self.parent.killProcess(forcibly = True)

        self.killedAlreadyFlag = False

        self.statusEnabled(self.parent.deviceLabel)

    def statusRunningPending(self, label = None):
        self.status = STATUS_RUNNING_PENDING
        self.deviceLabel.Enable(True)

        thread = threading.Thread(target=self.statusRunningPendingThread)
        thread.start()

        self.Layout()

    def statusRunningPendingThread(self):
        i = 0

        MIN_ITERATIONS = 6
        MAX_ITERATIONS = 60

        while ( not self.parent.isMinerRunning() and i < MAX_ITERATIONS ) or i < MIN_ITERATIONS:
            if i % 2:
                self.deviceLabel.SetBackgroundColour(clr.COLOR_GREEN)
                self.deviceLabel.SetForegroundColour(clr.COLOR_BLACK)
            else:
                self.deviceLabel.SetBackgroundColour(clr.COLOR_LIGHT_GRAY)
                self.deviceLabel.SetForegroundColour(clr.COLOR_BLACK)

            self.Layout()
            self.parent.Layout()
            self.parent.parent.Layout()
            self.parent.parent.parent.Layout()

            i += 1

            time.sleep(0.5)

        if i >= MAX_ITERATIONS:
            #print "Fuck, start timeouuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuut!!!!!!"
            self.parent.killProcess(forcibly = True)

            self.statusEnabled(self.parent.deviceLabel)

        else:
            self.statusRunning(self.parent.deviceLabel)

    def moveOn(self, flag = True):
        if self.status == STATUS_RUNNING:
            self.statusEnabled()
        else:
            if self.status == STATUS_ENABLED_PENDING:
                self.killedAlreadyFlag = flag

    def minerFailed(self):
        #todo: if restart:
        self.statusEnabled()

        time.sleep(2)

        if self.command:
            self.execute(self.command, WAIT_FOR_STREAMS)