__author__ = 'Dario'

import wx
from wallet import QTWallet
import FrameMYR
import wx.wizard as wiz
import wx.lib.agw.genericmessagedialog as GMD


PAGE_WELCOME  = "PAGE_WELCOME"
PAGE_ELECTRUM = "PAGE_ELECTRUM"
PAGE_SHORTCUT = "PAGE_SHORTCUT"
PAGE_DONE     = "PAGE_DONE"


class MyriadSwitcherWizard(wiz.Wizard):
    def __init__(self, parent):
        wiz.Wizard.__init__(self, parent, wx.ID_ANY, "Myriad Switcher Wizard", wx.Bitmap(FrameMYR.FrameMYRClass.RESOURCE_PATH + 'img/myriadS1.ico'))

    def startWizard(self):
        wallet = QTWallet.QTWallet()
        message = "Welcome to Myriad Switcher \n\n" \
                  "You can find your wallet at\n\n" + wallet.getPathToExe() + "\n\n" \
                  "or you can open it using the desktop shortcut if you choose to create it.\n\n" \
                  "You can access the documentation via\n\n" \
                  "Menu -> Help -> Open User Guide\n\nor browse to\n\n" + \
                  QTWallet.PATH_TO_DOC + "\n\nThe application will start now. \n" \
                  "Just pick your mining device(s) in the lower panel \n" \
                  "and start mining by pressing the 'Start' button.\n\n" \
                  "Do you want to create a desktop shortcut to your wallet?"

        dlg = GMD.GenericMessageDialog(self, message, "Welcome", wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION)
        result = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()

        if result:
            wallet.createDesktopShortcut()