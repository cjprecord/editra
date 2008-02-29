###############################################################################
# Name: ed_search.py                                                          #
# Purpose: Text searching services and utilities                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_search                                                          #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#     Provides various search controls and searching services for finding
#  text in a document.
#
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import ed_glob
from profiler import Profile_Get
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class TextFinder(object):
    """Provides an object to manage finding text in documents
    through various different methods, plain text, regex, ect...
    the Finder must be initialized with the variable callable set
    to a method that fetches the stc control that the search is to take
    place in.
    @todo: possibly reimplement as a singleton so that it can be used
           without having to go through the notebook each time its needed.

    """
    def __init__(self, parent, getstc):
        """Initializes the Text Finding Service, the getstc argument
        needs to be a function that returns reference to stc to perform 
        the search in.
        @param getstc: callable function that will return an stc

        """
        object.__init__(self)
        self._parent      = parent
        self._replace_dlg = None
        self._find_dlg    = None
        self._pool        = None
        self._scroll      = 0
        self._start       = 0
        self._last_found  = 0
        self.FetchPool    = getstc
        self._data        = wx.FindReplaceData()
        self._data.SetFlags(wx.FR_DOWN)

    def GetData(self):
        """Return the FindReplace data
        @return: search data
        @rtype: wx.FindReplaceData

        """
        return self._data

    def OnFind(self, evt):
        """Does the work of finding the text
        @param evt: Event that called this handler

        """
        # Map of search flags
        flag_map = {  wx.FR_MATCHCASE : wx.stc.STC_FIND_MATCHCASE, 
                      wx.FR_WHOLEWORD : wx.stc.STC_FIND_WHOLEWORD,
                      wx.FR_MATCHCASE | wx.FR_WHOLEWORD : \
                                        wx.stc.STC_FIND_MATCHCASE | \
                                        wx.stc.STC_FIND_WHOLEWORD,
                      0               : 0
        }

        # Get Search Type
        search_id = evt.GetEventType()

        # Get the Search Flags
        s_flags = self._data.GetFlags()
        # Fetch the Search Pool and Query
        pool = self.FetchPool()
        query = self._data.GetFindString()
        if search_id in [wx.wxEVT_COMMAND_FIND, wx.wxEVT_COMMAND_FIND_NEXT]:
            if search_id == wx.wxEVT_COMMAND_FIND_NEXT:
                if wx.FR_DOWN & s_flags:
                    if self._last_found < 0:
                        pool.SetCurrentPos(0) # Start at top again
                    else:
                        pool.SetCurrentPos(pool.GetCurrentPos() + len(query))
                else:
                    # Searching previous
                    if self._last_found < 0:
                        pool.SetCurrentPos(pool.GetLength())
                    else:
                        pool.SetCurrentPos(pool.GetCurrentPos() - len(query))

            pool.SearchAnchor()
            if not s_flags & wx.FR_DOWN:
                found = pool.SearchPrev(flag_map[s_flags] | \
                                        wx.stc.STC_FIND_REGEXP, query)
            else:
                found = pool.SearchNext(flag_map[s_flags - wx.FR_DOWN] | \
                                        wx.stc.STC_FIND_REGEXP, query)

            if found > 0:
                pool.SetCurrentPos(found)
                # HACK to ensure selection is visible
                sel = pool.GetSelection()
                pool.SetSelection(sel[1], sel[0])
            else:
                # Try search from begining/end again
                self.SetStart(pool)
                self.SetScroll(pool)
                if not s_flags & wx.FR_DOWN:
                    pool.SetCurrentPos(pool.GetLength())
                    pool.SetSelection(pool.GetLength(), pool.GetLength())
                else:
                    pool.SetCurrentPos(0)
                    pool.SetSelection(0, 0)
                pool.SearchAnchor()

                if not s_flags & wx.FR_DOWN:
                    found = pool.SearchPrev(flag_map[s_flags] | \
                                            wx.stc.STC_FIND_REGEXP, query)
                else:
                    found = pool.SearchNext(flag_map[s_flags - wx.FR_DOWN] | \
                                            wx.stc.STC_FIND_REGEXP, query)

            if found < 0:
                # Couldnt find it anywhere so set screen back to start position
                pool.ScrollToLine(self._scroll)
                pool.SetCurrentPos(self._start)
                pool.SetSelection(self._start, self._start)
                wx.Bell() # alert user to unfound string
            else:
                pool.SetCurrentPos(found)
                # HACK to ensure selection is visible
                sel = pool.GetSelection()
                pool.SetSelection(sel[1], sel[0])

            self._last_found = found
        elif search_id == wx.wxEVT_COMMAND_FIND_REPLACE:
            replacestring = evt.GetReplaceString()
            pool.ReplaceSelection(replacestring)
        elif search_id == wx.wxEVT_COMMAND_FIND_REPLACE_ALL:
            replacestring = evt.GetReplaceString()
            self.SetStart(pool) # Save Start point
            self.SetScroll(pool) # Save scroll pos
            pool.SetTargetStart(0)
            pool.SetTargetEnd(pool.GetLength())
            pool.SetSearchFlags(flag_map[s_flags - wx.FR_DOWN] | \
                                wx.stc.STC_FIND_REGEXP)
            replaced = 0
            while pool.SearchInTarget(query) > 0:
                pool.SetSelection(pool.GetTargetStart(), pool.GetTargetEnd())
                pool.ReplaceSelection(replacestring)
                pool.SetTargetStart(pool.GetTargetEnd() - (len(query) - \
                                    len(replacestring)))
                pool.SetTargetEnd(pool.GetLength())
                replaced += 1
            pool.ScrollToLine(self._scroll)
            pool.SetCurrentPos(self._start) # Move cursor back to start
            pool.SetSelection(self._start, self._start)
            dlg = wx.MessageDialog(self._parent, 
                                   _("Replace All Finished\n"
                                     "A Total of %d matches were replaced") % \
                                     replaced, 
                                    _("All Done"), 
                                    wx.OK | wx.ICON_INFORMATION)
            dlg.CenterOnParent()
            dlg.ShowModal()
            dlg.Destroy()
        else:
            evt.Skip()

    def GetLastFound(self):
        """Returns the position value of the last found search item
        if the last search resulted in nothing being found then the
        return value will -1.
        @return: position of last search opperation
        @rtype: int

        """
        return self._last_found

    def GetSearchFlags(self):
        """Get the find services search flags
        @return: bitmask of the set search flags

        """
        return self._data.GetFlags()

    def OnFindClose(self, evt):
        """Destroy Find Dialog After Cancel is clicked in it
        @param evt: event that called this handler

        """
        if self._find_dlg is not None:
            self._find_dlg.Destroy()
        self._find_dlg = None
        evt.Skip()

    def OnShowFindDlg(self, evt):
        """Catches the Find events and shows the appropriate find dialog
        @param evt: event that called this handler
        @postcondition: find dialog is shown

        """
        if self._find_dlg is not None:
            self._find_dlg.Destroy()
            self._find_dlg = None
        e_id = evt.GetId()
        if e_id == ed_glob.ID_FIND_REPLACE:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, \
                                                  _("Find/Replace"),
                                                  wx.FR_REPLACEDIALOG)
        elif e_id == ed_glob.ID_FIND:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, \
                                                  _("Find"))
        else:
            evt.Skip()
            return
        if wx.Platform == '__WXMAC__' and Profile_Get('METAL', 'bool', False):
            self._find_dlg.SetExtraStyle(wx.DIALOG_EX_METAL)
        self._find_dlg.CenterOnParent()
        try:
            self._find_dlg.Show()
        except wx.PyAssertionError:
            # Yes this is a bit strange but on windows if there was a find
            # dialog prevously shown and destroyed then the second time through
            # here will raise this assertion but not for any times after.
            self._find_dlg.Show()

    def SetQueryString(self, query):
        """Sets the search query value
        @param query: string to search for

        """
        self._data.SetFindString(query)

    def SetSearchFlags(self, flags):
        """Set the find services search flags
        @param flags: bitmask of paramters to set

        """
        self._data.SetFlags(flags)

    def SetScroll(self, pool):
        """Sets the value of the scroll attribute to the value of the
        current position in the search pool.
        @param pool: the search pool (a.k.a the text control)

        """
        self._scroll = pool.GetFirstVisibleLine()
        return True

    def SetStart(self, pool):
        """Sets the value of the start attribute to the value of the
        current position in the search pool.
        @param pool: the search pool (a.k.a the text control)

        """
        self._start = pool.GetCurrentPos()
        return True

