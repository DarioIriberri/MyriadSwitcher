__author__ = 'Dario'

from DataSource import DataSource

#URL_DIFFICULTIES = "http://myriad.theblockexplorer.com/api.php?mode=info"
#URL_BLOCK_REWARD = "http://myriad.theblockexplorer.com/api.php?mode=coins"

class Insight(DataSource):
    def __init__(self, parent, queue, url, timeout):
        DataSource.__init__(self, parent, queue, timeout)
        self.url_info = url + "/api.php?mode=info"
        self.url_coins = url + "/api.php?mode=coins"
        self.objDiff = None
        self.objReward = None

    def fetchDifficulties(self):
        self.objDiff = self.fetchDataURL(self.url_info)
        return self.objDiff

    def fetchBlockReward(self):
        self.objReward = self.fetchDataURL(self.url_coins)
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