__author__ = 'Dario'

import wx
import sys
import FrameMYR
from MainConfigTab import MainConfigTab
from SimpleConfigTab import SimpleConfigTab


if __name__ == "__main__":
    #sys.stdout = open('myriad_output.log', 'w')
    #sys.stderr = open('myriad_error.log', 'w')
    #warnings.simplefilter('ignore', DeprecationWarning)

    app = wx.App(False)
    frame = FrameMYR.FrameMYR()
    app.MainLoop()