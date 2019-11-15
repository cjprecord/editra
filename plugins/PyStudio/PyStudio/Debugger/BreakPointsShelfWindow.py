# -*- coding: utf-8 -*-
# Name: BreakPointsShelfWindow.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: BreakPointsShelfWindow.py 1453 2011-07-25 19:35:56Z rans@email.com $"
__revision__ = "$Revision: 1453 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path
import copy
import wx
from wx.stc import STC_INDIC_PLAIN

# Editra Libraries
import util
import ed_glob
from profiler import Profile_Get, Profile_Set
import ed_marker
import ed_msg
import ebmlib
import syntax.synglob as synglob

# Local imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.BaseShelfWindow import BaseShelfWindow
from PyStudio.Debugger.BreakPointsList import BreakPointsList
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger
from PyStudio.Debugger.MessageHandler import MessageHandler

# Globals
_ = wx.GetTranslation

ID_TOGGLE_BREAKPOINT = wx.NewId()
#-----------------------------------------------------------------------------#

class BreakpointController(object):
    __metaclass__ = ebmlib.Singleton
    def __init__(self):
        super(BreakpointController, self).__init__()

        # Attributes
        self._ui = None

        # Setup callbacks
        MessageHandler().AddMenuItem(0, False, ID_TOGGLE_BREAKPOINT, 
                                     _("Toggle Breakpoint"), 
                                     self.ToggleBreakpoint)
        ed_msg.Subscribe(self.OnMarginClick, ed_msg.EDMSG_UI_STC_MARGIN_CLICK)

    # Properties
    BreakpointWindow = property(lambda self: self._ui,
                                lambda self, win: setattr(self, '_ui', win))

    def OnMarginClick(self, msg):
        """Handle margin clicks for setting/disabling breakpoints"""
        data = msg.GetData()
        buff = data.get('stc', None)
        line = data.get('line', -1)
        if buff and line > 0:
            if buff.GetLangId() == synglob.ID_LANG_PYTHON:
                MessageHandler().ContextLine = line + 1
                self.ToggleBreakpoint(buff, None)
                data['handled'] = True

    @staticmethod
    def DeleteBreakpoint(filepath, lineno):
        """Remove a breakpoint from the list"""
        if not os.path.isfile(filepath) or \
           not filepath in RpdbDebugger().breakpoints:
            return None
        linenos = RpdbDebugger().breakpoints[filepath]
        if not lineno in linenos:
            return None

        # Delete the breakpoint
        enabled, exprstr = linenos[lineno]
        del linenos[lineno]
        if len(linenos) == 0:
            del RpdbDebugger().breakpoints[filepath]
        RpdbDebugger().delete_breakpoint(filepath, lineno)
        BreakpointController.SaveBreakpoints()
        BreakpointController.SetEditorBreakpoint(filepath, lineno, False, True)
        return lineno

    @staticmethod
    def SetEditorBreakpoint(filepath, lineno, enabled, delete=False):
        """Set a breakpoint the the current editor"""
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            curpath = os.path.normcase(editor.GetFileName())
            if filepath == curpath:
                editorlineno = lineno - 1
                if delete:
                    editor.DeleteBreakpoint(editorlineno)
                elif enabled:
                    editor.SetBreakpoint(editorlineno)
                else:
                    editor.SetBreakpoint(editorlineno, disabled=True)

    @staticmethod
    def SetBreakpoint(filepath, lineno, exprstr, enabled):
        """Set a breakpoint in the given file
        @param filepath: normalized file path
        @param lineno: buffer display line number

        """
        if not os.path.isfile(filepath):
            return
        if filepath in RpdbDebugger().breakpoints:
            linenos = RpdbDebugger().breakpoints[filepath]
        else:
            linenos = {}
            RpdbDebugger().breakpoints[filepath] = linenos
        linenos[lineno] = (enabled, exprstr)
        util.Log("[DbgBp][info] SetBreakpoint %s, %d, %s, %s" % \
                 (filepath, lineno, enabled, exprstr))
        if enabled:
            RpdbDebugger().set_breakpoint(filepath, lineno, exprstr)
        BreakpointController.SaveBreakpoints()
        BreakpointController.SetEditorBreakpoint(filepath, lineno, enabled, False)
        return lineno

    @staticmethod
    def SaveBreakpoints():
        """Save currently set breakpoints in the user configuration"""
        config = Profile_Get(ToolConfig.PYTOOL_CONFIG, default=dict())
        config[ToolConfig.TLC_BREAKPOINTS] = copy.deepcopy(RpdbDebugger().breakpoints)
        Profile_Set(ToolConfig.PYTOOL_CONFIG, config)

    def ToggleBreakpoint(self, editor, event):
        """Toggle a breakpoint"""
        filepath = os.path.normcase(editor.GetFileName())
        if not BreakpointController.DeleteBreakpoint(filepath, MessageHandler().ContextLine):
            BreakpointController.SetBreakpoint(filepath, MessageHandler().ContextLine, "", True)
        if self.BreakpointWindow:
            self.BreakpointWindow.RestoreBreakPoints()
        else:
            RpdbDebugger().restorestepmarker(editor)

