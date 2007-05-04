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
# Globals
_ = wx.GetTranslation

#--------------------------------------------------------------------------#

class ED_Menu(wx.Menu):
    """Overides the default wxMenu class to make it easier to
    customize and access items.

    """
    def __init__(self, title=wx.EmptyString, style=0):
        """Initialize a Menu Object"""
        wx.Menu.__init__(self, title, style)

    def Append(self, id, text=u'', help=u'', kind=wx.ITEM_NORMAL, use_bmp=True):
        """Append a MenuItem"""
        item = wx.Menu.Append(self, id, text, help, kind)
        if use_bmp:
            try:
                bmp = wx.ArtProvider.GetBitmap(str(id), wx.ART_MENU)
                item.SetBitmap(bmp)
            finally:
                pass
        return item

class ED_MenuBar(wx.MenuBar):
    """Custom menubar to allow for easier access and updating
    of menu components.
    
    """
    def __init__(self, style=0):
        """Initializes the Menubar"""
        wx.MenuBar.__init__(self, style)
        self._filehistorymenu = ED_Menu()
        self._filemenu = self.GenFileMenu()
        self._lineformatmenu = ED_Menu()
        self._editmenu = self.GenEditMenu()
        self._viewmenu = self.GenViewMenu()
        self._formatmenu = self.GenFormatMenu()
        self._settingsmenu = self.GenSettingsMenu()
        self._toolsmenu = self.GenToolsMenu()
        self._helpmenu = self.GenHelpMenu()

    # TODO these Gen functions should be broken up to the components
    #      that supply the functionality and inserted in the menus on
    #      init when the editor loads an associated widget. But this
    #      is the first step to get there.
    def GenFileMenu(self):
        """Makes and attaches the file menu"""
        filemenu = ED_Menu()
        filehist = self._filehistorymenu
        filemenu.Append(ed_glob.ID_NEW, _("New") + u"\tCtrl+N", 
                        _("Start a New File"))
        filemenu.Append(ed_glob.ID_OPEN, _("Open") + "\tCtrl+O", _("Open"))
        ## Setup File History in the File Menu
        filemenu.AppendMenu(ed_glob.ID_FHIST, _("Open Recent"), 
                            filehist, _("Recently Opened Files"))
        filemenu.AppendSeparator()
        filemenu.Append(ed_glob.ID_CLOSE, _("Close Page") + "\tCtrl+W", 
                        _("Close Current Page"))
        filemenu.AppendSeparator()
        filemenu.Append(ed_glob.ID_SAVE, _("Save") + "\tCtrl+S", 
                        _("Save Current File"))
        filemenu.Append(ed_glob.ID_SAVEAS, _("Save As") + "\tCtrl+Shift+S", 
                        _("Save As"))
        filemenu.AppendSeparator()
        filemenu.Append(ed_glob.ID_SAVE_PROFILE, _("Save Profile"), 
                             _("Save Current Settings to a New Profile"))
        filemenu.Append(ed_glob.ID_LOAD_PROFILE, _("Load Profile"), 
                        _("Load a Custom Profile"))
        filemenu.AppendSeparator()
        filemenu.Append(ed_glob.ID_PRINT_SU, _("Page Setup") + "\tCtrl+Shift+P",
                        _("Configure Printer"))
        filemenu.Append(ed_glob.ID_PRINT_PRE, _("Print Preview"), 
                        _("Preview Printout"))
        filemenu.Append(ed_glob.ID_PRINT, _("Print") + "\tCtrl+P", 
                        _("Print Current File"))
        filemenu.AppendSeparator()
        filemenu.Append(ed_glob.ID_EXIT, _("Exit") + "\tAlt+Q", 
                        _("Exit the Program"))
        self.Append(filemenu, _("File"))
        return filemenu

    def GenEditMenu(self):
        """Makes and attaches the edit menu"""
        editmenu = ED_Menu()
        editmenu.Append(ed_glob.ID_UNDO, _("Undo") + "\tCtrl+Z", 
                        _("Undo Last Action"))
        editmenu.Append(ed_glob.ID_REDO, _("Redo") + "\tCtrl+Shift+Z", 
                        _("Redo Last Undo"))
        editmenu.AppendSeparator()
        editmenu.Append(ed_glob.ID_CUT, _("Cut") + "\tCtrl+X", 
                        _("Cut Selected Text from File"))
        editmenu.Append(ed_glob.ID_COPY, _("Copy") + "\tCtrl+C", 
                        _("Copy Selected Text to Clipboard"))
        editmenu.Append(ed_glob.ID_PASTE, _("Paste") + "\tCtrl+V", 
                        _("Paste Text from Clipboard to File"))
        editmenu.AppendSeparator()
        editmenu.Append(ed_glob.ID_SELECTALL, _("Select All") + "\tCtrl+A", 
                        _("Select All Text in Document"))
        editmenu.AppendSeparator()
        linemenu = ED_Menu()
        linemenu.Append(ed_glob.ID_LINE_AFTER, _("New Line After") + "\tCtrl+L",
                         _("Add a new line after the current line"))
        linemenu.Append(ed_glob.ID_LINE_BEFORE, 
                        _("New Line Before") + "\tCtrl+Shift+L",
                        _("Add a new line before the current line"))
        linemenu.AppendSeparator()
        linemenu.Append(ed_glob.ID_CUT_LINE, _("Cut Line") + "\tCtrl+D",
                        _("Cut Current Line"))
        linemenu.Append(ed_glob.ID_COPY_LINE, _("Copy Line") + "\tCtrl+Y",
                        _("Copy Current Line"))
        linemenu.AppendSeparator()
        linemenu.Append(ed_glob.ID_JOIN_LINES, _("Join Lines") + "\tCtrl+J",
                        _("Join the Selected Lines"))
        linemenu.Append(ed_glob.ID_TRANSPOSE, _("Transpose Line") + "\tCtrl+T",
                        _("Transpose the current line with the previous one"))
        editmenu.AppendMenu(ed_glob.ID_LINE_EDIT, _("Line Edit"), linemenu,
                            _("Commands that affect an entire line"))
        bookmenu = ED_Menu()
        bookmenu.Append(ed_glob.ID_ADD_BM, _("Add Bookmark") + u"\tCtrl+B",
                        _("Add a bookmark to the current line"))
        bookmenu.Append(ed_glob.ID_DEL_BM, _("Remove Bookmark") + u"\tCtrl+Shift+B",
                        _("Remove bookmark from current line"))
        bookmenu.Append(ed_glob.ID_DEL_ALL_BM, _("Remove All Bookmarks"),
                        _("Remove all bookmarks from the current document"))
        editmenu.AppendMenu(ed_glob.ID_BOOKMARK, _("Bookmarks"),  bookmenu,
                            _("Add and remove bookmarks"))
        editmenu.AppendSeparator()
        editmenu.Append(ed_glob.ID_FIND, _("Find") + "\tCtrl+Shift+F", 
                        _("Find Text"))
        editmenu.Append(ed_glob.ID_FIND_REPLACE, _("Find/Replace") + "\tCtrl+R", 
                        _("Find and Replace Text"))
        editmenu.Append(ed_glob.ID_QUICK_FIND, _("Quick Find") + "\tCtrl+F", 
                        _("Open the Quick Find Bar"))
        editmenu.AppendSeparator()
        editmenu.Append(ed_glob.ID_PREF, _("Preferences"), 
                        _("Edit Preferences / Settings"))
        self.Append(editmenu, _("Edit"))
        return editmenu

    def GenViewMenu(self):
        """Makes and attaches the view menu"""
        viewmenu = ED_Menu()
        viewmenu.Append(ed_glob.ID_ZOOM_OUT, _("Zoom Out") + "\tCtrl+-", 
                        _("Zoom Out"))
        viewmenu.Append(ed_glob.ID_ZOOM_IN, _("Zoom In") + "\tCtrl++", 
                        _("Zoom In"))
        viewmenu.Append(ed_glob.ID_ZOOM_NORMAL, _("Zoom Default") + "\tCtrl+0", 
                            _("Zoom Default"))
        viewmenu.AppendSeparator()
        viewmenu.Append(ed_glob.ID_INDENT_GUIDES, _("Indentation Guides"), 
                             _("Show Indentation Guides"), wx.ITEM_CHECK)
        viewmenu.Append(ed_glob.ID_SHOW_EOL, _("Show EOL Markers"),
                        _("Show EOL Markers"), wx.ITEM_CHECK)
        viewmenu.Append(ed_glob.ID_SHOW_LN, _("Show Line Numbers"), 
                            _("Show Line Number Margin"), wx.ITEM_CHECK)
        viewmenu.Append(ed_glob.ID_SHOW_WS, _("Show Whitespace"), 
                             _("Show Whitespace Markers"), wx.ITEM_CHECK)
        viewmenu.AppendSeparator()
        viewmenu.Append(ed_glob.ID_GOTO_LINE, _("Goto Line") + u"\tCtrl+G",
                            _("Goto Line Number"))
        viewmenu.Append(ed_glob.ID_NEXT_MARK, _("Next Bookmark") + u"\tCtrl+Right", 
                            _("View Line of Next Bookmark"))
        viewmenu.Append(ed_glob.ID_PRE_MARK, _("Previous Bookmark") + u"\tCtrl+Left", 
                            _("View Line of Previous Bookmark"))
        viewmenu.AppendSeparator()
        viewmenu.Append(ed_glob.ID_VIEW_TOOL, _("Toolbar"), 
                             _("Show Toolbar"), wx.ITEM_CHECK)
        self.Append(viewmenu, _("View"))
        return viewmenu

    def GenFormatMenu(self):
        """Makes and attaches the format menu"""
        formatmenu = ED_Menu()
        formatmenu.Append(ed_glob.ID_FONT, _("Font"), _("Change Font Settings"))
        formatmenu.AppendSeparator()
        formatmenu.Append(ed_glob.ID_COMMENT, _("Comment Lines") + u"\tCtrl+1", 
                               _("Comment the selected lines"))
        formatmenu.Append(ed_glob.ID_UNCOMMENT, _("Uncomment Lines") + u"\tCtrl+2", 
                               _("Uncomment the selected lines"))
        formatmenu.AppendSeparator()
        formatmenu.Append(ed_glob.ID_INDENT, _("Indent Lines"), 
                              _("Indent the selected lines"))
        formatmenu.Append(ed_glob.ID_UNINDENT, _("Unindent Lines") + u"\tShift+Tab", 
                              _("Unindent the selected lines"))
        formatmenu.AppendSeparator()
        formatmenu.Append(ed_glob.ID_WORD_WRAP, _("Word Wrap"), 
                               _("Wrap Text Horizontally"), wx.ITEM_CHECK)
        formatmenu.AppendSeparator()
        lineformat = self._lineformatmenu
        lineformat.Append(ed_glob.ID_EOL_MAC, _("Macintosh (\\r)"), 
                              _("Format all EOL characters to %s Mode") % _("Macintosh (\\r)"),
                              wx.ITEM_CHECK)
        lineformat.Append(ed_glob.ID_EOL_UNIX, _("Unix (\\n)"), 
                              _("Format all EOL characters to %s Mode") % _("Unix (\\n)"),
                              wx.ITEM_CHECK)
        lineformat.Append(ed_glob.ID_EOL_WIN, _("Windows (\\r\\n)"), 
                              _("Format all EOL characters to %s Mode") % _("Windows (\\r\\n)"),
                              wx.ITEM_CHECK)
        formatmenu.AppendMenu(ed_glob.ID_EOL_MODE, _("EOL Mode"), lineformat,
                                  _("End of line character formatting"))
        self.Append(formatmenu, _("Format"))
        return formatmenu

    def GenSettingsMenu(self):
        """Makes and attaches the settings menu"""
        settingsmenu = ED_Menu()
        settingsmenu.Append(ed_glob.ID_AUTOCOMP, _("Auto-Completion"),
                            _("Use Auto Completion when available"), wx.ITEM_CHECK)
        settingsmenu.Append(ed_glob.ID_AUTOINDENT, _("Auto-Indent"),
                            _("Toggle Auto-Indentation functionality"), 
                            wx.ITEM_CHECK)
        settingsmenu.Append(ed_glob.ID_BRACKETHL, _("Bracket Highlighting"), 
                            _("Highlight Brackets/Braces"), wx.ITEM_CHECK)
        settingsmenu.Append(ed_glob.ID_FOLDING, _("Code Folding"),
                            _("Toggle Code Foldering"), wx.ITEM_CHECK)
        settingsmenu.Append(ed_glob.ID_SYNTAX, _("Syntax Highlighting"), 
                            _("Color Highlight Code Syntax"), wx.ITEM_CHECK)
        # Lexer Menu Appended later by main frame
        self.Append(settingsmenu, _("Settings"))
        return settingsmenu

    def GenToolsMenu(self):
        """Makes and attaches the tools menu"""
        toolsmenu = ED_Menu()
        toolsmenu.Append(ed_glob.ID_STYLE_EDIT, _("Style Editor"), 
                         _("Edit the way syntax is highlighted"))
        toolsmenu.Append(ed_glob.ID_KWHELPER,_("Keyword Helper") + u'\tCtrl+K', 
                         _("Provides a Contextual Help Menu Listing Standard Keywords/Functions"))
        toolsmenu.AppendSeparator()
        genmenu = ED_Menu()
        genmenu.Append(ed_glob.ID_HTML_GEN, _("Generate %s") % u"HTML",
                       _("Generate an HTML page from the current document"))
        genmenu.Append(ed_glob.ID_TEX_GEN, _("Generate %s") % u"LaTeX",
                       _("Generate an LaTeX page from the current document"))
        toolsmenu.AppendMenu(ed_glob.ID_GENERATOR, _("Generator"), genmenu,
                             _("Generate Code"))
        self.Append(toolsmenu, _("Tools"))
        return toolsmenu
 
    def GenHelpMenu(self):
        """Makes and attaches the help menu"""
        helpmenu = ED_Menu()
        helpmenu.Append(ed_glob.ID_ABOUT, _("&About") + u"...", _("About") + u"...")
        helpmenu.Append(ed_glob.ID_HOMEPAGE, _("Project Homepage"), 
                            _("Visit the project homepage %s") % ed_glob.home_page)
        helpmenu.Append(ed_glob.ID_CONTACT, _("Feedback"),
                            _("Send me bug reports and suggestions"))
        self.Append(helpmenu, _("Help"))
        return helpmenu

    def GetMenuByName(self, namestr):
        """Find and return a menu by name"""
        menu = "_%smenu" % namestr.lower()
        if hasattr(self, menu):
            return getattr(self, menu)
        else:
            return None
