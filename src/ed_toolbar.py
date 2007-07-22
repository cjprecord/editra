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

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import ed_glob
from profiler import Profile_Get

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
          ed_glob.ID_PASTE :(_("Paste"), 
                             _("Paste Text from Clipboard to File")),
          ed_glob.ID_FIND : (_("Find"), _("Find Text")),
          ed_glob.ID_FIND_REPLACE : (_("Find/Replace"), 
                                     _("Find and Replace Text"))
        }
ID_TLBL  = 0
ID_THELP = 1

TOOL_ID = [ ed_glob.ID_NEW, ed_glob.ID_OPEN, ed_glob.ID_SAVE, ed_glob.ID_PRINT,
            ed_glob.ID_UNDO, ed_glob.ID_REDO, ed_glob.ID_COPY, ed_glob.ID_CUT,
            ed_glob.ID_PASTE, ed_glob.ID_FIND, ed_glob.ID_FIND_REPLACE ]

#--------------------------------------------------------------------------#

class EdToolBar(wx.ToolBar):
    """Toolbar wrapper class
    @todo: make it more dynamic/configurable

    """
    def __init__(self, parent, id_):
        """Initializes the toolbar
        @param parent: parent window of this toolbar
        @param toolId: toolbar id

        """
        sstyle = wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT
        if wx.Platform == '__WXGTK__':
            sstyle = sstyle | wx.TB_DOCKABLE
        wx.ToolBar.__init__(self, parent, id_, style = sstyle)

        # Attributes
        self._theme = Profile_Get('ICONS')
        self.tool_size = Profile_Get('ICON_SZ', 'size_tuple')
        self.SetToolBitmapSize(self.tool_size)
        self.PopulateTools()
        #-- Bind Events --#

        #-- End Bind Events --#
        self.Realize()

    #---- End Init ----#

    #---- Function Definitions----#
    def AddSimpleTool(self, tool_id):
        """Overides the default function to allow for easier tool
        generation/placement.
        @param toolId: Id of tool to add
        
        """
        tool_bmp = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
        lbl = TOOLS[tool_id][ID_TLBL]
        helpstr = TOOLS[tool_id][ID_THELP]
        wx.ToolBar.AddSimpleTool(self, tool_id, tool_bmp, _(lbl), _(helpstr))

    def GetToolSize(self):
        """Returns the size of the tools in the toolbar
        @return: size of tool icons in toolbar
        @rtype: tuple (w, h)
        """
        return self.tool_size

    def GetToolTheme(self):
        """Returns the name of the current toolsets theme
        @return: name of icon theme used by this toolbar

        """
        return self._theme

    def InsertSimpleTool(self, pos, tool_id):
        """Overides the default function to allow for easier tool
        generation/placement.
        @param pos: position to insert tool at
        @param tool_id: id of tool to add
        
        """
        tool_bmp = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
        lbl = TOOLS[tool_id][ID_TLBL]
        helpstr = TOOLS[tool_id][ID_THELP]
        wx.ToolBar.InsertSimpleTool(self, pos, tool_id, tool_bmp, \
                                    _(lbl), _(helpstr))

    def PopulateTools(self):
        """Sets the tools in the toolbar
        @postcondition: all default tools are added to toolbar

        """
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

    def ReInit(self):
        """Re-Initializes the tools in the toolbar
        @postcondtion: all tool icons are recreated
        @todo: flickers too much try to reduce if possible

        """
        # Remove Current Tools
        total = self.GetToolsCount()
        tools = list()
        pos = -1
        lastpos = 0
        wx.GetApp().ReloadArtProvider()
        self.tool_size = Profile_Get('ICON_SZ', 'size_tuple')
        self._theme = Profile_Get('ICONS')
        self.SetToolBitmapSize(self.tool_size)
        self.GetParent().Freeze()
        self.Freeze()
        for tool_id in TOOL_ID:
            pos = pos + 1
            if lastpos != self.GetToolPos(tool_id):
                pos = pos + 1
            lastpos = self.GetToolPos(tool_id)
            self.RemoveTool(tool_id)

            if pos > total:
                pos = pos - 1
            tools.append((tool_id, pos))

        for tool_id, pos in tools:
            self.InsertSimpleTool(pos, tool_id)
        self.Realize()
        self.GetParent().Thaw()
        self.Thaw()
