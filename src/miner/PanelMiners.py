__author__ = 'Dario'

import wx
import time
import threading
import PanelMinerInstance as PMI
from wx.lib.splitter import MultiSplitterWindow


class PanelMiners(MultiSplitterWindow):
    lock = threading.RLock()

    def __init__(self, parent, frame, num_miners = 4):
        MultiSplitterWindow.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.SP_LIVE_UPDATE)

        self.parent = parent
        self.frame = frame
        self.resize_lock = False

        self.num_miners = num_miners

        self.miner0 = PMI.PanelMinerInstance(self, "Miner #0")
        self.miner1 = PMI.PanelMinerInstance(self, "Miner #1")
        self.miner2 = PMI.PanelMinerInstance(self, "Miner #2")
        self.miner3 = PMI.PanelMinerInstance(self, "Miner #3")
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

    def executeAlgo(self, maxAlgo, restart):
        ret0 = self.miner0.executeAlgo(maxAlgo, restart)
        ret1 = self.miner1.executeAlgo(maxAlgo, restart)
        ret2 = self.miner2.executeAlgo(maxAlgo, restart)
        ret3 = self.miner3.executeAlgo(maxAlgo, restart)

        if (ret0 is None and ret1 is None and ret2 is None and ret3 is None):
            return None

        return ret0 or ret1 or ret2 or ret3

    def checkMinerCrashed(self):
        if self.miner0.minerStatus() == PMI.STATUS_CRASHED or \
           self.miner1.minerStatus() == PMI.STATUS_CRASHED or \
           self.miner2.minerStatus() == PMI.STATUS_CRASHED or \
           self.miner3.minerStatus() == PMI.STATUS_CRASHED:

            return False

        return True

    def checkMinersReady(self):
        if ( self.miner0.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED) ) and \
           ( self.miner1.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED) ) and \
           ( self.miner2.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED) ) and \
           ( self.miner3.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED) ):

            return True

        return False

    def killMinersLazy(self, event=None):
        self.miner0.stopMiners()
        self.miner1.stopMiners()
        self.miner2.stopMiners()
        self.miner3.stopMiners()

    def rearrangeMiners(self, event=None, slide=False):
        try:
            width = self.GetSize()[0]
            best =  width / self.num_miners

            num_ready = sum(1 for miner in [self.miner0, self.miner1, self.miner2, self.miner3] if miner.minerStatus() != PMI.STATUS_DISABLED)
            #num_rinning = sum(1 for miner in [self.miner0, self.miner1, self.miner2, self.miner3] if miner.minerStatus() == PMI.STATUS_RUNNING)

            factor = 1.5
            factor = factor if num_ready == 0 else factor + ( float(num_ready * 1.5) / 10 )
            #factor = 1.5 if num_ready == 0 else 1.5 * ( 1 + ( self.num_miners - float(num_ready) - 1 ) / 10 )

            num_not_ready = self.num_miners - num_ready

            if num_ready == 0 or num_not_ready == 0:
                wide = narrow = best

            else:
                factored_num_ready = num_ready * factor

                factored_total = factored_num_ready + num_not_ready

                factor_ready = float(factored_num_ready) / factored_total
                factor_not_ready = float(num_not_ready) / factored_total

                wide = ( factor_ready * width ) / num_ready
                narrow = ( factor_not_ready * width ) / num_not_ready

            #no slide effect allowed for resize event triggered calls to the function for performance reasons.
            if not slide:
                self.SetSashPosition(0, int(wide if self.miner0.minerStatus() == PMI.STATUS_READY else narrow))
                self.SetSashPosition(1, int(wide if self.miner1.minerStatus() == PMI.STATUS_READY else narrow))
                self.SetSashPosition(2, int(wide if self.miner2.minerStatus() == PMI.STATUS_READY else narrow))
                self.SetSashPosition(3, int(wide if self.miner3.minerStatus() == PMI.STATUS_READY else narrow))

                return

            thread = threading.Thread(target=self.rearrangeMinersThread, args=(wide, narrow))
            thread.start()

        except AttributeError:
            pass

    def rearrangeMinersThread(self, wide, narrow):
        #with PanelMiners.lock:
        if self.resize_lock:
            time.sleep(0.5)

        if not self.resize_lock:
            self.resize_lock = True

            target0 = int(wide if self.miner0.minerStatus() == PMI.STATUS_READY else narrow)
            target1 = int(wide if self.miner1.minerStatus() == PMI.STATUS_READY else narrow)
            target2 = int(wide if self.miner2.minerStatus() == PMI.STATUS_READY else narrow)
            target3 = int(wide if self.miner3.minerStatus() == PMI.STATUS_READY else narrow)

            steps = 15

            for w in range (1, steps):
                #if self.resize_lock == False:
                #    break

                delta0 = target0 - self.GetSashPosition(0)
                delta1 = target1 - self.GetSashPosition(1)
                delta2 = target2 - self.GetSashPosition(2)
                delta3 = target3 - self.GetSashPosition(3)

                pct = float(w) / steps

                self.SetSashPosition(0, self.GetSashPosition(0) + pct * delta0)
                self.SetSashPosition(1, self.GetSashPosition(1) + pct * delta1)
                self.SetSashPosition(2, self.GetSashPosition(2) + pct * delta2)
                self.SetSashPosition(3, self.GetSashPosition(3) + pct * delta3)

                time.sleep(0.01)

            self.SetSashPosition(1, wide if self.miner1.minerStatus() == PMI.STATUS_READY else narrow )
            self.SetSashPosition(2, wide if self.miner2.minerStatus() == PMI.STATUS_READY else narrow )
            self.SetSashPosition(3, wide if self.miner3.minerStatus() == PMI.STATUS_READY else narrow )

            self.resize_lock = False