# -*- coding: utf-8 -*-
# Name: PyToolsUtils.py
# Purpose: Utility functions
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Utility functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: ProcessRunner.py 1081 2011-02-22 15:52:37Z CodyPrecord $"
__revision__ = "$Revision: 1081 $"

#-----------------------------------------------------------------------------#

import sys
import os.path
from subprocess import Popen, PIPE
import wx

if wx.Platform == "__WXMSW__":
    try:
        from win32process import CREATE_NO_WINDOW
    except ImportError:
        CREATE_NO_WINDOW = 0x08000000

class ProcessRunner(object):
    def __init__(self, pythonpath=None):
        super(ProcessRunner, self).__init__()

        self.pythonpath = pythonpath
        if wx.Platform == "__WXMSW__":
            self.creationflags = CREATE_NO_WINDOW
            self.environment = None
            self.curpath = self.get_pythonpath()
        else:
            self.creationflags = 0
            self.environment = {}
            self.curpath = None
        self.process = None

    @staticmethod
    def get_pythonpath():
        if os.environ.has_key("PYTHONPATH"):
            return os.getenv("PYTHONPATH")
        return None

    def runprocess(self, cmdline, parentPath):
        if self.pythonpath:
            if wx.Platform == "__WXMSW__":
                os.environ["PYTHONPATH"] = os.pathsep.join(self.pythonpath)
            else:
                self.environment["PYTHONPATH"] = str(os.pathsep.join(self.pythonpath))

        cmdline = [ cmd.encode(sys.getfilesystemencoding())
                    for cmd in cmdline ]
        parentPath = parentPath.encode(sys.getfilesystemencoding())
        self.process = Popen(cmdline,
                             bufsize=1048576, stdout=PIPE, stderr=PIPE,
                             cwd=parentPath, env=self.environment,
                             creationflags=self.creationflags)

    def getalloutput(self):
        return self.process.communicate()

    def restorepath(self):
        if wx.Platform == "__WXMSW__" and self.curpath:
            os.environ["PYTHONPATH"] = self.curpath

    def terminate(self):
        try:
            self.process.terminate()
        except:
            pass
