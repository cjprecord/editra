# -*- coding: utf-8 -*-
# Name: StackThreadShelfWindow.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: StackThreadShelfWindow.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import ed_glob
import eclib

# Local imports
from PyStudio.Common.BaseShelfWindow import BaseShelfWindow
from PyStudio.Debugger.StackFrameList import StackFrameList
from PyStudio.Debugger.ThreadsList import ThreadsList
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger

# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class StackThreadShelfWindow(BaseShelfWindow):
    def __init__(self, parent):
        """Initialize the window"""
        super(StackThreadShelfWindow, self).__init__(parent)

        # Attributes
        self.prevstack = None
        self.current_thread = None
        self.threads_list = None
        bstyle = eclib.SEGBOOK_STYLE_NO_DIVIDERS|eclib.SEGBOOK_STYLE_LEFT
        self._nb = eclib.SegmentBook(self, style=bstyle)
        self._stackframe = StackFrameList(self._nb)
        self._threads = ThreadsList(self._nb)

        # Setup
        self._InitImageList()
        self._nb.AddPage(self._stackframe, _("Stack Frame"), img_id=0)
        self._nb.AddPage(self._threads, _("Threads"), img_id=1)
        ctrlbar = self.setup(self._nb, self._stackframe,
                             self._threads)
        ctrlbar.AddStretchSpacer()
        self.layout()

        # Debugger Attributes
        RpdbDebugger().clearframe = self.ClearStackList
        RpdbDebugger().selectframe = self._stackframe.select_frame
        RpdbDebugger().updatestacklist = self.UpdateStackList
        RpdbDebugger().clearthread = self.ClearThreadList
        RpdbDebugger().updatethread = self._threads.update_thread
        RpdbDebugger().updatethreadlist = self.UpdateThreadList

        RpdbDebugger().update_stack()
        current_thread, threads_list = RpdbDebugger().get_thread_list()
        self.UpdateThreadList(current_thread, threads_list)

    def _InitImageList(self):
        """Initialize the segmentbooks image list"""
        dorefresh = False
        if len(self._imglst):
            del self._imglst
            self._imglst = list()
            dorefresh = True

        # TODO: add find better Bitmaps
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_VARIABLE_TYPE), wx.ART_MENU)
        self._imglst.append(bmp)
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU)
        self._imglst.append(bmp)
        self._nb.SetImageList(self._imglst)
        self._nb.SetUsePyImageList(True)

        if dorefresh:
            self._nb.Refresh()

    def Unsubscription(self):
        """Cleanup on Destroy"""
        RpdbDebugger().clearframe = lambda:None
        RpdbDebugger().selectframe = lambda x:None
        RpdbDebugger().updatestacklist = lambda x:None
        RpdbDebugger().clearthread = lambda:None
        RpdbDebugger().updatethread = lambda x,y,z:None
        RpdbDebugger().updatethreadlist = lambda x,y:None

    def UpdateStackList(self, stack):
        """Update stack information ListCtrl"""
        if not stack or self.prevstack == stack:
            return
        self.prevstack = stack
        self._stackframe.Clear()
        self._stackframe.PopulateRows(stack)
        self._stackframe.RefreshRows()

    def ClearStackList(self):
        """Clear the ListCtrl"""
        self.prevstack = None
        self._stackframe.Clear()

    def UpdateThreadList(self, current_thread, threads_list):
        if not threads_list:
            return
        if self.current_thread == current_thread and self.threads_list == threads_list:
            return
        self.current_thread = current_thread
        self.threads_list = threads_list
        self._threads.Clear()
        self._threads.PopulateRows(current_thread, threads_list)
        self._threads.RefreshRows()

    def ClearThreadList(self):
        self.current_thread = None
        self.threads_list = None
        self._threads.Clear()
