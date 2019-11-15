###############################################################################
# Name: __init__.py                                                           #
# Purpose: Simple Calculator Plugin                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
"""Simple Programmer's Calculator"""
__author__ = "Cody Precord"
__version__ = "0.6"

#-----------------------------------------------------------------------------#
# Imports
import wx
import ed_glob
import iface
import plugin
import util

# Local imports
import calc

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

# Try and add this plugins message catalogs to the app
try:
    wx.GetApp().AddMessageCatalog('calculator', __name__)
except:
    pass

#-----------------------------------------------------------------------------#

class Calculator(plugin.Plugin):
    """Simple Programmer's Calculator"""
    plugin.Implements(iface.MainWindowI)
    def PlugIt(self, parent):
        """Hook the calculator into the menu and bind the event"""
        util.Log("[calc][info] Installing calculator plugin")

        # Add Menu
        viewm = parent.GetMenuBar().GetMenuByName("view")
        mitem = viewm.InsertAlpha(calc.ID_CALC, _("Calculator"), 
                                  ("Open Calculator"), wx.ITEM_CHECK, 
                                  after=ed_glob.ID_PRE_MARK)

        if calc.CalcFrame.INSTANCE is not None:
            mitem.Check(calc.CalcFrame.INSTANCE.IsShown())

    def GetMenuHandlers(self):
        """Register the calculators menu event handler with the 
        top level window and the app.

        """
        return [(calc.ID_CALC, calc.ShowCalculator)]

    def GetUIHandlers(self):
        """No UpdateUI events are needed to be processed by this plugin
        so return an empty list.

        """
        return [(calc.ID_CALC, calc.UpdateMenu)]
