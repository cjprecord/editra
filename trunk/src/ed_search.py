############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

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

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies
import re
import wx
import ed_glob
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class TextFinder:
    """Provides an object to manage finding text in documents
    through various different methods, plain text, regex, ect...
    the Finder must be initialized with the variable callable set
    to a method that fetches the stc control that the search is to take
    place in.

    """
    def __init__(self, parent, callable):
        """Initializes the Service"""
        self._parent      = parent
        self._replace_dlg = None
        self._find_dlg    = None
        self._pool        = None
        self._scroll      = 0
        self._start       = 0
        self._last_found  = 0
        self.FetchPool    = callable
        self._data        = wx.FindReplaceData()
        self._data.SetFlags(wx.FR_DOWN)

    def GetData(self):
        return self._data

    def OnFind(self, evt):
        """Does the work of finding the text"""
        # Map of search flags
        flag_map = {  wx.FR_MATCHCASE                   : wx.stc.STC_FIND_MATCHCASE, 
                      wx.FR_WHOLEWORD                   : wx.stc.STC_FIND_WHOLEWORD,
                      wx.FR_MATCHCASE | wx.FR_WHOLEWORD : wx.stc.STC_FIND_MATCHCASE | wx.stc.STC_FIND_WHOLEWORD,
                      0                                 : 0
        }

        # Get Search Type
        search_id = evt.GetEventType()

        # Get the Search Flags
        s_flags = self._data.GetFlags()
        print s_flags       # TESTING 
        # Fetch the Search Pool and Query
        pool = self.FetchPool()
        query = self._data.GetFindString()
        if search_id in [wx.wxEVT_COMMAND_FIND, wx.wxEVT_COMMAND_FIND_NEXT]:
            if search_id == wx.wxEVT_COMMAND_FIND_NEXT: # or wx.FR_DOWN & s_flags:
                if self._last_found < 0:
                    pool.SetCurrentPos(0) # Start at top again
                else:
                    pool.SetCurrentPos(pool.GetCurrentPos() + len(query))

            pool.SearchAnchor()
            s_flags = flag_map[s_flags - wx.FR_DOWN]
           # if not s_flags & wx.FR_DOWN:
           #     found = pool.SearchPrev(flag_map[s_flags], query)
           # else:
            found = pool.SearchNext(s_flags | wx.stc.STC_FIND_REGEXP, query)
            if found > 0:
                pool.SetCurrentPos(found)
                # HACK to ensure selection is visible
                sel = pool.GetSelection()
                pool.SetSelection(sel[1], sel[0])
            else:
                # Try search from top
                self.SetStart(pool)
                self.SetScroll(pool)
                pool.SetCurrentPos(0)
                pool.SetSelection(0,0)
                pool.SearchAnchor()
                found = pool.SearchNext(s_flags | wx.stc.STC_FIND_REGEXP, query)
            if found < 0:
                # We couldnt find it anywhere so set screen back to start position
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
            pool.SetSearchFlags(flag_map[s_flags - wx.FR_DOWN] | wx.stc.STC_FIND_REGEXP)
            replaced = 0
            while pool.SearchInTarget(query) > 0:
                pool.SetSelection(pool.GetTargetStart(), pool.GetTargetEnd())
                pool.ReplaceSelection(replacestring)
                pool.SetTargetStart(pool.GetTargetEnd() - (len(query) - len(replacestring)))
                pool.SetTargetEnd(pool.GetLength())
                replaced += 1
            pool.ScrollToLine(self._scroll)
            pool.SetCurrentPos(self._start) # Move cursor back to start
            pool.SetSelection(self._start, self._start)
            dlg = wx.MessageDialog(self._parent, 
                                   _("Replace All Finished\n"
                                     "A Total of %d matches were replaced") % replaced, 
                                    _("All Done"), 
                                    wx.OK | wx.ICON_INFORMATION)
            dlg.CenterOnParent()
            dlg.ShowModal()
            dlg.Destroy()
        else:
            evt.Skip()

    def OnFindClose(self, evt):
        """Destroy Find Dialog After Cancel is clicked in it"""
        self._find_dlg.Destroy()
        self._find_dlg = None

    def OnShowFindDlg(self, evt):
        """Catches the Find events and organizes the data
        before pushing it to the DoFind Function.

        """
        if self._find_dlg != None:
            self._find_dlg.Destroy()
            self._find_dlg = None
        e_id = evt.GetId()
        if e_id == ed_glob.ID_FIND_REPLACE:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, _("Find/Replace"),
                                                 wx.FR_REPLACEDIALOG | wx.FR_NOUPDOWN)
        elif e_id == ed_glob.ID_FIND:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, _("Find"),
                                                 wx.FR_NOUPDOWN)
        else:
            return
        if wx.Platform == '__WXMAC__' and ed_glob.PROFILE.has_key('METAL'):
            if ed_glob.PROFILE['METAL']:
                self.find_dlg.SetExtraStyle(wx.DIALOG_EX_METAL)
        self._find_dlg.CenterOnParent()
        self._find_dlg.Show()

    def SetQueryString(self, query):
        """Sets the search query value"""
        self._data.SetFindString(query)

    def SetSearchFlags(self, flags):
        """Set the find services search flags"""
        self._data.SetFlags(flags)

    def SetScroll(self, pool):
        """Sets the value of the scroll attribute to the value of the
        current position in the search pool.

        """
        self._scroll = pool.GetFirstVisibleLine()
        return True

    def SetStart(self, pool):
        """Sets the value of the start attribute to the value of the
        current position in the search pool.

        """
        self._start = pool.GetCurrentPos()
        return True

