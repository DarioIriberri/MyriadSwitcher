__author__ = 'Dario'

import wx
import os
import time
import psutil
import subprocess
import threading
import FrameMYR
import socket
import json
from wx._core import PyDeadObjectError
from console.switcher import HTMLBuilder as clr
from console.switcher import SwitcherData

DEVICE_NONE_SELECTED = "Pick a device..."
ALL_DEVICES          = "All"

STATUS_DISABLED             = "STATUS_DISABLED"
STATUS_READY                = "STATUS_READY"
STATUS_STOPPING             = "STATUS_STOPPING"
STATUS_RUNNING              = "STATUS_RUNNING"
STATUS_STARTING             = "STATUS_STARTING"
STATUS_CRASHED              = "STATUS_CRASHED"
STATUS_EXITING              = "STATUS_EXITING"
STATUS_EXITED               = "STATUS_EXITED"

MIN_TIME_THREAD_PROBED = 60

WAIT_FOR_STREAMS = False

MIN_ITERATIONS = 8
MAX_ITERATIONS = 30


class PanelMinerInstance(wx.Panel):
    def __init__(self, parent, panelMiners, deviceLabel):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.panelMiners = panelMiners
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

        self.waitForStreams = WAIT_FOR_STREAMS
        self.killSignal = False

        self.handler = PanelMinerInstanceHandler(self, size=(-1, 24))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.handler, 0, wx.EXPAND | wx.TOP, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(-1, 4)), 0, wx.EXPAND | wx.TOP, 0)
        sizer.Add(self.resizable_panel, 1, wx.EXPAND | wx.BOTTOM, 0)
        #sizer.Add(self.shellStderr, 1, wx.EXPAND | wx.BOTTOM, 0)

        self.resizable_panel.SplitHorizontally(self.shellStdout, self.shellStderr)

        self.SetSizerAndFit(sizer)

    def executeAlgo(self, maxAlgo, switch):
        if self.handler.status == STATUS_DISABLED:
            return None

        # Except when switching, skip restart of running miners
        if not switch and self.handler.status == STATUS_RUNNING:
            return None

        if self.handler.status in (STATUS_RUNNING, STATUS_STOPPING, STATUS_CRASHED):
            self.handler.statusStopping(stopCrashed=True)

            i = 0

            while not self.handler.status == STATUS_READY and i < MAX_ITERATIONS:
                time.sleep(0.5)
                i += 1

            if i >= MAX_ITERATIONS:
                return False

        if self.handler.status == STATUS_READY:
            if SwitcherData.scryptS == maxAlgo:
                return self.handler.execute('"E:/Litecoin/SGMiner/sgminer.exe" --config "E:/Litecoin/SGMiner/cgminer-MYR - Single.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)

            if SwitcherData.groestlS == maxAlgo:
                return self.handler.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRG.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)

            if SwitcherData.skeinS == maxAlgo:
                return self.handler.execute('"E:/Skein - Single/cgminer.exe" --config "E:/Skein - Single/cgminer-MYR.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)

            if SwitcherData.qubitS == maxAlgo:
                return self.handler.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRQ.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)
                #self.handler.execute('"E:/sgminer v5/sgminer.exe" --config "E:/sgminer v5/cgminer-MYRQ.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)

        return False

    def execute(self, command, waitForStreams = False):
        self._killMiner()

        self.waitForStreams = waitForStreams

        self.clearAll()

        self.process = psutil.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #self.process = psutil.Popen(command, stdout=subprocess.PIPE, shell=True)
        #self.process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

        self.killSignal = False

        self.threadStreams = threading.Thread(target=self.__runStreamThreads, args = [waitForStreams])
        self.threadStreams.start()

        time.sleep(1)

        return self.__isProcessRunning()

    #None if disabled, False is crashed, True otherwise
    def minerStatus(self):
        #if self.handler.status == STATUS_DISABLED:
        #    return None

        return self.handler.status

    def stopMiner(self, exit=False):
        self.killSignal = True

        if not self.waitForStreams:
            self._killMiner()
            #self.handler.statusReady()

        if exit:
            self.handler.statusExiting()
        else:
            self.handler.statusStopping()

    def _killMiner(self):
        try:
            ret = 0

            if self.process and self.isMinerRunning():
                for childProcess in self.process.children():
                    ret = childProcess.kill()
                    ret = ret

                print "terrrrrminatorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                #ret = self.process.terminate()
                ret = self.process.kill()

            return ret
            #return 0

        except (psutil.NoSuchProcess, PyDeadObjectError):
            return 0


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
        try:
            self.__appendText(self.shellStdout, text + os.linesep + os.linesep)

        except PyDeadObjectError:
            pass

    def __runStreamThreads(self, waitForStreams):
        self.threadOut = threading.Thread(target=self.__outputThread, args=[self.shellStdout, self.process.stdout, waitForStreams])
        self.threadErr = threading.Thread(target=self.__outputThread, args=(self.shellStderr, self.process.stderr, waitForStreams))

        self.threadOut.start()
        self.threadErr.start()

        if waitForStreams:
            self.threadOut.join()
            self.threadErr.join()

            self._killMiner()

        #Check Miners...
        try:
            while self.isMinerRunning() and not self.killSignal:
                #print "checking miners .............................................. " + self.minerStatus()
                time.sleep(10)

                #if the kill signal is set, the miner was stopped by the user
            if not self.killSignal:
                self.handler.minerCrashed()
                #print "checking miners2222 .............................................. " + self.minerStatus()

            elif self.minerStatus() == STATUS_EXITING:
                self.handler.status = STATUS_EXITED
                #print "checking miners3333 .............................................. " + self.minerStatus()

            else:
                self.handler.moveOn()

        except PyDeadObjectError:
            pass

        #print "both streams finished.............................................. " + self.minerStatus()

    def __outputThread(self, shell, stream, waitForStreams):
        for line in iter(stream.readline, b''):
            try:
                #print "so????"
                if self.killSignal:
                    #print "killed!!!!!!!!!!!!"
                    break

                self.__appendText(shell, line.rstrip())
                self.__appendText(shell, os.linesep)

            except Exception:
                #print "oooooooooooooooooooooooops!!!!!!!!!!!!"
                break

        #print "outta here!!!!!!!!!!!!!!!!!"

    def __isProcessRunning(self):
        try:
            return self.process.is_running()

        except (psutil.NoSuchProcess, AttributeError) as ex:
            return False

        #return self.process and not self.process.returncode

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

        except PyDeadObjectError as ex:
            pass


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
        #self.deviceCombo.SetValue("AMD Radeon HD7950")
        self.deviceNum.SetValue("All")

        devEditor = wx.Button(self, wx.ID_ANY, size=(36, -1))
        devEditor.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH     + 'img/edit16.ico'))
        devEditor.SetToolTip(wx.ToolTip("Edit " + parent.deviceLabel + " parameters"))
        devEditor.Bind(wx.EVT_BUTTON, self.onDeviceEdit)

        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 0, wx.EXPAND, 0)
        sizer.Add(self.deviceCombo, 10, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(6, -1)), 1, wx.EXPAND, 0)
        sizer.Add(self.deviceNum, 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 1, wx.EXPAND, 0)
        sizer.Add(devEditor, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(80, -1)), 1, wx.EXPAND, 0)

        self.SetSizer(sizer)

        self.enableDevice(False)

    def onDeviceSelected(self, event):
        selection = self.deviceCombo.GetValue()

        self.parent.clearAll()

        if (selection == DEVICE_NONE_SELECTED):
            self.enableDevice(False)
        else:
            self.enableDevice(True)

        #self.deviceLabel.SetFocus()
        self.deviceLabel.SetValue(True)

        #event.Skip()

    def onDeviceToggle(self, event):
        if self.status == STATUS_RUNNING:
            self.parent.stopMiner()
            #self.statusStopping()
        else:
            self.statusDisabled()

        #event.Skip()

    def enableDevice(self, enable):
        label = self.parent.deviceLabel

        if enable:
            self.statusReady()
        else:
            #if self.parent.process.returncode
            self.statusDisabled()

    def onDeviceEdit(self, event):
        #if not self.status == STATUS_RUNNING:
        #self.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRQ.conf" --text-only', waitForStreams = WAIT_FOR_STREAMS)

        #event.Skip()
        pass

    def execute(self, command, waitForStreams):
        self.command = command

        if not self.parent.isMinerRunning():
            ret = self.parent.execute(command, waitForStreams)
            #self.parent.execute('"E:/sgminer v5/sgminer.exe" --config "E:/sgminer v5/cgminer-MYRQ.conf" --text-only', waitForStreams = True)
            #self.parent.execute('"E:/Skein - Single/cgminer.exe" --config "E:/Skein - Single/cgminer-MYR.conf" --text-only')

            self.statusStarting()

            return ret

        return False

    def statusRunning(self):
        if self.status not in ( STATUS_STOPPING, STATUS_EXITING ):
            self.status = STATUS_RUNNING

            self.__deviceRunningColors()

            self.deviceLabel.Enable(True)
            #self.parent.clearAll()

            self.deviceCombo.Enable(False)
            self.deviceNum.Enable(False)

    def statusDisabled(self):
        self.parent.clearAll()
        self.parent.printMessage(self.parent.deviceLabel + " is disabled." + os.linesep + "Pick a device to enable it.")

        self.status = STATUS_DISABLED

        self.parent.panelMiners.resizeMinerPanels(slide=True)

        self.deviceCombo.SetValue(DEVICE_NONE_SELECTED)
        self.deviceNum.SetValue(ALL_DEVICES)

        self.__deviceDisabledColors()

        self.deviceLabel.Enable(False)

        self.deviceCombo.Enable(True)
        self.deviceNum.Enable(True)

    def statusReady(self):
        try:
            self.parent.printMessage(os.linesep + self.deviceCombo.GetValue() + " is now ready to mine!")

            if self.status == STATUS_READY:
                return

            self.status = STATUS_READY

            self.parent.panelMiners.resizeMinerPanels(slide=True)

            self.__deviceReadyColors()

            self.deviceLabel.Enable(True)

            self.deviceCombo.Enable(True)
            self.deviceNum.Enable(True)

        except PyDeadObjectError:
            pass

    def statusCrashed(self):
        self.status = STATUS_CRASHED

        thread = threading.Thread(target=self.statusCrashedThread)
        thread.start()

    def statusCrashedThread(self):
        i = 0

        while self.status == STATUS_CRASHED:
            if i % 2:
                self.__deviceCrashedColors()
            else:
                self.__deviceDisabledColors()

            i += 1

            time.sleep(0.5)

    def statusStopping(self, stopCrashed=False):
        if stopCrashed and self.status == STATUS_CRASHED:
            self.statusReady()
            return

        if self.status in ( STATUS_RUNNING, STATUS_STARTING ) :
            self.status = STATUS_STOPPING

            #self.parent._killMiner()

            thread = threading.Thread(target=self.statusStoppingThread)
            thread.start()

    def statusStoppingThread(self):
        i = 0

        while self.status == STATUS_STOPPING and ( ( not self.killedAlreadyFlag and i < MAX_ITERATIONS ) or i < MIN_ITERATIONS ):
            if i % 2:
                self.__deviceReadyColors()
            else:
                self.__deviceDisabledColors()

            i += 1

            time.sleep(0.5)

        if i >= MAX_ITERATIONS:
            self.parent._killMiner()

        self.killedAlreadyFlag = False

        self.statusReady()

    def statusStarting(self):
        if self.status in (STATUS_READY, STATUS_CRASHED):
            self.status = STATUS_STARTING
            self.deviceLabel.Enable(True)

            thread = threading.Thread(target=self.statusStartingThread)
            thread.start()

    def statusStartingThread(self):
        i = 0

        while self.status == STATUS_STARTING and ( ( not self.parent.isMinerRunning() and i < MAX_ITERATIONS ) or i < MIN_ITERATIONS ):
            if i % 2:
                self.__deviceRunningColors()
            else:
                self.__deviceDisabledColors()

            i += 1

            time.sleep(0.5)

        if i >= MAX_ITERATIONS:
            self.statusReady()

        else:
            self.statusRunning()

    def statusExiting(self):
        if self.status in ( STATUS_DISABLED, STATUS_READY, STATUS_CRASHED ):
            self.status = STATUS_EXITED
        else:
            self.status = STATUS_EXITING

    def moveOn(self, flag = True):
        if self.status == STATUS_RUNNING:
            self.statusReady()
        else:
            if self.status == STATUS_STOPPING:
                self.killedAlreadyFlag = flag

    def minerCrashed(self):
        self.statusCrashed()

        time.sleep(2)

        #if self.command:
        #    self.execute(self.command, WAIT_FOR_STREAMS)


    ####################################################################################################################
    ################################################  PRIVATE MEMBERS  #################################################
    ####################################################################################################################

    # white foreground

    def __deviceDisabledColors(self):
        try:
            #self.deviceLabel.SetBackgroundColour(clr.COLOR_LIGHT_GRAY)
            #self.deviceLabel.SetForegroundColour(clr.COLOR_DARK_GRAY)
            self.deviceLabel.SetBackgroundColour(None)
            self.deviceLabel.SetForegroundColour(None)

        except PyDeadObjectError:
            pass

    def __deviceRunningColors(self):
        try:
            self.deviceLabel.SetBackgroundColour(clr.COLOR_DARK_GREEN)
            self.deviceLabel.SetForegroundColour(clr.COLOR_WHITE)

        except PyDeadObjectError:
            pass

    def __deviceReadyColors(self):
        try:
            self.deviceLabel.SetBackgroundColour(clr.COLOR_ORANGE)
            self.deviceLabel.SetForegroundColour(clr.COLOR_WHITE)

        except PyDeadObjectError:
            pass

    def __deviceCrashedColors(self):
        try:
            self.deviceLabel.SetBackgroundColour(clr.COLOR_SEMI_DARK_RED)
            self.deviceLabel.SetForegroundColour(clr.COLOR_WHITE)

        except PyDeadObjectError:
            pass

    # dark foreground

    #def __deviceDisabledColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_LIGHT_GRAY)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_GRAY)
    #
    #def __deviceRunningColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_SEMI_DARK_GREEN)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_DARK_GRAY)
    #
    #def __deviceReadyColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_DARK_YELLOW)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_DARK_GRAY)
    #
    #def __deviceCrashedColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_SEMI_DARK_RED)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_LIGHT_GRAY)


    # fosforescent

    #def __deviceDisabledColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_LIGHT_GRAY)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_GRAY)
    #
    #def __deviceRunningColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_GREEN)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_DARK_GRAY)
    #
    #def __deviceReadyColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_SEMI_DARK_YELLOW)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_DARK_GRAY)
    #
    #def __deviceCrashedColors(self):
    #    self.deviceLabel.SetBackgroundColour(clr.COLOR_RED)
    #    self.deviceLabel.SetForegroundColour(clr.COLOR_LIGHT_GRAY)