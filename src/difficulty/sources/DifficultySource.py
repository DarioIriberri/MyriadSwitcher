__author__ = 'Dario'

import json


class DifficultySource():
    def __init__(self, parent, queue, timeout):
        self.parent = parent
        self.queue = queue
        self.timeout = timeout

    def fetchDifficultiesURL(self, url):
        try:
            getResult = self.parent.httpGet(url)

        except:
            return -1

        try:
            self.obj = json.loads(getResult)
            #print str(self) + "   -   " + str(self.obj)
            self.queue.put(self)

        except:
            return -2

        return 0

