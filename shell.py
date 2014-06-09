__author__ = 'Dario'

import wx
import  wx.py

app = wx.App(False)
frm = wx.Frame(None, 400, "wxPyShell")
shell = wx.py.shell.Shell(frm)
shell.run("import os")
shell.run("import subprocess")
shell.run("subprocess.Popen([r'C:\WINDOWS\system32\WindowsPowerShell\\v1.0\powershell.exe', '-ExecutionPolicy', 'Unrestricted', './myriadSwitcher.ps1'], cwd=os.getcwd(), shell=True)")
#shell.run("subprocess.call('taskkill /im \"powershell.exe\" /f', shell=False)")
#shell.run("subprocess.call('powershell .\myriadSwitcher.ps1', shell=False)")
frm.Show()

app.MainLoop()