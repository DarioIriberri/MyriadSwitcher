__author__ = 'Dario'

import wx
import os
import time
import threading
import psutil
from wizard import MyriadSwitcherWizard as msw
from wx.lib.buttons import *
from Tkinter import Tk
from console.PanelConsole import PanelConsole
from console.switcher import SwitcherData
from miner.PanelMiners import PanelMiners
from wx._core import PyDeadObjectError
from notebook.ExpandableNotebook import ExpandableNotebook
from notebook.tabs.ConfigTab import ConfigTab
from notebook.tabs.SwitchingModesTab import SwitchingModesTab
from notebook.tabs.MiscellaneousTab import MiscellaneousTab
from event.EventLib import EVT_STATUS_BAR_EVENT, EVT_DUMMY_EVENT, DummyEvent


VERSION  = "0.3"
REVISION = 0

GRAVITY = 0.7

BUTTON_SIZE  = (76, 26)
SPLITTER_ID = 32612

class FrameMYRClass(wx.Frame):
    RESOURCE_PATH = None

    def __init__(self, resouce_path=""):
        FrameMYRClass.RESOURCE_PATH = resouce_path

        self.gravity = None
        self.resizable_panel_sash = None
        self.mining  = False

        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Myriad Switcher Configurator... ",
                          size=(800, 383)
        )

        self.onWizard(forceRun=False)

        self.prev_size = self.GetSize()
        self.isNotebookSimple = True
        self.terminating = False

        #self.setTitle(self.activeFile)
        #self.Bind(wx.EVT_SIZE, self.OnResize)

        self.status_bar = self.CreateStatusBar()

        self.buttonSave = wx.Button(self, wx.ID_SAVE, "Save  ", size=BUTTON_SIZE, style=wx.BU_EXACTFIT)
        self.buttonCancel = wx.Button(self, wx.ID_CANCEL, "Cancel", size=BUTTON_SIZE)
        self.buttonRun = wx.Button(self, -1, "Start  ", size=BUTTON_SIZE)
        self.buttonResume = wx.Button(self, -1, "Resume", size=BUTTON_SIZE)
        self.buttonStop = wx.Button(self, wx.ID_STOP, "Stop  ", size=BUTTON_SIZE)
        self.buttonWallet = wx.Button(self, wx.ID_ANY, "Wallet", size=BUTTON_SIZE)
        self.buttonQuit = wx.Button(self, wx.ID_EXIT, "Quit  ", size=BUTTON_SIZE)
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
        self.buttonQuit.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/exit-16.ico'), wx.LEFT)
        self.buttonWallet.SetBitmap(wx.Bitmap(FrameMYRClass.RESOURCE_PATH   + 'img/electrum16.ico'), wx.LEFT)

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
        menuWizard = helpmenu.Append(wx.ID_ANY, "Run the &wizard"," Run the wizard")
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
        self.Bind(wx.EVT_MENU, self.onWizard, menuWizard)
        self.Bind(wx.EVT_MENU, self.onDonateMYR, menuDonateMYR)
        self.Bind(wx.EVT_MENU, self.onDonateBTC, menuDonateBTC)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onButtonRun, self.buttonRun)
        self.Bind(wx.EVT_BUTTON, self.onButtonResume, self.buttonResume)
        self.buttonStop.Bind(wx.EVT_BUTTON, self.onButtonStop)
        self.Bind(wx.EVT_BUTTON, self.onButtonCancel, self.buttonCancel)
        self.Bind(wx.EVT_BUTTON, self.onButtonDefaults, self.buttonDefaults)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.buttonSave)
        self.Bind(wx.EVT_BUTTON, self.onQuit, self.buttonQuit)
        self.Bind(wx.EVT_BUTTON, self.onWallet, self.buttonWallet)

        #self.buttonWait1.Bind(wx.EVT_BUTTON, self.onButtonWait)
        #self.buttonWait2.Bind(wx.EVT_BUTTON, self.onButtonWait)
        #self.buttonWait3.Bind(wx.EVT_BUTTON, self.onButtonWait)
        #self.buttonWait4.Bind(wx.EVT_BUTTON, self.onButtonWait)

        #self.buttonSave.SetBitmapMargins(14, 0)
        #self.buttonCancel.SetBitmapMargins((14, 0))

        # Creating the menubar.
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(donationsmenu,"&Donations") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

        self.resizable_panel = wx.SplitterWindow(self, SPLITTER_ID)
        self.resizable_panel.SetMinimumPaneSize(1)
        self.resizable_panel.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onSplitterResized)
        #self.resizable_panel.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, lambda event : None)
        self.resizable_panel.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self.toggleSplitter)

        # Create the Notebook
        self.panelNotebook = wx.Panel(self)

        self.notebook = ExpandableNotebook(self.panelNotebook, self)
        self.notebook.addTab(ConfigTab, "Main Config", FrameMYRClass.RESOURCE_PATH + 'img/aquachecked.ico')
        self.notebook.addTab(SwitchingModesTab, "Switching Modes", FrameMYRClass.RESOURCE_PATH + 'img/switching16.ico')
        self.notebook.addTab(MiscellaneousTab, "Miscellaneous", FrameMYRClass.RESOURCE_PATH + 'img/advanced.ico')
        #self.notebook.addTab(MiscellaneousTab, "Miscellaneous2", FrameMYRClass.RESOURCE_PATH + 'img/advanced.ico')
        self.notebook.buildNotebook()

        self.panelConsole = PanelConsole(self.resizable_panel, self)
        self.panelConsole.addMessageEventListener(self.set_status_text)
        #self.panelConsole = webview.WebView.New(PanelConsole.PanelConsole)
        self.panelConsole.SetBackgroundColour("Black")

        self.miners = PanelMiners(parent=self.resizable_panel, frame=self)

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
        button_bottom_gap = 2
        flagsButtonRun = wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap).Proportion(0)
        sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        sizerButtonsWrapper = wx.BoxSizer(wx.HORIZONTAL)
        sizerButtons.AddF(self.buttonSave, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonCancel, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(5, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonDefaults, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.Add(wx.StaticLine(self, -1, size=(-1, 20), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.BOTTOM, 3)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonWallet, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.Add(wx.StaticLine(self, -1, size=(-1, 20), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.BOTTOM, 3)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.AddF(self.buttonMainMode, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, button_bottom_gap))
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        #sizerButtons.Add(wx.StaticLine(self, -1, size=(-1, 20), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.BOTTOM, 3)

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
        #sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        #sizerButtons.Add(wx.StaticLine(self, -1, size=(-1, 20), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.BOTTOM, 3)
        #sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        #sizerButtons.Add(self.buttonWallet, 0, wx.RIGHT, 4)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.Add(wx.StaticLine(self, -1, size=(-1, 20), style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.BOTTOM, 3)
        sizerButtons.Add(wx.StaticText(self, wx.ID_ANY, size=(15, -1)), 0, wx.EXPAND | wx.TOP, 0)
        sizerButtons.Add(self.buttonQuit, 0, wx.RIGHT, 4)
        sizerButtonsWrapper.Add(sizerButtons, 1, wx.EXPAND | wx.RIGHT | wx.LEFT, 1)

        self.sizerTotal.Add(self.panelNotebook, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)
        self.sizerTotal.Add(sizerButtonsWrapper, 0, wx.EXPAND | wx.RIGHT | wx.LEFT | wx.TOP, 1)

        self.resizable_panel.SetSashGravity(GRAVITY)
        #self.resizable_panel.SplitHorizontally(self.panelConsole, self.shell)
        self.sizerTotal.Add(self.resizable_panel, 5, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 2)

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

        self.miners.resizeMinerPanels()

        self.Show()

        self.buttonWait1.Hide()
        self.buttonWait2.Hide()
        self.buttonWait3.Hide()
        self.buttonWait4.Hide()

        self.chechReboot()

        self.stopEffectThread = None

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

            self.panelConsole.onBrowse('https://dl.dropboxusercontent.com/u/19353176/Myriad%20Switcher/README/README.html', 'User Guide')
            #self.panelConsole.setBrowser('http://wxpython.org/')

        except:
            print "Failed to open readme file"

    def onWizard(self, event=None, forceRun=True):
        wizard = msw.MyriadSwitcherWizard(self)
        if forceRun or not wizard.checkElectrumWalletExists():
            wizard.startWizard()

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

    def onWallet(self, event):
        psutil.Popen(FrameMYRClass.RESOURCE_PATH + "/electrum/Electrum-MyrWallet.exe", shell=False)

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

        if not self.checkMinersSelected():
            return

        if self.isThereAPreviousSession():
            question = "This will delete your previously stored session data. Are you sure you want to continue?"
            dlg = wx.MessageDialog(self, question, "Warning", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

        if result:
            if self.notebook.saveConfig({"mainMode" : self.getMainMode()}):
                self.enabled_buttons(False)
                self.panelConsole.mine(self.notebook.activeFile)

    def onButtonResume(self, event):
        if not self.checkMinersSelected():
            return

        if self.notebook.saveConfig({"mainMode" : self.getMainMode()}):
            self.enabled_buttons(False)
            self.panelConsole.mine(self.notebook.activeFile, resume=True)

    def checkMinersSelected(self):
        if not self.miners.checkMinersSelected():
            dlg = wx.MessageDialog(self,
                                   "Pick at least one mining device in the lower panel to start your mining session.\n\n ",
                                   "Unable to start the mining session..." , wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

            return False

        return True

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

    def collapseMinersSplitter(self, event=None):
        #self.getGravity()
        top = self.miners.miner0.handler.GetSize()[1] + 5
        self.resizable_panel.SetSashPosition(self.resizable_panel.GetSize()[1] - top)

    def expandMinersSplitter(self):
        self.resizable_panel.SetSashPosition(self.resizable_panel_sash)
        self.Layout()

    def toggleSplitter(self, event=None):
        if self.miners.getExpansionStatus():
            self.collapseMinersSplitter()
            self.miners.setButtonExpanded(False)
        else:
            self.expandMinersSplitter()
            self.miners.setButtonExpanded(True)

    def onSplitterResized(self, event):
        try:
            if not SPLITTER_ID == event.GetEventObject().GetId():
                event.Skip()
                return

            top = self.miners.miner0.handler.GetSize()[1] + 5
            current = self.resizable_panel.GetSize()[1] - self.resizable_panel.GetSashPosition()
            #current = self.resizable_panel.GetSashPosition()

            if current > top:
                self.resizable_panel_sash = self.resizable_panel.GetSashPosition()
                self.miners.setButtonExpanded(True)
            else:
                self.miners.setButtonExpanded(False)
                lim = self.resizable_panel.GetSize()[1] - top
                self.resizable_panel.SetSashPosition(lim)

        except AttributeError:
            pass

        event.Skip()

    def getGravity(self):
        if not self.gravity:
            self.gravity = GRAVITY
        else:
            if self.getMainMode() == "advanced":
                resizable_panel_height = self.resizable_panel.GetSize()[1]

                if resizable_panel_height == 0:
                    self.gravity = GRAVITY
                else:
                    self.gravity = float(self.panelConsole.GetSize()[1]) / resizable_panel_height

        return self.gravity

    def onBrowse(self, url, title):
        self.panelConsole.onBrowse(url, title)

    def onMiningProcessStarted(self):
        self.mining = True
        self.buttonRun.Enable(False)
        self.buttonResume.Enable(False)
        self.buttonMainMode.Enable(False)
        self.buttonStop.Enable(True)

    def onMiningProcessStopped(self):
        if not self.terminating:
            self.mining = False
            self.miningStoppedButtons()

        self.notebook.broadcastEventToAllTabs(event_id="stop_mining")

    def miningStoppedButtons(self):
        try:
            self.buttonRun.Enable(True)
            self.buttonResume.Enable(True)
            self.buttonMainMode.Enable(True)
            self.buttonStop.Enable(False)

            self.Layout()

        except PyDeadObjectError:
            pass

    def executeAlgo(self, maxAlgo, switch):
        ret = self.miners.executeAlgo(maxAlgo, switch)

        if ret :
            self.notebook.broadcastEventToAllTabs(event_id="start_mining", event_value=maxAlgo)

        return ret

    def checkMinerCrashed(self):
        return self.miners.checkMinerCrashed()

    def stopMiners(self, runStopButtonEffect=False, wait=False, exit=False):
        if runStopButtonEffect:
            self.stopEffectThread = threading.Thread(target=self.stopLabelSingletonThread)
            self.stopEffectThread.start()
            #StopLabelSingletonThread(self, self.miners).start()

        ret = self.miners.stopMiners(wait, exit)

        return ret

    def getMiningAlgo(self):
        return self.panelConsole.getMiningAlgo()

    def onQuit(self, event):
        self.Close(True)
        event.Skip()

    def onExit(self, event):
        self.Close(True)
        event.Skip()

    def onClose(self, event):
        if self.stopEffectThread and self.stopEffectThread.isAlive():
            return

        self.terminate()
        event.Skip()

    def terminate(self):
        #self.Iconize(True)
        #self.mining = False
        self.terminating = True

        self.waitForStopThread()

        threadMiners = threading.Thread(target=self.stopMiners, kwargs={'runStopButtonEffect' : False, 'wait' : True, 'exit' : True })
        threadConsole = threading.Thread(target=self.panelConsole.stop, kwargs={'kill_miners' : False, 'wait' : True })

        self.finished = False

        threadMiners.start()
        threadConsole.start()

        if self.mining:
            self.progressBar = wx.ProgressDialog(parent = self,
                                                 title="Myriad Switcher is shutting down...",
                                                 message="Please wait while all threads finish...",
                                                 maximum=100
                                                )
            threadProgressBar = threading.Thread(target=self.progressBarThread)
            threadProgressBar.start()


        #threadProgressBar.join()
        threadMiners.join()
        threadConsole.join()
        #if self.stopEffectThread and self.stopEffectThread.isAlive():
        #    self.stopEffectThread.join()

        self.finished = True

        print "See ya!!"

        #time.sleep(10)

    #def finalSleep(self):
    #    time.sleep(10)

    def waitForStopThread(self):
        MAX_WAIT_ITER = 120
        count = 0
        waitOnStop = self.stopEffectThread and self.stopEffectThread.isAlive()

        while waitOnStop and count < MAX_WAIT_ITER:
            time.sleep(1)
            count += 1
            self.stopEffectThread._reset_internal_locks()
            waitOnStop = self.stopEffectThread and self.stopEffectThread.isAlive()

    def progressBarThread(self):
        try:
            for i in range(0, 6000, 1):
                if self.finished:
                    break

                wx.MilliSleep(50)
                self.progressBar.Update(i % 100)

        except Exception as ex:
            pass

    def stopLabelSingletonThread(self):
        try:
            MAX_WAIT_ITER = 60

            count = 0

            wx.CallAfter(self.buttonQuit.Disable)

            previousBtn = self.buttonStop
            currentBtn = None

            mining = self.mining
            minersready = self.miners.checkMinersReady()

            if self.terminating:
                return

            buttonsWait = [self.buttonWait1, self.buttonWait2, self.buttonWait3, self.buttonWait4]

            while ( mining or not minersready ) and not self.terminating and count < MAX_WAIT_ITER:
                mod = count % 4

                if mod < 4:
                    if self.terminating:
                        return

                    currentBtn = buttonsWait[mod]

                    wx.CallAfter(currentBtn.Enable)
                    wx.CallAfter(currentBtn.Show)
                    wx.CallAfter(previousBtn.Hide)
                    wx.CallAfter(previousBtn.Disable)
                    self.Layout()

                    previousBtn = currentBtn

                mining = self.mining
                minersready = self.miners.checkMinersReady()

                time.sleep(0.5)

                count += 1

            if self.terminating:
                return

            if currentBtn:
                wx.CallAfter(currentBtn.Hide)

            wx.CallAfter(self.buttonStop.Show)
            wx.CallAfter(self.buttonQuit.Enable)

            wx.CallAfter(self.Layout)
            wx.CallAfter(self.miningStoppedButtons)

        except PyDeadObjectError:
            pass