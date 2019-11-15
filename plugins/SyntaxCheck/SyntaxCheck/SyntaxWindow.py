# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Syntax Checker plugin                                              #
# Author: Giuseppe "Cowo" Corbelli                                            #
# Copyright: (c) 2009 Giuseppe "Cowo" Corbelli                                #
# License: wxWindows License                                                  #
###############################################################################

"""Editra Shelf display window"""

__author__ = "Giuseppe 'Cowo' Corbelli"
__svnid__ = "$Id: SyntaxWindow.py 1223 2011-04-06 15:20:53Z CodyPrecord $"
__revision__ = "$Revision: 1223 $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.mixins.listctrl as mixins

# Editra Libraries
import util
import ed_basewin
import ed_msg
import syntax.synglob as synglob
import eclib.elistmix as elistmix

# Syntax checkers
from PhpSyntaxChecker import PhpSyntaxChecker
from PythonSyntaxChecker import PythonSyntaxChecker

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class FreezeDrawer(object):
    """To be used in 'with' statements. Upon enter freezes the drawing
    and thaws upon exit.

    """
    def __init__(self, wnd):
        self._wnd = wnd

    def __enter__(self):
        self._wnd.Freeze()

    def __exit__(self, eT, eV, tB):
        self._wnd.Thaw()

#-----------------------------------------------------------------------------#

class SyntaxCheckWindow(wx.Panel):
    """Syntax Check Results Window"""
    __syntaxCheckers = {
        synglob.ID_LANG_PYTHON: PythonSyntaxChecker,
        synglob.ID_LANG_PHP: PhpSyntaxChecker
    }

    def __init__(self, parent):
        """Initialize the window"""
        wx.Panel.__init__(self, parent)

        # Attributes
        # Parent is ed_shelf.EdShelfBook
        self._mw = parent
        self._log = wx.GetApp().GetLog()
        self._listCtrl = CheckResultsList(
            self, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SORT_ASCENDING
        )

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self._listCtrl, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(vbox)
        self.SetAutoLayout(True)

        ed_msg.Subscribe(self.OnFileSaved, ed_msg.EDMSG_FILE_SAVED)
        
    def __del__(self):
        ed_msg.Unsubscribe(self.OnFileSaved, ed_msg.EDMSG_FILE_SAVED)

    def GetMainWindow(self):
        return self._mw

    #~ @ed_msg.mwcontext
    def OnFileSaved(self, arg):
        """File Saved message"""
        (fileName, fileType) = arg.GetData()
        util.Log("[SyntaxCheckWindow][info] fileName %s" % (fileName))
        try:
            syntaxChecker = self.__syntaxCheckers[fileType]
        except Exception, msg:
            util.Log("[SyntaxCheckWindow][info] Error while checking %s: %s" % (fileName, msg))
            return
        
        #Something like [('Syntax Error', '__all__ = ["CSVSMonitorThread"]', 7)]
        data = syntaxChecker.Check(fileName)
        
#        with FreezeDrawer(self._listCtrl):
        self._listCtrl.Freeze()
        self._listCtrl.DeleteOldRows(fileName)
        if len(data) != 0:
            self._listCtrl.PopulateRows(fileName, data)
            self._listCtrl.RefreshRows()
        self._listCtrl.Thaw()

#-----------------------------------------------------------------------------#

class CheckResultsList(wx.ListCtrl,
                       mixins.ListCtrlAutoWidthMixin,
                       elistmix.ListRowHighlighter):
    """List control for displaying syntax check results"""
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        mixins.ListCtrlAutoWidthMixin.__init__(self)
        elistmix.ListRowHighlighter.__init__(self)

        # Attributes
        self._mainw = ed_basewin.FindMainWindow(self)
        self._charWidth = self.GetCharWidth()

        # Setup
        self.InsertColumn(0, _("Type"))
        self.InsertColumn(1, _("Error"))
        self.InsertColumn(2, _("File"))
        self.InsertColumn(3, _("Line"))
        # Auto-resize file
        self.setResizeColumn(3)

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivate)

    def OnItemActivate(self, evt):
        """Go to the error in the file"""
        idx = evt.GetIndex()
        fileName = self.GetItem(idx, 2).GetText()
        lineNo = int(self.GetItem(idx, 3).GetText())
        try:
            _OpenToLine(fileName, max(0, lineNo - 1), self._mainw)
        except:
            pass

    def DeleteOldRows(self, filename):
        """Delete all the rows that refer to a certain filename
        @param filename: unicode
        """
        for itemIndex in reversed(xrange(0, self.GetItemCount())):
            if (self.GetItem(itemIndex, 2).GetText() == filename):
                self.DeleteItem(itemIndex)
        
    def PopulateRows(self, filename, data):
        """Populate the list with the data
        @param filename: unicode
        @param data: list of tuples (errorType, errorText, errorLine)

        """
        editor = _GetEditorForFile(filename, self._mainw)
        if (not editor):
            return
        encoding = editor.GetDocument().GetEncoding()
        typeText = _("Type")
        errorText = _("Error")
        minLType = max(self.GetTextExtent(typeText)[0], self.GetColumnWidth(0))
        minLText = max(self.GetTextExtent(errorText)[0], self.GetColumnWidth(1))
        for (eType, eText, eLine) in data:
            minLType = max(minLType, self.GetTextExtent(eType)[0])
            minLText = max(minLText, self.GetTextExtent(eText)[0])
            #For some reason a simple Append() does not seem to work...
            lineNo = self.GetItemCount()
            lineNo = self.InsertStringItem(lineNo, unicode(eType))
            for (col, txt) in [ (1, unicode(eText, encoding)), (2, filename), (3, unicode(eLine)) ]:
                self.SetStringItem(lineNo, col, txt)
        self.SetColumnWidth(0, minLType)
        self.SetColumnWidth(1, minLText)
        
#-----------------------------------------------------------------------------#

def _OpenToLine(fname, line, mainw):
    """Open the given filename to the given line number and select the page
    @param fname: File name to open, relative paths will be converted to abs
                  paths.
    @param line: Line number to set the cursor to after opening the file
    @param mainw: MainWindow instance to open the file in

    """
    nb = mainw.GetNotebook()
    editor = _GetEditorForFile(fname, mainw)
    if (editor is None):
        nb.OnDrop([fname])
        editor = _GetEditorForFile(fname, mainw)
    
    nb.ChangePage(editor.GetTabIndex())
    editor.GotoLine(line)
    
def _GetEditorForFile(fname, mainw):
    """Return the EdEditorView that's managing the file, if available
    @param fname: File name to open
    @param mainw: MainWindow instance to open the file in
    @return: Text control managing the file
    @rtype: ed_editv.EdEditorView
    
    """
    nb = mainw.GetNotebook()
    for page in nb.GetTextControls():
        if page.GetFileName() == fname:
            return nb.GetPage(page.GetTabIndex())
    
    return None

def _printListCtrl(ctrl):
    for row in xrange(0, ctrl.GetItemCount()):
        for column in xrange(0, ctrl.GetColumnCount()):
            print ctrl.GetItem(row, column).GetText(), "\t",
        print ""
