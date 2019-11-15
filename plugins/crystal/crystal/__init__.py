###############################################################################
# Name: __init__.py                                                           #
# Purpose: Provides the Crystal Project based icon theme for Editra           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <cprecord@editra.org>                      #
# License: wxWindows License                                                  #
###############################################################################
"""Crystal icon theme for Editra"""
__author__ = "Cody Precord"
__version__ = "0.2"

import wx
import os
import cStringIO
import ed_glob
import plugin
import ed_theme
import syntax.synglob as synglob
import syntax.syntax as syntax

#-----------------------------------------------------------------------------#

# Paths
MENU_PATH = os.path.join('pixmaps', 'menu') + os.sep
MIME_PATH = os.path.join('pixmaps', 'mime') + os.sep
TOOL_PATH = os.path.join('pixmaps', 'toolbar') + os.sep

#-----------------------------------------------------------------------------#

class CrystalTheme(plugin.Plugin):
    """Represents the Crystal Icon theme for Editra"""
    plugin.Implements(ed_theme.ThemeI)

    def __LoadBitmapData(self, path):
        """Loads image data into a bitmap, returns None if there is a failure"""
        try:
            data = __loader__.get_data(os.path.join(__path__[0], path))
        except IOError:
            pass
        else:
            bmp = wx.ImageFromStream(cStringIO.StringIO(data), wx.BITMAP_TYPE_PNG)
            return bmp.ConvertToBitmap()

    def GetName(self):
        return u'Crystal'

    def GetMenuBitmap(self, bmp_id):
        if bmp_id in ed_theme.ART:
            path = MENU_PATH + ed_theme.ART[bmp_id]
            bmp = self.__LoadBitmapData(path)
            if bmp is not None:
                return bmp
        else:
            return self.GetFileBitmap(bmp_id)

        return wx.NullBitmap

    def GetFileBitmap(self, bmp_id):
        bmp = None
        if bmp_id in ed_theme.MIME_ART:
            path = MIME_PATH + ed_theme.MIME_ART[bmp_id]
            bmp = self.__LoadBitmapData(path)
            if bmp is not None:
                return bmp
        
        if bmp is None and bmp_id in syntax.SyntaxIds():
            # Fail back to plain text bitmap
            bkup = MIME_PATH + ed_theme.MIME_ART[synglob.ID_LANG_TXT]
            bmp = self.__LoadBitmapData(bkup)
            if bmp is not None:
                return bmp

        return wx.NullBitmap

    def GetToolbarBitmap(self, bmp_id):
        if bmp_id in ed_theme.ART:
            path = TOOL_PATH + ed_theme.ART[bmp_id]
            bmp = self.__LoadBitmapData(path)
            if bmp is not None:
                return bmp

        return wx.NullBitmap
