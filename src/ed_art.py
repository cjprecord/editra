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
import util
import syntax.synglob as synglob
from edimage import catalog

#--------------------------------------------------------------------------#
# Map object Id's to custom user definable art resources
ART = { ed_glob.ID_ABOUT  : u'about.png',
        ed_glob.ID_ADD_BM : u'bmark_add.png',
        ed_glob.ID_BIN_FILE : u'bin_file.png',
        ed_glob.ID_CDROM  : u'cdrom.png',
        ed_glob.ID_CONTACT : u'mail.png',
        ed_glob.ID_COPY   : u'copy.png',
        ed_glob.ID_COMPUTER : u'computer.png',
        ed_glob.ID_CUT    : u'cut.png',
        ed_glob.ID_DELETE : u'delete.png',
        ed_glob.ID_DOCPROP : u'doc_props.png',
        ed_glob.ID_DOWN   : u'down.png',
        ed_glob.ID_EXIT   : u'quit.png',
        ed_glob.ID_FILE   : u'file.png',
        ed_glob.ID_FIND   : u'find.png',
        ed_glob.ID_FIND_REPLACE : u'findr.png',
        ed_glob.ID_FLOPPY : u'floppy.png',
        ed_glob.ID_FOLDER : u'folder.png',
        ed_glob.ID_FONT   : u'font.png',
        ed_glob.ID_HARDDISK : u'harddisk.png',
        ed_glob.ID_HOMEPAGE : u'web.png',
        ed_glob.ID_HTML_GEN : u'html_gen.png',
        ed_glob.ID_KWHELPER : u'kw_help.png',
        ed_glob.ID_NEW    : u'new.png',
        ed_glob.ID_NEW_WINDOW: u'newwin.png',
        ed_glob.ID_NEXT_MARK : u'bmark_next.png',
        ed_glob.ID_OPEN    : u'open.png',
        ed_glob.ID_PACKAGE : u'package.png',
        ed_glob.ID_PASTE   : u'paste.png',
        ed_glob.ID_PLUGMGR : u'plugin.png',
        ed_glob.ID_PRE_MARK : u'bmark_pre.png',
        ed_glob.ID_PREF    : u'pref.png',
        ed_glob.ID_PRINT   : u'print.png',
        ed_glob.ID_PRINT_PRE : u'printpre.png',
        ed_glob.ID_REDO    : u'redo.png',
        ed_glob.ID_RTF_GEN : u'rtf_gen.png',
        ed_glob.ID_SAVE    : u'save.png',
        ed_glob.ID_SAVEAS  : u'saveas.png',
        ed_glob.ID_STYLE_EDIT : u'style_edit.png',
        ed_glob.ID_TEX_GEN : u'tex_gen.png',
        ed_glob.ID_THEME  : u'theme.png',
        ed_glob.ID_UNDO   : u'undo.png',
        ed_glob.ID_UP     : u'up.png',
        ed_glob.ID_USB    : u'usb.png',
        ed_glob.ID_WEB    : u'web.png',
        ed_glob.ID_ZOOM_IN : u'zoomi.png',
        ed_glob.ID_ZOOM_OUT : u'zoomo.png',
        ed_glob.ID_ZOOM_NORMAL : u'zoomd.png'
}

# File Type Art
MIME_ART = { synglob.ID_LANG_BASH : u'shell.png',
             synglob.ID_LANG_BOURNE : u'shell.png',
             synglob.ID_LANG_C : u'c.png',
             synglob.ID_LANG_CPP : u'cpp.png',
             synglob.ID_LANG_CSH : u'shell.png',
             synglob.ID_LANG_CSS : u'css.png',
             synglob.ID_LANG_HTML : u'html.png',
             synglob.ID_LANG_JAVA : u'java.png',
             synglob.ID_LANG_KSH : u'shell.png',
             synglob.ID_LANG_LATEX : u'tex.png',
             synglob.ID_LANG_MAKE : u'makefile.png',
             synglob.ID_LANG_PERL : u'perl.png',
             synglob.ID_LANG_PHP : u'php.png',
             synglob.ID_LANG_PYTHON : u'python.png',
             synglob.ID_LANG_RUBY : u'ruby.png',
             synglob.ID_LANG_TCL : u'tcl.png',
             synglob.ID_LANG_TEX : u'tex.png',
             synglob.ID_LANG_TXT : u'text.png'
 }
 
