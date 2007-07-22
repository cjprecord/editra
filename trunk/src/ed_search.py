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
            if search_id == wx.wxEVT_COMMAND_FIND_NEXT:#or wx.FR_DOWN & s_flags:
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
                pool.SetSelection(0, 0)
                pool.SearchAnchor()
                found = pool.SearchNext(s_flags | wx.stc.STC_FIND_REGEXP, query)
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

    def OnFindClose(self, evt):
        """Destroy Find Dialog After Cancel is clicked in it
        @param evt: event that called this handler

        """
        self._find_dlg.Destroy()
        self._find_dlg = None
        evt.Skip()

    def OnShowFindDlg(self, evt):
        """Catches the Find events and shows the appropriate find dialog
        @param evt: event that called this handler
        @postcondition: find dialog is shown

        """
        if self._find_dlg != None:
            self._find_dlg.Destroy()
            self._find_dlg = None
        e_id = evt.GetId()
        if e_id == ed_glob.ID_FIND_REPLACE:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, \
                                                  _("Find/Replace"),
                                                  wx.FR_REPLACEDIALOG | \
                                                  wx.FR_NOUPDOWN)
        elif e_id == ed_glob.ID_FIND:
            self._find_dlg = wx.FindReplaceDialog(self._parent, self._data, \
                                                  _("Find"), wx.FR_NOUPDOWN)
        else:
            evt.Skip()
            return
        if wx.Platform == '__WXMAC__' and Profile_Get('METAL', 'bool', False):
            self._find_dlg.SetExtraStyle(wx.DIALOG_EX_METAL)
        self._find_dlg.CenterOnParent()
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
from wx import ImageFromStream, BitmapFromImage
import cStringIO, zlib

