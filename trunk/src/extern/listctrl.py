#----------------------------------------------------------------------------
# Name:        wxPython.lib.mixins.listctrl
# Purpose:     Helpful mix-in classes for wxListCtrl
#
# Author:      Robin Dunn
#
# Created:     15-May-2001
# RCS-ID:      $Id$
# Copyright:   (c) 2001 by Total Control Software
# Licence:     wxWindows license
#----------------------------------------------------------------------------
# 12/14/2003 - Jeff Grimmett (grimmtooth@softhome.net)
#
# o 2.5 compatability update.
# o ListCtrlSelectionManagerMix untested.
#
# 12/21/2003 - Jeff Grimmett (grimmtooth@softhome.net)
#
# o wxColumnSorterMixin -> ColumnSorterMixin 
# o wxListCtrlAutoWidthMixin -> ListCtrlAutoWidthMixin
# ...
# 13/10/2004 - Pim Van Heuven (pim@think-wize.com)
# o wxTextEditMixin: Support Horizontal scrolling when TAB is pressed on long
#       ListCtrls, support for WXK_DOWN, WXK_UP, performance improvements on
#       very long ListCtrls, Support for virtual ListCtrls
#
# 15-Oct-2004 - Robin Dunn
# o wxTextEditMixin: Added Shift-TAB support
#

import  locale
import  wx

#----------------------------------------------------------------------------

class ColumnSorterMixin:
    """
    A mixin class that handles sorting of a wx.ListCtrl in REPORT mode when
    the column header is clicked on.

    There are a few requirments needed in order for this to work genericly:

      1. The combined class must have a GetListCtrl method that
         returns the wx.ListCtrl to be sorted, and the list control
         must exist at the time the wx.ColumnSorterMixin.__init__
         method is called because it uses GetListCtrl.

      2. Items in the list control must have a unique data value set
         with list.SetItemData.

      3. The combined class must have an attribute named itemDataMap
         that is a dictionary mapping the data values to a sequence of
         objects representing the values in each column.  These values
         are compared in the column sorter to determine sort order.

    Interesting methods to override are GetColumnSorter,
    GetSecondarySortValues, and GetSortImages.  See below for details.
    """

    def __init__(self, numColumns):
        self.SetColumnCount(numColumns)
        list = self.GetListCtrl()
        if not list:
            raise ValueError, "No wx.ListCtrl available"
        list.Bind(wx.EVT_LIST_COL_CLICK, self.__OnColClick, list)


    def SetColumnCount(self, newNumColumns):
        self._colSortFlag = [0] * newNumColumns
        self._col = -1


    def SortListItems(self, col=-1, ascending=1):
        """Sort the list on demand.  Can also be used to set the sort column and order."""
        oldCol = self._col
        if col != -1:
            self._col = col
            self._colSortFlag[col] = ascending
        self.GetListCtrl().SortItems(self.GetColumnSorter())
        self.__updateImages(oldCol)


    def GetColumnWidths(self):
        """
        Returns a list of column widths.  Can be used to help restore the current
        view later.
        """
        list = self.GetListCtrl()
        rv = []
        for x in range(len(self._colSortFlag)):
            rv.append(list.GetColumnWidth(x))
        return rv


    def GetSortImages(self):
        """
        Returns a tuple of image list indexesthe indexes in the image list for an image to be put on the column
        header when sorting in descending order.
        """
        return (-1, -1)  # (decending, ascending) image IDs


    def GetColumnSorter(self):
        """Returns a callable object to be used for comparing column values when sorting."""
        return self.__ColumnSorter


    def GetSecondarySortValues(self, col, key1, key2):
        """Returns a tuple of 2 values to use for secondary sort values when the
           items in the selected column match equal.  The default just returns the
           item data values."""
        return (key1, key2)


    def __OnColClick(self, evt):
        oldCol = self._col
        self._col = col = evt.GetColumn()
        self._colSortFlag[col] = int(not self._colSortFlag[col])
        self.GetListCtrl().SortItems(self.GetColumnSorter())
        if wx.Platform != "__WXMAC__" or wx.SystemOptions.GetOptionInt("mac.listctrl.always_use_generic") == 1:
            self.__updateImages(oldCol)
        evt.Skip()
        self.OnSortOrderChanged()
        
        
    def OnSortOrderChanged(self):
        """
        Callback called after sort order has changed (whenever user
        clicked column header).
        """
        pass


    def __ColumnSorter(self, key1, key2):
        col = self._col
        ascending = self._colSortFlag[col]
        item1 = self.itemDataMap[key1][col]
        item2 = self.itemDataMap[key2][col]

        #--- Internationalization of string sorting with locale module
        if type(item1) == type('') or type(item2) == type(''):
            cmpVal = locale.strcoll(str(item1), str(item2))
        else:
            cmpVal = cmp(item1, item2)
        #---

        # If the items are equal then pick something else to make the sort value unique
        if cmpVal == 0:
            cmpVal = apply(cmp, self.GetSecondarySortValues(col, key1, key2))

        if ascending:
            return cmpVal
        else:
            return -cmpVal


    def __updateImages(self, oldCol):
        sortImages = self.GetSortImages()
        if self._col != -1 and sortImages[0] != -1:
            img = sortImages[self._colSortFlag[self._col]]
            list = self.GetListCtrl()
            if oldCol != -1:
                list.ClearColumnImage(oldCol)
            list.SetColumnImage(self._col, img)


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

