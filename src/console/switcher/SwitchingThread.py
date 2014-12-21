__author__ = 'Dario'

import threading
import psutil
import subprocess
import time
import sys
import io
import os
import logging
import socket
import traceback
from console.switcher.ErrorReport import ErrorReport
from console.switcher import HTMLBuilder, SwitcherData


MIN_TIME_THREAD_PROBED = 60
CPU_TIME               = 0
TIME_PROBED            = 1
LOOP_SLEEP_TIME        = 5

MINER_CRASHED = "crashes"
MINER_FREEZED = "freezes"
MINER_CRASHED_OR_FREEZED = "crashes or freezes"


class SwitchingThread (threading.Thread):
    def __init__(self, name, counter, console, rebooting, resume):
        super(SwitchingThread, self).__init__()
        self._stop = threading.Event()

        self.configChangedFlag = False
        self.rebooting = rebooting
        self.resume = resume
        self.activeMiner = None
        self.switcherData = None

        self.console = console
        threading.Thread.__init__(self)
        self.name = name
        self.counter = counter

        self.line  = str()
        self.lines = []

    def setActiveConfigFile(self, activeConfigFile):
        self.activeConfigFile = activeConfigFile

    def run(self):
        #print "Starting thread " + self.name + " PID = " + str(self.ident) + " - counter = " + str(self.counter)
        self.mine_threaded(self)

    def mine_threaded(self, thread):
        if self.rebooting:
            time.sleep(30)

        self.console.onMiningProcessStarted()

        self.switcherData = SwitcherData.SwitcherData(self.console, thread.activeConfigFile)

        if self.resume or self.rebooting:
            self.switcherData.loadData()

        errors = 0

        #Init vars
        self.mainMode      = None
        switchtext         = None
        self.cpu1          = None
        self.cpu2          = None
        self.cpuF1         = None
        self.cpuF2         = None
        prevScriptPath     = None
        scriptPath         = None
        prevSwitchtext     = None
        globalStopped      = True
        wasStopped         = False
        stopReason         = None
        maxMinerFails      = False
        loopMinerStatus    = None

        while True:
            try:
                dataError = self.switcherData.fetchData(thread.activeConfigFile)
                self.mainMode = self.switcherData.config_json["mainMode"]

                threadStopped = self.isStopped()

                if dataError:
                    self.switcherData.pl(dataError, HTMLBuilder.COLOR_RED)

                    if threadStopped:
                        break
                    else:
                        loopMinerStatus = self.waitLoop(self.switcherData.config_json["sleepSHORT"], globalStopped, self.switcherData)
                        continue

                # New Algo found to switch to!
                if self.switcherData.isSwitchToNewAlgo(threadStopped):
                    prevSwitchtext = switchtext

                    scriptPath = self.switcherData.getScriptPath()
                    switchtext = "> " + self.switcherData.maxAlgo

                    restart = not threadStopped
                    status = "SWITCH"

                    errors = 0

                # Still same Algo, check if the miner is running OK
                else:
                    switchtext = "   " + self.switcherData.current

                    self.cpu2 = self.getCPUUsages(self.switcherData.getMiner())

                    #if not globalStopped or self.mainMode == "simple":
                    stopReason = loopMinerStatus if loopMinerStatus else self.minerStopped(self.cpu1, self.cpu2, self.switcherData.getMiner(), self.switcherData.config_json)

                    restart = ( not globalStopped or self.mainMode == "simple" ) and ( stopReason in (MINER_CRASHED, MINER_FREEZED) )

                    self.cpu1 = self.cpu2

                    if restart:
                        switchtext = "x " + self.switcherData.current
                        status = "FAIL"
                        errors += 1

                        if errors >= self.switcherData.config_json["maxErrors"]:
                            status = "MAX_FAIL"
                            prevSwitchtext = switchtext
                            maxMinerFails = True

                    else:
                        switchtext = ". " + self.switcherData.current
                        status = "OK"
                        errors = 0

                self.switcherData.initRound(status)

                globalStopped = self.switcherData.globalStopped
                wasStopped    = self.switcherData.wasStopped

                prevScriptPath = scriptPath

                if globalStopped:
                    self.kill()

                    if status != "SWITCH":
                        status = "OK"

                    switchtext = "S " + self.switcherData.current

                if self.checkRestart(prevScriptPath, scriptPath, restart, maxMinerFails, globalStopped, wasStopped):
                    sleepTime = self.switcherData.config_json["sleepLONG"]

                    t1 = time.time()

                    if not self.switcherData.config_json["debug"]:
                        if self.mainMode == "advanced":
                            self.kill()

                        retCode = self.startMiners(scriptPath, self.switcherData.maxAlgo, restart, status == "SWITCH")

                        #retCode = subprocess.Popen('cd /d "' + workingDirectory.encode(sys.getfilesystemencoding()) + '" && start cmd /c "' + scriptPath.encode(sys.getfilesystemencoding()) + '"', shell=True)
                        #subprocess.call('cd /d "' + unicode(workingDirectory) + '" && start cmd /c "' + unicode(scriptPath) + '"', shell=True)
                        #subprocess.call('cd /d "' + workingDirectory + '" && start cmd /c "' + scriptPath + '"', shell=True)

                        if retCode is None:
                            #switcherData.pl()
                            #switcherData.pl("Please, select a mining device first!: " + scriptPath, HTMLBuilder.COLOR_RED)

                            #question = "Please, select a mining device in the lower panel to start mining."
                            #dlg = wx.MessageDialog(self.console, question, "Unable to start your mining session...", wx.OK)
                            #dlg.ShowModal()
                            #dlg.Destroy()

                            self.switcherData.pl()
                            self.switcherData.pl("Failed to start your miner(s): " + scriptPath, HTMLBuilder.COLOR_RED)

                            breakAt = "No mining device set"
                            self.stop(True)
                            break

                        if not retCode:
                            self.switcherData.pl()
                            self.switcherData.pl("Failed to start your miner(s): " + scriptPath, HTMLBuilder.COLOR_RED)
                            breakAt = "failed miner start"
                            self.stop(True)
                            break

                        if self.waitForMinerToStart(self.switcherData.getMiner(), self.switcherData.config_json["rampUptime"]):
                            self.cpu1 = self.getCPUUsages(self.switcherData.getMiner())
                            self.activeMiner = self.switcherData.getMiner()

                            #if self.checkSwitchingThreadStopped():
                            #    breakAt = "after miner start"
                            #    break

                    restartTime = time.time() - t1

                else:
                    sleepTime = self.switcherData.config_json["sleepSHORT"]

                timeStopped = 0 if status != "FAIL" else LOOP_SLEEP_TIME if stopReason == MINER_CRASHED else MIN_TIME_THREAD_PROBED / 2.0

                self.switcherData.executeRound(status, timeStopped, maxMinerFails, self.resume, prevSwitchtext, switchtext)

                if self.isStopped():
                    breakAt = "after prints, thread stopped"
                    self.stop(True)
                    break

                if self.checkMaxFails(status, stopReason, self.switcherData):
                    breakAt = "after prints, max fails"
                    self.stop(True)
                    break

                loopMinerStatus = self.waitLoop(sleepTime, globalStopped, self.switcherData)

                self.switcherData.loadConfig(thread.activeConfigFile)

            except Exception as ex:
                self.switcherData.pl()
                self.switcherData.pl("Unexpected error.", HTMLBuilder.COLOR_RED)
                self.switcherData.pl()
                for line in traceback.format_exc().split('\n'):
                    self.switcherData.pl(line, HTMLBuilder.COLOR_RED)

                self.printTraceback("Unexpected error")

                ErrorReport().sendReport(self.console, traceback.format_exc())

                break

        self.switcherData.end()
        self.console.onMiningProcessStopped()

    def checkRestart(self, prevScriptPath, scriptPath, restart, maxMinerFails, globalStopped, wasStopped):
        return ( restart and not maxMinerFails and not globalStopped ) or \
               ( wasStopped and not globalStopped ) or \
               self.scriptChanged(prevScriptPath, scriptPath, restart, globalStopped)

    def scriptChanged(self, prevScriptPath, scriptPath, restart, globalStopped):
        return not restart and not globalStopped and ( prevScriptPath and scriptPath and (prevScriptPath != scriptPath) )

    def waitLoop(self, sleepTime, globalStopped, switcherData):
        self.cpuF1 = self.cpu1
        t_initSleep = time.time()

        while (time.time() < (t_initSleep + sleepTime)) and not self.configChangedFlag:
            if self.isStopped():
                return None

            ret = self.checkMinersInLoop(globalStopped, switcherData)
            if ret:
                return ret

            #print time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), "In thread loop..... "
            time.sleep(LOOP_SLEEP_TIME)

        if self.configChangedFlag:
            t_initSleep = time.time()

        self.configChangedFlag = False

    def checkMinersInLoop(self, globalStopped, switcherData):
        if self.mainMode == "advanced":
            if not globalStopped and switcherData.config_json["monitor"]:
                try:
                    self.cpuF2 = self.getCPUUsages(switcherData.getMiner())

                    if self.minerCrashed(self.cpu1, self.cpuF2, switcherData.getMiner(), switcherData.config_json):
                        return MINER_CRASHED

                    if (self.cpuF2[TIME_PROBED] - self.cpuF1[TIME_PROBED]) > MIN_TIME_THREAD_PROBED:
                        if self.minerFreezed(self.cpuF1, self.cpuF2, switcherData.getMiner(), switcherData.config_json):
                            return MINER_FREEZED

                        else:
                            self.cpuF1 = self.cpuF2

                except Exception, ex:
                    logging.exception("Loop error")

        else:
            return None if self.console.frame_myr.checkMinerCrashed() else MINER_CRASHED

    def startMiners(self, scriptPath, maxAlgo, restart, switch):
        retCode = None

        if "advanced" == self.mainMode:
            workingDirectory = scriptPath[0:scriptPath.rfind("\\")]
            retCode = subprocess.call('cd /d "' + workingDirectory.encode(sys.getfilesystemencoding()) + '" && start cmd /c "' + scriptPath.encode(sys.getfilesystemencoding()) + '"', shell=True)

            return not retCode

        else:
            # Not restart because in the switching thread context "restart" means "restart crashed miners"
            # while in the miner panels "restart" in execute means restart even if already running.
            # What we want here is to only have the crashed miners restarted. We use restart = true when switching algos
            # to restart all of the miners to run the new algo
            retCode = self.console.frame_myr.executeAlgo(maxAlgo, switch)

        return retCode

    def configChanged(self):
        self.configChangedFlag = True

    def checkMaxFails(self, status, stopReason, switcherData):
        if status == "MAX_FAIL":
            if switcherData.config_json["reboot"] and (switcherData.config_json["rebootIf"] == MINER_CRASHED_OR_FREEZED or switcherData.config_json["rebootIf"] == stopReason):
                switcherData.pl()
                self.prepareReboot()
                switcherData.pl(str(switcherData.config_json["maxErrors"]) + " back to back miner " + stopReason + " ...rebooting!", HTMLBuilder.COLOR_RED)
                subprocess.call('shutdown /r')
                self.stop(True)

            else:
                switcherData.pl()
                switcherData.pl(str(switcherData.config_json["maxErrors"]) + " back to back miner " + stopReason, HTMLBuilder.COLOR_RED)
                self.stop(True)

            switcherData.log()

            return True

        return False

    def getCPUUsages(self, miner):
        cpu = {}
        timeCPUProbed = None

        if not miner:
            return cpu

        for proc in psutil.process_iter():
            try:
                proc.name()
            except:
                continue

            if miner in proc.name():
                cpu[proc.pid] = proc.get_cpu_times().user
                timeCPUProbed = time.time()

        return (cpu, timeCPUProbed)

    #def checkSwitchingThreadStopped(self):
    #    return self.isStopped()

    def waitForMinerToStart(self, miner, ramp_up_time):
        if not miner:
            return False

        numThreadsPrev = 0
        i=0

        while not numThreadsPrev and i < 60:
            time.sleep(1)
            self.cpu1 = self.getCPUUsages(miner)
            numThreadsPrev = len(self.cpu1)

            time.sleep(ramp_up_time)

        return not(i == 60)

    # Returns None if the miner is running, or MINER_DIED or MINER_FREEZED
    def minerStopped(self, cpu1, cpu2, miner, config_json):
        if self.mainMode == "advanced":
            crashed = self.minerCrashed(cpu1, cpu2, miner, config_json)
            if crashed:
                return crashed
            else:
                return self.minerFreezed(cpu1, cpu2, miner, config_json)

        else:
            return None if self.console.frame_myr.checkMinerCrashed() else MINER_CRASHED

    # Returns None if the miner is running, or MINER_CRASHED
    def minerCrashed(self, cpu1, cpu2, miner, config_json):
        if not miner:
            return None

        if config_json["debug"] or not config_json["monitor"]:
            return None

        if not cpu2:
            return None

        if (not cpu2[CPU_TIME] or len(cpu2[CPU_TIME]) == 0):
            return MINER_CRASHED

        if (not cpu1 or not cpu1[CPU_TIME] or len(cpu1[CPU_TIME]) == 0):
            return None

        if not cpu2[CPU_TIME] or len(cpu2[CPU_TIME]) == 0:
            return MINER_CRASHED

        # Same number of instances runing?
        numThreadsPrev = len(cpu1[CPU_TIME])
        numThreadsNew = len(cpu2[CPU_TIME])

        if numThreadsNew < numThreadsPrev:
            return MINER_CRASHED

        return None

    # Returns None if the miner is running, or MINER_FREEZED
    def minerFreezed(self, cpu1, cpu2, miner, config_json):
        if not miner:
            return None

        if config_json["debug"] or not config_json["monitor"]:
            return None

        if not cpu1 or not cpu2:
            return None

        if (cpu2[TIME_PROBED] - cpu1[TIME_PROBED]) < MIN_TIME_THREAD_PROBED:
            return None

        if (not cpu1[CPU_TIME] or len(cpu1[CPU_TIME]) == 0):
            return None

        # Any CPU usage?
        for pid in cpu1[CPU_TIME]:
            try:
                if cpu1[CPU_TIME][pid] == cpu2[CPU_TIME][pid]:
                    return MINER_FREEZED
            except KeyError:
                return None

        return None

    def printTraceback(self, text):
        print time.strftime(SwitcherData.DATE_FORMAT_PATTERN, time.localtime()) + " - " + text
        print traceback.format_exc()
        #traceback.print_stack()

    # Returns MINER_CRASHED or MINER_FREEZED if the miner is not running, or the CPU usage/timestamp if it is
    def minerStoppedFinal(self, cpu1, miner, config_json):
        cpu2 = self.getCPUUsages(miner)
        minerStatus = self.minerStopped(cpu1, cpu2, miner, config_json)

        if minerStatus in (MINER_CRASHED, MINER_FREEZED):
            return minerStatus
        else:
            return cpu2

    # Returns True if not enough time has passed between CPU usage samples to check if the miner is stopped
    #def belowTimeBetweenCPUSamplesThreshold(self, self.cpu1, self.cpu2):
    #    #init_ref_time = self.cpu1[TIME_PROBED] if ref_time is None else ref_time
    #    time_between_probes = self.cpu2[TIME_PROBED] - self.cpu1[TIME_PROBED]
    #
    #    return (time_between_probes) < MIN_TIME_THREAD_PROBED

    def prepareReboot(self):
        io.open("reboot", 'wt').write("reboot=" + unicode(time.time()))

        if os.name == "nt":
            import win32com.client

            ws = win32com.client.Dispatch("wscript.shell")
            scut = ws.CreateShortcut(os.getenv('APPDATA') + '\\Microsoft\Windows\Start Menu\Programs\Startup\\myriadSwitcher.lnk')
            #self.htmlBuilder.pl(os.getcwd())
            scut.TargetPath = '"' + (os.getcwd() + '\\MyriadSwitcherGUI.exe"')
            scut.WorkingDirectory = os.getcwd()
            scut.Save()

        if os.name == "posix":
            pass

    def kill(self):
        if self.mainMode == "advanced":
            self.killMiner(self.activeMiner) if self.activeMiner else self.killMiners()
        else:
            self.console.frame_myr.stopMiners()

    def killMiners(self):
        for miner in SwitcherData.MINER_CHOICES:
            self.killMiner(miner)

    def killMiner(self, miner):
        for proc in psutil.process_iter():
            try:
                proc.name()
            except:
                continue

            if miner in proc.name():
                proc.kill()

    def stop(self, kill_miners=False):
        #self.htmlBuilder.pl()
        #self.htmlBuilder.pl("Stopping... ")

        socket.setdefaulttimeout(5)

        if kill_miners:
            try:
                #if self.mainMode == "advanced":
                self.kill()
            except:
                print "Failed to kill miners"

        #self.console.parent.onMiningProcessStopped()
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()