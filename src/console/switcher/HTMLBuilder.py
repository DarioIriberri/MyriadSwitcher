__author__ = 'Dario'

import SwitcherData
from event.EventLib import *

import wx
import time
import cPickle


SECONDS_PER_DAY = 86400

COLOR_DARK_BLUE         = (0, 0, 139)
COLOR_BLUE              = (0, 0, 255)
COLOR_RED               = (255, 0, 0)
COLOR_DARK_RED          = (139, 0, 0)
COLOR_SEMI_DARK_RED     = (215, 0, 0)
COLOR_DARK_MAGENTA      = (139, 0, 139)
COLOR_LIGHT_GRAY        = (220, 220, 220)
COLOR_GRAY              = (155, 155, 155)
COLOR_DARK_GRAY         = (30, 30, 30)
COLOR_WHITE             = (255, 255, 255)
COLOR_BLACK             = (0, 0, 0)
COLOR_GREEN             = (0, 255, 0)
COLOR_SEMI_DARK_GREEN   = (0, 215, 0)
COLOR_DARK_GREEN        = (0, 139, 0)
COLOR_YELLOW            = (255, 255, 0)
COLOR_DARK_YELLOW       = (255, 203, 0)
COLOR_SEMI_DARK_YELLOW  = (255, 233, 0)
COLOR_ORANGE            = (255, 130, 0)
COLOR_CYAN              = (0, 255, 255)
COLOR_DARK_CYAN         = (0, 139, 139)

hashColorF1  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorF2  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorF3  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorF4  = { "SWITCH" : COLOR_WHITE, 		"OK" : COLOR_WHITE, 		"FAIL" : COLOR_WHITE}
hashColorB1  = { "SWITCH" : COLOR_DARK_CYAN, 	"OK" : COLOR_DARK_BLUE, 	"FAIL" : COLOR_DARK_RED}
hashColorB2  = { "SWITCH" : COLOR_DARK_GREEN, 	"OK" : COLOR_BLACK, 		"FAIL" : COLOR_DARK_MAGENTA}
hashColorB3  = { "SWITCH" : COLOR_DARK_CYAN, 	"OK" : COLOR_DARK_BLUE, 	"FAIL" : COLOR_DARK_RED}
hashColorB4  = { "SWITCH" : COLOR_DARK_GREEN, 	"OK" : COLOR_BLACK, 		"FAIL" : COLOR_DARK_MAGENTA}

foregroundActive  = COLOR_GREEN
foregroundDisabled = COLOR_GRAY
spacerColor = COLOR_BLACK

ANCHOR = "MPLArvmR7dQrF7BCPDFsRCniFnCJhZkG9d"

SESSION_FILE_NAME = "m_s_session.myr"


