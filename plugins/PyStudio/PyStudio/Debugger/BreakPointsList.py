# -*- coding: utf-8 -*-
# Name: BreakPointsList.py
# Purpose: ModuleFinder plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: BreakPointsList.py 1448 2011-07-24 17:17:55Z rans@email.com $"
__revision__ = "$Revision: 1448 $"

#----------------------------------------------------------------------------#
# Imports
import os
import wx

# Editra Libraries
import ed_marker
import eclib

# Local Imports
from PyStudio.Common.PyStudioUtils import PyStudioUtils

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class BreakPointsList(eclib.EToggleEditListCtrl):
    """List control for displaying breakpoints results"""
    COL_FILE = 0
    COL_LINE = 1
    COL_EXPR = 2
    
    def __init__(self, parent):
        super(BreakPointsList, self).__init__(parent)

        # Setup
        self.colname_file = _("File")
        self.colname_line = _("Line")
        self.colname_expr = _("Expression")
        self.InsertColumn(BreakPointsList.COL_FILE, self.colname_file)
        self.InsertColumn(BreakPointsList.COL_LINE, self.colname_line)
        self.InsertColumn(BreakPointsList.COL_EXPR, self.colname_expr)
        self.SetCheckedBitmap(ed_marker.Breakpoint().Bitmap)
        self.SetUnCheckedBitmap(ed_marker.BreakpointDisabled().Bitmap)

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnItemEdited)

    def set_mainwindow(self, mw):
        self._mainw = mw

    def GetSelectedBreakpoints(self):
        """Get a list of selected breakpoints
        @return: [(fname, line, expr),]

        """
        rval = list()
        for index in self.GetSelections():
            rval.append(self.GetRowData(index))
        return rval

    def OnItemActivated(self, evt):
        """Go to the file"""
        idx = evt.GetIndex()
        fileName = self.GetItem(idx, BreakPointsList.COL_FILE).GetText()
        if not fileName:
            return
        editor = PyStudioUtils.GetEditorOrOpenFile(self._mainw, fileName)
        if editor:
            try:
                lineno = int(self.GetItem(idx, BreakPointsList.COL_LINE).GetText())
                editor.GotoLine(lineno - 1)
            except ValueError:
                pass

    def OpenEditor(self, col, row):
        """Disable the editor for the first and second columns
        @param col: Column to edit
        @param row: Row to edit

        """
        if col == BreakPointsList.COL_EXPR:
            super(BreakPointsList, self).OpenEditor(col, row)

    def OnItemEdited(self, evt):
        if evt.IsEditCancelled():
            evt.Veto()
            return
        idx = evt.GetIndex()
        newval = evt.GetLabel()
        column = evt.GetColumn()
        if column != BreakPointsList.COL_EXPR:
            return

        filepath, linenostr, exprstr = self.GetRowData(idx)
        lineno = ""
        if filepath and linenostr:
            try:
                lineno = int(linenostr)
                self.Parent.DeleteBreakpoint(filepath, lineno)
                self.Parent.SetEditorBreakpoint(filepath, lineno, False, True)
            except ValueError:
                pass
        exprstr = newval
        enabled = self.IsChecked(idx)
        if filepath and lineno:
            self.Parent.SetBreakpoint(filepath, lineno, exprstr, enabled)
            self.Parent.SetEditorBreakpoint(filepath, lineno, enabled)

    def OnCheckItem(self, idx, enabled):
        wx.CallAfter(self._oncheckitem, idx, enabled)

    def _oncheckitem(self, idx, enabled):
        data = self.GetRowData(idx)
        if len(data) == 3:
            filepath, linenostr, exprstr = data
            if not filepath or not linenostr:
                return
            try:
                lineno = int(linenostr)
                self.Parent.DeleteBreakpoint(filepath, lineno)
                self.Parent.SetBreakpoint(filepath, lineno, exprstr, enabled)
            except ValueError:
                pass

    def Clear(self):
        """Delete all the rows """
        self.DeleteAllItems()
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            editor.DeleteAllBreakpoints()

    def PopulateRows(self, data):
        """Populate the list with the data
        @param data: dictionary of breakpoints

        """
        idx = 0
        for filepath in sorted(data.keys()):
            linenos = data.get(filepath)
            if not linenos:
                continue
            for lineno in sorted(linenos.keys()):
                bpline = linenos.get(lineno)
                if not bpline:
                    continue
                enabled, exprstr = bpline
                if filepath and lineno:
                    self.Parent.SetEditorBreakpoint(filepath, lineno, enabled)
                self.Append((unicode(filepath), unicode(lineno), unicode(exprstr)))
                self.CheckItem(idx, enabled)
                idx += 1

        self.SetColumnWidth(BreakPointsList.COL_FILE, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(BreakPointsList.COL_EXPR, wx.LIST_AUTOSIZE)
        self.SendSizeEvent()
        filenamecolwidth = max(self.GetTextExtent(self.colname_file + "          ")[0], self.GetColumnWidth(BreakPointsList.COL_FILE))
        exprcolwidth = max(self.GetTextExtent(self.colname_expr + "          ")[0], self.GetColumnWidth(BreakPointsList.COL_EXPR))
        self.SetColumnWidth(BreakPointsList.COL_FILE, filenamecolwidth)
        self.SetColumnWidth(BreakPointsList.COL_EXPR, exprcolwidth)
