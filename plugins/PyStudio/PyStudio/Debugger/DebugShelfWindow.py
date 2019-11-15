# -*- coding: utf-8 -*-
# Name: DebugShelfWindow.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: DebugShelfWindow.py 1420 2011-07-13 20:29:09Z rans@email.com $"
__revision__ = "$Revision: 1420 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path
import copy
from time import sleep
import wx

# Editra Libraries
import ed_glob
import util
import eclib
import ed_msg
from profiler import Profile_Get, Profile_Set
from syntax import syntax
import syntax.synglob as synglob

# Local imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.BaseShelfWindow import BaseShelfWindow
from PyStudio.Common import Images
from PyStudio.Common.DummyProcessCreator import DummyProcessCreator
from PyStudio.Debugger.DebuggeeWindow import DebuggeeWindow
from PyStudio.Debugger.PythonDebugger import PythonDebugger
from PyStudio.Debugger.AttachDialog import AttachDialog
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger
from PyStudio.Debugger.MessageHandler import MessageHandler

# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class DebugShelfWindow(BaseShelfWindow):
    """Module Debug Results Window"""
    __debuggers = {
        synglob.ID_LANG_PYTHON: PythonDebugger
    }

    def __init__(self, parent):
        """Initialize the window"""
        super(DebugShelfWindow, self).__init__(parent)

        # Setup
        ctrlbar = self.setup(DebuggeeWindow(self))
        ctrlbar.AddControl(wx.StaticLine(ctrlbar, size=(-1, 16), style=wx.SL_VERTICAL),
                           wx.ALIGN_LEFT)
        self.gobtn = self.AddPlateButton(u"", Images.Go.Bitmap, wx.ALIGN_LEFT)
        self.gobtn.ToolTip = wx.ToolTip(_("Run"))
        self.abortbtn = self.AddPlateButton(u"", Images.Stop.Bitmap, wx.ALIGN_LEFT)
        self.abortbtn.ToolTip = wx.ToolTip(_("Stop debugging"))
        ctrlbar.AddControl(wx.StaticLine(ctrlbar, size=(-1, 16), style=wx.SL_VERTICAL),
                           wx.ALIGN_LEFT)
        self.stepinbtn = self.AddPlateButton(u"", Images.StepIn.Bitmap, wx.ALIGN_LEFT)
        self.stepinbtn.ToolTip = wx.ToolTip(_("Step In"))
        self.stepovbtn = self.AddPlateButton(u"", Images.StepOver.Bitmap, wx.ALIGN_LEFT)
        self.stepovbtn.ToolTip = wx.ToolTip(_("Step Over"))
        self.stepoutbtn = self.AddPlateButton(u"", Images.StepOut.Bitmap, wx.ALIGN_LEFT)
        self.stepoutbtn.ToolTip = wx.ToolTip(_("Step Out"))
        self.breakbtn = self.AddPlateButton(u"", Images.Break.Bitmap, wx.ALIGN_LEFT)
        self.breakbtn.ToolTip = wx.ToolTip(_("Break"))
        ctrlbar.AddStretchSpacer()
        self.choices = [_("Program Args"), _("Debugger Args")]
        self.combo = wx.Choice(ctrlbar, choices=self.choices)
        self.combo.SetStringSelection(self.choices[0])
        self.combo.Enable(False)
        ctrlbar.AddControl(self.combo, wx.ALIGN_RIGHT)
        self.combocurrent_selection = 0
        self.combotexts = {}
        for i, ignore in enumerate(self.choices):
            self.combotexts[i] = ""
        self.search = eclib.CommandEntryBase(ctrlbar, style=wx.TE_PROCESS_ENTER)
        self.search.Enable(False)
        self.search.SetDescriptiveText(u"")
        self.search.ShowSearchButton(False)
        self.search.ShowCancelButton(True)
        ctrlbar.AddControl(self.search, wx.ALIGN_RIGHT, 2)

        self.layout("Remote", self.OnRemote, self.OnJobTimer)

        # Attributes
        self.disablingpylinttext = _("Disabling Pylint Autorun during Debug.\n")
        self.enablingpylinttext = _("Reenabling Pylint Autorun.\n")
        self.debuggerattachedtextremote = _("Debugger attached.\n\n")
        self.debuggerdetachedtext = _("\n\nDebugger detached.")
        self.emptytext = u""
        
        MessageHandler().debugeditorupdate = self.OnEditorUpdate
        self._debugger = None
        self._debugrun = False
        self._debugargs = ""
        self.abortfn = lambda:None
        
        # For remote attachment
        self._lastpwd = ""
        self._lasthost = "localhost"
        self._remotetext = None

        # Debugger Attributes
        RpdbDebugger().mainwindow = self._mw #TODO
        RpdbDebugger().debugbuttonsupdate = self.OnButtonsUpdate
        RpdbDebugger().disabledebugbuttons = self.DisableButtons

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnGo, self.gobtn)
        self.Bind(wx.EVT_BUTTON, self.OnAbort, self.abortbtn)
        self.Bind(wx.EVT_BUTTON, self.OnStepIn, self.stepinbtn)
        self.Bind(wx.EVT_BUTTON, self.OnStepOver, self.stepovbtn)
        self.Bind(wx.EVT_BUTTON, self.OnStepOut, self.stepoutbtn)
        self.Bind(wx.EVT_BUTTON, self.OnBreak, self.breakbtn)
        self.Bind(wx.EVT_CHOICE, self.OnComboSelect, self.combo)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancelSearch, self.search)
        self.Bind(wx.EVT_SHOW, self.OnShow, self)

    def Unsubscription(self):
        """Cleanup message handlers on Destroy"""
        RpdbDebugger().abortattach = True
        processcreator = RpdbDebugger().processcreator
        if processcreator:
            processcreator.Abort()
        RpdbDebugger().debugbuttonsupdate = lambda:None
        RpdbDebugger().disabledebugbuttons = lambda:None
        MessageHandler().debugeditorupdate = lambda x,y,z:None

    def OnThemeChanged(self, msg):
        """Update Icons"""
        super(DebugShelfWindow, self).OnThemeChanged(msg)
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        self.taskbtn.SetBitmap(bmp)
        self.taskbtn.Refresh()

    def OnCancelSearch(self, event):
        """Clear the text from the text control"""
        self.combotexts[self.combocurrent_selection] = ""
        self.search.SetValue("")

    def OnComboSelect(self, event):
        """Handle change of combo choice"""
        self.combotexts[self.combocurrent_selection] = self.search.GetValue()
        self.combocurrent_selection = self.combo.GetSelection()
        self.search.SetValue(self.combotexts[self.combocurrent_selection])

    def OnShow(self, evt):
        """Handle EVT_SHOW"""
        if evt.IsShown():
            self.OnButtonsUpdate()

    def DisableButtons(self):
        """Disable all debugger buttons"""
        self.taskbtn.Enable(False)
        self.gobtn.Enable(False)
        self.abortbtn.Enable(False)
        self.stepinbtn.Enable(False)
        self.stepovbtn.Enable(False)
        self.stepoutbtn.Enable(False)
        self.breakbtn.Enable(False)
        self.combo.Enable(False)
        self.search.Enable(False)
    
    def _onbuttonsupdate(self, ispython):
        """Update button states based on debugger state"""
        attached = RpdbDebugger().attached
        self.taskbtn.Enable(not attached)
        broken = RpdbDebugger().broken
        attachedandbroken = attached and broken
        ispythonandnotattached = ispython and not attached
        self.gobtn.Enable(attachedandbroken or ispythonandnotattached)
        if attached:
            self.gobtn.SetBitmap(Images.GoRunning.Bitmap)
        else:
            self.gobtn.SetBitmap(Images.Go.Bitmap)
        self.abortbtn.Enable(attached)
        self.stepinbtn.Enable(attachedandbroken)
        self.stepovbtn.Enable(attachedandbroken)
        self.stepoutbtn.Enable(attachedandbroken)
        self.breakbtn.Enable(attached and not broken and not RpdbDebugger().analyzing)
        self.combo.Enable(ispythonandnotattached)
        self.search.Enable(ispythonandnotattached)

    def OnButtonsUpdate(self):
        editor = wx.GetApp().GetCurrentBuffer()
        if not editor:
            self._onbuttonsupdate(False)
            return
        langid = getattr(editor, 'GetLangId', lambda: -1)()
        ispython = langid == synglob.ID_LANG_PYTHON
        self._onbuttonsupdate(ispython)
        
    def OnEditorUpdate(self, ispython, filename, force):
        self._onbuttonsupdate(ispython)
        self.combotexts[self.combocurrent_selection] = self.search.GetValue()
        config = Profile_Get(ToolConfig.PYTOOL_CONFIG, default=dict())
        if MessageHandler().PreviousFile:
            emptycombotexts = True
            for key in self.combotexts:
                combotext = self.combotexts[key]
                if combotext:
                    emptycombotexts = False
                    break
            key = "DEBUG_%s" % MessageHandler().PreviousFile
            if emptycombotexts:
                if key in config:
                    del config["DEBUG_%s" % MessageHandler().PreviousFile]
            else:
                debuginfo = (self.combocurrent_selection, self.combotexts)
                config[key] = copy.deepcopy(debuginfo)
                Profile_Set(ToolConfig.PYTOOL_CONFIG, config)

        debuginfo = config.get("DEBUG_%s" % filename, None)
        if debuginfo:
            self.combocurrent_selection, self.combotexts = debuginfo
            self.combo.SetSelection(self.combocurrent_selection)
            self.search.SetValue(self.combotexts[self.combocurrent_selection])
        else:
            self.combocurrent_selection = 0
            self.combotexts = {}
            for i, ignore in enumerate(self.choices):
                self.combotexts[i] = ""
            self.combo.SetSelection(0)
            self.search.SetValue(u"")

        if force or not self._hasrun:
            ctrlbar = self.GetControlBar(wx.TOP)
            ctrlbar.Layout()

    def _ondebug(self, editor):
        """Start debugging
        @param editor: EditraStc

        """
        self._listCtrl.Clear()

        # With the text control (ed_stc.EditraStc) this will return the full
        # path of the file or a wx.EmptyString if the buffer does not contain
        # an on disk file
        filename = editor.GetFileName()
        if not filename:
            return
        filename = os.path.abspath(filename)
        
        filetype = editor.GetLangId()
        directoryvariables = self.get_directory_variables(filetype)
        if directoryvariables:
            vardict = directoryvariables.read_dirvarfile(filename)
        else:
            vardict = {}
        self._debug(filetype, vardict, filename)
        self._hasrun = True

    def OnGo(self, event):
        """Go button clicked. Starts debugging if not already attached or
        lets program run till next breakpoint is hit.

        """
        if RpdbDebugger().attached:
            RpdbDebugger().do_go()
            RpdbDebugger().clearexpressionvalues()
            return
            
        self.combotexts[self.combocurrent_selection] = self.search.GetValue()
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            wx.CallAfter(self._ondebug, editor)

    def get_debugger(self, filetype, vardict, filename):
        """Get the debugger object for the current context"""
        dbgr = None
        try:
            programargs = self.combotexts[0]
            debuggerargs = self.combotexts[1]
            dbgr = self.__debuggers[filetype](vardict, debuggerargs, 
                                              programargs, filename, 
                                              self._listCtrl)
        except Exception:
            pass
        return dbgr
        
    def restorepylint_autorun(self):
        config = Profile_Get(ToolConfig.PYTOOL_CONFIG, default=dict())
        config[ToolConfig.TLC_LINT_AUTORUN] = True
        Profile_Set(ToolConfig.PYTOOL_CONFIG, config)
        self._listCtrl.AppendUpdate(self.enablingpylinttext)
    
    def _setdebuggerdefaults(self):
        RpdbDebugger().set_default_password()
        RpdbDebugger().set_default_host()
    
    def _setdebuggeroptions(self):
        config = Profile_Get(ToolConfig.PYTOOL_CONFIG, default=dict())
        trap = config.get(ToolConfig.TLC_TRAP_EXCEPTIONS, True)
        RpdbDebugger().set_trap_unhandled_exceptions(trap)
        synchronicity = config.get(ToolConfig.TLC_SYNCHRONICITY, True)
        RpdbDebugger().set_synchronicity(synchronicity)
        autofork = config.get(ToolConfig.TLC_AUTO_FORK, True)
        forkmode = config.get(ToolConfig.TLC_FORK_MODE, False)
        RpdbDebugger().set_fork_mode(forkmode, autofork)
        encoding = config.get(ToolConfig.TLC_EXECEVALENCODING, "auto")
        escaping = config.get(ToolConfig.TLC_EXECEVALESCAPING, True)
        RpdbDebugger().set_encoding(encoding, escaping)
        mode = config.get(ToolConfig.TLC_LINT_AUTORUN, False)
        if mode:
            config[ToolConfig.TLC_LINT_AUTORUN] = False
            Profile_Set(ToolConfig.PYTOOL_CONFIG, config)
            self._listCtrl.AppendUpdate(self.disablingpylinttext)
            self._listCtrl.restoreautorun = self.restorepylint_autorun
        else:
            self._listCtrl.restoreautorun = lambda:None

    def _debug(self, filetype, vardict, filename):
        debugger = self.get_debugger(filetype, vardict, filename)
        if not debugger:
            return []
        self._debugger = debugger
        self._curfile = filename
        
        self._setdebuggerdefaults()
        self._setdebuggeroptions()
        # Start job timer
        self._StopTimer()
        self._jobtimer.Start(250, True)

    def OnJobTimer(self, evt):
        """Start a debug job"""
        if self._debugger:
            util.Log("[PyDebug][info] fileName %s" % (self._curfile))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (self._mw.GetId(), True))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (self._mw.GetId(), -1, -1))
            self.abortfn = self._abort
            self.DisableButtons()
            self._debugger.Debug()

    def OnAbort(self, event):
        self.abortfn()

    def _abort(self):
        """Stop debugging"""
        RpdbDebugger().do_abort()

    def _detach(self):
        """Detach debugger"""
        RpdbDebugger().debuggerdetachedtext = self.emptytext
        RpdbDebugger().do_detach()
        self._listCtrl.AppendUpdate(self.debuggerdetachedtext)
        self._listCtrl.Stop()

    def OnStepIn(self, event):
        """Step in to the code on the current line"""
        RpdbDebugger().do_step()

    def OnStepOver(self, event):
        """Step over the code on the current line"""
        RpdbDebugger().do_next()

    def OnStepOut(self, event):
        """Step out of the current scope"""
        RpdbDebugger().do_return()

    def OnBreak(self, event):
        """Break now"""
        RpdbDebugger().do_break()

    def OnRemote(self, event):
        """Remote debug"""
        if RpdbDebugger().attached:
            return
        attach_dialog = AttachDialog(self)
        r = attach_dialog.ShowModal()
        if r == wx.ID_OK:
            server = attach_dialog.get_server()
            debugger = self.get_debugger(synglob.ID_LANG_PYTHON, {}, "")
            if not debugger:
                return []
            self._debugger = debugger
            self._remotetext = _("Debugging remote debuggee %s\n\n" % server.m_filename)
            self._listCtrl.SetText(self._remotetext)
            self._listCtrl.Start(100)
            RpdbDebugger().do_abort()
            RpdbDebugger().debuggerattachedtext = self.debuggerattachedtextremote
            RpdbDebugger().debuggerdetachedtext = self.debuggerdetachedtext
            RpdbDebugger().remoteprocess = True
            dpc = DummyProcessCreator(server.m_rid, self.UpdateOutput, lambda:None)
            dpc.restorepath = lambda:None
            self._debugger.processcreator = dpc
            self._setdebuggeroptions()
            self.abortfn = self._detach
            self.DisableButtons()
            self._debugger.RunDebugger()
        
        attach_dialog.Destroy()

    def UpdateOutput(self, txt):
        """Check to prevent PyDeadObjectErrors"""
        if self and self._listCtrl:
            self._listCtrl.AppendUpdate(txt)
