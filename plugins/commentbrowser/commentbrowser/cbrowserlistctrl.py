###############################################################################
# Name:  cbrowserlistctrl.py                                                  #
# Purpose: a simple to use listctrl for todo tasks                            #
# Author: DR0ID <dr0iddr0id@googlemail.com>                                   #
# Copyright: (c) 2008 DR0ID                                                   #
# License: wxWindows License                                                  #
###############################################################################

"""
Provides a virtual ListCtrl for the CommentBrowser

"""

__author__ = "DR0ID"
__svnid__ = "$Id: cbrowserlistctrl.py 956 2010-03-30 04:29:16Z CodyPrecord $"
__revision__ = "$Revision: 956 $"

#------------------------------------------------------------------------------#
# Imports
import locale
import wx
import wx.lib.mixins.listctrl as listmix

#Editra Library Modules
import ed_glob
import ed_msg
import ebmlib
import ed_txt
from util import Log

#------------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation

#------------------------------------------------------------------------------#


class CustomListCtrl(wx.ListCtrl,
                     listmix.ListCtrlAutoWidthMixin,
                     listmix.ColumnSorterMixin):
    """The list ctrl used for the list"""

    def __init__(self, parent, id_=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|
                       wx.LC_SINGLE_SEL|wx.LC_VIRTUAL|wx.LC_SORT_DESCENDING):
        """Init the CustomListCtrl"""

        wx.ListCtrl.__init__(self, parent, id_, pos, size, style)

        #---- Images used by the list ----#
        self._img_list = None
        self.sm_up = None
        self.sm_dn = None
        self._SetupImages()

        #---- Set Columns Headers ----#
        self.InsertColumn(0, "!")
        self.InsertColumn(1, _("Type"))
        self.InsertColumn(2, _("Description"))
        self.InsertColumn(3, _("File"))
        self.InsertColumn(4, _("Line"))

        self.SetColumnWidth(0, 38)
        self.SetColumnWidth(1, 59)
        self.SetColumnWidth(2, 429)
        self.SetColumnWidth(3, 117)

        #---- data ----#
        #this attribute ist required by listmix.ColumnSorterMixin
        #{1:(prio, task, description, file, line, fullname), etc.}
        self.itemDataMap = {}
        # [key1, key2, key3, ...]
        self.itemIndexMap = self.itemDataMap.keys()
        self.SetItemCount(len(self.itemDataMap))

        # needed to hold a reference (otherwise it would be 
        # garbagecollected too soon causing a crash)
        self._attr = None
        self._max_prio = 0

        #---- init base classes ----#
        # hast to be after self.itemDataMap has been initialized and the
        # setup of the columns, but befor sorting
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 5)

        #---- Events ----#
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnItemRightClick, self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self)
        ed_msg.Subscribe(self._SetupImages, ed_msg.EDMSG_THEME_CHANGED)

        # set initial sort order
        # sort by prio (column 0), descending order (0)
        self.SortListItems(0, 0)

    def __del__(self):
        ed_msg.Unsubscribe(self._SetupImages)
        super(CustomListCtrl, self).__del__()

    #---- methods ----#

    @staticmethod
    def _log(msg):
        """
        Private log method of this class
        @params msg: message to log
        """
        Log(u"[commentbrowser][listctr] " + unicode(msg))

    def _SetupImages(self, msg=None):
        """Setup the images and respond to theme change messages
        @keyword msg: Message Object or None

        """
        isize = (8, 8)
        self._img_list = wx.ImageList(8, 8)

        ups = wx.ArtProvider_GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU, isize)
        if not ups.IsOk():
            ups = wx.ArtProvider_GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, isize)
        self.sm_up = self._img_list.Add(ups)

        down = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DOWN),
                                        wx.ART_MENU, isize)
        if not down.IsOk():
            down = wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN,
                                            wx.ART_TOOLBAR, isize)
        self.sm_dn = self._img_list.Add(down)

        self.SetImageList(self._img_list, wx.IMAGE_LIST_SMALL)
        self.Refresh()

    def AddEntries(self, entrydict):
        """
        Adds all entries from the entrydict. The entries must be a tuple
        containing 
        entrytuple = (prio, tasktype, description, file, line, fullname)
        Refresh is not called.
        @param entrydict: a dictionary containing {key:entrytuple}

        """
        self.itemDataMap = dict(entrydict)
        self.itemIndexMap = self.itemDataMap.keys()
        self.SetItemCount(len(self.itemDataMap))
        try:
            vals = [item[0] for item in self.itemDataMap.values()]
            self._max_prio = max(vals)
        except Exception, msg:
            self._log("[err] %s" % msg)

    def ClearEntries(self):
        """Removes all entries from list ctrl, refresh is not called"""
        self.itemDataMap.clear()
        self.itemIndexMap = []
        self.SetItemCount(0)

    def NavigateToTaskSource(self, itemIndex):
        """
        Navigates to the file and position saved in this item
        @param itemIndex: a int

        """
        if itemIndex < 0 or itemIndex > len(self.itemDataMap):
            self._log("[err] itemIndex out of range!")
            return
        
        key = self.itemIndexMap[itemIndex]
        source = self.itemDataMap[key][-1]
        if not ebmlib.IsUnicode(source):
            source = ed_txt.DecodeString(source)
        line = self.itemDataMap[key][-2]
        try:
            nbook = self.GetParent().GetMainWindow().GetNotebook()
            ctrls = nbook.GetTextControls()
            for ctrl in ctrls:
                if source == ctrl.GetFileName():
                    nbook.SetSelection(nbook.GetPageIndex(ctrl))
                    nbook.GoCurrentPage()
                    ctrl.GotoLine(line-1)
                    break
        except Exception, excp:
            self._log("[err] %s" % excp)

    #---- special methods used by the mixin classes ----#
    
    #Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        """ this method is required by listmix.ColumnSorterMixin"""
        return self

    #---------------------------------------------------
    #Matt C, 2006/02/22
    #Here's a better SortItems() method --
    #the ColumnSorterMixin.__ColumnSorter() method already handles the 
    #ascending/descending, and it knows to sort on another column if the chosen 
    #columns have the same value.
    def SortItems(self, sorter=cmp):
        """
        This method is required by the 
        wx.lib.mixins.listctrl.ColumnSorterMixin, for internal usage only

        """
        sorter = self.SpecialSorter # always use the special sorter
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items

        #redraw the list
        self.Refresh()
        
    def GetColumnSorter(self):
        """
        Overwrites the default GetColumnSorter of the mixin.
        @returns: a compare function object that takes two arguments: 
        func(key1, key2)

        """
        return self.SpecialSorter

    def GetSecondarySortValues(self, col, key1, key2):
        """
        Overwrites the default GetSecondarySortValues. It uses the SpecialSorter
        to return a result.
        @param col: column index
        @param key1: first item index to compare
        @param key2: second item index to compare
        @returns: a tuple of the keys either (key1, key2) or (key2, key1)

        """
        cval = self.SpecialSorter(key1, key2)
        if 0 < cval:
            return (key2, key1)
        return (key1, key2)
        
        
    def SpecialSorter(self, key1, key2):
        """
        SpecialSorter sorts the list depending on which column should be sorted.
        It sorts automatically also by other columns.
        @param key1: first key to compare
        @param key2: second key to compare
        @returns: -1, 0 or 1 like the compare function

        """
        col = self._col
        ascending = self._colSortFlag[col]
        # (prio, task, description, file, line, fullname)
        if 0 == col: # prio -> sortorder: prio task file line
            _sortorder = [col, 1, 3, 4]
        elif 1 == col: # task -> sortorder: task prio, file , line
            _sortorder = [col, 0, 3, 4]
        elif 2 == col: # descr -> sortorder: descr, prio, task
            _sortorder = [col, 0, 1, 3, 4]
        elif 3 == col : # file -> sortorder: file, prio line
            _sortorder = [col, 0, 4]
        elif 4 == col: # line number -> sortorder: file, line
            _sortorder = [3, 4]
            
        cmpval = 0
        _idx = 0
        while( 0 == cmpval and _idx < len(_sortorder) ):
            item1 = self.itemDataMap[key1][ _sortorder[_idx] ]
            item2 = self.itemDataMap[key2][ _sortorder[_idx] ]
            #--- Internationalization of string sorting with locale module
            if type(item1) == type('') or type(item2) == type(''):
                cmpval = locale.strcoll(str(item1), str(item2))
            else:
                cmpval = cmp(item1, item2)
            #---
            _idx += 1

        # in certain cases always ascending/descending order is prefered
        if 0 == _sortorder[_idx-1] and 0 != col: # prio
            ascending = 0
        elif 4 == _sortorder[_idx-1] and 4 != col: # linenumber
            ascending = 1
        elif 3 == _sortorder[_idx-1] and 4 == col: # filename
            ascending = 1
            
        if ascending:
            return cmpval
        else:
            return -cmpval

    #Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        """
        This method is required by the 
        wx.lib.mixins.listctrl.ColumnSorterMixin, for internal usage only

        """
        return (self.sm_dn, self.sm_up)
        
    #---- special listctrl eventhandlers ----#
        # These methods are callbacks for implementing the
        # "virtualness" of the list...

    def OnGetItemText(self, idx, col):
        """
        Virtual ListCtrl have to define this method, returns the text of the
        requested item.
        @param itemIdx: a int defining the item
        @param col: column
        @returns: text as a string for the item and column

        """
        index = self.itemIndexMap[idx]
        text = self.itemDataMap[index][col]
        return text

    @staticmethod
    def OnGetItemImage(item):
        """
        Virtual ListCtrl have to define this method, should return an image
        for the item, but since we have no images it always returns -1.
        @param item: itemindex (not used)
        @returns: always -1 because we have no images for the items.

        """
        return -1

    def OnGetItemAttr(self, idx):
        """
        Virtual ListCtrl have to define this method, should return item 
        attributes, but since we have none it always returns None.
        @param itemIdx: index of an item for which we want the attributes
        @returns: a wx.ListItemAttr if the prio of the item is high enough, 
        None otherwise

        """
        idx = self.itemIndexMap[idx]
        prio = self.itemDataMap[idx][0]
        prionum = [self._max_prio-i for i in range(5)]
        if prio in prionum and prio > 1:
            idx = prionum.index(prio)
            val = int( 255 - 255. / (2**idx) )
            self._attr = wx.ListItemAttr(wx.NullColour,
                                         wx.Colour(255, 255, val),
                                         wx.NullFont)
            return self._attr
        return None

    #---- Eventhandler ----#

    def OnItemActivated(self, event):
        """
        Callback when an item of the list has been activated (double click)
        @param event: wx.Event
        """
        self.NavigateToTaskSource(event.m_itemIndex)

    def OnItemRightClick(self, event):
        """
        Callback when an item of the list has been clicked with the right 
        mouse button.
        @param event: wx.Event
        """
        self.NavigateToTaskSource(event.m_itemIndex)
        event.Skip()