def get_search_data():
    """Get raw image data for search image
    @return: raw search image data

    """
    return zlib.decompress(
'x\xda\x01\x8a\x03u\xfc\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x03AIDAT8\x8dm\x93\xcfk\x1ce\x18\xc7\x9f\xe7}\
\xe7gwf7\xeb\xacf\xd3l\xd4M;m\xb5\xddP\x12B\xcc\xc5\x7f@\x0cMs0\xa5 xP\x10\
\xbaj+\xa1\x07\xf1 5\x14-JE\x0f\xb5B\x0f\x85B.Mb\x94"x\x12-\x1a\x8ax\xd8\xb6\
\xa9\xa9\xa6Yw\xf2\xa3\xd9\xddlv3\xb33\xd9y\xdfy\xbd\x18\xd8\xa8\xcf\xf19|\
\xf8<\xcf\xf3}P\x08\x01\xbb5={s\x80R:\x01\x00CQ\x14e\x08!\x0e\x00\xccs\xce/\
\x9d<1\xf6+\xfcO\xa1\x10\x02\xa6goJ\x84\x90ID\xcc\xa7;;\xb5X,\x86\xba\xa6A\
\xc884\x9bMQrJ\x01\x00|\xce9\x7f\xef\xe4\x891\xd6\x0e\x90\x00\x00\x08!\x93\
\x9a\xa6\xe5\xb3\xd9\xac\xbeX\xdabk\xce\x16\x0b\x05Qt\x99\xb42\xa9\x984\xfc\
\xc2\xb0^\xb8[\xc8\xbb\xae\x0b\x00p\xbe\x1d@\xfb\x8e\xe7\x06\x08!Wl\xdb\xd6\
\x7f,\xac\xb7\xaa>q\\\xa1}\x81r\xec\x13MU\x7f\tyt\xa4Tn\x98/\x0e\xf6i\xc5b\
\xb1\xff\xde\xfd\xbb\xdf=w\xe4\xf9\xb5]\x00\xa1\x94N\xa4;;\xb5E\xa7\xce\x9aB\
^\xa9F\x1d\xaf\xda\x99\xf4\x9d\x81\xc3]\xd4H$\x97\xd7}\xe3\rE\xdd\xb7t\x7fy\
\x83\x1d\xb2mM\x92\xa4\x89v\x03\x02\x00Cq3\x8ek\x9b\x01\xf3\x98t\xe3\xc0S\
\x86~\xec\xd9\x0e\xe3\xe8~\xc3\xccX\x8a\xf6d\\QZ\x1c?{\\s\xc3D"\x81\x000\xb4\
g\x07Q\x14e\xcc\xb8\tATU8H?\xc92\xa2\xb7\xc3\x18\x07\x10\x82Q!#b\xc5\x8fJ)9R\
UE\x05\xceyf\x8f\x01\xa5\xd4\tC\x06\xbaDZ\x92`\xc3e\xb7\xc9V7\x83\xa0\xf8\
\xd8\x0b6\x1a~k;h1\x13\xc3\x1e\x8ab\xc7u\xb7\x81R\xea\xfc\xfb\n\xf3\x9e\xe7=\
\x93\xedJH|}\xfb\xf4j\xd9\xff>\nA\xc4\x14\x9d\xf8\xcc\x17\xdb\x1e\x0f\xb3\
\xf1\xe0\x9ce\xe8Zm\xab&\x84\x10\xf3{\x0c\x18c\x97\x96\x1e-\x05C\xc7\xb2\x92\
\xa1\xe0\xd3\x19\xa3yM\t\xeb\xf6V\xbd\xa2\xaa\x91k\xf7\xe8\x8dk2\xf2\x83\xbd\
]\t\\~\xf4\x07V~\xbe\\\xfbO\x90\xbe\xfef\xf6#\xd3\x8c\xe7\xfb\xfb\x07\xf4\
\xdf\x1e\xfc\xc5\x9cr#l\xb1H\xd5U\xba\x93\xee\xd0\xb5\x83\xddI\\|p\x0fRq\x19\
\x16f\xdf\xf5\xab+\x0f/\x9e\xb9\x1e\\\xd8\x93DJ\xe9$"\xe6{\xb3\xbdZ\xdc4QUU\
\xf0<\x17\xea\x8d\x86(.\xff\x89\xb1\xdam8\x94V\xc0::\n\xdf^y\xd3\xaf8\xbf_<s\
=\xb8\x80\xbb\xbf\x80\x88\xd2\xd5\xaf\xbe\x1c\xb4R\xd69J\xc8`$D7"\xaep\xce\
\xef\xac\xdf\xbe\\\x83\x8d\xf9S}\xf6~#s\xfceH\xf5\xbd\x02\xb7\xae\xbe\xe5\
\x97\x9d\x85\x0fP\x08\x01\x88\xa8\x00\x80\x02\x00\x8aeYR.\x97\xc3d2\x89\xb5Z\
M\x14\n\x05Q\xadV\xd9\x87c\xf4lB\xc7wr\x07\x9e0\xbas/\x015{\xe0\xd6\x8d\x8f+\
\xed\x00\r\x00\xd4\xd1\xd1Q:>>NFFF\xc8\xdc\xdc\\455\x15\xcd\xcc\xccp\x00\x08\
>=E\xcfj2N\xf4v\xed3\xaa\x9e\x14l\xd6\xbd\xe9\xf6\x11\x08\x00\xc8\xbb&\xb2,c\
\x18\x86\x0c\x00Z\x00\x80\xff\xf4c\xef\x8f\x90\xb7-\x03_o1\xf8aa5z\xedo\x934\
z\x98\xc4#\x8c\t\x00\x00\x00\x00IEND\xaeB`\x82>\xaa\x97\xf1' )

def get_search_bitmap():
    """Convert search image data to bitmap format
    @return: bitmap version of search image

    """
    return BitmapFromImage(get_search_image())

def get_search_image():
    """Get an wxImage version of the raw image data
    @return: image version of search image

    """
    stream = cStringIO.StringIO(get_search_data())
    return ImageFromStream(stream)

