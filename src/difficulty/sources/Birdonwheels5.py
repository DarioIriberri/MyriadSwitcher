__author__ = 'Dario'

from DifficultySource import DifficultySource


class Birdonwheels5(DifficultySource):
    def __init__(self, parent, queue, timeout):
        DifficultySource.__init__(self, parent, queue, timeout)

    def fetchDifficulties(self):
        return self.fetchDifficultiesURL("http://birdonwheels5.no-ip.org/api/status?q=getInfo")

    def getScryptDifficulty(self):
        return self.obj["info"]["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.obj["info"]["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.obj["info"]["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.obj["info"]["difficulty_qubit"]