__author__ = 'Dario'

from sources.Birdonwheels5 import Birdonwheels5
from sources.Theblockexplorer import Theblockexplorer
from sources.InsightSingleQuery import InsightSingleQuery
from sources.TheblockexplorerSingleQuery import TheblockexplorerSingleQuery
from sources.P2pool import P2pool
from sources.Cryptap import Cryptap

import threading
import Queue as queue
import time

TIMEOUT = 10


class Difficulties:
    def loadDiffSources(self, queue):
        self.DIFF_SOURCES = \
        (
             #Birdonwheels5(self.parent, queue, TIMEOUT),
             InsightSingleQuery(self.parent, 'http://birdonwheels5.no-ip.org/api/status?q=getInfo', queue, TIMEOUT),
             #Theblockexplorer(self.parent, queue, TIMEOUT),
             TheblockexplorerSingleQuery(self.parent, queue, TIMEOUT),
             InsightSingleQuery(self.parent, 'https://cryptap.us/myr/insight/api/status?q=getInfo', queue, TIMEOUT),
             P2pool(self.parent, queue, TIMEOUT),
        )

        return self.DIFF_SOURCES

    def loadRewardSources(self, queue):
        self.REWARD_SOURCES = \
        (
             #Birdonwheels5(self.parent, queue, TIMEOUT),
             InsightSingleQuery(self.parent, 'http://birdonwheels5.no-ip.org/api/status?q=getInfo', queue, TIMEOUT),
             #Theblockexplorer(self.parent, queue, TIMEOUT),
             TheblockexplorerSingleQuery(self.parent, queue, TIMEOUT),
             InsightSingleQuery(self.parent, 'https://cryptap.us/myr/insight/api/status?q=getInfo', queue, TIMEOUT),
             Cryptap(self.parent, queue, TIMEOUT),
        )

        return self.REWARD_SOURCES

    def __init__(self, parent):
        self.parent = parent
        self.active_diff_source = None
        self.active_reward_source = None


    ####################################################################################################################
    ###############################################  FETCHERS  #########################################################
    ####################################################################################################################


    def fetchDifficulties(self):
        return self.fetchData(self.active_diff_source, "fetchDifficulties", self.fetchThreadedDifficulties)

    def fetchThreadedDifficulties(self):
        self.active_diff_source = self.fetchThreadedData(self.loadDiffSources, "fetchDifficulties")

    def fetchBlockReward(self):
        block_reward = None
        try:
            block_reward = self.active_diff_source.getBlockReward()
        except:
            pass

        if not block_reward:
            return self.fetchData(self.active_reward_source, "fetchBlockReward", self.fetchThreadedBlockReward)

    def fetchThreadedBlockReward(self):
        self.active_reward_source = self.fetchThreadedData(self.loadRewardSources, "fetchBlockReward")

    def fetchData(self, active_reward_source, fetchDataFunc, fetchThreadedFunc):
        t1 = time.time()

        if not active_reward_source or not getattr(active_reward_source, fetchDataFunc)():
            fetchThreadedFunc()

        return str((time.time() - t1) * 1000) + " ms" + " - " + str(self.active_diff_source)

    def fetchThreadedData(self, loadDataSourcesFunc, fetchDataFunc):
        q = queue.Queue()

        SOURCES = loadDataSourcesFunc(q)

        for source in SOURCES:
            thread = threading.Thread(target=getattr(source, fetchDataFunc))
            thread.start()
            #thread.join()

        return q.get(block=True, timeout=TIMEOUT)


    ####################################################################################################################
    ################################################  GETTERS  #########################################################
    ####################################################################################################################


    def getScryptDifficulty(self):
        return self.active_diff_source.getScryptDifficulty()

    def getGroestlDifficulty(self):
        return self.active_diff_source.getGroestlDifficulty()

    def getSkeinDifficulty(self):
        return self.active_diff_source.getSkeinDifficulty()

    def getQubitDifficulty(self):
        return self.active_diff_source.getQubitDifficulty()

    def getBlockReward(self):
        try:
            block_reward = self.active_diff_source.getBlockReward()
        except:
            return self.active_reward_source.getBlockReward()

        return block_reward