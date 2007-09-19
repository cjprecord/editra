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
from profiler import Profile_Get
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

    def __SetupFonts(self):
        """Create the font settings for the shell"""
        fonts = { 
                  'size'      : 11,
                  'lnsize'    : 10,
                  'backcol'   : '#FFFFFF',
                  'calltipbg' : '#FFFFB8',
                  'calltipfg' : '#404040',
        }

        font = Profile_Get('FONT1', 'font', wx.Font(11, wx.FONTFAMILY_MODERN, 
                                                        wx.FONTSTYLE_NORMAL, 
                                                        wx.FONTWEIGHT_NORMAL))
        if font.IsOk() and len(font.GetFaceName()):
            fonts['mono'] = font.GetFaceName()
            fonts['size'] = font.GetPointSize()
            if fonts['size'] < 11:
                fonts['size'] = 11
            fonts['lnsize'] = fonts['size'] - 1

        font = Profile_Get('FONT2', 'font', wx.Font(11, wx.FONTFAMILY_SWISS, 
                                                        wx.FONTSTYLE_NORMAL, 
                                                        wx.FONTWEIGHT_NORMAL))
        if font.IsOk() and len(font.GetFaceName()):
            fonts['times'] = font.GetFaceName()
            fonts['helv'] = font.GetFaceName()
            fonts['other'] = font.GetFaceName()

        return fonts

    def AllowMultiple(self):
        """PyShell allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a PyShell Panel"""
        self._log = wx.GetApp().GetLog()
        self._log("[pyshell][info] Creating PyShell instance for Shelf")
        pyshell = shell.Shell(parent, locals=dict())
        pyshell.setStyles(self.__SetupFonts())
        return pyshell

    def GetId(self):
        return self.ID_PYSHELL

    def GetMenuEntry(self, menu):
        return wx.MenuItem(menu, self.ID_PYSHELL, self.__name__, 
                                        _("Open A Python Shell"))

    def GetName(self):
        return self.__name__