class ListCtrlAutoWidthMixin:
    """ A mix-in class that automatically resizes the last column to take up
        the remaining width of the wx.ListCtrl.

        This causes the wx.ListCtrl to automatically take up the full width of
        the list, without either a horizontal scroll bar (unless absolutely
        necessary) or empty space to the right of the last column.

        NOTE:    This only works for report-style lists.

        WARNING: If you override the EVT_SIZE event in your wx.ListCtrl, make
                 sure you call event.Skip() to ensure that the mixin's
                 _OnResize method is called.

        This mix-in class was written by Erik Westra <ewestra@wave.co.nz>
    """
    def __init__(self):
        """ Standard initialiser.
        """
        self._resizeColMinWidth = None
        self._resizeColStyle = "LAST"
        self._resizeCol = 0
        self.Bind(wx.EVT_SIZE, self._onResize)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self._onResize, self)


    def setResizeColumn(self, col):
        """
        Specify which column that should be autosized.  Pass either
        'LAST' or the column number.  Default is 'LAST'.
        """
        if col == "LAST":
            self._resizeColStyle = "LAST"
        else:
            self._resizeColStyle = "COL"
            self._resizeCol = col
        

    def resizeLastColumn(self, minWidth):
        """ Resize the last column appropriately.

            If the list's columns are too wide to fit within the window, we use
            a horizontal scrollbar.  Otherwise, we expand the right-most column
            to take up the remaining free space in the list.

            This method is called automatically when the wx.ListCtrl is resized;
            you can also call it yourself whenever you want the last column to
            be resized appropriately (eg, when adding, removing or resizing
            columns).

            'minWidth' is the preferred minimum width for the last column.
        """
        self.resizeColumn(minWidth)


    def resizeColumn(self, minWidth):
        self._resizeColMinWidth = minWidth
        self._doResize()
        

    # =====================
    # == Private Methods ==
    # =====================

    def _onResize(self, event):
        """ Respond to the wx.ListCtrl being resized.

            We automatically resize the last column in the list.
        """
        if 'gtk2' in wx.PlatformInfo:
            self._doResize()
        else:
            wx.CallAfter(self._doResize)
        event.Skip()


    def _doResize(self):
        """ Resize the last column as appropriate.

            If the list's columns are too wide to fit within the window, we use
            a horizontal scrollbar.  Otherwise, we expand the right-most column
            to take up the remaining free space in the list.

            We remember the current size of the last column, before resizing,
            as the preferred minimum width if we haven't previously been given
            or calculated a minimum width.  This ensure that repeated calls to
            _doResize() don't cause the last column to size itself too large.
        """
        
        if not self:  # avoid a PyDeadObject error
            return

        if self.GetSize().height < 32:
            return  # avoid an endless update bug when the height is small.
        
        numCols = self.GetColumnCount()
        if numCols == 0: return # Nothing to resize.

        if(self._resizeColStyle == "LAST"):
            resizeCol = self.GetColumnCount()
        else:
            resizeCol = self._resizeCol

        if self._resizeColMinWidth == None:
            self._resizeColMinWidth = self.GetColumnWidth(resizeCol - 1)

        # We're showing the vertical scrollbar -> allow for scrollbar width
        # NOTE: on GTK, the scrollbar is included in the client size, but on
        # Windows it is not included
        listWidth = self.GetClientSize().width
        if wx.Platform != '__WXMSW__':
            if self.GetItemCount() > self.GetCountPerPage():
                scrollWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
                listWidth = listWidth - scrollWidth

        totColWidth = 0 # Width of all columns except last one.
        for col in range(numCols):
            if col != (resizeCol-1):
                totColWidth = totColWidth + self.GetColumnWidth(col)

        resizeColWidth = self.GetColumnWidth(resizeCol - 1)

        if totColWidth + self._resizeColMinWidth > listWidth:
            # We haven't got the width to show the last column at its minimum
            # width -> set it to its minimum width and allow the horizontal
            # scrollbar to show.
            self.SetColumnWidth(resizeCol-1, self._resizeColMinWidth)
            return

        # Resize the last column to take up the remaining available space.

        self.SetColumnWidth(resizeCol-1, listWidth - totColWidth)