class HTMLBuilder():
    def __init__(self, console, refresh_milisecs=180000):
        self.line  = str()
        self.lines = []
        self.console = console
        self.htmlEvent = None

        self.refresh_milisecs = str(refresh_milisecs)

    def html_begin(self, text_size=80):
        html =  "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN"
        html += "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
        html += "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
        html += "<head>"
        html += "<style>BODY{background-color:#000000;color:#FFFFFF;font-family:\"Courier New\";font-weight:bold;font-size:" + str(text_size) + "%;}table{border-collapse:collapse;width:1880px;}tr{line-height:1}div:{margin-bottom:20px;}</style>"
        #html += "<script>window.onload=function(){window.scrollTo(0, document.body.scrollHeight);setTimeout(function() {location.reload();}," + self.refresh_t + ")}</script>"
        html += "<script>window.onload=function(){window.scrollTo(0, document.body.scrollHeight);setTimeout(function() {window.scrollTo(0, document.body.scrollHeight);location.reload();}," + self.refresh_milisecs + ")}</script>"
        html += '<link id="page_favicon" href="data:image/x-icon;base64,AAABAAEAGBgAAAEAIACICQAAFgAAACgAAAAYAAAAMAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMiM/QS7dPwbvHT8KqqI/AN2cfwVgH38BQ' \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADU5vYBAAAAAAAAAADQnv0HvXT8Y6xS/MalRPzsqEr84LmC/RJGP/y3RD38zVlS+4iVk/co2MznAwAAAADf1NgCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' \
                'AAAAAAAAAAOuw7BPeq/koqEr866M9/f+jPv3/pkX97s2a/R9JQv21MCj9/zAo/P82L/zwamH3n6qg7Bnl1tUPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA5Z/hC9xq3rXkmupttmj7i6I9/f+jPv3/pEH89rpz/C9KQ/2jMCj9/zEp/f8xKf3/' \
                'Qz785Jqb9xqxv/QSzNPeHMfMvwQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4n7ka9la2/3aZtzOzo70MqdI/OuiPfz+pED89b98+0BVT/uLMCj8/zEp/f8wKPz/enr6jdTd8xNxkvqbcH2s466ij3Lp2qQEAAAAAAAAAAAAAAAAAAAAAAAAAADsre4P3Wne2' \
                'dpb3P/ZWtv95Z7pZrx2/GqzZvxksmD7PNiu8RGRiug0X1j7nToy/O9BOPrtn534JJqx9iZTffz2anCa/2taSPvHpnh888iJBQAAAAAAAAAAAAAAAAAAAADzl9wH5Y7fb8ZluPWUYXX/k2dx6496Y8CNemDAoIptutOwkEYAAAAAubLvAdnT9CCtmsZ9sY9tspR+Zu' \
                'yMeW7/f2VR/2hVQv9uV0L9q4ZhjdinfQoAAAAAAAAAAAAAAAD8gMhj+ITGZrB1iY1oVUL/aFVC/2hVQv9oVUL/aVVC/3pmT+udiGgg297ABOTgwSx/dGCuaVVB/mhVQv9oVUL/aFVC/2hVQv9oVUL/blhE/aJ/Yq3z3LUOAAAAAAAAAAD9br+S/Fa0+MBgh8lpVUL' \
                '+aFVC/2hVQv9oVUL/aFVC/2hVQv+Ib1a3v6uHDZKCZptpVkL/aFVC/2hVQv9oVUL/aFVC/2hVQv9oVUL/alZC/6qOccj48MoWAAAAAAAAAAD9XbiS/VSz//tVs/21g4xlk4JpaZeGcIGIcFeybVZB8mhVQv9oVEH/k3pfhYFsVBxrVkHmdl9J8o56XamRf2Opg2dL' \
                '5mhVQv9sWET8tZVynMXPvBaG2/g0peL4BAAAAAD7gcR4/Fa0+PxWtPv3vtoe1tCyAe7p2wPRuZYRh2tTfmhVQfpoVUL/emFI98uxe2RqWUhPxK+KZ+DQnQTfzaACnINooWhYSPyippe1jtfmcEfI/MQ3xPzyadH7QgAAAADvwM4P+Ym6Pf10wHH8ltEUAAAAAAAAA' \
                'AAAAAAAso5vEn1kTcloVUL/aFVB/4VrUO/pyZUcAAAAAAAAAAAAAAAAo5J+gJ+mnnhLyPnZMML8/jDC/f8wwv3/Usz8tObv6Ab7tKcm+XpkufmDbYT5oZEsAAAAAAAAAAAAAAAAAAAAAKyPcTdwWELtZ1RB/2pUQP+ghGe42sGUCwAAAAAAAAAAtJ6DhNG3lHVv0f' \
                'SEMMH8/zDC/P8wwvz/NMP8837Y/C36sKIG+XhiwvhiSP/5fGep+qGUAwAAAAAAAAAAo6amG4qKhzaVcFN5bFZB/WdUQf90Xkn+xayJfv74vQEAAAAAhm5XpHhjT/uosq2TOcP68y/B/P8wwvz/MML8/nHU+2IAAAAA9o18X/FlS/7lbVPw05Z3WLmJZEDTmmlZhnJ' \
                'fxm1hVN+ukG0ghmVKwWlVQf9oVUL/j3NW8NfBipbOwI9zknVW3WhVQv91YlH6lrawx1LJ92xazvx7TMv8fYPW90gAAAAA66mXD5pwWdpyVkH/c1ZB/HJWQf5sVUH/Z1RB/2dVQ/+jlXmR3LaIKHtiSuloVUL/aFVC/21XQv9pVED/a1ZB/2hVQv9oVUH/eV9J+3yz' \
                'o5lC6/VraPD4bHTy+TsAAAAAtYdsCIFkTs5nVEH/Z1RB/2dUQf9nVEH/aVVB/31oVd7Xx6Us8uesA8GogWNlVEP8aFVC/2hVQv9oVUL/aFVC/2hVQv9oVUL/ZlVE/3duX/823uP/AOf2/krw+WkAAAAArpJ1AoFsWKJtWUXwc11C/3NdQf91XT/6knZaxc6thjMAA' \
                'AAAAAAAAPDougWdj3l+c11H72hWRf1rVkL9bVZC/2hVQv9oVEH/eHBd/1DMyf8D5/X/Buf29WTr+DMAAAAAAAAAAJ+QfgTFtJYT6cNqkt+nJ/zgqi3y7dKPJ+DjfwsAAAAAAAAAAAAAAAAAAAAA3M+oH9vWxTDY0aIsjnlZs2dUQv91bFPtgM26fiLp97sF5/b5Ne' \
                'z3raD2/AQAAAAAAAAAAAAAAAAAAAAA7s99COa5Vnvktk2j6eWZJM3YI8vU3kF91uBQJ+PrgQSU0VIBg807AaPaaAO87cEGg4ptsHJwV/8zzX/2KOCNq2Lpu09Z6uQ/XO34HgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOC/cwHdwYAQ2eFVdsbSAP/G0wL/yNQL8Nr' \
                'iXkaO0Edsb8YYo3jKJLOy4Io2kb2QuDTLfP8A23r/ANt6/xveht9R5qMeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA5eqJC9rhTGfL1xvRxtMD+tHaLoKN0kdvYsEA/2LBAP9wxhffl994OC/hk7EN3IDtKt+Pk17prBkAAAAA39/fAejp5wEA' \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADX4VEM1d5IOdzjX0ue12IzcMYX327GE/Bxxxndhc06fHrdkRFa56ghXOWoAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACj2WkEh' \
                '848G4LNNSKM0UQZmM5WBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD4H/9BYAL/QcAA/0GAAD9BgAAfQQAAD0EAQAdBAAADQQAAA0EAAAFBAAABQQ4HAEEPAwBBBgEAQYAAAEGAAABBgAAAQYBgAEHAeABB8AABQfgAA0H+AARB/4APQf/wf0E="' \
                ' rel="icon" type="image/x-icon" />'
        html += " </head>"
        html += " <body>"
        html += "   <table>"
        html += "    <colgroup>"
        html += "       <col />"
        html += "     </colgroup>"

        return html

    def buildHTML(self, lines, text_size=80):
        html = self.html_begin(text_size)
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

        wx.PostEvent(self.console, ConsoleEvent(html=self.buildHTML(self.lines)))
        #self.fireHTMLEvent(self.buildHTML(self.lines))
        #self.console.onConsoleEvent(self.buildHTML(self.lines))
        #thread = threading.Thread(target=self.console.onConsoleEvent, args = (self.buildHTML(self.lines),))
        #thread.start()

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
            f.write(self.buildHTML(self.lines, 80))
            f.close()

        htmlTime = time.time() - startT

        return htmlTime

    def getCoinsPerDay(self, coins, time, formated=False):
        coinsR = 0 if time == 0 else coins * (SECONDS_PER_DAY / time)

        return '{0:>7}'.format(int(coinsR)) if formated else coinsR

    #def printData(self, status, now, globalTime, switchtext, previousPrice, currentPrice, valCorrected, coins, wattsAvg,
    #              active, stopped, hashtableExpectedCoins, hashtableMinedCoins, hashtableCorrected, hashtableTime, config_json):
    def printData(self, status, now, globalTime, switchtext, previousPrice, currentPrice, valCorrected, coins, wattsAvg,
                  active, stopped, hashtableExpectedCoins, hashtableCorrected, hashtableTime, config_json):

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

            if active == SwitcherData.scryptS:
                totalCoinsScrypt = coins
                totalCoinsGroestl = 0
                totalCoinsSkein   = 0
                totalCoinsQubit   = 0

                #valCorrectedY = dailyCoinsFormated
                #valCorrectedG = zeroValString
                #valCorrectedS = zeroValString
                #valCorrectedQ = zeroValString

            if active == SwitcherData.groestlS:
                totalCoinsScrypt = 0
                totalCoinsGroestl = coins
                totalCoinsSkein   = 0
                totalCoinsQubit   = 0

                #valCorrectedY = zeroValString
                #valCorrectedG = dailyCoinsFormated
                #valCorrectedS = zeroValString
                #valCorrectedQ = zeroValString

            if active == SwitcherData.skeinS:
                totalCoinsScrypt = 0
                totalCoinsGroestl = 0
                totalCoinsSkein   = coins
                totalCoinsQubit   = 0

                #valCorrectedY = zeroValString
                #valCorrectedG = zeroValString
                #valCorrectedS = dailyCoinsFormated
                #valCorrectedQ = zeroValString

            if active == SwitcherData.qubitS:
                totalCoinsScrypt = 0
                totalCoinsGroestl = 0
                totalCoinsSkein   = 0
                totalCoinsQubit   = coins

                #valCorrectedY = zeroValString
                #valCorrectedG = zeroValString
                #valCorrectedS = zeroValString
                #valCorrectedQ = dailyCoinsFormated


            valCorrectedY = self.getCoinsPerDay(hashtableExpectedCoins[SwitcherData.scryptS], hashtableTime[SwitcherData.scryptS], True)
            valCorrectedG = self.getCoinsPerDay(hashtableExpectedCoins[SwitcherData.groestlS], hashtableTime[SwitcherData.groestlS], True)
            valCorrectedS = self.getCoinsPerDay(hashtableExpectedCoins[SwitcherData.skeinS], hashtableTime[SwitcherData.skeinS], True)
            valCorrectedQ = self.getCoinsPerDay(hashtableExpectedCoins[SwitcherData.qubitS], hashtableTime[SwitcherData.qubitS], True)

        else:
            totalCoinsScrypt  = hashtableExpectedCoins[SwitcherData.scryptS]
            totalCoinsGroestl = hashtableExpectedCoins[SwitcherData.groestlS]
            totalCoinsSkein   = hashtableExpectedCoins[SwitcherData.skeinS]
            totalCoinsQubit   = hashtableExpectedCoins[SwitcherData.qubitS]

            valCorrectedY = '{0:>7}'.format(int(hashtableCorrected[SwitcherData.scryptS]))
            valCorrectedG = '{0:>7}'.format(int(hashtableCorrected[SwitcherData.groestlS]))
            valCorrectedS = '{0:>7}'.format(int(hashtableCorrected[SwitcherData.skeinS]))
            valCorrectedQ = '{0:>7}'.format(int(hashtableCorrected[SwitcherData.qubitS]))

        #minedY = '{0:>7}'.format(hashtableMinedCoins[scryptS])
        #minedG = '{0:>7}'.format(hashtableMinedCoins[groestlS])
        #minedS = '{0:>7}'.format(hashtableMinedCoins[skeinS])
        #minedQ = '{0:>7}'.format(hashtableMinedCoins[qubitS])

        stringOthersCoinsY = "{:7.0f}".format(totalCoinsScrypt)  + " " + self.formatPct(totalCoinsScrypt, coins, 0)  + valCorrectedY
        stringOthersCoinsG = "{:7.0f}".format(totalCoinsGroestl) + " " + self.formatPct(totalCoinsGroestl, coins, 0) + valCorrectedG
        stringOthersCoinsS = "{:7.0f}".format(totalCoinsSkein)   + " " + self.formatPct(totalCoinsSkein, coins, 0)   + valCorrectedS
        stringOthersCoinsQ = "{:7.0f}".format(totalCoinsQubit)   + " " + self.formatPct(totalCoinsQubit, coins, 0)   + valCorrectedQ

        #stringOthersCoinsY = minedY + " / " + "{:7.0f}".format(totalCoinsScrypt)  + valCorrectedY
        #stringOthersCoinsG = minedG + " / " + "{:7.0f}".format(totalCoinsGroestl) + valCorrectedG
        #stringOthersCoinsS = minedS + " / " + "{:7.0f}".format(totalCoinsSkein)   + valCorrectedS
        #stringOthersCoinsQ = minedQ + " / " + "{:7.0f}".format(totalCoinsQubit)   + valCorrectedQ

        stringPrice = '{0:>10} $'.format(int(currentPrice * valCorrected / float(config_json["scryptHashRate"]))) + '{0:>10} $ '.format(int((currentPrice * valCorrected)))

        fcY = fcG = fcS = fcQ = hashColorF3[status]
        bcY = bcG = bcS = bcQ = hashColorB3[status]

        if active == SwitcherData.scryptS:
            fcY = foregroundActive

        if active == SwitcherData.groestlS:
            fcG = foregroundActive

        if active == SwitcherData.skeinS:
            fcS = foregroundActive

        if active == SwitcherData.qubitS:
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
        coinsPerWatt = "{:0.2f}".format(0) if wattsAvg == 0 else "{:0.2f}".format(dailyCoinsTot / wattsAvg)

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
        self.pl("Time    Elapsed/Stint   Algo      Exch.  Prof 1Mh/s   My profit   Scrypt    %   /day   Groestl   %   /day    Skein    %   /day    Qubit    %   /day   Tot.Coins     Tot.$   /day   Prof 1Mh/s   My profit   Watts    C/W", COLOR_CYAN)
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