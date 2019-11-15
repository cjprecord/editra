# -*- coding: utf-8 -*-
# Name: FindShelfWindow.py
# Purpose: ModuleFinder plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: FindShelfWindow.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path
import wx

# Editra Libraries
import ed_glob
import util
import eclib
import ed_msg
from syntax import syntax
import syntax.synglob as synglob

# Local imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.BaseShelfWindow import BaseShelfWindow
from PyStudio.ModuleFinder.FindResultsList import FindResultsList
from PyStudio.ModuleFinder.PythonModuleFinder import PythonModuleFinder

# Globals
_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class FindShelfWindow(BaseShelfWindow):
    """Module Find Results Window"""
    __moduleFinders = {
        synglob.ID_LANG_PYTHON: PythonModuleFinder
    }

    def __init__(self, parent):
        """Initialize the window"""
        super(FindShelfWindow, self).__init__(parent)

        # Setup
        ctrlbar = self.setup(FindResultsList(self))
        ctrlbar.AddStretchSpacer()
        self.textentry = eclib.CommandEntryBase(ctrlbar, size=(256, -1),
                                                style=wx.TE_PROCESS_ENTER)
        ctrlbar.AddControl(self.textentry, wx.ALIGN_RIGHT)
        self.textentry.ToolTip = wx.ToolTip(_("Enter module name to search for"))
        self.textentry.EnterCallback = self.DoFindModule
        self.layout("Find", self.OnFindModule, self.OnJobTimer)
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FIND), wx.ART_MENU)
        self.taskbtn.SetBitmap(bmp)

        # Attributes
        self._finder = None

    def OnThemeChanged(self, msg):
        """Update Icons"""
        super(FindShelfWindow, self).OnThemeChanged(msg)
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FIND), wx.ART_MENU)
        self.taskbtn.SetBitmap(bmp)
        self.taskbtn.Refresh()

    def _onmodulefind(self, editor, moduletofind):
        self._listCtrl.Clear()

        vardict = {}
        # With the text control (ed_stc.EditraStc) this will return the full
        # path of the file or a wx.EmptyString if the buffer does not contain
        # an on disk file
        filename = editor.GetFileName()
        if filename:
            filename = os.path.abspath(filename)
            filetype = editor.GetLangId()
            directoryvariables = self.get_directory_variables(filetype)
            if directoryvariables:
                vardict = directoryvariables.read_dirvarfile(filename)

        self._findmodule(synglob.ID_LANG_PYTHON, vardict, moduletofind)
        self._hasrun = True

    def OnFindModule(self, event):
        self.DoFindModule()

    def DoFindModule(self):
        self.taskbtn.Enable(False)
        self.textentry.Enable(False)
        editor = wx.GetApp().GetCurrentBuffer()
        wx.CallAfter(self._onmodulefind, editor, self.textentry.GetValue())

    def get_module_finder(self, filetype, vardict, moduletofind):
        try:
            return self.__moduleFinders[filetype](vardict, moduletofind)
        except:
            pass
        return None

    def _findmodule(self, filetype, vardict, moduletofind):
        modulefinder = self.get_module_finder(filetype, vardict, moduletofind)
        if not modulefinder:
            return
        self._finder = modulefinder
        self._module = moduletofind

        # Start job timer
        self._StopTimer()
        self._jobtimer.Start(250, True)

    def _OnFindData(self, data):
        """Find job callback
        @param data: PythonModuleFinder.FindResults

        """
        self.taskbtn.Enable(True)
        self.textentry.Enable(True)
        self._listCtrl.PopulateRows(data)
        self._listCtrl.RefreshRows()
        mwid = self.GetMainWindow().GetId()
        ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (mwid, False))

    def OnJobTimer(self, evt):
        """Start a module find job"""
        if self._finder:
            util.Log("[PyFind][info] module %s" % self._module)
            mwid = self.GetMainWindow().GetId()
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (mwid, True))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (mwid, -1, -1))
            self._finder.Find(self._OnFindData)
