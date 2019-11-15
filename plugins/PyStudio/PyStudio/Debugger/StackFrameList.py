# -*- coding: utf-8 -*-
# Name: StackFrameList.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: StackFrameList.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#----------------------------------------------------------------------------#
# Imports
import os.path
import wx

# Editra Libraries
import util
import eclib

# Local Imports
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger
from PyStudio.Common.PyStudioUtils import PyStudioUtils

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class StackFrameList(eclib.EBaseListCtrl):
    """List control for displaying stack frame results"""
    COL_FRAME = 0
    COL_FILE = 1
    COL_LINE = 2
    COL_FUNCT = 3
    
    def __init__(self, parent):
        super(StackFrameList, self).__init__(parent)

        # Setup
        self.colname_frame = _("Frame")
        self.colname_file = _("File")
        self.colname_line = _("Line")
        self.colname_funct = _("Function")

        self.InsertColumn(StackFrameList.COL_FRAME, self.colname_frame)
        self.InsertColumn(StackFrameList.COL_FILE, self.colname_file)
        self.InsertColumn(StackFrameList.COL_LINE, self.colname_line)
        self.InsertColumn(StackFrameList.COL_FUNCT, self.colname_funct)
        if wx.Platform == '__WXMAC__':
            self.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        # Attributes
        self.previndex = None

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFrameSelected)

    def set_mainwindow(self, mw):
        self._mainw = mw

    def select_frame(self, index):
        """Select a frame in the ListCtrl"""
        if (index < 0) or (index > self.GetItemCount() or self.IsSelected(index)):
            return
        self.Select(index)

    def OnFrameSelected(self, evt):
        index = evt.GetIndex()
        if self.previndex == index:
            return
        filename = self.GetItem(index, StackFrameList.COL_FILE).GetText()
        if index > self.GetItemCount() - 4:
            if filename and os.path.basename(filename) == "rpdb2.py":
                return
        self.previndex = index
        RpdbDebugger().set_frameindex(index)

        if not filename:
            return
        editor = PyStudioUtils.GetEditorOrOpenFile(self._mainw, filename)
        if editor:
            try:
                lineno = int(self.GetItem(index, StackFrameList.COL_LINE).GetText())
                editor.GotoLine(lineno - 1)
            except ValueError:
                util.Log("[PyStudio][err] StackFrame: failed to jump to file")

    def Clear(self):
        """Delete all the rows """
        self.DeleteAllItems()
        self.previndex = None

    def PopulateRows(self, data):
        """Populate the list with the data
        @param data: dictionary of stack info

        """
        idx = 0
        while idx < len(data):
            frameinfo = data[-(1 + idx)]

            filename = os.path.normcase(frameinfo[0])
            lineno = frameinfo[1]
            function = frameinfo[2]

            self.Append((unicode(idx), unicode(filename), unicode(lineno), unicode(function)))
            if idx < len(data) - 3:
                enable = True
            elif os.path.basename(filename) == "rpdb2.py":
                enable = False
            else:
                enable = True
            self.EnableRow(idx, enable=enable)
            idx += 1

        self.SetColumnWidth(StackFrameList.COL_FILE, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(StackFrameList.COL_FUNCT, wx.LIST_AUTOSIZE)
        filenamecolwidth = max(self.GetTextExtent(self.colname_file + "          ")[0], self.GetColumnWidth(StackFrameList.COL_FILE))
        functcolwidth = max(self.GetTextExtent(self.colname_funct + "          ")[0], self.GetColumnWidth(StackFrameList.COL_FUNCT))
        self.SetColumnWidth(StackFrameList.COL_FILE, filenamecolwidth)
        self.SetColumnWidth(StackFrameList.COL_FUNCT, functcolwidth)
        self.previndex = None
        self.Select(0)
