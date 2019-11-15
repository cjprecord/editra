###############################################################################
# Name: HistWin.py                                                            #
# Purpose: Window for showing and searching the revision history of a file    #
#          that is under source control.                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
History Window

Provides a revision history window that shows the list of revisions
for a specific file and its related log entries. The window also
provides interactive searching/filtering of revision entries by searching
the log entries.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: HistWin.py 1406 2011-06-06 23:53:08Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1406 $"

#--------------------------------------------------------------------------#
# Imports
import wx
import re
import sys

# Local Imports
from projects.SourceControl import DecodeString
import projects.ScCommand as ScCommand
import projects.ProjCmnDlg as ProjCmnDlg

# Editra Library Imports
import util
import eclib

#--------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#--------------------------------------------------------------------------#

DATE_FORMAT = '%Y-%m-%d %I:%M %p'

edEVT_UPDATE_ITEMS = wx.NewEventType()
EVT_UPDATE_ITEMS = wx.PyEventBinder(edEVT_UPDATE_ITEMS, 1)
class UpdateItemsEvent(wx.PyCommandEvent):
    """Event to signal that items need updating"""
    def __init__(self, etype, eid, value=[]):
        super(UpdateItemsEvent, self).__init__(etype, eid)
        self._value = value

    def GetValue(self):
        """Get event value"""
        return self._value

#--------------------------------------------------------------------------#

