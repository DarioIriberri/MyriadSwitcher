__author__ = 'Dario'

import os
import psutil
import shutil
import time
import subprocess
import FrameMYR
import win32gui
import win32con
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


#PATH_TO_EXE = os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets\\myriadcoin-qt.exe"
PATH_TO_DOC = os.getcwd() + "\\README\\README.html"
PATH_TO_WALLET = os.environ['AppData'] + "\\Myriadcoin\\wallet.dat"
PATH_TO_WALLET_DIR = os.environ['AppData'] + "\\Myriadcoin\\"

walletProcess = None
rpc_conn = None

def openWallet(event=None, shell=False):
    global walletProcess

    if not __findQTWalletWindow():
        walletProcess = psutil.Popen(FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets/myriadcoin-qt.exe", shell=shell)

#def openWalletExtern(event=None, shell=False):
#    if not __findQTWalletWindow():
#        callS = os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + 'wallets\\myriadcoin-qt.exe'
#        subprocess.call(callS, shell=False)

def createDesktopShortcut():
    import win32com.client

    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(os.getenv('UserProfile') + '\\Desktop\\myriadcoin-qt.lnk')
    #self.htmlBuilder.pl(os.getcwd())
    #scut.TargetPath = '"' + (os.getcwd() + '\\electrum\\Electrum-MyrWallet.exe"')
    scut.TargetPath = '\"' + getPathToExe() + '\"'
    scut.WorkingDirectory = os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets"
    scut.Save()

def getPathToExe():
    return os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets\\myriadcoin-qt.exe"

def checkIfWalletExists():
    return os.path.isfile(PATH_TO_WALLET)

def getNewAddress(acc=""):
    global walletProcess
    global rpc_conn

    if not walletProcess or not walletProcess.is_running():
        __copyMyriadcoinConf()

        openWallet(shell=False)

    count = 0
    walletAddress = None
    MAX_ITER = 30

    while not walletAddress and count < MAX_ITER:
        try:
            rpc_conn = AuthServiceProxy("http://%s:%s@127.0.0.1:8333"%("myriadswitcher", "123"))
            walletAddress = rpc_conn.getaccountaddress('MyriadSwitcher_' + acc)
            #walletAddress = rpc_conn.getaccountaddress("Myriad_Switcher")
        except:
            pass

        count += 1
        time.sleep(1)

    return walletAddress

def killWallet():
    if walletProcess:
        walletProcess.kill()

    os.remove(PATH_TO_WALLET_DIR + "myriadcoin.conf")

def checkAddress(address):
    global rpc_conn

    #try:
        #acc = rpc_conn.getaccount(address)
    listAddGrp = rpc_conn.listaddressgroupings()

    listAdd = [
                   rpc_conn.getaccountaddress(""),
                   rpc_conn.getaccountaddress('MyriadSwitcher_' + FrameMYR.SCRYPT),
                   rpc_conn.getaccountaddress('MyriadSwitcher_' + FrameMYR.GROESTL),
                   rpc_conn.getaccountaddress('MyriadSwitcher_' + FrameMYR.SKEIN),
                   rpc_conn.getaccountaddress('MyriadSwitcher_' + FrameMYR.QUBIT)
              ]

    for list1 in listAddGrp:
        for list2 in list1:
            listAdd.append(list2[0])

    return address in listAdd

    #except JSONRPCException:
    #    return False

def __copyMyriadcoinConf():
    if not os.path.isdir(PATH_TO_WALLET_DIR):
        os.makedirs(PATH_TO_WALLET_DIR)

    shutil.copyfile(os.getcwd() + "\\myriadcoin.conf", PATH_TO_WALLET_DIR + "myriadcoin.conf")

def __findQTWalletWindow():
    cb = lambda x,y: y.append(x)

    wins = []
    win32gui.EnumWindows(cb,wins)

    # now check to see if any match our regexp:
    tgtWin = -1
    for win in wins:
        txt = win32gui.GetWindowText(win)
        if txt == 'Myriadcoin Core - Wallet':
            tgtWin = win

    if tgtWin >= 0:
        win32gui.ShowWindow(tgtWin, win32con.SW_RESTORE)
        win32gui.ShowWindow(tgtWin, win32con.SW_SHOW)
        win32gui.BringWindowToTop(tgtWin)
        win32gui.SetForegroundWindow(tgtWin)

        #        ShowWindow(hWnd,SW_SHOW);
        #::BringWindowToTop(hWnd);
        #::SetForegrounWindow(hWnd)

        return True

    return False