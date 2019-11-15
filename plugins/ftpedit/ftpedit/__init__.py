###############################################################################
# Name: __init__.py                                                           #
# Purpose: Ftp Edit Plugin                                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################
# Plugin Metadata
"""Edit files over ftp (Editra > 0.4.28)"""

__author__ = "Cody Precord <cprecord@editra.org>"
__version__ = "0.3"
__svnid__ = "$Id: __init__.py 1223 2011-04-06 15:20:53Z CodyPrecord $"
__revision__ = "$Revision: 1223 $"

#-----------------------------------------------------------------------------#
# Imports
import wx 

# Editra Libraries
import plugin 
import ed_glob
import iface
import ed_menu
import util

# Local Imports
import ftpwindow

#-----------------------------------------------------------------------------#
ID_FTPWINDOW = wx.NewId()

# Try and add this plugins message catalogs to the app
try:
    wx.GetApp().AddMessageCatalog('ftpedit', __name__)
except:
    pass

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class FtpEdit(plugin.Plugin):
    """Shelf interface implementation for the Ftp Window"""
    plugin.Implements(iface.ShelfI)

    @property
    def __name__(self):
        return u'Ftp'

    def AllowMultiple(self):
        """Ftp Window allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a Ftp Window"""
        return ftpwindow.FtpWindow(parent)

    def GetBitmap(self):
        """Get the tab icon
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_WEB), wx.ART_MENU)
        return bmp

    def GetId(self):
        """Plugin menu identifier ID"""
        return ID_FTPWINDOW

    def GetMenuEntry(self, menu):
        """Get the menu entry for the log viewer
        @param menu: the menu items parent menu

        """
        item = wx.MenuItem(menu, ID_FTPWINDOW, _("Ftp Window"),
                           _("Ftp File Window"))
        item.SetBitmap(self.GetBitmap())
        return item

    def GetMinVersion(self):
        """Get the minimum version of Editra that this plugin supports"""
        return "0.6.26"

    def GetName(self):
        """Return the name of this control"""
        return self.__name__

    def IsStockable(self):
        """ModList can be saved in the shelf preference stack"""
        return True
