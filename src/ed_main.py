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
# FILE: ed_main.py                                                         #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
#   This module impliments the main window class of the editor. The        #
#  MainWindow consists of a a WxFrame that contains the interface to the   #
#  editor.                                                                 #
#                                                                          #
# METHODS:                                                                 #
# - __init__: Initializes the frame/menu/toolbar/statusbar/event handlers  #
# - OnNew: Handles "New" event by asking the notebook to open a new blank  #
#          page.                                                           #
# - OnOpen: Catches Open event and passes it to DoOpen                     #
# - DoOpen: Does work of opening pages/files in Frame                      #
# - OnClosePage: Handles close page event by asking notebook to close the  #
#                Currently selected page.                                  #
# - ModifySave: Called when closing page / program to prompt user and ask  #
#               if they want to save or not.                               #
# - OnSave: Saves control text to acutal file by asking the control to     #
#           write the data out to file, unless the document does not have  #
#           a name which in that case it will in turn call SaveAs          #
# - OnSaveAs: Saves current document to the file specified in the dialog.  #
# - OnPrint: Sends current controls text to printer device                 #
# - OnExit: Closes all windows, and shuts the program down.                #
# - 
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies

import os
import sys
import time
import wx
from ed_glob import *
import util
import profiler
import ed_toolbar
import ed_pages
import ed_menu
import ed_print
import ed_cmdbar
import syntax.syntax as syntax
import generator

