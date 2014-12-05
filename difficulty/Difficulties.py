import Birdonwheels5
import P2pool
import Theblockexplorer
import Queue as queue

__author__ = 'Dario'

TIMEOUT = 10

class Difficulties:
    def __init__(self, parent):
        self.parent = parent

        self.active_source = None

    def fetchDifficulties(self):
        if self.active_source is None or self.active_source.fetchDifficulties() < 0:
            self.fetchThreadedDifficulties()

        #print self.active_source

    def fetchThreadedDifficulties(self):
        q = queue.Queue()

        self.DIFF_SOURCES = (
                             Birdonwheels5.Birdsonwheels5(self.parent),
                             Theblockexplorer.Theblockexplorer(self.parent),
                             P2pool.P2pool(self.parent)
        )

        for source in self.DIFF_SOURCES:
            thread = source
            thread.setQueue(q)
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
