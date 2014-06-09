__author__ = 'Dario'

import wx
import FrameMYR


if __name__ == "__main__":
    #sys.stdout = open('myriad_output.log', 'w')
    #sys.stderr = open('myriad_error.log', 'w')
    #warnings.simplefilter('ignore', DeprecationWarning)

    app = wx.App(False)
    frame = FrameMYR.FrameMYR()
    app.MainLoop()