__author__ = 'Dario'

import wx.lib.newevent


ConsoleEvent  , EVT_CONSOLE_EVENT    = wx.lib.newevent.NewEvent()
StatusBarEvent, EVT_STATUS_BAR_EVENT = wx.lib.newevent.NewEvent()
ConfigTabEvent, EVT_CONFIG_TAB_EVENT = wx.lib.newevent.NewEvent()
DummyEvent,     EVT_DUMMY_EVENT      = wx.lib.newevent.NewEvent()