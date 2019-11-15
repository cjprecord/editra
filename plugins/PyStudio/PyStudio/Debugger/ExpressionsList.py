# -*- coding: utf-8 -*-
# Name: ExpressionsList.py
# Purpose: ModuleFinder plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: ExpressionsList.py 1450 2011-07-24 18:04:12Z rans@email.com $"
__revision__ = "$Revision: 1450 $"

#----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import eclib

# Local Imports
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.PyStudioUtils import RunProcInThread
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class ExpressionsList(eclib.EToggleEditListCtrl):
    """List control for displaying breakpoints results"""

    COL_EXPR = 0
    COL_VALUE = 1
    COL_TYPE = 2
    
    def __init__(self, parent):
        super(ExpressionsList, self).__init__(parent)

        # Attributes
        self._data = {}
        
        # Setup
        self.colname_expr = _("Expression")
        self.colname_value = _("Value")
        self.colname_type = _("Type")
    
        self.InsertColumn(ExpressionsList.COL_EXPR, self.colname_expr)
        self.InsertColumn(ExpressionsList.COL_VALUE, self.colname_value)
        self.InsertColumn(ExpressionsList.COL_TYPE, self.colname_type)

        # Event Handlers
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnItemEdited)
        
    def set_mainwindow(self, mw):
        self._mainw = mw

    def GetSelectedExpressions(self):
        """Get a list of selected breakpoints
        @return: [(fname, line, expr),]

        """
        rval = list()
        for index in self.GetSelections():
            rval.append(self.GetRowData(index))
        return rval

    def OpenEditor(self, col, row):
        if col == 0:
            super(ExpressionsList, self).OpenEditor(col, row)
    
    def OnItemEdited(self, evt):
        if evt.IsEditCancelled():
            evt.Veto()
            return
        if evt.GetColumn() != 0:
            return
        idx = evt.GetIndex()
        self.CheckItem(idx)
        oldexpression, = self._data[idx]
        newexpression = unicode(evt.GetLabel())
        enabled = True
        success = self.Parent.SetExpression(newexpression, enabled, oldexpression)
        if success:
            self._data[idx] = [newexpression,]
            self.Evaluate(enabled, newexpression, idx)
        else:
            evt.Veto()

    def OnCheckItem(self, idx, enabled):
        expression, = self._data[idx]
        self.Parent.SetExpression(expression, enabled)
        if enabled:
            self.Evaluate(enabled, expression, idx)
        else:
            self.SetStringItem(idx, ExpressionsList.COL_VALUE, u"")        
            self.SetStringItem(idx, ExpressionsList.COL_TYPE, u"")        

    def Evaluate(self, enabled, expression, idx):
        if not enabled or not expression or not RpdbDebugger().broken:
            return
        worker = RunProcInThread("Expr", self.fillexpressionvalue, \
                                 RpdbDebugger().evaluate, expression)
        worker.pass_parameter(idx)
        worker.start()
        worker2 = RunProcInThread("Expr", self.fillexpressiontype, \
                                 RpdbDebugger().evaluate, "type(%s).__name__" % expression)
        worker2.pass_parameter(idx)
        worker2.start()
    
    def Clear(self):
        """Delete all the rows """
        self._data = {}
        self.DeleteAllItems()

    def PopulateRows(self, data):
        """Populate the list with the data
        @param data: dictionary of expressions

        """
        if not data:
            return
        self._data = {}
        idx = 0
        for expression in data:
            enabled = data[expression]
            self._data[idx] = [expression,]
            self.Evaluate(enabled, expression, idx)
            
            self.Append(self._data[idx] + [u""])
            self.SetItemData(idx, idx)
            self.CheckItem(idx, enabled)
            idx += 1

        self.SetColumnWidth(ExpressionsList.COL_EXPR, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(ExpressionsList.COL_VALUE, wx.LIST_AUTOSIZE)
        exprcolwidth = max(self.GetTextExtent(self.colname_expr + "          ")[0], self.GetColumnWidth(ExpressionsList.COL_EXPR))
        valuecolwidth = max(self.GetTextExtent(self.colname_value + "          ")[0], self.GetColumnWidth(ExpressionsList.COL_VALUE))
        self.SetColumnWidth(ExpressionsList.COL_EXPR, exprcolwidth)
        self.SetColumnWidth(ExpressionsList.COL_VALUE, valuecolwidth)

    def fillexpressionvalue(self, res, idx):
        if not res:
            return
        value, w, error = res
        if error:
            value = error
        self.SetStringItem(idx, ExpressionsList.COL_VALUE, PyStudioUtils.get_unicodevalue(value))        
        self.SetColumnWidth(ExpressionsList.COL_VALUE, wx.LIST_AUTOSIZE)

    def fillexpressiontype(self, res, idx):
        if not res:
            return
        value, w, error = res
        if error:
            value = error
        self.SetStringItem(idx, ExpressionsList.COL_TYPE, PyStudioUtils.get_unicodevalue(value))        
        
    def clearexpressionvalues(self):
        if not self._data:
            return
        for idx in range(len(self._data)):
            self.SetStringItem(idx, ExpressionsList.COL_EXPR, u"")
            self.SetStringItem(idx, ExpressionsList.COL_VALUE, u"")
            self.SetStringItem(idx, ExpressionsList.COL_TYPE, u"")
        
    @staticmethod
    def _printListCtrl(ctrl):
        for row in range(0, ctrl.GetItemCount()):
            for column in xrange(0, ctrl.GetColumnCount()):
                print ctrl.GetItem(row, column).GetText(), "\t",
            print ""
