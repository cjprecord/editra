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
"""Adds a File Browser sidepanel"""
__author__ = "Cody Precord"
__version__ = "0.1"

import os
import stat
import wx
import ed_glob
import ed_main
import ed_menu
import syntax.syntax
import util
import plugin

ID_FILEBROWSE = wx.NewId()
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
            fbrow = vm.InsertAlpha(ID_FILEBROWSE, _("File Browser"), 
                                   _("Open File Browser sidepanel"), 
                                   after=ed_glob.ID_PRE_MARK)

            #---- Create File Browser ----#
            ff = "".join(syntax.syntax.GenFileFilters())
            self._filebrowser = FileBrowser(mw, ID_FILEBROWSE, 
                                            dir = wx.GetHomeDir(), 
                                            size = (200,-1),
                                            style = wx.DIRCTRL_SHOW_FILTERS,
                                            filter = ff)

            mw._mgr.AddPane(self._filebrowser, wx.aui.AuiPaneInfo().Name("FileBrowser").\
                            Caption("Editra | File Browser").Left().Layer(0).\
                            CloseButton(True).MaximizeButton(False).\
                            BestSize(wx.Size(200,350)))
            mw._mgr.GetPane("FileBrowser").Hide()
            mw._mgr.Update()

            # Event Handlers
            mw.Bind(wx.EVT_MENU, self.OnShowBrowser, id = ID_FILEBROWSE)

    def OnShowBrowser(self, evt):
        """Shows the filebrowser"""
        mw = wx.GetApp().GetMainWindow().GetFrameManager()
        if evt.GetId() == ID_FILEBROWSE:
            mw.GetPane("FileBrowser").Show()
            mw.Update()
        else:
            evt.Skip()

class FileBrowser(wx.GenericDirCtrl):
    """A hack job done to make the genericdirctrl more useful
    and fit in to the editors environment better.

    """
    def __init__(self, parent, id, dir=u'', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DIRCTRL_SHOW_FILTERS,
                 filter=wx.EmptyString, defaultFilter=0):
        wx.GenericDirCtrl.__init__(self, parent, id, dir, pos, 
                                   size, style, filter, defaultFilter)
        self._tree = self.GetTreeCtrl()
        
        # Set custom styles
        self._tree.SetWindowStyle(self._tree.GetWindowStyle() | wx.TR_MULTIPLE)
        self._tree.Refresh()
        if ed_glob.PROFILE['ICONS'].lower() != u'default':
            bmp1 = wx.ArtProvider.GetBitmap(str(ed_glob.ID_OPEN), wx.ART_MENU)
            self._imglst = wx.ImageList(bmp1.GetWidth(), bmp1.GetHeight())
            self._imglst.Add(bmp1)
            self._imglst.Add(bmp1)
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # ???
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_HARDDISK), wx.ART_MENU)) # Root drive icon
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # ???
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # ???
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # ???
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU))  # Regular Files
            self._imglst.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU))  # Binary Files
            self._tree.SetImageList(self._imglst)

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnOpen)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragStart)
        self.Bind(wx.EVT_TREE_END_DRAG, self.OnDragEnd)

    def GetPaths(self, treeIds):
        """Builds a list of abs paths from a list of tree item ids"""
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
            print path, self._tree.GetItemText(root)
            if wx.Platform == '__WXMAC__':
                path.insert(0, u'/Volumes')
            else:
                # This needs testing
                path.insert(self._tree.GetItemText(root))
            ret_val.append(os.path.normpath(util.GetPathChar().join(path)))
        return ret_val

    def OnOpen(self, evt):
        """Handles item activations events. (i.e double clicked or 
        enter is hit) and passes the clicked on file to be opened in 
        the notebook.

        """
        nodes = self._tree.GetSelections()
        files = self.GetPaths(nodes)
        to_open = list()
        for fname in files:
            try:
                st = os.stat(fname)[0]
                if stat.S_ISREG(st):
                    to_open.append(fname)
            except:
                pass
        self.GetParent().nb.OnDrop(to_open)

    def OnDragEnd(self, evt):
        evt.Skip()

    def OnDragStart(self, evt):
        evt.Skip()
