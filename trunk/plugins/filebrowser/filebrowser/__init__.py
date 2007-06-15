# -*- coding: utf-8 -*-
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
# Plugin Meta
"""Adds a File Browser sidepanel"""
__author__ = "Cody Precord"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import os
import stat
import wx
import ed_glob
import ed_main
import ed_menu
import syntax.syntax
import util
import plugin

#-----------------------------------------------------------------------------#
# Globals
PANE_NAME = u'FileBrowser'
ID_BROWSERPANE = wx.NewId()
ID_FILEBROWSE = wx.NewId()
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface implementation
class FileBrowserPanel(plugin.Plugin):
    """Adds a filebrowser to the view menu"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
        mw = parent
        self._log = wx.GetApp().GetLog()
        if mw != None:
            self._log("[filebrowser] Installing filebrowser plugin")
            
            #---- Add Menu Items ----#
            mb = mw.GetMenuBar()
            vm = mb.GetMenuByName("view")
            self._mi = vm.InsertAlpha(ID_FILEBROWSE, _("File Browser"), 
                                      _("Open File Browser sidepanel"),
                                      wx.ITEM_CHECK,
                                      after=ed_glob.ID_PRE_MARK)

            #---- Create File Browser ----#
            self._filebrowser = BrowserPane(mw, ID_BROWSERPANE)

            mw._mgr.AddPane(self._filebrowser, wx.aui.AuiPaneInfo().Name(PANE_NAME).\
                            Caption("Editra | File Browser").Left().Layer(0).\
                            CloseButton(True).MaximizeButton(False).\
                            BestSize(wx.Size(215,350)))
            if ed_glob.PROFILE.get('SHOW_FB', False):
                mw._mgr.GetPane(PANE_NAME).Show()
                self._mi.Check(True)
            else:
                mw._mgr.GetPane(PANE_NAME).Hide()
                self._mi.Check(False)
            mw._mgr.Update()

            # Event Handlers
            mw.Bind(wx.EVT_MENU, self.OnShowBrowser, id = ID_FILEBROWSE)
            mw.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def OnPaneClose(self, evt):
        """Handles when the pane is closed to update the profile"""
        pane = evt.GetPane()
        if pane.name == PANE_NAME:
            ed_glob.PROFILE['SHOW_FB'] = False
            self._mi.Check(False)
        else:
            evt.Skip()

    def OnShowBrowser(self, evt):
        """Shows the filebrowser"""
        if evt.GetId() == ID_FILEBROWSE:
            mw = wx.GetApp().GetMainWindow().GetFrameManager()
            pane = mw.GetPane(PANE_NAME).Hide()
            if ed_glob.PROFILE.get('SHOW_FB', False) and pane.IsShown():
                pane.Hide()
                ed_glob.PROFILE['SHOW_FB'] = False
                self._mi.Check(False)
            else:
                pane.Show()
                ed_glob.PROFILE['SHOW_FB'] = True
                self._mi.Check(True)
            mw.Update()
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#
# Support Classe(s)/Function(s)

class BrowserMenuBar(wx.Panel):
    """Creates a menubar with """
    ID_MARK_PATH = wx.NewId()
    ID_OPEN_MARK = wx.NewId()
    ID_PATHS = wx.NewId()
    ID_REMOVE_MARK = wx.NewId()

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, pos=wx.DefaultPosition,
                          size=wx.DefaultSize, style=wx.NO_BORDER)

        # Attributes
        self._menub = wx.ToggleButton(self, self.ID_PATHS, _("Saved Paths..."))
        self._menu = ed_menu.ED_Menu()
        self._saved = ed_menu.ED_Menu()
        self._rmpath = ed_menu.ED_Menu()
        self._ids = list()  # List of ids of menu items
        self._rids = list() # List of remove menu item ids
        if wx.Platform == '__WXMAC__':
            key = u'Cmd'
        else:
            key = u'Ctrl'
        tt = wx.ToolTip(_("To open multiple files at once %s+Click to select "
                          "the desired files/folders then hit Enter to open "
                          "them all at once") % key)
        self.SetToolTip(tt)

        # Build Menus
        self._menu.Append(self.ID_MARK_PATH, _("Save Selected Paths"))
        self._menu.AppendMenu(self.ID_OPEN_MARK, _("Jump to Saved Path"), self._saved)
        self._menu.AppendSeparator()
        self._menu.AppendMenu(self.ID_REMOVE_MARK, _("Remove Saved Path"), self._rmpath)

        # Layout bar
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add((3,3))
        men_sz = wx.BoxSizer(wx.HORIZONTAL)
        men_sz.Add((6,6))
        men_sz.Add(self._menub, 0, wx.ALIGN_LEFT)
        self._sizer.Add(men_sz)
        self._sizer.Add((3,3))
        self.SetSizer(self._sizer)

        # Event Handlers
        self._menub.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton, id=self.ID_PATHS)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    # XXX maybe change to list the more recently added items near the top
    def AddItem(self, label):
        """Add an item to the saved list, this also adds an identical 
        entry to the remove list so it can be removed if need be.

        """
        id = wx.NewId()
        self._ids.append(id)
        id2 = wx.NewId()
        self._rids.append(id2)
        self._saved.Append(id, label)
        self._rmpath.Append(id2, label)

    def GetOpenIds(self):
        """Returns the ordered list of menu item ids"""
        return self._ids

    def GetRemoveIds(self):
        """Returns the ordered list of remove menu item ids"""
        return self._rids

    def GetItemText(self, id):
        """Retrieves the text label of the given item"""
        item = self.GetSavedMenu().FindItemById(id)
        if item:
            return item.GetLabel()
        else:
            return u''

    def GetRemoveMenu(self):
        """Returns the remove menu"""
        return self._rmpath

    def GetSavedMenu(self):
        """Returns the menu containg the saved items"""
        return self._saved

    # wxBug? The SetValue calls are needed on OSX for the button to 
    #        toggle properly. However On Windows making the calls to 
    #        SetValue cause the button continually pop up the menu without 
    #        dismissing it first.
    def OnButton(self, evt):
        """Pops the menu open when the button has been clicked on"""
        e_id = evt.GetId()
        if e_id == self.ID_PATHS and self._menub.GetValue():
            men_rect = self._menub.GetRect()
            pos = wx.Point(0, men_rect.GetY() + men_rect.GetHeight())
            if wx.Platform == '__WXMAC__':
                self._menub.SetValue(True)
            self._menub.PopupMenu(self._menu, pos)
            if wx.Platform == '__WXMAC__':
                self._menub.SetValue(False)
        else:
            evt.Skip()

    def OnPaint(self, evt):
        """Paints the background of the menubar"""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), -50)
        col2 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), 50)
        grad = gc.CreateLinearGradientBrush(0,1,0,29, col2, col1)
        rect = self.GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width-0.5, rect.height-0.5)

        gc.SetPen(wx.Pen(util.AdjustColour(col1,-60), 1))
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

    def RemoveItemById(self, id):
        """Removes a given menu item from both the saved
        and removed lists using the id as a lookup.

        """
        m_items = self.GetRemoveMenu().GetMenuItems()
        o_ids = self.GetOpenIds()
        r_ids = self.GetRemoveIds()
        index = None

        if id in r_ids:
            index = r_ids.index(id)
            r_item = self.GetRemoveMenu().Remove(id)
            s_item = self.GetSavedMenu().Remove(o_ids[index])
            self._rids.remove(id)
            del self._ids[index]

class BrowserPane(wx.Panel):
    """Creates a filebrowser pane"""
    ID_BROWSE_MENU = wx.NewId()
    ID_SHOW_HIDDEN = wx.NewId()

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER):
        wx.Panel.__init__(self, parent, id, pos, size, style)
        
        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        ff = "".join(syntax.syntax.GenFileFilters())
        self._menbar = BrowserMenuBar(self, self.ID_BROWSE_MENU)
        self._browser = FileBrowser(self, ID_FILEBROWSE, 
                                    dir = wx.GetHomeDir(), 
                                    size = (200,-1),
                                    style = wx.DIRCTRL_SHOW_FILTERS | wx.BORDER_SUNKEN,
                                    filter = ff)
        self._config = PathMarkConfig(ed_glob.CONFIG['CACHE_DIR'])
        for item in self._config.GetItemLabels():
            self._menbar.AddItem(item)
        self._showh_cb = wx.CheckBox(self, self.ID_SHOW_HIDDEN, _("Show Hidden Files"))
        self._showh_cb.SetValue(False)

        # Layout Pane
        self._sizer.Add(self._menbar, 0, wx.EXPAND)
        self._sizer.Add(self._browser, 1, wx.EXPAND)
        self._sizer.Add((2,2))
        cb_sz = wx.BoxSizer(wx.HORIZONTAL)
        cb_sz.Add((4,4))
        cb_sz.Add(self._showh_cb, 0, wx.ALIGN_LEFT)
        self._sizer.Add(cb_sz, 0, wx.ALIGN_LEFT)
        self._sizer.Add((3,3))
        self.SetSizer(self._sizer)

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def __del__(self):
        """Save the config before we get destroyed"""
        self._config.Save()

    def OnCheck(self, evt):
        """Toggles visibility of hidden files on and off"""
        e_id = evt.GetId()
        if e_id == self.ID_SHOW_HIDDEN:
            style = self._browser.GetTreeStyle()
            self._browser.SetTreeStyle(wx.TR_SINGLE)
            self._browser.Refresh()
            self._browser.ShowHidden(self._showh_cb.GetValue())
            self._browser.SetTreeStyle(style)
            self._browser.Refresh()
        else:
            evt.Skip()

    # TODO Add input method so that paths can be given custom
    #      labels
    # TODO after a jump the window should be properly rescrolled
    #      to have the jumped-to path at the top when possible
    def OnMenu(self, evt):
        """Handles the events associated with adding, opening,
        and removing paths in the menubars menus.

        """
        e_id = evt.GetId()
        o_ids = self._menbar.GetOpenIds()
        d_ids = self._menbar.GetRemoveIds()
        if e_id == self._menbar.ID_MARK_PATH:
            items = self._browser.GetPaths()
            for item in items:
                self._menbar.AddItem(item)
                self._config.AddPathMark(item, item)
                self._config.Save()
        elif e_id in o_ids:
            pmark = self._menbar.GetItemText(e_id)
            path = self._config.GetPath(pmark)
            res = self._browser.ExpandPath(path)
            self._browser.SetFocus()
        elif e_id in d_ids:
            plabel = self._menbar.GetItemText(e_id)
            self._menbar.RemoveItemById(e_id)
            self._config.RemovePathMark(plabel)
            self._config.Save()
        else:
            evt.Skip()

    def OnPaint(self, evt):
        """Paints the background of the panel"""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), -50)
        col2 = util.AdjustColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), 50)
        rect = self.GetRect()
        x = 0
        y = rect.height - (self._showh_cb.GetSize()[1] + 6)
        grad = gc.CreateLinearGradientBrush(x, y, x,y+self._showh_cb.GetSize()[1] + 6, col2, col1)

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(x, y, rect.width-0.5, self._showh_cb.GetSize()[1] + 6)

        gc.SetPen(wx.Pen(util.AdjustColour(col1,-60), 1))
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

class FileBrowser(wx.GenericDirCtrl):
    """A hack job done to make the genericdirctrl more useful
    and work with Editra's art provider.

    """
    def __init__(self, parent, id, dir=u'', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DIRCTRL_SHOW_FILTERS,
                 filter=wx.EmptyString, defaultFilter=0):
        wx.GenericDirCtrl.__init__(self, parent, id, dir, pos, 
                                   size, style, filter, defaultFilter)

        # Attributes
        self._tree = self.GetTreeCtrl()
        
        # Set custom styles
        self._tree.SetWindowStyle(self._tree.GetWindowStyle() | wx.TR_MULTIPLE)
        self._tree.Refresh()

        # HACK if the GenericDirCtrl ever changes the order of the images used in it
        #      this will have to be updated accordingly
        if ed_glob.PROFILE['ICONS'].lower() != u'default':
            bmp1 = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU)
            self._imglst = wx.ImageList(bmp1.GetWidth(), bmp1.GetHeight())
            self._imglst.Add(bmp1) # Folder Normal
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_OPEN), wx.ART_MENU)) # Folder Open
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_COMPUTER), wx.ART_MENU))  # Computer
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_HARDDISK), wx.ART_MENU)) # Root drive icon
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_CDROM), wx.ART_MENU))  # CD
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FLOPPY), wx.ART_MENU))  # Floppy
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_USB), wx.ART_MENU))  # Removable
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # Regular Files
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU))  # Binary Files
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # msw cmd Files
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # msw py Files
            if wx.Platform == '__WXMSW__':
                for x in range(6):
                    self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))
            self._tree.SetImageList(self._imglst)

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnOpen)
#         self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragStart)
#         self.Bind(wx.EVT_TREE_END_DRAG, self.OnDragEnd)

    def GetPaths(self):
        """Gets a list of abs paths of the selected items"""
        treeIds = self._tree.GetSelections()
        root = self._tree.GetRootItem()
        ret_val = list()
        for id in treeIds:
            start = id
            atoms = [id]
            while self._tree.GetItemParent(start) != root:
                atoms.append(self._tree.GetItemParent(start))
                start = atoms[-1]
            atoms.reverse()
            path = list()
            for atom in atoms:
                path.append(self._tree.GetItemText(atom))

            if wx.Platform == '__WXMSW__':
                r_txt = u''
            else:
                if path[0] != "/":
                    path.pop(0)
                r_txt = os.path.sep

            ret_val.append(r_txt + util.GetPathChar().join(path))
        return ret_val

    def GetScrollRange(self, orient=wx.VERTICAL):
        """Returns the scroll range of the tree control"""
        return self._tree.GetScrollRange(orient)

    def GetTreeStyle(self):
        """Returns the trees current style"""
        return self._tree.GetWindowStyle()

    def OnOpen(self, evt):
        """Handles item activations events. (i.e double clicked or 
        enter is hit) and passes the clicked on file to be opened in 
        the notebook.

        """
        files = self.GetPaths()
        to_open = list()
        for fname in files:
            try:
                st = os.stat(fname)[0]
                if stat.S_ISREG(st) or stat.S_ISDIR(st):
                    to_open.append(fname)
            except:
                pass
        wx.GetApp().GetMainWindow().nb.OnDrop(to_open)

      # TODO implement drag and drop from the control to the editor
#     def OnDragEnd(self, evt):
#         evt.Skip()

#     def OnDragStart(self, evt):
#         print evt.GetLabel()
#         evt.Skip()

#     def SelectPath(self, path):
#         """Selects the given path"""
#         parts = path.split(os.path.sep)
#         root = self._tree.GetRootItem()
#         rtxt = self._tree.GetItemText(root)
#         item, cookie = self._tree.GetFirstChild(root)
#         while item:
#             if self._tree.ItemHasChildren(item):
#                 i_txt = self._tree.GetItemText(item)
#                 print i_txt
#                 item, cookie = self._tree.GetFirstChild(item)
#                 continue
#             else:
#                 i_txt = self._tree.GetItemText(item)
#                 print i_txt
#             item, cookie = self._tree.GetNextChild(item, cookie)

    def SetTreeStyle(self, style):
        """Sets the style of directory controls tree"""
        self._tree.SetWindowStyle(style)

class PathMarkConfig(object):
    """Manages the saving of pathmarks to make them usable from
    one session to the next.

    """
    CONFIG_FILE = u'pathmarks'

    def __init__(self, pname):
        """Creates the config object, the pname parameter
        is the base path to store the config file at on write.

        """
        object.__init__(self)

        # Attributes
        self._base = os.path.join(pname, self.CONFIG_FILE)
        self._pmarks = dict()

        self.Load()

    def AddPathMark(self, label, path):
        """Adds a label and a path to the config"""
        self._pmarks[label.strip()] = path.strip()

    def GetItemLabels(self):
        """Returns a list of all the item labels in the config"""
        return self._pmarks.keys()

    def GetPath(self, label):
        """Returns the path associated with a given label"""
        return self._pmarks.get(label, u'')

    def Load(self):
        """Loads the configuration data into the dictionary"""
        file_h = util.GetFileReader(self._base)
        if file_h != -1:
            lines = file_h.readlines()
            file_h.close()
        else:
            return False

        for line in lines:
            vals = line.strip().split(u"=")
            if len(vals) != 2:
                continue
            if os.path.exists(vals[1]):
                self.AddPathMark(vals[0], vals[1])
        return True

    def RemovePathMark(self, pmark):
        """Removes a path mark from the config"""
        if self._pmarks.has_key(pmark):
            del self._pmarks[pmark]
        else:
            pass

    def Save(self):
        """Writes the config out to disk"""
        file_h = util.GetFileWriter(self._base)
        if file_h == -1:
            return False

        for label in self._pmarks:
            file_h.write(u"%s=%s\n" % (label, self._pmarks[label]))
        file_h.close()
        return True
