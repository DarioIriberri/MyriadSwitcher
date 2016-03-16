__author__ = 'Dario'

import os
import io
import psutil
import time
import random
import string
import FrameMYR
import win32gui
import win32con
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


#PATH_TO_EXE = os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets\\myriadcoin-qt.exe"
PATH_TO_DOC = os.getcwd() + "\\README\\README.html"
#PATH_TO_WALLET = os.environ['AppData'] + "\\Myriadcoin\\wallet.dat"
PATH_TO_WALLET = os.environ['AppData'] + "\\Digibyte\\wallet.dat"
#PATH_TO_WALLET_DIR = os.environ['AppData'] + "\\Myriadcoin\\"
PATH_TO_WALLET_DIR = os.environ['AppData'] + "\\Digibyte\\"
#EXE_NAME = "myriadcoin-qt.exe"
EXE_NAME = "digibyte-qt.exe"

USER = 'myriadswitcher'
PORT = "8333"

#RPC_CONFIG_FILE = 'myriadcoin.conf'
RPC_CONFIG_FILE = 'digibyte.conf'

walletProcess = None
rpc_conn = None

class QTWallet():
    def __init__(self):
        self.password = self.__generateRandomPassword()

    def openWallet(self, event=None, shell=False):
        global walletProcess

        if not self.__findQTWalletWindow():
            walletProcess = psutil.Popen(FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets\\" + EXE_NAME, shell=shell)

    def createDesktopShortcut(self):
        import win32com.client

        ws = win32com.client.Dispatch("wscript.shell")
        scut = ws.CreateShortcut(os.getenv('UserProfile') + '\\Desktop\\myriadcoin-qt.lnk')
        #self.htmlBuilder.pl(os.getcwd())
        #scut.TargetPath = '"' + (os.getcwd() + '\\electrum\\Electrum-MyrWallet.exe"')
        scut.TargetPath = '\"' + self.getPathToExe() + '\"'
        scut.WorkingDirectory = os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets"
        scut.Save()

    def getPathToExe(self):
        return os.getcwd() + "\\" + FrameMYR.FrameMYRClass.RESOURCE_PATH + "wallets\\" + EXE_NAME

    def checkIfWalletExists(self):
        return os.path.isfile(PATH_TO_WALLET)

    def checkIfWalletIsRunning(self):
        for proc in psutil.process_iter():
            try:
                proc.name()
            except:
                continue

            if EXE_NAME in proc.name():
                return True

        return False

    def getAccountAddress(self, acc=""):
        global walletProcess
        global rpc_conn

        if not walletProcess or not walletProcess.is_running():
            self.__copyDigibyteConf()

            self.openWallet(shell=False)

        count = 0
        walletAddress = None
        MAX_ITER = 60

        while not walletAddress and count < MAX_ITER:
            try:
                rpc_conn = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(USER, self.password, PORT))
                walletAddress = rpc_conn.getaccountaddress('MyriadSwitcher_' + acc)
                #walletAddress = rpc_conn.getaccountaddress("Myriad_Switcher")
            except:
                pass

            count += 1
            time.sleep(1)

        return walletAddress

    def killWallet(self):
        if walletProcess:
            walletProcess.kill()

        configPath = PATH_TO_WALLET_DIR + RPC_CONFIG_FILE
        if os.path.isfile(configPath):
            os.remove(configPath)

    def checkAddress(self, address):
        global rpc_conn

        if not rpc_conn:
            rpc_conn = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(USER, self.password, PORT))

        validateData = rpc_conn.validateaddress(address)

        return validateData['isvalid'] and validateData['ismine']

    def getDifficulties(self):
        global walletProcess
        global rpc_conn

        if not walletProcess or not walletProcess.is_running():
            self.__copyDigibyteConf()

            self.openWallet(shell=False)

        diffs = None
        count = 0
        MAX_ITER = 60

        while not diffs and count < MAX_ITER:
            try:
                rpc_conn = AuthServiceProxy("http://%s:%s@127.0.0.1:%s"%(USER, self.password, PORT))
                diffs = rpc_conn.getinfo()
                #walletAddress = rpc_conn.getaccountaddress("Myriad_Switcher")
            except:
                pass

            count += 1
            time.sleep(1)

        return diffs


    def __copyDigibyteConf(self):
        if not os.path.isdir(PATH_TO_WALLET_DIR):
            os.makedirs(PATH_TO_WALLET_DIR)

        f = open(RPC_CONFIG_FILE)
        lines = f.readlines()
        f.close()

        string_out = ''

        for i in range(0, len(lines)):
            if lines[i].startswith('rpcpassword'):
                lines[i] = "rpcpassword=" + self.password + os.linesep

            string_out += lines[i]

        io.open(PATH_TO_WALLET_DIR + RPC_CONFIG_FILE, 'wt', encoding='utf-8').write(unicode(string_out))

    def __findQTWalletWindow(self):
        cb = lambda x,y: y.append(x)

        wins = []
        win32gui.EnumWindows(cb,wins)

        # now check to see if any match our regexp:
        tgtWin = -1
        for win in wins:
            txt = win32gui.GetWindowText(win)
            if txt == 'DigiByte Core - Wallet':
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

    def __generateRandomPassword(self):
        chars = string.ascii_letters + string.digits
        random.seed = (os.urandom(1024))

        return  ''.join(random.choice(chars) for i in range(32))