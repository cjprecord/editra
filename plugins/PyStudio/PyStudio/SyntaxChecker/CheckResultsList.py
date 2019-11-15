# -*- coding: utf-8 -*-
# Name: CheckResultsList.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: CheckResultsList.py 1563 2012-08-18 21:00:33Z CodyPrecord $"
__revision__ = "$Revision: 1563 $"

#----------------------------------------------------------------------------#
# Imports
import wx
import wx.lib.mixins.listctrl as listmix

# Editra Libraries
import ed_msg
import ed_marker
import eclib

# Local imports
from PyStudio.Common.PyStudioUtils import PyStudioUtils

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class CheckResultsList(eclib.EBaseListCtrl,
                       listmix.ColumnSorterMixin):
    """List control for displaying syntax check results
    @todo: decouple marks and data from UI

    """
    _cache = dict()

    def __init__(self, parent):
        super(CheckResultsList, self).__init__(parent)

        # Attributes
        self.editor = None
        self._mw = None
        self._il = wx.ImageList(16, 16)

        # Setup
        self.InsertColumn(0, _("Type"))
        self.InsertColumn(1, _("Line"))
        self.InsertColumn(2, _("Error"))
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        for aid in (wx.ART_ERROR, wx.ART_WARNING, wx.ART_INFORMATION):
            bmp = wx.ArtProvider.GetBitmap(aid, wx.ART_MENU, (16, 16))
            self._il.Add(bmp)
        self.SetImageList(self._il, wx.IMAGE_LIST_SMALL)

        # ColumnSorterMixin has very poor api...
        self.itemDataMap = dict()
        listmix.ColumnSorterMixin.__init__(self, 3)

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivate)

        # Message Handler
        ed_msg.Subscribe(self.OnDwellStart, ed_msg.EDMSG_UI_STC_DWELL_START)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)

    def GetListCtrl(self):
        """Interface method to get current view"""
        return self

    def OnDestroy(self, evt):
        """Cleanup handlers on destroy"""
        if evt.GetEventObject() is self:
            ed_msg.Unsubscribe(self.OnDwellStart)
            self.ClearMarkers()

    def set_mainwindow(self, mw):
        """Set this lists mainwindow"""
        self._mw = mw

    def set_editor(self, editor):
        """Set the current editor"""
        self.editor = editor

    def OnDwellStart(self, msg):
        """Show calltips for the error if dwelling over a line"""
        data = msg.GetData()
        buf = data.get('stc', None)
        if buf:
            lineno = data.get('line', -1)
            fname = buf.GetFileName()
            if fname in CheckResultsList._cache:
                errorlist = CheckResultsList._cache[fname].GetLineData(lineno)
                if errorlist and len(errorlist):
                    errors = ["%s %s" % err for err in errorlist]
                    data['rdata'] = "\n".join(errors)

    def OnItemActivate(self, evt):
        """Go to the error in the file"""
        if self.editor:
            idx = evt.GetIndex()
            itm = self.GetItem(idx, 1).GetText()
            try:
                lineNo = int(itm)
                self.editor.GotoLine(max(0, lineNo - 1))
            except ValueError:
                pass

    def __LineSorter(self, key1, key2):
        """Sorter for the line number column, keeps the information messages
        from the analysis at the top regardless of sort order.

        """
        col, ascending = self.GetSortState()
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]

        if item1.isdigit() and item2.isdigit():
            cmpVal = cmp(int(item1), int(item2))
        elif item1.isdigit():
            if ascending:
                cmpVal = 1
            else:
                cmpVal = -1
        elif item2.isdigit():
            if ascending:
                cmpVal = -1
            else:
                cmpVal = 1
        else:
            cmpVal = 0

        if ascending:
            return cmpVal
        else:
            return -cmpVal

    def GetColumnSorter(self):
        """ColumnSorter Override"""
        col, ascending = self.GetSortState()
        if col == 1:
            return self.__LineSorter
        else:
            return super(CheckResultsList, self).GetColumnSorter()

    def OnSortOrderChanged(self):
        """ColumnSorter override"""
        self.RefreshRows()

    @staticmethod
    def DeleteEditorMarkers(editor):
        """Remove lint markers from the given editor"""
        editor.RemoveAllMarkers(ed_marker.LintMarker())
        editor.RemoveAllMarkers(ed_marker.LintMarkerError())
        editor.RemoveAllMarkers(ed_marker.LintMarkerWarning())

    def Clear(self):
        """Delete all the rows """
        if self.editor:
            fname = self.editor.GetFileName()
            if fname in CheckResultsList._cache:
                del CheckResultsList._cache[fname]
            self.DeleteAllItems()
            self.DeleteEditorMarkers(self.editor)
        else:
            # Editor has already been closed so just clear the list
            self.DeleteAllItems()

    def ClearMarkers(self):
        """Clear markers from all buffers"""
        if self._mw:
            nb = self._mw.GetNotebook()
            if nb:
                ctrls = nb.GetTextControls()
                for ctrl in ctrls:
                    if ctrl and ctrl.GetFileName() in CheckResultsList._cache:
                        self.DeleteEditorMarkers(ctrl)

    def GetCachedData(self):
        """Get the cached Lint data for the current editor
        @return: tuple(filename, LintData)

        """
        if self.editor:
            fname = self.editor.GetFileName()
            data = CheckResultsList._cache.get(fname, None)
        else:
            fname = u""
            data = None
        return fname, data

    def LoadData(self, data, fname=None):
        """Load data into the cache and display it in the list
        @param fname: filename
        @param data: Lint data [(errorType, errorText, errorLine),]

        """
        if fname is None:
            if not self.editor:
                return  # TODO: Log
            fname = self.editor.GetFileName()
        else:
            self.editor = PyStudioUtils.GetEditorOrOpenFile(self._mw, fname)
        CheckResultsList._cache[fname] = LintData(data)
        self._PopulateRows(CheckResultsList._cache[fname])

    def _PopulateRows(self, data):
        """Populate the list with the data
        @param data: LintData object

        """
        typeText = _("Type")
        errorText = _("Error")
        minLType = max(self.GetTextExtent(typeText)[0], self.GetColumnWidth(0))
        minLText = max(self.GetTextExtent(errorText)[0], self.GetColumnWidth(2))
        tmap = dict(Error=0, Warning=1)
        self.itemDataMap.clear()
        for idx, row in enumerate(data.GetOrderedData()):
            assert len(row) == 3
            mtype = row[0]
            dspmsg = LintData.GetDisplayString(mtype)
            minLType = max(minLType, self.GetTextExtent(dspmsg)[0])
            minLText = max(minLText, self.GetTextExtent(row[2])[0])
            row[0] = dspmsg
            self.Append(row)
            # Column Sorter
            self.itemDataMap[idx] = row
            self.SetItemData(self.ItemCount - 1, idx)
            # End Column Sorter
            img = tmap.get(mtype.strip(), 2)
            self.SetItemImage(self.ItemCount - 1, img)
            if self.editor:
                try:
                    if mtype == 'Error':
                        mark = ed_marker.LintMarkerError()
                    elif mtype == 'Warning':
                        mark = ed_marker.LintMarkerWarning()
                    else:
                        mark = ed_marker.LintMarker()
                    # TODO: store handles
                    self.editor.AddMarker(mark, int(row[1]) - 1)
                except ValueError:
                    pass
        self.SetColumnWidth(0, minLType)
        self.SetColumnWidth(2, minLText)

