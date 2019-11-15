# -*- coding: utf-8 -*-
# Name: ThreadsList.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: ThreadsList.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import eclib

# Local Imports
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class ThreadsList(eclib.EBaseListCtrl):
    """List control for displaying thread thread results"""
    COL_ID = 0
    COL_NAME = 1
    COL_STATE = 2
    def __init__(self, parent):
        super(ThreadsList, self).__init__(parent)

        # Setup
        self.InsertColumn(ThreadsList.COL_ID, _("Thread Id"))
        self.InsertColumn(ThreadsList.COL_NAME, _("Name"))
        self.InsertColumn(ThreadsList.COL_STATE, _("State"))
        
        # Attributes
        self.previndex = None
        
        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnThreadSelected)

    def set_mainwindow(self, mw):
        self._mainw = mw

    def update_thread(self, thread_id, thread_name, fBroken):
        for index in range(self.GetItemCount()):
            tid = self.GetItem(index, ThreadsList.COL_ID).GetText()
            try:
                tid = int(tid)
                if tid == thread_id:
                    self.SetStringItem(index, ThreadsList.COL_NAME, thread_name)
                    self.SetStringItem(index, ThreadsList.COL_STATE, 
                                       [_("running"), _("waiting at breakpoint")][fBroken])
                    break
            except ValueError:
                pass # TODO: log it

    def OnThreadSelected(self, evt):
        index = evt.GetIndex()
        if self.previndex == index:
            return
        self.previndex = index
        tid = int(self.GetItem(index, ThreadsList.COL_ID).GetText())
        RpdbDebugger().set_thread(tid)
        
    def Clear(self):
        """Delete all the rows """
        self.DeleteAllItems()
        self.previndex = None

    def PopulateRows(self, current_thread, threads_list):
        """Populate the list with the data
        @param current_thread: current threads
        @param threads_list: list of threads

        """
        nameText = _("Name")
        stateText = _("State")
        minLName = max(self.GetTextExtent(nameText)[0], self.GetColumnWidth(1))
        minLState = max(self.GetTextExtent(stateText)[0], self.GetColumnWidth(2))
        
        selectedidx = None
        for idx, threadinfo in enumerate(threads_list):
            tid = threadinfo["tid"]
            name = threadinfo["name"]
            fBroken = threadinfo["broken"]

            ename = unicode(name)
            estate = [_("running"), _("waiting at breakpoint")][fBroken]
            minLName = max(minLName, self.GetTextExtent(ename)[0])
            minLState = max(minLState, self.GetTextExtent(estate)[0])
            self.Append((unicode(tid), ename, estate))
            self.SetItemData(idx, tid)
            if tid == current_thread:
                selectedidx = idx
            
        self.SetColumnWidth(ThreadsList.COL_NAME, minLName)
        self.SetColumnWidth(ThreadsList.COL_STATE, minLState)
        if selectedidx is not None:
            self.previndex = None
            self.Select(selectedidx)
