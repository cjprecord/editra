# -*- coding: utf-8 -*-
# Name: ShelfWindow.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: ShelfWindow.py 1223 2011-04-06 15:20:53Z CodyPrecord $"
__revision__ = "$Revision: 1223 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Editra Libraries
import ed_glob
import util
import eclib
import ed_msg
import ed_basewin
from profiler import Profile_Get
from syntax import syntax
import syntax.synglob as synglob

# Local imports
import ToolConfig
from CheckResultsList import CheckResultsList
from PythonSyntaxChecker import PythonSyntaxChecker

# Directory Variables
from PythonDirectoryVariables import PythonDirectoryVariables

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ShelfWindow(eclib.ControlBox):
    """Syntax Check Results Window"""
    __syntaxCheckers = {
        synglob.ID_LANG_PYTHON: PythonSyntaxChecker
    }

    __directoryVariables = {
        synglob.ID_LANG_PYTHON: PythonDirectoryVariables
    }
    def __init__(self, parent):
        """Initialize the window"""
        super(ShelfWindow, self).__init__(parent)

        # Attributes
        # Parent is ed_shelf.EdShelfBook
        self._mw = ed_basewin.FindMainWindow(self)
        self._log = wx.GetApp().GetLog()
        self._listCtrl = CheckResultsList(self,
                                          style=wx.LC_REPORT|wx.BORDER_NONE)
        self._jobtimer = wx.Timer(self)
        self._checker = None
        self._curfile = u""
        self._hasrun = False

        # Setup
        self._listCtrl.set_mainwindow(self._mw)
        ctrlbar = eclib.ControlBar(self, style=eclib.CTRLBAR_STYLE_GRADIENT)
        ctrlbar.SetVMargin(2, 2)
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(eclib.CTRLBAR_STYLE_DEFAULT)
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            rbmp = None
        self.cfgbtn = eclib.PlateButton(ctrlbar, wx.ID_ANY, bmp=rbmp,
                                        style=eclib.PB_STYLE_NOBG)
        self.cfgbtn.SetToolTipString(_("Configure"))
        ctrlbar.AddControl(self.cfgbtn, wx.ALIGN_LEFT)
        self._lbl = wx.StaticText(ctrlbar)
        ctrlbar.AddControl(self._lbl)
        ctrlbar.AddStretchSpacer()
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            rbmp = None
        self.runbtn = eclib.PlateButton(ctrlbar, wx.ID_ANY, _("Lint"), rbmp,
                                        style=eclib.PB_STYLE_NOBG)
        ctrlbar.AddControl(self.runbtn, wx.ALIGN_RIGHT)

        # Layout
        self.SetWindow(self._listCtrl)
        self.SetControlBar(ctrlbar, wx.TOP)

        # Event Handlers
        self.Bind(wx.EVT_TIMER, self.OnJobTimer, self._jobtimer)
        self.Bind(wx.EVT_BUTTON, self.OnShowConfig, self.cfgbtn)
        self.Bind(wx.EVT_BUTTON, self.OnRunLint, self.runbtn)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)

        # Editra Message Handlers
        ed_msg.Subscribe(self.OnFileLoad, ed_msg.EDMSG_FILE_OPENED)
        ed_msg.Subscribe(self.OnFileSave, ed_msg.EDMSG_FILE_SAVED)
        ed_msg.Subscribe(self.OnPageChanged, ed_msg.EDMSG_UI_NB_CHANGED)
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)

    def OnDestroy(self, evt):
        """Stop timer and disconnect message handlers"""
        self._StopTimer()
        ed_msg.Unsubscribe(self.OnFileLoad)
        ed_msg.Unsubscribe(self.OnFileSave)
        ed_msg.Unsubscribe(self.OnPageChanged)
        ed_msg.Unsubscribe(self.OnThemeChanged)

    def GetMainWindow(self):
        return self._mw

    def _StopTimer(self):
        if self._jobtimer.IsRunning():
            self._jobtimer.Stop()

    def _onfileaccess(self, editor):
        # With the text control (ed_stc.EditraStc) this will return the full
        # path of the file or a wx.EmptyString if the buffer does not contain
        # an on disk file
        filename = editor.GetFileName()
        self._listCtrl.set_editor(editor)
        self._listCtrl.DeleteOldRows()

        if not filename:
            return

        filename = os.path.abspath(filename)
        fileext = os.path.splitext(filename)[1]
        if fileext == u"":
            return

        filetype = syntax.GetIdFromExt(fileext[1:]) # pass in file extension
        directoryvariables = self.get_directory_variables(filetype)
        if directoryvariables:
            vardict = directoryvariables.read_dirvarfile(filename)
        else:
            vardict = {}

        self._checksyntax(filetype, vardict, filename)
        self._hasrun = True

    def UpdateForEditor(self, editor, force=False):
        langid = getattr(editor, 'GetLangId', lambda: -1)()
        ispython = langid == synglob.ID_LANG_PYTHON
        self.runbtn.Enable(ispython)
        if force or not self._hasrun:
