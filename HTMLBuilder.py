__author__ = 'Dario'

import PanelConsole
import wx
import time
import cPickle


SECONDS_PER_DAY = 86400

COLOR_DARK_BLUE     = (0, 0, 139)
COLOR_DARK_GREEN    = (0, 139, 0)
COLOR_DARK_RED      = (139, 0, 0)
COLOR_DARK_MAGENTA  = (139, 0, 139)
COLOR_DARK_GRAY     = (155, 155, 155)
COLOR_WHITE         = (255, 255, 255)
COLOR_BLACK         = (0, 0, 0)
COLOR_RED           = (255, 0, 0)
COLOR_GREEN         = (0, 255, 0)
COLOR_YELLOW        = (255, 255, 0)
COLOR_CYAN          = (0, 255, 255)
COLOR_DARK_CYAN     = (0, 139, 139)

hashColorF1  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorF2  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorF3  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorF4  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorB1  = { "SWITCH" : COLOR_DARK_CYAN, 	"OK" : COLOR_DARK_BLUE, 	"FAIL" : COLOR_DARK_RED}
hashColorB2  = { "SWITCH" : COLOR_DARK_GREEN, 	"OK" : COLOR_BLACK, 		"FAIL" : COLOR_DARK_MAGENTA}
hashColorB3  = { "SWITCH" : COLOR_DARK_CYAN, 	"OK" : COLOR_DARK_BLUE, 	"FAIL" : COLOR_DARK_RED}
hashColorB4  = { "SWITCH" : COLOR_DARK_GREEN, 	"OK" : COLOR_BLACK, 		"FAIL" : COLOR_DARK_MAGENTA}

foregroundActive  = COLOR_GREEN
foregroundDisabled = COLOR_DARK_GRAY
spacerColor = COLOR_BLACK

scryptS  = " Scrypt "
groestlS = " Groestl"
skeinS   = " SKein  "
qubitS   = " Qubit  "

ANCHOR = "MPLArvmR7dQrF7BCPDFsRCniFnCJhZkG9d"

SESSION_FILE_NAME = "m_s_session.myr"


