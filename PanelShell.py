__author__ = 'Dario'

import wx
import os
import time
import subprocess
import threading

DEVICE_NONE_SELECTED = "Pick a device..."
ALL_DEVICES          = "All"

DISABLED = "DISABLED"
ENABLED  = "ENABLED"
RUNNING  = "RUNNING"

class PanelShell(wx.Panel):
    def __init__(self, parent, deviceLabel):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.parent = parent
        self.deviceLabel = deviceLabel
        self.process = None

        self.shell = wx.TextCtrl(self, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_RICH2)
        #self.SetDefaultStyle(wx.TextAttr("BLACK", wx.NullColour, wx.Font(10, wx.SCRIPT, wx.ITALIC, wx.BOLD, True)))
        self.shell.SetDefaultStyle(wx.TextAttr("BLACK", wx.NullColour, wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL, False)))
        self.shell.SetEditable(False)
        self.killed = False

        self.handler = PanelShellHandler(self, size=(-1, 24))

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.handler, 0, wx.EXPAND | wx.TOP, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(-1, 4)), 0, wx.EXPAND | wx.TOP, 0)
        sizer.Add(self.shell, 1, wx.EXPAND | wx.BOTTOM, 0)

        self.SetSizer(sizer)

    def execute(self, command):
        self.kill()
        self.handler.runningDevice(True)

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=False)
        thread = threading.Thread(target=self.outputThread)
        thread.start()

    def isRunning(self):
        return not self.process or not self.process.returncode

    def outputThread(self):
        for line in iter(self.process.stdout.readline, b''):
            self.shell.AppendText(line.rstrip())
            self.shell.AppendText(os.linesep)

            if self.killed:
                self.kill()
                break

    def printText(self, text, clear = False):
        if clear:
            self.shell.Clear()

        self.shell.AppendText(text + os.linesep + os.linesep)

    def kill(self):
        if self.process and self.isRunning():
            #self.WriteText(os.linesep + "Killing... " + str(self.p))
            #self.p.terminate()
            self.process.kill()
            self.killed = False
            #time.sleep(4)
            self.printText(os.linesep + "Killed... " + str(self.process))

            self.handler.killedAlready()

    def killProcess(self):
        if self.process and self.isRunning():
            self.killed = True

