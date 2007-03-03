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

class QueryData(wx.FindReplaceData):
    """A container class for holding various data related to finding text"""
    def __init__(self, flags=0):
        """Initializes the default data"""
        wx.FindReplaceData.__init__(self, flags)
        self.SetFlag(wx.FR_DOWN)

        # Attributes
        
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
        self._start       = 0
        self._last_found  = 0
        self.FetchPool    = callable
        self._data        = wx.FindReplaceData()
        self._data.SetFlags(wx.FR_DOWN)

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
            if found != -1:
                pool.SetCurrentPos(found)
                # HACK to ensure selection is visible
                sel = pool.GetSelection()
                pool.SetSelection(sel[1], sel[0])
            else:
                self.SetStart(pool)
                pool.SetCurrentPos(0)
                pool.SetSelection(0,0)
                found = pool.SearchNext(s_flags | wx.stc.STC_FIND_REGEXP, query)
            if found < 0:
                pool.SetCurrentPos(self._start)
                pool.SetSelection(self._start, self._start)
                dlg = wx.MessageDialog(self._parent, _("The search string \"%s\" was not found"
                                                      " in the document") % query,
                                       _("Not Found"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()

            self._last_found = found
        elif search_id == wx.wxEVT_COMMAND_FIND_REPLACE:
            replacestring = evt.GetReplaceString()
            pool.ReplaceSelection(replacestring)
        elif search_id == wx.wxEVT_COMMAND_FIND_REPLACE_ALL:
            replacestring = evt.GetReplaceString()
            self.SetStart(pool) # Save Start point
            pool.SetTargetStart(0)
            pool.SetTargetEnd(pool.GetLength())
            pool.SetSearchFlags(flag_map[s_flags - wx.FR_DOWN])
            replaced = 0
            while pool.SearchInTarget(query) > 0:
                pool.SetSelection(pool.GetTargetStart(), pool.GetTargetEnd())
                pool.ReplaceSelection(replacestring)
                pool.SetTargetStart(pool.GetTargetEnd() - (len(query) - len(replacestring)))
                pool.SetTargetEnd(pool.GetLength())
                replaced += 1
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
               size=wx.DefaultSize, style=wx.TE_PROCESS_ENTER):
        """Initializes the Search Control"""
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)
        
        # Attributes
        self._parent     = parent
        # TEMP HACK
        self.FindService = parent.GetParent().nb.FindService
        self.histlen     = menulen            # Length of history to keep
        self.recent      = list()             # The History List
        self._last       = None
        self.rmenu       = self.MakeMenu()     # Menu to display search history
        self.max_menu    = 6                  # Max length of history menu
        
        # Recent Search Menu
        self.SetMenu(self.rmenu)

        # Bind Events
        self.Bind(wx.EVT_TEXT_ENTER, self.ProcessEvent)
        self.Bind(wx.EVT_KEY_UP, self.ProcessEvent)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_MENU, self.OnHistMenu)

    #---- Functions ----#
    def MakeMenu(self):
        """Initializes the Search History Menu"""
        menu = wx.Menu()
        lbl = menu.Append(wx.ID_ANY, _("Recent Searches"))
        lbl.Enable(False)
        menu.AppendSeparator()
        return menu

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

        # Check Menu Length
        m_len = self.rmenu.GetMenuItemCount()
        if m_len > self.max_menu:
            self.rmenu.RemoveItem(m_items[-1])

    #---- End Functions ----#

    #---- Event Handlers ----#
    def ProcessEvent(self, evt):
        """Processes Events for the Search Control"""
        e_type = evt.GetEventType()
        if e_type == wx.wxEVT_COMMAND_TEXT_ENTER:
            dev_tool.DEBUGP("[search_evt] Search Text Entered %s" % str(self.GetValue()))
            self.InsertHistoryItem(self.GetValue())
            self.FindService.SetQueryString(self.GetValue())
            self.FindService.SetSearchFlags(wx.FR_DOWN)
            if self.GetValue() != self._last:
                s_cmd = wx.wxEVT_COMMAND_FIND
            else:
                s_cmd = wx.wxEVT_COMMAND_FIND_NEXT
            self._last = self.GetValue()
            self.FindService.OnFind(wx.FindDialogEvent(s_cmd))
        elif e_type == wx.wxEVT_KEY_UP:
            tmp = self.GetValue()
            if len(self.GetValue()) > 0:
                self.ShowCancelButton(True)
            else:
                self.ShowCancelButton(False)

    def OnCancel(self, evt):
        """Cancels the Search Query"""
        self.SetValue("")
        self.ShowCancelButton(False)

    def OnHistMenu(self, evt):
        """Sets the search controls value to the selected menu item"""
        item_id = evt.GetId()
        item = self.rmenu.FindItemById(item_id)
        self.SetValue(item.GetLabel())

    #---- End Event Handlers ----#