class HTMLBuilder():
    def __init__(self, console, refresh_milisecs):
        self.line  = str()
        self.lines = []
        self.console = console

        self.refresh_milisecs = str(refresh_milisecs)

    def html_begin(self):
        html =  "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN"
        html += "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
        html += "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        html += "<head>"
        html += "<style>BODY{background-color:#000000;color:#FFFFFF;font-family:\"Courier New\";font-weight:bold;font-size:80%;}table{border-collapse:collapse;width:1880px;}tr{line-height:1}div:{margin-bottom:20px;}</style>"
        #html += "<script>window.onload=function(){window.scrollTo(0, document.body.scrollHeight);setTimeout(function() {location.reload();}," + self.refresh_t + ")}</script>"
        html += "<script>window.onload=function(){window.scrollTo(0, document.body.scrollHeight);setTimeout(function() {window.scrollTo(0, document.body.scrollHeight);location.reload();}," + self.refresh_milisecs + ")}</script>"
        html += " </head>"
        html += " <body>"
        html += "   <table>"
        html += "    <colgroup>"
        html += "       <col />"
        html += "     </colgroup>"

        return html

    def buildHTML(self, lines):
        html = self.html_begin()
        for line in lines:
            html += line

        return html + self.html_end()

    def html_end(self):
        html =  "</table>"
        #html += "<tr><td><b style=\"color:rgb(0, 0, 0)\">" + ANCHOR + "</b></td></tr>"
        #html += "<div id=\"bottom\"/>"
        html += "</body>"
        html += "</html>"

        return html

    def pl(self, line_p=" ", colorForeground=(255, 255, 255), colorBackground=(0, 0, 0)):
        self.p(line_p, colorForeground, colorBackground)

        self.line = "<tr><td>" + self.line + "</td></tr>"
        self.lines.append(self.line)
        self.line = str()

        evt = PanelConsole.ConsoleEvent(html=self.buildHTML(self.lines))
        wx.PostEvent(self.console, evt)

        #self.wv.SetPage(self.buildHTML(self.lines), "/")
        #self.wv.LoadURL("https://dl.dropboxusercontent.com/u/19353176/Myriad_log/2014-05-04-040554.html")
        #self.LoadFile("C:\\Dropbox\\Public\\Myriad_log\\2014-05-09-214905.html")

    def p(self, text, color=(255, 255, 255), colorBackground=(0, 0, 0)):
        text = text.replace(" ", "&nbsp;")

        txtColor = "rgb" + str(color)
        txtColorBackground = "rgb" + str(colorBackground)

        if color == (255, 255, 255) and colorBackground == (0, 0, 0):
            self.line += "<b>" + text + "</b>"
        if color != (255, 255, 255) and colorBackground == (0, 0, 0):
            self.line += "<b style=\"color:" + txtColor + "\">" + text + "</b>"
        if color == (255, 255, 255) and colorBackground != (0, 0, 0):
            self.line += "<b style=\"background-color:" + txtColorBackground + "\">" + text + "</b>"
        if color != (255, 255, 255) and colorBackground != (0, 0, 0):
            self.line += "<b style=\"color:" + txtColor + ";background-color:" + txtColorBackground + "\">" + text + "</b>"

    def log(self, config_json, logFileName):
        htmlTime = 0

        startT = time.time()

        if config_json["logActive"]:
            startT = time.time()

            f = open(logFileName, "w")
            f.write(self.buildHTML(self.lines))
            f.close()

        htmlTime = time.time() - startT

        return htmlTime

    def getCoinsPerDay(self, coins, time, formated=False):
        coinsR = 0 if time == 0 else coins * (SECONDS_PER_DAY / time)

        return '{0:>7}'.format(int(coinsR)) if formated else coinsR

    def printData(self, status, now, globalTime, switchtext, previousPrice, currentPrice, valCorrected, coins, wattsAvg,
                  active, stopped, hashtableExpectedCoins, hashtableMinedCoins, hashtableCorrected, hashtableTime, config_json):

        status = "FAIL" if status == "MAX_FAIL" else status

        totalCoinsFormated = "{:7.0f}".format(coins)

        totalSatoshi = coins * currentPrice
        dailyCoinsTot = 0
        profitabilityTotal = 0

        if globalTime > 0:
            dailyCoinsTot = self.getCoinsPerDay(coins, globalTime)
            profitabilityTotal = self.getCoinsPerDay(totalSatoshi, globalTime)

        totalSatoshiStr = "{:11.0f}".format(totalSatoshi)
        dailyCoinsFormated = '{0:>7}'.format(int(dailyCoinsTot))

        priceForegroundColor = COLOR_WHITE

        if not previousPrice or ( currentPrice == previousPrice ):
            priceForegroundColor = COLOR_WHITE
        else:
            if currentPrice > previousPrice:
                priceForegroundColor = COLOR_GREEN

            else:
                priceForegroundColor = COLOR_RED

        totalCoinsScrypt  = 0
        totalCoinsGroestl = 0
        totalCoinsSkein   = 0
        totalCoinsQubit   = 0
        valCorrectedY     = 0
        valCorrectedG     = 0
        valCorrectedS     = 0
        valCorrectedQ     = 0

        if status == "SWITCH":

            zeroValString = "   ----"

            if active == scryptS:
                totalCoinsScrypt = coins
                totalCoinsGroestl = 0
                totalCoinsSkein   = 0
                totalCoinsQubit   = 0

                #valCorrectedY = dailyCoinsFormated
                #valCorrectedG = zeroValString
                #valCorrectedS = zeroValString
                #valCorrectedQ = zeroValString

            if active == groestlS:
                totalCoinsScrypt = 0
                totalCoinsGroestl = coins
                totalCoinsSkein   = 0
                totalCoinsQubit   = 0

                #valCorrectedY = zeroValString
                #valCorrectedG = dailyCoinsFormated
                #valCorrectedS = zeroValString
                #valCorrectedQ = zeroValString

            if active == skeinS:
                totalCoinsScrypt = 0
                totalCoinsGroestl = 0
                totalCoinsSkein   = coins
                totalCoinsQubit   = 0

                #valCorrectedY = zeroValString
                #valCorrectedG = zeroValString
                #valCorrectedS = dailyCoinsFormated
                #valCorrectedQ = zeroValString

            if active == qubitS:
                totalCoinsScrypt = 0
                totalCoinsGroestl = 0
                totalCoinsSkein   = 0
                totalCoinsQubit   = coins

                #valCorrectedY = zeroValString
                #valCorrectedG = zeroValString
                #valCorrectedS = zeroValString
                #valCorrectedQ = dailyCoinsFormated


            valCorrectedY = self.getCoinsPerDay(hashtableExpectedCoins[scryptS], hashtableTime[scryptS], True)
            valCorrectedG = self.getCoinsPerDay(hashtableExpectedCoins[groestlS], hashtableTime[groestlS], True)
            valCorrectedS = self.getCoinsPerDay(hashtableExpectedCoins[skeinS], hashtableTime[skeinS], True)
            valCorrectedQ = self.getCoinsPerDay(hashtableExpectedCoins[qubitS], hashtableTime[qubitS], True)

        else:
            totalCoinsScrypt  = hashtableExpectedCoins[scryptS]
            totalCoinsGroestl = hashtableExpectedCoins[groestlS]
            totalCoinsSkein   = hashtableExpectedCoins[skeinS]
            totalCoinsQubit   = hashtableExpectedCoins[qubitS]

            valCorrectedY = '{0:>7}'.format(int(hashtableCorrected[scryptS]))
            valCorrectedG = '{0:>7}'.format(int(hashtableCorrected[groestlS]))
            valCorrectedS = '{0:>7}'.format(int(hashtableCorrected[skeinS]))
            valCorrectedQ = '{0:>7}'.format(int(hashtableCorrected[qubitS]))

        minedY = '{0:>7}'.format(hashtableMinedCoins[scryptS])
        minedG = '{0:>7}'.format(hashtableMinedCoins[groestlS])
        minedS = '{0:>7}'.format(hashtableMinedCoins[skeinS])
        minedQ = '{0:>7}'.format(hashtableMinedCoins[qubitS])

        #stringOthersCoinsY = "{:7.0f}".format(totalCoinsScrypt)  + " " + self.formatPct(totalCoinsScrypt, coins, 0)  + valCorrectedY
        #stringOthersCoinsG = "{:7.0f}".format(totalCoinsGroestl) + " " + self.formatPct(totalCoinsGroestl, coins, 0) + valCorrectedG
        #stringOthersCoinsS = "{:7.0f}".format(totalCoinsSkein)   + " " + self.formatPct(totalCoinsSkein, coins, 0)   + valCorrectedS
        #stringOthersCoinsQ = "{:7.0f}".format(totalCoinsQubit)   + " " + self.formatPct(totalCoinsQubit, coins, 0)   + valCorrectedQ

        stringOthersCoinsY = minedY + "/" + "{:7.0f}".format(totalCoinsScrypt)  + valCorrectedY
        stringOthersCoinsG = minedG + "/" + "{:7.0f}".format(totalCoinsGroestl) + valCorrectedG
        stringOthersCoinsS = minedS + "/" + "{:7.0f}".format(totalCoinsSkein)   + valCorrectedS
        stringOthersCoinsQ = minedQ + "/" + "{:7.0f}".format(totalCoinsQubit)   + valCorrectedQ

        stringPrice = '{0:>10} $'.format(int(currentPrice * valCorrected / float(config_json["scryptHashRate"]))) + '{0:>10} $ '.format(int((currentPrice * valCorrected)))

        fcY = fcG = fcS = fcQ = hashColorF3[status]
        bcY = bcG = bcS = bcQ = hashColorB3[status]

        if active == scryptS:
            fcY = foregroundActive

        if active == groestlS:
            fcG = foregroundActive

        if active == skeinS:
            fcS = foregroundActive

        if active == qubitS:
            fcQ = foregroundActive


        tforeground = hashColorF2[status]

        if status != "SWITCH":
            if not config_json["scryptFactor"]:
                fcY = foregroundDisabled
                #$bcY = $backgroundDisabled

            if not config_json["groestlFactor"]:
                fcG = foregroundDisabled
                #$bcG = $backgroundDisabled

            if not config_json["skeinFactor"]:
                fcS = foregroundDisabled
                #$bcS = $backgroundDisabled

            if not config_json["qubitFactor"]:
                fcQ = foregroundDisabled
                #$bcQ = $backgroundDisabled

            if stopped:
                fcY = fcG = fcS = fcQ = tforeground = foregroundDisabled

        totals = totalSatoshiStr + " $" + dailyCoinsFormated + '{0: >11}'.format(int((profitabilityTotal / config_json["scryptHashRate"]))) + " $" + '{0: >10}'.format(int(profitabilityTotal)) + " $  "

        currentPriceFormated = '{0:>6} $'.format(int(currentPrice))
        coinsPerWatt = "{:0.2f}".format(dailyCoinsTot / wattsAvg)

        nowP = time.strftime("%H:%M:%S", time.localtime(now))
        nowG = self.getFormatedTime(globalTime)

        #self.pl(nowP + " ", hashColorF1[status], hashColorB1[status])
        self.p( nowP + " " + nowG + " ", hashColorF1[status], hashColorB1[status])
        self.p( switchtext, tforeground, hashColorB2[status] )
        self.p( currentPriceFormated, priceForegroundColor, hashColorB2[status])
        self.p( stringPrice, tforeground, hashColorB2[status])
        self.p( " ", colorBackground=spacerColor)
        self.p( stringOthersCoinsY + " ", fcY, bcY)
        self.p( " ", colorBackground=spacerColor)
        self.p( stringOthersCoinsG + " ", fcG, bcG)
        self.p( " ", colorBackground=spacerColor)
        self.p( stringOthersCoinsS + " ", fcS, bcS)
        self.p( " ", colorBackground=spacerColor)
        self.p( stringOthersCoinsQ + " ", fcQ, bcQ)
        self.p( " ", colorBackground=spacerColor)
        self.p( totalCoinsFormated + totals , hashColorF4[status], hashColorB4[status])
        self.p( " " + '{0:>4}'.format(int(wattsAvg)) + "W ", hashColorF1[status], hashColorB1[status])
        self.p( " ", colorBackground=spacerColor)
        self.p( '{0:>6} '.format(coinsPerWatt), hashColorF1[status], hashColorB1[status])

        self.pl()

    def printHeader(self):
        self.pl()
        self.pl("Time    Elapsed/Stint   Algo      Exch.  Prof 1Mh/s   My profit   Scrypt           /day   Groestl          /day    Skein           /day    Qubit           /day   Tot.Coins     Tot.$   /day   Prof 1Mh/s   My profit   Watts    C/W", COLOR_CYAN)
        #11:32:34 00 00:00:00 S  Qubit    522$    457958 $    591681 $        0   0%    785        0   0%    586        0   0%   1409        0   0%   1133        0          0 $      0          0 $         0 $    110W    0.00


    def getFormatedTime(self, timestamp):
        time_str = time.strftime('%H:%M:%S', time.gmtime(timestamp))
        days = int(timestamp / SECONDS_PER_DAY)

        return "{:02.0f}".format(days) + " " + time_str

    def formatPct(self, decim1, decim2, decDigits):
        if not decim2:
            return ("{:3." + str(decDigits) + "f}%").format(0)

        return ("{:3." + str(decDigits) + "f}%").format((decim1 / decim2) * 100)

    def loadLines(self):
        try:
            self.lines = cPickle.load(open(SESSION_FILE_NAME, "rb" ))
        except IOError:
            pass

    def dumpLines(self):
        try:
            cPickle.dump(self.lines, open(SESSION_FILE_NAME, "wb" ))
        except IOError:
            pass