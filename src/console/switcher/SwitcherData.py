__author__ = 'Dario'

import time
import json
import operator
import socket
import urllib2
import cPickle

import HTMLBuilder
import difficulty.Difficulties as Difficulties


SECONDS_PER_DAY = 86400

scryptS  = " Scrypt "
groestlS = " Groestl"
skeinS   = " Skein  "
qubitS   = " Qubit  "

MINER_CHOICES = ["sgminer",
                 "cgminer",
                 "bfgminer",
                 "reaper",
                 "reaper_cpuonly",
                 "cudaminer",
                 "minerd",
                 "vertminer",
                 "ScryptGPU",
                 "ScryptCPU64",
                 "skeingpu",
                 "SkeinCPU64",
                 "GroestlGPU",
                 "GroestlCPU64",
                 "QubitGPU",
                 "QubitCPU64"]

EXCHANGE_POLONIEX = "poloniex"
EXCHANGE_CRYPTSY  = "cryptsy"
exchangesURL = {EXCHANGE_POLONIEX: "https://poloniex.com/public?command=returnTicker", EXCHANGE_CRYPTSY: "http://pubapi2.cryptsy.com/api.php?method=singlemarketdata&marketid=200"}

MODE_MAX_PER_DAY = 1
MODE_MAX_PER_WATT = 2
MODE_MAX_PER_HYBRID = 3

num = 20.11656761

CURRENT_BLOCK_REWARD = 1000

DATA_FILE_NAME = "m_s_data.myr"

DATE_FORMAT_PATTERN = "%m/%d/%Y %H:%M:%S"
LOG_FORMAT_PATTERN = "%y.%m.%d.%H%M%S"


