# -*- coding: utf-8 -*-
# Name: PyToolsUtils.py
# Purpose: Utility functions
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Utility functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: PyToolsUtils.py 1081 2011-02-22 15:52:37Z CodyPrecord $"
__revision__ = "$Revision: 1081 $"

#-----------------------------------------------------------------------------#
# Imports
import ebmlib
import os.path
import wx

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

class PyToolsUtils():
    @staticmethod
    def get_packageroot(filepath):
        # traverse downwards until we are out of a python package
        fullPath = os.path.abspath(filepath)
        parentPath, childPath = os.path.dirname(fullPath), os.path.basename(fullPath)

        while parentPath != "/" and os.path.exists(os.path.join(parentPath, '__init__.py')):
            childPath = os.path.join(os.path.basename(parentPath), childPath)
            parentPath = os.path.dirname(parentPath)
        return (childPath, parentPath)

    @staticmethod
    def get_modulepath(childPath):
        return os.path.splitext(childPath)[0].replace(os.path.sep, ".")

    @staticmethod
    def GetDefaultPython():
        if wx.Platform == "__WXMSW__":
            pythonpath = ebmlib.Which("python.exe")
        else:
            pythonpath = ebmlib.Which("python")
        if pythonpath:
            return pythonpath
        return u""

    @staticmethod
    def GetDefaultScript(script, pythonpath=None):
        if wx.Platform == "__WXMSW__":
            path = ebmlib.Which("%s.bat" % script)
        else:
            path = ebmlib.Which(script)
        if path:
            return path
        if pythonpath:
            path = os.path.dirname(pythonpath)
            if wx.Platform == "__WXMSW__":
                path = os.path.join(path, "Scripts", script)
            else:
                path = "/usr/local/bin/%s" % script
            if os.path.isfile(path):
                return path
        return u""