SB_INFO = 0
SB_PROG = 1
class HistoryWindow(wx.Frame):
    """Window for displaying the Revision History of a file"""
    def __init__(self, parent, title, node, data):
        super(HistoryWindow, self).__init__(parent, title=title,
                                            style=wx.DEFAULT_DIALOG_STYLE)

        # Set Frame Icon
        if wx.Platform == '__WXMAC__':
            self._accel = wx.AcceleratorTable([(wx.ACCEL_CMD, ord('W'), wx.ID_CLOSE)])
        else:
            self._accel = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('W'), wx.ID_CLOSE)])
        self.SetAcceleratorTable(self._accel)
        util.SetWindowIcon(self)

        # Attributes
        statbar = eclib.ProgressStatusBar(self)
        statbar.SetStatusWidths([-1, 125])
        self.SetStatusBar(statbar)
        self._ctrls = HistoryPane(self, node, data)

        # Layout
        self._DoLayout()
        self.SetInitialSize()
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_MENU, lambda evt: self.Close(), id=wx.ID_CLOSE)

    def _DoLayout(self):
        """Layout the controls"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._ctrls, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def OnClose(self, evt):
        """Cleanup on exit"""
        self.Destroy()

    def OnContextMenu(self, evt):
        """For some reason the context menu from the projects pane gets shown
        on this window when a right click is sent. Not sure if this is a bug
        in the handling of the events in this code or in wx. This is just a
        handler to trap the event before it propagates to the project pane when
        the click is originated here.

        """
        evt.StopPropagation()

    def Show(self, show=True):
        """Show and center the dialog"""
        self.CenterOnScreen()
        super(HistoryWindow, self).Show(show)

    def StartBusy(self):
        """Start the window as busy"""
        self.SetStatusText(_("Retrieving File History") + u"...", SB_INFO)
        wx.CallAfter(self.GetStatusBar().StartBusy)

    def StopBusy(self):
        """Start the window as busy"""
        self.SetStatusText(u"", SB_INFO)
        wx.CallAfter(self.GetStatusBar().StopBusy)

#-----------------------------------------------------------------------------#

class HistoryPane(wx.Panel):
    """Panel for housing the the history window controls"""
    def __init__(self, parent, node, data):
        super(HistoryPane, self).__init__(parent)

        # Attributes
        self.srcCtrl = ScCommand.SourceController(self)

        # Note box sizer must be created before its siblings
        sbox = wx.StaticBox(self, label=_("Revision History"))
        self.boxsz = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        self._search = LogSearch(self, size=(150, -1))
        self._split = wx.SplitterWindow(self,
                                        style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)
        self._list = HistList(self._split)
        self._txt = wx.TextCtrl(self._split,
                                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self._btn = wx.Button(self, label=_("Compare Revisions"))
        self._btn.Disable()
        self.path = data['path']
        self.selected = -1

        # Layout
        self._DoLayout()
        self._txt.SetFocus()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, self._btn)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        self.Bind(ScCommand.EVT_DIFF_COMPLETE, self.OnEndScCommand)
        self.Bind(ScCommand.EVT_CMD_COMPLETE, self.OnEndScCommand)

        # Start lookup
        wx.CallAfter(self.GetParent().StartBusy)
        self.srcCtrl.ScCommand([(node, data)], 'history', self._list.Populate)

    def _DoLayout(self):
        """Layout the controls on the panel"""
        self.SetMinSize((550, -1))

        # Split Window
        self._split.SetMinimumPaneSize(80)
        self._split.SetMinSize((400, 350))
        self._split.SetSashSize(8)
        self._split.SplitHorizontally(self._list, self._txt, 250)
        self.boxsz.Add(self._search, 0, wx.ALIGN_RIGHT)
        self.boxsz.Add((10, 10))
        self.boxsz.Add(self._split, 1, wx.EXPAND)

        # Button sizer
        vsizer = wx.BoxSizer(wx.VERTICAL)
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)
        btn_sz.AddStretchSpacer()
        btn_sz.Add(self._btn, 0, wx.ALIGN_RIGHT)
        vsizer.AddMany([((12, 12)), (self.boxsz, 1, wx.EXPAND), ((8, 8)),
                        (btn_sz, 0, wx.ALIGN_RIGHT), ((12, 12))])

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([((8, 8)), (vsizer, 1, wx.EXPAND), ((8, 8))])
        self.SetSizer(sizer)

    def GetHistoryList(self):
        """Get the ListCtrl used by this window"""
        return self._list

    def OnButton(self, evt):
        """Handle button events"""
        self.GetParent().StartBusy()
        self._btn.Enable(False)
        selected = self.getSelectedItems()
        if not selected:
            self.srcCtrl.CompareRevisions(self.path)
        elif len(selected) == 1:
            rev = self._list.GetItem(selected[0], self._list.REV_COL)
            rev = rev.GetText().strip()
            self.srcCtrl.CompareRevisions(self.path, rev1=rev)
        else:
            rev1 = self._list.GetItem(selected[0], self._list.REV_COL).GetText().strip()
            rev2 = self._list.GetItem(selected[-1], self._list.REV_COL).GetText().strip()
            self.srcCtrl.CompareRevisions(self.path, rev1=rev1, rev2=rev2)

    def OnEndScCommand(self, evt):
        """Handle when a source control event has completed"""
        etype = evt.GetEventType()
        if etype == ScCommand.ppEVT_DIFF_COMPLETE:
            self._btn.Enable(True)
            self.GetParent().StopBusy()
            # Check for error in running diff command
            if evt.Error == ScCommand.SC_ERROR_RETRIEVAL_FAIL:
                ProjCmnDlg.RetrievalErrorDlg(self)

    def getSelectedItems(self):
        """ Get the selected items """
        item = -1
        selected = []
        while True:
            item = self._list.GetNextItem(item, wx.LIST_NEXT_ALL,
                                          wx.LIST_STATE_SELECTED)
            if item == -1:
                break
            selected.append(item)
        return selected

    def selectOnly(self, indices):
        """ Select only the given indices """
        item = -1
        while True:
            item = self._list.GetNextItem(item, wx.LIST_NEXT_ALL,
                                          wx.LIST_STATE_SELECTED)
            if item == -1:
                break
            if item not in indices:
                self._list.SetItemState(item, 0, wx.LIST_STATE_SELECTED)

    def OnItemSelected(self, evt):
        """Update text control when an item is selected in the
        list control.

        """
        self._btn.Enable()
        index = evt.GetIndex()
        rev = self._list.GetItem(index, self._list.REV_COL).GetText()
        date = self._list.GetItem(index, self._list.DATE_COL).GetText()
        self._txt.SetValue(self._list.GetFullLog(rev, date))
        self.updateButton()
        self.selectOnly((index, self.selected))
        self.selected = index

    def OnItemDeselected(self, evt):
        """Update text control when an item is selected in the
        list control.

        """
        selected = self.getSelectedItems()
        if not(selected):
            self.selected = -1
            self._btn.Disable()
        elif len(selected) == 1:
            self.selected = selected[0]
        self.updateButton()

    def updateButton(self):
        """ Change button text based on selection state """
        selected = self.getSelectedItems()
        if not selected:
            self._btn.SetLabel(_("Compare Revisions"))
        elif len(selected) == 1:
            self._btn.SetLabel(_("Compare to Selected Revision"))
        else:
            self._btn.SetLabel(_("Compare Selected Revisions"))

        self.Layout()
        self.GetParent().SendSizeEvent()
        self.GetParent().Layout()

#-----------------------------------------------------------------------------#

class HistList(eclib.EBaseListCtrl):
    """List for displaying a files revision history"""
    REV_COL  = 0
    DATE_COL = 1
    AUTH_COL = 2
    COM_COL  = 3
    def __init__(self, parent):
        """ Create the list control """
        super(HistList, self).__init__(parent, 
                                       style=wx.LC_REPORT|wx.LC_VRULES)

        # Attributes
        self._frame = parent.GetTopLevelParent()
        self._data = {}

        # Event Handlers
        self.Bind(EVT_UPDATE_ITEMS, self.OnUpdateItems)

        # Setup columns
        self.InsertColumn(self.REV_COL, _("Rev #"))
        self.InsertColumn(self.DATE_COL, _("Date"))
        self.InsertColumn(self.AUTH_COL, _("Author"))
        self.InsertColumn(self.COM_COL, _("Log Message"))

        self.SendSizeEvent()

    def OnUpdateItems(self, evt):
        """ Update and add items to the list """
        if not self._data:
            dlg = wx.MessageDialog(self,
               _('The history information for the requested file could ' \
                 'not be retrieved.  Please make sure that you have ' \
                 'network access.'),
               _('History information could not be retrieved'),
               style=wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.GetGrandParent().GetParent().Destroy()
            return

        index = -1
        append = False
        self.Freeze()
        for item in self._data:
            # Shorten log message for list item
            if 'shortlog' not in item:
                item['shortlog'] = log = item['log'].strip()
                if len(log) > 45:
                    log = DecodeString(log[:45]) + u'...'
                    item['shortlog'] = log

            # Create a key for searching all fields
            if 'key' not in item:
                unilog = DecodeString(item['log'])
                item['key'] = ('%s %s %s %s' % (item['revision'],
                                               item['date'].strftime(DATE_FORMAT),
                                               item['author'],
                                               re.sub(r'\s+', u' ', unilog))).lower()

            if append:
                index = self.InsertStringItem(sys.maxint, u'')
            else:
                index = self.GetNextItem(index)
                if index == -1:
                    append = True
                    index = self.InsertStringItem(sys.maxint, u'')

            if self.GetItemText(index).strip() != item['revision']:
                self.SetStringItem(index, 0, item['revision'])
                self.SetStringItem(index, 1, item['date'].strftime(DATE_FORMAT))
                self.SetStringItem(index, 2, item['author'])
                self.SetStringItem(index, 3, item['shortlog'])

        # We never got to append mode, delete the extras
        if not append:
            for i in range(self.GetItemCount()-1, index, -1):
                self.DeleteItem(i)

        self.Thaw()

    def GetFullLog(self, rev, timestamp):
        """Get the full log entry for the given revision"""
        for item in self._data:
            if item['revision'] == rev and \
               item['date'].strftime(DATE_FORMAT) == timestamp:
                return item['log']
        else:
            return wx.EmptyString

    def Populate(self, data):
        """Populate the list with the history data
        @note: called from background thread!

        """
        if data:
           data.sort(key=lambda x: x['date'], reverse=True) 
        self._data = data
        wx.PostEvent(self, UpdateItemsEvent(edEVT_UPDATE_ITEMS, -1, data))
        wx.CallAfter(self._frame.StopBusy)

    def Filter(self, query):
        """ Filter list entries based on search query """
        query = [x for x in query.strip().lower().split() if x]
        if query:
            newdata = []
            for item in self._data:
                i = 0
                for word in query:
                    if word in item['key']:
                        i += 1
                if i == len(query):
                    newdata.append(item)
        else:
            newdata = self._data

        evt = UpdateItemsEvent(edEVT_UPDATE_ITEMS, self.GetId(), newdata)
        wx.PostEvent(self, evt)

#-----------------------------------------------------------------------------#

class LogSearch(wx.SearchCtrl):
    """Control for filtering history entries by searching log data"""
    def __init__(self, parent, value="", \
                 pos=wx.DefaultPosition, size=wx.DefaultSize, \
                 style=wx.TE_PROCESS_ENTER | wx.TE_RICH2):
        """Initializes the Search Control"""
        super(LogSearch, self).__init__(parent, wx.ID_ANY, value,
                                        pos, size, style)

        # Attributes

        # Appearance
        self.SetDescriptiveText(_("Search Log"))

        # Event Handlers
        # HACK, needed on Windows to get key events
        if wx.Platform == '__WXMSW__':
            self.ShowCancelButton(False)
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
                    break

        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        self.Bind(wx.EVT_KEY_UP, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)

    def OnCancel(self, evt):
        """Clear the search"""
        self.SetValue(u"")
        self.ShowCancelButton(False)
        evt.Skip()

    def OnSearch(self, evt):
        """Search logs and filter"""
        self.GetParent().GetHistoryList().Filter(self.GetValue())

#-----------------------------------------------------------------------------#
