###############################################################################
# Name: diffwin.py                                                            #
# Purpose: Utilities for showing file diffs                                   #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: diffwin.py
# AUTHOR: Cody Precord
# LANGUAGE: Python
# SUMMARY:
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: diffwin.py 932 2010-02-03 03:59:04Z CodyPrecord $"
__revision__ = "$Revision: 932 $"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import os
import tempfile
import webbrowser

# Local libs
import difflib

# Editra libs
import ed_stc
import util

#--------------------------------------------------------------------------#

class DiffWindow(wx.Frame):
    """Creates a window for displaying file diffs"""
    def __init__(self, parent, id, title, files):
        """Initialize the Window"""
        wx.Frame.__init__(self, parent, id, title, size=(600, 400))
        
        self.CreateStatusBar()

        sizer = wx.BoxSizer(wx.VERTICAL)
#        self._book = DiffBook(self, files)
#        sizer.Add(self._book, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def OpenDiffs(self, flist):
        """Open a list of diffed files
        @param flist: list of file paths
        @type flist: [(a1, a2), (b1, b2), ...]

        """
        self._book.OpenFiles(flist)

#--------------------------------------------------------------------------#

class DisplayPanel(wx.Panel):
    """Creates a panel for displaying the diff in a side by side"""
    def __init__(self, parent, left, right):
        """Create the diff panel
        @param parent: parent window of this panel
        @param left: path to left file
        @param right: path to right file

        """
        wx.Panel.__init__(self, parent)
        
        # Attributes
        self._log = wx.GetApp().GetLog()
        self._left = (left, DiffCtrl(self))
        self._left[1].SetUseVerticalScrollBar(False)
        self._right = (right, DiffCtrl(self))
        self._difftxt = self.Generate()
        
        # Layout panel
        self._DoLayout()
        self._PopulateCtrls()

        # Event Handlers
#         self._left[1].Bind(wx.EVT_MOUSEWHEEL, self.OnScrollLeft)
        self._right[1].Bind(wx.EVT_MOUSEWHEEL, self.OnScrollRight)
        self._right[1].Bind(wx.EVT_SCROLLBAR, self.OnScrollRight)
        self._right[1].Bind(wx.EVT_SCROLLWIN, self.OnScrollRight)

    def _DoLayout(self):
        """Layout the window"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._left[1], 1, wx.EXPAND | wx.ALIGN_LEFT)
        sizer.Add(self._right[1], 1, wx.EXPAND | wx.ALIGN_RIGHT)
        self.SetSizer(sizer)
        self.SetInitialSize()

    def _PopulateCtrls(self):
        """Populate the text ctrls"""
        ltxt = GetLines(self._left[0])
        if ltxt != -1:
            for line in ltxt:
                self._left[1].AppendLine(line)
        rtxt = GetLines(self._right[0])
        if rtxt != -1:
            for line in rtxt:
                self._right[1].AppendLine(line)
        diffs = 0
        for item in self._difftxt:
            if item.startswith(u'+') or item.startswith(u'-'):
                diffs = diffs + 1
        self.GetTopLevelParent().SetStatusText("%d Differences" % diffs, 0)
        self._left[1].SetReadOnly(True)
        self._right[1].SetReadOnly(True)

    def Generate(self):
        """Generate the diff text from the displays left/right files
        and refresh the display.

        """
        diff = GenerateDiff(self._left[0], self._right[0])
        if isinstance(diff, int):
            if diff == ERR_DIFF_LFAILED:
                fname = self._left[0]
            else:
                fname = self._right[0]
            self._log("[diffwin][err] Failed to open %s" % fname)
        else:
            return diff

#     def OnScrollLeft(self, evt):
#         """Make both windows have matching scroll position"""
#         self._fromleft = True
#         if not self._fromRight:
#             wx.PostEvent(self._right[1], evt)
#         evt.Skip()

    def OnScrollRight(self, evt):
        """Make both windows have matching scroll position"""
        wx.PostEvent(self._left[1], evt)
        evt.Skip()

#--------------------------------------------------------------------------#
class DiffCtrl(ed_stc.EditraStc):
    """Custom text control for displaying diff files in"""
    def __init__(self, parent):
        ed_stc.EditraStc.__init__(self, parent, wx.ID_ANY, use_dt=False)
        
        # Configure the control
        self.FoldingOnOff(False)
#         self.SetReadOnly(True)

    def AppendLine(self, line):
        """Adds a line to the control. The line is checked
        for being a minus/plus line and colored properly for
        the context.

        """
        self.AppendText(line)

#--------------------------------------------------------------------------#
# Utility Functions

_tmpfiles = list()
ERR_DIFF_LFAILED = -1
ERR_DIFF_RFAILED = -2
# Unfortunatly wx.html.HtmlWindow does not handle the css generated
# by difflib so this will use an external webbrowser till wx.webkit
# is ready.
def GenerateDiff(left, right, tabwidth=8, html=False):
    """Generate the delta between the two files.
    @param left: path to left file
    @param right: path to right file
    @keyword tabwidth: tab stop spacing (only for html mode)
    @keyword html: If set to True the diff will be generated as HTML and
                   opened as a new tab in the systems webbrowser.

    """
    # Get Lines to diff
    lfile = GetLines(left)
    if lfile == -1:
        return ERR_DIFF_LFAILED

    rfile = GetLines(right)
    if rfile == -1:
        return ERR_DIFF_RFAILED

    if html:
        gen = difflib.HtmlDiff(tabwidth)
        diff = gen.make_file(lfile, rfile, left, right)
        tmp, name = tempfile.mkstemp('editra_projects_diff.html')
        _tmpfiles.append(name)
        tmp = file(name, 'wb')
        tmp.write(diff)
        tmp.close()
        webbrowser.open(name)
    else:
        return difflib.Differ().compare(lfile, rfile)

def CleanupTempFiles():
    """Cleanup all temporary diff files"""
    for tmp in _tmpfiles:
        try:
            os.remove(tmp)
        except OSError:
            pass

def GetLines(fname):
    """Gets all the lines from the given file
    @return: list of lines or -1 on error

    """
    reader = util.GetFileReader(fname)
    if reader != -1:
        try:
            lines = reader.readlines()
        except (AttributeError, IOError, OSError), msg:
            print msg
            return -1
        reader.close()
    else:
        lines = ['',]
    return lines