#            fname = getattr(editor, 'GetFileName', lambda: u"")()
#            if ispython:
#                self._lbl.SetLabel(fname)
#            else:
#                self._lbl.SetLabel(u"")
            ctrlbar = self.GetControlBar(wx.TOP)
            ctrlbar.Layout()

    def OnPageChanged(self, msg):
        """ Notebook tab was changed """
        notebook, pg_num = msg.GetData()
        editor = notebook.GetPage(pg_num)
        if ToolConfig.GetConfigValue(ToolConfig.TLC_AUTO_RUN):
            wx.CallAfter(self._onfileaccess, editor)
            self.UpdateForEditor(editor, True)
        else:
            self.UpdateForEditor(editor)

    def OnFileLoad(self, msg):
        """Load File message"""
        editor = self._GetEditorForFile(msg.GetData())
        if ToolConfig.GetConfigValue(ToolConfig.TLC_AUTO_RUN):
            wx.CallAfter(self._onfileaccess, editor)
            self.UpdateForEditor(editor, True)
        else:
            self.UpdateForEditor(editor)

    def OnFileSave(self, msg):
        """Load File message"""
        filename, tmp = msg.GetData()
        editor = self._GetEditorForFile(filename)
        if ToolConfig.GetConfigValue(ToolConfig.TLC_AUTO_RUN):
            wx.CallAfter(self._onfileaccess, editor)
            self.UpdateForEditor(editor, True)
        else:
            self.UpdateForEditor(editor)

    def OnThemeChanged(self, msg):
        """Icon theme has changed so update button"""
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            return
        else:
            self.runbtn.SetBitmap(rbmp)
            self.runbtn.Refresh()

    def OnShowConfig(self, event):
        """Show the configuration dialog"""
        mw = self.GetMainWindow()
        dlg = ToolConfig.ToolConfigDialog(mw)
        dlg.CenterOnParent()
        dlg.ShowModal()

    def OnRunLint(self, event):
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            wx.CallAfter(self._onfileaccess, editor)

    def get_syntax_checker(self, filetype, vardict, filename):
        try:
            return self.__syntaxCheckers[filetype](vardict, filename)
        except Exception:
            pass
        return None

    def get_directory_variables(self, filetype):
        try:
            return self.__directoryVariables[filetype]()
        except Exception:
            pass
        return None

    def _checksyntax(self, filetype, vardict, filename):
        syntaxchecker = self.get_syntax_checker(filetype, vardict, filename)
        if not syntaxchecker:
            return
        self._checker = syntaxchecker
        self._curfile = filename

        # Start job timer
        self._StopTimer()
        self._jobtimer.Start(250, True)

    def _OnSyntaxData(self, data):
        # Data is something like
        # [('Syntax Error', '__all__ = ["CSVSMonitorThread"]', 7)]
        if len(data) != 0:
            self._listCtrl.PopulateRows(data)
            self._listCtrl.RefreshRows()
        mwid = self.GetMainWindow().GetId()
        ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (mwid, False))

    def OnJobTimer(self, evt):
        """Start a syntax check job"""
        if self._checker:
            util.Log("[PyLint][info] fileName %s" % (self._curfile))
            mwid = self.GetMainWindow().GetId()
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (mwid, True))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (mwid, -1, -1))
            # Update the label to show what file the results are for
            self._lbl.SetLabel(self._curfile)
            self._checker.Check(self._OnSyntaxData)

    def delete_rows(self):
        self._listCtrl.DeleteOldRows()

    def _GetEditorForFile(self, fname):
        """Return the EdEditorView that's managing the file, if available
        @param fname: File name to open
        @param mainw: MainWindow instance to open the file in
        @return: Text control managing the file
        @rtype: ed_editv.EdEditorView

        """
        nb = self._mw.GetNotebook()
        for page in nb.GetTextControls():
            if page.GetFileName() == fname:
                return nb.GetPage(page.GetTabIndex())

        return None
