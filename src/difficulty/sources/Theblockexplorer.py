__author__ = 'Dario'

from DataSource import DataSource

URL_DIFFICULTIES = "http://myriad.theblockexplorer.com/api.php?mode=info"
URL_BLOCK_REWARD = "http://myriad.theblockexplorer.com/api.php?mode=coins"

class Theblockexplorer(DataSource):
    def __init__(self, parent, queue, timeout):
        DataSource.__init__(self, parent, queue, timeout)
        self.objDiff = None
        self.objReward = None

    def fetchDifficulties(self):
        self.objDiff = self.fetchDataURL(URL_DIFFICULTIES)
        return self.objDiff

    def fetchBlockReward(self):
        self.objReward = self.fetchDataURL(URL_BLOCK_REWARD)
        return self.objReward

    def getScryptDifficulty(self):
        return self.objDiff["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.objDiff["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.objDiff["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.objDiff["difficulty_qubit"]

    def getBlockReward(self):
        return self.objReward["per"]