__author__ = 'Dario'

from console import HTMLBuilder
import SwitcherData
from ErrorReport import ErrorReport

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


MIN_TIME_THREAD_PROBED = 60
CPU_TIME    = 0
TIME_PROBED = 1
LOOP_SLEEP_TIME = 2

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

        self.console.parent.onMiningProcessStarted()

        switcherData = SwitcherData.SwitcherData(self.console, thread.activeConfigFile)
        #config_json = self.loadConfig(thread.activeConfigFile)

        if self.resume or self.rebooting:
            switcherData.loadData()

        errors = 0

        #Init vars
        switchtext         = None
        cpu1               = None
        scriptPath         = None
        prevSwitchtext     = None
        globalStopped      = True
        wasStopped         = False
        stopReason         = None
        maxMinerFails      = False
        loopMinerStatus    = None

        while True:
            try:
                dataError = switcherData.fetchData(thread.activeConfigFile)

                threadStopped = self.checkSwitchingThreadStopped()

                if dataError:
                    switcherData.pl(dataError, HTMLBuilder.COLOR_RED)

                    if threadStopped:
                        break
                    else:
                        loopMinerStatus = self.waitLoop(cpu1, switcherData.config_json["sleepSHORT"], globalStopped, switcherData)
                        continue

                # New Algo found to switch to!
                if switcherData.isSwitchToNewAlgo(threadStopped):
                    prevSwitchtext = switchtext

                    scriptPath = switcherData.getScriptPath()
                    switchtext = "> " + switcherData.maxAlgo

                    restart = not threadStopped
                    status = "SWITCH"

                    errors = 0

                # Still same Algo, check if the miner is running OK
                else:
                    switchtext = "   " + switcherData.current

                    cpu2 = self.getCPUUsages(switcherData.getMiner())

                    stopReason = loopMinerStatus if loopMinerStatus else self.minerStopped(cpu1, cpu2, switcherData.getMiner(), switcherData.config_json)
                    restart = not globalStopped and ( stopReason in (MINER_CRASHED, MINER_FREEZED) )

                    cpu1 = cpu2

                    if restart:
                        switchtext = "x " + switcherData.current
                        status = "FAIL"
                        errors += 1

                        if errors >= switcherData.config_json["maxErrors"]:
                            status = "MAX_FAIL"
                            prevSwitchtext = switchtext
                            maxMinerFails = True

                    else:
                        switchtext = ". " + switcherData.current
                        status = "OK"
                        errors = 0

                switcherData.initRound(status)

                globalStopped = switcherData.globalStopped
                wasStopped    = switcherData.wasStopped

                if globalStopped:
                    self.killMiner(self.activeMiner) if self.activeMiner else self.killMiners()

                    if status != "SWITCH":
                        status = "OK"

                    switchtext = "S " + switcherData.current

                if ( restart and not maxMinerFails and not globalStopped ) or ( wasStopped and not globalStopped ):
                    sleepTime = switcherData.config_json["sleepLONG"]

                    t1 = time.time()

                    if not switcherData.config_json["debug"]:
                        self.killMiner(self.activeMiner) if self.activeMiner else self.killMiners()

                        workingDirectory = scriptPath[0:scriptPath.rfind("\\")]
                        retCode = subprocess.call('cd /d "' + workingDirectory.encode(sys.getfilesystemencoding()) + '" && start cmd /c "' + scriptPath.encode(sys.getfilesystemencoding()) + '"', shell=True)
                        #retCode = subprocess.Popen('cd /d "' + workingDirectory.encode(sys.getfilesystemencoding()) + '" && start cmd /c "' + scriptPath.encode(sys.getfilesystemencoding()) + '"', shell=True)
                        #subprocess.call('cd /d "' + unicode(workingDirectory) + '" && start cmd /c "' + unicode(scriptPath) + '"', shell=True)
                        #subprocess.call('cd /d "' + workingDirectory + '" && start cmd /c "' + scriptPath + '"', shell=True)

                        if retCode != 0:
                            switcherData.pl()
                            switcherData.pl("Failed to start your miner: " + scriptPath, HTMLBuilder.COLOR_RED)
                            breakAt = "failed miner start"
                            self.stop(True)
                            break

                        if self.waitForMinerToStart(switcherData.getMiner(), switcherData.config_json["rampUptime"]):
                            cpu1 = self.getCPUUsages(switcherData.getMiner())
                            self.activeMiner = switcherData.getMiner()

                            #if self.checkSwitchingThreadStopped():
                            #    breakAt = "after miner start"
                            #    break

                    restartTime = time.time() - t1

                else:
                    sleepTime = switcherData.config_json["sleepSHORT"]

                timeStopped = 0 if status != "FAIL" else LOOP_SLEEP_TIME if stopReason == MINER_CRASHED else MIN_TIME_THREAD_PROBED / 2.0

                switcherData.executeRound(status, timeStopped, maxMinerFails, self.resume, prevSwitchtext, switchtext)

                if self.checkSwitchingThreadStopped():
                    breakAt = "after prints, thread stopped"
                    break

                if self.checkMaxFails(status, stopReason, switcherData):
                    breakAt = "after prints, max fails"
                    break

                loopMinerStatus = self.waitLoop(cpu1, sleepTime, globalStopped, switcherData)

                switcherData.loadConfig(thread.activeConfigFile)

            except Exception:
                switcherData.pl()
                switcherData.pl("Unexpected error.", HTMLBuilder.COLOR_RED)

                self.printTraceback("Unexpected error")

                ErrorReport().sendReport(self.console, traceback.format_exc())

                break

        switcherData.end()
        self.console.parent.onMiningProcessStopped()

    def waitLoop(self, cpu1, sleepTime, globalStopped, switcherData):
        cpuF1 = cpu1
        t_initSleep = time.time()

        while (time.time() < (t_initSleep + sleepTime)) and not self.configChangedFlag:
            if self.checkSwitchingThreadStopped():
                return None

            if not globalStopped and switcherData.config_json["monitor"]:
                try:
                    cpuF2 = self.getCPUUsages(switcherData.getMiner())

                    if self.minerCrashed(cpu1, cpuF2, switcherData.getMiner(), switcherData.config_json):
                        return MINER_CRASHED

                    if (cpuF2[TIME_PROBED] - cpuF1[TIME_PROBED]) > MIN_TIME_THREAD_PROBED:
                        if self.minerFreezed(cpuF1, cpuF2, switcherData.getMiner(), switcherData.config_json):
                            return MINER_FREEZED

                        else:
                            cpuF1 = cpuF2

                except Exception, ex:
                    logging.exception("Loop error")

            #print time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), "In thread loop..... "
            time.sleep(LOOP_SLEEP_TIME)

        if self.configChangedFlag:
            t_initSleep = time.time()

        self.configChangedFlag = False

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

        if miner is None:
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

    def checkSwitchingThreadStopped(self):
        return self.isStopped()

    def waitForMinerToStart(self, miner, ramp_up_time):
        if miner is None:
            return False

        numThreadsPrev = 0
        i=0

        while not numThreadsPrev and i < 60:
            time.sleep(1)
            cpu1 = self.getCPUUsages(miner)
            numThreadsPrev = len(cpu1)

            time.sleep(ramp_up_time)

        return not(i == 60)

    # Returns None if the miner is running, or MINER_DIED or MINER_FREEZED
    def minerStopped(self, cpu1, cpu2, miner, config_json):
        crashed = self.minerCrashed(cpu1, cpu2, miner, config_json)
        if crashed:
            return crashed
        else:
            return self.minerFreezed(cpu1, cpu2, miner, config_json)

    # Returns None if the miner is running, or MINER_CRASHED
    def minerCrashed(self, cpu1, cpu2, miner, config_json):
        if miner is None:
            return None

        if config_json["debug"] or not config_json["monitor"]:
            return None

        if (cpu2 is None or cpu2[CPU_TIME] is None or len(cpu2[CPU_TIME]) == 0):
            return MINER_CRASHED

        if (cpu1 is None or cpu1[CPU_TIME] is None or len(cpu1[CPU_TIME]) == 0):
            return None

        if cpu2[CPU_TIME] is None or len(cpu2[CPU_TIME]) == 0:
            return MINER_CRASHED

        # Same number of instances runing?
        numThreadsPrev = len(cpu1[CPU_TIME])
        numThreadsNew = len(cpu2[CPU_TIME])

        if numThreadsNew < numThreadsPrev:
            return MINER_CRASHED

        return None

    # Returns None if the miner is running, or MINER_FREEZED
    def minerFreezed(self, cpu1, cpu2, miner, config_json):
        if miner is None:
            return None

        if config_json["debug"] or not config_json["monitor"]:
            return None

        if (cpu2[TIME_PROBED] - cpu1[TIME_PROBED]) < MIN_TIME_THREAD_PROBED:
            return None

        if (cpu1[CPU_TIME] is None or len(cpu1[CPU_TIME]) == 0):
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
        traceback.print_stack()

    # Returns MINER_CRASHED or MINER_FREEZED if the miner is not running, or the CPU usage/timestamp if it is
    def minerStoppedFinal(self, cpu1, miner, config_json):
        cpu2 = self.getCPUUsages(miner)
        minerStatus = self.minerStopped(cpu1, cpu2, miner, config_json)

        if minerStatus in (MINER_CRASHED, MINER_FREEZED):
            return minerStatus
        else:
            return cpu2

    # Returns True if not enough time has passed between CPU usage samples to check if the miner is stopped
    #def belowTimeBetweenCPUSamplesThreshold(self, cpu1, cpu2):
    #    #init_ref_time = cpu1[TIME_PROBED] if ref_time is None else ref_time
    #    time_between_probes = cpu2[TIME_PROBED] - cpu1[TIME_PROBED]
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

    def stop(self, kill_miners):
        #self.htmlBuilder.pl()
        #self.htmlBuilder.pl("Stopping... ")

        socket.setdefaulttimeout(5)

        if kill_miners:
            try:
                self.killMiner(self.activeMiner) if self.activeMiner else self.killMiners()
            except:
                print "Failed to kill miners"

        #self.console.parent.onMiningProcessStopped()
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()