###############################################################################
# Name: plugdlg.py                                                            #
# Purpose: User interface into the PluginManager, also provides interface for #
#          downloading and installing plugins.                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE:	plugdlg.py                                                         #
# @author: Cody Precord                                                    #
# LANGUAGE: Python                                                         #
# @summary:                                                                #
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
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import sys
import os
import re
import urllib
import wx
import wx.lib.delayedresult as delayedresult
# import wx.lib.mixins.listctrl as listmix
import extern.listctrl as listmix
import ed_glob
from profiler import Profile_Get, Profile_Set
import ed_event
import plugin
import util

#--------------------------------------------------------------------------#
# Globals
CONFIG_PG = 0
DOWNLOAD_PG = 1
INSTALL_PG = 2
PY_VER = str(sys.version_info[0]) + str(sys.version_info[1])
BASE_URL = "http://editra.org/"
PLUGIN_REPO = "http://editra.org/plugins.php?list=True&py=" + PY_VER

_ = wx.GetTranslation

#--------------------------------------------------------------------------#

def MakeThemeTool(tool_id):
    """Makes a themed bitmap for the tool book of the plugin dialog.
    @param tool_id: An art identifier id
    @return: 32x32 bitmap
    @todo: why does drawing a bitmap overlay on gtk not draw on transparent area

    """
    osize = Profile_Get('ICON_SZ', 'size_tuple', (24, 24))
    Profile_Set('ICON_SZ', (32, 32))
    base = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
    Profile_Set('ICON_SZ', osize)
    if not base.IsOk() or base.GetSize() != (32, 32):
        base = wx.ArtProvider.GetBitmap(wx.ART_WARNING, 
                                        wx.ART_TOOLBAR, 
                                        size=(32, 32))

    over = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PLUGMGR), wx.ART_MENU)
    if over.IsOk():
        # Draw overlay onto button
        mdc = wx.MemoryDC()
        mdc.SelectObject(base)
        mdc.SetBrush(wx.TRANSPARENT_BRUSH)
        mdc.SetPen(wx.TRANSPARENT_PEN)
        mdc.DrawBitmap(over, 15, 15, False)
        mdc.SelectObject(wx.NullBitmap)

    return base
    
#--------------------------------------------------------------------------#

