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
# FILE:	plugdlg.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#     Provides a dialog for downloading, installing and configuring        #
# plugins for Editra.                                                      #
#                                                                          #
# METHODS:                                                                 #
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import sys
import urllib
import wx
import wx.lib.delayedresult as delayedresult
import wx.lib.mixins.listctrl as listmix
import ed_glob
import ed_event
import plugin
import util

#--------------------------------------------------------------------------#
# Globals
CONFIG_PG = 0
DOWNLOAD_PG = 1
INSTALL_PG = 2
PLUGIN_REPO = "http://editra.org/plugins.php?list=True"

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class PluginDialog(wx.Frame):
    """Defines a Plugin manager Dialog that can be used to download plugins
    from a defined repository, offers servcies to install plugins that
    where downloaded with or without the dialog, as well as configure
    already installed plugins. It is instanciated as a standalone window
    when the show method is called so that if downloads are taking along time
    it does not interfere with usage of the editor.

    """
    def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        """Creates the dialog, does not call Show()"""
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._nb = PluginPages(self, wx.ID_ANY)
        
        # Layout Dialog
        self._sizer.Add(self._nb, 1, wx.EXPAND)
        self._title = title
        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)
        self.CreateStatusBar(2)
        self.SetStatusWidths([-1, 155]) # TODO variable width

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        """Handles closing the dialog and unregistering it from
        the mainloop.

        """
        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()

    def Show(self, show=True):
        """Shows the dialog and registers it with the mainloop"""
        wx.GetApp().RegisterWindow(repr(self), self, True)
        wx.Frame.Show(self, show)

#--------------------------------------------------------------------------#

class PluginPages(wx.Toolbook):
    """A notebook that contains three pages. One for downloading,
    One for installing, and one for configuration.

    """
    def __init__(self, parent, id, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=wx.TB_TOP):
        """Creates the Notebook"""
        wx.Toolbook.__init__(self, parent, id, pos, size, style)

        # Create Pages
        self._imglst = wx.ImageList(32,32)
        self._imgind = dict()
        self._imgind[CONFIG_PG] = self._imglst.Add(wx.ArtProvider.GetBitmap( 
                                                   str(ed_glob.ID_PLUGIN_CFG), wx.ART_OTHER))
        self._imgind[DOWNLOAD_PG] = self._imglst.Add(wx.ArtProvider.GetBitmap(
                                                  str(ed_glob.ID_PLUGIN_DL), wx.ART_OTHER))
        self._imgind[INSTALL_PG] = self._imglst.Add(wx.ArtProvider.GetBitmap( 
                                                  str(ed_glob.ID_PLUGIN_INST),wx.ART_OTHER))
        self._config = ConfigPanel(self, wx.ID_ANY)
        self._download = DownloadPanel(self, wx.ID_ANY)
        self._install = InstallPanel(self, wx.ID_ANY)
        self.SetImageList(self._imglst)

        # Add Pages
        self.AddPage(self._config, _("Configure"), imageId=self._imgind[CONFIG_PG])
        self.AddPage(self._download, _("Download"), imageId=self._imgind[DOWNLOAD_PG])
        self.AddPage(self._install, _("Install"), imageId=self._imgind[INSTALL_PG])
        self.SetSelection(CONFIG_PG)

        # Event handlers
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanging(self, evt):
        """Updates pages as they are being changed to"""
        cur_pg = evt.GetSelection()
        parent = self.GetParent()
        parent.SetTitle(parent._title + " | " + self.GetPageText(cur_pg))
        if cur_pg == CONFIG_PG:
            self._config.PopulateCtrl()
        elif cur_pg == DOWNLOAD_PG:
            self._download.PopulateList()
        elif cur_pg == INSTALL_PG:
            pass
        else:
            pass
        evt.Skip()