# Function Aliases
_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class MainWindow(wx.Frame):
    """Editras Main Window"""
    def __init__(self, parent, id, wsize, title, log):
        """Initialiaze the Frame and Event Handlers"""
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=wsize,
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetTitle(title + u' - v' + version)
        self.LOG = log
  
        # Try and set an app icon
        try:
            if wx.Platform == '__WXMSW__':
                ed_icon = CONFIG['PIXMAPS_DIR'] + "editra.ico"
                self.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_ICO))
                self.LOG("[main_evt] Set Icon for Windows")
            else:
                ed_icon = CONFIG['PIXMAPS_DIR'] + "editra.png"
                self.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_PNG))
                self.LOG("[main_evt] Set Icon for " + os.sys.platform)
        finally:
            pass

        # Check if user wants Metal Style under OS X
        if wx.Platform == '__WXMAC__' and PROFILE.has_key('METAL'):
            if PROFILE['METAL']:
                self.SetExtraStyle(wx.FRAME_EX_METAL)

        #---- Sizers to hold subapplets ----#
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #---- Setup File History ----#
        self.filehistory = wx.FileHistory(int(PROFILE['FHIST_LVL']))

        #---- Toolbar ----#
        self.toolbar = None

        #---- Notebook to hold editor windows ----#
        self.nb = ed_pages.ED_Pages(self, -1, log)
        self.sizer.Add(self.nb, 6, wx.EXPAND)
        self.sizer.Layout()
        self.SendSizeEvent()
        self.SetSizer(self.sizer)

        #---- Setup Printer ----#
        self.printer = ed_print.ED_Printer(self, self.nb.GetCurrentCtrl)

        #---- Command Bar ----#
        self._cmdbar = ed_cmdbar.CommandBar(self, ID_COMMAND_BAR)
        self._cmdbar.Hide()

        #---- Status bar on bottom of window ----#
        self.CreateStatusBar(2, style=wx.ST_SIZEGRIP | wx.ST_DOTS_MIDDLE)
        self.SetStatusWidths([-1, 155])
        #---- End Statusbar Setup ----#

        #---- Create a toolbar ----#
        if PROFILE['TOOLBAR']:
            self.toolbar = ed_toolbar.ED_ToolBar(self, wx.ID_ANY)
            self.SetToolBar(self.toolbar)

        # Toolbar Event Handlers
        # TODO move to toolbar module
        self.Bind(wx.EVT_TOOL, self.DispatchToControl)
        wx.EVT_TOOL(self, ID_NEW, self.OnNew)
        wx.EVT_TOOL(self, ID_OPEN, self.OnOpen)
        wx.EVT_TOOL(self, ID_SAVE, self.OnSave)
        wx.EVT_TOOL(self, ID_PRINT, self.OnPrint)
        wx.EVT_TOOL(self, ID_FIND, self.nb.FindService.OnShowFindDlg)
        wx.EVT_TOOL(self, ID_FIND_REPLACE, self.nb.FindService.OnShowFindDlg)
        #---- End Toolbar Setup ----#

        #---- Menus ----#
        menbar = ed_menu.ED_MenuBar()
        self.filemenu = menbar.GetMenuByName("file")
        self.editmenu = menbar.GetMenuByName("edit")
        self.viewmenu = menbar.GetMenuByName("view")
        self.formatmenu = menbar.GetMenuByName("format")
        self.settingsmenu = menbar.GetMenuByName("settings")
        self.toolsmenu = menbar.GetMenuByName("tools")
        self.helpmenu = menbar.GetMenuByName("help")
        self.menubar = menbar
        self.lineformat = menbar.GetMenuByName("lineformat")

        ## Setup additional menu items
        self.filehistory.UseMenu(menbar.GetMenuByName("filehistory"))
        self.languagemenu = syntax.GenLexerMenu()
        self.settingsmenu.AppendMenu(ID_LEXER, _("Lexers"), self.languagemenu,
                                     _("Manually Set a Lexer/Syntax"))

        # On mac, do this to make help menu appear in correct location
        if wx.Platform == '__WXMAC__':
            wx.GetApp().SetMacHelpMenuTitleName(_("Help"))

        #---- Menu Bar ----#
        self.SetMenuBar(self.menubar)

        # Bind Extra key commands
  #      accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, ord('K'), ID_SHOW_KWHELPER)])
  #      self.SetAcceleratorTable(accel)

        #---- Actions to take on menu events ----#
        self.Bind(wx.EVT_MENU_OPEN, self.UpdateMenu)
        self.BindLangMenu()
        if wx.Platform == '__WXGTK__':
            self.Bind(wx.EVT_MENU_HIGHLIGHT, self.OnMenuHighlight, id=ID_LEXER)
            self.Bind(wx.EVT_MENU_HIGHLIGHT, self.OnMenuHighlight, id=ID_EOL_MODE)

        # File Menu Events
        self.Bind(wx.EVT_MENU, self.OnNew, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnClosePage, id=ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnSave, id=ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSaveProfile, id=ID_SAVE_PROFILE)
        self.Bind(wx.EVT_MENU, self.OnLoadProfile, id=ID_LOAD_PROFILE)
        self.Bind(wx.EVT_MENU, self.OnPrint)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU_RANGE, self.OnFileHistory, 
                  id=wx.ID_FILE1, id2=wx.ID_FILE9)

        # Edit Menu Events
        self.Bind(wx.EVT_MENU, self.DispatchToControl)
        self.Bind(wx.EVT_MENU, self.nb.FindService.OnShowFindDlg, id=ID_FIND)
        self.Bind(wx.EVT_MENU, self.nb.FindService.OnShowFindDlg, id=ID_FIND_REPLACE)
        self.Bind(wx.EVT_MENU, self.OnQuickFind, id=ID_QUICK_FIND)
        self.Bind(wx.EVT_MENU, self.OnPreferences, id=ID_PREF)

        # View Menu Events
        self.Bind(wx.EVT_MENU, self.OnGoto, id=ID_GOTO_LINE)
        self.Bind(wx.EVT_MENU, self.OnViewTb, id=ID_VIEW_TOOL)

        # Format Menu Events
        self.Bind(wx.EVT_MENU, self.OnFont, id=ID_FONT)

        # Tool Menu
        self.Bind(wx.EVT_MENU, self.OnStyleEdit, id=ID_STYLE_EDIT)
        self.Bind(wx.EVT_MENU, self.OnGenHtml, id=ID_HTML_GEN)

        # Help Menu Events
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=ID_HOMEPAGE)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=ID_CONTACT)

        #---- End Menu Setup ----#

        #---- Actions to Take on other Events ----#
        # Frame
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        # Find Dialog
        self.Bind(wx.EVT_FIND, self.nb.FindService.OnFind)
        self.Bind(wx.EVT_FIND_NEXT, self.nb.FindService.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE, self.nb.FindService.OnFind)
        self.Bind(wx.EVT_FIND_REPLACE_ALL, self.nb.FindService.OnFind)
        self.Bind(wx.EVT_FIND_CLOSE, self.nb.FindService.OnFindClose)

        #---- End other event actions ----#

        #---- Final Setup Calls ----#
        self.LoadFileHistory(int(PROFILE['FHIST_LVL']))
        self.UpdateToolBar()

        #---- Check for commandline args ----#
        for arg in sys.argv[1:]:
            try:
                if arg != "" and arg[0] != "-":
                    self.DoOpen(ID_COMMAND_LINE_OPEN, arg)
                else:
                    break
            except IndexError:
                self.LOG("[main] [exception] Trapped Commandline IndexError on Init")
                pass

        #---- Show the Frame ----#
        if PROFILE.has_key('ALPHA'):
            self.SetTransparent(PROFILE['ALPHA'])
        if PROFILE['SET_WPOS'] and PROFILE.has_key('WPOS') and \
          isinstance(PROFILE['WPOS'], tuple) and len(PROFILE['WPOS']) == 2:
            self.SetPosition(PROFILE['WPOS'])
        else:
            self.CenterOnParent()
        self.Show(True)

    ### End Init ###

    ### Begin Function Definitions ###
    def DoOpen(self, evt, file_name=''):
        """ Do the work of opening a file and placing it
        in a new notebook page.

        """
        dlg = wx.FileDialog(self, _("Choose a File"), '', "", 
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
            self.LOG("[main_info] CMD Open File: " + file_name)
            filename = util.GetFileName(file_name)
            dirname = util.GetPathName(file_name)
            self.nb.OpenPage(dirname, filename)

    def LoadFileHistory(self, size):
        """Loads file history from profile"""
        file_key = "FILE"
        i = size - 1 
        while i >= 0:
            key = file_key + str(i)
            try:
                self.filehistory.AddFileToHistory(PROFILE[key])
            except KeyError: 
                self.LOG("[main] [exception] Invalid Key on LoadFileHistory")
                pass
            i -= 1

        return size - i

    def OnNew(self, evt):
        """New File"""
        self.nb.NewPage()
        self.nb.GoCurrentPage()
        self.UpdateToolBar()

    def OnOpen(self, evt):
        """Open File"""
        self.DoOpen(evt)
        self.UpdateToolBar()

    def OnFileHistory(self, evt):
        """ Open a File from the File History """
        fileNum = evt.GetId() - wx.ID_FILE1
        file_handle = self.filehistory.GetHistoryFile(fileNum)

        # Check if file still exists
        if not os.path.exists(file_handle):
            mdlg = wx.MessageDialog(self, _("%s could not be found\nPerhaps "
                                            "its been moved or deleted") % \
                                    file_handle, _("File Not Found"),
                                    wx.OK | wx.ICON_WARNING)
            mdlg.CenterOnParent()
            mdlg.ShowModal()
            mdlg.Destroy()
            # Remove offending file from history
            self.filehistory.RemoveFileFromHistory(fileNum)
        else:
            self.DoOpen(evt, file_handle)

    def OnClosePage(self, evt):
        """Close a page"""
        self.nb.ClosePage()

    def OnSave(self, evt):
        """Save"""
        fname = self.nb.control.filename
        if fname != '':
            result = self.nb.control.Save()
            if result == wx.ID_OK:
                self.PushStatusText(_("Saved File: %s") % fname, SB_INFO)
            else:
                self.PushStatusText(_("ERROR: Failed to save %s") % fname, SB_INFO)
                dlg = wx.MessageDialog(self, _("Failed to save file: %s\n\nError:\n%d") % 
                                                (fname, result), _("Save Error"),
                                        wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            ret_val = self.OnSaveAs(ID_SAVEAS)
            if ret_val == wx.ID_OK:
                self.filehistory.AddFileToHistory(os.path.join(self.nb.control.dirname, 
                                                              self.nb.control.filename))
        self.UpdateToolBar()

    def OnSaveAs(self, evt):
        """Save As"""
        self.dirname = ''
        dlg = wx.FileDialog(self, _("Choose a Save Location"), self.dirname, "", 
                            self.MenuFileTypes(), wx.SAVE|wx.OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        if result == wx.ID_OK: 
            path = dlg.GetPath()
            result = self.nb.control.SaveAs(path)
            fname = self.nb.control.filename
            if result != wx.ID_OK:
                dlg = wx.MessageDialog(self, _("Failed to save file: %s\n\nError:\n%d") % 
                                                (fname, result), _("Save Error"),
                                        wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.PushStatusText(_("ERROR: Failed to save %s") % fname, SB_INFO)
            else:
                self.PushStatusText(_("Saved File As: %s") % fname, SB_INFO)
                self.SetTitle(fname + u" - file://" + self.nb.control.dirname + 
                              self.nb.control.path_char + fname + " - " + 
                              prog_name + u" v" + version)
                self.nb.SetPageText(self.nb.GetSelection(), fname)
                self.nb.UpdatePageImage()
            return result
        else:
            pass

    def OnSaveProfile(self, evt):
        """Saves current settings as a profile"""
        dlg = wx.FileDialog(self, _("Where to Save Profile?"), CONFIG['PROFILE_DIR'], 
                            "default.pp", _("Profile") + " (*.pp)|*.pp", 
                            wx.SAVE | wx.OVERWRITE_PROMPT)

        result = dlg.ShowModal()
        if result == wx.ID_OK: 
            profile = dlg.GetFilename()
            path = dlg.GetPath()
            profiler.WriteProfile(path)
            self.PushStatusText(_("Profile Saved as: %s") % profile, SB_INFO)
            dlg.Destroy()
        else:
            pass

    def OnLoadProfile(self, evt):
        """Loads a profile"""
        dlg = wx.FileDialog(self, _("Load a Custom Profile"), CONFIG['PROFILE_DIR'], 
                            "default.pp", _("Profile") + " (*.pp)|*.pp", wx.OPEN)

        result = dlg.ShowModal()
        if result == wx.ID_OK: 
            profile = dlg.GetFilename()
            path = dlg.GetPath()
            profiler.ReadProfile(path)
            self.PushStatusText(_("Loaded Profile: %s") % profile, SB_INFO)
            dlg.Destroy()
        else:
            pass

        # Update editor to reflect loaded profile
        self.nb.UpdateTextControls()

    def OnPrint(self, evt):
        """Handles printing related events"""
        e_id = evt.GetId()
        pmode = PROFILE['PRINT_MODE'].replace(u'/', u'_').lower()
        self.printer.SetColourMode(pmode)
        if e_id == ID_PRINT:
           self.printer.Print()
        elif e_id == ID_PRINT_PRE:
           self.printer.Preview()
        elif e_id == ID_PRINT_SU:
           self.printer.PageSetup()
        else:
           evt.Skip()

    def OnExit(self, evt):
        """Exit"""
        # This event is bound at two location need to unbind it to avoid fireing
        # the event again
        self.Unbind(wx.EVT_CLOSE)

        # Cleanup Controls
        controls = self.nb.GetPageCount()
        self.LOG("[main_evt] [exit] Number of controls: " + str(controls))

        while controls:
            if controls <= 0:
                self.Close(True)

            self.LOG("[main_evt] [exit] Requesting Page Close")
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
            self.LOG("[main_evt] [exit] [exception] Trapped UnboundLocalError OnExit")
            pass

        ### If we get to here there is no turning back so cleanup
        ### additional items and save the user settings
        
        self.nb.DocMgr.WriteBook()

        # Save Window Size/Position for next launch
        #HACK workaround for possible bug in wxPython 2.8
        if wx.Platform == '__WXMAC__' and self.GetToolBar():
            self.toolbar.Destroy()
        PROFILE['WSIZE'] = self.GetSize()
        PROFILE['WPOS'] = self.GetPosition()
        self.LOG("[main_evt] [exit] Closing editor at pos=" + 
                        str(PROFILE['WPOS']) + " size=" + str(PROFILE['WSIZE']))
        
        # Update profile
        profiler.UpdateProfileLoader()
        profiler.AddFileHistoryToProfile(self.filehistory)
        profiler.WriteProfile(PROFILE['MYPROFILE'])

        # Cleanup file history
        try:
            del self.filehistory
        except AttributeError:
            self.LOG("[main_evt] [exit] [exception] Trapped AttributeError OnExt")
            pass
        self._cmdbar.Destroy()

        # Finally close the application
        self.LOG("[main_info] Exiting MainLoop...")
        if CONFIG.has_key('DL_IS_BUSY') and CONFIG['DL_IS_BUSY']:
            self.LOG("[main_info] Download is in progress...")
            self.LOG("[main_info] Frame will exit now but app will remain running")
            CONFIG['FRAME_HAS_EXITED'] = True
            self.Destroy()
        else:
            wx.Exit()

    #---- End File Menu Functions ----#

    #---- Edit Menu Functions ----#
    def OnPreferences(self, evt):
        """Open the Preference Panel"""
        # Import dialog if now since we need it
        import prefdlg
        dlg = prefdlg.PrefDlg(self, self.LOG)
        dlg.CenterOnParent()
        dlg.ShowModal()
        dlg.Destroy()
    #---- End Edit Menu Functions ----#

    #---- View Menu Functions ----#
    def OnGoto(self, evt):
        """Shows the Goto Line control"""
        e_id = evt.GetId()
        if e_id == ID_GOTO_LINE:
            self._cmdbar.Show(ed_cmdbar.ID_LINE_CTRL)
            self.sizer.Layout()
        else:
            evt.Skip()

    def OnViewTb(self, evt):
        """Toggles visibility of toolbar"""
        if PROFILE['TOOLBAR'] and self.toolbar != None:
            self.toolbar.Destroy()
            del self.toolbar
            PROFILE['TOOLBAR'] = False
        else:
            self.toolbar = ed_toolbar.ED_ToolBar(self, wx.ID_ANY)
            self.SetToolBar(self.toolbar)
            PROFILE['TOOLBAR'] = True
            self.UpdateToolBar()
    #---- End View Menu Functions ----#

    #---- Format Menu Functions ----#
    def OnFont(self, evt):
        """Font"""
        #TODO this is a quick stubin finish me later
        dlg = wx.FontDialog(self, wx.FontData())
        result = dlg.ShowModal()
        data = dlg.GetFontData()

        if result == wx.ID_OK:
            font = data.GetChosenFont()
            self.nb.control.SetGlobalFont(self.nb.control.FONT_TAG_MONO, font.GetFaceName())
            self.nb.control.UpdateAllStyles()
        dlg.Destroy()

    #---- End Format Menu Functions ----#

    #---- Tools Menu Functions ----#
    def OnStyleEdit(self, evt):
        """Opens the style editor and handles the setting of
        the return data.

        """
        import style_editor
        dlg = style_editor.StyleEditor(self, log=self.LOG)
        dlg.CenterOnParent()
        dlg.ShowModal()
        dlg.Destroy()

    def OnGenHtml(self, evt):
        """Generates html and opens the generated code in a new page"""
        html = generator.Html(self.nb.GetCurrentCtrl())
        self.nb.NewPage()
        self.nb.control.SetText(unicode(html))
        self.nb.control.FindLexer('html')

    #---- Help Menu Functions ----#
    def OnAbout(self, evt):
        """About"""
        info = wx.AboutDialogInfo()
        year = time.localtime()
        desc = ["Editra is a programmers text editor.",
                "Written in 100%% Python.",
                "Homepage: " + home_page + "\n",
                "Platform Info: (python %s,%s)", 
                "License: GPL v2 (see COPYING.txt for full license)"]
        desc = "\n".join(desc)
        py_version = sys.version.split()[0]
        platform = list(wx.PlatformInfo[1:])
        platform[0] += (" " + wx.VERSION_STRING)
        wx_info = ", ".join(platform)
        info.SetCopyright("Copyright(C) 2005-%d Cody Precord" % year[0])
        info.SetName(prog_name.title())
        info.SetDescription(desc % (py_version, wx_info))
        info.SetVersion(version)
        about = wx.AboutBox(info)
        del about

    def OnHelp(self, evt):
        """Handles the majority of the help menu functions"""
        import webbrowser
        e_id = evt.GetId()
        if e_id == ID_HOMEPAGE:
            webbrowser.open(home_page, 1)
        elif e_id == ID_CONTACT:
            webbrowser.open(u'mailto:%s' % contact_mail)
        else:
            evt.Skip()

    #---- End Help Menu Functions ----#

    #---- Misc Function Definitions ----#
    def MenuFileTypes(self):
        """Creates a string from a list of supported filetypes for use
        in menus of dialogs such as open and saveas

        """
        filefilters = syntax.GenFileFilters()
        typestr = ''.join(filefilters)
        return typestr

    def DispatchToControl(self, evt):
        """Catches control events and passes them to the text control
        as necessary.

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        e_type = evt.GetEventType()
        menu_ids = syntax.SyntaxIds()
        menu_ids.extend([ID_SHOW_EOL, ID_SHOW_WS, ID_INDENT_GUIDES, ID_SYNTAX,
                         ID_KWHELPER, ID_WORD_WRAP, ID_BRACKETHL, ID_ZOOM_IN,
                         ID_ZOOM_OUT, ID_ZOOM_NORMAL, ID_EOL_MAC, ID_EOL_UNIX,
                         ID_EOL_WIN, ID_JOIN_LINES, ID_CUT_LINE, ID_COPY_LINE,
                         ID_INDENT, ID_UNINDENT, ID_TRANSPOSE, ID_NEXT_MARK,
                         ID_PRE_MARK, ID_ADD_BM, ID_DEL_BM, ID_DEL_ALL_BM,
                         ID_FOLDING, ID_AUTOCOMP, ID_SHOW_LN, ID_COMMENT,
                         ID_UNCOMMENT, ID_AUTOINDENT, ID_LINE_AFTER,
                         ID_LINE_BEFORE])
        if e_id in [ID_UNDO, ID_REDO, ID_CUT, ID_COPY, ID_PASTE, ID_SELECTALL]:
            # If event is from the toolbar manually send it to the control as
            # the events from the toolbar do not propagate to the control.
            if e_obj.GetClassName() == "wxToolBar" or e_id in [ID_REDO, ID_UNDO] \
               or wx.Platform == '__WXMSW__':
                self.nb.control.ControlDispatch(evt)
                self.UpdateToolBar()
            else:
                evt.Skip()
        elif e_id in menu_ids:
            self.nb.control.ControlDispatch(evt)
        else:
            evt.Skip()
        return

    def OnKeyUp(self, evt):
        """ Update Line/Column indicator based on position """
        line, column = self.nb.control.GetPos(evt)
        if line >= 0 and column >= 0:
            self.SetStatusText(_("Line: %d  Column: %d") % (line, column), SB_ROWCOL)
            self.UpdateToolBar()

    def OnMenuHighlight(self, evt):
        """HACK for GTK, submenus dont seem to fire a EVT_MENU_OPEN
        but do fire a MENU_HIGHLIGHT

        """
        if evt.GetId() == ID_LEXER:
            self.UpdateMenu(self.languagemenu)
        elif evt.GetId() == ID_EOL_MODE:
            self.UpdateMenu(self.lineformat)
        else:
            evt.Skip()

    def BindLangMenu(self):
        """Binds Language Menu Ids to event handler"""
        for l_id in syntax.SyntaxIds():
            self.Bind(wx.EVT_MENU, self.DispatchToControl, id=l_id)

    def OnQuickFind(self, evt):
        self._cmdbar.Show(ed_cmdbar.ID_SEARCH_CTRL)
        self.sizer.Layout()

    # Menu Helper Functions
    #TODO this is fairly stupid, write a more general solution
    def UpdateMenu(self, evt):
        """ Update Status of a Given Menu """
        menu2 = None
        if evt.GetClassName() == "wxMenuEvent":
            menu = evt.GetMenu()
            # HACK MSW GetMenu returns None on submenu open events
            if menu == None:
                menu = self.languagemenu
                menu2 = self.lineformat
        else:
            menu = evt

        if menu == self.languagemenu:
            self.LOG("[main_evt] Updating Settings/Lexer Menu")
            lang_id = self.nb.control.lang_id
            for menu_item in menu.GetMenuItems():
                item_id = menu_item.GetId()
                if menu.IsChecked(item_id):
                    menu.Check(item_id, False)
                if item_id == lang_id or \
                   (menu_item.GetLabel() == 'Plain Text' and lang_id == 0):
                    menu.Check(item_id, True)
            # HACK real ugly needed for MSW
            if menu2 != None:
                self.LOG("[menu_evt] Updating EOL Mode Menu")
                eol = self.nb.control.GetEOLModeId()
                for id in [ID_EOL_MAC, ID_EOL_UNIX, ID_EOL_WIN]:
                    menu2.Check(id, eol == id)
        elif menu == self.editmenu:
            self.LOG("[main_evt] Updating Edit Menu")
            menu.Enable(ID_UNDO, self.nb.control.CanUndo())
            menu.Enable(ID_REDO, self.nb.control.CanRedo())
            menu.Enable(ID_PASTE, self.nb.control.CanPaste())
            sel1, sel2 = self.nb.control.GetSelection()
            menu.Enable(ID_COPY, sel1 != sel2)
            menu.Enable(ID_CUT, sel1 != sel2)
        elif menu == self.settingsmenu:
            self.LOG("[menu_evt] Updating Settings Menu")
            menu.Check(ID_AUTOCOMP, self.nb.control.GetAutoComplete())
            menu.Check(ID_AUTOINDENT, self.nb.control.GetAutoIndent())
            menu.Check(ID_KWHELPER, self.nb.control.kwhelp)
            menu.Check(ID_SYNTAX, self.nb.control.highlight)
            menu.Check(ID_FOLDING, self.nb.control.folding)
            menu.Check(ID_BRACKETHL, self.nb.control.brackethl)
        elif menu == self.viewmenu:
            zoom = self.nb.control.GetZoom()
            self.LOG("[menu_evt] Updating View Menu: zoom = " + str(zoom))
            if zoom == 0:
                self.viewmenu.Enable(ID_ZOOM_NORMAL, False)
                self.viewmenu.Enable(ID_ZOOM_IN, True)
                self.viewmenu.Enable(ID_ZOOM_OUT, True)
            elif zoom > 18:
                self.viewmenu.Enable(ID_ZOOM_NORMAL, True)
                self.viewmenu.Enable(ID_ZOOM_IN, False)
                self.viewmenu.Enable(ID_ZOOM_OUT, True)
            elif zoom < -8:
                self.viewmenu.Enable(ID_ZOOM_NORMAL, True)
                self.viewmenu.Enable(ID_ZOOM_IN, True)
                self.viewmenu.Enable(ID_ZOOM_OUT, False)
            else:
                self.viewmenu.Enable(ID_ZOOM_NORMAL, True)
                self.viewmenu.Enable(ID_ZOOM_IN, True)
                self.viewmenu.Enable(ID_ZOOM_OUT, True)
            menu.Check(ID_SHOW_WS, bool(self.nb.control.GetViewWhiteSpace()))
            menu.Check(ID_SHOW_EOL, bool(self.nb.control.GetViewEOL()))
            menu.Check(ID_SHOW_LN, bool(self.nb.control.GetMarginWidth(1)))
            menu.Check(ID_INDENT_GUIDES, bool(self.nb.control.GetIndentationGuides()))
            menu.Check(ID_VIEW_TOOL, hasattr(self, 'toolbar'))
        elif menu == self.formatmenu:
            self.LOG("[menu_evt] Updating Format Menu")
            menu.Check(ID_WORD_WRAP, bool(self.nb.control.GetWrapMode()))
        elif menu == self.lineformat:
            self.LOG("[menu_evt] Updating EOL Mode Menu")
            eol = self.nb.control.GetEOLModeId()
            for id in [ID_EOL_MAC, ID_EOL_UNIX, ID_EOL_WIN]:
                menu.Check(id, eol == id)
        else:
            pass
        return 0

    def UpdateToolBar(self, evt=0):
        """Update Tool Status"""
        if not hasattr(self, 'toolbar') or self.toolbar == None:
            return -1;
        self.toolbar.EnableTool(ID_UNDO, self.nb.control.CanUndo())
        self.toolbar.EnableTool(ID_REDO, self.nb.control.CanRedo())
        self.toolbar.EnableTool(ID_PASTE, self.nb.control.CanPaste())

    def ModifySave(self):
        """Called when document has been modified prompting
        a message dialog asking if the user would like to save
        the document before closing.

        """
        if self.nb.control.filename == "":
            name = self.nb.GetPageText(self.nb.GetSelection())
        else:
            name = self.nb.control.filename

        dlg = wx.MessageDialog(self, 
                                _("The file: \"%s\" has been modified since the last "
                                  "save point.\n Would you like to save the changes?") % name, 
                               _("Save Changes?"), 
                               wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            self.OnSave(ID_SAVE)

        return result
    #---- End Misc Functions ----#

    ### End Function Definitions ###