class PluginDialog(wx.Frame):
    """Defines a Plugin manager Dialog that can be used to download plugins
    from a defined repository, offers servcies to install plugins that
    where downloaded with or without the dialog, as well as configure
    already installed plugins. It is instanciated as a standalone window
    when the show method is called so that if downloads are taking along time
    it does not interfere with usage of the editor.

    """
    def __init__(self, parent, fid, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        """Creates the dialog, does not call Show()"""
        wx.Frame.__init__(self, parent, fid, title, pos, size, style)
        util.SetWindowIcon(self)

        if wx.Platform == '__WXMAC__' and Profile_Get('METAL', 'bool', False):
            self.SetExtraStyle(wx.FRAME_EX_METAL)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sb = DownloadStatusBar(self)
        self.SetStatusBar(self._sb)
        self._nb = PluginPages(self)
        
        # Layout Dialog
        self._sizer.Add(self._nb, 1, wx.EXPAND)
        self._title = title
        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        """Handles closing the dialog and unregistering it from
        the mainloop.
        @param evt: Event fired that called this handler
        @type evt: wx.EVT_CLOSE

        """
        busy = self._nb.IsBusy()
        if busy:
            dlg = wx.MessageDialog(self, busy, _("Do you wish to exit"), 
                                   style = wx.YES_NO | wx.ICON_EXCLAMATION | \
                                           wx.CENTER)
            result = dlg.ShowModal()
            if result == wx.YES:
                return
            else:
                pass
        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()

    def Show(self, show=True):
        """Shows the dialog
        @postcondition: Dialog is registered with the main loop and shown

        """
        wx.GetApp().RegisterWindow(repr(self), self, True)
        wx.Frame.Show(self, show)

    def Busy(self, busy=True):
        """Set the status of the frame to be busy or not
        @keyword busy: Start or Stop being busy

        """
        if busy:
            self._sb.StartBusy()
        else:
            self._sb.StopBusy()

#--------------------------------------------------------------------------#

class DownloadStatusBar(wx.StatusBar):
    """Custom StatusBar with a builtin progress bar"""
    def __init__(self, parent):
        """Creates a status bar that can hide and show a progressbar
        in the far right divider.
        @param parent: Frame this status bar belongs to

        """
        wx.StatusBar.__init__(self, parent, style=wx.SB_FLAT)
  
        # Attributes
        self._changed = False
        self.timer = wx.Timer(self)
        self.prog = wx.Gauge(self, style=wx.GA_HORIZONTAL)
        self.prog.Hide()

        # Layout
        self.SetFieldsCount(2)
        self.SetStatusWidths([-1, 155])

        # Event Handlers
        self.Bind(wx.EVT_TIMER, self.OnTick)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

    def __del__(self):
        """Make sure the timer is stopped
        @postcondition: timer is cleaned up

        """
        if self.timer.IsRunning():
            self.timer.Stop()

    def Destroy(self):
        """Cleanup timer
        @postcondition: timer is cleaned up and status bar is destroyed

        """
        if self.timer.IsRunning():
            self.timer.Stop()
        del self.timer
        wx.StatusBar.Destroy(self)

    def OnIdle(self, evt):
        """Reposition progress bar as necessary on moves, ect...
        @param evt: wx.EVT_IDLE

        """
        if self._changed:
            self.Reposition()
        evt.Skip()

    def OnSize(self, evt):
        """Reposition progress bar on resize
        @param evt: wx.EVT_SIZE

        """
        self.Reposition()
        self._changed = True
        evt.Skip()

    def OnTick(self, evt):
        """Update progress bar
        @param evt: wx.EVT_TIMER

        """
        self.prog.Pulse()

    def Reposition(self):
        """Does the actual repositioning of progress bar
        @postcondition: Progress bar is repostioned to right side

        """
        rect = self.GetFieldRect(1)
        self.prog.SetPosition((rect.x + 2, rect.y + 2))
        self.prog.SetSize((rect.width - 4, rect.height - 4))
        self._changed = False

    def StartBusy(self):
        """Start the timer
        @postcondition: Progress bar is shown and animated

        """
        self.Reposition()
        self.prog.Show()
        self.timer.Start(100)

    def StopBusy(self):
        """Stop the timer
        @postcondition: Progress bar is hidden from view

        """
        self.prog.Hide()
        self.timer.Stop()

#--------------------------------------------------------------------------#

class PluginPages(wx.Toolbook):
    """A notebook that contains three pages. One for downloading,
    One for installing, and one for configuration.

    """
    def __init__(self, parent, id_=wx.ID_ANY, style=wx.TB_TOP):
        """Creates the Toolbook"""
        wx.Toolbook.__init__(self, parent, id=id_, style=style)

        # Create Pages
        self._imglst = wx.ImageList(32, 32)
        self._imgind = dict()
        bmp = MakeThemeTool(ed_glob.ID_PREF)
        self._imgind[CONFIG_PG] = self._imglst.Add(bmp)
        bmp = MakeThemeTool(ed_glob.ID_WEB)
        self._imgind[DOWNLOAD_PG] = self._imglst.Add(bmp)
        bmp = MakeThemeTool(ed_glob.ID_PACKAGE)
        self._imgind[INSTALL_PG] = self._imglst.Add(bmp)
        self._config = ConfigPanel(self)
        self._download = DownloadPanel(self)
        self._install = InstallPanel(self)
        self.SetImageList(self._imglst)

        # Add Pages
        self.AddPage(self._config, _("Configure"), 
                     imageId=self._imgind[CONFIG_PG])
        self.AddPage(self._download, _("Download"), 
                     imageId=self._imgind[DOWNLOAD_PG])
        self.AddPage(self._install, _("Install"), 
                     imageId=self._imgind[INSTALL_PG])
        self.SetSelection(CONFIG_PG)

        # Event handlers
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGING, self.OnPageChanging)

    def IsBusy(self):
        """Returns whether any of the operations in the
        notebook are busy such as downloads or installs.
        The return will be None if not busy and a message
        string if it is busy.
        @return: status of dialog
        @rtype: string or None
        """
        dl_pg = self.GetPage(DOWNLOAD_PG)
        if dl_pg and dl_pg.IsDownloading():
            return _("Downloads are incomplete")
        else:
            return None

    def OnPageChanging(self, evt):
        """Updates pages as they are being changed to.
        @param evt: Event fired that called this handler
        @type evt: wx.EVT_NOTEBOOK_PAGE_CHANGING

        """
        cur_pg = evt.GetSelection()
        parent = self.GetParent()
        parent.SetTitle(parent.GetTitle().split(" | ")[0] + \
                        " | " + self.GetPageText(cur_pg))
        if cur_pg == CONFIG_PG:
            self._config.PopulateCtrl()
            self.GetParent().SetStatusText(_("Changes will take affect once the"
                                             " program has been restarted"), 0)
        elif cur_pg == DOWNLOAD_PG:
            self._download.UpdateList()
        elif cur_pg == INSTALL_PG:
            pass
        else:
            pass

        evt.Skip()

