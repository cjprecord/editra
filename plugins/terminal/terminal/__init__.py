# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Cody Precord                                                       #
# Author: Cody Precord <cprecord@editra.org                                   #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
# Plugin Metadata
"""Adds a graphical shell to the Shelf"""
__author__ = "Cody Precord"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import wx
import iface
import plugin
import terminal

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class Terminal(plugin.Plugin):
    """Adds a Terminal to the Shelf"""
    plugin.Implements(iface.ShelfI)
    ID_TERM = wx.NewId()
    __name__ = u'Terminal'

    def AllowMultiple(self):
        """Terminal allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a Terminal Panel"""
        self._log = wx.GetApp().GetLog()
        self._log("[term][info] Creating Terminal instance for Shelf")
        return terminal.Xterm(parent, wx.ID_ANY)

    def GetId(self):
        return self.ID_TERM

    def GetMenuEntry(self, menu):
        return wx.MenuItem(menu, self.ID_TERM, self.__name__, _("Open A Terminal"))

    def GetName(self):
        return self.__name__