class ED_SearchCtrl(wx.SearchCtrl):
    """Creates a quick search control for use in the toolbar
    or a statusbar and the such.

    """
    def __init__(self, parent, id, value="", menulen=0, pos=wx.DefaultPosition, 
               size=wx.DefaultSize, style=wx.TE_PROCESS_ENTER | wx.TE_RICH2):
        """Initializes the Search Control"""
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)
        
        # Attributes
        self._parent     = parent
        # TEMP HACK
        self.FindService = parent.GetParent().nb.FindService
        self._flags      = wx.FR_DOWN
        self._recent     = list()             # The History List
        self._last       = None
        self.rmenu       = self.MakeMenu()     # Menu to display search history
        self.max_menu    = menulen            # Max length of history menu

        # Recent Search Menu
        self.SetMenu(self.rmenu)

        # Bind Events
        self.Bind(wx.EVT_TEXT_ENTER, self.ProcessEvent)
        self.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_MENU, self.OnHistMenu)

    #---- Functions ----#
    def ClearSearchFlag(self, flag):
        """Clears a previously set search flag"""
        self._flags ^= flag

    def GetSearchData(self):
        """Gets the find data from the controls FindService"""
        if hasattr(self.FindService, "GetData"):
            return self.FindService.GetData()
        else:
            return None

    def GetHistory(self):
        """Gets and returns the history list of the control"""
        if hasattr(self, "_recent"):
            return self._recent
        else:
            return list()

    def InsertHistoryItem(self, value):
        """Inserts a search query value into the top of the history stack"""
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
            self.rmenu.RemoveItem(m_items[-1])

    # XXX ditch these and make the caller check the bitmask
    def IsMatchCase(self):
        """Returns True if the search control is set to search
        in Match Case mode.

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_MATCHCASE & data.GetFlags():
                return True
        return False

    def IsWholeWord(self):
        """Returns True if the search control is set to search
        in Whole Word mode.

        """
        data = self.GetSearchData()
        if data != None:
            if wx.FR_WHOLEWORD & data.GetFlags():
                return True
        return False

    def MakeMenu(self):
        """Initializes the Search History Menu"""
        menu = wx.Menu()
        lbl = menu.Append(wx.ID_ANY, _("Recent Searches"))
        lbl.Enable(False)
        menu.AppendSeparator()
        return menu

    def SetHistory(self, hist_list):
        """Populates the history list from a list of
        string values.

        """
        hist_list.reverse()
        for item in hist_list:
            self.InsertHistoryItem(item)

    def SetSearchFlag(self, flags):
        """Sets the search data flags"""
        self._flags |= flags

    #---- End Functions ----#

    #---- Event Handlers ----#
    def ProcessEvent(self, evt):
        """Processes Events for the Search Control"""
        e_type = evt.GetEventType()
        if e_type == wx.wxEVT_COMMAND_TEXT_ENTER:
            dev_tool.DEBUGP("[search_evt] Search Text Entered %s" % str(self.GetValue()))
            self.InsertHistoryItem(self.GetValue())
            self.FindService.SetQueryString(self.GetValue())
            self.FindService.SetSearchFlags(self._flags)
            if self.GetValue() != self._last:
                s_cmd = wx.wxEVT_COMMAND_FIND
            else:
                s_cmd = wx.wxEVT_COMMAND_FIND_NEXT
            self._last = self.GetValue()
            self.FindService.OnFind(wx.FindDialogEvent(s_cmd))
        elif e_type == wx.wxEVT_KEY_UP:
            e_key = evt.GetKeyCode()
            tmp = self.GetValue()
            # Dont do search 
            if tmp == wx.EmptyString or evt.CmdDown() or e_key == wx.WXK_COMMAND:
                return
            if len(self.GetValue()) > 0:
                self.ShowCancelButton(True)
            else:
                self.ShowCancelButton(False)
            self.FindService.SetQueryString(self.GetValue())
            self.FindService.SetSearchFlags(self._flags)
            self.FindService.OnFind(wx.FindDialogEvent(wx.wxEVT_COMMAND_FIND))
        else:
            evt.Skip()
            return

        # Give feedback on whether text was found or not
        if self.FindService._last_found < 0 and len(self.GetValue()) > 0:
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
        """Cancels the Search Query"""
        self.SetValue("")
        self.ShowCancelButton(False)

    def OnHistMenu(self, evt):
        """Sets the search controls value to the selected menu item"""
        item_id = evt.GetId()
        item = self.rmenu.FindItemById(item_id)
        if item != None:
            self.SetValue(item.GetLabel())
        else:
            evt.Skip()

    #---- End Event Handlers ----#

