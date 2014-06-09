__author__ = 'Dario'

import threading
import urllib2
import json
import socket
import operator
import psutil
import subprocess
import time
import sys
import io
import os
import logging
import cPickle
import PanelConsole
import HTMLBuilder



SECONDS_PER_DAY = 86400

MODE_MAX_PER_DAY = 1
MODE_MAX_PER_WATT = 2
MODE_MAX_PER_HYBRID = 3

EXCHANGE_POLONIEX = "poloniex"
EXCHANGE_MINTPAL  = "mintpal"

scryptS  = " Scrypt "
groestlS = " Groestl"
skeinS   = " SKein  "
qubitS   = " Qubit  "

MINER_CHOICES = ["sgminer", "cgminer", "bfgminer", "reaper", "cudaminer", "minerd"]

MIN_TIME_THREAD_PROBED = 45
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

        self.hashtableMiners = {}
        self.configChangedFlag = False
        self.rebooting = rebooting
        self.resume = resume

        self.console = console
        self.htmlBuilder = None
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

        config_json = self.loadConfig(thread.activeConfigFile)
        self.htmlBuilder = HTMLBuilder.HTMLBuilder(self, config_json["sleepSHORT"] * 60000)

        first = True
        i=1

        logFileName = self.init(config_json)

        greaterThanHys = True
        greaterThanMin = True

        #watts = 0

        errors = 0
        num = 20.11656761

        #Init vars
        hashtableCorrected = None
        currentPrice       = None
        current            = None
        #effectiveRoundTime = None
        miner              = None
        switchtext         = None
        cpu1               = None
        globalStart        = None
        #globalTime         = 0
        lastStintStart     = None
        prevRoundStart     = None
        prevStintStart     = None
        scriptPath         = None
        prevRestartTime    = 0
        coinsStint         = 0
        wattsStint         = 0
        prevSwitchtext     = None
        globalStopped      = False
        wasStopped         = False
        stopReason         = None
        maxMinerFails      = False
        loopMinerStatus    = None
        breakAt            = None
        restart            = False
        self.globalTime    = 0

        while True:
            #if self.checkSwitchingThreadStopped():
            #    breakAt = "main loop init"
            #    break

            self.hashtableMiners = self.buildHashtableMiners(config_json)

            hashtableFactors = { scryptS : config_json["scryptFactor"], groestlS : config_json["groestlFactor"], skeinS : config_json["skeinFactor"], qubitS : config_json["qubitFactor"] }
            scryptFactor	= hashtableFactors[scryptS]
            groestlFactor	= hashtableFactors[groestlS]
            skeinFactor	    = hashtableFactors[skeinS]
            qubitFactor	    = hashtableFactors[qubitS]

            #getResult      = None
            #getResultCoins = None
            getResultPrice = None
            #priceOK        = None

            startT2 = time.time()

            try:
                getResult = self.httpGet("http://myriad.theblockexplorer.com/api.php?mode=info")

            except:
                self.htmlBuilder.pl("Something went wrong while retrieving the difficulties from the block chain explorer       :-(   ", HTMLBuilder.COLOR_RED)

                if self.checkSwitchingThreadStopped():
                    break
                else:
                    continue

            try:
                getResultCoins = self.httpGet("http://myriad.theblockexplorer.com/api.php?mode=coins")

            except:
                self.htmlBuilder.pl("Something went wrong while retrieving the block reward data from the block chain explorer  :-(   ", HTMLBuilder.COLOR_RED)

                if self.checkSwitchingThreadStopped():
                    break
                else:
                    continue

            try:
                if EXCHANGE_POLONIEX == config_json["exchange"]:
                    getResultPrice = self.httpGet("https://poloniex.com/public?command=returnTicker")

                if EXCHANGE_MINTPAL ==  config_json["exchange"]:
                    getResultPrice = self.httpGet("https://api.mintpal.com/v1/market/stats/MYR/BTC")

                priceOK = True

            except:
                #Write-Host "Something went wrong while retrieving the exchange rate data :-(                                                                                                                                                          " -foreground "white" -background "black"
                currentPrice = 0
                priceOK = False

            httpTime = time.time() - startT2

            #if self.checkSwitchingThreadStopped():
            #    breakAt = "post HTTP"
            #    break

            obj = json.loads(getResult)
            objCoins = json.loads(getResultCoins)

            diffScrypt 	= obj["difficulty_scrypt"]
            diffGroestl = obj["difficulty_groestl"]
            diffSkein 	= obj["difficulty_skein"]
            diffQubit 	= obj["difficulty_qubit"]

            per = objCoins["per"]

            scryptCorrFactor  = config_json["scryptHashRate"]  * num * int(per)
            groestlCorrFactor = config_json["groestlHashRate"] * num * int(per)
            skeinCorrFactor   = config_json["skeinHashRate"]  * num * int(per)
            qubitCorrFactor   = config_json["qubitHashRate"]   * num * int(per)

            previousPrice = currentPrice

            if priceOK:
                objPrice = json.loads(getResultPrice)

                if EXCHANGE_POLONIEX == config_json["exchange"]:
                    currentPrice = float(objPrice["BTC_MYR"]["last"]) * 100000000

                if EXCHANGE_MINTPAL == config_json["exchange"]:
                    currentPrice = float(objPrice[0]["last_price"]) * 100000000

            prevHashtableCorrected = hashtableCorrected

            if config_json["mode"] == MODE_MAX_PER_WATT:
                config_json["attenuation"] = 0

            hashtableWatts = { scryptS : config_json["scryptWatts"], groestlS : config_json["groestlWatts"], skeinS : config_json["skeinWatts"], qubitS : config_json["qubitWatts"] }
            attenuationWatts = self.getAverageHashValues(hashtableWatts) ** ((float(1) / 500))
            attenuationWatts = attenuationWatts ** config_json["attenuation"]
            hashtableWattsAttenuated = { scryptS : config_json["scryptWatts"] + attenuationWatts, groestlS : config_json["groestlWatts"] + attenuationWatts, skeinS : config_json["skeinWatts"] + attenuationWatts, qubitS : config_json["qubitWatts"] + attenuationWatts }

            hashtableRaw  = { scryptS : ((scryptCorrFactor / diffScrypt)), groestlS : ((groestlCorrFactor / diffGroestl)), skeinS : ((skeinCorrFactor / diffSkein)), qubitS : ((qubitCorrFactor / diffQubit)) }
            hashtableRawAttenuated  = { scryptS : ((scryptCorrFactor / diffScrypt) ) / ( hashtableWatts[scryptS] + attenuationWatts ), groestlS : ((groestlCorrFactor / diffGroestl) ) / ( hashtableWatts[groestlS] + attenuationWatts ), skeinS : ((skeinCorrFactor / diffSkein) ) / ( hashtableWatts[skeinS] + attenuationWatts ), qubitS : ((qubitCorrFactor / diffQubit) ) / ( hashtableWatts[qubitS] + attenuationWatts ) }
            hashtableFactored  = { scryptS : ((scryptCorrFactor / diffScrypt) * scryptFactor), groestlS : ((groestlCorrFactor / diffGroestl) * groestlFactor), skeinS : ((skeinCorrFactor / diffSkein) * skeinFactor), qubitS : ((qubitCorrFactor / diffQubit) * qubitFactor) }
            hashtablePerWatt   =          { scryptS : ((scryptCorrFactor / diffScrypt) * scryptFactor) / hashtableWatts[scryptS], groestlS : ((groestlCorrFactor / diffGroestl) * groestlFactor) / hashtableWatts[groestlS], skeinS : ((skeinCorrFactor / diffSkein) * skeinFactor) / hashtableWatts[skeinS], qubitS : ((qubitCorrFactor / diffQubit) * qubitFactor) / hashtableWatts[qubitS] }
            hashtablePerWattAttenuated  = { scryptS : ((scryptCorrFactor / diffScrypt) * scryptFactor) / ( hashtableWatts[scryptS] + attenuationWatts ), groestlS : ((groestlCorrFactor / diffGroestl) * groestlFactor) / ( hashtableWatts[groestlS] + attenuationWatts ), skeinS : ((skeinCorrFactor / diffSkein) * skeinFactor) / ( hashtableWatts[skeinS] + attenuationWatts ), qubitS : ((qubitCorrFactor / diffQubit) * qubitFactor) / ( hashtableWatts[qubitS] + attenuationWatts ) }
            hashtableCorrected = { scryptS : (scryptCorrFactor / diffScrypt), groestlS : (groestlCorrFactor / diffGroestl), skeinS : (skeinCorrFactor / diffSkein), qubitS : (qubitCorrFactor / diffQubit) }

            if self.noAlgoSelected(config_json):
                if config_json["mode"] == MODE_MAX_PER_DAY:
                    hashtable = hashtableRaw
                else:
                    hashtable = hashtableRawAttenuated
            else:
                if config_json["mode"] == MODE_MAX_PER_DAY:
                    hashtable = hashtableFactored
                else:
                    hashtable = hashtablePerWattAttenuated


            valArraySorted = sorted(hashtable.iteritems(), key=operator.itemgetter(1), reverse=True)

            maxAlgo  = valArraySorted[0][0]
            maxValue = valArraySorted[0][1]

            newVal  = maxValue

            if current:
                prevVal = hashtable[current]

                greaterThanHys = ( not prevVal ) or ( float(newVal) / float(prevVal) ) > config_json["hysteresis"]
                #$greaterThanMin = ( $timeStint -gt $minTimeNoHysteresis )
                greaterThanMin = ((time.time() - lastStintStart) / 60.0) > config_json["minTimeNoHysteresis"]

            # New Algo found to switch to!
            if (current != maxAlgo and ( greaterThanHys or greaterThanMin )) or self.checkSwitchingThreadStopped():
                if current:
                    prevAlgo = current

                else:
                    prevAlgo = maxAlgo

                current = maxAlgo
                miner = self.hashtableMiners[current] if current in self.hashtableMiners.keys() else None

                prevSwitchtext = switchtext

                if maxAlgo == scryptS:
                    switchtext = "> " + scryptS
                    scriptPath = config_json["scryptBatchFile"]

                elif maxAlgo == groestlS:
                    switchtext = "> " + groestlS
                    scriptPath = config_json["groestlBatchFile"]

                elif maxAlgo == skeinS:
                    switchtext = "> " + skeinS
                    scriptPath = config_json["skeinBatchFile"]

                elif maxAlgo == qubitS:
                    switchtext = "> " + qubitS
                    scriptPath = config_json["qubitBatchFile"]

                restart = not self.checkSwitchingThreadStopped()
                status = "SWITCH"

                errors = 0

            # Still same Algo, check if the miner is running OK
            else:
                prevAlgo = current
                switchtext = "   " + current

                cpu2 = self.getCPUUsages(miner)

                stopReason = loopMinerStatus if loopMinerStatus else self.minerStopped(cpu1, cpu2, miner, config_json)
                restart = not globalStopped and ( stopReason in (MINER_CRASHED, MINER_FREEZED) )

                cpu1 = cpu2

                if restart:
                    switchtext = "x " + current
                    status = "FAIL"
                    errors += 1

                    if errors >= config_json["maxErrors"]:
                        status = "MAX_FAIL"
                        prevSwitchtext = switchtext
                        maxMinerFails = True

                else:
                    switchtext = ". " + current
                    status = "OK"
                    errors = 0

            now = time.time()

            if first:
                lastStintStart = now
                globalStart = prevStintStart = prevRoundStart = lastStintStart
                prevHashtableCorrected = hashtableCorrected

            if status == "SWITCH":
                prevStintStart = lastStintStart
                lastStintStart = now

            self.globalTime = self.storedGlobalTime + ( now - globalStart )
            globalRoundTime = now - prevRoundStart
            globalStintTime = now - prevStintStart
            prevRoundStart = now

            prevValCorrected = prevHashtableCorrected[prevAlgo]

            nextValCorrected = hashtableCorrected[current]
            newValCorrected  = hashtableCorrected[prevAlgo]

            restartTime = 0

            if self.noAlgoSelected(config_json):
                globalStopped = True

            else:
                if config_json["mode"] == MODE_MAX_PER_DAY:
                    globalStopped = newValCorrected < config_json["minCoins"]

                else:
                    averageMinimumCoinsPerWatt = config_json["minCoins"] / self.getAverageHashValues(hashtableWattsAttenuated)
                    globalStopped = hashtablePerWattAttenuated[current] < averageMinimumCoinsPerWatt

            if globalStopped:
                self.killMiner(miner) if miner else self.killMiners()

                if status != "SWITCH":
                    status = "OK"

                switchtext = "S " + current

            if ( restart and not maxMinerFails and not globalStopped ) or ( wasStopped and not globalStopped ):
                sleepTime = config_json["sleepLONG"]

                t1 = time.time()

                if not config_json["debug"]:
                    self.killMiner(miner) if miner else self.killMiners()

                    workingDirectory = scriptPath[0:scriptPath.rfind("\\")]
                    retCode = subprocess.call('cd /d "' + workingDirectory.encode(sys.getfilesystemencoding()) + '" && start cmd /c "' + scriptPath.encode(sys.getfilesystemencoding()) + '"', shell=True)
                    #retCode = subprocess.Popen('cd /d "' + workingDirectory.encode(sys.getfilesystemencoding()) + '" && start cmd /c "' + scriptPath.encode(sys.getfilesystemencoding()) + '"', shell=True)
                    #subprocess.call('cd /d "' + unicode(workingDirectory) + '" && start cmd /c "' + unicode(scriptPath) + '"', shell=True)
                    #subprocess.call('cd /d "' + workingDirectory + '" && start cmd /c "' + scriptPath + '"', shell=True)

                    if retCode != 0:
                        self.htmlBuilder.pl()
                        self.htmlBuilder.pl("Failed to start your miner: " + scriptPath, HTMLBuilder.COLOR_RED)
                        breakAt = "failed miner start"
                        self.stop(True)
                        break

                    if self.waitForMinerToStart(miner, config_json["rampUptime"]):
                        cpu1 = self.getCPUUsages(miner)

                    #if self.checkSwitchingThreadStopped():
                    #    breakAt = "after miner start"
                    #    break

                restartTime = time.time() - t1

            else:
                sleepTime = config_json["sleepSHORT"]

            if not prevValCorrected:
                prevValCorrected = newValCorrected

            avgValCorrected = ( float(newValCorrected) + float(prevValCorrected) ) / 2.0

            effectiveRoundTime = 0 if wasStopped else globalRoundTime - prevRestartTime

            if status == "FAIL":
                timeStopped = LOOP_SLEEP_TIME if stopReason == MINER_CRASHED else MIN_TIME_THREAD_PROBED / 2.0
                effectiveRoundTime -= timeStopped

            effectiveRoundTime = max(effectiveRoundTime, 0)

            if maxMinerFails:
                coinsRound = 0

            else:
                timeRoundDays = effectiveRoundTime / SECONDS_PER_DAY

                #self.hashtableTime[prevAlgo] += effectiveRoundTime
                self.hashtableTime[prevAlgo] += globalRoundTime
                coinsRound = avgValCorrected * timeRoundDays

            coinsStint = coinsStint  + coinsRound

            totalCoinsPrev = self.hashtableCoins[prevAlgo] + coinsRound
            self.hashtableCoins[prevAlgo] = totalCoinsPrev

            if wasStopped and not first or (globalStopped and first):
                currentWatts = config_json["idleWatts"]

            else:
                currentWatts = hashtableWatts[prevAlgo]
                if status in ("FAIL", "MAX_FAIL"):
                    currentWatts = (currentWatts * (effectiveRoundTime / globalRoundTime)) + (config_json["idleWatts"] * ((globalRoundTime - effectiveRoundTime) / globalRoundTime))

            wattsRound = currentWatts * globalRoundTime
            wattsStint += wattsRound

            self.watts = self.watts + wattsRound

            totalCoins = sum(self.hashtableCoins.values())

            if (first and not self.resume) or self.globalTime == 0:
                wattsAvg = currentWatts
            else:
                wattsAvg = self.watts / self.globalTime

            # Prepare next round
            prevRestartTime = restartTime
            wasStopped = globalStopped

            if status == "SWITCH" or status == "MAX_FAIL":
                if not first:
                    avgStintWatts = wattsStint / globalStintTime
                    self.htmlBuilder.printData("SWITCH", now, globalStintTime, prevSwitchtext, previousPrice, currentPrice,
                                               newValCorrected, coinsStint, avgStintWatts, prevAlgo, globalStopped,
                                               self.hashtableCoins, hashtableCorrected, self.hashtableTime, config_json)

                self.htmlBuilder.printHeader()

                coinsStint = 0
                wattsStint = 0

                if status == "SWITCH":
                    status = "OK"


            self.htmlBuilder.printData(status, now, self.globalTime, switchtext, previousPrice, currentPrice,
                                       nextValCorrected, totalCoins, wattsAvg, current, globalStopped,
                                       self.hashtableCoins, hashtableCorrected, self.hashtableTime, config_json)

            #globalStart, wattsAvg, hashtableCoins, hashtableTime

            self.htmlBuilder.log(config_json, logFileName)

            if self.checkSwitchingThreadStopped():
                breakAt = "after prints, thread stopped"
                break

            if self.checkMaxFails(status, stopReason, config_json, logFileName):
                breakAt = "after prints, max fails"
                break

            first = False

            cpuF1 = cpu1
            loopMinerStatus = None

            t_initSleep = time.time()

            while (time.time() < (t_initSleep + sleepTime)) and not self.configChangedFlag:
                if self.checkSwitchingThreadStopped():
                    break

                if not globalStopped:
                    try:
                        cpuF2 = self.getCPUUsages(miner)

                        if self.minerCrashed(cpu1, cpuF2, miner, config_json):
                            loopMinerStatus = MINER_CRASHED
                            break

                        if (cpuF2[TIME_PROBED] - cpuF1[TIME_PROBED]) > MIN_TIME_THREAD_PROBED:
                            if self.minerFreezed(cpuF1, cpuF2, miner, config_json):
                                loopMinerStatus = MINER_FREEZED
                                break

                            else:
                                cpuF1 = cpuF2

                    except Exception, ex:
                        logging.exception("Loop error")

                #print time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), "In thread loop..... "
                time.sleep(LOOP_SLEEP_TIME)

            if self.configChangedFlag:
                t_initSleep = time.time()

            self.configChangedFlag = False

            config_json = self.loadConfig(thread.activeConfigFile)

        self.end(breakAt)

    def init(self, config_json):
        dataInitComplete = False

        if self.resume or self.rebooting:
            dataInitComplete = self.loadData()

        if not dataInitComplete:
            self.hashtableTime  = { scryptS : 0, groestlS : 0, skeinS : 0, qubitS : 0 }
            self.hashtableCoins = { scryptS : 0, groestlS : 0, skeinS : 0, qubitS : 0 }
            self.storedGlobalTime = 0
            self.watts = 0

            self.resume = False

        time_now = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        time_now_file = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
        self.fileSuffix  = time_now_file

        if self.resume or self.rebooting:
            self.htmlBuilder.pl()

        if config_json["debug"]:
            self.fileSuffix = "debug-" + self.fileSuffix

        logFileName = config_json["logPath"] + "\\" + self.fileSuffix + ".html"

        self.htmlBuilder.pl("Init time: " + time_now)

        if config_json["debug"]:
            self.htmlBuilder.pl()
            self.htmlBuilder.pl("########################################################################################################################", HTMLBuilder.COLOR_YELLOW)
            self.htmlBuilder.pl("#####################################             DEBUG     MODE           #############################################", HTMLBuilder.COLOR_YELLOW)
            self.htmlBuilder.pl("########################################################################################################################", HTMLBuilder.COLOR_YELLOW)

        return logFileName

    def end(self, breakAt):
        self.htmlBuilder.pl()
        self.htmlBuilder.pl("Process stopped at ... " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        self.dumpData()

        self.console.parent.onMiningProcessStopped()

        print time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), "Exiting thread loop..... "

    def configChanged(self):
        self.configChangedFlag = True

    def checkMaxFails(self, status, stopReason, config_json, logFileName):
        if status == "MAX_FAIL":
            if config_json["reboot"] and (config_json["rebootIf"] == MINER_CRASHED_OR_FREEZED or config_json["rebootIf"] == stopReason):
                self.htmlBuilder.pl()
                self.prepareReboot()
                self.htmlBuilder.pl(str(config_json["maxErrors"]) + " back to back miner " + stopReason + " ...rebooting!", HTMLBuilder.COLOR_RED)
                subprocess.call('shutdown /r')
                self.stop(True)

            else:
                self.htmlBuilder.pl()
                self.htmlBuilder.pl(str(config_json["maxErrors"]) + " back to back miner " + stopReason, HTMLBuilder.COLOR_RED)
                self.stop(True)

            self.htmlBuilder.log(config_json, logFileName)

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

    def noAlgoSelected(self, config_json):
        return not (config_json["scryptFactor"] or config_json["groestlFactor"] or config_json["skeinFactor"] or config_json["qubitFactor"])

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
        if self.hashtableMiners:
            for miner in MINER_CHOICES:
                self.killMiner(miner)

    def killMiner(self, miner):
        if self.hashtableMiners:
            for proc in psutil.process_iter():
                try:
                    proc.name()
                except:
                    continue

                if miner in proc.name():
                    proc.kill()

    def getAverageHashValues(self, dict_p):
        return sum(dict_p.values()) / float(len(dict_p))

    def httpGet(self, url):
        return urllib2.urlopen(url).read()

    def loadConfig(self, activeFile):
        f = None
        try:
            f = open(activeFile)
        except IOError:
            print "Config file not found: " + activeFile
            #return None

        config = f.read()
        f.close()

        config_json = json.loads(config)

        if config_json["debug"]:
            config_json["sleepSHORT"] = config_json["sleepSHORTDebug"]
            config_json["sleepLONG"]  = config_json["sleepLONGDebug"]
        else:
            config_json["sleepSHORT"] *= 60
            config_json["sleepLONG"]  *= 60

        self.refresh_t = str(config_json["sleepSHORT"] * 1000)

        config_json["hysteresis"] = (float(config_json["hysteresis"]) / 100.0) + 1
        config_json["globalCorrectionFactor"] = (float(config_json["globalCorrectionFactor"]) / 100.0)
        config_json["scryptHashRate"] = config_json["scryptHashRate"] * config_json["globalCorrectionFactor"]
        config_json["groestlHashRate"] = config_json["groestlHashRate"] * config_json["globalCorrectionFactor"]
        config_json["skeinHashRate"] = config_json["skeinHashRate"] * config_json["globalCorrectionFactor"]
        config_json["qubitHashRate"] = config_json["qubitHashRate"] * config_json["globalCorrectionFactor"]

        socket.setdefaulttimeout(config_json["timeout"])

        return config_json

    def buildHashtableMiners(self, config_json):
        hashtableMiners = {}

        try:
            if config_json["scryptBatchFile"]:
                hashtableMiners[scryptS] = self.fetchMiner(config_json["scryptBatchFile"])
        except:
            print ("WARNING: Failed to fetch miner for Scrypt. Myriad Switcher is now unable to monitor your Scrypt miner for crashes or freezes.")
            hashtableMiners[scryptS] = None

        try:
            if config_json["groestlBatchFile"]:
                hashtableMiners[groestlS] = self.fetchMiner(config_json["groestlBatchFile"])
        except:
            print ("WARNING: Failed to fetch miner for Groestl. Myriad Switcher is now unable to monitor your Groestl miner for crashes or freezes.")
            hashtableMiners[groestlS] = None

        try:
            if config_json["skeinBatchFile"]:
                hashtableMiners[skeinS] = self.fetchMiner(config_json["skeinBatchFile"])
        except:
            print ("WARNING: Failed to fetch miner for Skein. Myriad Switcher is now unable to monitor your Skein miner for crashes or freezes.")
            hashtableMiners[skeinS] = None

        try:
            if config_json["qubitBatchFile"]:
                hashtableMiners[qubitS] = self.fetchMiner(config_json["qubitBatchFile"])
        except:
            print ("WARNING: Failed to fetch miner for Qubit. Myriad Switcher is now unable to monitor your Qubit miner for crashes or freezes.")
            hashtableMiners[qubitS] = None

        #hashtableMiners[scryptS] = None
        #hashtableMiners[groestlS] = None
        #hashtableMiners[skeinS] = None
        #hashtableMiners[qubitS] = None

        return hashtableMiners

    def fetchMiner(self, file):
        f = open(file)
        contents = f.read()
        f.close()

        for miner in MINER_CHOICES:
            if (miner + ".exe") in contents or (".\\" + miner) in contents:
                return miner

        return None

    def loadData(self):
        try:
            obj = cPickle.load(open(PanelConsole.DATA_FILE_NAME, "rb" ))

            self.hashtableTime  = obj[0]
            self.hashtableCoins = obj[1]
            self.storedGlobalTime = obj[2]
            self.watts = obj[3]

            self.htmlBuilder.loadLines()

            return True

        except IOError:
            return False

    def dumpData(self):
        try:
            obj = [self.hashtableTime, self.hashtableCoins, self.globalTime, self.watts]
            cPickle.dump(obj, open(PanelConsole.DATA_FILE_NAME, "wb"))

            self.htmlBuilder.dumpLines()

        except IOError:
            pass

    def stop(self, kill_miners):
        #self.htmlBuilder.pl()
        #self.htmlBuilder.pl("Stopping... ")

        socket.setdefaulttimeout(5)

        if kill_miners:
            try:
                self.killMiner(miner) if miner else self.killMiners()
            except:
                print "Failed to kill miners"

        #self.console.parent.onMiningProcessStopped()
        self._stop.set()

    def isStopped(self):
        return self._stop.isSet()