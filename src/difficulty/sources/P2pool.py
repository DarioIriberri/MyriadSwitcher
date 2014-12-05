__author__ = 'Dario'

from DifficultySource import DifficultySource


class P2pool(DifficultySource):
    def __init__(self, parent, queue, timeout):
        DifficultySource.__init__(self, parent, queue, timeout)

    def fetchDifficulties(self):
        return self.fetchDifficultiesURL("http://myriad.p2pool.geek.nz/api/network.php")

    def getScryptDifficulty(self):
        return self.obj["MYR"]["Algorithms"][1]["Difficulty"]

    def getGroestlDifficulty(self):
        return self.obj["MYR"]["Algorithms"][2]["Difficulty"]

    def getSkeinDifficulty(self):
        return self.obj["MYR"]["Algorithms"][3]["Difficulty"]

    def getQubitDifficulty(self):
        return self.obj["MYR"]["Algorithms"][4]["Difficulty"]
