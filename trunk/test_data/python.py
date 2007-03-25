############################################################################
#    Copyright (C) 2006 Editra Development Team   			   #
#    codyprecord@gmail.com   						   #
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
# FILE: MainWindow.py							   #
# LANGUAGE: Python							   #
#									   #
# SUMMARY:								   #
#   This module impliments the main window class of the editor. The        #
#  MainWindow consists of a a WxFrame that contains the interface to the   #
#  editor.                                                                 #
#									   #
# METHODS:								   #
# - __init__: Initializes the frame/menu/toolbar/statusbar/event handlers  #
# - OnNew: Handles "New" event by asking the notebook to open a new blank  #
#	   page.							   #
# - OnOpen: Catches Open event and passes it to DoOpen			   #
# - DoOpen: Does work of opening pages/files in Frame			   #
# - OnClosePage: Handles close page event by asking notebook to close the  #
#		 Currently selected page.				   #
# - ModifySave: Called when closing page / program to prompt user and ask  #
#		if they want to save or not.				   #
# - OnSave: Saves control text to acutal file by asking the control to     #
#	    write the data out to file, unless the document does not have  #
#	    a name which in that case it will in turn call SaveAs	   #
# - OnSaveAs: Saves current document to the file specified in the dialog.  #
# - OnPrint: Sends current controls text to printer device		   #
# - OnExit: Closes all windows, and shuts the program down.		   #
# - 
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies

import os			# Python OS libraries
import sys			# Python System libraries
import wx			# wxPython libraries
import wx.lib.printout as printout 
from ed_glob import *		# Global Variables
import util 			# Misc Helper functions
import dev_tool 		# Tools Used for Debugging
import profiler
import ed_toolbar
import ed_pages 		# Notebook Class
import prefdlg                  # Preference Dialog Class

#--------------------------------------------------------------------------#