#-----------------------------------------------------------------------------#

class LintData(object):
    """PyLint output data management object"""
    def __init__(self, data):
        """@param data: [(type, text, line),]"""
        super(LintData, self).__init__()

        # Attributes
        self._data = dict()  # lineno -> [(errorType, errorText),]

        # Setup
        for val in data:
            assert len(val) == 3
            line = val[2]
            if line not in self._data:
                self._data[line] = list()
            self._data[line].append((unicode(val[0]), unicode(val[1]).rstrip()))

    Data = property(lambda self: self._data)

    def GetOrderedData(self):
        """Iterate over the data ordered by line number
        @return: [(errType, line, errText),]

        """
        rdata = list()
        for key in sorted(self._data.keys()):
            for data in self._data[key]:
                if isinstance(key, basestring):
                    rdata.insert(0, [data[0], unicode(key), data[1]])
                else:
                    rdata.append([data[0], unicode(key), data[1]])
        return rdata

    def GetLineData(self, line):
        """Get data for the given line
        @param line: line number (int)
        @return: [(errType, errText),] or None

        """
        return self._data.get(line, None)

    @staticmethod
    def GetDisplayString(mtype):
        """Get the display string for the given mesage type"""
        msgmap = {'Error': _("Error"),
                  'Warning': _("Warning"),
                  'Convention': _("Convention"),
                  'Refactor': _("Refactor"),
                  '***': _("Information")}
        return msgmap.get(mtype, _("Warning"))