def get_search_close_data():
    """Search close button raw data
    @return: raw cancel button image data

    """
    return zlib.decompress(
'x\xda\x01\xbb\x01D\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x01rIDAT8\x8d\xa5\x93=\x8e\xe2@\x10\x85?[\x13\
\xd8\xfcK-A\xd2\x02\x11\x80\x10\xf8\x0e^_`\xa3\r8"1\x17\xf0\xce\x1e\x01\x99\
\xc0$N\x00\t\x89\x96E\xb0^\xd3n\xf0&x\xc5\nf\x82\xa1\xa2\xea\xa7\xae\xaa~\
\xf5^[eY\xf2J\xd8/U\x03o\xf7\x87 \x08\xde\x84\x10\x0b\x00\xa5\xd4<\x0cC\xf3\
\x19\x0e`U\x14n\x97\x96\x9e\xe7\x05\xb6m\xb3Z\xadB\xa5\xd4w\x80gx\xd5\xe4\
\xdf\x0b\x84\x10\x8b\xe9t\x1aH)\x9d\xcb\xe5\x82\xe7yA\x14EK\x80\xd9l\x16H)\
\x1d\x80\xeb\xf5\x1aDQ\xb4\x00~<P0\xc6\xa0\xb5&\x8ec\xc6\xe3\xb13\x99L|\x80^\
\xaf\xe7\xac\xd7kF\xa3\x11Z\xeb\xe7;PJ\xcd7\x9b\xcd\xd2\x18\x13\x0c\x06\x03\
\'\x8ec\x86\xc3a\r\xe0\x96\x93$I\x9e$I\xa8\x94\x9a?\xec\xe0~\x0f\xfd~\xdf\
\xefv\xbb\xb5\xddn\x87eYH)\xd9\xef\xf7\xd9v\xbb}\xbf\xe7\xff@\xa1\n\xadu\xa9\
\xb5\xa6j\x9e\xe79\xc6\x98\xa7\x86yPA\x08\xf1M\x08\xe1\x9eN\'\xda\xed6\x00U\
\xae\x94\xfa\xa3\x94\xfa\xf9\xa1\n\xadV\xcbo4\x1an\x9a\xa6\xb8\xae\xcb\xe1p\
\xf8]\x96%\x9dN\xa7\x9e\xa6)\xf5z\xdd-\x8a\xc2\x07>V!\xcfsl\xdb\xe6x<fY\x96\
\xfd\xba\xe1~\xb3\xd9\xac\x9d\xcfg\x8c1\xf7%\xff\xab\x00,o\x13(\x8a\xe2\xbd2\
\xd2\x13\xfcS\x15\xbef\xe5\xaf\xc6\xcb\xbf\xf1/p\x8b\xfb\xa1\xbb\xf8z\x0e\
\x00\x00\x00\x00IEND\xaeB`\x82\xb1E\xc6:' )

def get_search_close_bitmap():
    """Get a bitmap of the close button
    @return: bitmap of cancel button

    """
    return BitmapFromImage(get_search_close_image())

def get_search_close_image():
    """Get a wxImage version of the close button
    @return: image of cancel button

    """
    stream = cStringIO.StringIO(get_search_close_data())
    return ImageFromStream(stream)

class EdSearchCtrl(wx.SearchCtrl):
    """Creates a simple search control for use in the toolbar
    or a statusbar and the such. Supports incremental search,
    and uses L{FindService} to do the actual searching of the
    document.

    """
    def __init__(self, parent, id_, value="", menulen=0, \
                 pos=wx.DefaultPosition, size=wx.DefaultSize, \
                 style=wx.TE_PROCESS_ENTER | wx.TE_RICH2):
        """Initializes the Search Control
        @param menulen: max length of history menu

        """
        wx.SearchCtrl.__init__(self, parent, id_, value, pos, size, style)
        
        # Attributes
        self._parent     = parent
        # TEMP HACK
        self.FindService = parent.GetParent().nb.FindService
        self._flags      = wx.FR_DOWN
        self._recent     = list()             # The History List
        self._last       = None
        self.rmenu       = wx.Menu()
        self.max_menu    = menulen            # Max length of history menu

        # Make it look a little nicer on gtk
        if wx.Platform == '__WXGTK__':
            self.SetSearchBitmap(get_search_bitmap())
            self.SetCancelBitmap(get_search_close_bitmap())

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
        self.Bind(wx.EVT_TEXT_ENTER, self.ProcessEvent)
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
            self.rmenu.RemoveItem(m_items[-1])

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
        if e_type == wx.wxEVT_COMMAND_TEXT_ENTER:
            dev_tool.DEBUGP("[search_evt] Search Entered: %s" % self.GetValue())
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
            if tmp == wx.EmptyString or \
               evt.CmdDown() or e_key == wx.WXK_COMMAND:
                return
            if wx.Platform == '__WXMAC__' and len(self.GetValue()) > 0:
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
