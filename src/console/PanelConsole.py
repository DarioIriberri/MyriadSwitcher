__author__ = 'Dario'

import time

import wx
import wx.html2 as webview
import FrameMYR
from event.Event import Event
from console.switcher.SwitchingThread import SwitchingThread
from event.EventLib import ConsoleEvent, EVT_CONSOLE_EVENT

INDEX_CONSOLE = 0
INDEX_BROWSER = 1


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

        self.wvConsole = webview.WebView.New(self.notebook)
        self.wvBrowser = webview.WebView.New(self.notebook)

        self.notebook.AddPage(self.wvConsole, "Output  ")
        self.notebook.AddPage(self.wvBrowser, "Browser ")
        self.notebook.SetPageImage(INDEX_CONSOLE, self.il.Add(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/console16.ico', wx.BITMAP_TYPE_ICO)))
        self.notebook.SetPageImage(INDEX_BROWSER, self.il.Add(wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/browser2.ico', wx.BITMAP_TYPE_ICO)))

        self.notebook.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        sizer = wx.BoxSizer(wx.VERTICAL)
        #self.SetBackgroundColour("Black")

        self.wvConsole.SetPage('<html><body style="background-color: #000000;"></body></html>', "")
        self.wvBrowser.SetPage('<html><body style="background-color: #AAAAAA;"></body></html>', "")

        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)

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

    #def onConsoleEvent(self, html):
    #    self.wv.SetPage(html, "")
    #    self.wv.Reload()

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

    def setBrowser(self, url):
        self.notebook.SetSelection(INDEX_BROWSER)
        #self.notebook.GetPage(1).Show()
        #self.wvBrowser.SetPage(html, "")
        self.wvBrowser.LoadURL(url)
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
                    str_out = "done, Bye!"
                    print str_out
                    #time.sleep(2)
                    success = True
                    break

            print "Threads: Exited with success = " + str(success)

            if not success:
                str_out = "Damn it"
                print str_out
                time.sleep(5)


    def printToConsole(self, str_out):
        print str_out
        evt = ConsoleEvent(thread_ident=self.thread.ident, html=str_out)
        wx.PostEvent(self, evt)
