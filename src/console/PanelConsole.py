import psutil

__author__ = 'Dario'

import time

import wx
import os
import wx.html2 as webview
import FrameMYR
import threading
import  wx.lib.scrolledpanel as scrolled
from event.Event import Event
from os import listdir
from os.path import isfile, join
import wx.dataview as dv
from ObjectListView import ObjectListView, ColumnDefn
from console.switcher.SwitchingThread import SwitchingThread
from event.EventLib import ConsoleEvent, EVT_CONSOLE_EVENT

INDEX_CONSOLE = 0
INDEX_BROWSER = 1
INDEX_LOGS    = 2


class PanelConsole(wx.Panel):
    def __init__(self, parent, frame_myr, size=None, style=wx.BORDER_DEFAULT):
        wx.Panel.__init__(self, parent=parent, size=size, id=wx.ID_ANY, style=style)

        self.parent = parent
        self.frame_myr = frame_myr

        self.thread = None
        self.threadCount = 0
        self.messageEvent = None

        self.notebook = wx.Notebook(self, id=wx.ID_ANY, style=wx.BK_RIGHT | wx.TE_NO_VSCROLL)

        self.il = wx.ImageList(16, 16)
        self.notebook.AssignImageList(self.il)

        panelConsole = wx.Panel(self.notebook)
        self.wvConsole = webview.WebView.New(panelConsole)
        self.wvBrowser = webview.WebView.New(self.notebook)
        self.logs = PanelLogs(self.notebook, frame_myr)

        sizerC = wx.BoxSizer(wx.VERTICAL)
        sizerC.Add(self.wvConsole, 1, wx.EXPAND | wx.ALL, -3)
        panelConsole.SetSizer(sizerC)

        self.notebook.AddPage(panelConsole, "Output  ")
        self.notebook.AddPage(self.wvBrowser, "Browser ")
        self.notebook.AddPage(self.logs, " Logs ")
        self.notebook.SetPageImage(INDEX_CONSOLE, self.il.Add(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/console16.ico', wx.BITMAP_TYPE_ICO)))
        self.notebook.SetPageImage(INDEX_BROWSER, self.il.Add(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/browser2.ico', wx.BITMAP_TYPE_ICO)))
        self.notebook.SetPageImage(INDEX_LOGS, self.il.Add(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/logs16.ico', wx.BITMAP_TYPE_ICO)))

        self.notebook.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        sizer = wx.BoxSizer(wx.VERTICAL)
        #self.SetBackgroundColour("Black")

        self.wvConsole.SetPage('<html><body style="background-color: #000000;"></body></html>', "")
        self.wvBrowser.SetPage('<html><body style="background-color: #AAAAAA;"></body></html>', "")

        sizer.Add(self.notebook, 1, wx.EXPAND | wx.LEFT, -3)
        self.SetSizer(sizer)

        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
        self.Bind(wx.EVT_SIZE, self.onResize)

        self.Bind(EVT_CONSOLE_EVENT, self.onConsole)
        #EVT_CONSOLE_EVENT(self, self.onConsole)

    def addMessageEventListener(self, eventListener):
        messageEvent = Event(eventListener)

        if not self.messageEvent:
            self.messageEvent = messageEvent
        else:
            self.messageEvent += messageEvent

    def fireMessageEvent(self, output_text):
        if self.messageEvent:
            self.messageEvent(output_text)

    def getMiningAlgo(self):
        try:
            return self.thread.switcherData.getMiningAlgo()

        except Exception:
            return None

    def onResize(self, event):
        self.Layout()
        event.Skip()

    def onPageChanged(self, event):
        if event.Selection == INDEX_LOGS:
            self.logs.loadList()

        elif event.Selection == INDEX_BROWSER:
            self.wvBrowser.Reload()

        self.Layout()

        event.Skip()

    def onConsole(self, event):
        #print "console     " + str(time.time()) + "   -   " + event.html
        #self.wv.SetPage(str(time.time()), "")
        self.wvConsole.SetPage(event.html, "")
        self.wvConsole.Reload()
        #self.wv.Find(HTMLBuilder.ANCHOR)
        #self.Scroll(0, self.GetScrollRange(wx.VERTICAL))
        #self.parent.Scroll(0, self.parent.GetScrollRange(wx.VERTICAL))
        #self.SetScrollbars(0, 1111, 1111, 11)
        #print "Console says = " + event.html
        #self.wv.SetPage("<html><header><title>This is title</title></header><body>Hello world</body></html>", "")
        #self.wv.LoadURL("https://dl.dropboxusercontent.com/u/19353176/Myriad_log/2014-05-04-040554.html")

    def onBrowse(self, url, title):
        self.notebook.SetSelection(INDEX_BROWSER)
        #self.notebook.GetPage(1).Show()
        #self.wvBrowser.SetPage(html, "")
        self.notebook.SetPageText(INDEX_BROWSER, title)

        print "BROWSING " + title + " - url = " + url

        self.wvBrowser.LoadURL(url)
        #self.wvBrowser.Reload()

    def onLog(self, url, title):
        self.notebook.SetSelection(INDEX_LOGS)
        self.logs.onLog(url)

    def reloadLog(self):
        if self.notebook.GetSelection() == INDEX_LOGS:
            self.logs.reloadLog()

        if self.notebook.GetSelection() == INDEX_BROWSER:
            self.wvBrowser.Reload()

    def onMiningProcessStarted(self):
        self.frame_myr.onMiningProcessStarted()

    def onMiningProcessStopped(self):
        self.frame_myr.onMiningProcessStopped()

    def getThread(self, rebooting, resume):
        self.threadCount += 1
        return SwitchingThread("SwitchThread", self.threadCount, self, rebooting, resume)

    def mine(self, activeConfigFile, rebooting=False, resume=False):
        self.wvConsole.Show(True)
        self.Layout()

        self.notebook.SetSelection(INDEX_CONSOLE)

        if self.thread:
            self.thread.stop(True)

        self.thread = self.getThread(rebooting, resume)

        self.thread.setActiveConfigFile(activeConfigFile)
        self.thread.start()

    def configChanged(self):
        if self.thread:
            self.thread.configChanged()

    def stop(self, kill_miners=True, wait=True):
        if self.thread:
            self.thread.stop(kill_miners)
        else:
            return

        if wait:
            success = False
            i = 0
            str_ini = "Waiting for threads to die "
            print str_ini

            from miner import PanelMinerInstance

            while i < PanelMinerInstance.MAX_ITERATIONS:
                if self.thread.isAlive():
                    time.sleep(0.5)
                    i += 1
                    str_out = str_ini + str(i)
                    print str_out

                else:
                    str_out = "THREADS done, Bye!"
                    print str_out
                    #time.sleep(2)
                    success = True
                    break

            print "Threads: Exited with success = " + str(success)

            if not success:
                str_out = "THREADS Dammit"
                print str_out
                time.sleep(5)


    def printToConsole(self, str_out):
        print str_out
        evt = ConsoleEvent(thread_ident=self.thread.ident, html=str_out)
        wx.PostEvent(self, evt)


class PanelLogs(wx.Panel):
    lock = threading.RLock()

    def __init__(self, parentNotebook, frame_myr, size=None, style=wx.BORDER_DEFAULT):
        wx.Panel.__init__(self, parent=parentNotebook, size=size, id=wx.ID_ANY, style=style)
        self.parentNotebook = parentNotebook
        self.frame_myr = frame_myr

        self.logPath = frame_myr.notebook.getTempConfigParam("logPath")

        self.wvLogs = webview.WebView.New(self)
        self.selection = None


        #scrollPanel = wx.Panel(self)
        self.listLogs = ObjectListView(self, size=(108, -1), style=wx.LC_REPORT, sortable=False)
        self.listLogs.oddRowsBackColor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

        self.listLogs.SetColumns([
            ColumnDefn("Log File", "center", 94, "log")
        ])

        self.listLogs.SetFont(wx.Font(8.5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))

        self.loadList()

        self.listLogs.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onLogSelected)
        self.listLogs.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
        self.wvLogs.Bind(webview.EVT_WEBVIEW_TITLE_CHANGED, self.onFocusLost)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.wvLogs.SetPage('<html><body style="background-color: #111111;"></body></html>', "")

        sizer.Add(self.wvLogs, 1, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.TOP, -3)
        sizer.Add(self.listLogs, 0, wx.EXPAND | wx.LEFT, 0)

        self.SetSizer(sizer)

    def onFocusLost(self, event):
        self.listLogs.SetFocus()
        event.Skip()

    def loadList(self):
        with self.lock:
            if not self.logPath:
                return

            logFiles = [ {"log": os.path.splitext(f)[0] } for f in reversed(listdir(self.logPath)) if isfile(join(self.logPath, f)) and f.endswith('.html') ]

            self.listLogs.DeleteAllItems()

            self.listLogs.SetObjects(logFiles)

            if self.selection is not None:
                try:
                    self.listLogs.SelectObjects([self.selection])

                except IndexError:
                    self.selection = None

                self.listLogs.SetFocus()

    def onLogSelected(self, event):
        self.selection = self.listLogs.GetObjects()[event.GetEventObject().GetFirstSelected()]
        self.onLogSelectedIndex(self.selection)

        self.listLogs.SetFocus()

        event.Skip()

    def onLogSelectedIndex(self, selectedObj):
        #logFile = event.GetEventObject().GetValue(self.selection, 0)
        #logFile = self.listLogs.GetValue(index, 0)
        logFile = selectedObj['log']
        self.loadLogFile(logFile)

    def loadLogFile(self, logFile):
        f = open(self.logPath + "/" + logFile + ".html")
        html = f.read()
        f.close()
        self.onLog(html)

    def onLog(self, html):
        self.wvLogs.SetPage(html, "")
        self.wvLogs.Reload()

    def reloadLog(self):
        #self.wvLogs.Reload()
        if self.selection:
            self.loadLogFile(self.selection['log'])

    def OnRightClick(self, event):
        #self.log.WriteText("OnRightClick %s\n" % self.list.GetItemText(self.currentItem))

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupOpenLocation = wx.NewId()
            self.popupDelete = wx.NewId()

            self.Bind(wx.EVT_MENU, self.onPopUpOpenLocation, id=self.popupOpenLocation)
            self.Bind(wx.EVT_MENU, self.onPopUpDelete, id=self.popupDelete)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupOpenLocation, "Open file location")
        menu.Append(self.popupDelete, "Delete files...")

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def onPopUpOpenLocation(self, event):
        if os.name == "nt":
            #os.spawnl(os.P_NOWAIT, os.getenv('windir') + '\\explorer.exe', '.', '/n,/e,/select,"%s"'%self.logPath+"\\")
            psutil.Popen('explorer ' + '"' + self.logPath + '"')

        if os.name == "posix":
            pass

    def onPopUpDelete(self, event):
        question = "Are you sure you want to delete those files?"
        dlg = wx.MessageDialog(self, question, "Confirm deletion", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()

        if result:
            selected = self.listLogs.GetSelectedObjects()
            for file in selected:
                os.remove(self.logPath + '/' + file['log'] + '.html')

            self.loadList()
