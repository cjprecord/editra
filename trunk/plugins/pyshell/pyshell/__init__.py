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
"""Adds a PyShell to the View Menu"""
__author__ = "Cody Precord"
__version__ = "0.2"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.aui
from wx.py import shell
import ed_glob
import ed_main
import ed_menu
import plugin

#-----------------------------------------------------------------------------#
# Globals
PANE_NAME = u'PyShell'
ID_PYSHELL = wx.NewId()
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class PyShell(plugin.Plugin):
    """Adds a PyShell to the MainWindow's View Menu"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
        mw = parent
        self._log = wx.GetApp().GetLog()
        if mw != None:
            self._log("[pyshell] Installing PyShell Plugin")
            mb = mw.GetMenuBar()
            vm = mb.GetMenuByName("view")
            self._mi = vm.InsertAlpha(ID_PYSHELL, _(PANE_NAME), _("Show A Python Shell"), 
                                      wx.ITEM_CHECK, after=ed_glob.ID_PRE_MARK)
            self._mi.Check(ed_glob.PROFILE.get('PYSHELL', False))
            pyshell = shell.Shell(mw, wx.ID_ANY)
            mw._mgr.AddPane(pyshell, wx.aui.AuiPaneInfo().Name(PANE_NAME).\
                            Caption("Editra | PyShell").Bottom().Layer(0).\
                            CloseButton(True).MaximizeButton(False).\
                            BestSize(wx.Size(500,250)))
            if ed_glob.PROFILE.get('PYSHELL', False):
                mw._mgr.GetPane(PANE_NAME).Show()
            else:
                ed_glob.PROFILE['PYSHELL'] = False
                mw._mgr.GetPane(PANE_NAME).Hide()
            
            # Event Handlers
            mw.Bind(wx.EVT_MENU, self.OnShowShell, id = ID_PYSHELL)
            mw.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def OnPaneClose(self, evt):
        """Handles when a pane is closed and updates the profile"""
        pane = evt.GetPane()
        if pane.name == PANE_NAME:
            ed_glob.PROFILE['PYSHELL'] = False
            self._mi.Check(False)
        else:
            evt.Skip()

    def OnShowShell(self, evt):
        """Shows the python shell frame"""
        mw = wx.GetApp().GetMainWindow().GetFrameManager()
        if evt.GetId() == ID_PYSHELL:
            if ed_glob.PROFILE['PYSHELL']:
                self._log("[pyshell] Hide PyShell")
                ed_glob.PROFILE['PYSHELL'] = False
                mw.GetPane("PyShell").Hide()
            else:
                self._log("[pyshell] Show PyShell")
                ed_glob.PROFILE['PYSHELL'] = True
                mw.GetPane("PyShell").Show()
            mw.Update()
        else:
            evt.Skip()
