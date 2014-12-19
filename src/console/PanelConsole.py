__author__ = 'Dario'

import time

import wx
import wx.html2 as webview
from event.Event import Event
from console.switcher.SwitchingThread import SwitchingThread
from event.EventLib import ConsoleEvent, EVT_CONSOLE_EVENT


MAX_STOP_TIME = 45


class PanelConsole(wx.Panel):
    def __init__(self, parent, frame_myr, size=None, style=wx.BORDER_DEFAULT):
        wx.Panel.__init__(self, parent=parent, size=size, id=wx.ID_ANY, style=style)

        self.parent = parent
        self.frame_myr = frame_myr

        self.thread = None
        self.threadCount = 0
        self.messageEvent = None

        self.wv = webview.WebView.New(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.wv.SetBackgroundColour("Black")
        sizer.Add(self.wv, 1, wx.EXPAND | wx.ALL, -1)
        self.SetSizer(sizer)

        self.Bind(EVT_CONSOLE_EVENT, self.onConsole)
        #EVT_CONSOLE_EVENT(self, self.onConsole)

        self.wv.Show(False)

    def addMessageEventListener(self, eventListener):
        messageEvent = Event(eventListener)

        if not self.messageEvent:
            self.messageEvent = messageEvent
        else:
            self.messageEvent += messageEvent

    def fireMessageEvent(self, output_text):
        if self.messageEvent:
            self.messageEvent(output_text)

    #def onConsoleEvent(self, html):
    #    self.wv.SetPage(html, "")
    #    self.wv.Reload()

    def onConsole(self, event):
        #print "console     " + str(time.time()) + "   -   " + event.html
        #self.wv.SetPage(str(time.time()), "")
        self.wv.SetPage(event.html, "")
        self.wv.Reload()
        #self.wv.Find(HTMLBuilder.ANCHOR)
        #self.Scroll(0, self.GetScrollRange(wx.VERTICAL))
        #self.parent.Scroll(0, self.parent.GetScrollRange(wx.VERTICAL))
        #self.SetScrollbars(0, 1111, 1111, 11)
        #print "Console says = " + event.html
        #self.wv.SetPage("<html><header><title>This is title</title></header><body>Hello world</body></html>", "")
        #self.wv.LoadURL("https://dl.dropboxusercontent.com/u/19353176/Myriad_log/2014-05-04-040554.html")

    def onMiningProcessStarted(self):
        self.frame_myr.onMiningProcessStarted()

    def onMiningProcessStopped(self):
        self.frame_myr.onMiningProcessStopped()

    def getThread(self, rebooting, resume):
        self.threadCount += 1
        return SwitchingThread("SwitchThread", self.threadCount, self, rebooting, resume)

    def mine(self, activeConfigFile, rebooting=False, resume=False):
        self.wv.Show(True)
        self.Layout()

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
            t = time.time()
            success = False
            i = 0
            str_out = "Waiting for threads to die " + str(i)
            self.printToConsole(str_out)
            while time.time() < t + MAX_STOP_TIME:
                if self.thread.isAlive():
                    time.sleep(1)
                    i += 1
                    str_out +=  ", " + str(i)
                    self.printToConsole(str_out)

                else:
                    str_out = "done, Bye!"
                    self.printToConsole(str_out)
                    #time.sleep(2)
                    success = True
                    break

            print "Exited with success = " + str(success)

            if not success:
                str_out = "Damn it"
                self.printToConsole(str_out)
                time.sleep(5)


    def printToConsole(self, str_out):
        print str_out
        evt = ConsoleEvent(thread_ident=self.thread.ident, html=str_out)
        wx.PostEvent(self, evt)
