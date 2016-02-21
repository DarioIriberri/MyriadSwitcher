import SimpleHTTPServer
import SocketServer
#import logging
import threading
import smtplib
import cgi

import sys

PATH = '/ErrorReports'

if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    INTERFACE = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    INTERFACE = ""
else:
    PORT = 8080
    INTERFACE = ""


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        #logging.warning("======= GET STARTED =======")
        #logging.warning(self.headers)
        self.wfile.write("GET method not supported")
        #SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        #logging.warning("======= POST STARTED =======")
        #logging.warning(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        #logging.warning("======= POST VALUES =======")

        str_out = ""
        #str_out = self.rfile.readlines()

        exception = None
        version = None

        for item in form.list:
            #logging.warning(item)
            str_out += item.name + ':\n\n' + item.value

            if item.name == 'version':
                version = item.value

            if item.name == 'exception':
                exception = item.value

        #logging.warning("\n")
        print str_out
        self.wfile.write(str_out + "\n\nError report sent, thanks!")
        #SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

        if exception and version and self.path == PATH:
            mailReportThread = threading.Thread(target=self.sendReport, args=(exception, version, self.client_address))
            mailReportThread.start()

    def sendReport(self, exception, version, client_address):
        fromaddr = 'myriad.switcher@gmail.com'
        toaddrs  = 'dario.iriberri@gmail.com'

        message = 'Subject: Myriad Switcher ' + version + ' Error Report\n\nFrom\n\n%s\n\nError\n\n%s' % (client_address, exception)

        username = 'myriad.switcher'
        password = 'hdFBkFOLwZ48I3w'

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, message)
        server.quit()

Handler = ServerHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

#print "@rochacbruno Python http server version 0.1 (for testing purposes only)"
print "Serving at: http://%(interface)s:%(port)s" % dict(interface=INTERFACE or "localhost", port=PORT)
httpd.serve_forever()


#import SimpleHTTPServer
#import SocketServer
#
#PORT = 8080
#
#Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
#
#httpd = SocketServer.TCPServer(("", PORT), Handler)
#
#print "serving at port", PORT
#httpd.serve_forever()