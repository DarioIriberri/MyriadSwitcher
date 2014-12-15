__author__ = 'Dario'

import wx
from PanelMinerInstance import PanelMinerInstance
from wx.lib.splitter import MultiSplitterWindow


class PanelMiners(MultiSplitterWindow):
    def __init__(self, parent, num_miners = 4):
        MultiSplitterWindow.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.SP_LIVE_UPDATE)

        self.parent = parent
        self.num_miners = num_miners

        self.miner0 = PanelMinerInstance(self, "Miner #0")
        self.miner1 = PanelMinerInstance(self, "Miner #1")
        self.miner2 = PanelMinerInstance(self, "Miner #2")
        self.miner3 = PanelMinerInstance(self, "Miner #3")
        self.SetOrientation(wx.HORIZONTAL)

        self.AppendWindow(self.miner0)
        self.AppendWindow(self.miner1)
        self.AppendWindow(self.miner2)
        self.AppendWindow(self.miner3)

        #self.miner0.AppendText("Device 0 Output..." + os.linesep + os.linesep)
        #self.miner1.AppendText("Device 1 Output..." + os.linesep + os.linesep)
        #self.miner2.AppendText("Device 2 Output..." + os.linesep + os.linesep)
        #self.miner3.AppendText("Device 3 Output..." + os.linesep + os.linesep)

        self.Bind(wx.EVT_SIZE, self.rearrangeMiners)

    def rearrangeMiners(self, event):
        best = self.GetSize()[0] / self.num_miners

        self.SetSashPosition(0, best)
        self.SetSashPosition(1, best)
        self.SetSashPosition(2, best)
        self.SetSashPosition(3, best)