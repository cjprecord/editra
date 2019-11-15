# -*- coding: utf-8 -*-
# Name: BaseShelfWindow.py
# Purpose: Base shelf window
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Base Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: BaseShelfWindow.py 1544 2012-07-28 17:42:31Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1544 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import ed_glob
import util
import eclib
import ed_basewin
import ed_msg
import syntax.synglob as synglob

# Local imports
from PyStudio.Common.ToolConfig import ToolConfigDialog
from PyStudio.Common.PythonDirectoryVariables import PythonDirectoryVariables
from PyStudio.Common.Messages import PyStudioMessages

# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class BaseShelfWindow(ed_basewin.EdBaseCtrlBox):
    """Base class for most PyStudio Shelf Extensions"""
    __directoryVariables = {
        synglob.ID_LANG_PYTHON: PythonDirectoryVariables
    }

    def __init__(self, parent):
        """Initialize the window"""
        super(BaseShelfWindow, self).__init__(parent)

        # Attributes
        # Parent is ed_shelf.EdShelfBook
        self._mw = ed_basewin.FindMainWindow(self)
        self._log = wx.GetApp().GetLog()
        self.ctrlbar = None
        self.taskbtn = None
        self.cfgbtn = None
        self._listCtrl = None
        self._imglst = list()
        self._curfile = u""
        self._hasrun = False
        self._jobtimer = None
        self.destroyfn = lambda : None

        # PyStudio specific messages
        ed_msg.Subscribe(self.OnProjectLoaded, PyStudioMessages.PYSTUDIO_PROJECT_LOADED)

    # Properties
    TaskButton = property(lambda self: self.taskbtn)
    ConfigButton = property(lambda self: self.cfgbtn)
    ListWindow = property(lambda self: self.listCtrl)

    def setup(self, listCtrl, *args):
        """Setup the base shelf window"""
        self._listCtrl = listCtrl
        self._curfile = u""
        self._hasrun = False
        self._jobtimer = wx.Timer(self)

        # Setup
        if len(args) == 0:
            self._listCtrl.set_mainwindow(self._mw)            
        else:
            for ctrl in args:
                ctrl.set_mainwindow(self._mw)            
                
        self.ctrlbar = self.CreateControlBar(wx.TOP)
        self.cfgbtn = self.AddPlateButton(u"", ed_glob.ID_PREF, wx.ALIGN_LEFT)
        self.cfgbtn.SetToolTipString(_("Configure"))
        return self.ctrlbar

    def layout(self, taskbtndesc=None, taskfn=None, timerfn=None):
        """Layout the shelf window"""
        if taskfn:
            rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
            if rbmp.IsNull() or not rbmp.IsOk():
                rbmp = None
            self.taskbtn = eclib.PlateButton(self.ctrlbar, wx.ID_ANY, _(taskbtndesc), rbmp,
                                            style=eclib.PB_STYLE_NOBG)
            self.ctrlbar.AddControl(self.taskbtn, wx.ALIGN_RIGHT)
            self.Bind(wx.EVT_BUTTON, taskfn, self.taskbtn)

        # Layout
        self.SetWindow(self._listCtrl)
        self.SetControlBar(self.ctrlbar, wx.TOP)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnShowConfig, self.cfgbtn)
        if timerfn:
            self.Bind(wx.EVT_TIMER, timerfn, self._jobtimer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)

        # Editra Message Handlers
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        ed_msg.Subscribe(self.OnFontChanged, ed_msg.EDMSG_DSP_FONT)

    def GetMainWindow(self):
        """Get the Editra main window that owns this shelf object"""
        return self._mw

    # Overridden by derived classes
    def Unsubscription(self):
        pass

    def DoProjectLoaded(self, projfile):
        """Called when a project has been loaded
        @param projfile: ProjectFile

        """
        pass

    # End Overrides

    def OnDestroy(self, evt):
        """Stop timer and disconnect message handlers"""
        self._StopTimer()
        ed_msg.Unsubscribe(self.OnThemeChanged)
        ed_msg.Unsubscribe(self.OnFontChanged)
        ed_msg.Unsubscribe(self.OnProjectLoaded)
        self.Unsubscription()

    def _StopTimer(self):
        if self._jobtimer.IsRunning():
            self._jobtimer.Stop()

    def OnThemeChanged(self, msg):
        """Icon theme has changed so update button"""
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
        self.cfgbtn.SetBitmap(bmp)
        self.cfgbtn.Refresh()

    def OnFontChanged(self, msg):
        """Update for user font"""
        font = msg.GetData()
        if isinstance(font, wx.Font) and not font.IsNull():
            self.SetFont(font)
            if self._listCtrl:
                self._listCtrl.SetFont(font)

    def OnShowConfig(self, event):
        """Show the configuration dialog"""
        dlg = ToolConfigDialog(self._mw)
        dlg.CenterOnParent()
        dlg.ShowModal()

    def OnProjectLoaded(self, msg):
        """Project was loaded in the PyProject window.
        Handles updates for when the current project changes.

        """
        util.Log("[PyStudio][info] BaseShelfWindow - project loaded notification")
        self.DoProjectLoaded(msg.GetData())

    def get_directory_variables(self, filetype):
        """Get the directory variables for the file type."""
        try:
            return self.__directoryVariables[filetype]()
        except Exception:
            pass
        return None

    def Clear(self):
        """Clear the list view"""
        self._listCtrl.Clear()
        