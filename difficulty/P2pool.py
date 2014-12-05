__author__ = 'Dario'

import Difficulties
import json
import threading


class P2pool (threading.Thread):
    def __init__(self, parent):
        super(P2pool, self).__init__()

        self.parent = parent

    def fetchDifficulties(self):
        try:
            getResult = self.parent.httpGet("http://myriad.p2pool.geek.nz/api/network.php", Difficulties.TIMEOUT)

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
        return self.obj["MYR"]["Algorithms"][1]["Difficulty"]

    def getGroestlDifficulty(self):
        return self.obj["MYR"]["Algorithms"][2]["Difficulty"]

    def getSkeinDifficulty(self):
        return self.obj["MYR"]["Algorithms"][3]["Difficulty"]

    def getQubitDifficulty(self):
        return self.obj["MYR"]["Algorithms"][4]["Difficulty"]
