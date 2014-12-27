__author__ = 'Dario'

import wx
import json
import copy
import io
import os
import wx.lib.newevent

NotebookBroadcastEvent, EVT_NOTEBOOK_BROADCAST_EVENT = wx.lib.newevent.NewEvent()

class ExpandableNotebook(wx.Notebook):
    def __init__(self, parent, parent_window, border=2, expandable=True, activeFile='ExpandableNotebook.conf', expansion=1, sizer=None):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_TOP
                             #wx.BK_DEFAULT
                             #wx.BK_TOP
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
        )

        self.WIDTHS = []
        self.NOTEBOOKS = {}
        self.TABS = []
        self.TAB_MEMBERS = []

        self.parent_window = parent_window

        self.expandable = expandable
        self.parent  = parent
        self.border = border
        self.expansion  = expansion

        self.activeFile = None

        #init config

        if expansion == 1:
            f = open('activeConfig')
            lines = f.readlines()
            f.close()

            if (lines and len(lines) > 0):
                self.activeFile = lines[0]
            else:
                self.activeFile = activeFile

            self.workingDir = os.getcwd()

        else:
            self.activeFile = activeFile

        self.il = wx.ImageList(16, 16)
        self.AssignImageList(self.il)

        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

        self.sizer = sizer if sizer else wx.BoxSizer(wx.HORIZONTAL)

    def addTab(self, tabClass, tabTitle, tabIcon):
        """Add a new NotebookTab to the Notebook.

        Passing the tab class, the tab title, and the tab icon. """
        self.TAB_MEMBERS.append(_TabMember(tabClass, tabTitle, tabIcon))

    def buildNotebook(self):
        """After the contructor and addig the tabs, call this method to get the Notebook ready. """
        self.__buildExpandedNotebooks(0, len(self.TAB_MEMBERS))

        #set widths for expanding / resizing purposes
        increment = int((wx.GetDisplaySize()[0] * 0.75) / len(self.TAB_MEMBERS))
        for width in range (increment * 2, wx.GetDisplaySize()[0], increment):
            if len(self.WIDTHS) == len(self.TAB_MEMBERS) - 1:
                break

            self.WIDTHS.append(width)

        self.loadConfig()

    #def broadcast_bind(self, parent, event, instance=None, *args, **kwargs):
    #    parent.Bind(event, lambda event: self.broadcastEventToAllTabs(event, *args, **kwargs), instance)
    #
    #def broadcastEventToAllTabs(self, event=None, *args, **kwargs):
    #    for expansion, nbs in self.NOTEBOOKS.iteritems():
    #        for nb in nbs:
    #            for tab in nb.TABS:
    #                obj = event.EventObject if event else None
    #                #wx.PostEvent(tab, NotebookBroadcastEvent(broadcast_event=event, event_id=event_id))
    #                wx.PostEvent(tab, NotebookBroadcastEvent(broadcast_obj=obj, *args, **kwargs))
    #                #wx.PostEvent(tab, NotebookBroadcastEvent(broadcast_event=event.EventObject.GetValue(), event_id=event_id))

    def broadcastBind(self, parent, event, instance=None, event_id=None, event_value=None):
        parent.Bind(event, lambda event: self.broadcastEventToAllTabs(event, event_id, event_value), instance)

    def broadcastEventToAllTabs(self, event=None, event_id=None, event_value=None):
        value = event_value
        try:
            obj = event.GetEventObject()
            value = obj.GetValue()

        except AttributeError:
            obj = event

        for expansion, nbs in self.NOTEBOOKS.iteritems():
            for nb in nbs:
                for tab in nb.TABS:
                    wx.PostEvent(tab, NotebookBroadcastEvent(broadcast_obj=obj, event_id=event_id, event_value=value))

        #event.Skip()

    def notebookControlChanged(self, event=None):
        self.parent_window.notebookControlChanged(event)

    def loadDefaults(self):
        """Loads all tabs with default values"""
        for expansion, nbs in self.NOTEBOOKS.iteritems():
            for nb in nbs:
                for tab in nb.TABS:
                    tab.loadDefaults()

        #self.__loadNotebooksFromJson(defaults)

    # Method to load the current active configuration file data into the panels
    def loadConfig(self, activeFile=None):
        """Load the current active configuration file data into the panels.

        Passing the active configuration file name. """
        try :
            activeFile = activeFile if activeFile else self.activeFile

            f = open(activeFile)
            config = f.read()
            f.close()

            self.__loadTabsFromString(config)

            if self.expandable:
                for i in range (2, len(self.NOTEBOOKS) + 1):
                    nb = self.NOTEBOOKS[i]
                    for nbsub in nb:
                        nbsub.loadConfig(activeFile)

        except:
            return self.__configError()

        return json.loads(config)

    def openConfig(self):
        dlg = wx.FileDialog(self, "Choose a file", self.workingDir, os.getcwd(), "*.conf", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            #f = open(os.path.join(dirname, filename), 'r')
            activeFile = filename
            #f.close()

            if self.loadConfig(dirname + "\\" + activeFile):
                #self.activeFile = activeFile
                self.__save_active_file(self.activeFile)

                return activeFile

        dlg.Destroy()

        return False

    # Method to save the panel data into the currently active config file
    def saveConfig(self, extraParams=None):
        """Save the current Notebook data to a configuration file in json format.

        Passing the active configuration file name. """
        if self.expansionStatus != 1:
            self.__transferSubNotebookData(self.expansionStatus, 1)

        if not self.__checkFilesExist():
            return False

        config_json = self.__getConfigJson()

        if extraParams:
            config_json.update(extraParams)

        string_out = json.dumps(config_json)

        #io.open(self.activeFile, 'wt', encoding='utf-8').write(string_out.replace("\\", "\\\\"))
        io.open(self.activeFile, 'wt', encoding='utf-8').write(unicode(string_out))

        return True

    # Method to save the panel data into the currently active config file
    def saveConfigAs(self, extraParams=None):
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=self.workingDir,
            defaultFile=self.activeFile, wildcard="*.conf", style=wx.SAVE | wx.OVERWRITE_PROMPT
        )
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            #f = open(os.path.join(self.dirname, filename), 'r')
            activeFile = filename
            #f.close()

            if self.saveConfig(activeFile):
                #self.activeFile = activeFile
                self.workingDir = dirname
                self.__save_active_file(activeFile)

                return activeFile

        dlg.Destroy()

        return False

    def getDefaultConfigJson(self):
        return self.GetPage(0).get_default_values()

    def getTempConfigJson(self):
        return self.__getConfigJson()

    def getStoredConfigJson(self):
        try:
            f = open(self.activeFile)
            config = f.read()
            f.close()

        except IOError:
            return None

        try:
            config_json = json.loads(config)

        except ValueError:
            return self.__configError()

        return config_json

    def getTempConfigParam(self, param):
        try:
            config_json = self.__getConfigJson()
            return config_json[param]

        except KeyError:
            return None

    def getStoredConfigParam(self, param):
        config_json = self.getStoredConfigJson()

        try:
            return config_json[param]

        except (KeyError, TypeError):
            return None

    def getParentWindow(self):
        return self.parent_window


    ####################################################################################################################
    ############################################  PRIVATE MEMBERS   ####################################################
    ####################################################################################################################


    def __buildExpandedNotebooks(self, start, length, tabMembers = None):
        if tabMembers:
            self.TAB_MEMBERS = tabMembers

        notebook = self.__buildTabs(start, length)
        self.sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, self.border)

        #build sub notebooks
        if self.expandable:
            for expansion in range (2, len(self.TAB_MEMBERS) + 1):
                sub_notebooks = []

                #single tab sub-notebooks
                for single_nb in range (0, expansion - 1):
                    nb = ExpandableNotebook(self.parent, self.parent_window, self.border, expandable=False, activeFile=self.activeFile, expansion=expansion, sizer=self.sizer)
                    sub_notebooks.append(nb.__buildExpandedNotebooks(single_nb, 1, self.TAB_MEMBERS))

                #another sub-notebook with the rest of the tabs
                rest_start = expansion - 1
                rest_length = len(self.TAB_MEMBERS) - expansion + 1
                nb = ExpandableNotebook(self.parent, self.parent_window, self.border, expandable=False, activeFile=self.activeFile, expansion=expansion, sizer=self.sizer)
                sub_notebooks.append(nb.__buildExpandedNotebooks(rest_start, rest_length, self.TAB_MEMBERS))

                self.NOTEBOOKS[expansion] = sub_notebooks

        self.parent.SetSizer(self.sizer)
        frame_size = self.parent_window.GetSize()
        self.expansionStatus = self.__calculateExpansionStatus(frame_size)

        if self.expandable:
            self.parent_window.Bind(wx.EVT_SIZE, self.__onResize)

        self.prev_size = frame_size

        self.NOTEBOOKS[1] = [self]

        self.__show_notebook()

        return self

    def __buildTabs(self, start, length):
        count = 0

        for i in range(start, start + length):
            current_tab = self.TAB_MEMBERS[i]

            tabInstance = current_tab.tabClass(self)
            self.AddPage(tabInstance, current_tab.tabTitle)
            self.SetPageImage(count, self.il.Add(wx.Bitmap(current_tab.tabIcon, wx.BITMAP_TYPE_ICO)))

            self.TABS.append(tabInstance)

            count += 1

        return self

    # Changes the active config file
    def __save_active_file(self, activeFile):
        self.activeFile = activeFile
        f = open("activeConfig", "w")
        f.write(activeFile)
        f.close()

    #For tabs with file browsers, checks if files exist before saving
    def __checkFilesExist(self):
        for tab in self.TABS:
            if not tab.check_files_exist():
                return False

        return True

    # Loads the data in config_json into all the instance notebooks and their tabs
    def __loadNotebooksFromJson(self, config_json):
        self.__loadTabsFromJson(config_json)

        if self.expandable:
            for i in range (2, len(self.NOTEBOOKS) + 1):
                nb = self.NOTEBOOKS[i]
                for nbsub in nb:
                    nbsub.__loadTabsFromJson(config_json)

    def __loadTabsFromJson(self, config_json):
        #self.tabMainConfig.set_json(config_json)
        #self.tabSwitchModes.set_json(config_json)
        #self.tabMiscellaneous.set_json(config_json)

        for i in range(0, self.GetPageCount()):
            page = self.GetPage(i)
            page.set_json(config_json)

    def __loadTabsFromNotebooks(self, notebooks):
        config_json = dict()

        for notebook in notebooks:
            config_json.update(notebook.__getConfigJson())

        self.__loadTabsFromJson(config_json)

        return config_json

    def __loadTabsFromString(self, textConfig):
        config_json = json.loads(textConfig)

        self.__loadTabsFromJson(config_json)

    def __getConfigJson(self):
        if self.expansionStatus != 1:
            self.__transferSubNotebookData(self.expansionStatus, 1)

        config_json = dict()

        for i in range(0, self.GetPageCount()):
            page = self.GetPage(i)
            config_json.update(page.get_json())

        return config_json

    def __configError(self):
        dlg = wx.MessageDialog(self, 'The config file ' + self.activeFile + " is unreadable. Using defaults",
                                   'Configuration Error',
                                   wx.OK | wx.ICON_ERROR
                                   #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
        )

        dlg.ShowModal()
        dlg.Destroy()

        config_json = self.getDefaultConfigJson()
        self.__loadNotebooksFromJson(config_json)

        self.saveConfig()

        return config_json

    def __get_expansion(self):
        return self.expansion

    # Displays the notebook in compact or separated mode depending on the window width
    def __show_notebook(self):
        active_type = self.expansionStatus
        #active_type = self.DICT_TYPE[self.expansionStatus]
        for child in self.sizer.GetChildren():
            if active_type != child.GetWindow().__get_expansion():
                child.Show(False)
            else:
                child.Show(True)

        self.parent_window.Layout()

    def __onResize(self, event):
        if not self.expandable:
            return

        new_expansion_status = self.__calculateExpansionStatus(self.parent_window.GetSize())

        if self.expansionStatus == new_expansion_status:
            event.Skip()
            return

        self.__transferSubNotebookData(self.expansionStatus, new_expansion_status)

        self.expansionStatus = new_expansion_status
        self.__show_notebook()
        self.Layout()
        self.parent_window.Layout()

        event.Skip()

    def __transferSubNotebookData(self, source, destination):
        source_notebooks = self.NOTEBOOKS[source]
        destination_notebooks = self.NOTEBOOKS[destination]

        for nb in destination_notebooks:
            nb.__loadTabsFromNotebooks(source_notebooks)


    def __calculateExpansionStatus(self, size):
        width = size[0]
        array_widths = copy.deepcopy(self.WIDTHS)
        array_widths.append(width)
        array_widths.sort()

        for i in range(0, len(array_widths)):
            if array_widths[i] == width:
                return i + 1

        return 0

class _TabMember():
    def __init__(self, tabClass, tabTitle, tabIcon):
        self.tabClass = tabClass
        self.tabTitle    = tabTitle
        self.tabIcon     = tabIcon