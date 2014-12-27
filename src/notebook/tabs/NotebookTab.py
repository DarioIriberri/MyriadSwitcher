__author__ = 'Dario'

import wx
from notebook.ExpandableNotebookTab import ExpandableNotebookTab


DEFAULTS = {
                "scryptBatchFile"		: 	"",
                "groestlBatchFile"		: 	"",
                "skeinBatchFile"		: 	"",
                "qubitBatchFile"		: 	"",
                "scryptPool"            :   "stratum+tcp://birdspool.no-ip.org:5556",
                "groestlPool"           :   "stratum+tcp://birdspool.no-ip.org:3333",
                "skeinPool"             :   "stratum+tcp://birdspool.no-ip.org:5589",
                "qubitPool"             :   "stratum+tcp://birdspool.no-ip.org:5567",
                "scryptPoolData" : [
                                        {
                                            "url" : "stratum+tcp://birdspool.no-ip.org:5556",
                                            "user" : None,
                                            "pass" : "x",
                                            "poolBalanceUrl" : "http://birdonwheels5.no-ip.org:3000/address/"
                                        }
                                    ],
                "groestlPoolData" : [
                                        {
                                            "url" : "stratum+tcp://birdspool.no-ip.org:3333",
                                            "user" : None,
                                            "pass" : "x",
                                            "poolBalanceUrl" : "http://birdonwheels5.no-ip.org:3000/address/"
                                        }
                                    ],
                "skeinPoolData" : [
                                        {
                                            "url" : "stratum+tcp://birdspool.no-ip.org:5589",
                                            "user" : None,
                                            "pass" : "x",
                                            "poolBalanceUrl" : "http://birdonwheels5.no-ip.org:3000/address/"
                                        }
                                    ],
                "qubitPoolData" : [
                                        {
                                            "url" : "stratum+tcp://birdspool.no-ip.org:5567",
                                            "user" : None,
                                            "pass" : "x",
                                            "poolBalanceUrl" : "http://birdonwheels5.no-ip.org:3000/address/"
                                        }
                                    ],
                "logActive"				: 	0,
                "logPath"				: 	"",
                "mode"					: 	1,
                "sleepSHORT"			: 	3,
                "sleepLONG"				:	5,
                "hysteresis"			:	0,
                "minTimeNoHysteresis"	: 	9999,
                "rampUptime"			: 	5,
                "scryptHashRate"		: 	1,
                "groestlHashRate"		: 	14,
                "skeinHashRate"			: 	300,
                "qubitHashRate"			: 	7,
                "globalCorrectionFactor": 	95,
                "mainMode"			    : 	"simple",
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
                "exchange"				: 	"\"cryptsy\"",
                "debug"					: 	0,
                "monitor"				: 	1,
                "reboot"				: 	0,
                "maxErrors"				: 	5,
                "rebootIf"				: 	"crashes or freezes"
           }


class NotebookTab(ExpandableNotebookTab):
    def __init__(self, parentNotebook, id=wx.ID_ANY):
        ExpandableNotebookTab.__init__(self, parentNotebook, id)

    def loadDefaults(self):
        self.set_json(DEFAULTS)

    def get_default_values(self):
        return DEFAULTS

    def get_default_value(self, field_name):
        return DEFAULTS[field_name]

