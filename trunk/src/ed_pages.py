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
# FILE: ed_pages.py                                                        #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
# This file contains the definition of the class to handle the tabbed text #
# controls and all functions relating to the subpanel of the MainWindow    #
# class implimented in MainWindow.py. It will also manage and create the   #
# editra controls for the MainWindow.                                      #
#                                                                          #
# METHODS:                                                                 #
# - ED_Pages: Main instance of class. tracks page numbers                  #
# - NewPage: Creates a new empty page w/text control                       #
# - OpenPage: Opens a new page with an existing file                       #
# - GoCurrentPage: Sets focus to currentyl selected page                   #
# - OnPageChanging:                                                        #
# - OnPageChanged: Captures page change and switches context to the        #
#                  new page                                                #
# - ClosePage: Closes a page in the notebook                               #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies

import os
import sys
import re
import wx
import ed_glob
import ed_stc
import ed_search
import util
import doctools
import wx.lib.flatnotebook as FNB

#---- Class Globals ----#
# HACK till proper artprovider can be written
IMG = {}

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
class ED_Pages(FNB.FlatNotebook):
    """ Editra tabbed pages class """
    def __init__(self, parent, id_num):
        """Initialize a notebook with a blank text control in it"""
        FNB.FlatNotebook.__init__(self, parent, id_num, 
                                  style=FNB.FNB_FANCY_TABS | 
                                        FNB.FNB_X_ON_TAB | 
                                        FNB.FNB_SMART_TABS |
                                        FNB.FNB_BACKGROUND_GRADIENT
                            )

        # Notebook attributes
        self.LOG = wx.GetApp().GetLog()
        self.FindService = ed_search.TextFinder(self, self.GetCurrentCtrl)
        self.DocMgr = doctools.DocPositionMgr(ed_glob.CONFIG['CACHE_DIR'] + \
                                              util.GetPathChar() + u'positions')
        self.pg_num = 0               # Track page numbers for ID creation
        self.control = ed_stc.EDSTC   # Current Control page
        self.frame = parent.GetParent() # MainWindow

        # Set Additional Style Parameters
        self.SetNonActiveTabTextColour(wx.ColourRGB(long("666666", 16)))

        # Notebook Events
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.OnPageClosing)
        self.Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClosed)
        self._pages.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        self.CreateImageList()

        # Add a blank page
        self.NewPage()

    #---- End Init ----#

    #---- Function Definitions ----#
    def AddPage(self, control, title):
        """Adds a page to the notebook"""
        self.pg_num += 1
        FNB.FlatNotebook.AddPage(self, control, title)

    def GetCurrentCtrl(self):
        """Returns the control of the currently selected
        page in the notebook.

        """
        if hasattr(self, 'control'):
            return self.control
        else:
            return None

    def NewPage(self):
        """Create a new notebook page with a blank text control"""
        self.control = ed_stc.EDSTC(self, self.pg_num)
        self.LOG("[nb_evt] Page Creation ID: " + str(self.control.GetId()))
        self.AddPage(self.control, u"Untitled - " + str(self.pg_num))
        self.SetPageImage(self.GetSelection(), IMG['TXT'])

    def OpenPageType(self, page):
        """A Generic Page open Function to allow pages to contain
        any type of widget.

        """
        
    def OpenPage(self, path, filename):
        """Open a File Inside of a New Page"""
        # build path and check type
        path2file = os.path.join(path, filename)
        # Check if file exists and is actually a file
        if os.path.exists(path2file) and (not os.path.isfile(path2file)):
            return

        if self.HasFileOpen(path2file):
            mdlg = wx.MessageDialog(self,
                                    _("File is already open in an existing page."
                                      "\nDo you wish to open it again?"),
                                    _("Open File") + u"?", 
                                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION)
            result = mdlg.ShowModal()
            mdlg.Destroy()
            if result == wx.ID_NO:
                return

        # Create control to place text on
        self.control = ed_stc.EDSTC(self, self.pg_num)

        # Pass directory and file name info to control object to save reference
        self.control.dirname = path
        self.control.filename = filename

        # Put control into page an place page in notebook
        self.AddPage(self.control, self.control.filename)

        # Open file and put text into the control
        if os.path.exists(path2file):
            #self.control.LoadFile(path2file)
            try:
                f = open(path2file, "rb")
                self.control.SetText(util.EncodeRawText(f.read()))
                f.close()
                self.frame.filehistory.AddFileToHistory(path2file)
            except:
                wx.MessageBox(_("There was an error while opening the file"))
        else:
            # Set Tab title for blank new file
            self.SetPageText(self.GetSelection(), self.control.filename)
        self.LOG("[nb_evt] Opened Page: ID = " + str(self.GetSelection()))

        # Set style
        self.control.FindLexer()

        # Clear Undo Buffer of this control
        self.control.EmptyUndoBuffer()

        if ed_glob.PROFILE['SAVE_POS']:
            self.control.GotoPos(self.DocMgr.GetPos(self.control.GetFileName()))

        # Set tab image
        ftype = self.control.filename.split(".")
        ftype = ftype[-1].upper()
        pg_num = self.GetSelection()
        if ftype in IMG:
            self.LOG("[nb_info] Set Page Image to: " + ftype)
            self.SetPageImage(pg_num, IMG[ftype])
        else:
            self.SetPageImage(pg_num, IMG['TXT'])

        # Refocus on selected page
        self.GoCurrentPage()

    def GoCurrentPage(self):
        """Move Focus to Currently Selected Page"""
        current_page = self.GetSelection()
        if current_page < 0:
            return current_page

        self.LOG("[nb_info] Current Page = " + str(current_page))

        control = self.GetPage(current_page)
        control.SetFocus()
        self.control = control
        return current_page

    def GetTextControls(self):
        """Gets all the currently oppend text controls"""
        children = self.GetChildren()
        controls = list()
        for child in children:
            if hasattr(child, '__name__') and child.__name__ == u"EditraTextCtrl":
                controls.append(child)
        return controls

    def HasFileOpen(self, fpath):
        """Checks if one of the currently active buffers has
        the named file in it.

        """
        ctrls = self.GetTextControls()
        for ctrl in ctrls:
            if fpath == os.path.join(ctrl.dirname, ctrl.filename):
                return True
        return False

    #---- Event Handlers ----#
    def OnDrop(self, files):
        """Opens drop files"""
        # Check file properties and make a "clean" list of file(s) to open
        valid_files = list()
        for fname in files:
            self.LOG("[fdt_evt] File(s) Dropped: " + fname)
            if (not os.path.exists(fname)) or (not os.path.isfile(fname)):
                self.frame.PushStatusText(_("Invalid file: %s") % fname, ed_glob.SB_INFO)
            else:
                valid_files.append(fname)

        for fname in valid_files:
            pathname = util.GetPathName(fname)
            the_file = util.GetFileName(fname)
            self.OpenPage(pathname, the_file)
            self.frame.PushStatusText(_("Opened file: %s") % fname, ed_glob.SB_INFO)
        return

    def OnLeftUp(self, evt):
        """Traps clicks sent to page close buttons and 
        redirects the action to the ClosePage function

        """
        cord, tabIdx = self._pages.HitTest(evt.GetPosition())
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
        """Page changing event handler."""
        self.LOG("[nb_evt] Page Changed to " + str(evt.GetSelection())) 
        evt.Skip()

    def OnPageChanged(self, evt):
        """Actions to do after a page change"""
        current = evt.GetSelection()
        window = self.GetPage(current) #returns current stc
        window.SetFocus()
        self.control = window

        if self.control.filename == "":
            self.control.filename = "Untitled - " + str(window.GetId())

        self.frame.SetTitle(self.control.filename + " - " + "file://" + 
                      self.control.dirname + self.control.path_char + 
                      self.control.filename + " - " + ed_glob.prog_name + " v" + ed_glob.version)

        matchstrn = re.compile('Untitled*')
        if matchstrn.match(self.control.filename):
            self.control.filename = ""

        self.control.Bind(wx.EVT_KEY_UP, self.frame.OnKeyUp)

        self.LOG("[nb_evt] Control Changing from Page: " + str(evt.GetOldSelection()) + 
                " to Page: " + str(evt.GetSelection()) + "\n" +
                "[nb_info] It has file named: " + self.control.filename + "\n" +
                "[nb_info] In DIR: " + self.control.dirname)
        self.frame.UpdateToolBar()
        evt.Skip()

    def OnPageClosing(self, evt):
        """Checks page status to flag warnings before closing"""
        self.LOG("[nb_evt] Closing Page: #" + str(self.GetSelection()))
        pg = self.GetCurrentPage()
        if len(pg.GetFileName()) > 1:
            self.DocMgr.AddRecord([pg.GetFileName(), pg.GetCurrentPos()])
        evt.Skip()

    def OnPageClosed(self, evt):
        """Handles Paged Closed Event"""
        self.LOG("[nb_evt] Closed Page: #" + str(self.GetSelection()))
        evt.Skip()
    #---- End Event Handlers ----#

    def ClosePage(self):
        """Closes Currently Selected Page"""
        self.GoCurrentPage()
        pg_num = self.GetSelection()
        result = wx.ID_OK
        try:
            act = self.control.GetModify()
        except AttributeError:
            act = False

        if act:
            result = self.frame.ModifySave()
            if result != wx.ID_CANCEL:
                self.DeletePage(pg_num)
                self.GoCurrentPage()
            else:
                pass
        else:
            self.DeletePage(pg_num)
            self.GoCurrentPage()

        return result

    def CreateImageList(self):
        """Creates the image list for the tabs buttons."""
        #HACK should use themimetypemanager to handle filetypes/images ect
        #     just cant seem to get it to work properly on the mac right now.
        # Get Images
        img_dir = ed_glob.CONFIG['MIME_DIR']
        IMG["C"] = wx.Bitmap(img_dir + "c.png", wx.BITMAP_TYPE_PNG)
        IMG["CPP"] = wx.Bitmap(img_dir + "cpp.png", wx.BITMAP_TYPE_PNG)
        IMG["CSS"] = wx.Bitmap(img_dir + "css.png", wx.BITMAP_TYPE_PNG)
        IMG["H"] = wx.Bitmap(img_dir + "header.png", wx.BITMAP_TYPE_PNG)
        IMG["HTML"] = wx.Bitmap(img_dir + "html.png", wx.BITMAP_TYPE_PNG)
        IMG["JAVA"] = wx.Bitmap(img_dir + "java.png", wx.BITMAP_TYPE_PNG)
        IMG["MAKEFILE"] = wx.Bitmap(img_dir + "makefile.png", wx.BITMAP_TYPE_PNG)
        IMG["PL"] = wx.Bitmap(img_dir + "perl.png", wx.BITMAP_TYPE_PNG)
        IMG["PHP"] = wx.Bitmap(img_dir + "php.png", wx.BITMAP_TYPE_PNG)
        IMG["PY"] = wx.Bitmap(img_dir + "python.png", wx.BITMAP_TYPE_PNG)
        IMG["RB"] = wx.Bitmap(img_dir + "ruby.png", wx.BITMAP_TYPE_PNG)
        IMG["SH"] = wx.Bitmap(img_dir + "shell.png", wx.BITMAP_TYPE_PNG)
        IMG["TCL"] = wx.Bitmap(img_dir + "tcl.png", wx.BITMAP_TYPE_PNG)
        IMG["TEX"] = wx.Bitmap(img_dir + "tex.png", wx.BITMAP_TYPE_PNG)
        IMG["TXT"] = wx.Bitmap(img_dir + "text.png", wx.BITMAP_TYPE_PNG)

        # Create Image List
        il = wx.ImageList(16, 16)

        # Add Images to List and store index in IMG dictionary
        IMG["C"] = il.Add(IMG["C"])
        IMG["CPP"] = il.Add(IMG["CPP"])
        IMG["CSS"] = il.Add(IMG["CSS"])
        IMG["H"] = il.Add(IMG["H"])
        IMG["HTML"] = il.Add(IMG["HTML"])
        IMG["JAVA"] = il.Add(IMG["JAVA"])
        IMG["MAKEFILE"] = il.Add(IMG["MAKEFILE"])
        IMG["PL"] = il.Add(IMG["PL"])
        IMG["PHP"] = il.Add(IMG["PHP"])
        IMG["PY"] = il.Add(IMG["PY"])
        IMG["RB"] = il.Add(IMG["RB"])
        IMG["SH"] = il.Add(IMG["SH"])
        IMG["TCL"] = il.Add(IMG["TCL"])
        IMG["TEX"] = il.Add(IMG["TEX"])
        IMG["TXT"] = il.Add(IMG["TXT"])

        # Set duplicate indexs
        IMG["CSH"] = IMG["SH"]
        IMG["KSH"] = IMG["SH"]

        self.SetImageList(il)
        self.LOG("[nb_info] Created Image List: Size = " + str(self.GetImageList().GetImageCount()))
        return 0

    def UpdatePageImage(self):
        """Updates the page tab image"""
        pg_num = self.GetSelection()
        ftype = self.control.filename.split(".")
        ftype = ftype[-1].upper()
        self.LOG("[nb_info] Updating Page Image: Page " + str(pg_num))
        if IMG.has_key(ftype):
            self.SetPageImage(pg_num, IMG[ftype])
        else:
            self.SetPageImage(pg_num, IMG["TXT"])

    def UpdateTextControls(self):
        """Updates all text controls to use any new settings that have
        been changed since initialization.

        """
        for control in self.GetTextControls():
            control.UpdateAllStyles()
            control.Configure()

#---- End Function Definitions ----#

