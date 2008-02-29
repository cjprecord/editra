###############################################################################
# Name: iface.py                                                              #
# Purpose: Plugin interface definitions                                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: iface.py
# AUTHOR: Cody Precord
# LANGUAGE: Python
# SUMMARY:
#   This module contains numerous plugin interfaces and the Extension points
# that they extend.
#
# Intefaces:
#   * ShelfI: Interface into the L{Shelf}
#   * MainWindowI: Interface into L{ed_main.MainWindow}
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import re
import wx
import plugin
from extern import flatnotebook as FNB
from profiler import Profile_Get
import ed_menu
import ed_glob
import util

#--------------------------------------------------------------------------#
PGNUM_PAT = re.compile(' - [0-9]+')

#--------------------------------------------------------------------------#

class MainWindowI(plugin.Interface):
    """The MainWindow Interface is intended as a simple general purpose
    interface for adding functionality to the main window. It does little
    managing of how object the implementing it is handled, most is left up to
    the plugin. Some examples of plugins using this interface are the
    FileBrowser and Calculator plugins.

    """
    def PlugIt(self, window):
        """This method is called once and only once per window when it is 
        created. It should typically be used to register menu entries, 
        bind event handlers and other similar actions.

        @param window: The parent window of the plugin
        @postcondition: The plugins controls are installed in the L{MainWindow}

        """
        raise NotImplementedError

    def GetMenuHandlers(self):
        """Get menu event handlers/id pairs. This function should return a
        list of tuples containing menu ids and their handlers. The handlers
        should be not be a member of this class but a member of the ui component
        that they handler acts upon.
        
        
        @return: list [(ID_FOO, foo.OnFoo), (ID_BAR, bar.OnBar)]

        """
        raise NotImplementedError

    def GetUIHandlers(self):
        """Get update ui event handlers/id pairs. This function should return a
        list of tuples containing object ids and their handlers. The handlers
        should be not be a member of this class but a member of the ui component
        that they handler acts upon.
        
        
        @return: list [(ID_FOO, foo.OnFoo), (ID_BAR, bar.OnBar)]

        """
        raise NotImplementedError

#-----------------------------------------------------------------------------#

class ShelfI(plugin.Interface):
    """Interface into the L{Shelf}. All plugins wanting to be
    placed on the L{Shelf} should implement this interface.

    """
    def AllowMultiple(self):
        """This method is used to check if multiple instances of this
        item are allowed to be open at one time.
        @return: True/False
        @rtype: boolean

        """

    def CreateItem(self, parent):
        """This is them method used to open the item in the L{Shelf}
        It should return an object that is a Panel or subclass of a Panel.
        @param parent: The would be parent window of this panel
        @return: wx.Panel

        """

    def GetId(self):
        """Return the id that identifies this item (same as the menuid)
        @return: Item ID
        @rtype: int

        """

    def GetMenuEntry(self, menu):
        """Returns the menu entry associated with this item
        @param menu: The menu this entry will be added to
        @return: wx.MenuItem

        """

    def GetName(self):
        """Return the name of this shelf item. This should be the
        same as the MenuEntry's label.
        @return: name of item
        @rtype: string

        """

