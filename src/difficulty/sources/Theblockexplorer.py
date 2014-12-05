__author__ = 'Dario'

from DifficultySource import DifficultySource


class Theblockexplorer(DifficultySource):
    def __init__(self, parent, queue, timeout):
        DifficultySource.__init__(self, parent, queue, timeout)

    def fetchDifficulties(self):
        return self.fetchDifficultiesURL("http://myriad.theblockexplorer.com/api.php?mode=info")

    def getScryptDifficulty(self):
        return self.obj["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.obj["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.obj["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.obj["difficulty_qubit"]
