__author__ = 'Dario'

from sources.Birdonwheels5 import Birdonwheels5
from sources.Theblockexplorer import Theblockexplorer
from sources.P2pool import P2pool

import threading
import Queue as queue

TIMEOUT = 10


class Difficulties:
    def __init__(self, parent):
        self.parent = parent
        self.active_source = None

    def loadSources(self, queue):
        self.DIFF_SOURCES = (
                             Birdonwheels5(self.parent, queue, TIMEOUT),
                             Theblockexplorer(self.parent, queue, TIMEOUT),
                             P2pool(self.parent, queue, TIMEOUT),
        )

    def fetchDifficulties(self):
        if self.active_source is None or self.active_source.fetchDifficulties() < 0:
            self.fetchThreadedDifficulties()

        #print self.active_source

    def fetchThreadedDifficulties(self):
        q = queue.Queue()

        self.loadSources(q)

        for source in self.DIFF_SOURCES:
            thread = threading.Thread(target=source.fetchDifficulties)
            thread.start()
            #thread.join()

        self.active_source = q.get(block=True, timeout=TIMEOUT)

    def getScryptDifficulty(self):
        return self.active_source.getScryptDifficulty()

    def getGroestlDifficulty(self):
        return self.active_source.getGroestlDifficulty()

    def getSkeinDifficulty(self):
        return self.active_source.getSkeinDifficulty()

    def getQubitDifficulty(self):
        return self.active_source.getQubitDifficulty()
