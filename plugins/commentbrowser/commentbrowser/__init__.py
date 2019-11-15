#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: CommentBrowser Plugin                                              #
# Author: DR0ID <dr0iddr0id@googlemail.com>                                   #
# Copyright: (c) 2008 DR0ID                                                   #
# License: wxWindows License                                                  #
###############################################################################
# Plugin Meta
"""Adds a Comment Browser Sidepanel"""
__author__ = "DR0ID"
__version__ = "0.4"

#-----------------------------------------------------------------------------#
# Imports
import wx.aui

# Libs from Editra
import ed_glob
import iface
import plugin
from profiler import Profile_Get, Profile_Set

# Local imports
import cbrowser

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

# Try and add this plugins message catalogs to the app
try:
    wx.GetApp().AddMessageCatalog('commentbrowser', __name__)
except:
    pass

#-----------------------------------------------------------------------------#
# Interface implementation
class CommentBrowserPanel(plugin.Plugin):
    """Adds a commentbrowser to the view menu"""
    
    plugin.Implements(iface.MainWindowI, iface.ShelfI)

    @property
    def __name__(self):
        return cbrowser.PANE_NAME

    def AllowMultiple(self):
        """Shelf interface"""
        return False

    def CreateItem(self, parent):
        """Shelf Interface"""
        return cbrowser.CBrowserPane(parent)

    def GetId(self):
        """Shelf Interface"""
        return cbrowser.ID_CB_SHELF

    def GetMenuEntry(self, menu):
        """Shelf Interface"""
        return wx.MenuItem(menu, cbrowser.ID_CB_SHELF, _("CommentBrowser"))

    def GetName(self):
        """Shelf Interface"""
        return _("CommentBrowser")

    def IsStockable(self):
        """Shelf Interface"""
        return True

    ### MainWindowI Implementation ###
    def PlugIt(self, parent):
        """ Adds the view menu entry and registers the event handler"""
        self._mainwin = parent
        self._log = wx.GetApp().GetLog()
        if self._mainwin != None:
            self._log("[commentbrowser] Installing commentbrowser plugin")

            #---- Add Menu Items ----#
            viewm = self._mainwin.GetMenuBar().GetMenuByName('view')
            mi = viewm.InsertAlpha(cbrowser.ID_COMMENTBROWSE,
                                   _('Comment Browser'),
                                   _('Open Comment Browser Sidepanel'),
                                   wx.ITEM_CHECK,
                                   after=ed_glob.ID_PRE_MARK)

            #---- Make the Panel ----#
            self._commentbrowser = cbrowser.CBrowserPane(self._mainwin, 
                                                         cbrowser.ID_CBROWSERPANE,
                                                         menu=mi)
            mgr = self._mainwin.GetFrameManager()
            mgr.AddPane(self._commentbrowser, 
                        wx.aui.AuiPaneInfo().Name(cbrowser.PANE_NAME).\
                        Caption(_("Comment Browser")).Bottom().Layer(1).\
                        CloseButton(True).MaximizeButton(True).\
                        BestSize(wx.Size(-1, 350)))

            # Get settings from profile
            if Profile_Get(cbrowser.CB_KEY, 'bool', False):
                mgr.GetPane(cbrowser.PANE_NAME).Show()
            else:
                mgr.GetPane(cbrowser.PANE_NAME).Hide()

            mgr.Update()
            
    def GetMenuHandlers(self):
        """Pass event handler for menu item to main window for management"""
        return [(cbrowser.ID_COMMENTBROWSE, self._commentbrowser.OnShow)]

    def GetUIHandlers(self):
        """Pass Ui handlers to main window for management"""
        return [(cbrowser.ID_COMMENTBROWSE, self._commentbrowser.OnUpdateMenu)]
