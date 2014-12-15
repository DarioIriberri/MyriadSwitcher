__author__ = 'Dario'

from DataSource import DataSource

URL_DIFFICULTIES = "http://myriad.p2pool.geek.nz/api/network.php"

class P2pool(DataSource):
    def __init__(self, parent, queue, timeout):
        DataSource.__init__(self, parent, queue, timeout)
        self.objDiff = None

    def fetchDifficulties(self):
        self.objDiff = self.fetchDataURL(URL_DIFFICULTIES)
        return self.objDiff

    def getScryptDifficulty(self):
        return self.objDiff["MYR"]["Algorithms"][1]["Difficulty"]

    def getGroestlDifficulty(self):
        return self.objDiff["MYR"]["Algorithms"][2]["Difficulty"]

    def getSkeinDifficulty(self):
        return self.objDiff["MYR"]["Algorithms"][3]["Difficulty"]

    def getQubitDifficulty(self):
        return self.objDiff["MYR"]["Algorithms"][4]["Difficulty"]
