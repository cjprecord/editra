# -*- coding: utf-8 -*-
# Name: ExpressionsShelfWindow.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window for debugger expressions"""

__author__ = "Mike Rans"
__svnid__ = "$Id: ExpressionsShelfWindow.py 1520 2012-03-26 20:18:58Z rans@email.com $"
__revision__ = "$Revision: 1520 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path
import wx
import copy

# Editra Libraries
import ed_glob
from profiler import Profile_Get, Profile_Set

# Local imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.odict import OrderedDict
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.PyStudioUtils import RunProcInThread
from PyStudio.Debugger.ExpressionDialog import ExpressionDialog
from PyStudio.Common.BaseShelfWindow import BaseShelfWindow
from PyStudio.Debugger.ExpressionsList import ExpressionsList
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger

# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ExpressionsShelfWindow(BaseShelfWindow):
    def __init__(self, parent):
        """Initialize the window"""
        super(ExpressionsShelfWindow, self).__init__(parent)

        # setup
        ctrlbar = self.setup(ExpressionsList(self))
        self.addbtn = self.AddPlateButton(u"", ed_glob.ID_ADD, wx.ALIGN_LEFT)
        self.addbtn.ToolTip = wx.ToolTip(_("Set Expression"))
        self.delbtn = self.AddPlateButton(u"", ed_glob.ID_REMOVE, wx.ALIGN_LEFT)
        self.delbtn.ToolTip = wx.ToolTip(_("Delete Expression"))
        self.delallbtn = self.AddPlateButton(u"", ed_glob.ID_DELETE, wx.ALIGN_LEFT)
        self.delallbtn.ToolTip = wx.ToolTip(_("Delete All Expressions"))
        self.refreshbtn = self.AddPlateButton(u"", ed_glob.ID_REFRESH, wx.ALIGN_LEFT)
        self.refreshbtn.ToolTip = wx.ToolTip(_("Refresh Expressions"))
        ctrlbar.AddStretchSpacer()
        self.layout("Execute", self.OnExecute)
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        self.taskbtn.SetBitmap(bmp)
        self.taskbtn.ToolTip = wx.ToolTip(_("Execute"))

        # Attributes
        expressionslist = ToolConfig.GetConfigValue(ToolConfig.TLC_EXPRESSIONS)
        self.expressions = OrderedDict()
        if isinstance(expressionslist, list):
            for tup in expressionslist:
                if isinstance(tup, tuple) and len(tup) == 2:
                    expression, enabled = tup
                    self.expressions[expression] = enabled

        self.ignoredwarnings = {}
        
        # Debugger Attributes
        RpdbDebugger().setexpression = self.SetExpression
        RpdbDebugger().restoreexpressions = self.RestoreExpressions
        RpdbDebugger().saveandrestoreexpressions = self.SaveAndRestoreExpressions
        RpdbDebugger().clearexpressionvalues = self._listCtrl.clearexpressionvalues

        self._listCtrl.PopulateRows(self.expressions)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.addbtn)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.delbtn)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.delallbtn)
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.refreshbtn)

    def Unsubscription(self):
        """Cleanup callbacks when window is destroyed"""
        RpdbDebugger().setexpression = lambda x,y:None
        RpdbDebugger().restoreexpressions = lambda:None
        RpdbDebugger().saveandrestoreexpressions = lambda:None
        RpdbDebugger().clearexpressionvalues = lambda:None

    def OnThemeChanged(self, msg):
        """Update Icons"""
        super(ExpressionsShelfWindow, self).OnThemeChanged(msg)
        for btn, bmp in ((self.executebtn, ed_glob.ID_BIN_FILE),
                         (self.taskbtn, ed_glob.ID_DELETE)):
            bitmap = wx.ArtProvider.GetBitmap(str(bmp), wx.ART_MENU)
            btn.SetBitmap(bitmap)

    def DeleteExpression(self, expression):
        if not expression in self.expressions:
            return
        del self.expressions[expression]
        self.SaveExpressions()

    def SetExpression(self, expression, enabled, oldexpression = None):
        if oldexpression is not None and oldexpression in self.expressions:
            if expression in self.expressions:
                return False
            self.expressions.rename(oldexpression, expression)
        self.expressions[expression] = enabled
        return True

    def RestoreExpressions(self):
        self._listCtrl.Clear()
        self._listCtrl.PopulateRows(self.expressions)
        self._listCtrl.RefreshRows()

    def SaveExpressions(self):
        """Store expressions to the users persistent configuration"""
        config = Profile_Get(ToolConfig.PYTOOL_CONFIG, default=dict())
        expressionslist = []
        for expression in self.expressions:
            expressionslist.append((expression, self.expressions[expression]))
        config[ToolConfig.TLC_EXPRESSIONS] = expressionslist
        Profile_Set(ToolConfig.PYTOOL_CONFIG, config)

    def SaveAndRestoreExpressions(self):
        self.SaveExpressions()
        self.RestoreExpressions()

    def OnButton(self, event):
        """Handle control bar button clicks"""
        eobj = event.GetEventObject()
        if eobj is self.addbtn:
            self.SetExpression(u"", False)
            self.RestoreExpressions()
        elif eobj is self.delbtn:
            for item in self._listCtrl.GetSelectedExpressions():
                if len(item) > 1:
                    self.DeleteExpression(item[0])
                    self.RestoreExpressions()
        else:
            event.Skip()

    def OnClear(self, evt):
        """Clear the expressions"""
        self.expressions = OrderedDict()
        self.SaveAndRestoreExpressions()

    def OnRefresh(self, evt):
        """Refresh the expressions"""
        self.RestoreExpressions()

    def OnExecute(self, event):
        """Execute an expression"""
        desc = _("This code will be executed at the debuggee:")
        expr_dialog = ExpressionDialog(self, u"", _("Enter Code to Execute"),
                                       desc, None, (200, 200))
        pos = self.GetPositionTuple()
        expr_dialog.SetPosition((pos[0] + 50, pos[1] + 50))
        if expr_dialog.ShowModal() == wx.ID_OK:
            _expr = expr_dialog.get_expression()
            worker = RunProcInThread("DbgExec", self._oncodeexecuted,
                                     RpdbDebugger().execute, _expr)
            worker.start()
        expr_dialog.Destroy()

    def _oncodeexecuted(self, res):
        """Expression execution callback"""
        if not res:
            return
        if len(res) == 2:
            warning, error = res
        else:
            error = res
            warning = None

        PyStudioUtils.error_dialog(self, error)
        if warning and not warning in self.ignoredwarnings:
            dlg = wx.MessageDialog(self,
                                   _("Would you like to ignore this warning for the rest of this session?\n\n%s") % warning,\
                                   _("Ignore Warning"),
                                   wx.YES_NO|wx.YES_DEFAULT|wx.ICON_WARNING)
            if dlg.ShowModal() == wx.ID_YES:
                self.ignoredwarnings[warning] = True
            dlg.Destroy()
