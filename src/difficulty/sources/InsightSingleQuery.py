__author__ = 'Dario'

from DataSource import DataSource

class InsightSingleQuery(DataSource):
    def __init__(self, parent, url, queue, timeout):
        DataSource.__init__(self, parent, queue, timeout)
        self.url_info = url
        self.objInfo = None

    def fetchDifficulties(self):
        self.objInfo = self.fetchDataURL(self.url_info)
        return self.objInfo

    def fetchBlockReward(self):
        self.objInfo = self.fetchDataURL(self.url_info)
        return self.objInfo

    def getScryptDifficulty(self):
        return self.objInfo['info']["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.objInfo['info']["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.objInfo['info']["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.objInfo['info']["difficulty_qubit"]

    def getBlockReward(self):
        block = int(self.objInfo['info']["blocks"])
        return self.calculateBlockReward(block)
