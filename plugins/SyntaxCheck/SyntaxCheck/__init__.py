# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Syntax Checker plugin                                              #
# Author: Giuseppe "Cowo" Corbelli                                            #
# Copyright: (c) 2009 Giuseppe "Cowo" Corbelli                                #
# License: wxWindows License                                                  #
###############################################################################

# Plugin Metadata
""" Syntax checker plugin.
It's a simple Shelf window that can do syntax checking for some kind of files.
Syntax checking is triggered by the Save action.
Currently supported languages are:
  - python: check implemented by means of compile() function
  - php: check implemented by "php -l" execution

"""
__version__ = "0.2"
__author__ = "Giuseppe 'Cowo' Corbelli"
__svnid__ = "$Id: __init__.py 961 2010-05-21 08:33:03Z cowo78 $"
__revision__ = "$Revision: 961 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra imports
import ed_glob
import iface
import plugin
import util

# Local Imports
from SyntaxWindow import SyntaxCheckWindow

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Implementation
class SyntaxCheck(plugin.Plugin):
    """Script Launcher and output viewer"""
    plugin.Implements(iface.ShelfI)
    ID_SYNTAXCHECK = wx.NewId()
    INSTALLED = False
    SHELF = None

    @property
    def __name__(self):
        return u'SyntaxCheck'

    def AllowMultiple(self):
        """Launch allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Create a Launch panel"""
        util.Log("[Launch][info] Creating SyntaxCheck instance for Shelf")
        return SyntaxCheckWindow(parent)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        return bmp

    def GetId(self):
        """The unique identifier of this plugin"""
        return self.ID_SYNTAXCHECK

    def GetMenuEntry(self, menu):
        """This plugins menu entry"""
        item = wx.MenuItem(menu, self.ID_SYNTAXCHECK, self.__name__,
                           _("Show syntax checker"))
        item.SetBitmap(self.GetBitmap())
        return item

    def GetMinVersion(self):
        """Minimum version of Editra this plugin is compatible with"""
        return "4.89"

    def GetName(self):
        """The name of this plugin"""
        return self.__name__

    def InstallComponents(self, mainw):
        """Install extra menu components
        param mainw: MainWindow Instance

        """
        pass

    def IsInstalled(self):
        """Check whether launch has been installed yet or not
        @note: overridden from Plugin
        @return bool

        """
        return SyntaxCheck.INSTALLED

    def IsStockable(self):
        """This item can be reloaded between sessions"""
        return True

#-----------------------------------------------------------------------------#