class Shelf(plugin.Plugin):
    """Plugin that creates a notebook for holding the various Shelf items
    implemented by L{ShelfI}.

    """
    observers = plugin.ExtensionPoint(ShelfI)
    __name__ = u"Shelf"

    def __init__(self, pmgr):
        """Create the Shelf
        @param pmgr: This plugins manager

        """
        self._log = wx.GetApp().GetLog()
        self._shelf = None
        self._parent = None
        self._open = dict()

    def _GetMenu(self):
        """Return the menu of this object
        @return: ed_menu.ED_Menu()

        """
        menu = ed_menu.ED_Menu()
        menu.Append(ed_glob.ID_SHOW_SHELF, _("Show Shelf") + "\tCtrl+Alt+S", 
                    _("Show the Shelf"))
        menu.AppendSeparator()
        menu_items = list()
        for observer in self.observers:
            # Register Observers
            self._open[observer.GetName()] = 0
            try:
                menu_i = observer.GetMenuEntry(menu)
                if menu_i:
                    menu_items.append((menu_i.GetLabel(), menu_i))
            except Exception, msg:
                self._log("[shelf][err] %s" % str(msg))
        menu_items.sort()

        genmenu = ed_menu.ED_Menu()
        combo = 0
        for item in menu_items:
            combo += 1
            item[1].SetText(item[1].GetText() + "\tCtrl+Alt+" + str(combo))
            menu.AppendItem(item[1])
        return menu

    def Init(self, parent):
        """Mixes the shelf into the parent window
        @param parent: Reference to MainWindow

        """
        # First check if the parent has an instance already
        self._parent = parent
        mgr = parent.GetFrameManager()
        if mgr.GetPane(self.__name__).IsOk():
            return

        self._shelf = FNB.FlatNotebook(parent, 
                                       style=FNB.FNB_FF2 | \
                                             FNB.FNB_X_ON_TAB | \
                                             FNB.FNB_BACKGROUND_GRADIENT | \
                                             FNB.FNB_NODRAG)
        mgr.AddPane(self._shelf, wx.aui.AuiPaneInfo().Name(self.__name__).\
                            Caption("Shelf").Bottom().Layer(0).\
                            CloseButton(True).MaximizeButton(False).\
                            BestSize(wx.Size(500,250)))

        # Hide the pane and let the perspective manager take care of it
        mgr.GetPane(self.__name__).Hide()
        mgr.Update()

        # Install Menu and bind event handler
        view = parent.GetMenuBar().GetMenuByName("view")
        menu = self._GetMenu()
        pos = 0
        for pos in xrange(view.GetMenuItemCount()):
            mitem = view.FindItemByPosition(pos)
            if mitem.GetId() == ed_glob.ID_PERSPECTIVES:
                break
        view.InsertMenu(pos + 1, ed_glob.ID_SHELF, self.__name__, 
                        menu, _("Put an item on the Shelf"))
        for item in menu.GetMenuItems():
            if item.IsSeparator():
                continue
            parent.Bind(wx.EVT_MENU, self.OnGetShelfItem, item)

        if menu.GetMenuItemCount() < 3:
            view.Enable(ed_glob.ID_SHELF, False)

        self.StockShelf(Profile_Get('SHELF_ITEMS', 'list', []))

    def EnsureShelfVisible(self):
        """Make sure the Shelf is visable
        @precondition: Shelf.Init has been called
        @postcondition: Shelf is shown

        """
        if not hasattr(self._parent, 'GetFrameManager'):
            return
        mgr = self._parent.GetFrameManager()
        pane = mgr.GetPane(self.__name__)
        if not pane.IsShown():
            pane.Show()
            mgr.Update()

    def GetCount(self, item_name):
        """Get the number of open instances of a given Shelf Item
        @param item_name: Name of the Shelf item
        @return: number of instances on the Shelf

        """
        count = 0
        if self._shelf is None:
            return count
        for page in xrange(self._shelf.GetPageCount()):
            if item_name == re.sub(PGNUM_PAT, u'', 
                                  self._shelf.GetPageText(page), 1):
                count = count + 1
        return count

    def GetItemId(self, item_name):
        """Get the id that identifies a given item
        @param item_name: name of item to get ID for
        @return: integer id or None if not found

        """
        for item in self.observers:
            if item_name == item.GetName():
                return item.GetId()
        return None

    def GetItemStack(self):
        """Returns a list of ordered named items that are open in the shelf
        @return: list of strings

        """
        rval = list()
        if self._shelf is None:
            return rval
        for page in xrange(self._shelf.GetPageCount()):
            rval.append(re.sub(PGNUM_PAT, u'', 
                        self._shelf.GetPageText(page), 1))
        return rval

    def Hide(self):
        """Hide the shelf
        @postcondition: Shelf is hidden by aui manager

        """
        if not hasattr(self._parent, 'GetFrameManager'):
            return
        mgr = self._parent.GetFrameManager()
        pane = mgr.GetPane(self.__name__)
        if pane.IsOk():
            pane.Hide()
            mgr.Update()

    def IsShown(self):
        """Is the shelf visible?
        @return: bool

        """
        if not hasattr(self._parent, 'GetFrameManager'):
            return
        mgr = self._parent.GetFrameManager()
        pane = mgr.GetPane(self.__name__)
        if pane.IsOk():
            return pane.IsShown()
        else:
            return False

    def OnGetShelfItem(self, evt):
        """Handles menu events that have been registered
        by the Shelf Items on the Shelf.
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        if e_id == ed_glob.ID_SHOW_SHELF:
            if self.IsShown():
                self.Hide()
            else:
                self.EnsureShelfVisible()
        else:
            self.PutItemOnShelf(evt.GetId())

    def OnPutShelfItemAway(self, evt):
        """Handles when an item is closed
        @param evt: event that called this handler

        """
        print "OnPutShelfItemAway Not implemented"
        evt.Skip()

    def PutItemOnShelf(self, shelfid):
        """Put an item on the shelf
        @param shelfid: id of the ShelfItem to open

        """
        found = False
        for shelfi in self.observers:
            if shelfi.GetId() == shelfid:
                found = True
                break
        if not found:
            return
        name = shelfi.GetName()
        if self.ItemIsOnShelf(name) and \
            not shelfi.AllowMultiple() or \
            self._shelf is None:
            return
        else:
            self.EnsureShelfVisible()
            self._shelf.AddPage(shelfi.CreateItem(self._shelf), 
                                u"%s - %d" % (name, self._open.get(name, 0)))
            self._open[name] = self._open.get(name, 0) + 1

    def ItemIsOnShelf(self, item_name):
        """Check if at least one instance of a given item
        is currently on the Shelf.
        @param item_name: name of Item to look for

        """
        if self._shelf is None:
            return False
        for page in xrange(self._shelf.GetPageCount()):
            if item_name in self._shelf.GetPageText(page):
                return True
        return False

    def StockShelf(self, i_list):
        """Fill the shelf by opening an ordered list of items
        @param i_list: List of named L{ShelfI} instances
        @type i_list: list of strings

        """
        for item in i_list:
            itemid = self.GetItemId(item)
            if itemid:
                self.PutItemOnShelf(itemid)
#--------------------------------------------------------------------------#