class ConfigPanel(wx.Panel):
    """Creates a panel for configuring plugins."""
    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER):
        """Build config panel"""
        wx.Panel.__init__(self, parent, id, pos, size, style)
        self._list = PluginListCtrl(self)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Layout List Control
        self._list.InsertColumn(0, _("Plugin"))
        self._list.InsertColumn(1, _("Description"))
        self._list.InsertColumn(2, _("Author"))
        self._list.InsertColumn(3, _("Version"))
        self.PopulateCtrl()

        # Layout Panel
        self._sizer.Add(wx.StaticText(self, wx.ID_ANY, 
                        _("To enable a plugin check the box next to its label")),
                        0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizer.Add(wx.Size(10,10))
        self._sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(self._sizer)

        # Event handlers
        self.Bind(ed_event.EVT_NOTIFY, self.OnNotify)

    def OnNotify(self, evt):
        """Handles the notification events that are
        posted from the list control.

        """
        index = evt.GetId()
        plugin = self._list.GetItemText(index)
        pmgr = wx.GetApp().GetPluginManager()
        if evt.GetValue():
            pmgr.EnablePlugin(plugin)
        else:
            pmgr.DisablePlugin(plugin)

    def PopulateCtrl(self):
        """Populates the list of plugins and sets the
        values of their states. Any successive calls to
        this function will clear the list and Repopulate it
        with current config values. Returns the number of
        items populated to the list

        """
        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        p_mgr = wx.GetApp().GetPluginManager()
        for item in p_mgr.GetConfig():
            mod = sys.modules.get(item)
            try:
                doc = str(mod.__doc__)
            except:
                doc = _("No Description Available")
            try:
                auth = str(mod.__author__)
            except:
                auth = _("Unknown")
            try:
                ver = str(mod.__version__)
            except:
                ver = _("Unknown")

            index = self._list.InsertStringItem(sys.maxint, item)
            self._list.SetStringItem(index, 0, item)
            self._list.CheckItem(index, p_mgr._config[item])
            self._list.SetStringItem(index, 1, doc)
            self._list.SetStringItem(index, 2, auth)
            self._list.SetStringItem(index, 3, ver)

        self._list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self._list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self._list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self._list.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self._list.SendSizeEvent()
        return self._list.GetItemCount()

class DownloadPanel(wx.Panel):
    """Creates a panel with controls for downloading plugins."""
    ID_DOWNLOAD = wx.NewId()

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER):
        """ """
        wx.Panel.__init__(self, parent, id, pos, size, style)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._p_list = dict()
        self._dl_list = dict()
        self._list = PluginListCtrl(self)
        self._downlb = wx.Button(self, self.ID_DOWNLOAD, _("Download"))

        # Layout List Control
        self._list.InsertColumn(0, _("Plugin"))
        self._list.InsertColumn(1, _("Description"))
        self._list.InsertColumn(2, _("Author"))
        self._list.InsertColumn(3, _("Version"))

        # Layout Panel
        self._sizer.Add(wx.StaticText(self, wx.ID_ANY,
                        _("Select the desired plugins and then Click Download")),
                        0, wx.ALIGN_CENTER)
        self._sizer.Add(self._list, 1, wx.EXPAND)
        self._sizer.Add(wx.Size(5,5))
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self._downlb, 0, wx.ALIGN_RIGHT)
        bsizer.Add(wx.Size(5,5))
        self._sizer.Add(bsizer, 0, wx.ALIGN_RIGHT)
        self._sizer.Add(wx.Size(5,5))
        self.SetSizer(self._sizer)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(ed_event.EVT_NOTIFY, self.OnNotify)

    def _GetPluginListData(self, url=PLUGIN_REPO):
        """Gets the list of plugins and their related meta data
        as a string and returns it.
        
        """
        text = u''
        try:
            h_file = urllib.urlopen(url)
            text = h_file.read()
            h_file.close()
        finally:
            return text

    def GetPluginList(self, url=PLUGIN_REPO):
        """Gets the list of available plugins from the web and returns
        it as a dictionary of names mapped to metadata.

        """
        plugins = self._GetPluginListData().split("###")
        p_list = dict()
        for meta in plugins:
            data = meta.split("\n")
            if len(data) < 4:
                continue
            tmpdat = PluginData()
            for attr in data:
                tmp = attr.split("=")
                if len(tmp) != 2:
                    continue
                set_map = {'author' : tmpdat.SetAuthor,
                           'version' : tmpdat.SetVersion,
                           'name' : tmpdat.SetName,
                           'url' : tmpdat.SetUrl,
                           'description' : tmpdat.SetDescription}
                funct = set_map.get(tmp[0].lower(), None)
                if funct:
                    funct(tmp[1].strip())
            if tmpdat.GetName() != u'':
                p_list[tmpdat.GetName()] = tmpdat
        return p_list

    def OnButton(self, evt):
        """Handles the Button Events"""
        e_id = evt.GetId()
        if e_id == self.ID_DOWNLOAD:
            pass
        else:
            evt.Skip()

    def OnNotify(self, evt):
        """Handles the notification events that are posted by the
        list control when items are checked.

        """
        index = evt.GetId()
        flag = evt.GetValue()
        plugin = self._list.GetItemText(index)
        if flag:
            self._dl_list[plugin] = flag
        else:
            if self._dl_list.has_key(plugin):
                del self._dl_list[plugin]

    def PopulateList(self):
        """Populates the list control based off data in the plugin data
        list.

        """
        self._p_list = self.GetPluginList()
        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        for item in self._p_list:
            index = self._list.InsertStringItem(sys.maxint, item)
            self._list.SetStringItem(index, 0, item)
            self._list.SetStringItem(index, 1, self._p_list[item].GetDescription())
            self._list.SetStringItem(index, 2, self._p_list[item].GetAuthor())
            self._list.SetStringItem(index, 3, self._p_list[item].GetVersion())

        self._list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self._list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self._list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        self._list.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self._list.SendSizeEvent()
        return self._list.GetItemCount()