class PanelShellHandler(wx.Panel):
    def __init__(self, parent, size=wx.DefaultSize):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY, size=size)
        self.parent = parent

        self.status = DISABLED

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
        #self.deviceLabel = wx.StaticText(self, wx.ID_ANY, size=(68, -1), label=parent.deviceLabel)
        #self.deviceLabel.SetFont(wx.Font(11, wx.TELETYPE, wx.NORMAL, wx.BOLD, False))

        self.deviceCombo = wx.ComboBox(self, size=(300, 26), choices=self.devices, style=wx.CB_READONLY)
        self.deviceCombo.Bind(wx.EVT_COMBOBOX, self.onDeviceSelected)
        self.deviceNum = wx.ComboBox(self, size=(50, 26), choices=self.numDevices, style=wx.CB_READONLY)

        self.deviceCombo.SetValue(DEVICE_NONE_SELECTED)
        self.deviceNum.SetValue("All")

        devEditor = wx.Button(self, wx.ID_ANY, "Edit", size=(40, -1))
        devEditor.Bind(wx.EVT_BUTTON, self.onDeviceEdit)
        #self.Bind(wx.EVT_BUTTON, self.onButton, pool_editor)

        #sizerLabel = wx.BoxSizer(wx.HORIZONTAL)


        #sizerLabel.Add(self.deviceLabel, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT, 5)
        #sizerLabel.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 5)

        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.TOP, -1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 0, wx.EXPAND, 0)
        sizer.Add(self.deviceCombo, 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(6, -1)), 0, wx.EXPAND, 0)
        sizer.Add(self.deviceNum, 0, wx.EXPAND | wx.BOTTOM | wx.ALIGN_BOTTOM, 1)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, size=(34, -1)), 0, wx.EXPAND, 0)
        sizer.Add(devEditor, 0, wx.EXPAND | wx.TOP, -1)

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
        if self.status == RUNNING:
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
        self.parent.execute('"E:/SPH-SGMINER - Single/sgminer.exe" --config "E:/SPH-SGMINER - Single/cgminer-MYRQ.conf" --text-only')

        event.Skip()

    def runningDevice(self, running):
        label = self.parent.deviceLabel

        if running:
            self.statusRunning(label)

        else:
            self.statusEnabled(label)

    def statusDisabled(self, label):
        self.deviceCombo.SetValue(DEVICE_NONE_SELECTED)
        self.deviceNum.SetValue(ALL_DEVICES)

        self.deviceLabel.SetBackgroundColour((240, 240, 240))
        self.deviceLabel.SetForegroundColour((0, 0, 0))
        self.deviceLabel.Enable(False)
        self.parent.printText(label + " is disabled. Please, pick a device to enable it.")

        self.deviceCombo.Enable(True)
        self.deviceNum.Enable(True)

        self.status = DISABLED

        self.Layout()

    def statusEnabled(self, label):
        self.deviceLabel.SetBackgroundColour((255, 0, 0))
        self.deviceLabel.SetForegroundColour((255, 255, 255))

        self.deviceLabel.Enable(True)
        #self.parent.killProcess()

        #for i in range(1, 30):
        #    if self.parent.isRunning():
        #        a = i % 2
        #        if a:
        #            self.deviceLabel.SetBackgroundColour((255, 0, 0))
        #            self.deviceLabel.SetForegroundColour((255, 255, 255))
        #        else:
        #            self.deviceLabel.SetBackgroundColour((240, 240, 240))
        #            self.deviceLabel.SetForegroundColour((0, 0, 0))
        #
        #        self.Show()
        #        self.Layout()
        #        self.parent.Show()
        #        self.parent.Layout()
        #        time.sleep(0.5)
        #    else:
        #        break

        self.parent.printText(self.deviceCombo.GetValue() + " is now ready to mine!")

        self.deviceCombo.Enable(True)
        self.deviceNum.Enable(True)

        self.status = ENABLED

        self.Layout()

    def statusEnabledPending(self, label):
        self.parent.killProcess()

        thread = threading.Thread(target=self.statusEnabledPendingThread)
        thread.start()

        #self.parent.printText(self.deviceCombo.GetValue() + " is ready to mine!", True)

        #self.deviceCombo.Enable(True)
        #self.deviceNum.Enable(True)

        #self.status = ENABLED

        self.Layout()

    def statusEnabledPendingThread(self):
        i = 0
        self.killedAlreadyFlag = False

        while not self.killedAlreadyFlag and i < 60:
            a = i % 2
            if a:
                self.deviceLabel.SetBackgroundColour((255, 0, 0))
                self.deviceLabel.SetForegroundColour((255, 255, 255))
            else:
                self.deviceLabel.SetBackgroundColour((240, 240, 240))
                self.deviceLabel.SetForegroundColour((0, 0, 0))

            self.Layout()

            i = i + 1

            time.sleep(0.5)

        if i >= 60:
            self.deviceLabel.SetBackgroundColour((0, 0, 255))
            self.deviceLabel.SetForegroundColour((0, 0, 0))

    def killedAlready(self):
        self.killedAlreadyFlag = True
        self.statusEnabled(self.parent.deviceLabel)

    def statusRunning(self, label):
        self.deviceLabel.SetBackgroundColour((0, 255, 0))
        self.deviceLabel.SetForegroundColour((0, 0, 0))

        self.deviceLabel.Enable(True)
        self.parent.shell.Clear()

        self.deviceCombo.Enable(False)
        self.deviceNum.Enable(False)

        self.status = RUNNING

        self.Layout()
