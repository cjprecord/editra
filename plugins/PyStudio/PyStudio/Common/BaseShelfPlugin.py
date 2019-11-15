# -*- coding: utf-8 -*-
# Name: BaseShelfPlugin.py
# Purpose: Base shelf plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

# Plugin Metadata
"""
Base shelf plugin.

"""

__author__ = "Mike Rans"
__svnid__ = "$Id: BaseShelfPlugin.py 1546 2012-07-29 18:35:50Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1546 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import ed_glob
import iface
import plugin
import util

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Implementation
class BaseShelfPlugin(plugin.Plugin):
    """Script Launcher and output viewer"""
    plugin.Implements(iface.ShelfI)
    
    def __init__(self, pluginmgr, pluginname, shelfwindow):
        """Plugin interface base class for all Shelf plugins
        @param pluginmgr: Editra plugin manager instance
        @param pluginname: This plugin's name
        @param shelwindow: Window class object

        """
        super(BaseShelfPlugin, self).__init__()

        # Attributes
        self.pluginmgr = pluginmgr
        self.pluginname = pluginname
        self.shelfwindow = shelfwindow
        self.pluginid = wx.NewId()
        self.installed = False
        self.shelf = None

    @property
    def __name__(self):
        return self.pluginname

    def AllowMultiple(self):
        """Plugin allows multiple instances"""
        return False

    def CreateItem(self, parent):
        """Create a panel"""
        util.Log("[%s][info] Creating %s instance for Shelf" % \
                  (self.pluginname, self.pluginname))
        return self.shelfwindow(parent)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        return bmp

    def GetId(self):
        """The unique identifier of this plugin"""
        return self.pluginid

    def GetMenuEntry(self, menu):
        """This plugins menu entry"""
        item = wx.MenuItem(menu, self.pluginid, self.__name__,
                           _("Show %s" % self.pluginname))
        item.SetBitmap(self.GetBitmap())
        return item

    def GetMinVersion(self):
        """Minimum version of Editra this plugin is compatible with"""
        return "0.7.08"

    def GetName(self):
        """The name of this plugin"""
        return self.__name__

    def InstallComponents(self, mainw):
        """Install extra menu components
        param mainw: MainWindow Instance

        """
        pass

    def IsInstalled(self):
        """Check whether the plugin has been installed yet or not
        @note: overridden from Plugin
        @return bool

        """
        return self.installed

    def IsStockable(self):
        """This item can be reloaded between sessions"""
        return True
