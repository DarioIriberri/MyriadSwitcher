from cx_Freeze import setup, Executable
#import sys
#sys.path.append("/src")
#sys.path.append("/notebook")
#sys.path.append("/difficulty")
#sys.path.append("/switcher")
#sys.path.append("/src/notebook")
#sys.path.append("/src/difficulty")
#sys.path.append("/src/switcher")
import FrameMYR

currentRevision = FrameMYR.REVISION

f = open('FrameMYR.py')
lines = f.readlines()
f.close()

for i in range(0, len(lines)):
    if lines[i].startswith("REVISION"):
        lines[i] = "REVISION = " + str(currentRevision + 1) + "\n"
        break

f = open('FrameMYR.py', 'w')
f.writelines(lines)
f.close()


#setup(
#    name = "Myriad Switcher",
#    version = FrameMYR.FrameMYR.getVersion(),
#    description = "A Myriadcoin Auto-switching mining software",
#    #author="Dario Iriberri",
#    executables = [Executable("MyriadSwitcherGUI.pyw", base = "Win32GUI",icon="myriadS1.ico")]
#    )




