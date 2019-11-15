# -*- coding: utf-8 -*-
# Name: ProcessCreator.py
# Purpose: Create processes
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Utility functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: ProcessCreator.py 1408 2011-06-08 17:55:29Z rans@email.com $"
__revision__ = "$Revision: 1408 $"

#-----------------------------------------------------------------------------#
# Imports
import sys
import os.path
from subprocess import Popen, PIPE
import wx

# Editra Libraries
import util
#-----------------------------------------------------------------------------#

if wx.Platform == "__WXMSW__":
    try:
        from win32process import CREATE_NO_WINDOW
    except ImportError:
        CREATE_NO_WINDOW = 0x08000000

class ProcessCreator(object):
    def __init__(self, info, parentPath, cmdline, pythonpath=None):
        super(ProcessCreator, self).__init__()

        self.info = info
        self.parentPath = parentPath
        self.cmdline = cmdline
        self.pythonpath = pythonpath
        if wx.Platform == "__WXMSW__":
            self.creationflags = CREATE_NO_WINDOW
            self.environment = None
            self.curpath = self.get_pythonpath()
        else:
            self.creationflags = 0
            self.environment = {}
            self.curpath = None

    @staticmethod
    def get_pythonpath():
        if os.environ.has_key("PYTHONPATH"):
            return os.getenv("PYTHONPATH")
        return None

    @staticmethod
    def get_path():
        if os.environ.has_key("PATH"):
            return os.getenv("PATH")
        return ""

    def createprocess(self, stderr=PIPE):
        if self.pythonpath:
            if wx.Platform == "__WXMSW__":
                os.environ["PYTHONPATH"] = os.pathsep.join(self.pythonpath)
            else:
                self.environment["PYTHONPATH"] = str(os.pathsep.join(self.pythonpath))
        if wx.Platform != "__WXMSW__":
            self.environment["PATH"] = str(self.get_path())
            # If not frozen binary inherit the shell environment
            if not getattr(sys, 'frozen', False):
                self.environment.update(os.environ)

        cmdline = [ cmd.encode(sys.getfilesystemencoding())
                       for cmd in self.cmdline ]
        parentPath = self.parentPath.encode(sys.getfilesystemencoding())
        util.Log("[%s][info] Using CWD: %s" % (self.info, parentPath))
        util.Log("[%s][info] Starting command: %s" % (self.info, repr(cmdline)))
        return Popen(cmdline,
                    bufsize=1048576, stdout=PIPE, stderr=stderr,
                    cwd=parentPath, env=self.environment,
                    creationflags=self.creationflags)

    def restorepath(self):
        if wx.Platform == "__WXMSW__" and self.curpath:
            os.environ["PYTHONPATH"] = self.curpath
