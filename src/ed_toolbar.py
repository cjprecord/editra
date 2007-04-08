############################################################################
#  Copyright (C) 2007 Cody Precord                                         #
#  cprecord@editra.org                                                     #
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
# FILE: ed_toolbar.py                                                      #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
#   This module creates and manages the customization of the toolbar       #
#                                                                          #
# METHODS:                                                                 #
# - __init__ : Creates the toolbar object                                  #
# - CreateIcons : Creates the icons to use in the toolbar                  #
# - LoadIconSet : Loads the icons from the theme handler                   #
# - PopulateTools : Puts tools in the toolbar                              #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id Exp $"

#--------------------------------------------------------------------------#
# Dependancies

import wx
import glob
import ed_glob
import ed_search
import util

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
# Global Variables
ICON_SET = {}
TOOL_SET = {}

#--------------------------------------------------------------------------#

class ED_ToolBar(wx.ToolBar):
    """Toolbar wrapper class"""
    def __init__(self, parent, tb_id, icon_size=0, style=0):
        """Initializes the toolbar"""
        self.platform = wx.Platform
        if self.platform == '__WXMSW__':
            wx.ToolBar.__init__(self, parent, tb_id, style=wx.TB_HORIZONTAL |
                                wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        elif self.platform == '__WXGTK__':
            wx.ToolBar.__init__(self, parent, tb_id, style=wx.TB_HORIZONTAL | 
                                wx.NO_BORDER  | wx.TB_FLAT | 
                                wx.TB_DOCKABLE | wx.TB_TEXT)
        else:
            wx.ToolBar.__init__(self, parent, tb_id,
                                style=wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        self.tool_loc = ed_glob.CONFIG['THEME_DIR'] + util.GetPathChar() + \
                        ed_glob.PROFILE['ICONS'] + util.GetPathChar() + u"toolbar" + \
                        util.GetPathChar()
        self.tool_size = self.GetToolSize()
        self.SetToolBitmapSize(self.tool_size)
        self.CreateDefaultIcons(self.tool_size)
        self.PopulateTools()

        #-- Bind Events --#

        #-- End Bind Events --#
        self.Realize()

    #---- End Init ----#

    #---- Function Definitions----#

    def GetToolSize(self):
        """Gets the size of the icons to be used in the toolbar and
        returns that size as a wxSize object.

        """
        icons = glob.glob(self.tool_loc + "*.png")
        if len(icons) < 1:
            return wx.Size(16, 16)
        else:
            icon =  wx.Bitmap(icons[0], wx.BITMAP_TYPE_PNG)
            i_size = icon.GetSize()
            if ed_glob.PROFILE['ICON_SZ'][0] < i_size[0]:
                i_size = ed_glob.PROFILE['ICON_SZ']
            return i_size

    #TODO this is just a quick hack to make things work for now
    def CreateDefaultIcons(self, tool_size):
        """Creates the Icons to be used in the toolbar"""
        if wx.Platform in ['__WXMAC__', '__WXMSW__'] or ed_glob.PROFILE['ICONS'].lower() != u"stock":
            # TODO check this path to see if it is valid before trying to use it
            stock_dir = self.tool_loc

            TOOL_SET["new"]   = wx.Image(stock_dir + "new.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["open"]  = wx.Image(stock_dir + "open.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["save"]  = wx.Image(stock_dir + "save.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["print"] = wx.Image(stock_dir + "print.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["undo"]  = wx.Image(stock_dir + "undo.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["redo"]  = wx.Image(stock_dir + "redo.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["copy"]  = wx.Image(stock_dir + "copy.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["cut"]   = wx.Image(stock_dir + "cut.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["paste"] = wx.Image(stock_dir + "paste.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["find"]  = wx.Image(stock_dir + "find.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["findr"] = wx.Image(stock_dir + "findr.png", wx.BITMAP_TYPE_PNG)
            if TOOL_SET["new"].GetSize()[0] != ed_glob.PROFILE['ICON_SZ'][0] and \
               wx.Platform != '__WXMAC__':
                for tool in TOOL_SET:
                    TOOL_SET[tool].Rescale(tool_size[0], tool_size[1])
            for tool in TOOL_SET:
                TOOL_SET[tool] = wx.BitmapFromImage(TOOL_SET[tool])
        else:
            TOOL_SET["new"]   = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["open"]  = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["save"]  = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["print"] = wx.ArtProvider.GetBitmap(wx.ART_PRINT, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["undo"]  = wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["redo"]  = wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["copy"]  = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["cut"]   = wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["paste"] = wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["find"]  = wx.ArtProvider.GetBitmap(wx.ART_FIND, wx.ART_TOOLBAR, tool_size)
            TOOL_SET["findr"] = wx.ArtProvider.GetBitmap(wx.ART_FIND_AND_REPLACE, wx.ART_TOOLBAR, tool_size)

    def LoadIconSet(self):
        """Loads the Icon set from the theme handler.
        If no custom icon set is defined it simply loads
        the system default icon set.

        """
        # Theme handler not implimented yet


    def PopulateTools(self):
        """Sets the tools in the toolbar"""
        # Place Icons in toolbar
        self.AddSimpleTool(ed_glob.ID_NEW, TOOL_SET["new"], _("New"), _("Start a New File"))
        self.AddSimpleTool(ed_glob.ID_OPEN, TOOL_SET["open"], _("Open"), _("Open"))
        self.AddSimpleTool(ed_glob.ID_SAVE, TOOL_SET["save"], _("Save"), 
                           _("Save Current File"))
        self.AddSimpleTool(ed_glob.ID_PRINT, TOOL_SET["print"], _("Print"), 
                           _("Print Current File"))
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_UNDO, TOOL_SET["undo"], _("Undo"), _("Undo Last Action"))
        self.AddSimpleTool(ed_glob.ID_REDO, TOOL_SET["redo"], _("Redo"), _("Redo Last Undo"))
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_COPY, TOOL_SET["copy"], _("Copy"), 
                          _("Copy Selected Text to Clipboard"))
        self.AddSimpleTool(ed_glob.ID_CUT, TOOL_SET["cut"], _("Cut"), 
                          _("Cut Selected Text from File"))
        self.AddSimpleTool(ed_glob.ID_PASTE, TOOL_SET["paste"], _("Paste"), 
                          _("Paste Text from Clipboard to File"))
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_FIND, TOOL_SET["find"], _("Find"), _("Find Text"))
        self.AddSimpleTool(ed_glob.ID_FIND_REPLACE, TOOL_SET["findr"], _("Find/Replace"), 
                           _("Find and Replace Text"))
        self.AddSeparator()

	
