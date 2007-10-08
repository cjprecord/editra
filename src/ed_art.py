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
# FILE: ed_art.py                                                          #
# @author: Cody Precord                                                    #
# LANGUAGE: Python                                                         #
# @summary:                                                                #
#    Provides and ArtProvider class for loading the custom images into the #
#   editor.                                                                #
#                                                                          #
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
import ed_glob
from profiler import Profile_Get
import syntax.syntax as syntax
import ed_theme

#--------------------------------------------------------------------------#

# Map for default system/wx provided graphic resources.
DEFAULT = { 
            ed_glob.ID_ADD_BM  : wx.ART_ADD_BOOKMARK,
            ed_glob.ID_BIN_FILE : wx.ART_EXECUTABLE_FILE,
            ed_glob.ID_CDROM   : wx.ART_CDROM,
            ed_glob.ID_COPY    : wx.ART_COPY,
            ed_glob.ID_CUT     : wx.ART_CUT,
            ed_glob.ID_DELETE  : wx.ART_DELETE,
            ed_glob.ID_DEL_BM  : wx.ART_DEL_BOOKMARK,
            ed_glob.ID_DOCPROP : wx.ART_NORMAL_FILE,        # Bad match
            ed_glob.ID_DOWN    : wx.ART_GO_DOWN,
            ed_glob.ID_EXIT    : wx.ART_QUIT,
            ed_glob.ID_FILE    : wx.ART_NORMAL_FILE,
            ed_glob.ID_FIND    : wx.ART_FIND,
            ed_glob.ID_FIND_REPLACE : wx.ART_FIND_AND_REPLACE,
            ed_glob.ID_FLOPPY  : wx.ART_FLOPPY,
            ed_glob.ID_FOLDER  : wx.ART_FOLDER,
            ed_glob.ID_HARDDISK : wx.ART_HARDDISK,
            ed_glob.ID_NEW     : wx.ART_NEW,
            ed_glob.ID_NEXT_MARK : wx.ART_GO_FORWARD,
            ed_glob.ID_OPEN    : wx.ART_FILE_OPEN,
            ed_glob.ID_PACKAGE : wx.ART_HARDDISK,           # Poor match
            ed_glob.ID_PASTE   : wx.ART_PASTE,
            ed_glob.ID_PREF    : wx.ART_EXECUTABLE_FILE,    # Bad match
            ed_glob.ID_PRE_MARK : wx.ART_GO_BACK,
            ed_glob.ID_PRINT   : wx.ART_PRINT,
            ed_glob.ID_REDO    : wx.ART_REDO,
            ed_glob.ID_SAVE    : wx.ART_FILE_SAVE,
            ed_glob.ID_SAVEAS  : wx.ART_FILE_SAVE_AS,
            ed_glob.ID_THEME   : wx.ART_INFORMATION,   # Bad match
            ed_glob.ID_UNDO    : wx.ART_UNDO,
            ed_glob.ID_UP      : wx.ART_GO_UP,
            ed_glob.ID_USB     : wx.ART_REMOVABLE,
            ed_glob.ID_WEB     : wx.ART_HARDDISK       # Bad match
}

#--------------------------------------------------------------------------#

class EditraArt(wx.ArtProvider):
    """Editras Art Provider. Provides the mimetype images and
    loads any custom user defined icon sets as well.

    """
    def __init__(self):
        """Initializes the art provider"""
        wx.ArtProvider.__init__(self)
        self._library = ed_theme.BitmapProvider(wx.GetApp().GetPluginManager())

    def CreateBitmap(self, art_id, client, size):
        """Makes the bitmaps from the images
        @return: Requested image object if one exists
        @rtype: wx.Bitmap

        """
        # All art ids we can handle can be converted to int
        try:
            art_id = int(art_id)
        except ValueError:
            return wx.NullBitmap

        # If using default theme let the system provide the art when possible
        if Profile_Get('ICONS', 'str').lower() == u'default' and \
           DEFAULT.has_key(art_id):
            if client == wx.ART_MENU:
                size = (16, 16)
            elif client == wx.ART_TOOLBAR:
                size = Profile_Get('ICON_SZ', default=(24, 24))
            return wx.ArtProvider.GetBitmap(DEFAULT[art_id], client, size)

        # If a custom theme is set fetch the requested bitmap
        bmp = self._library.GetBitmap(art_id, client)
        if not bmp.IsNull() and bmp.IsOk():
            if client == wx.ART_TOOLBAR and not wx.Platform == '__WXMAC__':
                if size == wx.DefaultSize:
                    size = Profile_Get('ICON_SZ', 'size_tuple')
                img = wx.ImageFromBitmap(bmp)
                img_sz = img.GetSize()
                if size[0] < img_sz[0]:
                    img.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
                bmp = wx.BitmapFromImage(img)
            elif client == wx.ART_MENU and bmp.GetSize() != (16, 16):
                img = wx.ImageFromBitmap(bmp)
                img.Rescale(16, 16, wx.IMAGE_QUALITY_HIGH)
                bmp = wx.BitmapFromImage(img)
        elif client == wx.ART_TOOLBAR:
            bmp = wx.ArtProvider.GetBitmap(wx.ART_WARNING, client, size)
        elif art_id in syntax.SyntaxIds():
            bmp = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, 
                                           wx.ART_MENU, (16, 16))

        if bmp.IsOk() and not bmp.IsNull():
            return bmp

        # All failed so return a Null
        return wx.NullBitmap

#-----------------------------------------------------------------------------#