class InstallPanel(wx.Panel):
    """Creates a panel for installing plugins."""
    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER):
        """ """
        wx.Panel.__init__(self, parent, id, pos, size, style)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)

        # Layout Panel
        sbmp = wx.StaticBitmap(self, wx.ID_ANY, wx.ArtProvider.GetBitmap(str(ed_glob.ID_DOWNLOAD_DLG), wx.ART_OTHER))
        self._sizer.Add(sbmp, 0, wx.ALIGN_CENTER)
#--------------------------------------------------------------------------#

class PluginListCtrl(wx.ListCtrl, 
                     listmix.ListCtrlAutoWidthMixin,
                     listmix.CheckListCtrlMixin):
    """Creates a list control for displaying plugins and configuring them."""
    def __init__(self, parent):
        """Initializes the Profile List Control"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, wx.DefaultSize, 
                             style = wx.LC_REPORT | wx.LC_SORT_ASCENDING |
                                     wx.LC_VRULES)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.CheckListCtrlMixin.__init__(self)

    def GetItemValues(self):
        """Returns a dictionary of item names mapped to check values,
        where the item name is the item at column zero and the
        dictionary contains all entries in the list.

        """
        item_vals = dict()
        for item in range(self.GetItemCount()):
            plugin = self.GetItemText(item)
            item_vals[plugin] = self.IsChecked(item)
        return item_vals

    def OnCheckItem(self, index, flag):
        """Sends a custom notification event to the lists parent
        so that it can handle the check event if it needs to.

        """
        evt = ed_event.NotificationEvent(ed_event.edEVT_NOTIFY, index, flag, self)
        wx.PostEvent(self.GetParent(), evt)
        listmix.CheckListCtrlMixin.OnCheckItem(self, index, flag)

class PluginData(plugin.PluginData):
    """Plugin Metadata storage class used to store data
    about plugins and where to download them from.

    """
    def __init__(self, name=u'', descript=u'', author=u'', ver=u'', url=u''):
        plugin.PluginData.__init__(self, name, descript, author, ver)
        self._url = url

    def GetUrl(self):
        """Returns the URL of the plugin"""
        return self._url

    def SetUrl(self, url):
        """Sets the url of the plugin"""
        if not isinstance(url, basestring):
            try:
                url = str(url)
            except:
                url = u''
        self._url = url

        
