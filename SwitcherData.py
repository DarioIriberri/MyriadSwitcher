__author__ = 'Dario'

import time
import json
import operator
import socket
import urllib2
import cPickle
import HTMLBuilder


SECONDS_PER_DAY = 86400

scryptS  = " Scrypt "
groestlS = " Groestl"
skeinS   = " SKein  "
qubitS   = " Qubit  "

MINER_CHOICES = ["sgminer", "cgminer", "bfgminer", "reaper", "cudaminer", "minerd"]

EXCHANGE_POLONIEX = "poloniex"
EXCHANGE_MINTPAL  = "mintpal"
exchangesURL = {EXCHANGE_POLONIEX: "https://poloniex.com/public?command=returnTicker", EXCHANGE_MINTPAL: "https://api.mintpal.com/v1/market/stats/MYR/BTC"}

MODE_MAX_PER_DAY = 1
MODE_MAX_PER_WATT = 2
MODE_MAX_PER_HYBRID = 3

num = 20.11656761

DATA_FILE_NAME = "m_s_data.myr"

class SwitcherData():
    def __init__(self):
        self.current                = None
        self.first                  = True

        self.currentPrice           = None
        self.hashtableCorrected     = None
        self.wasStopped             = False
        self.prevRestartTime        = 0
        self.coinsStint             = 0
        self.wattsStint             = 0

    def fetchData(self, activeConfigFile):
        self.config_json = self.loadConfig(activeConfigFile)

        self.hashtableMiners = self.buildHashtableMiners(self.config_json)

        hashtableFactors = { scryptS : self.config_json["scryptFactor"], groestlS : self.config_json["groestlFactor"], skeinS : self.config_json["skeinFactor"], qubitS : self.config_json["qubitFactor"] }
        scryptFactor	= hashtableFactors[scryptS]
        groestlFactor	= hashtableFactors[groestlS]
        skeinFactor	    = hashtableFactors[skeinS]
        qubitFactor	    = hashtableFactors[qubitS]

        getResult = None
        getResultCoins = None
        getResultPrice = None

        startT2 = time.time()

        try:
            getResult = self.httpGet("http://myriad.theblockexplorer.com/api.php?mode=info")

        except:
            return "Something went wrong while retrieving the difficulties from the block chain explorer       :-(   "

        try:
            getResultCoins = self.httpGet("http://myriad.theblockexplorer.com/api.php?mode=coins")

        except:
            return "Something went wrong while retrieving the block reward data from the block chain explorer  :-(   "

        try:
            getResultPrice = self.httpGet(exchangesURL.get(self.config_json["exchange"]))

            priceOK = True

        except:
            #Write-Host "Something went wrong while retrieving the exchange rate data :-(                                                                                                                                                          " -foreground "white" -background "black"
            self.currentPrice = 0
            priceOK = False

        #httpTime = time.time() - startT2

        obj = json.loads(getResult)
        objCoins = json.loads(getResultCoins)

        diffScrypt 	= obj["difficulty_scrypt"]
        diffGroestl = obj["difficulty_groestl"]
        diffSkein 	= obj["difficulty_skein"]
        diffQubit 	= obj["difficulty_qubit"]

        per = objCoins["per"]

        scryptCorrFactor  = self.config_json["scryptHashRate"]  * num * int(per)
        groestlCorrFactor = self.config_json["groestlHashRate"] * num * int(per)
        skeinCorrFactor   = self.config_json["skeinHashRate"]  * num * int(per)
        qubitCorrFactor   = self.config_json["qubitHashRate"]   * num * int(per)

        self.previousPrice = self.currentPrice

        if priceOK:
            objPrice = json.loads(getResultPrice)

            if EXCHANGE_POLONIEX == self.config_json["exchange"]:
                self.currentPrice = float(objPrice["BTC_MYR"]["last"]) * 100000000

            if EXCHANGE_MINTPAL == self.config_json["exchange"]:
                self.currentPrice = float(objPrice[0]["last_price"]) * 100000000

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

    def init(self, config_json, htmlBuilder, resume, rebooting, dataInitComplete):
        if not dataInitComplete:
            self.hashtableTime  = { scryptS : 0, groestlS : 0, skeinS : 0, qubitS : 0 }
            self.hashtableCoins = { scryptS : 0, groestlS : 0, skeinS : 0, qubitS : 0 }
            self.storedGlobalTime = 0
            self.watts = 0

        time_now = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        time_now_file = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())
        self.fileSuffix  = time_now_file

        if resume or rebooting:
            htmlBuilder.pl()

        if config_json["debug"]:
            self.fileSuffix = "debug-" + self.fileSuffix

        logFileName = config_json["logPath"] + "\\" + self.fileSuffix + ".html"

        htmlBuilder.pl("Init time: " + time_now)

        if config_json["debug"]:
            htmlBuilder.pl()
            htmlBuilder.pl("########################################################################################################################", HTMLBuilder.COLOR_YELLOW)
            htmlBuilder.pl("#####################################             DEBUG     MODE           #############################################", HTMLBuilder.COLOR_YELLOW)
            htmlBuilder.pl("########################################################################################################################", HTMLBuilder.COLOR_YELLOW)

        return logFileName

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

    def executeRound(self, status, timeStopped, maxMinerFails, htmlBuilder, resume, prevSwitchtext, switchtext):
        self.setEffectiveRoundTime(status == "FAIL", timeStopped)

        self.calculateCoins(maxMinerFails)
        self.calculateWatts(status, timeStopped, maxMinerFails, resume)

        self.prepareNextRound()

        self.printData(status, htmlBuilder, prevSwitchtext, switchtext)

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


    def getGlobalStopped(self):
        if self.noAlgoSelected(self.config_json):
            self.globalStopped = True

        else:
            if self.config_json["mode"] == MODE_MAX_PER_DAY:
                self.globalStopped = self.newValCorrected < self.config_json["minCoins"]

            else:
                averageMinimumCoinsPerWatt = self.config_json["minCoins"] / self.getAverageHashValues(self.hashtableWattsAttenuated)
                self.globalStopped = self.hashtablePerWattAttenuated[self.current] < averageMinimumCoinsPerWatt

    def noAlgoSelected(self, config_json):
        return not (config_json["scryptFactor"] or config_json["groestlFactor"] or config_json["skeinFactor"] or config_json["qubitFactor"])

    def httpGet(self, url):
        return urllib2.urlopen(url).read()

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

        totalCoinsPrev = self.hashtableCoins[self.prevAlgo] + coinsRound
        self.hashtableCoins[self.prevAlgo] = totalCoinsPrev

        self.totalCoins = sum(self.hashtableCoins.values())

    def calculateWatts(self, status, wasStopped, globalStopped, resume):
        currentWatts = 0
        if wasStopped and not self.first or (globalStopped and self.first):
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

    def printData(self, status, htmlBuilder, prevSwitchtext, switchtext):
        if status == "SWITCH" or status == "MAX_FAIL":
            if prevSwitchtext:
                htmlBuilder.printData("SWITCH", self.now, self.globalStintTime, prevSwitchtext, self.previousPrice, self.currentPrice,
                                          self.newValCorrected, self.coinsStint, self.avgStintWatts, self.prevAlgo, self.globalStopped,
                                           self.hashtableCoins, self.hashtableCorrected, self.hashtableTime, self.config_json)

            htmlBuilder.printHeader()

            self.coinsStint = 0
            self.wattsStint = 0

            if status == "SWITCH":
                status = "OK"


        htmlBuilder.printData(status, self.now, self.globalTime, switchtext, self.previousPrice, self.currentPrice,
                                   self.nextValCorrected, self.totalCoins, self.wattsAvg, self.current, self.globalStopped,
                                   self.hashtableCoins, self.hashtableCorrected, self.hashtableTime, self.config_json)

        self.first = False

    def loadData(self, htmlBuilder):
        try:
            obj = cPickle.load(open(DATA_FILE_NAME, "rb" ))

            self.hashtableTime  = obj[0]
            self.hashtableCoins = obj[1]
            self.storedGlobalTime = obj[2]
            self.watts = obj[3]

            htmlBuilder.loadLines()

            return True

        except IOError:
            return False

    def dumpData(self, htmlBuilder):
        try:
            obj = [self.hashtableTime, self.hashtableCoins, self.globalTime, self.watts]
            cPickle.dump(obj, open(DATA_FILE_NAME, "wb"))

            htmlBuilder.dumpLines()

        except IOError:
            pass

    def end(self, htmlBuilder):
        htmlBuilder.pl()
        htmlBuilder.pl("Process stopped at ... " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        self.dumpData(htmlBuilder)

        print time.strftime("%d-%m-%Y %H:%M:%S", time.localtime()), "Exiting thread loop..... "