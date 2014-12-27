__author__ = 'Dario'

import wx
import os
#from wallet import Electrum as wallet
from wallet import QTWallet as wallet
import FrameMYR
import wx.wizard as wiz


PAGE_WELCOME  = "PAGE_WELCOME"
PAGE_ELECTRUM = "PAGE_ELECTRUM"
PAGE_SHORTCUT = "PAGE_SHORTCUT"
PAGE_DONE     = "PAGE_DONE"


class MyriadSwitcherWizard(wiz.Wizard):
    def __init__(self, parent):
        wiz.Wizard.__init__(self, parent, wx.ID_ANY, "Myriad Switcher Wizard", wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH + 'img/myriadS1.ico'))
        #self.Bind(wiz.EVT_WIZARD_PAGE_CHANGED, self.onPageChanged)
        self.Bind(wiz.EVT_WIZARD_BEFORE_PAGE_CHANGED, self.onBeforePageChanged)
        self.isRunning = False

    def startWizard(self):
        page1 = WizardPage(self, "Welcome to Myriad Switcher", PAGE_WELCOME)
        page2 = WizardPage2(self, "Wallet shortcut in your desktop?", PAGE_ELECTRUM)
        page3 = WizardPage(self, "That's it! Happy mining", PAGE_SHORTCUT)
        self.page4 = WizardPage(self, "Oops, your Electrum setup failed.", PAGE_DONE)
        self.page1 = page1

        page1.sizer.Add(wx.StaticText(page1, -1, """
    This wizard will guide you through the process of setting up
    everything you need to start mining Myriadcoin in just a few.
    steps.

    First we need a wallet to store your mined coins. Press 'Next'
    to open your wallet and follow the instructions if any.

    Once the wallet shows up after the setup process is done
    come back to the wizard and complete the next steps."""))

        page3.sizer.Add(wx.StaticText(page3, -1, """
    You can find your wallet at

    """ + wallet.PATH_TO_EXE + """

    or you can open it using the desktop shortcut if you created it.

    You can access the documentation via
    Menu -> Help -> Open User Guide
    or browse to

    """ + wallet.PATH_TO_DOC + """

    The application will start now. Just pick your mining device(s)
    in the lower panel and start mining by pressing the 'Start' button."""))

        self.page4.sizer.Add(wx.StaticText(self.page4, -1, """
    Click 'Next' to run the wizard again."""))

        #self.FitToPage(page1)
        self.FitToPage(page3)

        page1.SetNext(page2)
        page2.SetPrev(page1)
        page2.SetNext(page3)
        page3.SetPrev(page2)
        #page3.SetNext(page4)
        self.page4.SetNext(WizardPage(self, ""))

        self.GetPageAreaSizer().Add(page1)

        if self.RunWizard(page1):
            pass
            #wx.MessageBox("Wizard completed successfully", "That's all folks!")
        else:
            wx.MessageBox("Wizard was cancelled", "Configuration may be incomplete")

    #def onPageChanged(self, event):
    #    if event.GetPage().pageId == PAGE_ELECTRUM:
    #        psutil.Popen(FrameMYR.FrameMYRClass.RESOURCE_PATH + "/electrum/Electrum-MyrWallet.exe", shell=False)
    #
    #    if event.GetPage().pageId == PAGE_SHORTCUT:
    #        psutil.Popen(FrameMYR.FrameMYRClass.RESOURCE_PATH + "/electrum/Electrum-MyrWallet.exe", shell=False)
    #
    #    event.Skip()

    def onBeforePageChanged(self, event):
        if event.GetPage().pageId == PAGE_WELCOME:
            self.isRunning = False

        if event.GetPage().pageId == PAGE_ELECTRUM:
            self.isRunning = True
            if os.name == "nt":
                #psutil.Popen(FrameMYR.FrameMYRClass.RESOURCE_PATH + "/electrum/Electrum-MyrWallet.exe", shell=False)
                wallet.openWallet()

            if os.name == "posix":
                pass

        if event.GetPage().pageId == PAGE_SHORTCUT:
            if os.name == "nt":
                if event.GetPage().prev.cb.GetValue():
                    wallet.createDesktopShortcut()

            if os.name == "posix":
                pass

        event.Skip()


class WizardPage(wiz.PyWizardPage):
    def __init__(self, parent, title=None, pageId=None):
        wiz.PyWizardPage.__init__(self, parent)
        self.parent = parent
        self.pageId = pageId
        self.sizer = makePageTitle(self, title)
        self.next = self.prev = None
        #self.error = False

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        if self.parent.isRunning and self.pageId == PAGE_DONE:
            return self.parent.page1
        return self.next

    def GetPrev(self):
        return self.prev


class WizardPage2(WizardPage):
    def __init__(self, parent, title, pageId):
        WizardPage.__init__(self, parent, title, pageId)

        self.cb = wx.CheckBox(self, -1, "Do you want to create a shorcut to your wallet in the desktop?")
        self.sizer.Add(self.cb, 0, wx.ALL, 5)

    def GetNext(self):
        if not wallet.checkIfWalletExists():
            return self.parent.page4

        return self.next


def makePageTitle(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer