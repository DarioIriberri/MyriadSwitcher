import SimpleHTTPServer
import SocketServer
import threading
import time
import sys

PATH = '/ExternalProfitDGB'
STARTED = False
FORCE_STOP = False
httpd   = None

if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    INTERFACE = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    INTERFACE = ""
else:
    PORT = 8081
    INTERFACE = ""

def start(switcherdata_p):
    global STARTED, httpd
    st_count = 0
    while STARTED and st_count < 60:
        #httpd.setSwitcherData(switcherdata_p)
        time.sleep(1)
        st_count += 1

    httpd = ExternalProfitServer(switcherdata_p, ("localhost", PORT), ExternalProfitHandler)

    #print "@rochacbruno Python http server version 0.1 (for testing purposes only)"
    threading.Thread(target=start_serving, args=(httpd,)).start()
    STARTED = True

    print "Serving DGB Profit at: http://%(interface)s:%(port)s" % dict(interface=INTERFACE or "localhost", port=PORT)

def keep_running():
    global FORCE_STOP
    return not FORCE_STOP

def force_stop():
    if not STARTED:
        return

    global FORCE_STOP
    FORCE_STOP = True

def start_serving(httpd):
    global STARTED, FORCE_STOP
    while keep_running():
        httpd.handle_request()

    FORCE_STOP = False
    STARTED = False
    print "DGB Profit service stopped"


class ExternalProfitServer(SocketServer.TCPServer):
    def __init__(self, switcherData, server_address, RequestHandlerClass, bind_and_activate=False):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        try:
            self.allow_reuse_address = True
            self.server_bind()
            self.server_activate()
        except:
            self.server_close()
            raise

        self.switcherData = switcherData

    #def setSwitcherData(self, switcherdata):
    #    self.switcherdata = switcherdata

class ExternalProfitHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        #logging.warning("======= GET STARTED =======")
        #logging.warning(self.headers)
        sd = self.server.switcherData

        try:
            profit = 0 if self.isNotMining() else sd.getProfit()
            profitabilityTotal = sd.htmlBuilder.getCoinsPerDay(sd.totalCoins * sd.currentPrice, sd.globalTime)
        except:
            profit = 0
            profitabilityTotal = 0

        #logging.warning("\n")

        if self.path == PATH:
            self.wfile.write('%s;%s' % (profit, profitabilityTotal))

    def do_POST(self):
        #logging.warning("======= POST STARTED =======")
        self.wfile.write("POST method not supported")
        #logging.warning(self.headers)

    def isNotMining(self):
        return not self.server.switcherData.getMiningAlgo()
        #return not self.server.switcherData.noAlgoSelected() and not self.server.switcherData.getMiningAlgo()