# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: PyRun Plugin                                                       #
# Author: Fred Lionetti <flionetti@gmail.com>
#         based closely on Cody Precord's PyShell                             #
# Copyright: (c) 2007 Fred Lionetti <flionetti@gmail.com>                     #
# Licence: wxWindows Licence                                                  #
###############################################################################
# Plugin Metadata
"""Executes python script in the Shelf"""
__author__ = "Fred Lionetti"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Local modules
import outwin

# Editra imports
import iface
import plugin
import syntax.synglob as synglob

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class PyRun(plugin.Plugin):
    """Adds a PyRun to the Shelf"""
    plugin.Implements(iface.ShelfI)
    ID_PYRUN = wx.NewId()
    __name__ = u'PyRun'

    def AllowMultiple(self):
        """PyRun allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a PyRun Panel"""
        self._log = wx.GetApp().GetLog()
        self._log("[PyRun][info] Creating PyRun instance for Shelf")

        output = outwin.OutputWindow(parent)
        window = wx.GetApp().GetTopWindow()
        if getattr(window, '__name__', ' ') == 'MainWindow':
            ctrl = window.GetNotebook().GetCurrentCtrl()
            if ctrl.GetLangId() == synglob.ID_LANG_PYTHON:
                wx.CallLater(100, output.SetScript, ctrl.GetFileName())
        return output

    def GetId(self):
        return self.ID_PYRUN

    def GetMenuEntry(self, menu):
        return wx.MenuItem(menu, self.ID_PYRUN, self.__name__, 
                           _("Executes a python script"))

    def GetName(self):
        return self.__name__

#-----------------------------------------------------------------------------#
