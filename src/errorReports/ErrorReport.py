__author__ = 'Dario'

import smtplib
import requests
import wx
import FrameMYR
import wx.lib.agw.genericmessagedialog as GMD

URL = 'http://myriadswitcher.duckdns.org:8080'
TIMEOUT = 30

class ErrorReport():

    def sendReport(self, parent, text):
        try:
            question = "Sorry, something went wrong and your mining session will stop.\n\nDo you want to send an error report? No personal data will be included."
            dlg = GMD.GenericMessageDialog(parent, question, "Send Error Report", wx.YES_NO | wx.ICON_STOP)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()

            if result:
                version = FrameMYR.VERSION + '.' + str(FrameMYR.REVISION)
                data = {'exception' : text, 'version' : version}

                #resp = requests.request('post', URL, data=data, timeout=TIMEOUT)

                fromaddr = 'myriad.switcher@gmail.com'
                toaddrs  = 'dario.iriberri@gmail.com'

                message = 'Subject: Myriad Switcher ' + FrameMYR.VERSION + '.' + str(FrameMYR.REVISION) + ' Error\n\n%s' % (text)

                username = 'myriad.switcher'
                password = 'hdFBkFOLwZ48I3w'

                server = smtplib.SMTP('smtp.gmail.com:587')
                server.starttls()
                server.login(username,password)
                server.sendmail(fromaddr, toaddrs, message)
                server.quit()

        except:
            pass