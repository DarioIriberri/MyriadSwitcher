__author__ = 'Dario'

import Difficulties
import json
import threading


class Theblockexplorer (threading.Thread):
    def __init__(self, parent):
        super(Theblockexplorer, self).__init__()

        self.parent = parent

    def fetchDifficulties(self):
        try:
            getResult = self.parent.httpGet("http://myriad.theblockexplorer.com/api.php?mode=info", Difficulties.TIMEOUT)

        except:
            return -1

        try:
            self.obj = json.loads(getResult)
            self.queue.put(self)

        except:
            return -2

        return 0

    def setQueue(self, queue):
        self.queue = queue

    def run(self):
        self.fetchDifficulties()

    def getScryptDifficulty(self):
        return self.obj["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.obj["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.obj["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.obj["difficulty_qubit"]
