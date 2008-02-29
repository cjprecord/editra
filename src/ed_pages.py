###############################################################################
# Name: ed_pages.py                                                           #
# Purpose: The main editor notebook                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_pages.py                                                        #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
# This file defines the notebook for containing the text controls for      #
# for editing text in Editra. The note book is a custom sublclass of       #
# FlatNotebook that allow for automatic page images and drag and dropping  #
# of tabs between open editor windows. The notebook is also primarly in    #
# charge of opening files that are requested by the user and setting up the#
# text control to use them. For more information on the text controls used #
# in the notebook see ed_stc.py                                            #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import glob
import wx
import ed_glob
from profiler import Profile_Get
import ed_stc
import syntax.synglob as synglob
import ed_search
import util
import doctools
from extern import flatnotebook as FNB

#--------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
class EdPages(FNB.FlatNotebook):
    """Editras editor buffer botebook
    @todo: allow for tab styles to be configurable (maybe)

    """
    def __init__(self, parent, id_num):
        """Initialize a notebook with a blank text control in it
        @param parent: parent window of the notebook
        @param id_num: this notebooks id

        """
        FNB.FlatNotebook.__init__(self, parent, id_num, 
                                  style=FNB.FNB_FF2 |
                                        FNB.FNB_X_ON_TAB | 
                                        FNB.FNB_SMART_TABS |
                                        FNB.FNB_BACKGROUND_GRADIENT |
                                        FNB.FNB_DROPDOWN_TABS_LIST |
                                        FNB.FNB_ALLOW_FOREIGN_DND
                            )

        # Notebook attributes
        self.LOG = wx.GetApp().GetLog()
        self.FindService = ed_search.TextFinder(self, self.GetCurrentCtrl)
        self.DocMgr = doctools.DocPositionMgr(ed_glob.CONFIG['CACHE_DIR'] + \
                                              util.GetPathChar() + u'positions')
        self.pg_num = -1              # Track new pages (aka untitled docs)
        self.control = None
        self.frame = self.GetTopLevelParent() # MainWindow
        self._index = dict()          # image list index

        # Set Additional Style Parameters
        self.SetNonActiveTabTextColour(wx.Colour(102, 102, 102))
        ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.png"
        self.SetNavigatorIcon(wx.Bitmap(ed_icon, wx.BITMAP_TYPE_PNG))

        # Setup the ImageList and the default image
        imgl = wx.ImageList(16, 16)
        txtbmp = wx.ArtProvider.GetBitmap(str(synglob.ID_LANG_TXT), wx.ART_MENU)
        self._index[synglob.ID_LANG_TXT] = imgl.Add(txtbmp)
        self.SetImageList(imgl)

        # Notebook Events
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnUpdatePageText)
        self._pages.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Add a blank page
        self.NewPage()

    #---- End Init ----#

    #---- Function Definitions ----#
    def _NeedOpen(self, path):
        """Check if a file needs to be opened. If the file is already open in
        the notebook a dialog will be opened to ask if the user wants to reopen
        the file again. If the file is not open and exists or the user chooses 
        to reopen the file again the function will return True else it will 
        return False.
        @param path: file to check for

        """
        result = wx.ID_YES
        if self.HasFileOpen(path):
            mdlg = wx.MessageDialog(self,
                                    _("File is already open in an existing "
                                      "page.\nDo you wish to open it again?"),
                                    _("Open File") + u"?", 
                                    wx.YES_NO | wx.NO_DEFAULT | \
                                    wx.ICON_INFORMATION)
            result = mdlg.ShowModal()
            mdlg.Destroy()
            if result == wx.ID_NO:
                for page in xrange(self.GetPageCount()):
                    ctrl = self.GetPage(page)
                    if path == ctrl.GetFileName():
                        self.SetSelection(page)
                        self.ChangePage(page)
                        break
        elif os.path.exists(path) and not os.path.isfile(path):
            result = wx.ID_NO
        else:
            pass

        return result == wx.ID_YES

    def GetCurrentCtrl(self):
        """Returns the control of the currently selected
        page in the notebook.
        @return: window object contained in current page or None

        """
        if hasattr(self, 'control'):
            return self.control
        else:
            return None

    def GetFileNames(self):
        """Gets the name of all open files in the notebook
        @return: list of file names

        """
        rlist = list()
        for buff in self.GetTextControls():
            fname = buff.GetFileName()
            if fname != wx.EmptyString:
                rlist.append(fname)
        return rlist

    def LoadSessionFiles(self):
        """Load files from saved session data in profile
        @postcondition: Files saved from previous session are
                        opened. If no files were found then only a
                        single blank page is opened.

        """
        files = Profile_Get('LAST_SESSION')
        if files is not None:
            for fname in files:
                if os.path.exists(fname) and os.access(fname, os.R_OK):
                    self.OpenPage(os.path.dirname(fname), 
                                  os.path.basename(fname))

        if self.GetPageCount() == 0:
            self.NewPage()

    def NewPage(self):
        """Create a new notebook page with a blank text control
        @postcondition: a new page with an untitled document is opened

        """
        self.pg_num += 1
        self.control = ed_stc.EditraStc(self, wx.ID_ANY)
        self.LOG("[nb_evt] Page Creation ID: %d" % self.control.GetId())
        self.AddPage(self.control, u"Untitled - %d" % self.pg_num)
        self.SetPageImage(self.GetSelection(), str(self.control.GetLangId()))

    def OpenPage(self, path, filename):
        """Open a File Inside of a New Page
        @param path: files base path
        @param filename: name of file to open

        """
        path2file = os.path.join(path, filename)

        # Check if file needs to be opened
        if not self._NeedOpen(path2file):
            return

        # Create new control to place text on if necessary
        new_pg = True
        if self.GetPageCount():
            if self.control.GetModify() or self.control.GetLength() or \
               self.control.GetFileName() != u'':
                control = ed_stc.EditraStc(self, wx.ID_ANY)
                control.Hide()
            else:
                new_pg = False
        else:
            control = ed_stc.EditraStc(self, wx.ID_ANY)
            control.Hide()

        # Open file and get contents
        err = False
        in_txt = u''
        enc = u'utf-8'
        if os.path.exists(path2file):
            try:
                in_txt, enc = util.GetDecodedText(path2file)
            except (UnicodeDecodeError, IOError, OSError), msg:
                self.LOG(("[ed_pages][err] Failed to open file %s\n"
                          "[ed_pages][err] %s") % (path2file, msg))

                # File could not be opened/read give up
                err = wx.MessageDialog(self, _("Editra could not properly "
                                               "open %s\n") \
                                       % path2file, _("Error Opening File"),
                                       style=wx.OK | wx.CENTER | wx.ICON_ERROR)
                err.ShowModal()
                err.Destroy()

                if new_pg:
                    control.Destroy()
                return

        # Put control into page an place page in notebook
        if new_pg:
            control.Show()
            self.control = control

        # Pass directory and file name info to control object to save reference
        self.control.SetText(in_txt, enc)
        self.control.SetFileName(path2file)
        self.control.SetModTime(util.GetFileModTime(path2file))
        self.frame.AddFileToHistory(path2file)
        if new_pg:
            self.AddPage(self.control, filename)

        self.frame.SetTitle("%s - file://%s" % (filename, 
                                                self.control.GetFileName()))
        self.SetPageText(self.GetSelection(), filename)
        self.LOG("[nb_evt] Opened Page: ID = %d" % self.GetSelection())

        # Setup Document
        self.control.FindLexer()
        self.control.CheckEOL()
        self.control.EmptyUndoBuffer()

        if Profile_Get('SAVE_POS'):
            self.control.GotoPos(self.DocMgr.GetPos(self.control.GetFileName()))

        # Set tab image
        self.SetPageImage(self.GetSelection(), str(self.control.GetLangId()))

        # Refocus on selected page
        self.GoCurrentPage()

    def GoCurrentPage(self):
        """Move Focus to Currently Selected Page.
        @postcondition: focus is set to current page

        """
        current_page = self.GetSelection()
        if current_page < 0:
            return current_page

        self.LOG("[nb_info] Current Page = %d" % current_page)

        control = self.GetPage(current_page)
        control.SetFocus()
        self.control = control
        return current_page

    def GetPageText(self, pg_num):
        """Gets the tab text from the given page number, stripping
        the * mark if there is one.
        @param pg_num: index of page to get tab text from
        @return: the tabs text

        """
        txt = FNB.FlatNotebook.GetPageText(self, pg_num)
        if not txt or txt[0] != u"*":
            return txt
        return txt[1:]

    def GetTextControls(self):
        """Gets all the currently opened text controls
        @return: list containing reference to all stc controls opened in the
                 notebook.

        """
        return [self.GetPage(page) for page in xrange(self.GetPageCount())]

    def HasFileOpen(self, fpath):
        """Checks if one of the currently active buffers has
        the named file in it.
        @param fpath: full path of file to check
        @return: bool indicating whether file is currently open or not

        """
        for ctrl in self.GetTextControls():
            if fpath == ctrl.GetFileName():
                return True
        return False

    #---- Event Handlers ----#
    def OnDrop(self, files):
        """Opens dropped files
        @param files: list of file paths
        @postcondition: all files that could be properly opend are added to
                        the notebook

        """
        # Check file properties and make a "clean" list of file(s) to open
        valid_files = list()
        for fname in files:
            self.LOG("[fdt_evt] File(s) Dropped: %s" % fname)
            if not os.path.exists(fname):
                self.frame.PushStatusText(_("Invalid file: %s") % fname, \
                                          ed_glob.SB_INFO)
            elif os.path.isdir(fname):
                dcnt = glob.glob(os.path.join(fname, '*'))
                dcnt = util.FilterFiles(dcnt)
                if not len(dcnt):
                    dlg = wx.MessageDialog(self, 
                                           _("There are no files that Editra"
                                             " can open in %s") % fname,
                                           _("No Valid Files to Open"),
                                           style=wx.OK | wx.CENTER | \
                                                 wx.ICON_INFORMATION)
                else:
                    dlg = wx.MessageDialog(self, 
                                           _("Do you wish to open all %d files"
                                             " in this directory?\n\nWarning"
                                             " opening many files at once may"
                                             " cause the editor to temporarly "
                                             " freeze.") % len(dcnt),
                                           _("Open Directory?"),
                                           style=wx.YES | wx.NO | \
                                                 wx.ICON_INFORMATION)
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_YES:
                    valid_files.extend(dcnt)
                else:
                    pass
            else:
                valid_files.append(fname)

        for fname in valid_files:
            pathname = util.GetPathName(fname)
            the_file = util.GetFileName(fname)
            self.OpenPage(pathname, the_file)
            self.frame.PushStatusText(_("Opened file: %s") % fname, \
                                      ed_glob.SB_INFO)
        return

    def OnIdle(self, evt):
        """Update tabs and check if files have been modified
        @param evt: Event that called this handler
        @type evt: wx.IdleEvent

        """
        if wx.GetApp().IsActive() and \
           Profile_Get('CHECKMOD') and self.GetPageCount():
            cfile = self.control.GetFileName()
            lmod = util.GetFileModTime(cfile)
            if self.control.GetModTime() and \
               not lmod and not os.path.exists(cfile):
                wx.CallAfter(PromptToReSave, self, cfile)
            elif self.control.GetModTime() < lmod:
                wx.CallAfter(AskToReload, self, cfile)
            else:
                return False
                        
    def OnLeftUp(self, evt):
        """Traps clicks sent to page close buttons and 
        redirects the action to the ClosePage function
        @param evt: Event that called this handler
        @type evt: wx.MouseEvent

        """
        cord = self._pages.HitTest(evt.GetPosition())[0]
        if cord == FNB.FNB_X:
            # Make sure that the button was pressed before
            if self._pages._nXButtonStatus != FNB.FNB_BTN_PRESSED:
                return
            self._pages._nXButtonStatus = FNB.FNB_BTN_HOVER
            self.ClosePage()
        elif cord == FNB.FNB_TAB_X:
            # Make sure that the button was pressed before
            if self._pages._nTabXButtonStatus != FNB.FNB_BTN_PRESSED:
                return 
            self._pages._nTabXButtonStatus = FNB.FNB_BTN_HOVER
            self.ClosePage()
        else:
            evt.Skip()

    def OnPageChanging(self, evt):
        """Page changing event handler.
        @param evt: event that called this handler
        @type evt: flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGING

        """
        evt.Skip()
        self.LOG("[nb_evt] Page Changed to %d" % evt.GetSelection())

    def ChangePage(self, pgid):
        """Change the page and focus to the the given page id
        @param pgid: Page number to change to

        """
        window = self.GetPage(pgid) # returns current stc
        window.SetFocus()
        self.control = window
        fname = self.control.GetFileName()

        if fname == "":
            fname = self.GetPageText(pgid)

        self.frame.SetTitle("%s - file://%s" % (util.GetFileName(fname), fname))

    def OnPageChanged(self, evt):
        """Actions to do after a page change
        @param evt: event that called this handler
        @type evt: wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED

        """
        self.ChangePage(evt.GetSelection())
        self.LOG(("[nb_evt] Control Changing from Page: %d to Page: %d\n"
                  "[nb_info] It has file named: %s" % (evt.GetOldSelection(), 
                                                       evt.GetSelection(), 
                                                       self.control.GetFileName())))
        self.frame.UpdateToolBar()
        evt.Skip()

    def OnPageClosing(self, evt):
        """Checks page status to flag warnings before closing
        @param evt: event that called this handler
        @type evt: wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING

        """
        self.LOG("[nb_evt] Closing Page: #%d" % self.GetSelection())
        page = self.GetCurrentPage()
        if len(page.GetFileName()) > 1:
            self.DocMgr.AddRecord([page.GetFileName(), page.GetCurrentPos()])
        evt.Skip()

    def OnPageClosed(self, evt):
        """Handles Paged Closed Event
        @param evt: event that called this handler
        @type evt: wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSED

        """
        self.LOG("[nb_evt] Closed Page: #%d" % self.GetSelection())
        evt.Skip()
    #---- End Event Handlers ----#

    def CloseAllPages(self):
        """Closes all open pages
        @postcondition: all pages in the notebook are closed

        """
        for page in xrange(self.GetPageCount()):
            result = self.ClosePage()
            if result == wx.ID_CANCEL:
                self.LOG("[nb][closeall] Canceled on page %d" % page)
                break
            
    def ClosePage(self):
        """Closes Currently Selected Page
        @postcondtion: currently selected page is closed

        """
        self.GoCurrentPage()
        pg_num = self.GetSelection()
        result = wx.ID_OK

        if self.control.GetModify():
            result = self.frame.ModifySave()
            if result != wx.ID_CANCEL:
                self.DeletePage(pg_num)
                self.GoCurrentPage()
            else:
                pass
        else:
            self.DeletePage(pg_num)
            self.GoCurrentPage()

        # TODO this causes some flashing
        frame = self.GetTopLevelParent()
        if not self.GetPageCount() and \
           hasattr(frame, 'IsExiting') and not frame.IsExiting():
            self.NewPage()
        return result

    def SetPageImage(self, pg_num, lang_id):
        """Sets the page image by querying the ArtProvider based
        on the language id associated with the type of open document.
        Any unknown filetypes are associated with the plaintext page
        image.
        @param pg_num: page index to set image for
        @param lang_id: language id of file type to get mime image for

        """
        imglst = self.GetImageList()
        if not self._index.has_key(lang_id):
            bmp = wx.ArtProvider.GetBitmap(lang_id, wx.ART_MENU)
            if bmp.IsNull():
                self._index.setdefault(lang_id, \
                                       self._index[synglob.ID_LANG_TXT])
            else:
                self._index[lang_id] = imglst.Add(wx.ArtProvider.\
                                              GetBitmap(lang_id, wx.ART_MENU))
        FNB.FlatNotebook.SetPageImage(self, pg_num, self._index[lang_id])

    def UpdatePageImage(self):
        """Updates the page tab image
        @postcondtion: page image is updated to reflect any changes in ctrl

        """
        pg_num = self.GetSelection()
        ftype = util.GetExtension(self.control.GetFileName())
        ftype = ftype[-1].upper()
        self.LOG("[nb_info] Updating Page Image: Page %d" % pg_num)
        self.SetPageImage(pg_num, str(self.control.GetLangId()))

    def OnUpdatePageText(self, evt):
        """Update the title text of the current page
        @param evt: event that called this handler
        @type evt: stc.EVT_STC_MODIFY
        @note: this method must complete its work very fast it gets
               called everytime a character is entered or removed from
               the document.

        """
        pg_num = self.GetSelection()
        title = self.GetPageText(pg_num)
        if self.control.GetModify():
            title = u"*" + title
        if title != FNB.FlatNotebook.GetPageText(self, pg_num):
            wx.CallAfter(self.SetPageText, pg_num, title)
        
    def UpdateTextControls(self):
        """Updates all text controls to use any new settings that have
        been changed since initialization.
        @postcondition: all stc controls in the notebook are reconfigured
                        to match profile settings

        """
        for control in self.GetTextControls():
            control.UpdateAllStyles()
            control.Configure()

