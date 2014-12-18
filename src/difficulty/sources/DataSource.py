__author__ = 'Dario'

import json
import math
import time


class DataSource():
    def __init__(self, parent, queue, timeout):
        self.parent = parent
        self.queue = queue
        self.timeout = timeout

    def fetchDataURL(self, url):
        try:
            getResult = self.parent.httpGet(url)

        except:
            return None

        try:
            obj = json.loads(getResult)
            #print time.strftime("%m/%d/%Y %H:%M:%S", time.localtime()) + " : " + str(self) + "   -   " + str(obj)
            if obj:
                self.queue.put(self)

        except:
            return None

        return obj

    def calculateBlockReward(self, block):
        halves = block / 967680
        reward = 1000 / math.pow(2, halves)

        return reward

