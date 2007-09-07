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
"""Simple Programmer's Calculator"""
__author__ = "Cody Precord"
__version__ = "0.2"

import wx
import ed_glob
import ed_main
import plugin
import calc

#-----------------------------------------------------------------------------#

class Calculator(plugin.Plugin):
    """Simple Programmer's Calculator"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
        """Hook the calculator into the menu and bind the event"""
        self._mw = parent
        self._log = wx.GetApp().GetLog()
        self._log("[calc] Installing calculator plugin")

        # Add Menu
        mb = self._mw.GetMenuBar()
        vm = mb.GetMenuByName("view")
        self._mi = vm.InsertAlpha(calc.ID_CALC, _("Calculator"), 
                                 ("Open Calculator"), wx.ITEM_CHECK, 
                                 after=ed_glob.ID_PRE_MARK)

        # Event Handlers
        self._mw.Bind(wx.EVT_MENU, self.OnShowCalc, id=calc.ID_CALC)

    def OnCalcClose(self):
        """Called when calculator is closed to update menu"""
        self._mi.Check(False)

    def OnShowCalc(self, evt):
        """Shows the calculator"""
        if evt.GetId() == calc.ID_CALC:
            self._log("[calc] Calculator opened")
            if calc.CalcFrame.INSTANCE is None:
                cframe = calc.CalcFrame(None, "Editra | Calculator", 
                                                self.OnCalcClose)
                self._mi.Check(True)
                cframe.Show()
            else:
                self._mi.Check(False)
                calc.CalcFrame.INSTANCE.Destroy()
                calc.CalcFrame.INSTANCE = None
        else:
            evt.Skip()