# Map of non user definable art resources
OTHER_ART = { ed_glob.ID_APP_SPLASH : catalog['splashwarn'] }

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

# Client Id Map
CLIENTS = { wx.ART_MENU    : u'menu',       # $theme/menu
            wx.ART_TOOLBAR : u'toolbar',    # $theme/toolbar
            wx.ART_OTHER   : u''            # $pixmaps/
          }

#--------------------------------------------------------------------------#

class EditraArt(wx.ArtProvider):
    """Editras Art Provider. Provides the mimetype images and
    loads any custom user defined icon sets as well.

    """
    def __init__(self):
        """Initializes the art provider"""
        wx.ArtProvider.__init__(self)

    # ??? Why when making a call to the ArtProvider and supplying a size
    #     does it degrade the image quality so much. If no size is supplied
    #     and the image is scaled it looks fine, but if a size is supplied and
    #     the image is not scaled it will still look poor.
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
            return wx.ArtProvider.GetBitmap(DEFAULT[art_id], client, size)
        if CLIENTS.has_key(client) and \
           (ART.has_key(art_id) or \
            OTHER_ART.has_key(art_id) or \
            MIME_ART.has_key(art_id)):
            resource_path = GetArtPath(client)
            if client == wx.ART_OTHER:
                return OTHER_ART[art_id].getBitmap()
            else:
                if ART.has_key(art_id):
                    art_src = resource_path + ART[art_id]
                else:
                    mime_path = GetArtPath(client, mime=True)
                    art_src = mime_path + MIME_ART[art_id]

            if os.path.exists(art_src):
                img = wx.Image(art_src, wx.BITMAP_TYPE_PNG)
                img_sz = img.GetSize()
            else:
                return wx.NullBitmap

            # Assume ART_MENU by default since its most common
            size = wx.Size(16, 16) # Menu icons must be 16x16
            if client == wx.ART_TOOLBAR:
                size = Profile_Get('ICON_SZ', 'size_tuple')

            # Rescale image to specified size if need be but dont allow
            # upscaling as it reduces quality.
            if client != wx.ART_OTHER and size[0] < img_sz[0] and not \
               (client == wx.ART_TOOLBAR and wx.Platform == '__WXMAC__'):
                img.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)

            bmp = wx.BitmapFromImage(img)
            if bmp.IsOk() and not bmp.IsNull():
                return bmp
        # All failed so return a Null
        return wx.NullBitmap

#-----------------------------------------------------------------------------#
def GetArtPath(client, mime = False):
    """Gets the path of the resource directory to get
    the bitmaps from.
    @return: path of art resource
    @rtype: string

    """
    if ed_glob.CONFIG['THEME_DIR'] == u'':
        theme = util.ResolvConfigDir(os.path.join("pixmaps", "theme"))
        ed_glob.CONFIG['THEME_DIR'] = theme

    if not CLIENTS.has_key(client):
        return wx.EmptyString

    # ART_OTHER is used for dialogs and other base icon that are
    # not meant to be themeable by the user.
    if client == wx.ART_OTHER:
        path = ed_glob.CONFIG['SYSPIX_DIR']
    else:
        if mime:
            path = ed_glob.CONFIG['SYSPIX_DIR'] + util.GetPathChar() + \
                   u'mime' + util.GetPathChar()
        else:
            path = ed_glob.CONFIG['THEME_DIR'] + util.GetPathChar() + \
                   Profile_Get('ICONS') + util.GetPathChar() + \
                   CLIENTS[client] + util.GetPathChar()

    if os.path.exists(path):
        return path
    else:
        return wx.EmptyString