#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
def selectBeforePopup(event):
    """Ensures the item the mouse is pointing at is selected before a popup.

    Works with both single-select and multi-select lists."""
    ctrl = event.GetEventObject()
    if isinstance(ctrl, wx.ListCtrl):
        n, flags = ctrl.HitTest(event.GetPosition())
        if n >= 0:
            if not ctrl.GetItemState(n, wx.LIST_STATE_SELECTED):
                for i in range(ctrl.GetItemCount()):
                    ctrl.SetItemState(i, 0, SEL_FOC)
                #for i in getListCtrlSelection(ctrl, SEL_FOC):
                #    ctrl.SetItemState(i, 0, SEL_FOC)
                ctrl.SetItemState(n, SEL_FOC, SEL_FOC)


def getListCtrlSelection(listctrl, state=wx.LIST_STATE_SELECTED):
    """ Returns list of item indexes of given state (selected by defaults) """
    res = []
    idx = -1
    while 1:
        idx = listctrl.GetNextItem(idx, wx.LIST_NEXT_ALL, state)
        if idx == -1:
            break
        res.append(idx)
    return res

wxEVT_DOPOPUPMENU = wx.NewEventType()
EVT_DOPOPUPMENU = wx.PyEventBinder(wxEVT_DOPOPUPMENU, 0)


class ListCtrlSelectionManagerMix:
    """Mixin that defines a platform independent selection policy

    As selection single and multi-select list return the item index or a
    list of item indexes respectively.
    """
    _menu = None

    def __init__(self):
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnLCSMRightDown)
        self.Bind(EVT_DOPOPUPMENU, self.OnLCSMDoPopup)
#        self.Connect(-1, -1, self.wxEVT_DOPOPUPMENU, self.OnLCSMDoPopup)


    def getPopupMenu(self):
        """ Override to implement dynamic menus (create) """
        return self._menu


    def setPopupMenu(self, menu):
        """ Must be set for default behaviour """
        self._menu = menu


    def afterPopupMenu(self, menu):
        """ Override to implement dynamic menus (destroy) """
        pass


    def getSelection(self):
        res = getListCtrlSelection(self)
        if self.GetWindowStyleFlag() & wx.LC_SINGLE_SEL:
            if res:
                return res[0]
            else:
                return -1
        else:
            return res


    def OnLCSMRightDown(self, event):
        selectBeforePopup(event)
        event.Skip()
        menu = self.getPopupMenu()
        if menu:
            evt = wx.PyEvent()
            evt.SetEventType(wxEVT_DOPOPUPMENU)
            evt.menu = menu
            evt.pos = event.GetPosition()
            wx.PostEvent(self, evt)


    def OnLCSMDoPopup(self, event):
        self.PopupMenu(event.menu, event.pos)
        self.afterPopupMenu(event.menu)


#----------------------------------------------------------------------------
#----------------------------------------------------------------------------
from bisect import bisect