#-----------------------------------------------------------------------------#

class EdSearchCtrl(wx.SearchCtrl):
    """Creates a simple search control for use in the toolbar
    or a statusbar and the such. Supports incremental search,
    and uses L{FindService} to do the actual searching of the
    document.

    """
    def __init__(self, parent, id_, value="", menulen=0, \
                 pos=wx.DefaultPosition, size=wx.DefaultSize, \
                 style=wx.TE_RICH2):
        """Initializes the Search Control
        @param menulen: max length of history menu

        """
        wx.SearchCtrl.__init__(self, parent, id_, value, pos, size, style)
        
        # Attributes
        self._parent     = parent
        # TEMP HACK
        self.FindService = self.GetTopLevelParent().nb.FindService
        self._flags      = wx.FR_DOWN
        self._recent     = list()        # The History List
        self._last       = None
        self.rmenu       = wx.Menu()
        self.max_menu    = menulen + 2   # Max menu length + descript/separator

        # Setup Recent Search Menu
        lbl = self.rmenu.Append(wx.ID_ANY, _("Recent Searches"))
        lbl.Enable(False)
        self.rmenu.AppendSeparator()
        self.SetMenu(self.rmenu)

        # Bind Events
        if wx.Platform == '__WXMSW__':
            self.ShowCancelButton(False)
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
                    break

        self.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_MENU, self.OnHistMenu)

    #---- Functions ----#
    def ClearSearchFlag(self, flag):
        """Clears a previously set search flag
        @param flag: flag to clear from search data

        """
        self._flags ^= flag

    def GetSearchData(self):
        """Gets the find data from the controls FindService
        @return: search data
        @rtype: wx.FindReplaceData

        """
        if hasattr(self.FindService, "GetData"):
            return self.FindService.GetData()
        else:
            return None

    def GetHistory(self):
        """Gets and returns the history list of the control
        @return: list of recent search items

        """
        if hasattr(self, "_recent"):
            return self._recent
        else:
            return list()

    def InsertHistoryItem(self, value):
        """Inserts a search query value into the top of the history stack
        @param value: search string
        @postcondition: the value is added to the history menu

        """
        if value == wx.EmptyString:
            return

        # Make sure menu only has unique items
        m_items = self.rmenu.GetMenuItems()
        for menu_i in m_items:
            if value == menu_i.GetLabel():
                self.rmenu.RemoveItem(menu_i)

        # Create and insert the new item
        n_item = wx.MenuItem(self.rmenu, wx.NewId(), value)
        self.rmenu.InsertItem(2, n_item)

        # Update History list
        self._recent.insert(0, value)
        if len(self._recent) > self.max_menu:
            self._recent.pop()

        # Check Menu Length
        m_len = self.rmenu.GetMenuItemCount()
        if m_len > self.max_menu:
            try:
                self.rmenu.RemoveItem(m_items[-1])
            except IndexError, msg:
                wx.GetApp().GetLog()("[searchbar] menu error: %s" % str(msg))

    def IsMatchCase(self):
        """Returns True if the search control is set to search
        in Match Case mode.
        @return: whether search is using match case or not
        @rtype: boolean

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_MATCHCASE & data.GetFlags():
                return True
        return False

    def IsSearchPrevious(self):
        """Returns True if the search control is set to search
        in Previous mode.
        @return: whether search is searchin up or not
        @rtype: boolean

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_DOWN & data.GetFlags():
                return False
        return True

    def IsWholeWord(self):
        """Returns True if the search control is set to search
        in Whole Word mode.
        @return: whether search is using match whole word or not
        @rtype: boolean

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_WHOLEWORD & data.GetFlags():
                return True
        return False

    def SetHistory(self, hist_list):
        """Populates the history list from a list of
        string values.
        @param hist_list: list of search items

        """
        hist_list.reverse()
        for item in hist_list:
            self.InsertHistoryItem(item)

    def SetSearchFlag(self, flags):
        """Sets the search data flags
        @param flag: search flag to add

        """
        self._flags |= flags

    #---- End Functions ----#

    #---- Event Handlers ----#
    def ProcessEvent(self, evt):
        """Processes Events for the Search Control
        @param evt: the event that called this handler

        """
        e_type = evt.GetEventType()
        if e_type == wx.wxEVT_KEY_UP:
            e_key = evt.GetKeyCode()
            if e_key == wx.WXK_ESCAPE:
                # HACK change to more safely determine the context
                # Currently control is only used in command bar
                self.GetParent().Hide()
                return
            elif e_key == wx.WXK_SHIFT:
                self.SetSearchFlag(wx.FR_DOWN)
                return
            else:
                pass

            tmp = self.GetValue()
            # Dont do search 
            if tmp == wx.EmptyString or \
               evt.CmdDown() or \
               e_key in [wx.WXK_COMMAND, wx.WXK_LEFT, wx.WXK_RIGHT, 
                         wx.WXK_UP, wx.WXK_DOWN]:
                return

            if wx.Platform != '__WXMSW__' and len(self.GetValue()) > 0:
                self.ShowCancelButton(True)
            else:
                self.ShowCancelButton(False)

            if e_key == wx.WXK_RETURN:
                if evt.ShiftDown():
                    if wx.FR_DOWN & self._flags:
                        self.ClearSearchFlag(wx.FR_DOWN)
                else:
                    self.SetSearchFlag(wx.FR_DOWN)

                if self.GetValue() != self._last:
                    s_cmd = wx.wxEVT_COMMAND_FIND
                else:
                    s_cmd = wx.wxEVT_COMMAND_FIND_NEXT
                self.InsertHistoryItem(self.GetValue())
            else:
                self.SetSearchFlag(wx.FR_DOWN)
                s_cmd = wx.wxEVT_COMMAND_FIND

            self._last = self.GetValue()
            self.FindService.SetQueryString(self.GetValue())
            self.FindService.SetSearchFlags(self._flags)
            self.FindService.OnFind(wx.FindDialogEvent(s_cmd))
        else:
            evt.Skip()
            return

        # Give feedback on whether text was found or not
        if self.FindService.GetLastFound() < 0 and len(self.GetValue()) > 0:
            chgd = self.SetForegroundColour(wx.RED)
            if chgd:
                wx.Bell() # Beep on the first not found char
            
        else:
            # ?wxBUG? cant set text back to black after changing color
            # But setting it to this almost black color works. Most likely its
            # due to bit masking but I havent looked at the source so I am not
            # sure
            chgd = self.SetForegroundColour(wx.ColorRGB(0 | 1 | 0))
        self.Refresh()

    def OnCancel(self, evt):
        """Cancels the Search Query
        @param evt: the event that called this handler

        """
        self.SetValue(u"")
        self.ShowCancelButton(False)
        evt.Skip()

    def OnHistMenu(self, evt):
        """Sets the search controls value to the selected menu item
        @param evt: the event that called this handler
        @type evt: wx.MenuEvent

        """
        item_id = evt.GetId()
        item = self.rmenu.FindItemById(item_id)
        if item != None:
            self.SetValue(item.GetLabel())
        else:
            evt.Skip()

    #---- End Event Handlers ----#
