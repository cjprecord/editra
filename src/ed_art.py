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
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    Provides and ArtProvider class for loading the custom images into the #
#   editor.                                                                #
#
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
import util

#--------------------------------------------------------------------------#
# Map object Id's to Custom Art Resources
ART = { ed_glob.ID_ABOUT  : u'about.png',
        ed_glob.ID_CONTACT : u'mail.png',
        ed_glob.ID_COPY   : u'copy.png',
        ed_glob.ID_CUT    : u'cut.png',
        ed_glob.ID_EXIT   : u'quit.png',
        ed_glob.ID_FIND   : u'find.png',
        ed_glob.ID_FIND_REPLACE : u'findr.png',
        ed_glob.ID_FONT   : u'font.png',
        ed_glob.ID_HOMEPAGE : u'web.png',
        ed_glob.ID_NEW    : u'new.png',
        ed_glob.ID_NEXT_MARK : u'bmark_next.png',
        ed_glob.ID_OPEN   : u'open.png',
        ed_glob.ID_PASTE  : u'paste.png',
        ed_glob.ID_PRE_MARK : u'bmark_pre.png',
        ed_glob.ID_PREF   : u'pref.png',
        ed_glob.ID_PRINT  : u'print.png',
        ed_glob.ID_PRINT_PRE : u'printpre.png',
        ed_glob.ID_REDO   : u'redo.png',
        ed_glob.ID_SAVE   : u'save.png',
        ed_glob.ID_SAVEAS : u'saveas.png',
        ed_glob.ID_UNDO   : u'undo.png',
        ed_glob.ID_ZOOM_IN : u'zoomi.png',
        ed_glob.ID_ZOOM_OUT : u'zoomo.png',
        ed_glob.ID_ZOOM_NORMAL : u'zoomd.png'
}

# Map for default system/wx provided graphic resources.
DEFAULT = { 
            ed_glob.ID_COPY    : wx.ART_COPY,
            ed_glob.ID_CUT     : wx.ART_CUT,
            ed_glob.ID_EXIT    : wx.ART_QUIT,
            ed_glob.ID_FIND    : wx.ART_FIND,
            ed_glob.ID_FIND_REPLACE : wx.ART_FIND_AND_REPLACE,
            ed_glob.ID_NEW     : wx.ART_NEW,
            ed_glob.ID_NEXT_MARK : wx.ART_GO_FORWARD,
            ed_glob.ID_OPEN    : wx.ART_FILE_OPEN,
            ed_glob.ID_PASTE   : wx.ART_PASTE,
            ed_glob.ID_PRE_MARK : wx.ART_GO_BACK,
            ed_glob.ID_PRINT   : wx.ART_PRINT,
            ed_glob.ID_REDO    : wx.ART_REDO,
            ed_glob.ID_SAVE    : wx.ART_FILE_SAVE,
            ed_glob.ID_SAVEAS  : wx.ART_FILE_SAVE_AS,
            ed_glob.ID_UNDO    : wx.ART_UNDO
}

# Client Id Map
CLIENTS = { wx.ART_MENU    : u'menu',       # $theme/menu
            wx.ART_TOOLBAR : u'toolbar',    # $theme/toolbar
            wx.ART_OTHER   : u''            # $pixmaps/
          }

#--------------------------------------------------------------------------#

class ED_Art(wx.ArtProvider):
    """Editras Art Provider. Provides the mimetype images and
    loads any custom user defined icon sets as well.

    """
    def __init__(self):
        """Initializes the art provider"""
        wx.ArtProvider.__init__(self)

    # XXX Why when making a call to the ArtProvider and supplying a size why
    #     does it degrade the image quality so much. If no size is supplied
    #     and the image is scaled it looks fine, but if a size is supplied and
    #     the image is not scaled it will still look poor.
    def CreateBitmap(self, id, client, size):
        """Makes the bitmaps from the images"""
        # All art ids we can handle can be converted to int
        try:
            id = int(id)
        except ValueError:
            return wx.NullBitmap

        # If using default theme let the system provide the art when possible
        if ed_glob.PROFILE['ICONS'].lower() == u'default' and DEFAULT.has_key(int(id)):
            return wx.ArtProvider.GetBitmap(DEFAULT[int(id)], client, size)
        if CLIENTS.has_key(client) and ART.has_key(int(id)):
            resource_path = self.GetArtPath(client)
            art_src = resource_path + ART[int(id)]
            if os.path.exists(art_src):
                img = wx.Image(art_src, wx.BITMAP_TYPE_PNG)
            else:
                return wx.NullBitmap

            img_sz = img.GetSize()
            if client == wx.ART_MENU:
                size = wx.Size(16, 16) # Menu icons must be 16x16
            elif client == wx.ART_TOOLBAR:
                size = ed_glob.PROFILE['ICON_SZ']

            # Rescale image to specified size if need be but dont allow upscaling
            # as it reduces quality.
            if client == wx.ART_TOOLBAR and wx.Platform == '__WXMAC__':
                # Dont worry about scaling on MAC it is done by the
                # toolbar automagically.
                pass
            elif size[0] < img_sz[0]:
                img.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)
            else:
                pass
            bmp = wx.BitmapFromImage(img)
            if bmp.IsOk():
                return bmp
            else:
                return wx.NullBitmap
        else:
            return wx.NullBitmap

    def GetArtPath(self, client):
        """Gets the path of the resource directory to get
        the bitmaps from.

        """
        if ed_glob.CONFIG['THEME_DIR'] == u'':
            ed_glob.CONFIG['THEME_DIR'] = util.ResolvConfigDir(os.path.join("pixmaps", "theme"))

        if not CLIENTS.has_key(client):
            return wx.EmptyString

        # ART_OTHER is used for dialogs and other base icon that are
        # not meant to be themeable by the user.
        if client == wx.ART_OTHER:
            path = ed_glob.CONFIG['SYSPIX_DIR']
        else:
            path = ed_glob.CONFIG['THEME_DIR'] + util.GetPathChar() + \
                   ed_glob.PROFILE['ICONS'] + util.GetPathChar() + \
                   CLIENTS[client] + util.GetPathChar()

        if os.path.exists(path):
            return path
        else:
            return wx.EmptyString


