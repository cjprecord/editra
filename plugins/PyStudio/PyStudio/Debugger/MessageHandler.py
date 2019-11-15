# -*- coding: utf-8 -*-
# Name: MessageHandler.py
# Purpose: Message Handler
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Message Handler"""

__author__ = "Mike Rans"
__svnid__ = "$Id: MessageHandler.py 1466 2011-08-20 14:32:05Z rans@email.com $"
__revision__ = "$Revision: 1466 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path
import wx
import threading

# Editra Libraries
import util
import ed_msg
import syntax.synglob as synglob
import ebmlib

# Local imports
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger
from PyStudio.Common import ToolConfig
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.PyStudioUtils import RunProcInThread

# Globals
_ = wx.GetTranslation
RPDBEXCEPTIONSSTR = u"rpdb_exception_info"
ID_ON_RUNTOLINE = wx.NewId()
ID_ON_JUMP = wx.NewId()
#-----------------------------------------------------------------------------#

class MessageHandler(object):
    """Module Message Handler"""
    __metaclass__ = ebmlib.Singleton
    def __init__(self):
        """Initialize"""
        super(MessageHandler, self).__init__()

        # Attributes
        self._prevfile = u""
        self._evthandler = wx.EvtHandler()
        self._jobtimer = wx.Timer(self._evthandler)
        self._updateeditor = None
        self.editor = None
        self.editorlineno = None
        self.contextlineno = None
        self.contextmenus = {1:(True, ID_ON_RUNTOLINE, _("Run To Line"), self.OnRunToLine), 
                             2:(True, ID_ON_JUMP, _("Jump"), self.OnJump)}
        self.debugeditorupdate = lambda x,y,z:None
        
        # Setup debugger hooks
        rpdbdebugger = RpdbDebugger() # singleton don't keep ref
        rpdbdebugger.conflictingmodules = self.ConflictingModules
        rpdbdebugger.clearstepmarker = self.ClearStepMarker
        rpdbdebugger.setstepmarker = self.SetStepMarker
        rpdbdebugger.restorestepmarker = self.RestoreStepMarker
        rpdbdebugger.catchunhandledexception = self.CatchUnhandledException
        
        # Editra Message Handlers
        ed_msg.Subscribe(self.OnFileLoad, ed_msg.EDMSG_FILE_OPENED)
        ed_msg.Subscribe(self.OnFileSave, ed_msg.EDMSG_FILE_SAVED)
        ed_msg.Subscribe(self.OnPageChanged, ed_msg.EDMSG_UI_NB_CHANGED)        
        ed_msg.Subscribe(self.OnContextMenu, ed_msg.EDMSG_UI_STC_CONTEXT_MENU)
        self._evthandler.Bind(wx.EVT_TIMER,
                              lambda evt: self.UpdateForEditor(self._updateeditor))

    # Properties
    ContextLine = property(lambda self: self.contextlineno,
                           lambda self, line: setattr(self, 'contextlineno', line))
    PreviousFile = property(lambda self: self._prevfile,
                            lambda self, fname: setattr(self, '_prevfile', fname))

    @property
    def mainwindow(self):
        mw = wx.GetApp().GetActiveWindow() # Gets main window if one created
        return mw

    def _StopTimer(self):
        if self._jobtimer.IsRunning():
            self._jobtimer.Stop()

    def ConflictingModules(self, moduleslist):
        dlg = wx.MessageDialog(self.mainwindow, 
        _("The modules: %s, which are incompatible with the debugger were "
        "detected and can possibly cause the debugger to fail.") % moduleslist,
        _("Warning"), wx.OK|wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()
        
    def ClearStepMarker(self):
        if self.editor:
            self.editor.ShowStepMarker(show=False)
            self.editor = None
        
    def SetStepMarker(self, fileName, lineNo):
        self.editor = PyStudioUtils.GetEditorOrOpenFile(self.mainwindow, fileName)
        if not self.editor:
            util.Log("[PyStudio][err] Unable to get editor for file: %s" % fileName)
            return
        self.editorlineno = lineNo - 1
        self.editor.GotoLine(self.editorlineno)
        self.editor.ShowStepMarker(self.editorlineno, show=True)
        
    def RestoreStepMarker(self, editor):
        if not editor or self.editor != editor:
            return
        self.editor.GotoLine(self.editorlineno)
        self.editor.ShowStepMarker(self.editorlineno, show=True)

    def CatchUnhandledException(self):
        if not ToolConfig.GetConfigValue(ToolConfig.TLC_IGNORE_SYSEXIT, True):
            wx.CallAfter(self._unhandledexception)
            return
            
        expressionlist = [(RPDBEXCEPTIONSSTR, True)]

        worker = RunProcInThread(RPDBEXCEPTIONSSTR, self._issysexit,
                                 RpdbDebugger().catchexc_get_namespace,
                                 expressionlist, 0)
        worker.start()
        
    def _issysexit(self, variables):
        if not variables:
            wx.CallAfter(self._unhandledexception)
            return
        variables_with_expr = []
        for expression in variables:
            if hasattr(expression, "get"):
                variables_with_expr.append(expression)
        if variables_with_expr == []:
            wx.CallAfter(self._unhandledexception)
            return

        first_variable_with_expr = variables_with_expr[0]
        if first_variable_with_expr is None:
            wx.CallAfter(self._unhandledexception)
            return

        if "error" in first_variable_with_expr:
            wx.CallAfter(self._unhandledexception)
            return

        if first_variable_with_expr["n_subnodes"] == 0:
            wx.CallAfter(self._unhandledexception)
            return

        #
        # Create a list of the subitems.
        # The list is indexed by name or directory key.
        # In case of a list, no sorting is needed.
        #
        for subnode in first_variable_with_expr["subnodes"]:
            _name = unicode(subnode["name"])
            _type = unicode(subnode["type"])
            _value = PyStudioUtils.get_unicodevalue(subnode["repr"])
            if _name == u"type" and _value.find(u"SystemExit") != -1:
                RpdbDebugger().unhandledexception = False
                RpdbDebugger().do_go()
                return

        wx.CallAfter(self._unhandledexception)

    def _unhandledexception(self):
        dlg = wx.MessageDialog(self.mainwindow,
                               _("An unhandled exception was caught. Would you like to analyze it?"),
                               _("Warning"),
                               wx.YES_NO|wx.YES_DEFAULT|wx.ICON_QUESTION)
        res = dlg.ShowModal()
        dlg.Destroy()

        if res != wx.ID_YES:
            RpdbDebugger().unhandledexception = False
            RpdbDebugger().do_go()
        else:
            RpdbDebugger().set_analyze(True)

    def UpdateForEditor(self, editor, force=False):
        """Update the context based on the current editor."""
        self._updateeditor = None
        if not editor:
            return
        langid = getattr(editor, 'GetLangId', lambda: -1)()
        ispython = langid == synglob.ID_LANG_PYTHON
        filename = os.path.normcase(editor.GetFileName())
        self.debugeditorupdate(ispython, filename, force)
        self._prevfile = filename
        RpdbDebugger().saveandrestoreexpressions()
        RpdbDebugger().saveandrestorebreakpoints()
        self.RestoreStepMarker(editor)

    def _starttimer(self, editor):
        self._StopTimer()
        self._updateeditor = editor
        self._jobtimer.Start(250, True)
    
    def OnPageChanged(self, msg):
        """ Notebook tab was changed """
        notebook, pg_num = msg.GetData()
        editor = notebook.GetPage(pg_num)
        self._starttimer(editor)

    def OnFileLoad(self, msg):
        """Load File message"""
        editor = PyStudioUtils.GetEditorForFile(self.mainwindow, msg.GetData())
        self._starttimer(editor)

    def OnFileSave(self, msg):
        """Load File message"""
        filename, tmp = msg.GetData()
        editor = PyStudioUtils.GetEditorForFile(self.mainwindow, filename)
        self._starttimer(editor)

    def AddMenuItem(self, pos, reqattach, wxid, menutitle, menufncallback):
        self.contextmenus[pos] = (reqattach, wxid, menutitle, menufncallback)
    
    def DeleteMenuItem(self, pos):
        del self.contextmenus[pos]
    
    def OnContextMenu(self, msg):
        """Customize the editor buffers context menu"""
        if not len(self.contextmenus):
            return
        ctxmgr = msg.GetData()
        editor = ctxmgr.GetUserData('buffer')
        if not editor:
            return
        langid = editor.GetLangId()
        if langid != synglob.ID_LANG_PYTHON:
            return

        # Add our custom options to the menu
        menu = ctxmgr.GetMenu()
        self.contextlineno = editor.LineFromPosition(ctxmgr.GetPosition()) + 1
        menu.AppendSeparator()
        for pos in sorted(self.contextmenus.keys()):
            reqattach, wxid, menutitle, menufncallback = self.contextmenus[pos]
            if reqattach and not RpdbDebugger().attached and not RpdbDebugger().broken:
                continue
            menu.Append(wxid, menutitle)
            ctxmgr.AddHandler(wxid, menufncallback)

    def OnRunToLine(self, editor, event):
        RpdbDebugger().run_toline(editor.GetFileName(), self.contextlineno)

    def OnJump(self, editor, event):
        RpdbDebugger().do_jump(self.contextlineno)
