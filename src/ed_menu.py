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

"""
#--------------------------------------------------------------------------#
# FILE: ed_menu.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#   Provides a more convenient menu class for the editor.                  #
#                                                                          #
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
import ed_glob

#--------------------------------------------------------------------------#

class ED_Menu(wx.Menu):
    """Overides the default wxMenu class to make it easier to
    customize and access items.

    """
    def __init__(self, title=wx.EmptyString, style=0):
        """Initialize a Menu Object"""
        wx.Menu.__init__(self, title, style)

    def Append(self, id, text=u'', help=u'', kind=wx.ITEM_NORMAL, bmp_path=None):
        """Append a MenuItem"""
        item = wx.Menu.Append(self, id, text, help, kind)
        if bmp_path != None and os.path.exists(bmp_path):
            try:
                bmp = wx.Bitmap(bmp_path, wx.BITMAP_TYPE_PNG)
                item.SetBitmap(bmp)
            finally:
                pass
        return item