class TextEditMixin:
    """    
    A mixin class that enables any text in any column of a
    multi-column listctrl to be edited by clicking on the given row
    and column.  You close the text editor by hitting the ENTER key or
    clicking somewhere else on the listctrl. You switch to the next
    column by hiting TAB.

    To use the mixin you have to include it in the class definition
    and call the __init__ function::

        class TestListCtrl(wx.ListCtrl, TextEditMixin):
            def __init__(self, parent, ID, pos=wx.DefaultPosition,
                         size=wx.DefaultSize, style=0):
                wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
                TextEditMixin.__init__(self) 


    Authors:     Steve Zatz, Pim Van Heuven (pim@think-wize.com)
    """

    editorBgColour = wx.Colour(255,255,175) # Yellow
    editorFgColour = wx.Colour(0,0,0)       # black
        
    def __init__(self):
        #editor = wx.TextCtrl(self, -1, pos=(-1,-1), size=(-1,-1),
        #                     style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB \
        #                     |wx.TE_RICH2)

        self.make_editor()
        self.Bind(wx.EVT_TEXT_ENTER, self.CloseEditor)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)


    def make_editor(self, col_style=wx.LIST_FORMAT_LEFT):
        
        style =wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_RICH2
        style |= {wx.LIST_FORMAT_LEFT: wx.TE_LEFT,
                  wx.LIST_FORMAT_RIGHT: wx.TE_RIGHT,
                  wx.LIST_FORMAT_CENTRE : wx.TE_CENTRE
                  }[col_style]
        
        editor = wx.TextCtrl(self, -1, style=style)
        editor.SetBackgroundColour(self.editorBgColour)
        editor.SetForegroundColour(self.editorFgColour)
        font = self.GetFont()
        editor.SetFont(font)

        self.curRow = 0
        self.curCol = 0

        editor.Hide()
        if hasattr(self, 'editor'):
            self.editor.Destroy()
        self.editor = editor

        self.col_style = col_style
        self.editor.Bind(wx.EVT_CHAR, self.OnChar)
        self.editor.Bind(wx.EVT_KILL_FOCUS, self.CloseEditor)
        
        
    def OnItemSelected(self, evt):
        self.curRow = evt.GetIndex()
        evt.Skip()
        

    def OnChar(self, event):
        ''' Catch the TAB, Shift-TAB, cursor DOWN/UP key code
            so we can open the editor at the next column (if any).'''

        keycode = event.GetKeyCode()
        if keycode == wx.WXK_TAB and event.ShiftDown():
            self.CloseEditor()
            if self.curCol-1 >= 0:
                self.OpenEditor(self.curCol-1, self.curRow)
            
        elif keycode == wx.WXK_TAB:
            self.CloseEditor()
            if self.curCol+1 < self.GetColumnCount():
                self.OpenEditor(self.curCol+1, self.curRow)

        elif keycode == wx.WXK_ESCAPE:
            self.CloseEditor()

        elif keycode == wx.WXK_DOWN:
            self.CloseEditor()
            if self.curRow+1 < self.GetItemCount():
                self._SelectIndex(self.curRow+1)
                self.OpenEditor(self.curCol, self.curRow)

        elif keycode == wx.WXK_UP:
            self.CloseEditor()
            if self.curRow > 0:
                self._SelectIndex(self.curRow-1)
                self.OpenEditor(self.curCol, self.curRow)
            
        else:
            event.Skip()

    
    def OnLeftDown(self, evt=None):
        ''' Examine the click and double
        click events to see if a row has been click on twice. If so,
        determine the current row and columnn and open the editor.'''
        
        if self.editor.IsShown():
            self.CloseEditor()
            
        x,y = evt.GetPosition()
        row,flags = self.HitTest((x,y))
    
        if row != self.curRow: # self.curRow keeps track of the current row
            evt.Skip()
            return
        
        # the following should really be done in the mixin's init but
        # the wx.ListCtrl demo creates the columns after creating the
        # ListCtrl (generally not a good idea) on the other hand,
        # doing this here handles adjustable column widths
        
        self.col_locs = [0]
        loc = 0
        for n in range(self.GetColumnCount()):
            loc = loc + self.GetColumnWidth(n)
            self.col_locs.append(loc)

        
        col = bisect(self.col_locs, x+self.GetScrollPos(wx.HORIZONTAL)) - 1
        self.OpenEditor(col, row)


    def OpenEditor(self, col, row):
        ''' Opens an editor at the current position. '''

        # give the derived class a chance to Allow/Veto this edit.
        evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_BEGIN_LABEL_EDIT, self.GetId())
        evt.m_itemIndex = row
        evt.m_col = col
        item = self.GetItem(row, col)
        evt.m_item.SetId(item.GetId()) 
        evt.m_item.SetColumn(item.GetColumn()) 
        evt.m_item.SetData(item.GetData()) 
        evt.m_item.SetText(item.GetText()) 
        ret = self.GetEventHandler().ProcessEvent(evt)
        if ret and not evt.IsAllowed():
            return   # user code doesn't allow the edit.

        if self.GetColumn(col).m_format != self.col_style:
            self.make_editor(self.GetColumn(col).m_format)
    
        x0 = self.col_locs[col]
        x1 = self.col_locs[col+1] - x0

        scrolloffset = self.GetScrollPos(wx.HORIZONTAL)

        # scroll forward
        if x0+x1-scrolloffset > self.GetSize()[0]:
            if wx.Platform == "__WXMSW__":
                # don't start scrolling unless we really need to
                offset = x0+x1-self.GetSize()[0]-scrolloffset
                # scroll a bit more than what is minimum required
                # so we don't have to scroll everytime the user presses TAB
                # which is very tireing to the eye
                addoffset = self.GetSize()[0]/4
                # but be careful at the end of the list
                if addoffset + scrolloffset < self.GetSize()[0]:
                    offset += addoffset

                self.ScrollList(offset, 0)
                scrolloffset = self.GetScrollPos(wx.HORIZONTAL)
            else:
                # Since we can not programmatically scroll the ListCtrl
                # close the editor so the user can scroll and open the editor
                # again
                self.editor.SetValue(self.GetItem(row, col).GetText())
                self.curRow = row
                self.curCol = col
                self.CloseEditor()
                return

        y0 = self.GetItemRect(row)[1]
        
        editor = self.editor
        editor.SetDimensions(x0-scrolloffset,y0, x1,-1)
        
        editor.SetValue(self.GetItem(row, col).GetText()) 
        editor.Show()
        editor.Raise()
        editor.SetSelection(-1,-1)
        editor.SetFocus()
    
        self.curRow = row
        self.curCol = col

    
    # FIXME: this function is usually called twice - second time because
    # it is binded to wx.EVT_KILL_FOCUS. Can it be avoided? (MW)
    def CloseEditor(self, evt=None):
        ''' Close the editor and save the new value to the ListCtrl. '''
        if not self.editor.IsShown():
            return
        text = self.editor.GetValue()
        self.editor.Hide()
        self.SetFocus()
        
        # post wxEVT_COMMAND_LIST_END_LABEL_EDIT
        # Event can be vetoed. It doesn't has SetEditCanceled(), what would 
        # require passing extra argument to CloseEditor() 
        evt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_END_LABEL_EDIT, self.GetId())
        evt.m_itemIndex = self.curRow
        evt.m_col = self.curCol
        item = self.GetItem(self.curRow, self.curCol)
        evt.m_item.SetId(item.GetId()) 
        evt.m_item.SetColumn(item.GetColumn()) 
        evt.m_item.SetData(item.GetData()) 
        evt.m_item.SetText(text) #should be empty string if editor was canceled
        ret = self.GetEventHandler().ProcessEvent(evt)
        if not ret or evt.IsAllowed():
            if self.IsVirtual():
                # replace by whather you use to populate the virtual ListCtrl
                # data source
                self.SetVirtualData(self.curRow, self.curCol, text)
            else:
                self.SetStringItem(self.curRow, self.curCol, text)
        self.RefreshItem(self.curRow)

    def _SelectIndex(self, row):
        listlen = self.GetItemCount()
        if row < 0 and not listlen:
            return
        if row > (listlen-1):
            row = listlen -1
            
        self.SetItemState(self.curRow, ~wx.LIST_STATE_SELECTED,
                          wx.LIST_STATE_SELECTED)
        self.EnsureVisible(row)
        self.SetItemState(row, wx.LIST_STATE_SELECTED,
                          wx.LIST_STATE_SELECTED)



