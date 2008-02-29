###############################################################################
# Name: ed_main.py                                                            #
# Purpose: Editra's Main Window                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_main.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
#  This module provides the class for the main window. The MainWindow is   #
# main object of the editor containing the notebook, shelf, command bar    #
# and other items.                                                         #
#                                                                          #
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
        @param wsize: Windows initial size
        @param title: Windows Title

        """
        wx.Frame.__init__(self, parent, id_, title, size=wsize,
                          style=wx.DEFAULT_FRAME_STYLE)

        self._mgr = wx.aui.AuiManager(flags=wx.aui.AUI_MGR_DEFAULT | \
                                      wx.aui.AUI_MGR_TRANSPARENT_DRAG | \
                                      wx.aui.AUI_MGR_TRANSPARENT_HINT)
        self._mgr.SetManagedWindow(self)
        viewmgr.PerspectiveManager.__init__(self, self._mgr, \
                                            CONFIG['CACHE_DIR'])

        # Setup app icon and title 
        self.SetTitle()
        util.SetWindowIcon(self)

        # Check if user wants Metal Style under OS X
        # NOTE: soon to be deprecated
        if wx.Platform == '__WXMAC__' and _PGET('METAL'):
            self.SetExtraStyle(wx.FRAME_EX_METAL)

        # Attributes
        self.LOG = wx.GetApp().GetLog()
        self._handlers = dict(menu=list(), ui=list())

        #---- Sizers to hold subapplets ----#
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        #---- Setup File History ----#
        self.filehistory = wx.FileHistory(_PGET('FHIST_LVL', 'int', 5))

        #---- Status bar on bottom of window ----#
        self.CreateStatusBar(3, style=wx.ST_SIZEGRIP)
        self.SetStatusWidths([-1, 120, 155])
        #---- End Statusbar Setup ----#

        #---- Notebook that contains the editting buffers ----#
        edit_pane = wx.Panel(self)
        self.nb = ed_pages.EdPages(edit_pane, wx.ID_ANY)
        edit_pane.nb = self.nb
        self.sizer.Add(self.nb, 1, wx.EXPAND)
        edit_pane.SetSizer(self.sizer)
        self._mgr.AddPane(edit_pane, wx.aui.AuiPaneInfo(). \
                          Name("EditPane").Center().Layer(1).Dockable(False). \
                          CloseButton(False).MaximizeButton(False). \
                          CaptionVisible(False))

        #---- Command Bar ----#
        self._cmdbar = ed_cmdbar.CommandBar(edit_pane, ID_COMMAND_BAR)
        self._cmdbar.Hide()

        #---- Setup Toolbar ----#
        self.SetToolBar(ed_toolbar.EdToolBar(self))
        if not _PGET('TOOLBAR'):
            self.GetToolBar().Hide()
        #---- End Toolbar Setup ----#

        #---- Menus ----#
        menbar = ed_menu.EdMenuBar()
        self._menus = dict(file=menbar.GetMenuByName("file"),
                           edit=menbar.GetMenuByName("edit"),
                           view=menbar.GetMenuByName("view"),
                           viewedit=menbar.GetMenuByName("viewedit"),
                           format=menbar.GetMenuByName("format"),
                           settings=menbar.GetMenuByName("settings"),
                           tools=menbar.GetMenuByName("tools"),
                           lineformat=menbar.GetMenuByName("lineformat"),
                           language=syntax.GenLexerMenu())

        # Todo this should not be hard coded
        self._menus['view'].InsertMenu(5, ID_PERSPECTIVES, _("Perspectives"), 
                                       self.GetPerspectiveControls())

        ## Setup additional menu items
        self.filehistory.UseMenu(menbar.GetMenuByName("filehistory"))
        self._menus['settings'].AppendMenu(ID_LEXER, _("Lexers"), 
                                           self._menus['language'],
                                           _("Manually Set a Lexer/Syntax"))

        # On mac, do this to make help menu appear in correct location
        # Note it must be done before setting the menu bar and after the
        # menus have been created.
        if wx.Platform == '__WXMAC__':
            wx.GetApp().SetMacHelpMenuTitleName(_("Help"))

        #---- Menu Bar ----#
        self.SetMenuBar(menbar)

        #---- Actions to take on menu events ----#
        self.Bind(wx.EVT_MENU_OPEN, self.UpdateMenu)
        if wx.Platform == '__WXGTK__':
            self.Bind(wx.EVT_MENU_HIGHLIGHT, \
                      self.OnMenuHighlight, id=ID_LEXER)
            self.Bind(wx.EVT_MENU_HIGHLIGHT, \
                      self.OnMenuHighlight, id=ID_EOL_MODE)

        # Collect Menu Event handler pairs
        self._handlers['menu'].extend([# File Menu
                                       (ID_NEW, self.OnNew),
                                       (ID_OPEN, self.OnOpen),
                                       (ID_CLOSE, self.OnClosePage),
                                       (ID_CLOSE_WINDOW, self.OnClose),
                                       (ID_CLOSEALL, self.OnClosePage),
                                       (ID_SAVE, self.OnSave),
                                       (ID_SAVEAS, self.OnSaveAs),
                                       (ID_SAVEALL, self.OnSave),
                                       (ID_SAVE_PROFILE, self.OnSaveProfile),
                                       (ID_LOAD_PROFILE, self.OnLoadProfile),
                                       (ID_EXIT, wx.GetApp().OnExit),
                                       (ID_PRINT, self.OnPrint),
                                       (ID_PRINT_PRE, self.OnPrint),
                                       (ID_PRINT_SU, self.OnPrint),

                                       # Edit Menu
                                       (ID_FIND, 
                                        self.nb.FindService.OnShowFindDlg),
                                       (ID_FIND_REPLACE, 
                                        self.nb.FindService.OnShowFindDlg),
                                       (ID_QUICK_FIND, self.OnCommandBar),
                                       (ID_PREF, self.OnPreferences),

                                       # View Menu
                                       (ID_GOTO_LINE, self.OnCommandBar),
                                       (ID_VIEW_TOOL, self.OnViewTb),

                                       # Format Menu
                                       (ID_FONT, self.OnFont),

                                       # Tool Menu
                                       (ID_COMMAND, self.OnCommandBar),
                                       (ID_STYLE_EDIT, self.OnStyleEdit),
                                       (ID_PLUGMGR, self.OnPluginMgr),

                                       # Help Menu
                                       (ID_ABOUT, self.OnAbout),
                                       (ID_HOMEPAGE, self.OnHelp),
                                       (ID_DOCUMENTATION, self.OnHelp),
                                       (ID_CONTACT, self.OnHelp)])

        self._handlers['menu'].extend([(l_id, self.DispatchToControl) 
                                       for l_id in syntax.SyntaxIds()])

        # Extra menu handlers (need to work these into above system yet
        self.Bind(wx.EVT_MENU, self.DispatchToControl)
        self.Bind(wx.EVT_MENU, self.OnGenerate)
        self.Bind(wx.EVT_MENU_RANGE, self.OnFileHistory, 
                  id=wx.ID_FILE1, id2=wx.ID_FILE9)

        #---- End Menu Setup ----#

        #---- Other Event Handlers ----#
        # Frame
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(ed_event.EVT_STATUS, self.OnStatus)

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

        # Call add on plugins
        self.LOG("[main][info] Loading MainWindow Plugins ")
        plgmgr = wx.GetApp().GetPluginManager()
        addons = MainWindowAddOn(plgmgr)
        addons.Init(self)
        self._handlers['menu'].extend(addons.GetEventHandlers())
        self._handlers['ui'].extend(addons.GetEventHandlers(ui_evt=True))
        self._shelf = iface.Shelf(plgmgr)
        self._shelf.Init(self)
        self.LOG("[main][info] Loading Generator plugins")
        generator.Generator(plgmgr).InstallMenu(self._menus['tools'])

        # Set Perspective
        self.SetPerspective(_PGET('DEFAULT_VIEW'))
        self._mgr.Update()

    __name__ = u"MainWindow"

    #---- End Private Member Functions/Variables ----#

    #---- Begin Public Member Function ----#
    def OnActivate(self, evt):
        """Activation Event Handler
        @param evt: event that called this handler
        @type evt: wx.ActivateEvent

        """
        app = wx.GetApp()
        if evt.GetActive():
            for handler in self._handlers['menu']:
                app.AddHandlerForID(*handler)

            for handler in self._handlers['ui']:
                app.AddUIHandlerForID(*handler)
        else:
            for handler in self._handlers['menu']:
                app.RemoveHandlerForID(handler[0])

            for handler in self._handlers['ui']:
                app.RemoveUIHandlerForID(handler[0])
        evt.Skip()

    def AddFileToHistory(self, fname):
        """Add a file to the windows file history as well as any
        other open windows history.
        @param fname: name of file to add
        @todo: change the file history to a centrally manaaged object that
               all windows pull from to avoid this quick solution.

        """
        for win in wx.GetApp().GetMainWindows():
            if hasattr(win, 'filehistory'):
                win.filehistory.AddFileToHistory(fname)
        
    def DoOpen(self, evt, fname=u''):
        """ Do the work of opening a file and placing it
        in a new notebook page.
        @keyword fname: can be optionally specified to open
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
                                ''.join(syntax.GenFileFilters()), 
                                wx.OPEN | wx.MULTIPLE)
            dlg.SetFilterIndex(_PGET('FFILTER', 'int', 0))
            result = dlg.ShowModal()
            _PSET('FFILTER', dlg.GetFilterIndex())
            paths = dlg.GetPaths()
            dlg.Destroy()

            if result != wx.ID_OK:
                self.LOG('[mainw][info] Canceled Opening File')
            else:
                for path in paths:
                    if _PGET('OPEN_NW', default=False):
                        wx.GetApp().OpenNewWindow(path)
                    else:
                        dirname = util.GetPathName(path)
                        filename = util.GetFileName(path)
                        self.nb.OpenPage(dirname, filename)   
                        self.nb.GoCurrentPage()
        else:
            self.LOG("[mainw][info] CMD Open File: %s" % fname)
            filename = util.GetFileName(fname)
            dirname = util.GetPathName(fname)
            self.nb.OpenPage(dirname, filename)

    def GetFrameManager(self):
        """Returns the manager for this frame
        @return: Reference to the AuiMgr of this window

        """
        return self._mgr

    def GetNotebook(self):
        """Get the windows main notebook that contains the editing buffers
        @return: reference to L{extern.flatnotebook.Flatnotebook} instance

        """
        return self.nb

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
        try:
            hist_list = _PGET('FHIST', default=list())
            if len(hist_list) > size:
                hist_list = hist_list[:size]

            for fname in hist_list:
                if isinstance(fname, basestring) and fname:
                    self.filehistory.AddFileToHistory(fname)
        except UnicodeEncodeError, msg:
            self.LOG("[main][err] Filehistory load failed: %s" % str(msg))

    def OnNew(self, evt):
        """Start a New File in a new tab
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
            evt.Skip()

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
            for page in xrange(self.nb.GetPageCount()):
                if issubclass(self.nb.GetPage(page).__class__, 
                                           wx.stc.StyledTextCtrl):
                    ctrls.append((self.nb.GetPageText(page), 
                                  self.nb.GetPage(page)))
        else:
            evt.Skip()
            return

        for ctrl in ctrls:
            fname = util.GetFileName(ctrl[1].GetFileName())
            if fname != '':
                fpath = ctrl[1].GetFileName()
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
                    self.AddFileToHistory(ctrl[1].GetFileName())
        self.UpdateToolBar()

    def OnSaveAs(self, evt, title=u'', page=None):
        """Save File Using a new/different name
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        dlg = wx.FileDialog(self, _("Choose a Save Location"), u'', 
                            title.lstrip(u"*"), 
                            ''.join(syntax.GenFileFilters()), 
                            wx.SAVE | wx.OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            dlg.Destroy()

            if page:
                ctrl = page
            else:
                ctrl = self.nb.GetCurrentCtrl()

            result = ctrl.SaveFile(path)
            fname = util.GetFileName(ctrl.GetFileName())
            if not result:
                dlg = wx.MessageDialog(self, _("Failed to save file: %s\n\nError:\n%d") % \
                                       (fname, result), _("Save Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                self.PushStatusText(_("ERROR: Failed to save %s") % fname, SB_INFO)
            else:
                self.PushStatusText(_("Saved File As: %s") % fname, SB_INFO)
                self.SetTitle(u"%s - file://%s" % (fname, ctrl.GetFileName()))
                self.nb.SetPageText(self.nb.GetSelection(), fname)
                self.nb.GetCurrentCtrl().FindLexer()
                self.nb.UpdatePageImage()
            return result
        else:
            dlg.Destroy()

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
                profiler.Profile().Write(dlg.GetPath())
                self.PushStatusText(_("Profile Saved as: %s") % \
                                    dlg.GetFilename(), SB_INFO)
            dlg.Destroy()
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
                profiler.Profile().Load(dlg.GetPath())
                self.PushStatusText(_("Loaded Profile: %s") % \
                                    dlg.GetFilename(), SB_INFO)
            dlg.Destroy()

            # Update editor to reflect loaded profile
            for win in wx.GetApp().GetMainWindows():
                win.nb.UpdateTextControls()
        else:
            evt.Skip()

    def OnStatus(self, evt):
        """Update status text with messages from other controls
        @param evt: event that called this handler

        """
        if self.GetStatusBar():
            self.PushStatusText(evt.GetMessage(), evt.GetSection())

    def OnPrint(self, evt):
        """Handles sending the current document to the printer,
        showing print previews, and opening the printer settings
        dialog.
        @todo: is any manual cleanup required for the printer objects?
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        printer = ed_print.EdPrinter(self, self.nb.GetCurrentCtrl)
        printer.SetColourMode(_PGET('PRINT_MODE', "str").\
                              replace(u'/', u'_').lower())
        if e_id == ID_PRINT:
            printer.Print()
        elif e_id == ID_PRINT_PRE:
            printer.Preview()
        elif e_id == ID_PRINT_SU:
            printer.PageSetup()
        else:
            evt.Skip()

    def Close(self, force=False):
        """Close the window
        @param force: force the closer by vetoing the event handler

        """
        if force:
            return wx.Frame.Close(self, True)
        else:
            result = self.OnClose()
            return not result

    def OnClose(self, evt=None):
        """Close this frame and unregister it from the applications
        mainloop.
        @note: Closing the frame will write out all session data to the
               users configuration directory.
        @keyword evt: Event fired that called this handler
        @type evt: wxMenuEvent
        @return: None on destroy, or True on cancel

        """
        # Cleanup Controls
        _PSET('LAST_SESSION', self.nb.GetFileNames())
        self._exiting = True
        controls = self.nb.GetPageCount()
        self.LOG("[main_evt][exit] Number of controls: %d" % controls)
        while controls:
            if controls <= 0:
                self.Close(True) # Force exit since there is a problem

            self.LOG("[main_evt][exit] Requesting Page Close")
            result = self.nb.ClosePage()
            if result == wx.ID_CANCEL:
                break
            controls -= 1

        if result == wx.ID_CANCEL:
            self._exiting = False
            return True

        ### If we get to here there is no turning back so cleanup
        ### additional items and save user settings

        # Write out saved document information
        self.nb.DocMgr.WriteBook()
        syntax.SyntaxMgr().SaveState()

        # Save Shelf contents
        _PSET('SHELF_ITEMS', self._shelf.GetItemStack())

        # Save Window Size/Position for next launch
        # XXX On wxMac the window size doesnt seem to take the toolbar
        #     into account so destroy it so that the window size is accurate.
        if wx.Platform == '__WXMAC__' and self.GetToolBar():
            self.GetToolBar().Destroy()
        _PSET('WSIZE', self.GetSizeTuple())
        _PSET('WPOS', self.GetPositionTuple())
        self.LOG("[main_evt] [exit] Closing editor at pos=%s size=%s" % \
                 (_PGET('WPOS', 'str'), _PGET('WSIZE', 'str')))
        
        # Update profile
        profiler.AddFileHistoryToProfile(self.filehistory)
        profiler.Profile().Write(_PGET('MYPROFILE'))

        # Cleanup file history
        try:
            del self.filehistory
        except AttributeError:
            self.LOG("[main][exit][err] Trapped AttributeError OnExit")

        # Post exit notice to all aui panes
        panes = self._mgr.GetAllPanes()
        exit_evt = ed_event.MainWindowExitEvent(ed_event.edEVT_MAINWINDOW_EXIT,
                                                wx.ID_ANY)
        for pane in panes:
            wx.PostEvent(pane.window, exit_evt)

        # Finally close the window
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
            dlg = prefdlg.PreferencesDialog(None)
            dlg.CenterOnParent()
            dlg.Show()
        else:
            evt.Skip()
    #---- End Edit Menu Functions ----#

    #---- View Menu Functions ----#
    def OnViewTb(self, evt):
        """Toggles visibility of toolbar
        @note: On OSX there is a frame button for hidding the toolbar
               that is handled internally by the osx toolbar and not this
               handler.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if evt.GetId() == ID_VIEW_TOOL:
            size = self.GetSize()
            toolbar = self.GetToolBar()
            if _PGET('TOOLBAR', 'bool', False) or toolbar.IsShown():
                _PSET('TOOLBAR', False)
                toolbar.Hide()
                if wx.Platform != '__WXMAC__':
                    self.SetSize((size[0], size[1] - toolbar.GetSize()[1]))
            else:
                _PSET('TOOLBAR', True)
                toolbar.Show()
                if wx.Platform != '__WXMAC__':
                    self.SetSize((size[0], size[1] + toolbar.GetSize()[1]))
                self.UpdateToolBar()

            self.SendSizeEvent()
            self.Refresh()
            self.Update()
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
            dlg = plugdlg.PluginDialog(self, wx.ID_ANY, PROG_NAME + " " \
                                        + _("Plugin Manager"), \
                                        size=wx.Size(550, 350))
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
        gen = generator.Generator(wx.GetApp().GetPluginManager())
        doc = gen.GenerateText(e_id, self.nb.GetCurrentCtrl())
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
                    "Homepage: " + HOME_PAGE + "\n",
                    "Platform Info: (%s,%s)", 
                    "License: GPL v2 (see COPYING.txt for full license)"]
            desc = "\n".join(desc)
            py_version = sys.platform + ", python " + sys.version.split()[0]
            platform = list(wx.PlatformInfo[1:])
            platform[0] += (" " + wx.VERSION_STRING)
            wx_info = ", ".join(platform)
            info.SetCopyright("Copyright(C) 2005-%d Cody Precord" % year[0])
            info.SetName(PROG_NAME.title())
            info.SetDescription(desc % (py_version, wx_info))
            info.SetVersion(VERSION)
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
            webbrowser.open(HOME_PAGE, 1)
        elif e_id == ID_DOCUMENTATION:
            webbrowser.open_new_tab(HOME_PAGE + "/?page=doc")
        elif e_id == ID_CONTACT:
            webbrowser.open(u'mailto:%s' % CONTACT_MAIL)
        else:
            evt.Skip()

    #---- End Help Menu Functions ----#

    #---- Misc Function Definitions ----#
    def DispatchToControl(self, evt):
        """Catches events that need to be passed to the current
        text control for processing.
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        if not self.IsActive() or \
           not (self.FindFocus() == self.nb.GetCurrentCtrl()):
            evt.Skip()
            return

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
                         ID_TO_UPPER, ID_SELECTALL, ID_UNDO, ID_REDO, ID_CUT, 
                         ID_COPY, ID_PASTE])
        if evt.GetId() in menu_ids:
            self.nb.GetCurrentCtrl().ControlDispatch(evt)
            self.UpdateToolBar()
        else:
            evt.Skip()
        return

    def OnKeyUp(self, evt):
        """Update Line/Column indicator based on position.
        @param evt: Key Event
        @type evt: wx.KeyEvent(EVT_KEY_UP)

        """
        self.SetStatusText(_("Line: %d  Column: %d") % \
                           self.nb.GetCurrentCtrl().GetPos(), SB_ROWCOL)
        evt.Skip()

    def OnMenuHighlight(self, evt):
        """HACK for GTK, submenus dont seem to fire a EVT_MENU_OPEN
        but do fire a MENU_HIGHLIGHT
        @note: Only used on GTK
        @param evt: Event fired that called this handler
        @type evt: wx.MenuEvent(EVT_MENU_HIGHLIGHT)

        """
        if evt.GetId() == ID_LEXER:
            self.UpdateMenu(self._menus['language'])
        elif evt.GetId() == ID_EOL_MODE:
            self.UpdateMenu(self._menus['lineformat'])
        else:
            evt.Skip()

    def OnCommandBar(self, evt):
        """Open the Commandbar
        @param evt: Event fired that called this handler
        @type evt: wxMenuEvent

        """
        e_id = evt.GetId()
        if e_id == ID_QUICK_FIND:
            self._cmdbar.Show(ed_cmdbar.ID_SEARCH_CTRL)
        elif e_id == ID_GOTO_LINE:
            self._cmdbar.Show(ed_cmdbar.ID_LINE_CTRL)
        elif e_id == ID_COMMAND:
            self._cmdbar.Show(ed_cmdbar.ID_CMD_CTRL)
        else:
            evt.Skip()
        self.sizer.Layout()

    def ShowCommandCtrl(self):
        """Open the Commandbar in command mode.
        @todo: check if this is necessary

        """
        self._cmdbar.Show(ed_cmdbar.ID_CMD_CTRL)
        self.sizer.Layout()

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
                menu = self._menus['language']
                menu2 = self._menus['lineformat']
        else:
            menu = evt

        if menu == self._menus['language']:
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
                menu = self._menus['viewedit']
        if menu == self._menus['edit']:
            self.LOG("[main_evt] Updating Edit Menu")
            menu.Enable(ID_UNDO, ctrl.CanUndo())
            menu.Enable(ID_REDO, ctrl.CanRedo())
            menu.Enable(ID_PASTE, ctrl.CanPaste())
            sel1, sel2 = ctrl.GetSelection()
            menu.Enable(ID_COPY, sel1 != sel2)
            menu.Enable(ID_CUT, sel1 != sel2)
            menu.Enable(ID_FIND, True)
            menu.Enable(ID_FIND_REPLACE, True)
        elif menu == self._menus['settings']:
            self.LOG("[menu_evt] Updating Settings Menu")
            menu.Check(ID_AUTOCOMP, ctrl.GetAutoComplete())
            menu.Check(ID_AUTOINDENT, ctrl.GetAutoIndent())
            menu.Check(ID_SYNTAX, ctrl.IsHighlightingOn())
            menu.Check(ID_FOLDING, ctrl.IsFoldingOn())
            menu.Check(ID_BRACKETHL, ctrl.IsBracketHlOn())
        elif menu == self._menus['view']:
            zoom = ctrl.GetZoom()
            self.LOG("[menu_evt] Updating View Menu: zoom = %d" % zoom)
            self._menus['view'].Enable(ID_ZOOM_NORMAL, zoom)
            self._menus['view'].Enable(ID_ZOOM_IN, zoom < 18)
            self._menus['view'].Enable(ID_ZOOM_OUT, zoom > -8)
            menu.Check(ID_VIEW_TOOL, self.GetToolBar().IsShown())
        elif menu == self._menus['viewedit']:
            menu.Check(ID_SHOW_WS, bool(ctrl.GetViewWhiteSpace()))
            menu.Check(ID_SHOW_EDGE, bool(ctrl.GetEdgeMode()))
            menu.Check(ID_SHOW_EOL, bool(ctrl.GetViewEOL()))
            menu.Check(ID_SHOW_LN, bool(ctrl.GetMarginWidth(1)))
            menu.Check(ID_INDENT_GUIDES, bool(ctrl.GetIndentationGuides()))
        elif menu == self._menus['format']:
            self.LOG("[menu_evt] Updating Format Menu")
            menu.Check(ID_WORD_WRAP, bool(ctrl.GetWrapMode()))
        elif menu == self._menus['lineformat']:
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
        toolbar = self.GetToolBar()
        if not hasattr(toolbar, 'IsShown') or not toolbar.IsShown():
            return -1
        ctrl = self.nb.GetCurrentCtrl()
        toolbar.EnableTool(ID_UNDO, ctrl.CanUndo())
        toolbar.EnableTool(ID_REDO, ctrl.CanRedo())
        toolbar.EnableTool(ID_PASTE, ctrl.CanPaste())

    def ModifySave(self):
        """Called when document has been modified prompting
        a message dialog asking if the user would like to save
        the document before closing.
        @return: Result value of whether the file was saved or not

        """
        name = self.nb.GetCurrentCtrl().GetFileName()
        if name == u"":
            name = self.nb.GetPageText(self.nb.GetSelection())

        dlg = wx.MessageDialog(self, 
                                _("The file: \"%s\" has been modified since "
                                  "the last save point.\n\nWould you like to "
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
        name = "%s v%s" % (PROG_NAME, VERSION)
        if len(title):
            name = u' - ' + name
        wx.Frame.SetTitle(self, title + name)

    #---- End Misc Functions ----#

#-----------------------------------------------------------------------------#
# Plugin interface's to the MainWindow
# For backwards compatibility soon to be moved
MainWindowI = iface.MainWindowI

class MainWindowAddOn(plugin.Plugin):
    """Plugin that Extends the L{MainWindowI}"""
    observers = plugin.ExtensionPoint(MainWindowI)
    def Init(self, window):
        """Call all observers once to initialize
        @param window: window that observers become children of

        """
        for observer in self.observers:
            try:
                observer.PlugIt(window)
            except Exception, msg:
                util.Log("[main_addon][err] %s" % str(msg))

    def GetEventHandlers(self, ui_evt=False):
        """Get Event handlers and Id's from all observers
        @keyword ui_evt: Get Update Ui handlers (default get menu handlers)
        @return: list [(ID_FOO, foo.OnFoo), (ID_BAR, bar.OnBar)]

        """
        handlers = list()
        for observer in self.observers:
            try:
                if ui_evt:
                    items = observer.GetUIHandlers()
                else:
                    items = observer.GetMenuHandlers()
            except Exception, msg:
                util.Log("[main_addon][err] %s" % str(msg))
                continue
            handlers.extend(items)
        return handlers
