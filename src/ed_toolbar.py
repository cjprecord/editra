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
TOOL_ID = [ ed_glob.ID_NEW, ed_glob.ID_OPEN, ed_glob.ID_SAVE, ed_glob.ID_PRINT,
            ed_glob.ID_UNDO, ed_glob.ID_REDO, ed_glob.ID_COPY, ed_glob.ID_CUT,
            ed_glob.ID_PASTE, ed_glob.ID_FIND, ed_glob.ID_FIND_REPLACE ]

#--------------------------------------------------------------------------#

class EdToolBar(wx.ToolBar):
    """Toolbar wrapper class
    @todo: make it more dynamic/configurable

    """
    def __init__(self, parent):
        """Initializes the toolbar
        @param parent: parent window of this toolbar
        @param toolId: toolbar id

        """
        sstyle = wx.TB_HORIZONTAL | wx.NO_BORDER
        if wx.Platform == '__WXGTK__':
            sstyle = sstyle | wx.TB_DOCKABLE
        wx.ToolBar.__init__(self, parent, style=sstyle)

        # Attributes
        self._theme = Profile_Get('ICONS')
        self.SetToolBitmapSize(Profile_Get('ICON_SZ', 'size_tuple'))
        self._PopulateTools()

        self.Realize()

    #---- End Init ----#

    #---- Function Definitions----#
    def _PopulateTools(self):
        """Sets the tools in the toolbar
        @postcondition: all default tools are added to toolbar

        """
        # Place Icons in toolbar
        self.AddSimpleTool(ed_glob.ID_NEW, _("New"), _("Start a New File"))
        self.AddSimpleTool(ed_glob.ID_OPEN, _("Open"), _("Open"))
        self.AddSimpleTool(ed_glob.ID_SAVE, _("Save"), _("Save Current File"))
        self.AddSimpleTool(ed_glob.ID_PRINT, _("Print"), 
                           _("Print Current File"))
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_UNDO, _("Undo"), _("Undo Last Action"))
        self.AddSimpleTool(ed_glob.ID_REDO, _("Redo"), _("Redo Last Undo"))
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_COPY, _("Copy"), 
                           _("Copy Selected Text to Clipboard"))
        self.AddSimpleTool(ed_glob.ID_CUT, _("Cut"), 
                           _("Cut Selected Text from File"))
        self.AddSimpleTool(ed_glob.ID_PASTE, _("Paste"), 
                           _("Paste Text from Clipboard to File"))
        self.AddSeparator()
        self.AddSimpleTool(ed_glob.ID_FIND, _("Find"), _("Find Text"))
        self.AddSimpleTool(ed_glob.ID_FIND_REPLACE, _("Find/Replace"), 
                           _("Find and Replace Text"))
        self.AddSeparator()

    def AddSimpleTool(self, tool_id, lbl, helpstr):
        """Overides the default function to allow for easier tool
        generation/placement by automatically getting an appropriat icon from
        the art provider.
        @param tool_id: Id of tool to add
        @param lbl: tool lable
        @param helpstr: tool help string
        
        """
        tool_bmp = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
        wx.ToolBar.AddSimpleTool(self, tool_id, tool_bmp, _(lbl), _(helpstr))

    def GetToolTheme(self):
        """Returns the name of the current toolsets theme
        @return: name of icon theme used by this toolbar

        """
        return self._theme

    def ReInit(self):
        """Re-Initializes the tools in the toolbar
        @postcondtion: all tool icons are changed to match current theme

        """
        self._theme = Profile_Get('ICONS')
        self.SetToolBitmapSize(Profile_Get('ICON_SZ', 'size_tuple'))
        for tool_id in TOOL_ID:
            bmp = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
            self.SetToolNormalBitmap(tool_id, bmp)
                                     