#-----------------------------------------------------------------------------#

class BreakPointsShelfWindow(BaseShelfWindow):
    def __init__(self, parent):
        """Initialize the window"""
        super(BreakPointsShelfWindow, self).__init__(parent)

        ctrlbar = self.setup(BreakPointsList(self))
        ctrlbar.AddControl(wx.StaticLine(ctrlbar, size=(1, 16), style=wx.LI_VERTICAL),
                           0, wx.ALIGN_LEFT)
        self.addbtn = self.AddPlateButton(u"", ed_glob.ID_ADD, wx.ALIGN_LEFT)
        self.addbtn.ToolTip = wx.ToolTip(_("Set Breakpoint"))
        self.delbtn = self.AddPlateButton(u"", ed_glob.ID_REMOVE, wx.ALIGN_LEFT)
        self.delbtn.ToolTip = wx.ToolTip(_("Delete Breakpoint"))
        self.delallbtn = self.AddPlateButton(u"", ed_glob.ID_DELETE, wx.ALIGN_LEFT)
        self.delallbtn.ToolTip = wx.ToolTip(_("Delete All Breakpoints"))
        self.layout(None, None)

        # Attributes
        bpoints = ToolConfig.GetConfigValue(ToolConfig.TLC_BREAKPOINTS)
        if isinstance(bpoints, dict):
            RpdbDebugger().breakpoints = bpoints
        else:
            RpdbDebugger().breakpoints = dict()        
        RpdbDebugger().saveandrestorebreakpoints = self.SaveAndRestoreBreakpoints
        
        self._listCtrl.PopulateRows(RpdbDebugger().breakpoints)
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            RpdbDebugger().restorestepmarker(editor)
        RpdbDebugger().install_breakpoints()
        BreakpointController().BreakpointWindow = self

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.addbtn)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.delbtn)
        self.Bind(wx.EVT_BUTTON, self.OnClear, self.delallbtn)

    def Unsubscription(self):
        """Cleanup items on destroy"""
        editor = wx.GetApp().GetCurrentBuffer()
        RpdbDebugger().saveandrestorebreakpoints = lambda:None
        RpdbDebugger().install_breakpoints()
        if BreakpointController.BreakpointWindow is self:
            BreakpointController.BreakpointWindow = None

    def OnThemeChanged(self, msg):
        """Update Icons"""
        super(BreakPointsShelfWindow, self).OnThemeChanged(msg)
        for btn, bmp in ((self.addbtn, ed_glob.ID_ADD),
                         (self.delbtn, ed_glob.ID_REMOVE),
                         (self.delallbtn, ed_glob.ID_DELETE)):
            bitmap = wx.ArtProvider.GetBitmap(str(bmp), wx.ART_MENU)
            btn.SetBitmap(bitmap)
            btn.Refresh()

    def RestoreBreakPoints(self):
        """Restore breakpoints"""
        self._listCtrl.Clear()
        self._listCtrl.PopulateRows(RpdbDebugger().breakpoints)
        self._listCtrl.RefreshRows()
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            RpdbDebugger().restorestepmarker(editor)

    def SaveAndRestoreBreakpoints(self):
        """Save an reset breakpoints"""
        BreakpointController.SaveBreakpoints()
        self.RestoreBreakPoints()

    @staticmethod
    def DeleteBreakpoint(filepath, lineno):
        BreakpointController.DeleteBreakpoint(filepath, lineno)

    @staticmethod
    def SetBreakpoint(filepath, lineno, exprstr, enabled):
        BreakpointController.SetBreakpoint(filepath, lineno, exprstr, enabled)

    @staticmethod
    def SetEditorBreakpoint(filepath, lineno, enabled, delete=False):
        BreakpointController.SetEditorBreakpoint(filepath, lineno, enabled, delete)

    def OnButton(self, event):
        """Handle control bar button clicks"""
        eobj = event.GetEventObject()
        if eobj is self.addbtn:
            editor = wx.GetApp().GetCurrentBuffer()
            fname = editor.GetFileName()
            if fname:
                fname = os.path.normcase(fname)
                lnum = BreakpointController.SetBreakpoint(fname, editor.CurrentLine + 1, u"", True)
                editor.SetBreakpoint(lnum)
                self.RestoreBreakPoints()
        elif eobj is self.delbtn:
            for item in self._listCtrl.GetSelectedBreakpoints():
                if len(item) > 1:
                    BreakpointController.DeleteBreakpoint(item[0], int(item[1]))
                    self.RestoreBreakPoints()
        else:
            event.Skip()

    def OnClear(self, event):
        """Clear all breakpoints"""
        for fname, points in dict(RpdbDebugger().breakpoints).iteritems():
            for line in points.keys():
                BreakpointController.DeleteBreakpoint(fname, int(line))
        RpdbDebugger().breakpoints = {}
        self.SaveAndRestoreBreakpoints()
