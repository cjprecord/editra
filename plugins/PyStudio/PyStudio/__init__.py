# -*- coding: utf-8 -*-
# Name: __init__.py
# Purpose: Plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

# Plugin Metadata
"""
Upgrades Editra into a Python IDE, including syntax checking, module search and debugging

"""

__version__ = "0.1"
__author__ = "Mike Rans, Cody Precord"
__svnid__ = "$Id: __init__.py 1543 2012-06-08 16:09:40Z CodyPrecord $"
__revision__ = "$Revision: 1543 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import ed_glob
import ed_fmgr
import ed_main
import iface
import plugin
import util

# Local Imports
from PyStudio.Common import Images
from PyStudio.Common.ToolConfig import ToolConfigPanel
from PyStudio.Common.BaseShelfPlugin import BaseShelfPlugin
from PyStudio.SyntaxChecker.LintShelfWindow import LintShelfWindow
from PyStudio.SyntaxChecker.CompileChecker import CompileEntryPoint
from PyStudio.ModuleFinder.FindTabMenu import FindTabMenu
from PyStudio.ModuleFinder.FindShelfWindow import FindShelfWindow
from PyStudio.Debugger.DebugShelfWindow import DebugShelfWindow
from PyStudio.Debugger.BreakPointsShelfWindow import BreakPointsShelfWindow, BreakpointController
from PyStudio.Debugger.StackThreadShelfWindow import StackThreadShelfWindow
from PyStudio.Debugger.VariablesShelfWindow import VariablesShelfWindow
from PyStudio.Debugger.ExpressionsShelfWindow import ExpressionsShelfWindow
from PyStudio.Debugger.MessageHandler import MessageHandler
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger
from PyStudio.Project.ProjectMgr import ProjectManager

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

# Implementation
class PyAnalysis(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyAnalysis, self).__init__(pluginmgr, "PyAnalysis", LintShelfWindow)

    def AllowMultiple(self):
        """Plugin allows multiple instances"""
        return True

    def InstallComponents(self, parent):
        """Initialize and install"""
        setattr(self, '_installed', True)
        CompileEntryPoint()

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Images.Lint.Bitmap

class PyFind(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyFind, self).__init__(pluginmgr, "PyFind", FindShelfWindow)

    def AllowMultiple(self):
        """Plugin allows multiple instances"""
        return True

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FIND), wx.ART_MENU)
        return bmp

    def InstallComponents(self, parent):
        """Initialize and install"""
        setattr(self, '_installed', True)
        FindTabMenu() # Initialize singleton tab menu handler

    def IsInstalled(self):
        return getattr(self, '_installed', False)

class PyDebug(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyDebug, self).__init__(pluginmgr, "PyDebug", DebugShelfWindow)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Images.Bug.Bitmap

    def InstallComponents(self, parent):
        """Initialize and install"""
        setattr(self, '_installed', True)
        # Initialize singletons
        RpdbDebugger()
        MessageHandler()
        BreakpointController()

    def IsInstalled(self):
        return getattr(self, '_installed', False)

class PyBreakPoint(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyBreakPoint, self).__init__(pluginmgr, "PyBreakPoint", BreakPointsShelfWindow)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Images.Bug.Bitmap

class PyStackThread(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyStackThread, self).__init__(pluginmgr, "PyStackThread", 
                                            StackThreadShelfWindow)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Images.Bug.Bitmap

class PyVariable(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyVariable, self).__init__(pluginmgr, "PyVariable", 
                                         VariablesShelfWindow)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Images.Bug.Bitmap

class PyExpression(BaseShelfPlugin):
    """Script Launcher and output viewer"""
    def __init__(self, pluginmgr):
        super(PyExpression, self).__init__(pluginmgr, "PyExpression",
                                           ExpressionsShelfWindow)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Images.Bug.Bitmap

class PyProject(plugin.Plugin):
    """Python Project component of PyStudio
    Implements the MainWindowI to provide a file management window.

    """
    plugin.Implements(iface.MainWindowI)
    ID_PYPROJECT = wx.NewId()
    def PlugIt(self, mainw):
        """Install the components provided by this plugin"""
        pmgr = ProjectManager(mainw)
        info = ed_fmgr.EdPaneInfo()
        info = info.Name(ProjectManager.PANE_NAME).\
                    Caption(u"PyProject").Left().Layer(1).\
                    CloseButton(True).MaximizeButton(True).\
                    BestSize(wx.Size(215, 350))
        mainw.PanelMgr.AddPane(pmgr, info)
        mainw.PanelMgr.Update()

        # Setup Menu(s)
        viewm = mainw.MenuBar.GetMenuByName("view")
        viewm.InsertAlpha(PyProject.ID_PYPROJECT,
                          _("PyProject"), 
                          _("Open PyStudio Project side panel"),
                          wx.ITEM_CHECK,
                          after=ed_glob.ID_PRE_MARK)

    def GetMenuHandlers(self):
        """Pass even handler for menu item to main window for management"""
        return [(PyProject.ID_PYPROJECT, self.OnShowProjectWindow)]

    def GetMinVersion(self):
        return "0.7.08" # all new file view controls and other interfaces needed

    def GetUIHandlers(self):
        """Pass Ui handlers to main window for management"""
        return [(PyProject.ID_PYPROJECT, self.OnUpdateMenu)]

    def OnShowProjectWindow(self, evt):
        """Show the project window in the current MainWindow."""
        if evt.Id == PyProject.ID_PYPROJECT:
            mainw = wx.GetApp().GetActiveWindow()
            if mainw and isinstance(mainw, ed_main.MainWindow):
                pane = mainw.PanelMgr.GetPane(ProjectManager.PANE_NAME)
                if pane.IsShown():
                    pane.Hide()
                else:
                    pane.Show()
                mainw.PanelMgr.Update()
        else:
            util.Log("[PyStudio][warn] Can't show PyProject panel")

    def OnUpdateMenu(self, evt):
        """Update menu state"""
        if evt.Id == PyProject.ID_PYPROJECT:
            mainw = wx.GetApp().GetActiveWindow()
            if mainw and isinstance(mainw, ed_main.MainWindow):
                pane = mainw.PanelMgr.GetPane(ProjectManager.PANE_NAME)
                evt.Check(pane.IsShown())
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#
# Configuration Interface

def GetConfigObject():
    return ConfigObject()

class ConfigObject(plugin.PluginConfigObject):
    """Plugin configuration object for PyStudio
    Provides configuration panel for plugin dialog.

    """
    def GetConfigPanel(self, parent):
        """Get the configuration panel for this plugin
        @param parent: parent window for the panel
        @return: wxPanel

        """
        return ToolConfigPanel(parent)

    def GetLabel(self):
        """Get the label for this config panel
        @return string

        """
        return _("PyStudio")