class SwitcherData():
    def __init__(self, console, activeFile):
        self.current                            = None
        self.first                              = True
        self.currentPrice                       = None
        self.hashtableCorrected                 = None
        self.hashtableMinedCoins                = {}
        self.hashtablePreviousStintMinedCoins   = None
        self.wasStopped                         = False
        self.prevRestartTime                    = 0
        self.coinsStint                         = 0
        self.wattsStint                         = 0
        self.storedGlobalTime                   = 0
        self.watts                              = 0
        self.config_json                        = None

        self.hashtableTime  = { scryptS : 0, groestlS : 0, skeinS : 0, qubitS : 0 }
        self.hashtableExpectedCoins = { scryptS : 0, groestlS : 0, skeinS : 0, qubitS : 0 }

        self.console = console

        self.difficulties = Difficulties.Difficulties(self)

        self.config_json = self.loadConfig(activeFile)

        self.htmlBuilder = HTMLBuilder.HTMLBuilder(self.console, self.config_json["sleepSHORT"] * 1000)
        #self.htmlBuilder.addHTMLEventListener(self.console.onConsoleEvent)

        time_now = time.strftime(DATE_FORMAT_PATTERN, time.localtime())
        time_now_file = time.strftime(LOG_FORMAT_PATTERN, time.localtime())
        self.fileSuffix  = time_now_file

        #if resume or rebooting:
        #    htmlBuilder.pl()

        if self.config_json["debug"]:
            self.fileSuffix = "debug-" + self.fileSuffix

        self.logFileName = self.config_json["logPath"] + "\\" + self.fileSuffix + ".html"

        self.pl("Init time: " + time_now)

        if self.config_json["debug"]:
            self.pl()
            self.pl("########################################################################################################################", HTMLBuilder.COLOR_YELLOW)
            self.pl("#####################################             DEBUG     MODE           #############################################", HTMLBuilder.COLOR_YELLOW)
            self.pl("########################################################################################################################", HTMLBuilder.COLOR_YELLOW)

    def fetchData(self, activeConfigFile):
        self.config_json = self.loadConfig(activeConfigFile)

        self.hashtableMiners = self.buildHashtableMiners(self.config_json)

        hashtableFactors = { scryptS : self.config_json["scryptFactor"], groestlS : self.config_json["groestlFactor"], skeinS : self.config_json["skeinFactor"], qubitS : self.config_json["qubitFactor"] }
        scryptFactor	= hashtableFactors[scryptS]
        groestlFactor	= hashtableFactors[groestlS]
        skeinFactor	    = hashtableFactors[skeinS]
        qubitFactor	    = hashtableFactors[qubitS]

        getResultCoins = None
        getResultPrice = None
        blockReward    = None

        startT2 = time.time()

        try:
            output_text = self.difficulties.fetchDifficulties()
            self.console.fireMessageEvent(output_text)

            diffScrypt   = self.difficulties.getScryptDifficulty()
            diffGroestl  = self.difficulties.getGroestlDifficulty()
            diffSkein 	 = self.difficulties.getSkeinDifficulty()
            diffQubit 	 = self.difficulties.getQubitDifficulty()

        except Exception as ex:
            return "Something went wrong while retrieving the difficulties from the block chain explorer       :-(   "

        try:
            self.difficulties.fetchBlockReward()
            blockReward = self.difficulties.getBlockReward()

            if not blockReward:
                blockReward = CURRENT_BLOCK_REWARD

        except:
            blockReward = CURRENT_BLOCK_REWARD
            #return "Something went wrong while retrieving the block reward data from the block chain explorer  :-(   "

        try:
            getResultPrice = self.httpGet(exchangesURL.get(self.config_json["exchange"]))

            priceOK = True

        except:
            #Write-Host "Something went wrong while retrieving the exchange rate data :-(                                                                                                                                                          " -foreground "white" -background "black"
            self.currentPrice = 0
            priceOK = False

        #httpTime = time.time() - startT2

        scryptCorrFactor  = self.config_json["scryptHashRate"]  * num * float(blockReward)
        groestlCorrFactor = self.config_json["groestlHashRate"] * num * float(blockReward)
        skeinCorrFactor   = self.config_json["skeinHashRate"]  * num * float(blockReward)
        qubitCorrFactor   = self.config_json["qubitHashRate"]   * num * float(blockReward)

        self.previousPrice = self.currentPrice

        if priceOK:
            objPrice = json.loads(getResultPrice)

            if EXCHANGE_POLONIEX == self.config_json["exchange"]:
                self.currentPrice = float(objPrice["BTC_MYR"]["last"]) * 100000000

            if EXCHANGE_CRYPTSY == self.config_json["exchange"]:
                self.currentPrice = float(objPrice["return"]["markets"]["MYR"]["lasttradeprice"]) * 100000000

        self.prevHashtableCorrected = self.hashtableCorrected

        if self.config_json["mode"] == MODE_MAX_PER_WATT:
            self.config_json["attenuation"] = 0

        self.hashtableWatts = { scryptS : self.config_json["scryptWatts"], groestlS : self.config_json["groestlWatts"], skeinS : self.config_json["skeinWatts"], qubitS : self.config_json["qubitWatts"] }
        self.attenuationWatts = self.getAverageHashValues(self.hashtableWatts) ** ((float(1) / 500))
        attenuationWatts = self.attenuationWatts ** self.config_json["attenuation"]
        self.hashtableWattsAttenuated = { scryptS : self.config_json["scryptWatts"] + attenuationWatts, groestlS : self.config_json["groestlWatts"] + attenuationWatts, skeinS : self.config_json["skeinWatts"] + attenuationWatts, qubitS : self.config_json["qubitWatts"] + attenuationWatts }

        self.hashtableRaw  = { scryptS : ((scryptCorrFactor / diffScrypt)), groestlS : ((groestlCorrFactor / diffGroestl)), skeinS : ((skeinCorrFactor / diffSkein)), qubitS : ((qubitCorrFactor / diffQubit)) }
        self.hashtableRawAttenuated  = { scryptS : ((scryptCorrFactor / diffScrypt) ) / ( self.hashtableWatts[scryptS] + attenuationWatts ), groestlS : ((groestlCorrFactor / diffGroestl) ) / ( self.hashtableWatts[groestlS] + attenuationWatts ), skeinS : ((skeinCorrFactor / diffSkein) ) / ( self.hashtableWatts[skeinS] + attenuationWatts ), qubitS : ((qubitCorrFactor / diffQubit) ) / ( self.hashtableWatts[qubitS] + attenuationWatts ) }
        self.hashtableFactored  = { scryptS : ((scryptCorrFactor / diffScrypt) * scryptFactor), groestlS : ((groestlCorrFactor / diffGroestl) * groestlFactor), skeinS : ((skeinCorrFactor / diffSkein) * skeinFactor), qubitS : ((qubitCorrFactor / diffQubit) * qubitFactor) }
        #hashtablePerWatt   =          { scryptS : ((scryptCorrFactor / diffScrypt) * scryptFactor) / self.hashtableWatts[scryptS], groestlS : ((groestlCorrFactor / diffGroestl) * groestlFactor) / self.hashtableWatts[groestlS], skeinS : ((skeinCorrFactor / diffSkein) * skeinFactor) / self.hashtableWatts[skeinS], qubitS : ((qubitCorrFactor / diffQubit) * qubitFactor) / self.hashtableWatts[qubitS] }
        self.hashtablePerWattAttenuated  = { scryptS : ((scryptCorrFactor / diffScrypt) * scryptFactor) / ( self.hashtableWatts[scryptS] + attenuationWatts ), groestlS : ((groestlCorrFactor / diffGroestl) * groestlFactor) / ( self.hashtableWatts[groestlS] + attenuationWatts ), skeinS : ((skeinCorrFactor / diffSkein) * skeinFactor) / ( self.hashtableWatts[skeinS] + attenuationWatts ), qubitS : ((qubitCorrFactor / diffQubit) * qubitFactor) / ( self.hashtableWatts[qubitS] + attenuationWatts ) }
        self.hashtableCorrected = { scryptS : (scryptCorrFactor / diffScrypt), groestlS : (groestlCorrFactor / diffGroestl), skeinS : (skeinCorrFactor / diffSkein), qubitS : (qubitCorrFactor / diffQubit) }

        if self.noAlgoSelected(self.config_json):
            if self.config_json["mode"] == MODE_MAX_PER_DAY:
                self.hashtable = self.hashtableRaw
            else:
                self.hashtable = self.hashtableRawAttenuated
        else:
            if self.config_json["mode"] == MODE_MAX_PER_DAY:
                self.hashtable = self.hashtableFactored
            else:
                self.hashtable = self.hashtablePerWattAttenuated


        valArraySorted = sorted(self.hashtable.iteritems(), key=operator.itemgetter(1), reverse=True)

        self.maxAlgo  = valArraySorted[0][0]
        self.maxValue = valArraySorted[0][1]

    def isSwitchToNewAlgo(self, forceSwitch):
        greaterThanHys = True
        greaterThanMin = True

        if self.current:
            prevVal = self.hashtable[self.current]

            greaterThanHys = ( not prevVal ) or ( float(self.maxValue) / float(prevVal) ) > self.config_json["hysteresis"]
            greaterThanMin = ((time.time() - self.lastStintStart) / 60.0) > self.config_json["minTimeNoHysteresis"]

        isSwitch = (self.current != self.maxAlgo and ( greaterThanHys or greaterThanMin )) or forceSwitch

        self.prevAlgo = self.current if self.current else self.maxAlgo

        if isSwitch:
            self.current = self.maxAlgo

        return isSwitch

    def executeRound(self, status, timeStopped, maxMinerFails, resume, prevSwitchtext, switchtext):
        self.setEffectiveRoundTime(status == "FAIL", timeStopped)

        self.calculateCoins(maxMinerFails)
        self.calculateWatts(status, resume)

        self.prepareNextRound()

        self.printData(status, prevSwitchtext, switchtext)

        self.htmlBuilder.log(self.config_json, self.logFileName)
        self.dumpData(self.htmlBuilder)

    def getMiner(self):
        return self.hashtableMiners[self.current] if self.current in self.hashtableMiners.keys() else None

    def getScriptPath(self):
        if self.current == scryptS:
            return self.config_json["scryptBatchFile"]

        elif self.current == groestlS:
            return self.config_json["groestlBatchFile"]

        elif self.current == skeinS:
            return self.config_json["skeinBatchFile"]

        elif self.current == qubitS:
            return self.config_json["qubitBatchFile"]

    def initRound(self, status):
        self.now = time.time()

        if self.first:
            self.lastStintStart = self.now
            self.globalStart = self.prevStintStart = self.prevRoundStart = self.lastStintStart
            self.prevHashtableCorrected = self.hashtableCorrected

        if status == "SWITCH":
            self.prevStintStart = self.lastStintStart
            self.lastStintStart = self.now

        self.globalTime = self.storedGlobalTime + ( self.now - self.globalStart )
        self.globalRoundTime = self.now - self.prevRoundStart
        self.globalStintTime = self.now - self.prevStintStart
        self.prevRoundStart = self.now

        self.prevValCorrected = self.prevHashtableCorrected[self.prevAlgo]

        self.nextValCorrected = self.hashtableCorrected[self.current]
        self.newValCorrected  = self.hashtableCorrected[self.prevAlgo]

        self.restartTime = 0

        self._isGlobalStopped()

    def _isGlobalStopped(self):
        if self.noAlgoSelected(self.config_json):
            self.globalStopped = True

        else:
            if self.config_json["mode"] == MODE_MAX_PER_DAY:
                self.globalStopped = self.newValCorrected < self.config_json["minCoins"]

            else:
                averageMinimumCoinsPerWatt = self.config_json["minCoins"] / self.getAverageHashValues(self.hashtableWattsAttenuated)
                self.globalStopped = self.hashtablePerWattAttenuated[self.current] < averageMinimumCoinsPerWatt

        #return self.globalStopped

    def noAlgoSelected(self, config_json):
        return not (config_json["scryptFactor"] or config_json["groestlFactor"] or config_json["skeinFactor"] or config_json["qubitFactor"])

    def httpGet(self, url, timeout=None):
        prev_timeout = socket.getdefaulttimeout()
        if timeout:
            socket.setdefaulttimeout(timeout)

        req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
        resp = urllib2.urlopen(req).read()

        socket.setdefaulttimeout(prev_timeout)

        return resp

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

        return hashtableMiners

    def fetchMiner(self, file):
        f = open(file)
        contents = f.read()
        f.close()

        for miner in MINER_CHOICES:
            if (miner + ".exe") in contents or (".\\" + miner) in contents:
                return miner

        return None

    def loadConfig(self, activeFile):
        f = None
        try:
            f = open(activeFile)
        except IOError:
            #print "Config file not found: " + activeFile
            return self.config_json

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

    def setEffectiveRoundTime(self, failed, timeStopped):
        self.effectiveRoundTime = 0 if self.wasStopped else self.globalRoundTime - self.prevRestartTime

        if failed:
            self.effectiveRoundTime -= timeStopped

        self.effectiveRoundTime = max(self.effectiveRoundTime, 0)

    def calculateCoins(self, maxMinerFails):
        if not self.prevValCorrected:
            prevValCorrected = self.newValCorrected

        avgValCorrected = ( float(self.newValCorrected) + float(self.prevValCorrected) ) / 2.0

        if maxMinerFails:
            coinsRound = 0

        else:
            timeRoundDays = self.effectiveRoundTime / SECONDS_PER_DAY

            #self.hashtableTime[prevAlgo] += effectiveRoundTime
            self.hashtableTime[self.prevAlgo] += self.globalRoundTime
            coinsRound = avgValCorrected * timeRoundDays

        self.coinsStint = self.coinsStint  + coinsRound

        totalCoinsPrev = self.hashtableExpectedCoins[self.prevAlgo] + coinsRound
        self.hashtableExpectedCoins[self.prevAlgo] = totalCoinsPrev

        self.totalCoins = sum(self.hashtableExpectedCoins.values())

        #self.updateAlgoMinedCoins()

    #def updateAlgoMinedCoins(self):
    #    self.hashtableMinedCoins[scryptS]  = self.getAlgoCoins(urlScryptAPI)
    #    self.hashtableMinedCoins[groestlS] = self.getAlgoCoins(urlGroestlAPI)
    #    self.hashtableMinedCoins[skeinS]   = self.getAlgoCoins(urlSkeinAPI)
    #    self.hashtableMinedCoins[qubitS]   = self.getAlgoCoins(urlQubitAPI)

    def getAlgoCoins(self, url):
        try:
            getAlgoData  = json.loads(self.httpGet(url))

            confirmed = float(getAlgoData['getuserbalance']['data']['confirmed'])
            unconfirmed = float(getAlgoData['getuserbalance']['data']['unconfirmed'])
        except:
            return 0

        return int(round(confirmed + unconfirmed))

    def calculateWatts(self, status, resume):
        currentWatts = 0
        if self.wasStopped and not self.first or (self.globalStopped and self.first):
            currentWatts = self.config_json["idleWatts"]

        else:
            currentWatts = self.hashtableWatts[self.prevAlgo]
            if status in ("FAIL", "MAX_FAIL"):
                currentWatts = (currentWatts * (self.effectiveRoundTime / self.globalRoundTime)) + (self.config_json["idleWatts"] * ((self.globalRoundTime - self.effectiveRoundTime) / self.globalRoundTime))

        self.wattsRound = currentWatts * self.globalRoundTime
        self.wattsStint += self.wattsRound

        self.watts = self.watts + self.wattsRound

        if (self.first and not resume) or self.globalTime == 0:
            self.wattsAvg = currentWatts
        else:
            self.wattsAvg = self.watts / self.globalTime

        if status == "SWITCH" or status == "MAX_FAIL":
            if not self.first:
                self.avgStintWatts = self.wattsStint / self.globalStintTime

    def prepareNextRound(self):
        self.prevRestartTime = self.restartTime
        self.wasStopped = self.globalStopped

    def getAverageHashValues(self, dict_p):
        return sum(dict_p.values()) / float(len(dict_p))

    def printData(self, status, prevSwitchtext, switchtext):
        if status == "SWITCH" or status == "MAX_FAIL":
            if prevSwitchtext:
                self.htmlBuilder.printData("SWITCH", self.now, self.globalStintTime, prevSwitchtext, self.previousPrice, self.currentPrice,
                                          self.newValCorrected, self.coinsStint, self.avgStintWatts, self.prevAlgo, self.globalStopped,
                                           self.hashtableExpectedCoins, self.hashtableCorrected, self.hashtableTime, self.config_json)

            self.htmlBuilder.printHeader()

            self.coinsStint = 0
            self.wattsStint = 0

            if status == "SWITCH":
                status = "OK"


        self.htmlBuilder.printData(status, self.now, self.globalTime, switchtext, self.previousPrice, self.currentPrice,
                                   self.nextValCorrected, self.totalCoins, self.wattsAvg, self.current, self.globalStopped,
                                   self.hashtableExpectedCoins, self.hashtableCorrected, self.hashtableTime, self.config_json)

        self.first = False

    #def printData(self, status, htmlBuilder, prevSwitchtext, switchtext):
    #    if status == "SWITCH" or status == "MAX_FAIL":
    #        if prevSwitchtext:
    #            hashtableCoinsMinedStint = Counter(self.hashtableMinedCoins) - Counter(self.hashtablePreviousStintMinedCoins)
    #
    #            htmlBuilder.printData("SWITCH", self.now, self.globalStintTime, prevSwitchtext, self.previousPrice, self.currentPrice,
    #                                      self.newValCorrected, self.coinsStint, self.avgStintWatts, self.prevAlgo, self.globalStopped,
    #                                       self.hashtableExpectedCoins, hashtableCoinsMinedStint, self.hashtableCorrected, self.hashtableTime, self.config_json)
    #
    #        htmlBuilder.printHeader()
    #
    #        self.coinsStint = 0
    #        self.wattsStint = 0
    #        self.hashtablePreviousStintMinedCoins = copy.copy(self.hashtableMinedCoins)
    #        #self.hashtableStintMinedCoins[scryptS]  = 0
    #        #self.hashtableStintMinedCoins[groestlS] = 0
    #        #self.hashtableStintMinedCoins[skeinS]   = 0
    #        #self.hashtableStintMinedCoins[qubitS]   = 0
    #
    #        if status == "SWITCH":
    #            status = "OK"
    #
    #
    #    htmlBuilder.printData(status, self.now, self.globalTime, switchtext, self.previousPrice, self.currentPrice,
    #                               self.nextValCorrected, self.totalCoins, self.wattsAvg, self.current, self.globalStopped,
    #                               self.hashtableExpectedCoins, self.hashtableMinedCoins, self.hashtableCorrected, self.hashtableTime, self.config_json)
    #
    #    self.first = False
    def loadData(self):
        try:
            obj = cPickle.load(open(DATA_FILE_NAME, "rb" ))

            self.hashtableTime  = obj[0]
            self.hashtableExpectedCoins = obj[1]
            self.storedGlobalTime = obj[2]
            self.watts = obj[3]

            #htmlBuilder.loadLines()

            return True

        except IOError:
            return False

    def dumpData(self, htmlBuilder):
        try:
            obj = [self.hashtableTime, self.hashtableExpectedCoins, self.globalTime, self.watts]
            cPickle.dump(obj, open(DATA_FILE_NAME, "wb"))

            htmlBuilder.dumpLines()

        except (IOError, AttributeError):
            pass

    def log(self):
        self.htmlBuilder.log(self.config_json, self.logFileName)

    def end(self):
        count = 0

        import miner.PanelMinerInstance as mi

        while not self.console.frame_myr.miners.checkMinersReady() and count < mi.MAX_ITERATIONS:
            time.sleep(0.5)
            count += 1

        self.htmlBuilder.pl()
        self.htmlBuilder.pl("Process stopped at ... " + time.strftime(DATE_FORMAT_PATTERN, time.localtime()))

        self.dumpData(self.htmlBuilder)

        self.globalStopped = True

        print time.strftime(DATE_FORMAT_PATTERN, time.localtime()), "Exiting thread loop..... "

    def pl(self, line_p=" ", colorForeground=(255, 255, 255), colorBackground=(0, 0, 0)):
        self.htmlBuilder.pl(line_p, colorForeground, colorBackground)

    def p(self, text, colorForeground=(255, 255, 255), colorBackground=(0, 0, 0)):
        self.htmlBuilder.pl(text, colorForeground, colorBackground)

    def getMiningAlgo(self):
        try:
            if self.globalStopped:
                return None

            return self.maxAlgo

        except Exception:
            return None