#----------------------------------------------------------------------------
#----------------------------------------------------------------------------

"""
FILENAME: CheckListCtrlMixin.py
AUTHOR:   Bruce Who (bruce.who.hk at gmail.com)
DATE:     2006-02-09
$Revision$
DESCRIPTION:
    This script provide a mixin for ListCtrl which add a checkbox in the first
    column of each row. It is inspired by limodou's CheckList.py(which can be
    got from his NewEdit) and improved:
        - You can just use InsertStringItem() to insert new items;
        - Once a checkbox is checked/unchecked, the corresponding item is not
          selected;
        - You can use SetItemData() and GetItemData();
        - Interfaces are changed to OnCheckItem(), IsChecked(), CheckItem().

    You should not set a imagelist for the ListCtrl once this mixin is used.

HISTORY:
1.3     - You can check/uncheck a group of sequential items by <Shift-click>:
          First click(or <Shift-Click>) item1 to check/uncheck it, then
          Shift-click item2 to check/uncheck it, and you'll find that all
          items between item1 and item2 are check/unchecked!
1.2     - Add ToggleItem()
1.1     - Initial version
"""

from wx import ImageFromStream, BitmapFromImage
import cStringIO, zlib

def getUncheckData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4\xbb{\xba8\x86X\xf4\
&\xa7\xa4$\xa5-`1\x08\\2\xbb\xb1\xb1\x91\xf5\xd8\x84o\xeb\xff\xfaw\x1d[.=[2\
\x90'\x01\x08v\xec]\xd3\xa3qvU`l\x81\xd9\xd18\t\xd3\x84+\x0cll[\xa6t\xcc9\
\xd4\xc1\xda\xc3<O\x9a1\xc3\x88\xc3j\xfa\x86_\xee@#\x19<]\xfd\\\xd69%4\x01\
\x00\xdc\x80-\x05" )

def getUncheckBitmap():
    return BitmapFromImage(getUncheckImage())

def getUncheckImage():
    stream = cStringIO.StringIO(getUncheckData())
    return ImageFromStream(stream)

def getCheckData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe47{\xba8\x86X\xf4&\
\xa7\xa4$\xa5-`1\x08\\2\xbb\xb1\xb1\x91\xf5\xd8\x84o\xeb\xff\xfaw\x1d[.=[2\
\x90\'\x01\x08v\xec\\2C\xe3\xec+\xc3\xbd\x05fG\xe3\x14n1\xcc5\xad\x8a8\x1a\
\xb9\xa1\xeb\xd1\x853-\xaa\xc76\xecb\xb8i\x16c&\\\xc2\xb8\xe9Xvbx\xa1T\xc3U\
\xd6p\'\xbd\x85\x19\xff\xbe\xbf\xd7\xe7R\xcb`\xd8\xa5\xf8\x83\xe1^\xc4\x0e\
\xa1"\xce\xc3n\x93x\x14\xd8\x16\xb0(\x15q)\x8b\x19\xf0U\xe4\xb10\x08V\xa8\
\x99\xf3\xdd\xde\xad\x06t\x0e\x83\xa7\xab\x9f\xcb:\xa7\x84&\x00\xe0HE\xab' )

def getCheckBitmap():
    return BitmapFromImage(getCheckImage())

def getCheckImage():
    stream = cStringIO.StringIO(getCheckData())
    return ImageFromStream(stream)

# Mac OSX style checkbox
def getMacCheckData():
    return zlib.decompress(
'x\xda\x01\xe8\x02\x17\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\
\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\
\x08\x08\x08\x08|\x08d\x88\x00\x00\x02\x9fIDAT8\x8d\x95\x93\xcbkTw\x14\xc7?\
\xbf;w&\x99\xfb{\xdc<t\xa3\xab )\xc1\x10C"\xad\x16\xd4D\x91\xd8P\xd4H\r\xc5W\
\xacX[*A\x88\xa4\xbaQ\\\x88\xa0A\xf1\x0f(\xd5\xd8@J\xe9\xc6\x95\x90H\x11E\
\xbb\x11\xe2\xa3.|l\x0c\xf8\nM\x9a\xce$b\xee\x9d\x99{\\\x8cd\xba\xac\x8b\xef\
\xea\x9c\xf39\xe7{8\x07\xe5\xa5\xf8X544\x08 CCC\xf2\xd1\xc5\x83\x83\x83\x02H\
{{\xbb(/\xc5b\xa0\xb3\xb3S\x80\xff%\xa5\x94\x0c\x0f\x0f\x8b\xf2R(\xe5\xa5\
\xd8\xdf\xb7O>i[\xcf\xb6-\x1d\x18\xad\xf1\xd4\x87L\x11\x94R \x82\x00\x87\x0e\
\x1e\xe0\xfa\xf8\x18k\xd6m$\xa3\x8a\xdc\xbe\xf3\xa7\xf2\x01~\x19\xff\x8b+_\
\xeedf6G~\xee-\x00\xcaS$I\x82\x88\x00p\xfb\xd6M\xae\x8f\x8fQ[WG\xff\x91\x01\
\xbe9z\x1a\x00\x1f\xa0}U\x13:\x08\x88\xa2\x98(\x8e\x11\x01\xa5T\xb9;\xc2\xc2\
B\xc4\xc5\xf3\xe7\x008\xf4C?a\x18\xd2\xda\xdc\xc8\xbdW\x13x\x005\xce\x11\x17\
\x8b\xdc\xb8\xf1\x07\xbbwn\xa7w\xdb\x17\xbc~\xf5\x92\xb8P I\x12FG\x86\x99z\
\xf3\x9a\xe6\x96Utl\xea\xa2$B\xads\x00e@\xa85\xef\x16"V\x7f\xba\x86\xfa%K\
\xc9\xe7s\\8w\x06\x11x\xfe|\x92\xdf\x7f\x1d\xc1\xf7}\xfa\x07\x8e\x11E\x05fsy\
L6[\x01\x04:\xcb\xdf\xb39^\xbc\x99\xa1\xb7\xef;\xd2\x99\x0c\x0f\xefOp\xf9\
\xd2\xcf\\<\x7f\x96b\xb1H\xc7\xe6n\nd\x98|9\xc5\xd4\xf4\xbf8g+\x00\x9d\xcdb\
\x8d\xc6X\xcb\x8a\x15\x8d\xf4\xee9\x00\xc0\xd5\xdfFx\xfc\xe8\x01\xb5\xf5K\
\xd8\xb1\xab\x0f\xa35\xa1s\x84\xceb\x82\xa0\xb2Dc\r\xd6X\xaa\xaa2\xa4<\xc5W_\
\xef\xe5\xe1\xc4]\x1e=\x98\x00\xe0\xdb\xc3\x03,_\xb6\x8cR)\x81DH\xc7i\x8c\
\xd5\x95\t\x9c58g\xb1\xceb\x9c\xc3\x85\x8e\xe3\xa7\xce\x10h\xcd\xea\xcf>\xa7\
\xab{+A`\x08\xc3\x1a\x02k\xa8q!\xd6\x9a\xca\x04\xe9\xaa*\xb46d\xb3\xd5(\xa5H\
\xa5<\x8c\xb1\xfcx\xe24\xcd-\xad\x845\x0eI\x04\x91\x04\x94G\x14\x17\xa8\xae\
\xfe\x8f\x85\xb7\xf39\xea\xea\xea1Z\xa3\xbc\xf2\xe5\xa1\x14\xfb\x0f~O)\x11J\
\xc5"\xbe\x97\xa2$\x82$%\xde\xc51s\xf9\x99\n`!7\xcd\xd3gO\xe8\xda\xb2\x81\
\xb4\x07\x8a\xb2\x92\x0f\x1e\x13X\xf4\x1b\x03c\xd7n\x11\xcd\xfdS\x01\xacm[\
\xc9\xd5\xd1\x9f\x18:y\x94\xf9\xf9yDd\xf1\x0fD\x84$)#|\xdf\xc7ZKSS\x13===\
\x00\xbc\x07\xc7\xfc\xfc\x8c\xc6Nx\x85\x00\x00\x00\x00IEND\xaeB`\x82\x07kSx'\
 )

def getMacCheckBitmap():
    return BitmapFromImage(getMacCheckImage())

def getMacCheckImage():
    stream = cStringIO.StringIO(getMacCheckData())
    return ImageFromStream(stream)

#----------------------------------------------------------------------
def getMacUncheckData():
    return zlib.decompress(
'x\xda\x01\xc1\x01>\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x01xIDAT8\x8d\xa5\x92O\x8a"1\x14\x87\xbf\xfc\
\xb1\xcaP\x14\xb8\x90Z\xba\x13\xea\x1c\x9e\xc0\xa3\xd8\xdds\x86\x99\xb9\x82\
\xbb\x99\xbe\x8c\x88\xc7P\\\x89(\x88$\xa5If\xd1T\xaa\xab\x05g\xd1\x0f\x02I\
\xc8\xef{\xbf\xf7\xf2\x84\x90\x8a\xef\x84\xfc\x96\x1a\xd0\xed\xe6\xc7\xdbk<\
\x9f\xcf\x18c\xd0\xfa\xe3:\xc6\xd8{\xec\xbd\xe7z\xbdRU\x15?\x7f\xfd\x16\t\
\xf0\xfe\xf7O\x1c\x8f\xc7\xccf3\x94z^\x92\xf7\x9e\xd5jEUUq\xf1\xf2*$\xc0\xf1\
xd:\x9d\xd24\r\xd6Z\x9cs8\xe7\xb0\xd6>\xac\xa6i\x98L&Xk\xbb\x12N\xa7\x13J)\
\xee\xf7\xfb\xd3\xecmIB\x08\x8c1\x1d`4\x1a\x11B\xc0{\x9f\x1e|\x15J)\x891&H\
\x08\xa1\x03\x94e\xf9\x00\x10B\xf4\x9a\xd8\nB\x088\xe7(\x8a\xa2\x03H)\xb1\
\xd6\xf6,~\x16J)\t!\xa4{\xe7\x1cy\x9ew\x80\xa2(\xc8\xf3\x9c\xc1`\xf0\x00\x10\
B\xa4\xec\xed\xd9{\x9f\xbeZ\x03\x18c0\xc6\xa0\x94"\xc6\x98Jh\xa3u\xf0\x19\
\xd0s\xa0\xb5&\xcb2\xb4\xd6\xbd9h{\xa2\xb5\xe6v\xbb\xa1\x94"\x84\x801\xa6\
\x0fPJ\x91e\x19\xc3\xe10u\xfc\xab\xed,\xcb\xd2Y)\xd5\x07\xec\xf7\xfb\x1e\xf5\
Y\xb4\t\x0e\x87\xc3Gy\x00\xdb\xed\x96\xcdf\xf3_q\xebf\xbd^\xb3\xdb\xed:\x07u\
]\xb3\\.Y,\x16\\.\x9740\xed,\xa4\xa1\xd1\x9a\xb2,\xa9\xeb\x9a\xf9|\x0e\xc0?\
\x07\\\xc1\xc6\xab\x1f\x1bB\x00\x00\x00\x00IEND\xaeB`\x82\xb96\xcb-' )

def getMacUncheckBitmap():
    return BitmapFromImage(getMacUncheckImage())

def getMacUncheckImage():
    stream = cStringIO.StringIO(getMacUncheckData())
    return ImageFromStream(stream)

class CheckListCtrlMixin:
    """
    This is a mixin for ListCtrl which add a checkbox in the first
    column of each row. It is inspired by limodou's CheckList.py(which
    can be got from his NewEdit) and improved:
    
        - You can just use InsertStringItem() to insert new items;

        - Once a checkbox is checked/unchecked, the corresponding item
          is not selected;

        - You can use SetItemData() and GetItemData();

        - Interfaces are changed to OnCheckItem(), IsChecked(),
          CheckItem().

    You should not set a imagelist for the ListCtrl once this mixin is used.
    """
    def __init__(self, check_image=None, uncheck_image=None):
        self.__imagelist_ = wx.ImageList(16, 16)
        if not check_image:
#             check_image, uncheck_image = self.__CreateDefaultBitmaps()
            if wx.Platform == '__WXMAC__':
                check_image = getMacCheckBitmap()
            else:
                check_image = getCheckBitmap()
        if not uncheck_image:
            if wx.Platform == '__WXMAC__':
                uncheck_image = getMacUncheckBitmap()
            else:
                uncheck_image = getUncheckBitmap()
        self.uncheck_image = self.__imagelist_.Add(uncheck_image)
        self.check_image = self.__imagelist_.Add(check_image)
        self.SetImageList(self.__imagelist_, wx.IMAGE_LIST_SMALL)
        self.__last_check_ = None

        self.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown_)
        
        # override the default methods of ListCtrl/ListView
        self.InsertStringItem = self.__InsertStringItem_

    def __CreateDefaultBitmaps(self):
        dc = wx.MemoryDC(wx.EmptyBitmap(16, 16))
        # Draw Boxes
        wx.RendererNative.Get().DrawCheckBox(self, dc, wx.Rect(0, 0, 16, 16), 
                                       wx.CONTROL_CHECKED)
        cbmp = dc.GetAsBitmap()
        dc.SelectObject(wx.EmptyBitmap(16, 16))
        wx.RendererNative.Get().DrawCheckBox(self, dc, wx.Rect(0, 0, 16, 16), 
                                       wx.CONTROL_CHECKABLE)
        ucbmp = dc.GetAsBitmap()

        return cbmp, ucbmp

    # NOTE: if you use InsertItem, InsertImageItem or InsertImageStringItem,
    #       you must set the image yourself.
    def __InsertStringItem_(self, index, label):
        index = self.InsertImageStringItem(index, label, 0)
        return index

    def __OnLeftDown_(self, evt):
        (index, flags) = self.HitTest(evt.GetPosition())
        if flags == wx.LIST_HITTEST_ONITEMICON:
            img_idx = self.GetItem(index).GetImage()
            flag_check = img_idx == 0
            begin_index = index
            end_index = index
            if self.__last_check_ is not None \
                    and wx.GetKeyState(wx.WXK_SHIFT):
                last_index, last_flag_check = self.__last_check_
                if last_flag_check == flag_check:
                    # XXX what if the previous item is deleted or new items
                    # are inserted?
                    item_count = self.GetItemCount()
                    if last_index < item_count:
                        if last_index < index:
                            begin_index = last_index
                            end_index = index
                        elif last_index > index:
                            begin_index = index
                            end_index = last_index
                        else:
                            assert False
            while begin_index <= end_index:
                self.CheckItem(begin_index, flag_check)
                begin_index += 1
            self.__last_check_ = (index, flag_check)
        else:
            evt.Skip()

    def OnCheckItem(self, index, flag):
        pass

    def IsChecked(self, index):
        return self.GetItem(index).GetImage() == 1

    def CheckItem(self, index, check = True):
        img_idx = self.GetItem(index).GetImage()
        if img_idx == 0 and check is True:
            self.SetItemImage(index, 1)
            self.OnCheckItem(index, True)
        elif img_idx == 1 and check is False:
            self.SetItemImage(index, 0)
            self.OnCheckItem(index, False)

    def ToggleItem(self, index):
        self.CheckItem(index, not self.IsChecked(index))


#----------------------------------------------------------------------------
