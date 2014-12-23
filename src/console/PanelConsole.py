__author__ = 'Dario'

import time

import wx
import os
import wx.html2 as webview
import FrameMYR
import threading
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

        self.Layout()

        event.Skip()

    def onConsole(self, event):
        #print "console     " + str(time.time()) + "   -   " + event.html
        #self.wv.SetPage(str(time.time()), "")
        self.wvConsole.SetPage(event.html, "")
        #self.wvConsole.Reload()
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
        self.wvBrowser.LoadURL(url)
        #self.wvBrowser.Reload()

    def onLog(self, url, title):
        self.notebook.SetSelection(INDEX_LOGS)
        self.logs.onLog(url)

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

        #self.listLogs = wx.ListBox(self, wx.ID_ANY, (-1, -1), (160, 120), logFiles, wx.LB_SINGLE)
        self.listLogs = dv.DataViewListCtrl(self, size=(108, -1), style=dv.DV_ROW_LINES)
        #self.listLogs = ObjectListView(self, size=(108, -1), style=dv.DV_ROW_LINES)
        self.listLogs.AppendTextColumn('Log File', width=87, flags=dv.DATAVIEW_COL_SORTABLE)

        self.listLogs.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))

        self.loadList()

        self.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.onLogSelected, self.listLogs)
        #self.Bind(wx.EVT_ENTER_WINDOW, self.onFocusWV, self.wvLogs)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.wvLogs.SetPage('<html><body style="background-color: #000000;"></body></html>', "")

        sizer.Add(self.wvLogs, 1, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.TOP, -3)
        sizer.Add(self.listLogs, 0, wx.EXPAND | wx.LEFT, 0)

        self.SetSizer(sizer)

    def loadList(self):
        with self.lock:
            logFiles = [ f for f in reversed(listdir(self.logPath)) if isfile(join(self.logPath, f)) and f.endswith('.html') ]

            self.listLogs.DeleteAllItems()

            for logFile in logFiles:
                self.listLogs.AppendItem([os.path.splitext(logFile)[0]])

            if self.selection is not None:
                self.onLogSelectedIndex(self.selection)
                self.listLogs.SelectRow(self.selection)
                #self.listLogs.SetFocus()

    def onLogSelected(self, event):
        self.selection = event.GetEventObject().GetSelectedRow()
        self.onLogSelectedIndex(self.selection)

        self.parentNotebook.GetPage(INDEX_LOGS).SetFocus()
        #self.listLogs.SetFocus()

        print "****************************************"
        print self.HasFocus()
        print self.listLogs.HasFocus()
        print self.wvLogs.HasFocus()
        print self.parentNotebook.HasFocus()
        print self.parentNotebook.GetPage(0).HasFocus()
        print self.parentNotebook.GetPage(1).HasFocus()
        print self.parentNotebook.GetPage(2).HasFocus()
        print "---------------------------------------"

        #self.Layout()

        #event.Skip()

    def onLogSelectedIndex(self, index):
        #logFile = event.GetEventObject().GetValue(self.selection, 0)
        logFile = self.listLogs.GetValue(index, 0)
        self.loadLogFile(logFile)

    def loadLogFile(self, logFile):
        f = open(self.logPath + "/" + logFile + ".html")
        html = f.read()
        f.close()
        self.onLog(html)

    def onLog(self, html):
        #self.wvLogs.LoadURL("https://dl.dropboxusercontent.com/u/19353176/Myriad%20Switcher/Myriad_log/14.12.23.174707.html")
        self.wvLogs.SetPage(html, "")
        #self.wvLogs.Reload()

    #def onFocusWV(self, index):
    #    pass
