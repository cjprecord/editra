#!/usr/bin/env python
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
"""Adds Hello World to the View Menu"""
__author__ = "Cody Precord"
__version__ = "0.01"

import wx
import ed_main
import ed_menu
import plugin

ID_HELLO = wx.NewId()
class Hello(plugin.Plugin):
    """Adds Hello World to the View Menu"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
       """Adds the view menu entry registers the event handler"""
       mw = parent
       self._log = wx.GetApp().GetLog()
       if mw:
           self._log("[hello] Installing Hello World")
	   mb = mw.GetMenuBar()
	   hm = mb.GetMenuByName("view")
	   hm.Append(ID_HELLO, _("Hello World"), _("Open a Hello World Dialog"))
	   mw.Bind(wx.EVT_MENU, self.OnHello, id=ID_HELLO)
       else:
           self._log("[hello][err] Failed to install hello plugin")

    def OnHello(self, evt):
       """Opens the hello dialog"""
       e_id = evt.GetId()
       if e_id == ID_HELLO:
           dlg = wx.MessageBox(_("Hello World from the hello plugin"), _("Hello World"))
       else:
           evt.Skip()