class MainWindow(wx.Frame):
    """This is the main class that glues everything together"""
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(700, 450),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetTitle(prog_name + u' - v' + version)

        # Try and set an app icon
        try:
            if wx.Platform == '__WXMSW__':
                ed_icon = CONFIG['PIXMAPS_DIR'] + "editra.ico"
                self.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_ICO))
                dev_tool.DEBUGP("Set Icon for Windows")
            else:
                ed_icon = CONFIG['PIXMAPS_DIR'] + "editra.png"
                self.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_PNG))
                dev_tool.DEBUGP("Set Icon for " + os.sys.platform)
        finally:
            pass

        #---- Sizers to hold subapplets ----#
        self.sizer = wx.BoxSizer()

        #---- Setup File History ----#
        self.filehistory = wx.FileHistory(int(PROFILE['FHIST_LVL']))

        #---- Toolbar ----#
        self.toolbar = None

        #---- Notebook to hold editor windows ----#
        self.nb = ed_pages.ED_Pages(self, -1)

        #---- Fill the sizer ----#
        self.sizer.Add(self.nb, 0, wx.EXPAND)

        #---- Check for commandline args ----#
        for arg in sys.argv[1:]:
            try:
                if arg != "" and arg[0] != "-":
                    self.DoOpen(ID_COMMAND_LINE_OPEN, arg)
                else:
                    break
            except IndexError:
                dev_tool.DEBUGP("Error: Trapped IndexError on Init")
                pass

        #---- Status bar on bottom of window ----#
        self.CreateStatusBar(2, style=wx.ST_SIZEGRIP)
        self.SetStatusWidths([-1, 155])
        #---- End Statusbar Setup ----#

        #---- Create a toolbar ----#
        if PROFILE['TOOLBAR']:
            self.toolbar = ed_toolbar.ED_ToolBar(self, 16)
            self.SetToolBar(self.toolbar)

        # Toolbar Event Handlers
        wx.EVT_TOOL(self, ID_NEW, self.OnNew)
        wx.EVT_TOOL(self, ID_OPEN, self.OnOpen)
        wx.EVT_TOOL(self, ID_SAVE, self.OnSave)
        wx.EVT_TOOL(self, ID_PRINT, self.OnPrint)
        wx.EVT_TOOL(self, ID_UNDO, self.OnUndo)
        wx.EVT_TOOL(self, ID_REDO, self.OnRedo)
        wx.EVT_TOOL(self, ID_COPY, self.OnCopy)
        wx.EVT_TOOL(self, ID_CUT, self.OnCut)
        wx.EVT_TOOL(self, ID_PASTE, self.OnPaste)
        wx.EVT_TOOL(self, ID_FIND, self.OnShowFind)
        wx.EVT_TOOL(self, ID_FIND_REPLACE, self.OnShowFindReplace)
        #---- End Toolbar Setup ----#

        #---- Menus ----#
        self.filemenu = wx.Menu()
        self.editmenu = wx.Menu()
        self.viewmenu = wx.Menu()
        self.formatmenu = wx.Menu()
        self.settingsmenu = wx.Menu()
        self.helpmenu = wx.Menu()

        # Submenus
        self.fileopen = wx.Menu() #submenu of file
        languagemenu = wx.Menu() #submenu of settings

        #---- Submenu Items ----#
        # Language (sub of settings)
        languagemenu.Append(ID_LANG_ASM, "ASM", "Switch Lexer to ASM", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_BATCH, "Batch", "Switch Lexer to Batch",
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_C, "C", "Switch Lexer to C", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_CPP, "CPP", "Switch Lexer to CPP", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_CSS, "CSS", "Switch Lexer to CSS", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_H, "Header Files", 
                            "Switch Lexer to Header Files", wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_HTML, "HTML", "Switch Lexer to HTML", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_JAVA, "Java", "Switch Lexer to Java", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_LISP, "Lisp", "Switch Lexer to Lisp", 
                            wx.ITEM_CHECK)	
        languagemenu.Append(ID_LANG_MAKE, "Makefile", 
                            "Switch Lexer to Makefiles", wx.ITEM_CHECK)	
        languagemenu.Append(ID_LANG_NSIS, "NSIS", 
                            "Switch Lexer to Nullsoft Scriptable Installer", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_PASCAL, "Pascal", "Switch Lexer to Pascal",
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_PERL, "Perl", 
                           "Switch Lexer to Perl Scripts", wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_PHP, "PHP", "Switch Lexer to PHP", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_PS, "PostScript", 
                            "Switch Lexer to PostScript", wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_PYTHON, "PYTHON", "Switch Lexer to Python",
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_RUBY, "Ruby", "Switch Lexer to Ruby", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_SHELL, "Shell Scripts", 
                            "Switch Lexer to Shell Scripts", wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_SQL, "SQL", "Switch Lexer to SQL", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_TEX, "Tex/LaTex", 
                            "Switch Lexer to Tex/LaTex", wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_VHDL, "VHDL", "Switch Lexer to VHDL", 
                            wx.ITEM_CHECK)
        languagemenu.Append(ID_LANG_VB, "Visual Basic", 
                            "Switch Lexer to Visual Basic", wx.ITEM_CHECK)

        #---- Menu Items ----#
        # File Menu Items
        self.filemenu.Append(ID_NEW, LANG['New'] + "\tCtrl+N", 
                             "Start a New File")
        self.filemenu.Append(ID_OPEN, LANG['Open'] + "\tCtrl+O", "Open a File")
        ## Setup File History in the File Menu
        self.filehistory.UseMenu(self.fileopen)
        self.filemenu.AppendMenu(wx.ID_ANY, LANG['OpenR'], self.fileopen, 
                                     "Recently Opened Files")
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_CLOSE, LANG['Close'] + "\tCtrl+W", "Close Current Page")
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_SAVE, LANG['Save'] + "\tCtrl+S", LANG['Save'])
        self.filemenu.Append(ID_SAVEAS, LANG['SaveAs'], LANG['SaveAs'])
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_SAVE_PROFILE, LANG['SavePro'], 
			"Save Current Settings to New Profile")
        self.filemenu.Append(ID_LOAD_PROFILE, LANG['LoadPro'], 
                             "Load a Custom Profile")
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_PRINT, LANG['Print'] + "\tCtrl+P", "Print a File")
        self.filemenu.AppendSeparator()
        self.filemenu.Append(ID_EXIT, LANG['Exit'] + "\tAlt+Q", "Exit the Program")

        # Edit Menu Items
        self.editmenu.Append(ID_UNDO, LANG['Undo'] + "\tCtrl+Z", "Undo Last Action")
        self.editmenu.Append(ID_REDO, LANG['Redo'] + "\tCtrl+Shift+Z", "Redo Last Undo")
        self.editmenu.AppendSeparator()
        self.editmenu.Append(ID_CUT, LANG['Cut'] + "\tCtrl+X", 
                             "Cut Selected Text From Document")
        self.editmenu.Append(ID_COPY, LANG['Copy'] + "\tCtrl+C", "Copy Selected Text to Clipboard")
        self.editmenu.Append(ID_PASTE, LANG['Paste'] + "\tCtrl+V", 
                             "Paste Text from Clipboard to Document")
        self.editmenu.AppendSeparator()
        self.editmenu.Append(ID_SELECTALL, LANG['SelectA'] + "\tCtrl+A", 
                             "Select All Text In Document")
        self.editmenu.AppendSeparator()
        self.editmenu.Append(ID_FIND, LANG['Find'] + "\tCtrl+F", "Find Text")
        self.editmenu.Append(ID_FIND_REPLACE, LANG['FReplace'] + "\tCtrl+R", 
                             "Find & Replace")
        self.editmenu.AppendSeparator()
        self.editmenu.Append(ID_PREF, LANG['Pref'], "Edit Preferences / Settings")

        # View Menu Items
        self.viewmenu.Append(ID_ZOOM_OUT, LANG['ZoomO'] + "\tCtrl+-", LANG['ZoomO'])
        self.viewmenu.Append(ID_ZOOM_IN, LANG['ZoomI'] + "\tCtrl++", LANG['ZoomI'])
        self.viewmenu.Append(ID_ZOOM_NORMAL, LANG['ZoomD'] + "\tCtrl+0", LANG['ZoomD'])
        # Disable default at init
        self.viewmenu.Enable(ID_ZOOM_NORMAL, False)
        self.viewmenu.AppendSeparator()
        self.viewmenu.Append(ID_SHOW_WS, u"Show Whitespace", 
                             u"Toggle Whitespace visibility", wx.ITEM_CHECK)
        if PROFILE['SHOW_WS']:
            self.viewmenu.Check(ID_SHOW_WS, -1)
        self.viewmenu.AppendSeparator()
        self.viewmenu.Append(ID_VIEW_TOOL, LANG['Toolbar'], "Show Toolbar",
                            wx.ITEM_CHECK)
        if PROFILE['TOOLBAR']:
            self.viewmenu.Check(ID_VIEW_TOOL, -1)

        # Format Menu Items
        self.formatmenu.Append(ID_WORD_WRAP, LANG['WordWrap'], 
                               "Wrap Text Horizontally", wx.ITEM_CHECK)
        self.formatmenu.Append(ID_FONT, LANG['Font'], "Change Font Settings")

        ## Set Check Marks
        if PROFILE['WRAP']:
            self.formatmenu.Check(ID_WORD_WRAP, -1)

        # Settings Menu Items
        self.settingsmenu.Append(ID_SYNTAX, "Syntax Highlight",
                                 "Color Highlight Code Syntax", wx.ITEM_CHECK)
        self.settingsmenu.Append(ID_INDENT_GUIDES, "Indentation Guides", 
                                 "Use Indentation Guides", wx.ITEM_CHECK)
        self.settingsmenu.Append(ID_BRACKETHL, "Bracket Highlighting", 
                                 "Turn Bracket Highlighting On or Off", wx.ITEM_CHECK)
        self.settingsmenu.Append(ID_COMPLETION, "Code Completion", 
                                 "Provide Function/Keyword Hints and Tips", 
                                 wx.ITEM_CHECK)
        self.settingsmenu.AppendMenu(ID_LANG, "Lexers", languagemenu, 
                                     "Manually Set Lexer")

        self.languagemenu = languagemenu

        ## Set Check Marks
        if PROFILE['SYNTAX']:
            self.settingsmenu.Check(ID_SYNTAX, -1)
        if PROFILE['GUIDES']:
            self.settingsmenu.Check(ID_INDENT_GUIDES, -1)
        if PROFILE['BRACKETHL']:
            self.settingsmenu.Check(ID_BRACKETHL, -1)
        if PROFILE['COMPLETION']:
            self.settingsmenu.Check(ID_COMPLETION, -1)

        # Help Menu Items
        self.helpmenu.Append(ID_ABOUT, LANG['About'], 
                             "Information About this Program")

        #---- Menu Bar ----#
        self.menubar = wx.MenuBar()
        self.menubar.Append(self.filemenu, LANG['File'])
        self.menubar.Append(self.editmenu, LANG['Edit'])
        self.menubar.Append(self.viewmenu, LANG['View'])
        self.menubar.Append(self.formatmenu, LANG['Format'])
        self.menubar.Append(self.settingsmenu, LANG['Settings'])
        self.menubar.Append(self.helpmenu, LANG['Help'])
        self.SetMenuBar(self.menubar)

        #---- Actions to take on menu events ----#
        wx.EVT_MENU_OPEN(self, self.UpdateMenu)

        # File Menu Events
        wx.EVT_MENU(self, ID_NEW, self.OnNew)
        wx.EVT_MENU(self, ID_OPEN, self.OnOpen)
        wx.EVT_MENU(self, ID_CLOSE, self.OnClosePage)
        wx.EVT_MENU(self, ID_SAVE, self.OnSave)
        wx.EVT_MENU(self, ID_SAVEAS, self.OnSaveAs)
        wx.EVT_MENU(self, ID_SAVE_PROFILE, self.OnSaveProfile)
        wx.EVT_MENU(self, ID_LOAD_PROFILE, self.OnLoadProfile)
        wx.EVT_MENU(self, ID_PRINT, self.OnPrint)
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)
        self.Bind(wx.EVT_MENU_RANGE, self.OnFileHistory, 
                  id=wx.ID_FILE1, id2=wx.ID_FILE4)

        # Edit Menu Events
        wx.EVT_MENU(self, ID_UNDO, self.OnUndo)
        wx.EVT_MENU(self, ID_REDO, self.OnRedo)
        wx.EVT_MENU(self, ID_CUT, self.OnCut)
        wx.EVT_MENU(self, ID_COPY, self.OnCopy)
        wx.EVT_MENU(self, ID_PASTE, self.OnPaste)
        wx.EVT_MENU(self, ID_SELECTALL, self.OnSelectAll)
        wx.EVT_MENU(self, ID_FIND, self.OnShowFind)
        wx.EVT_MENU(self, ID_FIND_REPLACE, self.OnShowFindReplace)
        wx.EVT_MENU(self, ID_PREF, self.OnPreferences)

        # View Menu Events
        wx.EVT_MENU(self, ID_ZOOM_OUT, self.OnZoom)
        wx.EVT_MENU(self, ID_ZOOM_IN, self.OnZoom)
        wx.EVT_MENU(self, ID_ZOOM_NORMAL, self.OnZoom)
        wx.EVT_MENU(self, ID_SHOW_WS, self.OnShowWS)
        wx.EVT_MENU(self, ID_VIEW_TOOL, self.OnViewTb)

        # Format Menu Events
        wx.EVT_MENU(self, ID_WORD_WRAP, self.OnWrap)
        wx.EVT_MENU(self, ID_FONT, self.OnFont)

        # Settings Menu Events
        wx.EVT_MENU(self, ID_SYNTAX, self.OnSyntaxHL)
        wx.EVT_MENU(self, ID_INDENT_GUIDES, self.OnIndentGuides)
        wx.EVT_MENU(self, ID_BRACKETHL, self.OnHLBrackets)
        wx.EVT_MENU(self, ID_COMPLETION, self.OnCodeCompletion)

        ## Language Menu Events (Sub of Settings)
        wx.EVT_MENU(self, wx.ID_ANY, self.OnSetLexer)

        # Help Menu Events
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        #---- End Menu Setup ----#

        #---- Actions to Take on other Events ----#
        # Drop Events
        self.Bind(wx.EVT_DROP_FILES, self.nb.control.dt.OnDropFiles)

        # Frame
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # Find Dialog
        self.Bind(wx.EVT_FIND, self.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE, self.OnFindClose)

        # Text Control Events #TODO move to stc
        self.nb.control.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        #---- End other event actions ----#

        #---- Final Setup Calls ----#
        self.LoadFileHistory(int(PROFILE['FHIST_LVL']))
        self.UpdateToolBar()

        #---- Show the Frame ----#
        self.CenterOnParent()
        self.Show(True)

    ### End Init ###

    ### Begin Function Definitions ###

    #---- File Menu Functions ----#
    def OnNew(self, evt):
        """New File"""
        self.nb.NewPage()
        self.nb.GoCurrentPage()
	self.UpdateToolBar()

    def OnOpen(self, evt):
        """Open File"""
        self.DoOpen(evt)
	self.UpdateToolBar()

    def DoOpen(self, evt, file_name=''):
        """ Do the work of opening a file and placing it
        in a new notebook page.

        """
        dlg = wx.FileDialog(self, "Choose a File", '', "", 
                            self.MenuFileTypes(), wx.OPEN | wx.MULTIPLE)

        result = wx.ID_CANCEL

        try:
            e_id = evt.GetId()
        except AttributeError:
            e_id = evt

        if e_id == ID_OPEN:
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                dlg.Destroy()
                result = dlg.GetReturnCode()

            if result != wx.ID_CANCEL:
                for path in paths:
                    dirname = util.GetPathName(path)
                    filename = util.GetFileName(path)
                    self.nb.OpenPage(dirname, filename)		   
                    self.SetTitle(self.nb.control.filename + " - " + 
                                  "file://" + self.nb.control.dirname +
                                  "/" + self.nb.control.filename + 
                                  " - " + prog_name + " v" + version)
                    self.nb.GoCurrentPage()
            else:
                pass
        else:
            dev_tool.DEBUGP("INFO: CMD OPEN FILE = " + file_name)
            filename = util.GetFileName(file_name)
            dirname = util.GetPathName(file_name)
            self.nb.OpenPage(dirname, filename)

    def OnClosePage(self, evt):
        """Close a page"""
        self.nb.ClosePage()

    def ModifySave(self):
        """Called when document has been modified prompting
        a message dialog asking if the user would like to save
        the document before closing.

        """
        if self.nb.control.filename == "":
            name = self.nb.GetPageText(self.nb.GetSelection()) #"This Document "
        else:
            name = self.nb.control.filename

	dlg = wx.MessageDialog(self, "The file: \"" + name + 
                               "\" has been modified since the last save point \n"
                               "Would you like to save the changes?", 
                               "Save Changes?", 
                               wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            self.OnSave(ID_SAVE)
        else:
            pass

        return result

    def OnSave(self, evt):
        """Save"""
        if self.nb.control.filename != '':
            self.nb.control.Save()
            self.PushStatusText("Saved File: " + self.nb.control.filename, 
                                SB_INFO)
        else:
            self.OnSaveAs(ID_SAVEAS)
	self.UpdateToolBar()

    def OnSaveAs(self, evt):
        """Save As"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a save location", self.dirname, "", 
                            self.MenuFileTypes(), wx.SAVE|wx.OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        if result == wx.ID_OK: 
            path = dlg.GetPath()
            self.nb.control.SaveAs(path)
            self.PushStatusText("Saved File As: " + self.nb.control.filename, 
                                SB_INFO)
            self.SetTitle(self.nb.control.filename + " - file://" + 
                          self.nb.control.dirname + self.nb.control.path_char + 
                          self.nb.control.filename + " - " + prog_name + " v" + version)
            self.nb.SetPageText(self.nb.GetSelection(), 
                                self.nb.control.filename)
            self.nb.UpdatePageImage()
        else:
            pass

    def OnSaveProfile(self, evt):
        """Saves current settings as a profile"""
        dlg = wx.FileDialog(self, "Where to Save Profile", CONFIG['PROFILE_DIR'], 
                            "default.pp", "Profiles (*.pp)|*.pp", 
                            wx.SAVE | wx.OVERWRITE_PROMPT)

        result = dlg.ShowModal()
        if result == wx.ID_OK: 
            profile = dlg.GetFilename()
            path = dlg.GetPath()
            profiler.WriteProfile(path)
            self.PushStatusText("Profile Saved as: " + profile, SB_INFO)
        else:
            pass

    def OnLoadProfile(self, evt):
        """Loads a profile"""
        dlg = wx.FileDialog(self, "Profile to Load", CONFIG['PROFILE_DIR'], 
                            "default.pp", "Profiles (*.pp)|*.pp", wx.OPEN)

        result = dlg.ShowModal()
        if result == wx.ID_OK: 
            profile = dlg.GetFilename()
            path = dlg.GetPath()
            profiler.ReadProfile(path)
            self.PushStatusText("Loaded Profile: " + profile, SB_INFO)
            dlg.Destroy()
        else:
            pass

        # Update editor to reflect loaded profile
        if PROFILE['SYNTAX']:
            self.nb.control.SyntaxOnOff(ID_SYN_ON)
            self.settingsmenu.Check(ID_SYNTAX, -1)
        else:
            self.nb.control.SyntaxOnOff(ID_SYN_OFF)
            self.settingsmenu.Check(ID_SYNTAX, 0)

        if PROFILE['WRAP']:
            self.nb.control.WrapOnOff(1)
            self.formatmenu.Check(ID_WORD_WRAP, -1)
        else:
            self.nb.control.WrapOnOff(0)
            self.formatmenu.Check(ID_WORD_WRAP, 0)

        if PROFILE['GUIDES']:
            self.nb.control.IndentGuideOnOff(1)
            self.settingsmenu.Check(ID_INDENT_GUIDES, -1)
        else:
            self.nb.control.IndentGuideOnOff(0)
            self.settingsmenu.Check(ID_INDENT_GUIDES, 0)

        if PROFILE['COMPLETION']:
            self.nb.control.codecompletion = False
            self.nb.control.CodeCompletionOnOff()
            self.settingsmenu.Check(ID_COMPLETION, -1)
        else:
            self.nb.control.codecompletion = True
            self.nb.control.CodeCompletionOnOff()
            self.settingsmenu.Check(ID_COMPLETION, 0)

        evt.Skip()

    def LoadFileHistory(self, size):
        """Loads file history from profile"""
        file_key = "FILE"
        i = size - 1 

        while i >= 0:
            key = file_key + str(i)
            try:
                self.filehistory.AddFileToHistory(PROFILE[key])
            except KeyError: 
                dev_tool.DEBUGP("Invalid Key on LoadFileHistory")
                pass

            i -= 1

        return size - i

    def OnPrint(self, evt):
        """Prints contents of current control to printer device"""
        self.PreviewText()
        evt.Skip()

    def OnExit(self, evt):
        """Exit"""

        # This event is bound at two location need to unbind it to avoid fireing
	# the event again
        self.Unbind(wx.EVT_CLOSE)

        # Cleanup Controls
        controls = self.nb.GetPageCount()
        dev_tool.DEBUGP("EXIT: Number of controls = " + str(controls))

        while controls:
            if controls <= 0:
                self.Close(True)

            dev_tool.DEBUGP("ON EXIT: Closed Page #" + 
                            str(self.nb.GetSelection()))
            result = self.nb.ClosePage()
            if result == wx.ID_CANCEL:
                break
            controls -= 1

        try:
            if result != wx.ID_CANCEL:
                # We are exiting so continue finish cleanup
                pass
            else:
                # Rebind the event
                self.Bind(wx.EVT_CLOSE,self.OnExit)
                return
        except UnboundLocalError:
            dev_tool.DEBUGP("Trapped UnboundLocalError OnExit")
            pass

        # If we get to here we are exiting for sure so cleanup
	# additional items and save the user settings

        # Update profile loader
        profiler.UpdateProfileLoader()

        # Update File History in Profile
        profiler.AddFileHistoryToProfile(self.filehistory)

        # Update profile
        profiler.WriteProfile(PROFILE['MYPROFILE'])
	
        # Cleanup file history
        try:
            del self.filehistory
        except AttributeError:
            dev_tool.DEBUGP("Trapped AttributeError OnExt")
            pass

        # Finally close the application
        self.Close(True)

    def OnFileHistory(self, evt):
        """ Open a File from the File History """
        fileNum = evt.GetId() - wx.ID_FILE1
        file_handle = self.filehistory.GetHistoryFile(fileNum)

        # Check if file still exists
	if not os.path.exists(file_handle):
            mdlg = wx.MessageDialog(self, "file: " + file_handle,
                                          "The file you selected could not " + 
			                  "be found\n" + 
					  "Perhaps its been moved or deleted",
                                     wx.OK | wx.ICON_WARNING)
            mdlg.CenterOnParent()
            mdlg.ShowModal()
            mdlg.Destroy()
            # Remove offending file from history
            self.filehistory.RemoveFileFromHistory(fileNum)
        else:
            # Open File
            self.DoOpen(evt, file_handle)

        evt.Skip()

    #---- End File Menu Functions ----#

    #---- Edit Menu Functions ----#
    def OnUndo(self, evt):
        """Undo"""
        self.nb.control.Undo()
	self.UpdateToolBar()

    def OnRedo(self, evt):
        """Redo"""
        self.nb.control.Redo()
	self.UpdateToolBar()

    def OnCut(self, evt):
        """Cut"""
        self.nb.control.Cut()
	self.UpdateToolBar()

    def OnCopy(self, evt):
        """Copy"""
        self.nb.control.Copy()
	self.UpdateToolBar()

    def OnPaste(self, evt):
        """Paste"""
        self.nb.control.Paste()
	self.UpdateToolBar()

    def OnSelectAll(self, evt):
        """Select All"""
        self.nb.control.SelectAll()
        evt.Skip()

    def OnShowFind(self, evt):
        """Show a Find dialog"""
        data = wx.FindReplaceData()
	data.SetFlags(wx.FR_DOWN)
        self.find_dlg = wx.FindReplaceDialog(self.nb, data, LANG['Find'].replace(u"&",u""), 
                                             wx.FR_NOUPDOWN |
					     wx.FR_NOWHOLEWORD)		# TODO
        self.find_dlg.data = data # save reference to data
	self.find_dlg.CenterOnParent()
        self.find_dlg.Show()

    def OnShowFindReplace(self, evt):
        """Show a find/replace dialog"""
        data = wx.FindReplaceData()
	data.SetFlags(wx.FR_DOWN)
        self.find_dlg = wx.FindReplaceDialog(self.nb, data, LANG['FReplace'].replace(u"&",u""),
                                             wx.FR_REPLACEDIALOG |
                                             wx.FR_NOUPDOWN |
					     wx.FR_NOWHOLEWORD)		# TODO
        self.find_dlg.data = data # save reference to data
	self.find_dlg.CenterOnParent()
        self.find_dlg.Show()

    def OnFind(self, evt):
        """Actually do the work of Finding text in a document"""
        dlg = self.find_dlg

        # Set of events to map to identifiers
        e_map = { wx.wxEVT_COMMAND_FIND : "FIND",
                  wx.wxEVT_COMMAND_FIND_NEXT : "FIND_NEXT",
                  wx.wxEVT_COMMAND_FIND_REPLACE : "REPLACE",
                  wx.wxEVT_COMMAND_FIND_REPLACE_ALL : "REPLACE_ALL",
                }

        # Get Search Type
        etype = evt.GetEventType()
        if etype in e_map:
            evtType = e_map[etype]
        else:
            evtType = "**Unknown Event Type**"

	# Process Special search flags
        eflags = self.find_dlg.data.GetFlags() - 1
        eflag_map = { wx.FR_MATCHCASE : "MATCH_CASE", 
                      wx.FR_WHOLEWORD : "WHOLE_WORD",
                      wx.FR_MATCHCASE + wx.FR_WHOLEWORD : "WORD_CASE"
                    }
	if eflags in eflag_map:
            eflags = eflag_map[eflags]
        else:
            eflags = "**Uknown Search Flag**"

        if evtType in ["FIND", "FIND_NEXT"]:
            line_count = self.nb.control.GetLineCount()
            last = self.nb.control.GetLineEndPosition(line_count)
            start = self.nb.control.GetCurrentPos()
            if eflags in ["MATCH_CASE", "WORD_CASE"]:
                textstring = self.nb.control.GetTextRange(0, last)
                dlg.findstring = dlg.data.GetFindString()
            else:
                textstring = self.nb.control.GetTextRange(0, last).lower()
                dlg.findstring = dlg.data.GetFindString().lower()

            loc = textstring.find(dlg.findstring, start)

            if loc == -1 and start != 0:
                # string not found, start at beginning again
                dev_tool.DEBUGP("FIND: starting at top again")
                start = 0
                loc = textstring.find(dlg.findstring, start)

            if loc == -1:
                # Couldn't Find the string let user know
                mdlg = wx.MessageDialog(self, 'Not Found',
                                        '\'' + dlg.findstring + 
                                        '\' Not Found in File',
                                        wx.OK | wx.ICON_INFORMATION)
                mdlg.ShowModal()
                mdlg.Destroy()

            self.nb.control.SetCurrentPos(loc)
            self.nb.control.SetSelection(loc, loc + len(dlg.findstring))

        elif evtType == "REPLACE":
            replacestring = evt.GetReplaceString()
            self.nb.control.ReplaceSelection(replacestring)

	elif evtType == "REPLACE_ALL":
            replacestring = evt.GetReplaceString()
            if eflags in ["MATCH_CASE", "WORD_CASE"]:
                dlg.findstring = dlg.data.GetFindString()
            else:
                dlg.findstring = dlg.data.GetFindString().lower()

	    if replacestring != dlg.findstring:
                # Find all instances and replace with replacestring
                line_count = self.nb.control.GetLineCount()
                last = self.nb.control.GetLineEndPosition(line_count)
                start = 0
                loc = 0
                while 1:
                    if eflags in ["MATCH_CASE", "WORD_CASE"]:
                        textstring = self.nb.control.GetTextRange(loc, last)
                    else:
                        textstring = self.nb.control.GetTextRange(loc, last).lower()
                    loc = textstring.find(dlg.findstring, start)

		    # Text not found
                    if loc == -1:
                        break

		    if self.nb.control.GetCurrentPos() != loc:
                        self.nb.control.SetCurrentPos(loc)
                    self.nb.control.SetSelection(loc, loc + len(dlg.findstring))
                    self.nb.control.ReplaceSelection(replacestring)
		    start = self.nb.control.GetCurrentPos()
		    loc = 0

		    # Document size may have changed so lets check
                    line_count = self.nb.control.GetLineCount()
                    last = self.nb.control.GetLineEndPosition(line_count)

            # Notify that replace all is finished
            mdlg = wx.MessageDialog(self, "Replace All Finished", "All Done", 
                                    wx.OK | wx.ICON_INFORMATION)
            mdlg.ShowModal()
            mdlg.Destroy()
        else:
            pass

    def OnFindClose(self, evt):
        """Destroy Find Dialog on cancel to avoid memory leaks"""
        dev_tool.DEBUGP("FIND DLG DESTROYED")

        self.find_dlg.Destroy()
        evt.Skip()

    def OnPreferences(self, evt):
        """Open the Preference Panel"""
        dlg = prefdlg.PrefDlg(self)
	dlg.CenterOnParent()
        dlg.ShowModal()
        dlg.Destroy()

    #---- End Edit Menu Functions ----#

    #---- View Menu Functions ----#
    def OnZoom(self, evt):
        """Zoom in or out on a document"""
        mode = evt.GetId()
        zoom_level = self.nb.control.DoZoom(mode)

        # Enable/Disable Menu Entries
        if zoom_level == 19:
            self.viewmenu.Enable(ID_ZOOM_IN, False)
            self.viewmenu.Enable(ID_ZOOM_OUT, True)
            self.viewmenu.Enable(ID_ZOOM_NORMAL, True)
        elif zoom_level == -8:
            self.viewmenu.Enable(ID_ZOOM_OUT, False)
            self.viewmenu.Enable(ID_ZOOM_IN, True)
            self.viewmenu.Enable(ID_ZOOM_NORMAL, True)
        elif zoom_level == 0:
            self.viewmenu.Enable(ID_ZOOM_NORMAL, False)
            self.viewmenu.Enable(ID_ZOOM_OUT, True)
            self.viewmenu.Enable(ID_ZOOM_IN, True)
        else:
            self.viewmenu.Enable(ID_ZOOM_OUT, True)
            self.viewmenu.Enable(ID_ZOOM_NORMAL, True)
            self.viewmenu.Enable(ID_ZOOM_IN, True)
        return 0

    def OnShowWS(self, evt):
        """Toggle Whitespace Visibility"""
        if PROFILE['SHOW_WS']:
            self.nb.control.SetViewWhiteSpace(False)
	    PROFILE['SHOW_WS'] = False
        else:
            self.nb.control.SetViewWhiteSpace(True)
	    PROFILE['SHOW_WS'] = True

    def OnViewTb(self, evt):
        """Toggles visibility of toolbar"""
	if PROFILE['TOOLBAR'] and self.toolbar != None:
            self.toolbar.Destroy()
            PROFILE['TOOLBAR'] = False
        else:
	    self.toolbar = ed_toolbar.ED_ToolBar(self, 16)
            self.SetToolBar(self.toolbar)
            PROFILE['TOOLBAR'] = True
	    self.UpdateToolBar()
	self.SetBestFittingSize()
        evt.Skip()

    #---- End View Menu Functions ----#

    #---- Format Menu Functions ----#
    def OnWrap(self, evt):
        """Word Wrap"""
        if self.nb.control.wordwrap:
            self.nb.control.WrapOnOff(0)
            self.PushStatusText("Word Wrap Off", SB_INFO)
        else:	
            self.nb.control.WrapOnOff(1)
            self.PushStatusText("Word Wrap On", SB_INFO)
        evt.Skip()

    def OnFont(self, evt):
        """Font"""
        dlg = wx.FontDialog(self, wx.FontData())
        result = dlg.ShowModal()
        data = dlg.GetFontData()

        if result == wx.ID_OK:
            font = data.GetChosenFont()
            self.nb.control.StyleSetFont(0, font)

        dlg.Destroy()
        evt.Skip()

    #---- End Format Menu Functions ----#

    #---- Settings Menu Functions ----#
    def OnSyntaxHL(self, evt):
        """Turn Syntax Highlighting on and off"""
        if self.nb.control.highlight:
            self.nb.control.SyntaxOnOff(ID_SYN_OFF)
            self.PushStatusText("Syntax Highlighting Off", SB_INFO)
        else:
            self.nb.control.SyntaxOnOff(ID_SYN_ON)
            self.PushStatusText("Syntax Highlighting On", SB_INFO)

        evt.Skip()

    def OnIndentGuides(self, evt):
        """Turn Indentation Guides on and off"""
        if self.settingsmenu.IsChecked(ID_INDENT_GUIDES):
            self.nb.control.IndentGuideOnOff(1)
            self.PushStatusText("Indentation Guides On", SB_INFO)
        else:
            self.nb.control.IndentGuideOnOff(0)
            self.PushStatusText("Indentation Guides Off", SB_INFO)

        evt.Skip()

    def OnHLBrackets(self, evt):
        """Turns Bracket Highlighting on and off"""
	if PROFILE['BRACKETHL']:
	    self.nb.control.Unbind(wx.stc.EVT_STC_UPDATEUI)
	    PROFILE['BRACKETHL'] = False
	    self.PushStatusText("Bracket Highlighting Off", SB_INFO)
	else:
	    self.nb.control.Bind(wx.stc.EVT_STC_UPDATEUI, self.nb.control.OnUpdateUI)
            PROFILE['BRACKETHL'] = True
	    self.PushStatusText("Bracket Highlighting On", SB_INFO)

        evt.Skip()
	    
    def OnCodeCompletion(self, evt):
        """Turn Code Completion On and Off"""
        self.nb.control.CodeCompletionOnOff()

        if self.nb.control.codecompletion:
            self.PushStatusText("Code Completion Off", SB_INFO)
        else:
            self.PushStatusText("Code Completion On", SB_INFO)

    ### Language Menu Functions
    def OnSetLexer(self, evt):
        """Manualy Set Lexer from Menu Selection"""
        lang = evt.GetId()

        # Dont trap event if it has nothing to do with languages
        if lang < 600 or lang > 699:
            evt.Skip()
            return 1

        if lang == ID_LANG_ASM:
            self.nb.control.FindLexer("asm")
        elif lang == ID_LANG_BATCH:
            self.nb.control.FindLexer("bat")
        elif lang == ID_LANG_C:
            self.nb.control.FindLexer("c")
        elif lang == ID_LANG_CPP:
            self.nb.control.FindLexer("cpp")
        elif lang == ID_LANG_CSS:
            self.nb.control.FindLexer("css")
        elif lang == ID_LANG_H:
            self.nb.control.FindLexer("h")
        elif lang == ID_LANG_HTML:
            self.nb.control.FindLexer("html")
        elif lang == ID_LANG_LISP:
            self.nb.control.FindLexer("lisp")
        elif lang == ID_LANG_MAKE:
            self.nb.control.FindLexer("makefile")
        elif lang == ID_LANG_NSIS:
            self.nb.control.FindLexer("nsi")
        elif lang == ID_LANG_PASCAL:
            self.nb.control.FindLexer("pas")
        elif lang == ID_LANG_PERL:
            self.nb.control.FindLexer("pl")
        elif lang == ID_LANG_PHP:
            self.nb.control.FindLexer("php")
        elif lang == ID_LANG_PS:
            self.nb.control.FindLexer("ps")
        elif lang == ID_LANG_PYTHON:
            self.nb.control.FindLexer("py")
        elif lang == ID_LANG_RUBY:
            self.nb.control.FindLexer("rb")
        elif lang == ID_LANG_SHELL:
            self.nb.control.FindLexer("sh")
        elif lang == ID_LANG_SQL:
            self.nb.control.FindLexer("sql")
        elif lang == ID_LANG_TEX:
            self.nb.control.FindLexer("tex")
        elif lang == ID_LANG_VHDL:
            self.nb.control.FindLexer("vhd")
        elif lang == ID_LANG_VB:
            self.nb.control.FindLexer("vb")
        else:
            evt.Skip()

        return 0

    #---- End Settings Menu Functions ----#

    #---- Help Menu Functions ----#
    def OnAbout(self, evt):
        """About"""
        dlg = util.About(self)
        dlg.ShowModal()
        dlg.Destroy()
        evt.Skip()

    #---- End Help Menu Functions ----#

    #---- Misc Function Definitions ----#
    def MenuFileTypes(self):
        """Creates a string from a list of supported filetypes for use
        in menus of dialogs such as open and saveas

        """

        filetypes = [ "All Files (*.*)|*.*|", "Assembly Files (*.asm)|*.asm|", 
                      "Batch Files (*.bat)|*.bat|", "C Files (*.c)|*.c|", 
                      "CPP Files (*.cpp)|*.cpp|", "CSS Files (*.css)|*.css|",
                      "Header Files (*.h)|*.h|", 
                      "Html Files (*.htm *.html)|*.htm *.html|",
                      "Java Files (*.java)|*.java|", "Makefiles | Makefile*|", 
                      "Lisp Files (*.lisp) |*.lisp|", "Pascal Files (*.p)|*.p|", 
                      "Perl Files (*.pl)|*.pl|", "PHP Files (*.php)|*.php|",
                      "Python Files (*.py)|*.py|", "Ruby Files (*.rb)|*.rb|", 
                      "Shell Scripts (*.sh)|*.sh *.csh *.ksh|", 
                      "SQL Files (*.sql)|*.sql|", "TeX Files (*.tex)|*.tex|", 
                      "Text Files (*.txt)|*.txt|", "Visual Basic (*.vb)|*.vb"
                   ]

        typestr = ''.join(filetypes)
        return typestr

    # Line / Column Indicator functions
    def OnKeyUp(self, evt):
        """ Update Line/Column indicator based on position """
        line, column = self.nb.control.GetPos()
        if line >= 0 and column >= 0:
            self.SetStatusText(LANG['Line'] + u": " + str(line) + "  " + 
                               LANG['Column'] + u": " + str(column), SB_ROWCOL)
        else:
            pass
	self.UpdateToolBar()
        evt.Skip()

    # Menu Helper Functions
    #TODO this is fairly stupid, write a more general solution
    def UpdateMenu(self, menu):
        """ Update Status of a Given Menu """
        menu = menu.GetMenu()
        if menu == self.languagemenu:
            lexer = self.nb.control.GetLexer()

            if lexer == wx.stc.STC_LEX_CPP or lexer == wx.stc.STC_LEX_HTML:
                file_ext = util.GetExtension(self.nb.control.filename).lower()
            else:
                file_ext = 0

            for menu_item in menu.GetMenuItems():
                item_id = menu_item.GetId()
                if menu.IsChecked(item_id):
                    if EXT_DICT[item_id] != file_ext:
                        menu.Check(item_id, 0)
                    else:
                        pass
                elif LANG_DICT[item_id] == lexer:
                    if not file_ext:
                        menu.Check(item_id, -1)
                    elif file_ext == EXT_DICT[item_id]:
                        menu.Check(item_id, -1)
                else:
                    pass
        elif menu == self.editmenu:
            if self.nb.control.CanUndo():
                menu.Enable(ID_UNDO, True)
            else:
                menu.Enable(ID_UNDO, False)

            if self.nb.control.CanRedo():
                menu.Enable(ID_REDO, True)
            else:
                menu.Enable(ID_REDO, False)

            if self.nb.control.CanPaste():
                menu.Enable(ID_PASTE, True)
            else:
                menu.Enable(ID_PASTE, False)

            sel1, sel2 = self.nb.control.GetSelection()
            if sel1 != sel2:
                menu.Enable(ID_COPY, True)
                menu.Enable(ID_CUT, True)
            else:
                menu.Enable(ID_COPY, False)
                menu.Enable(ID_CUT, False)
        elif menu == self.settingsmenu:
            if self.nb.control.codecompletion:
                menu.Check(ID_COMPLETION, -1)
            else:
                menu.Check(ID_COMPLETION, 0)

            if self.nb.control.highlight:
                menu.Check(ID_SYNTAX, -1)
            else:
                menu.Check(ID_SYNTAX, 0)

            if self.nb.control.guides:
                menu.Check(ID_INDENT_GUIDES, -1)
            else:
                menu.Check(ID_INDENT_GUIDES, 0)
        else:
            pass

        return 0

    def UpdateToolBar(self, evt=0):
        """What we need to do on a UI update"""
        # Skip the work if toolbar is invisible
        if(self.toolbar == None):
            return -1;

        if self.nb.control.CanUndo():
            self.toolbar.EnableTool(ID_UNDO, True)
        else:
            self.toolbar.EnableTool(ID_UNDO, False)

        if self.nb.control.CanRedo():
            self.toolbar.EnableTool(ID_REDO, True)
        else:
            self.toolbar.EnableTool(ID_REDO, False)

        if self.nb.control.CanPaste():
            self.toolbar.EnableTool(ID_PASTE, True)
        else:
            self.toolbar.EnableTool(ID_PASTE, False)
    #---- End Misc Functions ----#

    #TODO this is junk and needs lots of help
    def PreviewText(self):
        """Print Preview and print function"""
        mdlg = wx.MessageDialog(self, "The Document " + 
                                self.nb.control.filename +
                                "\nMust be saved before printing!" +
                                "\nThis is a current limitation that" +
                                " I hope lift later",
                                "Print Warning",
                                wx.OK | wx.ICON_INFORMATION)
        if self.nb.control.GetModify():
            mdlg.ShowModal()
            mdlg.Destroy()
        else:
            prt = printout.PrintTable(self)
            prt.SetHeader("FILE: " + self.nb.control.filename)
            file_handle = open(self.nb.control.dirname + 
                               self.nb.control.path_char + 
                               self.nb.control.filename)
            data = []
            for txt in file_handle:
                data.append(txt.strip())
                file_handle.close()
                prt.data = data
                prt.Preview()

    ### End Function Definitions ###

### End Class Definition ####

### End Script ###
