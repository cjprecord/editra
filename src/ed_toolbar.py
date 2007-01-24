############################################################################
#  Copyright (C) 2007 Cody Precord                                         #
#  cprecord@editra.org                                                     #
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
import ed_glob
import util

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
# Global Variables
ICON_SET = {}
TOOL_SET = {}

#--------------------------------------------------------------------------#

class ED_ToolBar(wx.ToolBar):
    """Toolbar wrapper class"""
    def __init__(self, parent, tb_id, icon_size, style=0):
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
            #icon_size = 32 #TODO Mac icons are suggested to be 32x32 with the native toolbar
            wx.ToolBar.__init__(self, parent, tb_id, size=(icon_size,-1), 
                                style=wx.TB_FLAT | wx.TB_NODIVIDER | wx.NO_BORDER)
        self.tool_size = wx.Size(icon_size, icon_size)
        self.SetToolBitmapSize(self.tool_size)
        self.CreateDefaultIcons(self.tool_size)
        self.PopulateTools()

	#-- Bind Events --#

        #-- End Bind Events --#
        self.Realize()

    #---- End Init ----#

    #---- Function Definitions----#

    #TODO this is just a quick hack to make things work for now
    def CreateDefaultIcons(self, tool_size):
        """Creates the Icons to be used in the toolbar"""
        stock_dir = (ed_glob.CONFIG['PIXMAPS_DIR'] + u"toolbar" + util.GetPathChar() +
                     ed_glob.PROFILE['ICONS'] + util.GetPathChar())
        # wx 2.8 uses a native mac toolbar and the builtin wx icons look like complete
        # garbage in it so provide some custom pixmaps instead.
        if wx.Platform == '__WXMAC__' or ed_glob['ICONS'].lower() != u"stock":
            TOOL_SET["new"]   = wx.Bitmap(stock_dir + "new.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["open"]  = wx.Bitmap(stock_dir + "open.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["save"]  = wx.Bitmap(stock_dir + "save.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["print"] = wx.Bitmap(stock_dir + "print.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["undo"]  = wx.Bitmap(stock_dir + "undo.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["redo"]  = wx.Bitmap(stock_dir + "redo.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["copy"]  = wx.Bitmap(stock_dir + "copy.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["cut"]   = wx.Bitmap(stock_dir + "cut.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["paste"] = wx.Bitmap(stock_dir + "paste.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["find"]  = wx.Bitmap(stock_dir + "find.png", wx.BITMAP_TYPE_PNG)
            TOOL_SET["findr"] = wx.Bitmap(stock_dir + "findr.png", wx.BITMAP_TYPE_PNG)
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
        self.AddSimpleTool(ed_glob.ID_FIND_REPLACE, TOOL_SET["findr"], _("FReplace"), 
                           _("Find and Replace Text"))
        self.AddSeparator()

    #---- Event Handlers ----#
#    def OnEnableTools(self, evt):
#        """Enables and disables tools based on their availability"""
	
