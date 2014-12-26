__author__ = 'Dario'

import os
import psutil
import FrameMYR

PATH_TO_EXE = os.getcwd() + "\\wallets\\Electrum-MyrWallet.exe"
PATH_TO_DOC = os.getcwd() + "\\README\\README.html"
PATH_TO_WALLET = os.environ['AppData'] + "\\Electrum-MYR\\wallets\\default_wallet"


def openWallet(event=None):
    psutil.Popen(FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets/Electrum-MyrWallet.exe", shell=False)

def createDesktopShortcut():
    import win32com.client

    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(os.getenv('UserProfile') + '\\Desktop\\Electrum-MyrWallet.lnk')
    #self.htmlBuilder.pl(os.getcwd())
    #scut.TargetPath = '"' + (os.getcwd() + '\\electrum\\Electrum-MyrWallet.exe"')
    scut.TargetPath = '\"' + PATH_TO_EXE + '\"'
    scut.WorkingDirectory = os.getcwd() + '\\electrum'
    scut.Save()

def checkIfWalletExists():
    return os.path.isfile(PATH_TO_WALLET)

def getMyrAddress():
    walletAddress = None

    if os.path.isfile(PATH_TO_WALLET):
        f = open(PATH_TO_WALLET)
        data = f.read()
        f.close()
        walletAddress = data[data.index('addr_history') + 17 : data.index('[]') - 3 ]

    return walletAddress