class ConfigPanel(wx.Panel):
    """Creates a panel for configuring plugins."""
    def __init__(self, parent, id_=wx.ID_ANY, style=wx.NO_BORDER):
        """Build config panel"""
        wx.Panel.__init__(self, parent, id_, style=style)
        self._list = PluginListCtrl(self)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Layout Panel
        self._sizer.Add(wx.StaticText(self, wx.ID_ANY, 
                       _("To enable a plugin check the box next to its label")),
                        0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizer.Add(wx.Size(10, 10))
        self._sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(self._sizer)

        # Event handlers
        self.Bind(ed_event.EVT_NOTIFY, self.OnNotify)

    def GetItemIdentifier(self, name):
        """Gets the named item and returns its identifier. The
        identifier is the combination of the name and version 
        strings.
        @param name: name of item in list
        @type name: string
        @return: identifier for the named list item

        """
        identifer = None
        if self.HasItem(name):
            item_id = self._list.FindItem(0, name)
            ver = self._list.GetItem(item_id, self._list.VERSION_COL)
            identifer = (name, ver.GetText())
        return identifer

    def HasItem(self, name):
        """Checks if a given named plugin is the list of this panel.
        @param name: name of item to look for
        @type name: string
        @return: whether item is in list or not
        @rtype: bool
        """
        if self._list.FindItem(0, name) >= 0:
            return True
        else:
            return False

    def OnNotify(self, evt):
        """Handles the notification events that are
        posted from the list control.
        @param evt: Event fired that called this handler
        @type evt: ed_event.NotificationEvent

        """
        index = evt.GetId()
        pin = self._list.GetItemText(index)
        pmgr = wx.GetApp().GetPluginManager()
        if evt.GetValue():
            pmgr.EnablePlugin(pin)
        else:
            pmgr.DisablePlugin(pin)

    def PopulateCtrl(self):
        """Populates the list of plugins and sets the
        values of their states. Any successive calls to
        this function will clear the list and Repopulate it
        with current config values. Returns the number of
        items populated to the list
        @postcondition: list is popluated with all plugins that are
                        currently loaded and sets the checkmarks accordingly
        @return: number of items added to list

        """
        p_mgr = wx.GetApp().GetPluginManager()
        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        p_mgr = wx.GetApp().GetPluginManager()
        p_mgr.ReInit()
        for item in p_mgr.GetConfig():
            self._list.Freeze()
            mod = sys.modules.get(item)
            pin = PluginData()
            pin.SetName(item)
            try:
                pin.SetDescription(str(mod.__doc__))
            except (NameError, TypeError):
                pin.SetDescription(_("No Description Available"))
            try:
                pin.SetAuthor(str(mod.__author__))
            except (NameError, TypeError):
                pin.SetAuthor(_("Unknown"))
            try:
                pin.SetVersion(str(mod.__version__))
            except (NameError, TypeError):
                pin.SetVersion(_("Unknown"))

            self._list.InsertPluginItem(pin)
            self._list.Thaw()

        # Check Enabled Items
        for item in p_mgr.GetConfig():
            ind = self._list.FindItem(0, item)
            self._list.CheckItem(ind, p_mgr.GetConfig()[item])

        if self._list.GetItemCount():
            self._list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self._list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self._list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self._list.SetColumnWidth(3, wx.LIST_AUTOSIZE)
            self._list.SendSizeEvent()
        return self._list.GetItemCount()

class DownloadPanel(wx.Panel):
    """Creates a panel with controls for downloading plugins."""
    ID_DOWNLOAD = wx.NewId()
    EGG_PATTERN = re.compile(r"(?P<name>[^-]+)"
    r"( -(?P<ver>[^-]+) (-py(?P<pyver>[^-]+) (-(?P<plat>.+))? )? )?",
    re.VERBOSE | re.IGNORECASE
    ).match

    def __init__(self, parent, pid=wx.ID_ANY, style=wx.NO_BORDER):
        """Initializes the panel"""
        wx.Panel.__init__(self, parent, pid, style=style)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._p_list = dict()           # list of available plugins/meta
        self._dl_list = dict()          # List of download urls
        self._eggcount = 0              # Number of plugins to download
        self._eggbasket = dict()        # Basket of downloaded eggs
        self._list = PluginListCtrl(self)
        self._downlb = wx.Button(self, self.ID_DOWNLOAD, _("Download"))
        self._downlb.Disable()

        # Layout Panel
        self._sizer.Add(wx.StaticText(self, wx.ID_ANY,
                       _("Select the desired plugins and then Click Download")),
                        0, wx.ALIGN_CENTER)
        self._sizer.Add(self._list, 1, wx.EXPAND)
        self._sizer.Add(wx.Size(5, 5))
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self._downlb, 0, wx.ALIGN_RIGHT)
        bsizer.Add(wx.Size(5, 5))
        self._sizer.Add(bsizer, 0, wx.ALIGN_RIGHT)
        self._sizer.Add(wx.Size(5, 5))
        self.SetSizer(self._sizer)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(ed_event.EVT_NOTIFY, self.OnNotify)

    def _DownloadPlugin(self, *args):
        """Downloads the plugin at the given url.
        @note: *args is really a string that has been exploded
        @return: name, completed, egg data
        @rtype: tuple

        """
        url = "".join(args)
        egg = None
        try:
            h_file = urllib.urlopen(url)
            egg = h_file.read()
            h_file.close()
        except (IOError, OSError), msg:
            util.Log("[plugdlg][err] %s" % str(msg))
        finally:
            return (url.split("/")[-1], True, egg)

    # The obtained meta data must be served as a file that is formated
    # as follows. Each meta data item must be on a single line with
    # each set of meta data for different plugins separated by three
    # hash marks '###'.
    def _GetPluginListData(self, url=PLUGIN_REPO):
        """Gets the list of plugins and their related meta data
        as a string and returns it.
        @return: list of data of available plugins from website
        
        """
        text = u''
        try:
            h_file = urllib.urlopen(url)
            text = h_file.read()
            h_file.close()
        except (IOError, OSError), msg:
            util.Log("[plugdlg][err] %s" % str(msg))
        finally:
            return text.split("###")

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
                frame.SetStatusText(_("Finshed downloading plugins"), 0)
                wx.CallAfter(frame.Busy, False)
                inst_pg = self.GetParent().GetPage(INSTALL_PG)
                for key in self._eggbasket:
                    inst_pg.AddItemToInstall(key)
                self.GetParent().SetSelection(INSTALL_PG)

    def _UpdateCatcher(self, delayedResult):
        """Catches the results from the download worker threads"""
        frame = self.GetGrandParent()
        try:
            result = delayedResult.get()
            if len(result):
                self._p_list = self.FormatPluginList(result)
                self.PopulateList()
                frame.SetStatusText(_("Select plugins to download"), 0)
                wx.CallAfter(frame.Busy, False)
        except Exception, msg:
            frame.SetStatusText(_("Unable to retrieve plugin list"), 0)

    def FormatPluginList(self, data):
        """Formats a list of plugin data served by the server into
        PluginData objects for usage in the list view.
        @return: PluginData of all available plugins
        @rtype: dict

        """
        plugins = data
        p_list = dict()
        if len(plugins) < 2:
            return p_list

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

        # Remove items that have already been installed
        config_pg = self.GetParent().GetPage(CONFIG_PG)
        to_clean = list()
        for pin in p_list:
            ver = p_list[pin].GetVersion()
            pin_id = p_list[pin].GetName() + ver
            cfg_id = config_pg.GetItemIdentifier(pin.lower())
            if cfg_id is not None and cfg_id[1] >= ver:
                to_clean.append(pin)
        for item in to_clean:
            del p_list[item]
        return p_list

    def GetDownloadedData(self):
        """Returns the dictionary of downloaded data or an
        empty dictionary if no data has been downloaded.
        @return: set of all successfully downloaded plugins

        """
        return self._eggbasket

    def IsDownloading(self):
        """Returns whether the panel has active download
        threads or not.
        @return: status of downloading
        @rtype: boolean

        """
        if self._eggcount:
            return True
        else:
            return False

    def OnButton(self, evt):
        """Handles the Button Events.
        @param evt: Event that called this handler
        @type evt: wx.EVT_BUTTON

        """
        e_id = evt.GetId()
        if e_id == self.ID_DOWNLOAD:
            urls = list()
            for item in self._dl_list:
                if self._dl_list[item] and item in self._p_list:
                    urls.append(BASE_URL + self._p_list[item].GetUrl())
            self._eggcount = len(urls)
            
            # Start a separate thread to download each selection
            for egg in range(len(urls)):
                self.GetGrandParent().SetStatusText(_("Downloading") + "...", 0)
                self.GetGrandParent().Busy(True)
                delayedresult.startWorker(self._ResultCatcher, 
                                          self._DownloadPlugin,
                                          wargs = (urls[egg]), jobID = egg)
        else:
            evt.Skip()

    def OnNotify(self, evt):
        """Handles the notification events that are posted by the
        list control when items are checked.
        @param evt: Event that called this handler
        @type evt: ed_event.NotificationEvent

        """
        index = evt.GetId()
        flag = evt.GetValue()
        pin = self._list.GetItemText(index)
        if flag:
            self._downlb.Enable()
            self._dl_list[pin] = flag
        else:
            for item in self._dl_list:
                if self._dl_list[item]:
                    self._downlb.Enable()
                    break
            else:
                self._downlb.Disable()
            if self._dl_list.has_key(pin):
                del self._dl_list[pin]

    def PopulateList(self):
        """Populates the list control based off data in the plugin data
        list. The plugin data list is set as a result of calling UpdateList
        it is not recomended to call this directly.

        @return: number of items added to control

        """
        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        for item in self._p_list:
            self._list.Freeze()
            self._list.InsertPluginItem(self._p_list[item])
            self._list.Thaw()

        if self._list.GetItemCount():
            self._list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self._list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self._list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self._list.SetColumnWidth(3, wx.LIST_AUTOSIZE)
            self._list.SendSizeEvent()
        return self._list.GetItemCount()

    def RemoveDownloadedItem(self, item):
        """Remove an item from the download cache
        @param item: Name of item to remove

        """
        # Removed downloaded data
        if self._eggbasket.has_key(item):
            del self._eggbasket[item]

        # Remove download entry data
        match = self.EGG_PATTERN(item)
        if match:
            plugin_name = match.group('name').lower()
            if self._dl_list.has_key(plugin_name):
                del self._dl_list[plugin_name]

    def UpdateList(self, url=PLUGIN_REPO):
        """Update the list of available downloads
        @param url: url to fetch update list from
        @postcondition: Worker thread is started that will update list when it
                        finishes.

        """
        if self._list.GetItemCount():
            self._list.DeleteAllItems()
        frame =  self.GetGrandParent()
        frame.SetStatusText(_("Retrieving Plugin List") + "...", 0)
        frame.Busy(True)
        delayedresult.startWorker(self._UpdateCatcher,
                                  self._GetPluginListData,
                                  wkwargs={'url' : url}, jobID='update')

