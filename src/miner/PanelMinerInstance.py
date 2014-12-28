__author__ = 'Dario'

import wx
import os
import time
import psutil
import subprocess
import threading
import FrameMYR
import copy
import io
import json
from wx._core import PyDeadObjectError
from console.switcher import HTMLBuilder as clr
from console.switcher import SwitcherData


DEVICE_NONE_SELECTED = "Pick a device..."
#ALL_DEVICES          = "All"

STATUS_DISABLED             = "STATUS_DISABLED"
STATUS_READY                = "STATUS_READY"
STATUS_STOPPING             = "STATUS_STOPPING"
STATUS_RUNNING              = "STATUS_RUNNING"
STATUS_STARTING             = "STATUS_STARTING"
STATUS_CRASHED              = "STATUS_CRASHED"
STATUS_EXITING              = "STATUS_EXITING"
STATUS_EXITED               = "STATUS_EXITED"

MIN_TIME_THREAD_PROBED = 60

MIN_ITERATIONS = 8
MAX_ITERATIONS = 30


class PanelMinerInstance(wx.Panel):
    def __init__(self, parent, panelMiners, deviceLabel, activeDevice, numDevice, devices):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.panelMiners = panelMiners

        self.deviceLabel = deviceLabel
        self.activeDevice = activeDevice
        self.numDevice = numDevice
        self.devices = devices

        self.process = None

        self.threadStreams = None
        self.threadErr = None
        self.threadErr = None

        self.previousCPUUsage = None
        self.currentCPUUsage  = None

        self.res_panel = wx.SplitterWindow(self, wx.ID_ANY)
        self.res_panel.SetMinimumPaneSize(1)
        self.res_panel.SetSashGravity(0.65)

        self.shellStdout = wx.TextCtrl(self.res_panel, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.shellStderr = wx.TextCtrl(self.res_panel, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.shellStdout.SetDefaultStyle(wx.TextAttr(wx.BLACK, wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))
        self.shellStderr.SetDefaultStyle(wx.TextAttr(wx.RED,   wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))

        self.shellStdout.SetEditable(False)
        self.shellStderr.SetEditable(False)

        self.killSignal = False

        self.handler = PanelMinerInstanceHandler(self, size=(-1, 24))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.handler, 0, wx.EXPAND | wx.TOP, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(-1, 4)), 0, wx.EXPAND | wx.TOP, 0)
        sizer.Add(self.res_panel, 1, wx.EXPAND | wx.BOTTOM, 0)
        #sizer.Add(self.shellStderr, 1, wx.EXPAND | wx.BOTTOM, 0)

        self.res_panel.SplitHorizontally(self.shellStdout, self.shellStderr)

        self.SetSizer(sizer)

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
            algoKey = maxAlgo.strip().lower()
            minerS = self.__findMiner(algoKey)
            configS = self.__findConfig(algoKey)

            return self.handler.execute('"' + minerS + '" --config "' + configS + '" --text-only')

            #if SwitcherData.scryptS == maxAlgo:
            #    #return self.handler.execute('"E:/Litecoin/SGMiner/sgminer.exe" --config "E:/Litecoin/SGMiner/cgminer-MYR - Single.conf" --text-only')
            #    #return self.handler.execute('"E:/Litecoin/SGMiner/sgminer.exe" --config "E:/Litecoin/SGMiner/cgminer-MYR - ELECTRUM.conf" --text-only')
            #    return self.handler.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYR - ELECTRUM.conf" --text-only')
            #
            #if SwitcherData.groestlS == maxAlgo:
            #    #return self.handler.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRG.conf" --text-only')
            #    return self.handler.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRG - ELECTRUM.conf" --text-only')
            #
            #if SwitcherData.skeinS == maxAlgo:
            #    #return self.handler.execute('"E:/Skein - Single/cgminer.exe" --config "E:/Skein - Single/cgminer-MYR.conf" --text-only')
            #    return self.handler.execute('"E:/Skein - Single/cgminer.exe" --config "E:/Skein - Single/cgminer-MYR - ELECTRUM.conf" --text-only')
            #
            #if SwitcherData.qubitS == maxAlgo:
            #    #self.handler.execute('"E:/sgminer v5/sgminer.exe" --config "E:/sgminer v5/cgminer-MYRQ.conf" --text-only')
            #    return self.handler.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRQ - ELECTRUM.conf" --text-only')

        return False

    def execute(self, command):
        self._killMiner()

        self.clearAll()

        self.process = psutil.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        #self.process = psutil.Popen(command, stdout=subprocess.PIPE, shell=True)
        #self.process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

        self.killSignal = False

        self.threadStreams = threading.Thread(target=self.__runStreamThreads)
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

        self._killMiner()

        if exit:
            self.handler.statusExiting()
        else:
            self.handler.statusStopping()

    def __findMiner(self, algoKey):
        miner = self.handler.getDevice()[algoKey]['miner']

        return FrameMYR.FrameMYRClass.RESOURCE_PATH + 'miners/' + miner + '/' + miner

    def __findConfig(self, algoKey):
        miner = self.handler.getDevice()[algoKey]['miner']
        config = self.handler.getDevice()[algoKey]['config']
        configPath = FrameMYR.FrameMYRClass.RESOURCE_PATH + 'miners/' + miner + '/' + config

        #Open the config file
        f = open(os.getcwd() + '/' + configPath)
        data = f.read()
        f.close()

        configData = json.loads(data)

        #Add the pool section with the user config, then save it back
        #the first in the list must be the active/selected pool
        poolSelected = self.panelMiners.frame.notebook.getStoredConfigParam(algoKey + 'Pool')
        poolData = self.panelMiners.frame.notebook.getStoredConfigParam(algoKey + 'PoolData')

        finalPoolDataList = list()
        restPoolDataList  = list()

        for pool in poolData:
            del pool['poolBalanceUrl']

            if poolSelected == pool['url']:
                finalPoolDataList = [pool]
            else:
                restPoolDataList.append(pool)

        finalPoolDataList += restPoolDataList

        configData['pools'] = finalPoolDataList

        io.open(configPath, 'wt', encoding='utf-8').write(unicode(json.dumps(configData)))

        return configPath

    def _killMiner(self):
        try:
            ret = 0

            if self.process and self.isMinerRunning():
                for childProcess in self.process.children():
                    ret = childProcess.kill()
                    ret = ret

                #print "terrrrrminatorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
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

    def __runStreamThreads(self):
        self.threadOut = threading.Thread(target=self.__outputThread, args=[self.shellStdout, self.process.stdout])
        self.threadErr = threading.Thread(target=self.__outputThread, args=(self.shellStderr, self.process.stderr))

        self.threadOut.start()
        self.threadErr.start()

        #Check Miners...
        try:
            CHECK_POLL_RATE = 5

            #Wait 10 seconds before checking the miner to give it plenty of time to start
            time.sleep(CHECK_POLL_RATE)

            while self.isMinerRunning() and not self.killSignal:
                #print "checking miners .............................................. " + self.minerStatus()
                time.sleep(CHECK_POLL_RATE)

            #if the kill signal is set, the miner was stopped by the user
            if not self.killSignal:
                self.handler.minerCrashed()
                #print "checking miners CRASHED!!! .............................................. " + self.minerStatus()

            elif self.minerStatus() == STATUS_EXITING:
                self.handler.status = STATUS_EXITED
                #print "checking miners EXITED zzzzzzz .............................................. " + self.minerStatus()

            else:
                self.handler.moveOn()

        except PyDeadObjectError:
            pass

        #print "both streams finished.............................................. " + self.minerStatus()

    def __outputThread(self, shell, stream):
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

        self.devices = [DEVICE_NONE_SELECTED] + [device['name'] for device in self.parent.devices]

        self.numDevices = [
            '1',
            '2',
            '3',
            '4',
            '5',
            '6'
        ]

        self.deviceLabel = wx.ToggleButton(self, -1, label=parent.deviceLabel, size=(68, -1))
        self.deviceLabel.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        #self.deviceLabel.SetDefaultStyle(wx.TextAttr("BLACK", wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))

        self.deviceLabel.Bind(wx.EVT_TOGGLEBUTTON, self.onDeviceToggle)

        self.deviceCombo = wx.ComboBox(self, size=(200, 26), choices=self.devices, style=wx.CB_READONLY)
        self.deviceCombo.Bind(wx.EVT_COMBOBOX, self.onDeviceSelected)
        self.deviceNum = wx.ComboBox(self, size=(30, 26), choices=self.numDevices, style=wx.CB_READONLY)
        self.deviceNum.Bind(wx.EVT_COMBOBOX, self.onNumDeviceSelected)

        if self.parent.activeDevice and self.parent.activeDevice != DEVICE_NONE_SELECTED:
            self.deviceCombo.SetValue(self.parent.activeDevice)
            self.enableDevice(True)

        else:
            self.deviceCombo.SetValue(DEVICE_NONE_SELECTED)
            self.enableDevice(False)

        if self.parent.numDevice:
            self.deviceNum.SetValue(self.parent.numDevice)
        else:
            self.deviceNum.SetValue(self.numDevices[0])

        devEditor = wx.Button(self, wx.ID_ANY, size=(34, -1))
        devEditor.SetBitmap(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH     + 'img/edit16.ico'))
        devEditor.SetToolTip(wx.ToolTip("Edit " + parent.deviceLabel + " parameters"))
        devEditor.Bind(wx.EVT_BUTTON, self.onDeviceEdit)

        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 0, wx.EXPAND, 0)
        sizer.Add(self.deviceCombo, 10, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, id=wx.ID_ANY, size=(6, -1)), 1, wx.EXPAND, 0)
        sizer.Add(wx.StaticText(self, label=" x ", id=wx.ID_ANY, size=(-1, -1)), 0, wx.TOP, 4)
        sizer.Add(self.deviceNum, 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 1, wx.EXPAND, 0)
        sizer.Add(devEditor, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(80, -1)), 1, wx.EXPAND, 0)

        self.SetSizer(sizer)

    def getDevice(self):
        device = self.findDevice(self.deviceCombo.GetValue())
        if not device:
            return None

        device['num'] = int(self.deviceNum.GetValue())
        return device

    def onDeviceSelected(self, event):
        selection = self.deviceCombo.GetValue()

        self.parent.panelMiners.deviceChanged()

        self.parent.clearAll()
        self.parent.panelMiners.saveDevices()

        self.enableDevice(not selection == DEVICE_NONE_SELECTED)

        #self.deviceLabel.SetFocus()
        self.deviceLabel.SetValue(True)

        #event.Skip()

    def onNumDeviceSelected(self, event):
        self.parent.panelMiners.deviceChanged()
        self.parent.panelMiners.saveDevices()

        #event.Skip()

    def findDevice(self, name):
        dev = [device for device in self.parent.devices if device['name'] == name]
        return copy.deepcopy(dev[0]) if len(dev) == 1 else None

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
        #self.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRQ.conf" --text-only')

        #event.Skip()
        pass

    def execute(self, command):
        self.command = command

        if not self.parent.isMinerRunning():
            ret = self.parent.execute(command)
            #self.parent.execute('"E:/sgminer v5/sgminer.exe" --config "E:/sgminer v5/cgminer-MYRQ.conf" --text-only')
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
        self.deviceNum.SetValue(self.numDevices[0])

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