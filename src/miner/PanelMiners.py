__author__ = 'Dario'

import wx
import time
import threading
import PanelMinerInstance as PMI
from wx._core import PyDeadObjectError
from wx.lib.splitter import MultiSplitterWindow


class PanelMiners(MultiSplitterWindow):
    lock = threading.RLock()

    def __init__(self, parent, frame, num_miners = 4):
        MultiSplitterWindow.__init__(self, parent=parent, id=wx.ID_ANY, style=wx.SP_LIVE_UPDATE)

        #self.parent = parent
        self.frame = frame
        self.resize_lock = False

        self.num_miners = num_miners

        self.miner0 = PMI.PanelMinerInstance(self, "Miner #0")
        self.miner1 = PMI.PanelMinerInstance(self, "Miner #1")
        self.miner2 = PMI.PanelMinerInstance(self, "Miner #2")
        self.miner3 = PMI.PanelMinerInstance(self, "Miner #3", isCollapse=True)
        self.SetOrientation(wx.HORIZONTAL)

        self.AppendWindow(self.miner0)
        self.AppendWindow(self.miner1)
        self.AppendWindow(self.miner2)
        self.AppendWindow(self.miner3)

        self.Bind(wx.EVT_SIZE, self.resizeMinerPanels)

    def executeAlgo(self, maxAlgo, switch):
        if switch:
            self.stopMiners()
        else:
            self.stopCrashedMiners()

        ret0 = self.miner0.executeAlgo(maxAlgo, switch)
        ret1 = self.miner1.executeAlgo(maxAlgo, switch)
        ret2 = self.miner2.executeAlgo(maxAlgo, switch)
        ret3 = self.miner3.executeAlgo(maxAlgo, switch)

        if (ret0 is None and ret1 is None and ret2 is None and ret3 is None):
            return None

        return ret0 or ret1 or ret2 or ret3

    def stopMiners(self, wait=False, exit=False):
        self.miner0.stopMiner(exit)
        self.miner1.stopMiner(exit)
        self.miner2.stopMiner(exit)
        self.miner3.stopMiner(exit)

        if exit:
            self.stopLoop(self.checkMinersExited)

        elif wait:
            self.stopLoop(self.checkMinersReady)

        self.frame.notebook.broadcastEventToAllTabs(event_id="stop_mining")

    def stopCrashedMiners(self):
        if self.miner0.minerStatus() == PMI.STATUS_CRASHED:
            self.miner0.stopMiner()

        if self.miner1.minerStatus() == PMI.STATUS_CRASHED:
            self.miner1.stopMiner()

        if self.miner2.minerStatus() == PMI.STATUS_CRASHED:
            self.miner2.stopMiner()

        if self.miner3.minerStatus() == PMI.STATUS_CRASHED:
            self.miner3.stopMiner()

    def stopLoop(self, endFunction):
        success = False
        i = 0
        str_ini = "Waiting for miners to die "

        from miner import PanelMinerInstance

        while i < PanelMinerInstance.MAX_ITERATIONS:
            if not endFunction():
                time.sleep(0.5)
                i += 1
                str_out = str_ini + str(i)
                print str_out

            else:
                str_out = "done, Bye!"
                print str_out
                #time.sleep(2)
                success = True
                break

        print "Miners: Exited with success = " + str(success)

        if not success:
            str_out = "Damn it"
            print str_out
            time.sleep(5)

    def checkMinerCrashed(self):
        if self.miner0.minerStatus() == PMI.STATUS_CRASHED or \
           self.miner1.minerStatus() == PMI.STATUS_CRASHED or \
           self.miner2.minerStatus() == PMI.STATUS_CRASHED or \
           self.miner3.minerStatus() == PMI.STATUS_CRASHED:

            return False

        return True

    def checkMinersReady(self):
        if ( self.miner0.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED, PMI.STATUS_EXITED, PMI.STATUS_EXITING ) ) and \
           ( self.miner1.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED, PMI.STATUS_EXITED, PMI.STATUS_EXITING ) ) and \
           ( self.miner2.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED, PMI.STATUS_EXITED, PMI.STATUS_EXITING ) ) and \
           ( self.miner3.minerStatus() in (PMI.STATUS_READY, PMI.STATUS_DISABLED, PMI.STATUS_CRASHED, PMI.STATUS_EXITED, PMI.STATUS_EXITING ) ):

            return True

        return False

    def checkMinersExited(self):
        if ( self.miner0.minerStatus() == PMI.STATUS_EXITED ) and \
           ( self.miner1.minerStatus() == PMI.STATUS_EXITED ) and \
           ( self.miner2.minerStatus() == PMI.STATUS_EXITED ) and \
           ( self.miner3.minerStatus() == PMI.STATUS_EXITED ):

            return True

        return False

    def checkMinersSelected(self):
        if ( self.miner0.minerStatus() == PMI.STATUS_DISABLED ) and \
           ( self.miner1.minerStatus() == PMI.STATUS_DISABLED ) and \
           ( self.miner2.minerStatus() == PMI.STATUS_DISABLED ) and \
           ( self.miner3.minerStatus() == PMI.STATUS_DISABLED ):

            return False

        return True

    def resizeMinerPanels(self, event=None, slide=False):
        try:
            width = self.GetSize()[0]
            best =  width / self.num_miners

            num_ready = sum(1 for miner in [self.miner0, self.miner1, self.miner2, self.miner3] if miner.minerStatus() is not PMI.STATUS_DISABLED)
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
                self.SetSashPosition(0, int(wide if self.miner0.minerStatus() != PMI.STATUS_DISABLED else narrow))
                self.SetSashPosition(1, int(wide if self.miner1.minerStatus() != PMI.STATUS_DISABLED else narrow))
                self.SetSashPosition(2, int(wide if self.miner2.minerStatus() != PMI.STATUS_DISABLED else narrow))
                self.SetSashPosition(3, int(wide if self.miner3.minerStatus() != PMI.STATUS_DISABLED else narrow))

                return

            thread = threading.Thread(target=self.resizeMinerPanelsThread, args=(wide, narrow))
            thread.start()

        except (PyDeadObjectError, AttributeError):
            pass

    def resizeMinerPanelsThread(self, wide, narrow):
        try:
            #with PanelMiners.lock:
            if self.resize_lock:
                time.sleep(0.5)

            if not self.resize_lock:
                self.resize_lock = True

                target0 = int(wide if self.miner0.minerStatus() != PMI.STATUS_DISABLED else narrow)
                target1 = int(wide if self.miner1.minerStatus() != PMI.STATUS_DISABLED else narrow)
                target2 = int(wide if self.miner2.minerStatus() != PMI.STATUS_DISABLED else narrow)
                target3 = int(wide if self.miner3.minerStatus() != PMI.STATUS_DISABLED else narrow)

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

                self.resize_lock = False

        except PyDeadObjectError:
            pass

    def setButtonExpanded(self, expanded):
        self.miner3.handler.setButtonExpanded(expanded)

    def getExpansionStatus(self):
        return self.miner3.handler.collapseBtn.GetValue()