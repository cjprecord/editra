# -*- coding: utf-8 -*-
# Name: FindResultsList.py
# Purpose: ModuleFinder plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: FindResultsList.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#----------------------------------------------------------------------------#
# Imports
import os
import wx

# Editra Libraries
import eclib

# Local Imports
from PyStudio.ModuleFinder import PythonModuleFinder
from PyStudio.Common.PyStudioUtils import PyStudioUtils

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

def GetErrorMessage(msgid):
    """Get error string from Message ID"""
    smap = { PythonModuleFinder.ERROR_NO_FINDMODULE : _("Internal Search Error"),
             PythonModuleFinder.ERROR_UNKNOWN : _("Unknown Error") }
    return smap.get(msgid, _("Unknown Error"))

def GetInfoMessage(msgid, data):
    """Get an information message
    @param msgid: message ID
    @param data: message data string

    """
    smap = { PythonModuleFinder.INFO_USED_PATH : _("INFO: Using PYTHONPATH + %s"),
             PythonModuleFinder.INFO_COMMAND_LINE : _("INFO: PyFind command line: %s"),
             PythonModuleFinder.INFO_DIRVARS : _("INFO: Directory Variables file: %s") }
    msg = smap.get(msgid, u"%s")
    return msg % data

#----------------------------------------------------------------------------#

class FindResultsList(eclib.EBaseListCtrl):
    """List control for displaying breakpoints results"""
    def __init__(self, parent):
        super(FindResultsList, self).__init__(parent)

        # Setup
        self.InsertColumn(0, _("File"))

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivate)

    def set_mainwindow(self, mw):
        self._mainw = mw

    def OnItemActivate(self, evt):
        """Go to the file"""
        idx = evt.GetIndex()
        fname = self.GetItem(idx, 0).GetText()
        if os.path.exists(fname):
            PyStudioUtils.GetEditorOrOpenFile(self._mainw, fname)

    def Clear(self):
        """Delete all the rows """
        self.DeleteAllItems()

    def PopulateRows(self, data):
        """Populate the list with the data
        @param data: PythonModuleFinder.FindResults

        """
        has_err = len(data.Errors)
        for info in data.Info:
            if len(info) == 2:
                msg = GetInfoMessage(info[0], info[1])
                self.Append((msg,))

        if has_err:
            for err in data.Errors:
                if isinstance(err, int):
                    err = GetErrorMessage(err)
                self.Append((err,))
        else:
            for eText in data.Results:
                eText = unicode(eText).rstrip()
                self.Append((eText,))
