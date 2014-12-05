__author__ = 'Dario'

from notebook import NotebookMYR
from switcher import SwitcherData
import wx
import os
import time
import threading
from wx.lib.agw.ribbon.page import GetSizeInOrientation
import wx.lib.newevent
import PanelConsole
from Tkinter import Tk


VERSION  = "0.2"
REVISION = 29


class FrameMYR(wx.Frame):
    def __init__(self, resouce_path):
        self.resouce_path = resouce_path

        f = open('activeConfig')
        lines = f.readlines()
        f.close()

        if (lines and len(lines) > 0):
            self.activeFile = lines[0]
        else:
            self.activeFile = "myriadSwitcher.conf"

        self.workingDir = os.getcwd()

        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Myriad Switcher Configurator... " + self.activeFile,
                          size=(668, 390)
        )

        self.prev_size = self.GetSize()
        self.isNotebookSimple = True

        self.setTitle(self.activeFile)
        #self.Bind(wx.EVT_SIZE, self.OnResize)

        self.status_bar = self.CreateStatusBar()

        self.buttonSave = wx.Button(self, -1, "Save")
        self.buttonCancel = wx.Button(self, -1, "Cancel")
        self.buttonRun = wx.Button(self, -1, "Run")
        self.buttonResume = wx.Button(self, -1, "Resume")
        self.buttonStop = wx.Button(self, -1, "Stop")
        buttonReset = wx.Button(self, -1, "Defaults")

        # Setting up the menu.
        filemenu= wx.Menu()
        donationsmenu= wx.Menu()
        helpmenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuSave = filemenu.Append(wx.ID_SAVE, "&Save"," Save configuration")
        menuSaveAs = filemenu.Append(wx.ID_SAVEAS, "&Save as..."," Save configuration as...")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuRTFM = helpmenu.Append(wx.ID_ANY, "&Open the User Guide"," Open the user guide")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuDonateMYR = donationsmenu.Append(wx.ID_ANY, "&Donate Myriadcoins (MYR)"," Copies MYR address to clipboard to donate Myriadcoins")
        menuDonateBTC = donationsmenu.Append(wx.ID_ANY, "&Donate Bitcoins (BTC)"," Copies MYR address to clipboard to donate Bitcoins")

        # Events.
        self.Bind(wx.EVT_MENU, self.onOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.onSave, menuSave)
        self.Bind(wx.EVT_MENU, self.onSaveAs, menuSaveAs)
        self.Bind(wx.EVT_MENU, self.onExit, menuExit)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_MENU, self.onAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.onRTFM, menuRTFM)
        self.Bind(wx.EVT_MENU, self.onDonateMYR, menuDonateMYR)
        self.Bind(wx.EVT_MENU, self.onDonateBTC, menuDonateBTC)

        # Creating the menubar.
        menuBar = wx.MenuBar()
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(donationsmenu,"&Donations") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

        # Create the Notebook
        self.panelNotebook = wx.Panel(self)
        #self.panelNotebook.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWFRAME))
        #self.panelNotebook.SetBackgroundColour("White")
        #self.panelNotebook.SetTransparent(255)
        #self.panelConsole = wx.Panel(self)
        self.panelConsole = PanelConsole.PanelConsole(self, size=(1500, -1))
        #self.panelConsole = webview.WebView.New(PanelConsole.PanelConsole)
        self.panelConsole.SetBackgroundColour("Black")

        #self.SetTransparent(210)

        self.sizerNotebookAll = wx.BoxSizer(wx.HORIZONTAL)
        self.notebook = NotebookMYR.NotebookMYR(self.panelNotebook, self, self.sizerNotebookAll, 4, expandable=True)
        self.notebook.loadConfig(self.activeFile)

        self.notebook.show_notebook()

        self.sizerTotal = wx.BoxSizer(wx.VERTICAL)

        # Buttons section
        flagsButtonRun = wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 6).Proportion(0)
        sizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        sizerButtons.AddF(self.buttonSave, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 6))
        sizerButtons.AddF(self.buttonCancel, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 6))
        sizerButtons.AddF(buttonReset, wx.SizerFlags().Expand().Border(wx.LEFT | wx.RIGHT | wx.BOTTOM, 6))
        self.Bind(wx.EVT_BUTTON, self.onButtonRun, self.buttonRun)
        self.Bind(wx.EVT_BUTTON, self.onButtonResume, self.buttonResume)
        self.Bind(wx.EVT_BUTTON, self.onButtonStop, self.buttonStop)
        self.Bind(wx.EVT_BUTTON, self.onButtonCancel, self.buttonCancel)
        self.Bind(wx.EVT_BUTTON, self.onButtonReset, buttonReset)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.buttonSave)
        spacerFlags = wx.SizerFlags().Expand().Border(wx.ALL, 1).Proportion(1)
        sizerButtons.AddF((-1, -1), spacerFlags)
        sizerButtons.AddF(self.buttonRun, flagsButtonRun)
        sizerButtons.AddF(self.buttonResume, flagsButtonRun)
        sizerButtons.AddF(self.buttonStop, flagsButtonRun)

        self.sizerTotal.Add(self.panelNotebook, 1, wx.ALL | wx.EXPAND)
        self.sizerTotal.Add(sizerButtons, 0, wx.EXPAND)
        self.sizerTotal.Add(self.panelConsole, 5, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 3)

        self.icon = wx.Icon(self.resouce_path + 'img/myriadS1.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetSizer(self.sizerTotal)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUBAR))

        self.Layout()
        self.Show()

        self.StatusBarEvent, EVT_STATUS_BAR_EVENT = wx.lib.newevent.NewEvent()
        EVT_STATUS_BAR_EVENT(self, self.on_mouse_over)

        self.Maximize()

        self.chechReboot()
        try:
            os.remove("reboot")
            os.remove(os.getenv('APPDATA') + '\\Microsoft\Windows\Start Menu\Programs\Startup\\myriadSwitcher.lnk')
        except:
            pass

        self.enabled_buttons(False)
        self.buttonStop.Enable(False)
        self.buttonResume.Enable(os.path.isfile(SwitcherData.DATA_FILE_NAME))

    def chechReboot(self):
        if os.path.isfile("reboot"):
            self.panelConsole.mine(self.activeFile, rebooting=True)

    # Required for NotebookMyr
    def notebookControlChanged(self):
        self.enabled_buttons(True)

    # Enables the Save & Cancel buttons
    def enabled_buttons(self, enabled):
        self.buttonCancel.Enable(enabled)
        self.buttonSave.Enable(enabled)

    # Changes the active config file
    def save_active_file(self, activeFile):
        f = open("activeConfig", "w")
        f.write(activeFile)
        f.close()

    @staticmethod
    def getVersion():
        return VERSION + "." + str(REVISION)

    # Sets the main window title
    def setTitle(self, activeFile):
        self.SetTitle("Myriad Switcher " + self.getVersion() + "... (" + activeFile + ")")

    def on_mouse_over(self, event):
        self.status_bar.SetStatusText(event.message)

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

        #dlg = AboutBox()
        #dlg.ShowModal()
        #dlg.Destroy()

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

    def onClose(self, event):
        self.Iconize(True)
        self.panelConsole.stop(kill_miners=False)
        event.Skip()

    def onOpen(self, event):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", self.workingDir, os.getcwd(), "*.conf", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            #f = open(os.path.join(dirname, filename), 'r')
            activeFile = filename
            #f.close()

            if self.notebook.loadConfig(dirname + "\\" + activeFile):
                self.setTitle(activeFile)
                self.activeFile = activeFile
                self.save_active_file(self.activeFile)
                self.enabled_buttons(False)

        dlg.Destroy()


    def onSave(self, event):
        if self.notebook.saveConfig(self.activeFile):
            self.panelConsole.configChanged()
            self.enabled_buttons(False)
        #else:
        #    self.onButtonCancel(None)

    def onSaveAs(self, event):
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=self.workingDir,
            defaultFile=self.activeFile, wildcard="*.conf", style=wx.SAVE | wx.OVERWRITE_PROMPT
            )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            #f = open(os.path.join(self.dirname, filename), 'r')
            activeFile = filename
            #f.close()

            if self.notebook.saveConfig(activeFile):
                self.activeFile = activeFile
                self.workingDir = dirname
                self.setTitle(activeFile)
                self.save_active_file(self.activeFile)
                self.enabled_buttons(False)

        dlg.Destroy()


    def onButtonCancel(self, event):
        self.notebook.loadConfig(self.activeFile)
        self.enabled_buttons(False)

    def onButtonReset(self, event):
        self.notebook.loadDefaults()
        self.enabled_buttons(True)

    def onButtonRun(self, event):
        question = "This will delete any previously stored session data. Are you sure you want to continue?"
        dlg = wx.MessageDialog(self, question, "Warning", wx.YES_NO | wx.ICON_WARNING)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()

        if result:
            if self.notebook.saveConfig(self.activeFile):
                self.enabled_buttons(False)

                self.panelConsole.mine(self.activeFile)

                #self.buttonRun.Enable(False)
                #self.buttonStop.Enable(True)

    def onButtonResume(self, event):
        if self.notebook.saveConfig(self.activeFile):
            self.enabled_buttons(False)

            self.panelConsole.mine(self.activeFile, resume=True)

            #self.buttonRun.Enable(False)
            #self.buttonStop.Enable(True)

    def onButtonStop(self, event):
        #self.buttonStop.SetLabelText("Stopping   ")
        self.panelConsole.stop(kill_miners=True, wait=False)
        StopLabelSingletonThread(self.buttonStop).start()
        #self.buttonRun.Enable(True)
        #self.buttonStop.Enable(False)

    def onMiningProcessStarted(self):
        self.buttonRun.Enable(False)
        self.buttonResume.Enable(False)
        self.buttonStop.Enable(True)

    def onMiningProcessStopped(self):
        self.buttonRun.Enable(True)
        self.buttonResume.Enable(True)
        self.buttonStop.Enable(False)
        self.buttonStop.SetLabelText("Stop")

