__author__ = 'Dario'

from DataSource import DataSource

URL_INFO = "http://myriad.theblockexplorer.com/api.php?mode=info"

class TheblockexplorerSingleQuery(DataSource):
    def __init__(self, parent, queue, timeout):
        DataSource.__init__(self, parent, queue, timeout)
        self.objInfo = None

    def fetchDifficulties(self):
        self.objInfo = self.fetchDataURL(URL_INFO)
        return self.objInfo

    def fetchBlockReward(self):
        self.objInfo = self.fetchDataURL(URL_INFO)
        return self.objInfo

    def getScryptDifficulty(self):
        return self.objInfo["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.objInfo["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.objInfo["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.objInfo["difficulty_qubit"]

    def getBlockReward(self):
        block = int(self.objInfo["blocks"])
        return self.calculateBlockReward(block)
