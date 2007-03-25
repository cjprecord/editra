############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_statbar
# AUTHOR: Cody Precord
# LANGUAGE: Python	
# SUMMARY:
#     Provides a statusbar class for the editor that can contain controls
#  as well as the usual status information.
#
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies
import wx

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class ED_StatusBar(wx.StatusBar):
    """Custom StatusBar"""
    def __init__(self, parent):
        """Creates the StatusBar"""
        wx.StatusBar.__init__(self, parent, -1, style=wx.BOTTOM)

        self.sizeChanged = False
        self.SetFieldsCount(1)
        #self.SetStatusWidths([-2, -1, -2])

        #self.SetStatusText(_("Welcome to Editra"), 0)
        self.search = wx.SearchCtrl(self, wx.ID_ANY, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.Reposition()

        # Bind Events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

    def OnSize(self, evt):
        self.Reposition()  # for normal size events
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    def Reposition(self):
        rect = self.GetFieldRect(0)
        self.search.SetPosition((rect.x+2, rect.y+2))
        self.search.SetSize((rect.width-4, rect.height-4))
        self.sizeChanged = False