class StopLabelSingletonThread (threading.Thread):
    _instance = None
    lock = threading.RLock()

    def __new__(self, *args, **kwargs):
        if not self._instance:
            self._instance = super(StopLabelSingletonThread, self).__new__(self, *args, **kwargs)
        return self._instance

    def __init__(self, buttonStop):
        self.buttonStop = buttonStop
        threading.Thread.__init__ (self)

    def run(self):
        with StopLabelSingletonThread.lock:
            count = 0
            while self.buttonStop.Enabled and count < 120:
                count += 1
                mod = count % 4
                self.buttonStop.SetLabelText("Wait" + (mod * ".") + ( ( 4 - mod ) * " ") )
                time.sleep(0.5)

#def __init__(self, coin):
#        wx.Dialog.__init__(self, None, -1, "%s Donation" %coin,
#            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
#                wx.TAB_TRAVERSAL)
#        #hwin = wx.html.HtmlWindow(self, -1, size=(400,200))
#        hwin = wx.html2.WebView.New(self, -1, size=(400, 200))
#        vers = {}
#        vers["python"] = sys.version.split()[0]
#        vers["wxpy"] = wx.VERSION_STRING
#        hwin.SetPage('<html><head><title>Myriad Switcher 0.1 User Guide</title></head>	<body><b><a href="bitcoin:1PS2WmKorxCeFoNZbZ5XKgbiDjofxFgcPL?amount=0.00100000">1PS2WmKorxCeFoNZbZ5XKgbiDjofxFgcPL</a></b></body></html>', '')
#        #hwin.SetPage('<html><head><title>Myriad Switcher 0.1 User Guide</title></head>	<body><b><a href="http://www.as.com">1PS2WmKorxCeFoNZbZ5XKgbiDjofxFgcPL</a></b></body></html>', "")
#        btn = hwin.FindWindowById(wx.ID_OK)
#        #irep = hwin.GetInternalRepresentation()
#        #hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
#        self.SetClientSize(hwin.GetSize())
#        self.CentreOnParent(wx.BOTH)
#        self.SetFocus()

#----------------------------------------------------------------------
