__author__ = 'Dario'

from DataSource import DataSource

URL_INFO = "http://birdonwheels5.no-ip.org/api/status?q=getInfo"

class Birdonwheels5(DataSource):
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
        return self.objInfo["info"]["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.objInfo["info"]["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.objInfo["info"]["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.objInfo["info"]["difficulty_qubit"]

    def getBlockReward(self):
        block = int(self.objInfo["info"]["blocks"])
        return self.calculateBlockReward(block)