__author__ = 'Dario'

import wx
import MainConfigTab
import SwitchingModesTab
import Miscellaneous
import json
import copy
import io


class NotebookMYR(wx.Notebook):
    # --------------------  CONSTANTS  ------------------------------
    ALL_TABS    = 7
    MAIN_TAB    = 1
    SWITCH_TAB  = 2
    MISC_TAB    = 4

    NOTEBOOK_SIMPLE_TYPE = 1439
    NOTEBOOK_DUAL_TYPE   = 2439
    NOTEBOOK_TRIPLE_TYPE = 3439

    WIDTH_DUAL_PANELS = 1000
    WIDTH_TRIPLE_PANELS = 1600

    WIDTHS = [WIDTH_DUAL_PANELS, WIDTH_TRIPLE_PANELS]
    NOTEBOOKS = {}

    STATUS_SIMPLE = 1
    STATUS_DUAL   = 2
    STATUS_TRIPLE = 3

    DICT_TYPE = {}
    DICT_TYPE[STATUS_SIMPLE] = NOTEBOOK_SIMPLE_TYPE
    DICT_TYPE[STATUS_DUAL]   = NOTEBOOK_DUAL_TYPE
    DICT_TYPE[STATUS_TRIPLE] = NOTEBOOK_TRIPLE_TYPE

    def __init__(self, parent, frame_myr_p, sizer=None, border=4, expandable=True, type=NOTEBOOK_SIMPLE_TYPE, tab_flags=ALL_TABS, id=1123):
        wx.Notebook.__init__(self, parent, id=id, style=
        wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
        )

        #if id != wx.ID_ANY:
        #    self.NOTEBOOK_SIMPLE_TYPE = id

        global frame_myr
        frame_myr = frame_myr_p

        self.expandable = expandable

        self.il = wx.ImageList(16, 16)
        self.AssignImageList(self.il)

        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

        self.sizer = sizer
        self.id  = id
        self.type  = type
        self.tab_flags = tab_flags

        #self.print_object()

        notebook = self.buildTabs(tab_flags)
        self.sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, border)

        if expandable:
            notebookDualPanels = []
            notebookDualPanels.append(NotebookMYR(parent, frame_myr, sizer, border, expandable=False, type=self.NOTEBOOK_DUAL_TYPE, tab_flags=NotebookMYR.MAIN_TAB, id=21))
            notebookDualPanels.append(NotebookMYR(parent, frame_myr, sizer, border, expandable=False, type=self.NOTEBOOK_DUAL_TYPE, tab_flags=NotebookMYR.SWITCH_TAB | NotebookMYR.MISC_TAB, id=223))
            self.NOTEBOOKS[self.STATUS_DUAL] = notebookDualPanels

            notebookTriplePanels = []
            notebookTriplePanels.append(NotebookMYR(parent, frame_myr, sizer, border, expandable=False, type=self.NOTEBOOK_TRIPLE_TYPE, tab_flags=NotebookMYR.MAIN_TAB, id=31))
            notebookTriplePanels.append(NotebookMYR(parent, frame_myr, sizer, border, expandable=False, type=self.NOTEBOOK_TRIPLE_TYPE, tab_flags=NotebookMYR.SWITCH_TAB, id=32))
            notebookTriplePanels.append(NotebookMYR(parent, frame_myr, sizer, border, expandable=False, type=self.NOTEBOOK_TRIPLE_TYPE, tab_flags=NotebookMYR.MISC_TAB, id=33))
            self.NOTEBOOKS[self.STATUS_TRIPLE] = notebookTriplePanels

        parent.SetSizer(sizer)
        frame_size = frame_myr.GetSize()
        self.expansionStatus = self.getExpansionStatus(frame_size)

        if expandable:
            frame_myr.Bind(wx.EVT_SIZE, self.OnResize)

        self.prev_size = frame_size

        self.NOTEBOOKS[self.STATUS_SIMPLE] = [self]

    def print_object(self):
        print ("id = " + str(self.id) + "  ---  type = " + str(self.type) + "  ---  tab_flags = " + str(self.tab_flags))

    def buildTabs(self, tab_flags):
        i = 0
        if tab_flags & self.MAIN_TAB:
            self.tabMainConfig = MainConfigTab.TabPanel(self, frame_myr)
            self.AddPage(self.tabMainConfig, "Main Config")
            self.SetPageImage(i, self.il.Add(wx.Bitmap('img/aquachecked.ico', wx.BITMAP_TYPE_ICO)))

            i += 1

        if tab_flags & self.SWITCH_TAB:
            self.tabSwitchModes = SwitchingModesTab.TabPanel(self, frame_myr)
            self.AddPage(self.tabSwitchModes, "Switching Modes")
            self.SetPageImage(i, self.il.Add(wx.Bitmap('img/switching16.ico', wx.BITMAP_TYPE_ICO)))

            i += 1

        if tab_flags & self.MISC_TAB:
            self.tabMiscellaneous = Miscellaneous.TabPanel(self, frame_myr)
            self.AddPage(self.tabMiscellaneous, "Miscellaneous")
            self.SetPageImage(i, self.il.Add(wx.Bitmap('img/advanced.ico', wx.BITMAP_TYPE_ICO)))

        return self

    # Method to save the panel data into the currently active config file
    def saveConfig(self, activeFile):
        if self.expansionStatus != 1:
            self.transferData(self.expansionStatus, 1)

        if not self.checkFilesExist():
            return False

        string_out = self.getConfigText()

        #f = open(activeFile, "w")
        f = io.open(activeFile, 'wt', encoding='utf-8').write(string_out.replace("\\", "\\\\"))
        #f.write(string_out.replace("\\", "\\\\"))
        #f.close()
        return True

    def checkFilesExist(self):
        #if self.expansionStatus != 1:
        #    self.transferData(self.expansionStatus, 1)
        return self.tabMainConfig.checkFilesExist() and self.tabMiscellaneous.checkFilesExist()

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        event.Skip()

    #todo Get defaults from each panel
    def loadDefaults(self):
        defaults = {
                "scryptBatchFile"		: 	"",
                "groestlBatchFile"		: 	"",
                "skeinBatchFile"		: 	"",
                "qubitBatchFile"		: 	"",
                "logActive"				: 	0,
                "logPath"				: 	"",
                "mode"					: 	1,
                "sleepSHORT"			: 	3,
                "sleepLONG"				:	5,
                "hysteresis"			:	0,
                "minTimeNoHysteresis"	: 	9999,
                "rampUptime"			: 	10,
                "scryptHashRate"		: 	1,
                "groestlHashRate"		: 	14,
                "skeinHashRate"			: 	300,
                "qubitHashRate"			: 	7,
                "globalCorrectionFactor": 	95,
                "scryptFactor"			: 	1,
                "groestlFactor"			: 	1,
                "skeinFactor"			: 	1,
                "qubitFactor"			: 	1,
                "scryptWatts"			: 	480,
                "groestlWatts"			: 	270,
                "skeinWatts"			: 	430,
                "qubitWatts"			: 	280,
                "idleWatts"				: 	100,
                "minCoins"				: 	0,
                "attenuation"		    : 	500,
                "timeout"				: 	30,
                "sleepSHORTDebug"		: 	20,
                "sleepLONGDebug"		: 	20,
                "exchange"				: 	"\"mintpal\"",
                "debug"					: 	0,
                "monitor"				: 	1,
                "reboot"				: 	0,
                "maxErrors"				: 	5,
                "rebootIf"				: 	"crashes or freezes"
        }

        self.loadAllConfigDict(defaults)

    # Loads the data in config_json into all the instance notebooks and their tabs
    def loadAllConfigDict(self, config_json):
        self.loadTabs(config_json)

        if self.expandable:
            for i in range (2, len(self.NOTEBOOKS) + 1):
                nb = self.NOTEBOOKS[i]
                for nbsub in nb:
                    nbsub.loadTabs(config_json)

    # Method to load the current active configuration file data into the panels
    def loadConfig(self, activeFile):
        try :
            f = open(activeFile)
            config = f.read()
            f.close()

            self.loadConfigText(config)

            if self.expandable:
                for i in range (2, len(self.NOTEBOOKS) + 1):
                    nb = self.NOTEBOOKS[i]
                    for nbsub in nb:
                        nbsub.loadConfig(activeFile)

        except:
            dlg = wx.MessageDialog(self, 'The config file ' + activeFile + " is unreadable.",
                                       'Configuration Error',
                                       wx.OK | wx.ICON_ERROR
                                       #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
            )

            dlg.ShowModal()
            dlg.Destroy()

            return False

            #self.loadDefaults()
        return True

    def loadTabs(self, config_json):
        for i in range(0, self.GetPageCount()):
            page = self.GetPage(i)
            page.set_json(config_json)

    def loadConfigMultiDict(self, notebooks):
        config_json = dict()

        for notebook in notebooks:
            config_json.update(notebook.getConfigDict())

        self.loadTabs(config_json)

        return config_json

    def loadConfigText(self, textConfig):
        config_json = json.loads(textConfig)

        self.loadTabs(config_json)

    def getConfigDict(self):
        config_json = dict()

        for i in range(0, self.GetPageCount()):
            page = self.GetPage(i)
            config_json.update(page.get_json())

        return config_json

    def getConfigText(self):
        config_json = self.getConfigDict()
        string_out = "{\n"

        for i, (key, value) in enumerate(config_json.iteritems()):
            key_str = "\"" + key + "\""

            if type(value) is unicode or type(value) is str:
                string_out += ( key_str + " : \"" + value + "\"")

            else:
                if type(value) is bool:
                    string_out += ( key_str + " : " + str(int(value)))

                else:
                    if type(value) is int or float:
                        string_out += ( key_str + " : " + str(value))

            if not ( i == len(config_json) -1 ) :
                string_out += ", "

            string_out += "\n"

        string_out += "}"

        return string_out

    def get_type(self):
        return self.type

    # Displays the notebook in compact or separated mode depending on the window width
    def show_notebook(self):
        active_type = self.DICT_TYPE[self.expansionStatus]
        for child in self.sizer.GetChildren():
            if active_type != child.GetWindow().get_type():
                child.Show(False)
            else:
                child.Show(True)

        frame_myr.Layout()

    def OnResize(self, event):
        if not self.expandable:
            return

        new_expansion_status = self.getExpansionStatus(frame_myr.GetSize())

        if self.expansionStatus == new_expansion_status:
            event.Skip()
            return

        self.transferData(self.expansionStatus, new_expansion_status)

        self.expansionStatus = new_expansion_status
        self.show_notebook()
        self.Layout()
        frame_myr.Layout()

        event.Skip()

    def transferData(self, source, destination):
        source_notebooks = self.NOTEBOOKS[source]
        destination_notebooks = self.NOTEBOOKS[destination]

        for nb in destination_notebooks:
            nb.loadConfigMultiDict(source_notebooks)


    def getExpansionStatus(self, size):
        width = size[0]
        array_widths = copy.deepcopy(self.WIDTHS)
        array_widths.append(width)
        array_widths.sort()

        for i in range(0, len(array_widths)):
            if array_widths[i] == width:
                return i + 1

        return 0