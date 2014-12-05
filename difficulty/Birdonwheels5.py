__author__ = 'Dario'

import Difficulties
import json
import threading


class Birdonwheels5 (threading.Thread):
    def __init__(self, parent):
        super(Birdonwheels5, self).__init__()

        self.parent = parent

    def fetchDifficulties(self):
        try:
            getResult = self.parent.httpGet("http://birdonwheels5.no-ip.org/api/status?q=getInfo", Difficulties.TIMEOUT)

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
        return self.obj["info"]["difficulty_scrypt"]

    def getGroestlDifficulty(self):
        return self.obj["info"]["difficulty_groestl"]

    def getSkeinDifficulty(self):
        return self.obj["info"]["difficulty_skein"]

    def getQubitDifficulty(self):
        return self.obj["info"]["difficulty_qubit"]
