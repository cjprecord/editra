# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################
# Plugin Metadata
"""Adds a PyShell to the Shelf"""
__author__ = "Cody Precord"
__version__ = "0.4"

#-----------------------------------------------------------------------------#
# Imports
import wx
from wx.py import shell
import iface
import plugin

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class PyShell(plugin.Plugin):
    """Adds a PyShell to the Shelf"""
    plugin.Implements(iface.ShelfI)
    ID_PYSHELL = wx.NewId()
    __name__ = u'PyShell'

    def AllowMultiple(self):
        """PyShell allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a PyShell Panel"""
        self._log = wx.GetApp().GetLog()
        self._log("[pyshell][info] Creating PyShell instance for Shelf")
        pyshell = shell.Shell(parent, locals=dict())
        return pyshell

    def GetId(self):
        return self.ID_PYSHELL

    def GetMenuEntry(self, menu):
        return wx.MenuItem(menu, self.ID_PYSHELL, self.__name__, 
                                        _("Open A Python Shell"))

    def GetName(self):
        return self.__name__
