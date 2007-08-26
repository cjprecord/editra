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
# @author: Cody Precord                                                    #
# LANGUAGE: Python                                                         #
#                                                                          #
# @summary:                                                                #
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

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies

import os
import sys
import time
import wx
import wx.aui
from ed_glob import *
import util
from profiler import Profile_Get as _PGET
from profiler import Profile_Set as _PSET
import profiler
import ed_toolbar
import ed_event
import ed_pages
import ed_menu
import ed_print
import ed_cmdbar
import syntax.syntax as syntax
import generator
import plugin
import perspective as viewmgr
import iface

# Function Aliases
_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class MainWindow(wx.Frame, viewmgr.PerspectiveManager):
    """Editras Main Window
    @todo: modularize the event handling more (pubsub?)

    """
    def __init__(self, parent, id_, wsize, title):
        """Initialiaze the Frame and Event Handlers.
        @note: Automatically calls Show at the end of __init__

        """
        wx.Frame.__init__(self, parent, id_, title, size=wsize,
                          style=wx.DEFAULT_FRAME_STYLE)

        self._mgr = wx.aui.AuiManager(flags=wx.aui.AUI_MGR_DEFAULT | \
                                      wx.aui.AUI_MGR_TRANSPARENT_DRAG | \
                                      wx.aui.AUI_MGR_TRANSPARENT_HINT)
        self._mgr.SetManagedWindow(self)
        viewmgr.PerspectiveManager.__init__(self, self._mgr, \
                                            CONFIG['CACHE_DIR'])

        self.SetTitle()
        self.LOG = wx.GetApp().GetLog()
  
        # Try and set an app icon 
        util.SetWindowIcon(self)

        # Check if user wants Metal Style under OS X
        if wx.Platform == '__WXMAC__' and _PGET('METAL'):
            self.SetExtraStyle(wx.FRAME_EX_METAL)

        #---- Sizers to hold subapplets ----#
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #---- Setup File History ----#
        self.filehistory = wx.FileHistory(_PGET('FHIST_LVL', 'int', 5))

        #---- Toolbar ----#
        self.toolbar = None

        #---- Notebook to hold editor windows ----#
        self.edit_pane = wx.Panel(self, wx.ID_ANY)
        self.nb = ed_pages.EdPages(self.edit_pane, wx.ID_ANY)
        self.edit_pane.nb = self.nb
        self.sizer.Add(self.nb, 1, wx.EXPAND)
        self.sizer.Layout()
        self.edit_pane.SendSizeEvent()
        self.edit_pane.SetSizer(self.sizer)
        self.Layout()
        self._mgr.AddPane(self.edit_pane, wx.aui.AuiPaneInfo(). \
                          Name("EditPane").Center().Layer(1).Dockable(False). \
                          CloseButton(False).MaximizeButton(False). \
                          CaptionVisible(False))
        #---- Setup Printer ----#
        self.printer = ed_print.EdPrinter(self, self.nb.GetCurrentCtrl)

        #---- Command Bar ----#
        self._cmdbar = ed_cmdbar.CommandBar(self.edit_pane, ID_COMMAND_BAR)
        self._cmdbar.Hide()

        #---- Status bar on bottom of window ----#
        self.CreateStatusBar(3, style = wx.ST_SIZEGRIP | wx.ST_DOTS_MIDDLE)
        self.SetStatusWidths([-1, 120, 155])
        #---- End Statusbar Setup ----#

        #---- Create a toolbar ----#
        if _PGET('TOOLBAR'):
            self.toolbar = ed_toolbar.EdToolBar(self, wx.ID_ANY)
            self.SetToolBar(self.toolbar)

        # Toolbar Event Handlers
        # TODO move to toolbar module
        self.Bind(wx.EVT_TOOL, self.DispatchToControl)
        self.Bind(wx.EVT_TOOL, self.OnNew, id=ID_NEW)
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=ID_OPEN)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=ID_SAVE)
        self.Bind(wx.EVT_TOOL, self.OnPrint, id=ID_PRINT)
        self.Bind(wx.EVT_TOOL, self.nb.FindService.OnShowFindDlg, id=ID_FIND)
        self.Bind(wx.EVT_TOOL, self.nb.FindService.OnShowFindDlg, \
                  id=ID_FIND_REPLACE)
        #---- End Toolbar Setup ----#

        #---- Menus ----#
        menbar = ed_menu.EdMenuBar()
        self.filemenu = menbar.GetMenuByName("file")
        self.editmenu = menbar.GetMenuByName("edit")
        self.viewmenu = menbar.GetMenuByName("view")
        self.vieweditmenu = menbar.GetMenuByName("viewedit")
        self.viewmenu.InsertMenu(5, ID_PERSPECTIVES, _("Perspectives"), 
                                 self.GetPerspectiveControls())
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

        #---- Actions to take on menu events ----#
        self.Bind(wx.EVT_MENU_OPEN, self.UpdateMenu)
        self.BindLangMenu()
        if wx.Platform == '__WXGTK__':
            self.Bind(wx.EVT_MENU_HIGHLIGHT, \
                      self.OnMenuHighlight, id=ID_LEXER)
            self.Bind(wx.EVT_MENU_HIGHLIGHT, \
                      self.OnMenuHighlight, id=ID_EOL_MODE)

        # File Menu Events
        self.Bind(wx.EVT_MENU, self.OnNew, id=ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnClosePage, id=ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnClosePage, id=ID_CLOSEALL)
        self.Bind(wx.EVT_MENU, self.OnSave, id=ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnSave, id=ID_SAVEALL)
        self.Bind(wx.EVT_MENU, self.OnSaveProfile, id=ID_SAVE_PROFILE)
        self.Bind(wx.EVT_MENU, self.OnLoadProfile, id=ID_LOAD_PROFILE)
        self.Bind(wx.EVT_MENU, self.OnPrint)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)
        self.Bind(wx.EVT_MENU_RANGE, self.OnFileHistory, 
                  id=wx.ID_FILE1, id2=wx.ID_FILE9)

        # Edit Menu Events
        self.Bind(wx.EVT_MENU, self.DispatchToControl)
        self.Bind(wx.EVT_MENU, self.nb.FindService.OnShowFindDlg, id=ID_FIND)
        self.Bind(wx.EVT_MENU, self.nb.FindService.OnShowFindDlg, 
                  id=ID_FIND_REPLACE)
        self.Bind(wx.EVT_MENU, self.OnQuickFind, id=ID_QUICK_FIND)
        self.Bind(wx.EVT_MENU, self.OnPreferences, id=ID_PREF)

        # View Menu Events
        self.Bind(wx.EVT_MENU, self.OnGoto, id=ID_GOTO_LINE)
        self.Bind(wx.EVT_MENU, self.OnViewTb, id=ID_VIEW_TOOL)

        # Format Menu Events
        self.Bind(wx.EVT_MENU, self.OnFont, id=ID_FONT)

        # Tool Menu
        self.Bind(wx.EVT_MENU, self.OnStyleEdit, id=ID_STYLE_EDIT)
        self.Bind(wx.EVT_MENU, self.OnPluginMgr, id=ID_PLUGMGR)
        self.Bind(wx.EVT_MENU, self.OnGenerate)

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
        self._exiting = False
        self.LoadFileHistory(_PGET('FHIST_LVL', fmt='int'))
        self.UpdateToolBar()

        #---- Set Position and Size ----#
        self.SetTransparent(_PGET('ALPHA', default=255))
        if _PGET('SET_WPOS') and _PGET('WPOS', "size_tuple", False):
            self.SetPosition(_PGET('WPOS'))
        else:
            self.CenterOnParent()

        # Call add on plugins
        self.LOG("[main][info] Loading MainWindow Plugins ")
        plgmgr = wx.GetApp().GetPluginManager()
        addons = MainWindowAddOn(plgmgr)
        addons.Init(self)
        self._shelf = iface.Shelf(plgmgr)
        self._shelf.Init(self)
        self.LOG("[main][info] Loading Generator plugins")
        self._generator = generator.Generator(plgmgr)
        self._generator.InstallMenu(self.toolsmenu)

        # Load Session Data
        if _PGET('SAVE_SESSION', 'bool', False):
            self.nb.LoadSessionFiles()

        # Set Perspective
        self.SetPerspective(_PGET('DEFAULT_VIEW'))
        self._mgr.Update()
        self.Show(True)

    __name__ = u"MainWindow"

    ### End Private Member Functions/Variables ###

    ### Begin Public Function Definitions ###
    def DoOpen(self, evt, fname=u''):
        """ Do the work of opening a file and placing it
        in a new notebook page.
        @param fname: can be optionally specified to open
                      a file without opening a FileDialog
        @type fname: string

        """
        result = wx.ID_CANCEL
        try:
            e_id = evt.GetId()
        except AttributeError:
            e_id = evt

        if e_id == ID_OPEN:
            dlg = wx.FileDialog(self, _("Choose a File"), '', "", 
                                self.MenuFileTypes(), wx.OPEN | wx.MULTIPLE)
            dlg.SetFilterIndex(_PGET('FFILTER', 'int', 0))
            if dlg.ShowModal() == wx.ID_OK:
                paths = dlg.GetPaths()
                dlg.Destroy()
                result = dlg.GetReturnCode()

            _PSET('FFILTER', dlg.GetFilterIndex())
            if result != wx.ID_CANCEL:
                for path in paths:
                    dirname = util.GetPathName(path)
                    filename = util.GetFileName(path)
                    self.nb.OpenPage(dirname, filename)		   
                    self.SetTitle("%s - file://%s/%s" % \
                                  (filename, dirname, filename))
                    self.nb.GoCurrentPage()
            else:
                pass
        else:
            self.LOG("[main_info] CMD Open File: %s" % fname)
            filename = util.GetFileName(fname)
            dirname = util.GetPathName(fname)
            self.nb.OpenPage(dirname, filename)

    def GetFrameManager(self):
        """Returns the manager for this frame
        @return: Reference to the AuiMgr of this window

        """
        return self._mgr

    def IsExiting(self):
        """Returns whether the windows is in the process of exiting
        or not.
        @return: boolean stating if the window is exiting or not

        """
        return self._exiting

    def LoadFileHistory(self, size):
        """Loads file history from profile
        @return: None

        """
        file_key = "FILE"
        keys = range(size - 1)
        keys.reverse()
        for i in keys:
            key = file_key + str(i)
            path = _PGET(key, "str")
            if isinstance(path, basestring) and path != wx.EmptyString:
                self.filehistory.AddFileToHistory(path)
            else:
                pass

    def OnNew(self, evt):
        """Star a New File
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_NEW:
            self.nb.NewPage()
            self.nb.GoCurrentPage()
            self.UpdateToolBar()
        else:
            evt.Skip()

    def OnOpen(self, evt):
        """Open a File
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_OPEN:
            self.DoOpen(evt)
            self.UpdateToolBar()
        else:
            evt.SkipId()

    def OnFileHistory(self, evt):
        """Open a File from the File History
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        fnum = evt.GetId() - wx.ID_FILE1
        file_h = self.filehistory.GetHistoryFile(fnum)

        # Check if file still exists
        if not os.path.exists(file_h):
            mdlg = wx.MessageDialog(self, _("%s could not be found\nPerhaps "
                                            "its been moved or deleted") % \
                                    file_h, _("File Not Found"),
                                    wx.OK | wx.ICON_WARNING)
            mdlg.CenterOnParent()
            mdlg.ShowModal()
            mdlg.Destroy()
            # Remove offending file from history
            self.filehistory.RemoveFileFromHistory(fnum)
        else:
            self.DoOpen(evt, file_h)

    def OnClosePage(self, evt):
        """Close a page
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        if e_id == ID_CLOSE:
            self.nb.ClosePage()
        elif e_id == ID_CLOSEALL:
            # XXX maybe warn and ask if they really want to close
            #     all pages before doing it.
            self.nb.CloseAllPages()
        else:
            evt.Skip()

    def OnSave(self, evt):
        """Save Current or All Buffers
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        ctrls = list()
        if e_id == ID_SAVE:
            ctrls = [(self.nb.GetPageText(self.nb.GetSelection()), 
                     self.nb.GetCurrentCtrl())]
        elif e_id == ID_SAVEALL:
            for page in range(self.nb.GetPageCount()):
                if issubclass(self.nb.GetPage(page).__class__, 
                                           wx.stc.StyledTextCtrl):
                    ctrls.append((self.nb.GetPageText(page), 
                                  self.nb.GetPage(page)))
        else:
            evt.Skip()
            return
        for ctrl in ctrls:
            fname = ctrl[1].filename
            if fname != '':
                fpath = os.path.join(ctrl[1].dirname, ctrl[1].filename)
                result = ctrl[1].SaveFile(fpath)
                if result:
                    self.PushStatusText(_("Saved File: %s") % fname, SB_INFO)
                else:
                    self.PushStatusText(_("ERROR: Failed to save %s") % fname, SB_INFO)
                    dlg = wx.MessageDialog(self, 
                                           _("Failed to save file: %s\n\nError:\n%d") % \
                                             (fname, result), _("Save Error"),
                                            wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
            else:
                ret_val = self.OnSaveAs(ID_SAVEAS, ctrl[0], ctrl[1])
                if ret_val:
                    fpath = os.path.join(ctrl[1].dirname, ctrl[1].filename)
                    self.filehistory.AddFileToHistory(fpath)
        self.UpdateToolBar()

    def OnSaveAs(self, evt, title=u'', page=None):
        """Save File Using a new/different name
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        dlg = wx.FileDialog(self, _("Choose a Save Location"), u'', 
                            title.lstrip(u"*"), self.MenuFileTypes(), 
                            wx.SAVE | wx.OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            path = dlg.GetPath()
            if page:
                ctrl = page
            else:
                ctrl = self.nb.GetCurrentCtrl()
            result = ctrl.SaveFile(path)
            fname = ctrl.filename
            if not result:
                dlg = wx.MessageDialog(self, _("Failed to save file: %s\n\nError:\n%d") % 
                                                (fname, result), _("Save Error"),
                                        wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.PushStatusText(_("ERROR: Failed to save %s") % fname, SB_INFO)
            else:
                self.PushStatusText(_("Saved File As: %s") % fname, SB_INFO)
                self.SetTitle(u"%s - file://%s%s%s" % \
                              (fname, ctrl.dirname, util.GetPathChar(), fname))
                self.nb.SetPageText(self.nb.GetSelection(), fname)
                self.nb.GetCurrentCtrl().FindLexer()
                self.nb.UpdatePageImage()
            return result
        else:
            pass

    def OnSaveProfile(self, evt):
        """Saves current settings as a profile
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_SAVE_PROFILE:
            dlg = wx.FileDialog(self, _("Where to Save Profile?"), \
                               CONFIG['PROFILE_DIR'], "default.ppb", \
                               _("Profile") + " (*.ppb)|*.ppb", 
                                wx.SAVE | wx.OVERWRITE_PROMPT)

            result = dlg.ShowModal()
            if result == wx.ID_OK: 
                profile = dlg.GetFilename()
                path = dlg.GetPath()
                profiler.Profile().Write(path)
                self.PushStatusText(_("Profile Saved as: %s") % profile, SB_INFO)
                dlg.Destroy()
            else:
                pass
        else:
            evt.Skip()

    def OnLoadProfile(self, evt):
        """Loads a profile and refreshes the editors state to match
        the settings found in the profile file.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_LOAD_PROFILE:
            dlg = wx.FileDialog(self, _("Load a Custom Profile"), 
                                CONFIG['PROFILE_DIR'], "default.ppb", 
                                _("Profile") + " (*.ppb)|*.ppb", wx.OPEN)

            result = dlg.ShowModal()
            if result == wx.ID_OK: 
                profile = dlg.GetFilename()
                path = dlg.GetPath()
                profiler.Profile().Load()(path)
                self.PushStatusText(_("Loaded Profile: %s") % profile, SB_INFO)
                dlg.Destroy()
            else:
                pass

            # Update editor to reflect loaded profile
            self.nb.UpdateTextControls()
        else:
            evt.Skip()

    def OnPrint(self, evt):
        """Handles sending the current document to the printer,
        showing print previews, and opening the printer settings
        dialog.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        pmode = _PGET('PRINT_MODE', "str").replace(u'/', u'_').lower()
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
        """Close this frame and unregister it from the applications
        mainloop.
        @note: Closing the frame will write out all session data to the
               users configuration directory.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        # This event is bound at two location need to unbind it to avoid fireing
        # the event again
        self.Unbind(wx.EVT_CLOSE)

        # Cleanup Controls
        controls = self.nb.GetPageCount()
        _PSET('LAST_SESSION', self.nb.GetFileNames())
        self.LOG("[main_evt] [exit] Number of controls: %d" % controls)

        self._exiting = True
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
                self._exiting = False
                self.Bind(wx.EVT_CLOSE, self.OnExit)
                return
        except UnboundLocalError:
            self.LOG("[main][exit][err] Trapped UnboundLocalError OnExit")

        ### If we get to here there is no turning back so cleanup
        ### additional items and save the user settings

        # Write out saved document information
        self.nb.DocMgr.WriteBook()
        syntax.SyntaxMgr().SaveState()

        # Save Shelf contents
        _PSET('SHELF_ITEMS', self._shelf.GetItemStack())

        # Save Window Size/Position for next launch
        # XXX workaround for possible bug in wxPython 2.8
        if wx.Platform == '__WXMAC__' and self.GetToolBar():
            self.toolbar.Destroy()
        _PSET('WSIZE', self.GetSizeTuple())
        _PSET('WPOS', self.GetPositionTuple())
        self.LOG("[main_evt] [exit] Closing editor at pos=%s size=%s" % \
                 (_PGET('WPOS', 'str'), _PGET('WSIZE', 'str')))
        
        # Update profile
        profiler.UpdateProfileLoader()
        profiler.AddFileHistoryToProfile(self.filehistory)
        profiler.Profile().Write(_PGET('MYPROFILE'))

        # Cleanup file history
        try:
            del self.filehistory
        except AttributeError:
            self.LOG("[main][exit][err] Trapped AttributeError OnExit")
        self._cmdbar.Destroy()

        # Post exit notice to all aui panes
        panes = self._mgr.GetAllPanes()
        exit_evt = ed_event.MainWindowExitEvent(ed_event.edEVT_MAINWINDOW_EXIT,
                                                wx.ID_ANY)
        for pane in panes:
            wx.PostEvent(pane.window, exit_evt)

        # Finally close the application
        self.LOG("[main_info] Closing Main Frame")
        wx.GetApp().UnRegisterWindow(repr(self))
        self.Destroy()

    #---- End File Menu Functions ----#

    #---- Edit Menu Functions ----#
    def OnPreferences(self, evt):
        """Open the Preference Panel
        @note: The dialogs module is not imported until this is 
               first called so the first open may lag a little.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_PREF:
            import prefdlg
            win = wx.GetApp().GetWindowInstance(prefdlg.PreferencesDialog)
            if win is not None:
                win.Raise()
                return
            dlg = prefdlg.PreferencesDialog(None, 
                                            title=_("Preferences - Editra"))
            dlg.CenterOnParent()
            dlg.Show()
        else:
            evt.Skip()
    #---- End Edit Menu Functions ----#

    #---- View Menu Functions ----#
    def OnGoto(self, evt):
        """Shows the Goto Line control
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        if e_id == ID_GOTO_LINE:
            self._cmdbar.Show(ed_cmdbar.ID_LINE_CTRL)
            self.sizer.Layout()
        else:
            evt.Skip()

    def OnViewTb(self, evt):
        """Toggles visibility of toolbar
        @note: On OSX there is a frame button for hidding the toolbar
               that is handled internally by the osx toolbar and not this
               handler.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_VIEW_TOOL:
            if _PGET('TOOLBAR', 'bool', False) and self.toolbar != None:
                self.toolbar.Destroy()
                del self.toolbar
                _PSET('TOOLBAR', False)
            else:
                self.toolbar = ed_toolbar.EdToolBar(self, wx.ID_ANY)
                self.SetToolBar(self.toolbar)
                _PSET('TOOLBAR', True)
                self.UpdateToolBar()
        else:
            evt.Skip()

    #---- End View Menu Functions ----#

    #---- Format Menu Functions ----#
    def OnFont(self, evt):
        """Open Font Settings Dialog for changing fonts on a per document
        basis.
        @status: This currently does not allow for font settings to stick
                 from one session to the next.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_FONT:
            ctrl = self.nb.GetCurrentCtrl()
            fdata = wx.FontData()
            fdata.SetInitialFont(ctrl.GetDefaultFont())
            dlg = wx.FontDialog(self, fdata)
            result = dlg.ShowModal()
            data = dlg.GetFontData()
            dlg.Destroy()
            if result == wx.ID_OK:
                font = data.GetChosenFont()
                ctrl.SetGlobalFont(self.nb.control.FONT_PRIMARY, \
                                   font.GetFaceName(), font.GetPointSize())
                ctrl.UpdateAllStyles()
        else:
            evt.Skip()

    #---- End Format Menu Functions ----#

    #---- Tools Menu Functions ----#
    def OnStyleEdit(self, evt):
        """Opens the style editor
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_STYLE_EDIT:
            import style_editor
            dlg = style_editor.StyleEditor(self)
            dlg.CenterOnParent()
            dlg.ShowModal()
            dlg.Destroy()
        else:
            evt.Skip()

    def OnPluginMgr(self, evt):
        """Opens and shows Plugin Manager window
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_PLUGMGR:
            import plugdlg
            win = wx.GetApp().GetWindowInstance(plugdlg.PluginDialog)
            if win is not None:
                win.Raise()
                return
            dlg = plugdlg.PluginDialog(self, wx.ID_ANY, prog_name + " " \
                                        + _("Plugin Manager"), \
                                        size=wx.Size(500, 350))
            dlg.CenterOnParent()
            dlg.Show()
        else:
            evt.Skip()

    def OnGenerate(self, evt):
        """Generates a given document type
        @requires: PluginMgr must be initialized and have active
                   plugins that implement the Generator Interface
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        doc = self._generator.GenerateText(e_id, self.nb.GetCurrentCtrl())
        if doc:
            self.nb.NewPage()
            ctrl = self.nb.GetCurrentCtrl()
            ctrl.SetText(doc[1]) 
            ctrl.FindLexer(doc[0])
        else:
            evt.Skip()

    #---- Help Menu Functions ----#
    def OnAbout(self, evt):
        """Show the About Dialog
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_ABOUT:
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
            wx.AboutBox(info)
        else:
            evt.Skip()

    def OnHelp(self, evt):
        """Handles help related menu events
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
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
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent
        @return: A string of all filefilters for all supported filetypes
                 and extensions.

        """
        filefilters = syntax.GenFileFilters()
        typestr = ''.join(filefilters)
        return typestr

    def DispatchToControl(self, evt):
        """Catches events that need to be passed to the current
        text control for processing.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if not self.IsActive():
            evt.Skip()
            return
        
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        menu_ids = syntax.SyntaxIds()
        menu_ids.extend([ID_SHOW_EOL, ID_SHOW_WS, ID_INDENT_GUIDES, ID_SYNTAX,
                         ID_KWHELPER, ID_WORD_WRAP, ID_BRACKETHL, ID_ZOOM_IN,
                         ID_ZOOM_OUT, ID_ZOOM_NORMAL, ID_EOL_MAC, ID_EOL_UNIX,
                         ID_EOL_WIN, ID_JOIN_LINES, ID_CUT_LINE, ID_COPY_LINE,
                         ID_INDENT, ID_UNINDENT, ID_TRANSPOSE, ID_NEXT_MARK,
                         ID_PRE_MARK, ID_ADD_BM, ID_DEL_BM, ID_DEL_ALL_BM,
                         ID_FOLDING, ID_AUTOCOMP, ID_SHOW_LN, ID_COMMENT,
                         ID_UNCOMMENT, ID_AUTOINDENT, ID_LINE_AFTER,
                         ID_LINE_BEFORE, ID_TAB_TO_SPACE, ID_SPACE_TO_TAB,
                         ID_TRIM_WS, ID_SHOW_EDGE, ID_MACRO_START, 
                         ID_MACRO_STOP, ID_MACRO_PLAY, ID_TO_LOWER, 
                         ID_TO_UPPER])
        ctrl = self.nb.GetCurrentCtrl()
        if e_id in [ID_UNDO, ID_REDO, ID_CUT, ID_COPY, ID_PASTE, ID_SELECTALL]:
            # If event is from the toolbar manually send it to the control as
            # the events from the toolbar do not propagate to the control.
            if e_obj.GetClassName() == "wxToolBar" or \
               e_id in [ID_REDO, ID_UNDO] \
               or wx.Platform == '__WXMSW__':
                ctrl.ControlDispatch(evt)
                self.UpdateToolBar()
            else:
                evt.Skip()
        elif e_id in menu_ids:
            ctrl.ControlDispatch(evt)
        else:
            evt.Skip()
        return

    def OnKeyUp(self, evt):
        """Update Line/Column indicator based on position.
        @param evt: Key Event
        @type evt: wx.KeyEvent(EVT_KEY_UP)

        """
        line, column = self.nb.GetCurrentCtrl().GetPos(evt)
        if line >= 0 and column >= 0:
            self.SetStatusText(_("Line: %d  Column: %d") % \
                               (line, column), SB_ROWCOL)
            self.UpdateToolBar()
        evt.Skip()

    def OnMenuHighlight(self, evt):
        """HACK for GTK, submenus dont seem to fire a EVT_MENU_OPEN
        but do fire a MENU_HIGHLIGHT
        @note: Only used on GTK
        @param evt: Event fired that called this handler
        @type evt: wx.MenuEvent(EVT_MENU_HIGHLIGHT)

        """
        if evt.GetId() == ID_LEXER:
            self.UpdateMenu(self.languagemenu)
        elif evt.GetId() == ID_EOL_MODE:
            self.UpdateMenu(self.lineformat)
        else:
            evt.Skip()

    def BindLangMenu(self):
        """Binds Language Menu Ids to event handler
        @note: This menu is dynamically generated based on the 
               available file types and lexer configurations. 
               
        """
        for l_id in syntax.SyntaxIds():
            self.Bind(wx.EVT_MENU, self.DispatchToControl, id=l_id)

    def OnQuickFind(self, evt):
        """Open the Commandbar in Search mode.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_QUICK_FIND:
            self._cmdbar.Show(ed_cmdbar.ID_SEARCH_CTRL)
            self.sizer.Layout()
        else:
            evt.Skip()

    # Menu Helper Functions
    #TODO this is fairly stupid, write a more general solution
    def UpdateMenu(self, evt):
        """Update Status of a Given Menu.
        @status: very ugly (hopefully temporary) hack that I hope I
                 can get rid of as soon as I can find a better way
                 to handle updating menuitem status.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        ctrl = self.nb.GetCurrentCtrl()
        menu2 = None
        if evt.GetClassName() == "wxMenuEvent":
            menu = evt.GetMenu()
            # HACK MSW GetMenu returns None on submenu open events
            if menu is None:
                menu = self.languagemenu
                menu2 = self.lineformat
        else:
            menu = evt

        if menu == self.languagemenu:
            self.LOG("[main_evt] Updating Settings/Lexer Menu")
            lang_id = ctrl.GetLangId()
            for menu_item in menu.GetMenuItems():
                item_id = menu_item.GetId()
                if menu.IsChecked(item_id):
                    menu.Check(item_id, False)
                if item_id == lang_id or \
                   (menu_item.GetLabel() == 'Plain Text' and lang_id == 0):
                    menu.Check(item_id, True)
            # HACK needed for MSW
            if menu2 != None:
                self.LOG("[menu_evt] Updating EOL Mode Menu")
                eol = ctrl.GetEOLModeId()
                for menu_id in [ID_EOL_MAC, ID_EOL_UNIX, ID_EOL_WIN]:
                    menu2.Check(menu_id, eol == menu_id)
                menu = self.vieweditmenu
        if menu == self.editmenu:
            self.LOG("[main_evt] Updating Edit Menu")
            menu.Enable(ID_UNDO, ctrl.CanUndo())
            menu.Enable(ID_REDO, ctrl.CanRedo())
            menu.Enable(ID_PASTE, ctrl.CanPaste())
            sel1, sel2 = ctrl.GetSelection()
            menu.Enable(ID_COPY, sel1 != sel2)
            menu.Enable(ID_CUT, sel1 != sel2)
            menu.Enable(ID_FIND, True)
            menu.Enable(ID_FIND_REPLACE, True)
        elif menu == self.settingsmenu:
            self.LOG("[menu_evt] Updating Settings Menu")
            menu.Check(ID_AUTOCOMP, ctrl.GetAutoComplete())
            menu.Check(ID_AUTOINDENT, ctrl.GetAutoIndent())
            menu.Check(ID_SYNTAX, ctrl.IsHighlightingOn())
            menu.Check(ID_FOLDING, ctrl.IsFoldingOn())
            menu.Check(ID_BRACKETHL, ctrl.IsBracketHlOn())
        elif menu == self.viewmenu:
            zoom = ctrl.GetZoom()
            self.LOG("[menu_evt] Updating View Menu: zoom = %d" % zoom)
            self.viewmenu.Enable(ID_ZOOM_NORMAL, zoom)
            self.viewmenu.Enable(ID_ZOOM_IN, zoom < 18)
            self.viewmenu.Enable(ID_ZOOM_OUT, zoom > -8)
            menu.Check(ID_VIEW_TOOL, hasattr(self, 'toolbar'))
        elif menu == self.vieweditmenu:
            menu.Check(ID_SHOW_WS, bool(ctrl.GetViewWhiteSpace()))
            menu.Check(ID_SHOW_EDGE, bool(ctrl.GetEdgeMode()))
            menu.Check(ID_SHOW_EOL, bool(ctrl.GetViewEOL()))
            menu.Check(ID_SHOW_LN, bool(ctrl.GetMarginWidth(1)))
            menu.Check(ID_INDENT_GUIDES, bool(ctrl.GetIndentationGuides()))
        elif menu == self.formatmenu:
            self.LOG("[menu_evt] Updating Format Menu")
            menu.Check(ID_WORD_WRAP, bool(ctrl.GetWrapMode()))
        elif menu == self.lineformat:
            self.LOG("[menu_evt] Updating EOL Mode Menu")
            eol = ctrl.GetEOLModeId()
            for menu_id in [ID_EOL_MAC, ID_EOL_UNIX, ID_EOL_WIN]:
                menu.Check(menu_id, eol == menu_id)
        else:
            pass
        return 0

    def UpdateToolBar(self):
        """Update Tool Status
        @status: Temporary fix for toolbar status updating

        """
        if not hasattr(self, 'toolbar') or self.toolbar is None:
            return -1
        ctrl = self.nb.GetCurrentCtrl()
        self.toolbar.EnableTool(ID_UNDO, ctrl.CanUndo())
        self.toolbar.EnableTool(ID_REDO, ctrl.CanRedo())
        self.toolbar.EnableTool(ID_PASTE, ctrl.CanPaste())

    def ModifySave(self):
        """Called when document has been modified prompting
        a message dialog asking if the user would like to save
        the document before closing.
        @return: Result value of whether the file was saved or not

        """
        if self.nb.GetCurrentCtrl().filename == u"":
            name = self.nb.GetPageText(self.nb.GetSelection())
        else:
            name = self.nb.GetCurrentCtrl().filename

        dlg = wx.MessageDialog(self, 
                                _("The file: \"%s\" has been modified since "
                                  "the last save point.\n Would you like to "
                                  "save the changes?") % name, 
                               _("Save Changes?"), 
                               wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | \
                               wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            self.OnSave(wx.MenuEvent(wx.wxEVT_COMMAND_MENU_SELECTED, ID_SAVE))

        return result

    def SetTitle(self, title=u''):
        """Sets the windows title
        @param title: The text to tag on to the default frame title
        @type title: string

        """
        name = "%s v%s" % (prog_name, version)
        if len(title):
            name = u' - ' + name
        wx.Frame.SetTitle(self, title + name)

    #---- End Misc Functions ----#

#-----------------------------------------------------------------------------#
# Plugin interface's to the MainWindow
class MainWindowI(plugin.Interface):
    """Provides simple one method interface into adding extra
    functionality to the main window. 
    @note: The method in this interface called once at the end 
           of the window's internationalization.

    """
    def PlugIt(self, window):
        """Do whatever is needed to integrate is plugin
        into the editor.
        @postcondition: The plugins controls are installed in the L{MainWindow}

        """
        pass

class MainWindowAddOn(plugin.Plugin):
    """Plugin that Extends the L{MainWindowI}"""
    observers = plugin.ExtensionPoint(MainWindowI)
    def Init(self, window):
        """Call all observers once to initialize
        @param window: window that observers become children of

        """
        log = wx.GetApp().GetLog()
        for ob in self.observers:
            try:
                ob.PlugIt(window)
            except Exception, msg:
                log("[main_addon][err] %s" % str(msg))
