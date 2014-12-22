__author__ = 'Dario'

import wx
import os
import wx.wizard as wiz
import FrameMYR


class MyriadSwitcherWizard(wiz.Wizard):
    def __init__(self, parent):
        wiz.Wizard.__init__(self, parent, wx.ID_ANY, "Myriad Switcher Wizard", wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH   + 'img/myriadS1.ico'))

    def runWizard(self):
        page1 = TitledPage(self, "Welcome to Myriad Switcher")
        page2 = TitledPage(self, "Page 2")
        page3 = TitledPage(self, "Page 3")
        page4 = TitledPage(self, "Page 4")
        self.page1 = page1

        page1.sizer.Add(wx.StaticText(page1, -1, """
            This wizard is totally useless, but is meant to show how to
            chain simple wizard pages together in a non-dynamic manner.
            IOW, the order of the pages never changes, and so the
            wxWizardPageSimple class can easily be used for the pages."""))

        self.FitToPage(page1)
        page4.sizer.Add(wx.StaticText(page4, -1, "\nThis is the last page."))

        # Use the convenience Chain function to connect the pages
        wiz.WizardPageSimple.Chain(page1, page2)
        wiz.WizardPageSimple.Chain(page2, page3)
        wiz.WizardPageSimple.Chain(page3, page4)

        self.GetPageAreaSizer().Add(page1)
        if self.RunWizard(page1):
            wx.MessageBox("Wizard completed successfully", "That's all folks!")
        else:
            wx.MessageBox("Wizard was cancelled", "That's all folks!")



class TitledPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        self.sizer = self.makePageTitle(self, title)

    def makePageTitle(self, wizPg, title):
        sizer = wx.BoxSizer(wx.VERTICAL)
        wizPg.SetSizer(sizer)
        title = wx.StaticText(wizPg, -1, title)
        title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
        return sizer