#---- End Function Definitions ----#

#-----------------------------------------------------------------------------#

#---- Utility Function Definitions ----#
def PromptToReSave(win, cfile):
    """Show a dialog prompting to resave the current file
    @param cfile: the file in question

    """
    mdlg = wx.MessageDialog(win.frame,
                            _("%s has been deleted since its "
                              "last save point.\n\nWould you "
                              "like to save it again?") % cfile,
                            _("Resave File?"), 
                            wx.YES_NO | wx.ICON_INFORMATION)
    mdlg.CenterOnParent()
    result = mdlg.ShowModal()
    mdlg.Destroy()
    if result == wx.ID_YES:
        win.control.SaveFile(cfile)
    else:
        win.control.SetModTime(0)

def AskToReload(win, cfile):
    """Show a dialog asking if the file should be reloaded
    @param cfile: the file to prompt for a reload of

    """
    mdlg = wx.MessageDialog(win.frame, 
                            _("%s has been modified by another "
                              "application.\n\nWould you like "
                              "to Reload it?") % cfile, 
                              _("Reload File?"),
                              wx.YES_NO | wx.ICON_INFORMATION)
    mdlg.CenterOnParent()
    result = mdlg.ShowModal()
    mdlg.Destroy()
    if result == wx.ID_YES:
        ret, rmsg = win.control.ReloadFile()
        if not ret:
            mdlg = wx.MessageDialog(win.frame, 
                                    _("Failed to reload %s:\n"
                                      "Error: %s") % \
                                      (cfile, rmsg),
                                    _("Error"),
                                    wx.OK | wx.ICON_ERROR)
            mdlg.ShowModal()
            mdlg.Destroy()
    else:
        win.control.SetModTime(util.GetFileModTime(cfile))
