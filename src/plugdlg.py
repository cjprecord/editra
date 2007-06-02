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
import os
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
BASE_URL = "http://editra.org/"
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
        self._p_list = dict()           # list of available plugins/meta
        self._dl_list = dict()          # List of download urls
        self._eggcount = 0              # Number of plugins to download
        self._eggbasket = dict()        # Basket of downloaded eggs
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

    # XXX *args is really a string but for some reason when it passed
    #     here from startWorker it gets broken into a list of chars
    def _DownloadPlugin(self, *args):
        """Downloads the plugin at the given url"""
        url = "".join(args)
        egg = None
        try:
            h_file = urllib.urlopen(url)
            egg = h_file.read()
            h_file.close()
        finally:
            return (url.split("/")[-1], True, egg)

    # TODO possibly process this on a separate thread to keep the 
    #      gui responsive.
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

    def _ResultCatcher(self, delayedResult):
        """Catches the results from the download worker threads"""
        frame = self.GetGrandParent()
        self._eggcount = self._eggcount - 1
        try:
            result = delayedResult.get()
            plug = result[0]
            if result[1]:
                self._eggbasket[plug] = result[2]
                frame.SetStatusText(_("Downloaded") + ": " + plug, 0)
        finally:
            if not self._eggcount:
                frame.SetStatusText(_("Complete"), 1)
                frame.SetStatusText(_("Finshed downloading plugins"), 0)
                inst_pg = self.GetParent().GetPage(INSTALL_PG)
                for key in self._eggbasket:
                    inst_pg.AddItemToInstall(key)
                self.GetParent().SetSelection(INSTALL_PG)

    def GetDownloadedData(self):
        """Returns the dictionary of downloaded data or an
        empty dictionary if no data has been downloaded.

        """
        return self._eggbasket

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

    def IsDownloading(self, evt):
        """Returns whether the panel has active download
        threads or not.

        """
        if self._eggcount:
            return True
        else:
            return False

    def OnButton(self, evt):
        """Handles the Button Events"""
        e_id = evt.GetId()
        if e_id == self.ID_DOWNLOAD:
            urls = list()
            for item in self._dl_list:
                if self._dl_list[item]:
                    urls.append(BASE_URL + self._p_list[item].GetUrl())
            self._eggcount = len(urls)
            for egg in range(len(urls)):
                self.GetGrandParent().SetStatusText(_("Downloading") + "...", 1)
                delayedresult.startWorker(self._ResultCatcher, self._DownloadPlugin,
                                          wargs=(urls[egg]), jobID=egg)
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
    ID_INSTALL = wx.NewId()
    ID_USER = wx.NewId()
    ID_SYS = wx.NewId()

    def __init__(self, parent, id, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER):
        """ """
        wx.Panel.__init__(self, parent, id, pos, size, style)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, wx.ID_ANY,
                            _("Click on Install to install the plugins in the list"))
        self._install = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SORT)
        self._instb = wx.Button(self, self.ID_INSTALL, _("Install"))
        self._usercb = wx.CheckBox(self, self.ID_USER, _("User Directory"))
        self._usercb.SetValue(True)
        self._usercb.SetToolTip(wx.ToolTip(_("Install the plugins only for the current user")))
        self._syscb = wx.CheckBox(self, self.ID_SYS, _("System Directory"))
        self._syscb.SetToolTip(wx.ToolTip(_("Install the plugins for all users,"
                                            " **requires administrative privileges**")))

        # Layout Panel
        self._sizer.Add(lbl, 0, wx.ALIGN_CENTER)
        self._sizer.Add(self._install, 1, wx.EXPAND)
        self._sizer.Add(wx.Size(5,5))
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(wx.Size(5,5))
        bsizer.Add(self._usercb, 0, wx.ALIGN_LEFT)
        bsizer.Add(wx.Size(5,5))
        bsizer.Add(self._syscb, 0, wx.ALIGN_LEFT)
        bsizer.AddStretchSpacer()
        bsizer.Add(self._instb, 0, wx.ALIGN_RIGHT)
        bsizer.Add(wx.Size(5,5))
        self._sizer.Add(bsizer, 0, wx.EXPAND)
        self._sizer.Add(wx.Size(5,5))
        self.SetSizer(self._sizer)
        self.SendSizeEvent()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)

    def _Install(self):
        """Install the plugins in the list"""
        items = self._install.GetItems()
        user = self.FindWindowById(self.ID_USER)
        sysp = self.FindWindowById(self.ID_SYS)
        if sysp and sysp.GetValue():
            inst_loc = ed_glob.CONFIG['SYS_PLUGIN_DIR']
        else:
            inst_loc = ed_glob.CONFIG['PLUGIN_DIR']
        for item in items:
            egg_name = item.split("/")[-1]
            if os.path.isabs(item):
                try:
                    reader = file(item, "rb")
                    egg = reader.read()
                    reader.close()
                except IOError:
                    continue
            else:
                dl_pg = self.GetParent().GetPage(DOWNLOAD_PG)
                egg = dl_pg.GetDownloadedData().get(item, None)
                if not egg:
                    continue

            try:
                writer = file(inst_loc + egg_name, "wb")
                writer.write(egg)
            except IOError:
                continue
            else:
                # If successfully installed remove from list
                ind = self._install.FindString(item)
                if ind != wx.NOT_FOUND:
                    self._install.Delete(ind)
        self.GetGrandParent().SetStatusText(_("Finished Installing Plugins"), 0)

    def AddItemToInstall(self, item):
        """Adds an item to the install list, the item
        should be a string of the path to the item or
        the items name if it is an in memory file from the
        download page.

        """
        if self._install.FindString(item) == wx.NOT_FOUND:
            self._install.Append(item)
        else:
            pass

    def OnButton(self, evt):
        """Handles button events generated by the panel"""
        e_id = evt.GetId()
        if e_id == self.ID_INSTALL:
            self._Install()
        else:
            evt.Skip()

    def OnCheckBox(self, evt):
        """Handles the checkbox events to make sure that
        only one of the two check boxes is checked at a time

        """
        e_id = evt.GetId()
        val = evt.GetEventObject().GetValue()
        u_cb = self.FindWindowById(self.ID_USER)
        s_cb = self.FindWindowById(self.ID_SYS)
        if e_id == self.ID_USER:
            if not s_cb.IsEnabled():
                u_cb.SetValue(True)
            elif val:
                s_cb.SetValue(False)
            else:
                s_cb.SetValue(True)
        elif e_id == self.ID_SYS:
            if val:
                u_cb.SetValue(False)
            else:
                u_cb.SetValue(True)
        else:
            pass
        evt.Skip()

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

        
