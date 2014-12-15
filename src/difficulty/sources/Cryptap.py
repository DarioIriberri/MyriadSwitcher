__author__ = 'Dario'

from DataSource import DataSource

URL_BLOCK_REWARD = "http://cryptap.us/myr/explorer/chain/Myriadcoin/q/getblockcount?format=json"

class Cryptap(DataSource):
    def __init__(self, parent, queue, timeout):
        DataSource.__init__(self, parent, queue, timeout)
        self.objReward = None

    def fetchBlockReward(self):
        self.objReward = self.fetchDataURL(URL_BLOCK_REWARD)
        return self.objReward

    def getBlockReward(self):
        block = int(self.objReward[0])
        return self.calculateBlockReward(block)