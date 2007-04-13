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
import os
import wx
import glob
import ed_glob
import ed_search
import util

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
# Global Variables
#             ID         | TOOL_LABLE | TOOL HELP STRING
TOOLS = { ed_glob.ID_NEW :  (_("New"), _("Start a New File")),
          ed_glob.ID_OPEN : (_("Open"), _("Open")),
          ed_glob.ID_SAVE : (_("Save"), _("Save Current File")),
          ed_glob.ID_PRINT :(_("Print"), _("Print Current File")),
          ed_glob.ID_UNDO : (_("Undo"), _("Undo Last Action")),
          ed_glob.ID_REDO : (_("Redo"), _("Redo Last Undo")),
          ed_glob.ID_COPY : (_("Copy"), _("Copy Selected Text to Clipboard")),
          ed_glob.ID_CUT :  (_("Cut"), _("Cut Selected Text from File")),
          ed_glob.ID_PASTE :(_("Paste"), _("Paste Text from Clipboard to File")),
          ed_glob.ID_FIND : (_("Find"), _("Find Text")),
          ed_glob.ID_FIND_REPLACE : (_("Find/Replace"), _("Find and Replace Text"))
        }
ID_TLBL  = 0
ID_THELP = 1

TOOL_ID = [ ed_glob.ID_NEW, ed_glob.ID_OPEN, ed_glob.ID_SAVE, ed_glob.ID_PRINT,
            ed_glob.ID_UNDO, ed_glob.ID_REDO, ed_glob.ID_COPY, ed_glob.ID_CUT,
            ed_glob.ID_PASTE, ed_glob.ID_FIND, ed_glob.ID_FIND_REPLACE ]

#--------------------------------------------------------------------------#

class ED_ToolBar(wx.ToolBar):
    """Toolbar wrapper class"""
    def __init__(self, parent, tb_id, icon_size=0, style=0):
        """Initializes the toolbar"""
        sstyle = wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT
        if wx.Platform == '__WXMSW__':
            sstyle = sstyle | wx.TB_TEXT
        elif wx.Platform == '__WXGTK__':
            sstyle = sstyle | wx.TB_TEXT | wx.TB_DOCKABLE
        wx.ToolBar.__init__(self, parent, tb_id, style=sstyle)

        # Attributes
        self._theme = ed_glob.PROFILE['ICONS']
        self.tool_size = ed_glob.PROFILE['ICON_SZ']
        self.SetToolBitmapSize(self.tool_size)
        self.PopulateTools()
        #-- Bind Events --#

        #-- End Bind Events --#
        self.Realize()

    #---- End Init ----#

    #---- Function Definitions----#
    def AddSimpleTool(self, id):
        """Overides the default function to allow for easier tool
        generation/placement.
        
        """
        tool_bmp = wx.ArtProvider.GetBitmap(str(id), wx.ART_TOOLBAR)
        lbl = TOOLS[id][ID_TLBL]
        help = TOOLS[id][ID_THELP]
        wx.ToolBar.AddSimpleTool(self, id, tool_bmp, _(lbl), _(help))

    def GetToolSize(self):
        """Returns the size of the tools in the toolbar"""
        return self.tool_size

    def GetToolTheme(self):
        """Returns the name of the current toolsets theme"""
        return self._theme

    def InsertSimpleTool(self, pos, id):
        """Overides the default function to allow for easier tool
        generation/placement.
        
        """
        tool_bmp = wx.ArtProvider.GetBitmap(str(id), wx.ART_TOOLBAR)
        lbl = TOOLS[id][ID_TLBL]
        help = TOOLS[id][ID_THELP]
        wx.ToolBar.InsertSimpleTool(self, pos, id, tool_bmp, _(lbl), _(help))

    def PopulateTools(self):
        """Sets the tools in the toolbar"""
        # Place Icons in toolbar
        self.AddSimpleTool(ed_glob.ID_NEW)
        self.AddSimpleTool(ed_glob.ID_OPEN)
        self.AddSimpleTool(ed_glob.ID_SAVE)
        self.AddSimpleTool(ed_glob.ID_PRINT)
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_UNDO)
        self.AddSimpleTool(ed_glob.ID_REDO)
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_COPY)
        self.AddSimpleTool(ed_glob.ID_CUT)
        self.AddSimpleTool(ed_glob.ID_PASTE)
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_FIND)
        self.AddSimpleTool(ed_glob.ID_FIND_REPLACE)
        self.AddSeparator()

    # TODO Flickers too much, try and find a way to reduce it if possible
    def ReInit(self):
        """Re-Initializes the tools in the toolbar"""
        # Remove Current Tools
        total = self.GetToolsCount()
        tools = list()
        pos = -1
        lastpos = 0
        wx.GetApp().ReloadArtProvider()
        self.tool_size = ed_glob.PROFILE['ICON_SZ']
        self._theme = ed_glob.PROFILE['ICONS']
        self.SetToolBitmapSize(self.tool_size)
        self.GetParent().Freeze()
        self.Freeze()
        for id in TOOL_ID:
            pos = pos + 1
            try:
                if lastpos != self.GetToolPos(id):
                    pos = pos + 1
                lastpos = self.GetToolPos(id)
                self.RemoveTool(id)
            except:
                pass
            else:
                if pos > total:
                    pos = pos - 1
                tools.append((id, pos))

        for id, pos in tools:
            self.InsertSimpleTool(pos, id)
        self.Realize()
        self.GetParent().Thaw()
        self.Thaw()