class InstallPanel(wx.Panel):
    """Creates a panel for installing plugins."""
    ID_INSTALL = wx.NewId()
    ID_USER = wx.NewId()
    ID_SYS = wx.NewId()
    ID_REMOVE_ITEM = wx.NewId()

    def __init__(self, parent, id_=wx.ID_ANY, style=wx.NO_BORDER):
        """Initializes the panel"""
        wx.Panel.__init__(self, parent, id_, style=style)

        # Attributes
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        lbl = wx.StaticText(self, wx.ID_ANY,
                            _("Click on Install to install the plugins "
                              "in the list"))
        toolt = wx.ToolTip(_("To add a new item drag and drop the plugin file "
                             "into the list.\n\nTo remove an item select it "
                             "and hit Delete or Backspace."))
        self._install = wx.ListBox(self, wx.ID_ANY, style=wx.LB_SORT)
        self._install.SetToolTip(toolt)
        self._install.SetDropTarget(util.DropTargetFT(self._install, 
                                                      None, self.OnDrop))
        self._instb = wx.Button(self, self.ID_INSTALL, _("Install"))
        self._instb.Disable()
        self._usercb = wx.CheckBox(self, self.ID_USER, _("User Directory"))
        self._usercb.SetValue(True)
        toolt = wx.ToolTip(_("Install the plugins only for the current user"))
        self._usercb.SetToolTip(toolt)
        self._syscb = wx.CheckBox(self, self.ID_SYS, _("System Directory"))
        toolt = wx.ToolTip(_("Install the plugins for all users\n"
                             " **requires administrative privileges**"))
        self._syscb.SetToolTip(toolt)
        if not os.access(ed_glob.CONFIG['SYS_PLUGIN_DIR'], os.R_OK | os.W_OK):
            self._syscb.Disable()

        # Layout Panel
        self._sizer.Add(lbl, 0, wx.ALIGN_CENTER)
        self._sizer.Add(self._install, 1, wx.EXPAND)
        self._sizer.Add(wx.Size(5, 5))
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(wx.Size(5, 5))
        bsizer.Add(self._usercb, 0, wx.ALIGN_LEFT)
        bsizer.Add(wx.Size(5, 5))
        bsizer.Add(self._syscb, 0, wx.ALIGN_LEFT)
        bsizer.AddStretchSpacer()
        bsizer.Add(self._instb, 0, wx.ALIGN_RIGHT)
        bsizer.Add(wx.Size(5, 5))
        self._sizer.Add(bsizer, 0, wx.EXPAND)
        self._sizer.Add(wx.Size(5, 5))
        self.SetSizer(self._sizer)
        self.SendSizeEvent()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckBox)
        self._install.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def _Install(self):
        """Install the plugins in the list.
        @postcondition: all plugins listed in the list are installed and loaded

        """
        items = self._install.GetItems()
        inst_loc = ed_glob.CONFIG['PLUGIN_DIR']
        if self._syscb.GetValue():
            inst_loc = ed_glob.CONFIG['SYS_PLUGIN_DIR']

        for item in items:
            egg_name = item.split("/")[-1]
            if os.path.isabs(item):
                try:
                    reader = file(item, "rb")
                    egg = reader.read()
                    reader.close()
                except (IOError, SystemError, OSError):
                    continue
            else:
                dl_pg = self.GetParent().GetPage(DOWNLOAD_PG)
                egg = dl_pg.GetDownloadedData().get(item, None)
                if not egg:
                    continue

            try:
                writer = file(inst_loc + egg_name, "wb")
                writer.write(egg)
                writer.close()
            except IOError:
                continue
            else:
                # If successfully installed remove from list
                ind = self._install.FindString(item)
                dl_pg = self.GetParent().GetPage(DOWNLOAD_PG)
                if ind != wx.NOT_FOUND:
                    self._install.Delete(ind)
                    dl_pg.RemoveDownloadedItem(item)

        if not len(self._install.GetItems()):
            # All plugins installed correctly
            grand_p = self.GetTopLevelParent()
            grand_p.SetStatusText(_("Successfully Installed Plugins"), 0)
            dlg = wx.MessageDialog(self, _("Go to configuration page?"),
                                   _("Finished Installing Plugins"), 
                                   style=wx.YES_NO | wx.CENTER | \
                                         wx.ICON_INFORMATION)
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_YES:
                self.GetParent().SetSelection(CONFIG_PG)
            self._instb.Disable()
        else:
            self.GetGrandParent().SetStatusText(_("Error"), 1)
            dlg = wx.MessageDialog(self, 
                                   _("Failed to install %d plugins") % \
                                   self._install.GetCount(),
                                   _("Installation Error"),
                                   style = wx.OK | wx.CENTER | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def AddItemToInstall(self, item):
        """Adds an item to the install list, the item
        should be a string of the path to the item or
        the items name if it is an in memory file from the
        download page.
        @param item: path or name of plugin item
        @type item: string

        """
        if self._install.FindString(item) == wx.NOT_FOUND:
            self._instb.Enable()
            self._install.Append(item)
        else:
            pass

    def OnButton(self, evt):
        """Handles button events generated by the panel.
        @param evt: Event that called this handler
        @type evt: wx.EVT_BUTTON

        """
        e_id = evt.GetId()
        if e_id == self.ID_INSTALL:
            self._Install()
        else:
            evt.Skip()

    def OnCheckBox(self, evt):
        """Handles the checkbox events to make sure that
        only one of the two check boxes is checked at a time
        @param evt: Event that called this handler
        @type evt: wx.EVT_CHECKBOX

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

    def OnDrop(self, files):
        """Get Drop files and place paths in control
        @status: should also check entry points in addition to filetype
        @param files: list of file paths
        @postcondtion: all non egg files are filtered only placing
                       the eggs in the list.
        """
        # Filter out any files that are not eggs
        good = list()
        for fname in files:
            if fname.split(u'.')[-1] == u'egg':
                good.append(fname)
        self._install.AppendItems(good)
        if self._install.GetCount():
            self._instb.Enable()

    def OnKeyUp(self, evt):
        """Key Event handler. Removes the selected item from
        the list control when the delete or backspace kis is pressed.
        @param evt: Event that called this handler
        @type evt: wx.KeyEvent(wx.EVT_KEY_UP)

        """
        if evt.GetKeyCode() in [wx.WXK_DELETE, wx.WXK_BACK]:
            item = self._install.GetSelection()
            if item != wx.NOT_FOUND:
                self._install.Delete(item)
        evt.Skip()

#--------------------------------------------------------------------------#

class PluginListCtrl(wx.ListCtrl, 
                     listmix.ListCtrlAutoWidthMixin,
                     listmix.CheckListCtrlMixin):
    """Creates a list control for displaying plugins and configuring them."""
    PLUGIN_COL   = 0
    DESCRIPT_COL = 1
    AUTHOR_COL   = 2
    VERSION_COL  = 3

    def __init__(self, parent):
        """Initializes the Profile List Control
        @param parent: parent window of this control

        """
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, wx.DefaultSize, 
                             style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_HRULES)

        self.InsertColumn(self.PLUGIN_COL, _("Plugin"))
        self.InsertColumn(self.DESCRIPT_COL, _("Description"))
        self.InsertColumn(self.AUTHOR_COL, _("Author"))
        self.InsertColumn(self.VERSION_COL, _("Version"))

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.CheckListCtrlMixin.__init__(self)

    def GetItemValues(self):
        """Returns a dictionary of item names mapped to check values,
        where the item name is the item at column zero and the
        dictionary contains all entries in the list.
        @return: mapping of items to check falues
        @rtype: dict string->bool

        """
        item_vals = dict()
        for item in range(self.GetItemCount()):
            pin = self.GetItemText(item)
            item_vals[pin] = self.IsChecked(item)
        return item_vals

    def OnCheckItem(self, index, flag):
        """Sends a custom notification event to the lists parent
        so that it can handle the check event if it needs to.
        @postcondition: checkbox is checked/unchecked and parent is notified

        """
        evt = ed_event.NotificationEvent(ed_event.edEVT_NOTIFY, 
                                         index, flag, self)
        wx.PostEvent(self.GetParent(), evt)
        listmix.CheckListCtrlMixin.OnCheckItem(self, index, flag)

    def InsertPluginItem(self, pi_data, check=False):
        """Does a smart add to the list that will insert the given
        a PluginData item alphabetically into the table based on
        the name value.
        @postcondition: plugin is inserted alphabetically into list

        """
        items = self.GetItemCount()
        names = list()
        for item in range(items):
            names.append(self.GetItem(item).GetText())
        before = u''
        for name in names:
            if pi_data.GetName() > name:
                before = name
                break
        if before not in names:
            index = 0
        else:
            index = names.index(before) - 1
        if index == -1:
            index = 0
        self.InsertStringItem(index, pi_data.GetName())
        self.SetStringItem(index, 1, pi_data.GetDescription())
        self.SetStringItem(index, 2, pi_data.GetAuthor())
        self.SetStringItem(index, 3, pi_data.GetVersion())
        self.CheckItem(index, check)

class PluginData(plugin.PluginData):
    """Plugin Metadata storage class used to store data
    about plugins and where to download them from
    @see: plugin.PluginData

    """
    def __init__(self, name=u'', descript=u'', author=u'', \
                 ver=u'', url=u''):
        plugin.PluginData.__init__(self, name, descript, author, ver)
        self._url = url

    def GetUrl(self):
        """Returns the URL of the plugin
        @return: url string of plugins location

        """
        return self._url

    def SetUrl(self, url):
        """Sets the url of the plugin.
        @param url: fully qualified url string

        """
        if not isinstance(url, basestring):
            try:
                url = str(url)
            except (TypeError, ValueError):
                url = u''
        self._url = url
