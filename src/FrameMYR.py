__author__ = 'Dario'

import wx
import os
import time
import threading
from wx.lib.buttons import *
from Tkinter import Tk
from console.PanelConsole import PanelConsole
from console.switcher import SwitcherData
from miner.PanelMiners import PanelMiners
from notebook.ExpandableNotebook import ExpandableNotebook
from notebook.tabs.ConfigTab import ConfigTab
from notebook.tabs.SwitchingModesTab import SwitchingModesTab
from notebook.tabs.MiscellaneousTab import MiscellaneousTab
from event.EventLib import EVT_STATUS_BAR_EVENT, EVT_DUMMY_EVENT, DummyEvent


VERSION  = "0.3"
REVISION = 0

GRAVITY = 0.6

BUTTON_SIZE  = (76, 26)

class FrameMYRClass(wx.Frame):
    RESOURCE_PATH = None

    def __init__(self, resouce_path=""):
        #self.resouce_path = resouce_path
        FrameMYRClass.RESOURCE_PATH = resouce_path
        #FrameMYR.FrameMYR.RESOURCE_PATH = resouce_path

        self.gravity = None
        self.mining  = False

        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Myriad Switcher Configurator... ",
                          size=(710, 383)
        )

        self.prev_size = self.GetSize()
        self.isNotebookSimple = True

        #self.setTitle(self.activeFile)
        #self.Bind(wx.EVT_SIZE, self.OnResize)

        self.status_bar = self.CreateStatusBar()

        self.buttonSave = wx.Button(self, wx.ID_SAVE, "Save  ", size=BUTTON_SIZE, style=wx.BU_EXACTFIT)
        self.buttonCancel = wx.Button(self, wx.ID_CANCEL, "Cancel", size=BUTTON_SIZE)
        self.buttonRun = wx.Button(self, -1, "Start  ", size=BUTTON_SIZE)
        self.buttonResume = wx.Button(self, -1, "Resume", size=BUTTON_SIZE)
        self.buttonStop = wx.Button(self, wx.ID_STOP, "Stop  ", size=BUTTON_SIZE)
        self.buttonDefaults = wx.Button(self, wx.ID_RESET, "Defaults", size=BUTTON_SIZE)
        self.buttonMainMode = wx.ToggleButton(self, -1, "Simple", size=BUTTON_SIZE)

        self.buttonWait1 = wx.Button(self, wx.ID_STOP, "Wait   ", size=BUTTON_SIZE)
        self.buttonWait2 = wx.Button(self, wx.ID_STOP, "Wait.  ", size=BUTTON_SIZE)
        self.buttonWait3 = wx.Button(self, wx.ID_STOP, "Wait.. ", size=BUTTON_SIZE)
        self.buttonWait4 = wx.Button(self, wx.ID_STOP, "Wait...", size=BUTTON_SIZE)

        self.buttonSave.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH     + 'img/save16.ico'), wx.LEFT)
        self.buttonCancel.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/cancel16.ico'), wx.LEFT)
        #self.buttonCancel.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/back16.ico'), wx.LEFT)
        self.buttonDefaults.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/defaults16.ico'), wx.LEFT)
        self.buttonRun.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/rungreen16.ico'), wx.LEFT)
        self.buttonResume.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/resume16.ico'), wx.LEFT)
        self.buttonStop.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/stop16.ico'), wx.LEFT)

        self.buttonWait1.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/sw16-1.ico'), wx.LEFT)
        self.buttonWait2.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/sw16-2.ico'), wx.LEFT)
        self.buttonWait3.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/sw16-3.ico'), wx.LEFT)
        self.buttonWait4.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/sw16-4.ico'), wx.LEFT)

        # Setting up the menu.
        filemenu= wx.Menu()
        donationsmenu= wx.Menu()
        helpmenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save"," Save configuration")
        menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "Save &as..."," Save configuration as...")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuRTFM = helpmenu.Append(wx.ID_ANY, "&Open the User Guide"," Open the user guide")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuDonateMYR = donationsmenu.Append(wx.ID_ANY, "Donate &Myriadcoins (MYR)"," Copies MYR address to clipboard to donate Myriadcoins")
        menuDonateBTC = donationsmenu.Append(wx.ID_ANY, "Donate &Bitcoins (BTC)"," Copies MYR address to clipboard to donate Bitcoins")

        # Events.
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        self.Bind(wx.EVT_MENU, self.onSaveAs, menuSaveAs)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onRTFM, menuRTFM)
        self.Bind(wx.EVT_MENU, self.onDonateMYR, menuDonateMYR)
        self.Bind(wx.EVT_MENU, self.onDonateBTC, menuDonateBTC)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onButtonRun, self.buttonRun)
        self.Bind(wx.EVT_BUTTON, self.onButtonResume, self.buttonResume)
        self.Bind(wx.EVT_BUTTON, self.onButtonStop, self.buttonStop)
        self.Bind(wx.EVT_BUTTON, self.onButtonCancel, self.buttonCancel)
        self.Bind(wx.EVT_BUTTON, self.onButtonDefaults, self.buttonDefaults)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.buttonSave)

        #self.buttonSave.SetBitmapMargins(14, 0)
        #self.buttonCancel.SetBitmapMargins((14, 0))

        # Creating the menubar.
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(donationsmenu,"&Donations") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

        self.resizable_panel = wx.SplitterWindow(self, wx.ID_ANY)
        self.resizable_panel.SetMinimumPaneSize(1)

        # Create the Notebook
        self.panelNotebook = wx.Panel(self)

        self.panelConsole = PanelConsole(self.resizable_panel, self)
        self.panelConsole.addMessageEventListener(self.set_status_text)
        #self.panelConsole = webview.WebView.New(PanelConsole.PanelConsole)
        self.panelConsole.SetBackgroundColour("Black")

        self.miners = PanelMiners(parent = self.resizable_panel, frame=self)

        self.notebook = ExpandableNotebook(self.panelNotebook, self)
        self.notebook.addTab(ConfigTab, "Main Config", FrameMYRClass.RESOURCE_PATH + 'img/aquachecked.ico')
        self.notebook.addTab(SwitchingModesTab, "Switching Modes", FrameMYRClass.RESOURCE_PATH + 'img/switching16.ico')
        self.notebook.addTab(MiscellaneousTab, "Miscellaneous", FrameMYRClass.RESOURCE_PATH + 'img/advanced.ico')
        #self.notebook.addTab(MiscellaneousTab, "Miscellaneous2", FrameMYRClass.RESOURCE_PATH + 'img/advanced.ico')
        self.notebook.buildNotebook()

        self.setMainMode(self.notebook.getStoredConfigParam('mainMode'))
        self.setTitle(self.notebook.activeFile)

        self.Bind(wx.EVT_TOGGLEBUTTON, self.onMainModeToggle, self.buttonMainMode)
        #self.notebook.broadcastBind(self, wx.EVT_TOGGLEBUTTON, self.buttonToggle, event_id="main_config")

        #self.notebook.broadcast_bind(self, EVT_NOTEBOOK_BROADCAST_EVENT, event_id="lalala")
        #self.notebook.Bind(EVT_NOTEBOOK_BROADCAST_EVENT, self.notebook.onBroadcastEventToAllTabs)
        #wx.PostEvent(self, NotebookBroadcastEvent(data="main_config"))
        #self.notebook.broadcastEventToAllTabs(data=11, kjgkg="d")

        self.sizerTotal = wx.BoxSizer(wx.VERTICAL)

        # Buttons section
        button_bottom_gap = 4
        flagsButtonRun = wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap).Proportion(0)
        sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        sizerButtons.AddF(self.buttonSave, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonCancel, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonDefaults, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.Add(wx.StaticLine(self, -1, size=(-1, 20), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.BOTTOM, 3)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonMainMode, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))

        spacerFlags = wx.SizerFlags().Expand().Border(wx.ALL, 1).Proportion(1)
        sizerButtons.AddF((-1, -1), spacerFlags)
        sizerButtons.AddF(self.buttonRun, flagsButtonRun)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonResume, flagsButtonRun)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonStop, flagsButtonRun)
        sizerButtons.AddF(self.buttonWait1, flagsButtonRun)
        sizerButtons.AddF(self.buttonWait2, flagsButtonRun)
        sizerButtons.AddF(self.buttonWait3, flagsButtonRun)
        sizerButtons.AddF(self.buttonWait4, flagsButtonRun)

        self.sizerTotal.Add(self.panelNotebook, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)
        self.sizerTotal.Add(sizerButtons, 0, wx.EXPAND | wx.RIGHT | wx.LEFT | wx.TOP, 1)

        self.resizable_panel.SetSashGravity(GRAVITY)
        #self.resizable_panel.SplitHorizontally(self.panelConsole, self.shell)
        self.sizerTotal.Add(self.resizable_panel, 5, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 4)

        self.icon = wx.Icon(FrameMYRClass.RESOURCE_PATH + 'img/myriadS1.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        #self.icon = wx.Icon('myriadS1.ico', wx.BITMAP_TYPE_ICO)

        self.SetSizer(self.sizerTotal)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUBAR))

        self.Bind(EVT_STATUS_BAR_EVENT, self.on_mouse_over)
        self.notebook.broadcastEventToAllTabs(event_id="main_config",
                                              event_value=("advanced" == self.getMainMode()))

        self.Maximize()
        self.Layout()
        self.Show()

        self.buttonWait1.Hide()
        self.buttonWait2.Hide()
        self.buttonWait3.Hide()
        self.buttonWait4.Hide()

        self.chechReboot()

        try:
            os.remove("reboot")
            os.remove(os.getenv('APPDATA') + '\\Microsoft\Windows\Start Menu\Programs\Startup\\myriadSwitcher.lnk')
        except:
            pass

        self.enabled_buttons(False)
        self.buttonStop.Enable(False)
        self.buttonResume.Enable(self.isThereAPreviousSession())

    def chechReboot(self):
        if os.path.isfile("reboot"):
            self.panelConsole.mine(self.notebook.activeFile, rebooting=True)

    # Required for NotebookMyr
    def notebookControlChanged(self, event=None):
        self.enabled_buttons(True)

    # Enables the Save & Cancel buttons
    def enabled_buttons(self, enabled):
        self.buttonCancel.Enable(enabled)
        self.buttonSave.Enable(enabled)

    @staticmethod
    def getVersion():
        #return VERSION + "." + str(REVISION) + "-" + BRANCH
        return VERSION + "." + str(REVISION)

    # Sets the main window title
    def setTitle(self, activeFile):
        self.SetTitle("Myriad Switcher " + self.getVersion() + "... (" + activeFile + ")")

    def on_mouse_over(self, event):
        self.status_bar.SetStatusText(event.message)

    def set_status_text(self, status_text):
        if status_text:
            self.status_bar.SetStatusText(status_text)

    def onAbout(self, event):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " Myriad Switcher " + self.getVersion() + " by Dario Iriberri (dazz).", "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onRTFM(self, event):
        try:
            os.system("start README/README.html")
        except:
            print "Failed to open readme file"

    def onDonateMYR(self, event):
        myr_address = "MPLArvmR7dQrF7BCPDFsRCniFnCJhZkG9d"
        self.writeClipboard(myr_address)
        dlg = wx.MessageDialog(self, "MYR address " + myr_address + " copied to clipboard.\n\nThanks for your support.", "MYR Donation" , wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def onDonateBTC(self, event):
        btc_address = "1PS2WmKorxCeFoNZbZ5XKgbiDjofxFgcPL"
        self.writeClipboard(btc_address)
        dlg = wx.MessageDialog(self, "BTC address " + btc_address + " copied to clipboard.\n\nThanks for your support.", "BTC Donation", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def writeClipboard(self, address):
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(address)
        r.destroy()

    def onExit(self, event):
        self.Iconize(True)
        self.panelConsole.stop(kill_miners=True, wait=True)
        self.Close(True)
        event.Skip()

    def onOpen(self, event):
        activeFile = self.notebook.openConfig()
        if activeFile:
            self.setTitle(activeFile)
            self.enabled_buttons(False)

    def onSave(self, event):
        #if self.notebook.saveConfig(self.activeFile, {"mainMode" : self.getMainMode()}):
        if self.notebook.saveConfig({"mainMode" : self.getMainMode()}):
            self.panelConsole.configChanged()
            self.enabled_buttons(False)
            #else:
            #    self.onButtonCancel(None)

    def onSaveAs(self, event):
        activeFile = self.notebook.saveConfigAs({"mainMode" : self.getMainMode()})
        if activeFile:
            self.setTitle(activeFile)
            self.enabled_buttons(False)

    def onButtonCancel(self, event):
        self.notebook.loadConfig()
        self.enabled_buttons(False)
        self.notebook.broadcastEventToAllTabs(event_id="main_config",
                                              event_value=("advanced" == self.notebook.getStoredConfigParam("mainMode")))

    def onButtonDefaults(self, event):
        self.notebook.loadDefaults()
        self.enabled_buttons(True)
        self.notebook.broadcastEventToAllTabs(event_id="main_config",
                                              event_value=("advanced" == self.notebook.getStoredConfigParam("mainMode")))

    def onMainModeToggle(self, event):
        self.enabled_buttons(True)

        if self.buttonMainMode.GetValue():
            self.showSimple()
        else:
            self.showAdvanced()

        self.notebook.broadcastEventToAllTabs(event_id="main_config",
                                              event_value=("advanced" == self.getMainMode()))

    def onButtonRun(self, event):
        result = True

        if self.isThereAPreviousSession():
            question = "This will delete your previously stored session data. Are you sure you want to continue?"
            dlg = wx.MessageDialog(self, question, "Warning", wx.YES_NO | wx.ICON_WARNING)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

        if result:
            if self.notebook.saveConfig({"mainMode" : self.getMainMode()}):
                self.enabled_buttons(False)
                self.panelConsole.mine(self.notebook.activeFile)

    def onButtonResume(self, event):
        if self.notebook.saveConfig({"mainMode" : self.getMainMode()}):
            self.enabled_buttons(False)
            self.panelConsole.mine(self.notebook.activeFile, resume=True)

    def onButtonStop(self, event):
        #self.buttonStop.SetLabelText("Stopping   ")
        self.panelConsole.stop(kill_miners=False, wait=False)
        self.stopMiners(runStopButtonEffect=True)
        #self.buttonRun.Enable(True)
        #self.buttonStop.Enable(False)

    #def signalStop(self):
    #    StopLabelSingletonThread(self, self.miners).start()

    def isThereAPreviousSession(self):
        return os.path.isfile(SwitcherData.DATA_FILE_NAME)

    def getMainMode(self):
        return "simple" if self.buttonMainMode.GetValue() else "advanced"

    def setMainMode(self, mainMode):
        if not mainMode or mainMode == "simple":
            self.buttonMainMode.SetValue(True)
            self.showSimple()
        else:
            self.buttonMainMode.SetValue(False)
            self.showAdvanced()

    def showSimple(self):
        self.buttonMainMode.SetLabel("Simple")
        self.resizable_panel.SplitHorizontally(self.panelConsole, self.miners, self.resizable_panel.GetSize()[1] * self.getGravity())
        #self.shell.rearrangeMiners(self.shell.GetSize()[0])
        #self.resizable_panel.Unsplit(self.advancedConfig)

    def showAdvanced(self):
        self.buttonMainMode.SetLabel("Advanced")
        self.getGravity()
        self.resizable_panel.SplitHorizontally(self.panelConsole, self.miners)
        self.resizable_panel.Unsplit(self.miners)

    def getGravity(self):
        if not self.gravity:
            self.gravity = GRAVITY
        else:
            if self.getMainMode() == "advanced":
                resizable_panel_width = self.resizable_panel.GetSize()[1]

                if resizable_panel_width == 0:
                    self.gravity = GRAVITY
                else:
                    self.gravity = float(self.panelConsole.GetSize()[1]) / resizable_panel_width

        return self.gravity

    def onMiningProcessStarted(self):
        self.mining = True
        self.buttonRun.Enable(False)
        self.buttonResume.Enable(False)
        self.buttonMainMode.Enable(False)
        self.buttonStop.Enable(True)

    def onMiningProcessStopped(self):
        self.mining = False

    def miningStoppedButtons(self):
        self.buttonRun.Enable(True)
        self.buttonResume.Enable(True)
        self.buttonMainMode.Enable(True)
        self.buttonStop.Enable(False)
        #self.buttonStop.Show(True)
        #self.buttonStop.SetLabelText("Stop")
        #self.buttonStop.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/stop16.ico'), wx.LEFT)

        self.Layout()

    def executeAlgo(self, maxAlgo, switch):
        return self.miners.executeAlgo(maxAlgo, switch)

    def checkMinerCrashed(self):
        return self.miners.checkMinerCrashed()

    def stopMiners(self, runStopButtonEffect, forcibly=False, wait=False):
        if runStopButtonEffect:
            StopLabelSingletonThread(self, self.miners).start()

        return self.miners.stopMiners(forcibly, wait)

    def onClose(self, event):
        self.Iconize(True)
        self.mining = False

        threadMiners = threading.Thread(target=self.stopMiners, kwargs={'runStopButtonEffect' : False, 'forcibly' : False, 'wait' : True })
        threadConsole = threading.Thread(target=self.panelConsole.stop, kwargs={'kill_miners' : False, 'wait' : True })
        threadProgressBar = threading.Thread(target=self.progressBar)

        self.finished = False
        self.pulse_dlg = wx.ProgressDialog(parent = self,
                                           title="Myriad Switcher is shutting down...",
                                           message="Please wait while all threads finish...",
                                           maximum=100
                                          )
        threadProgressBar.start()

        threadMiners.start()
        threadConsole.start()

        #threadProgressBar.join()
        threadMiners.join()
        threadConsole.join()

        self.finished = True

        event.Skip()

    def progressBar(self):
        #from wx._core import PyDeadObjectError
        #import traceback

        try:
            for i in range(0, 6000, 1):
                if self.finished:
                    break

                wx.MilliSleep(50)
                self.pulse_dlg.Update(i % 100)

        except Exception as ex:
            pass
            #print traceback.format_exc()


class StopLabelSingletonThread (threading.Thread):
    _instance = None
    lock = threading.RLock()

    MAX_WAIT_ITER = 40

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(StopLabelSingletonThread, self).__new__(self, *args, **kwargs)
        return self._instance

    def __init__(self, frame, miners):
        self.frame  = frame
        self.miners = miners

        threading.Thread.__init__ (self)

    def run(self):
        with StopLabelSingletonThread.lock:
            count = 0

            previousBtn = self.frame.buttonStop
            currentBtn = None

            mining = self.frame.mining
            minersready = self.miners.checkMinersReady()

            buttonsWait = [self.frame.buttonWait1, self.frame.buttonWait2, self.frame.buttonWait3, self.frame.buttonWait4]

            while ( mining or not minersready ) and count < self.MAX_WAIT_ITER:
                mod = count % 4

                if mod < 4:
                    currentBtn = buttonsWait[mod]

                    currentBtn.Show()
                    previousBtn.Hide()
                    self.frame.Layout()

                    previousBtn = currentBtn

                mining = self.frame.mining
                minersready = self.miners.checkMinersReady()

                time.sleep(0.5)

                count += 1

            if currentBtn:
                currentBtn.Hide()

            self.frame.buttonStop.Show()

            self.frame.Layout()
            self.frame.miningStoppedButtons()

