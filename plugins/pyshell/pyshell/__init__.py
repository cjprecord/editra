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
__version__ = "0.3"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.aui
from wx.py import shell
import ed_glob
import profiler
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
            self._mi.Check(profiler.Profile_Get('PYSHELL', 'bool', False))
            pyshell = shell.Shell(mw, locals=dict())
            mw._mgr.AddPane(pyshell, wx.aui.AuiPaneInfo().Name(PANE_NAME).\
                            Caption("Editra | PyShell").Bottom().Layer(0).\
                            CloseButton(True).MaximizeButton(False).\
                            BestSize(wx.Size(500,250)))
            if profiler.Profile_Get('PYSHELL', 'bool', False):
                mw._mgr.GetPane(PANE_NAME).Show()
            else:
                profiler.Profile_Set('PYSHELL', False)
                mw._mgr.GetPane(PANE_NAME).Hide()
            
            # Event Handlers
            mw.Bind(wx.EVT_MENU, self.OnShowShell, id = ID_PYSHELL)
            mw.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def OnPaneClose(self, evt):
        """Handles when a pane is closed and updates the profile"""
        pane = evt.GetPane()
        if pane.name == PANE_NAME:
            profiler.Profile_Set('PYSHELL', False)
            self._mi.Check(False)
        else:
            evt.Skip()

    def OnShowShell(self, evt):
        """Shows the python shell frame"""
        if evt.GetId() == ID_PYSHELL:
            mw = wx.GetApp().GetMainWindow().GetFrameManager()
            pane = mw.GetPane("PyShell")
            if profiler.Profile_Get('PYSHELL', 'bool') and pane.IsShown():
                self._log("[pyshell] Hide PyShell")
                profiler.Profile_Set('PYSHELL', False)
                pane.Hide()
                self._mi.Check(False)
            else:
                self._log("[pyshell] Show PyShell")
                profiler.Profile_Set('PYSHELL', True)
                pane.Show()
                self._mi.Check(True)
            mw.Update()
        else:
            evt.Skip()
