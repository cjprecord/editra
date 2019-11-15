###############################################################################
# Name: ftpwindow.py                                                          #
# Purpose: Ftp Window                                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Ftp Window"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ftpwindow.py 1223 2011-04-06 15:20:53Z CodyPrecord $"
__revision__ = "$Revision: 1223 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx
import wx.lib.mixins.listctrl as listmix

# Editra Libraries
import ed_glob
import ed_msg
from profiler import Profile_Get, Profile_Set
import util
import eclib
import ed_basewin

# Local Imports
import IconFile
import ftpconfig
import ftpclient
import ftpfile

#-----------------------------------------------------------------------------#
# Globals
CONFIG_KEY = u"FtpEdit.Sites"
ID_SITES = wx.NewId()

# Context Menu
ID_REFRESH = wx.NewId()
ID_EDIT = wx.NewId()
ID_RENAME = wx.NewId()
ID_DELETE = wx.NewId()
ID_NEW_FILE = wx.NewId()
ID_NEW_FOLDER = wx.NewId()
ID_COPY_URL = wx.NewId()
ID_DOWNLOAD = wx.NewId()
ID_UPLOAD = wx.NewId()

MENU_IDS = [ ID_REFRESH, ID_EDIT, ID_RENAME, ID_DELETE, ID_NEW_FILE,
             ID_NEW_FOLDER, ID_COPY_URL, ID_DOWNLOAD, ID_UPLOAD ]

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class FtpWindow(ed_basewin.EdBaseCtrlBox):
    """Ftp file window"""
    def __init__(self, parent, id_=wx.ID_ANY):
        super(FtpWindow, self).__init__(parent, id_)

        # Attributes
        self._mw = ed_basewin.FindMainWindow(self)
        self._config = ftpconfig.ConfigData
        self._config.SetData(Profile_Get(CONFIG_KEY, default=dict()))
        self._connected = False
        self._client = ftpclient.FtpClient(self)
        self._files = list()
        self._select = None
        self._open = list()   # Open ftpfile objects

        # Ui controls
        self._cbar = None     # ControlBar
        self._list = None     # FtpList
        self._sites = None    # wx.Choice
        self.prefbtn = None
        self._username = None # wx.TextCtrl
        self._password = None # wx.TextCtrl

        # Layout
        self.__DoLayout()
        self.EnableControls(bool(self._config.GetCount()))
        self.RefreshControlBar()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.prefbtn)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.cbtn)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, id=ID_SITES)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(ftpclient.EVT_FTP_REFRESH, self.OnRefresh)
        self.Bind(ftpclient.EVT_FTP_DOWNLOAD, self.OnDownload)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)

        # Editra Message Handlers
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        ed_msg.Subscribe(self.OnCfgUpdated, ftpconfig.EDMSG_FTPCFG_UPDATED)

    def OnDestroy(self, event):
        """Cleanup"""
        if self:
            ed_msg.Unsubscribe(self.OnThemeChanged)
            ed_msg.Unsubscribe(self.OnCfgUpdated)

        # Cleanup file notifiers
#        self.__DisconnectFiles()

    def __DisconnectFiles(self):
        """Disconnect opened files"""
        for fobj in self._open:
            try:
                fobj[1].ClearFtpStatus()
            except:
                pass

    def __DoLayout(self):
        """Layout the window"""
        self._cbar = self.CreateControlBar(wx.TOP)

        # Preferences
        self.prefbtn = self.AddPlateButton(u"", ed_glob.ID_PREF, wx.ALIGN_LEFT)
        btn.SetToolTipString(_("Configuration"))

        # Sites
        self._cbar.AddControl(wx.StaticText(self._cbar, label=_("Sites:")), wx.ALIGN_LEFT)
        self._sites = wx.Choice(self._cbar, ID_SITES)
        self._cbar.AddControl(self._sites, wx.ALIGN_LEFT)

        # Username
        self._cbar.AddControl(wx.StaticText(self._cbar, label=_("Username:")), wx.ALIGN_LEFT)
        self._username = wx.TextCtrl(self._cbar)
        self._cbar.AddControl(self._username, wx.ALIGN_LEFT)

        # Password
        self._cbar.AddControl(wx.StaticText(self._cbar, label=_("Password:")), wx.ALIGN_LEFT)
        self._password = wx.TextCtrl(self._cbar, style=wx.TE_PASSWORD)
        self._cbar.AddControl(self._password, wx.ALIGN_LEFT)

        # Connect
        self._cbar.AddStretchSpacer()
        bmp = IconFile.Connect.GetBitmap()
        self.cbtn = self.AddPlateButton(_("Connect"), bmp, wx.ALIGN_RIGHT)

        # Setup Window
        self._list = FtpList(self, wx.ID_ANY)
        self.SetWindow(self._list)

    def _HandleDisconnect(self):
        """Handle having to disconnect from the server"""
        self._connected = False
        self.cbtn.SetLabel(_("Connect"))
        self.cbtn.SetBitmap(IconFile.Connect.GetBitmap())
        self._list.DeleteAllItems()
#        self.__DisconnectFiles()
        self.EnableOptions(True)

        # Need to create a new client
        tmp = self._client.Clone()
        del self._client
        self._client = tmp

    def _StartBusy(self, busy=True):
        """Start/Stop the main windows busy indicator
        @keyword busy: bool

        """
        pid = self._mw.GetId()
        if busy:
            # Pulse
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (pid, True))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (pid, -1, -1))
        else:
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (pid, 0, 0))

        self._list.Enable(not busy)

    def EnableControls(self, enable=True):
        """Enable or disable controls in the control bar
        @keyword enable: bool

        """
        for child in self._cbar.GetChildren():
            if child.GetId() != wx.ID_PREFERENCES:
                child.Enable(enable)

    def EnableOptions(self, enable=True):
        """Enable or disable the options controls while connecting/disconnecting
        from the server.
        @param enable: bool

        """
        for child in self._cbar.GetChildren():
            if child is not self.cbtn:
                child.Enable(enable)

    def NotifyFtpFileDeleted(self, name):
        """Callback from FtpFile's owned by this client.
        @param name: name of file deleted

        """
        # Remove the file object from our watch
        for idx, finfo in enumerate(list(self._open)):
            if finfo[0] == name:
                self._open.pop(idx)
                break

    def OnButton(self, evt):
        """Handle Button click events"""
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_obj is self.cbtn:
            if self._connected:
                # Warn if any ftp files are open
#                num = len(self._open)
#                if num:
#                    # TODO: use custom dialog with list of files in it
#                    result = wx.MessageBox(_("There are currently %d ftp files open.\n"
#                                             "If you disconnect now you will be unable to upload any further changes to these files.\n"
#                                             "Disconnect from site?") % num,
#                                           _("Disconnect from Site?"),
#                                           style=wx.YES_NO|wx.CENTER|wx.ICON_WARNING)
#                    if result == wx.NO:
#                        return

                # Disconnect from server
                result = self._client.Disconnect()
                if not result:
                    err = self._client.GetLastError()
                    wx.MessageBox(_("Error on disconnect:\nError:\n%s") % err,
                                  _("Ftp Error"),
                                  style=wx.OK|wx.CENTER|wx.ICON_ERROR)
                    self._client.ClearLastError()

                self._HandleDisconnect()
            else:
                # Connect to site
                user = self._username.GetValue().strip()
                password = self._password.GetValue().strip()
                site = self._sites.GetStringSelection()

                url = self._config.GetSiteHostname(site)
                port = self._config.GetSitePort(site)
                self._client.SetDefaultPath(self._config.GetSitePath(site))
                self._client.SetHostname(url)
                self._client.SetPort(port)
                connected = self._client.Connect(user, password)
                if not connected:
                    wx.MessageBox(unicode(self._client.GetLastError()),
                                  _("Ftp Connection Error"),
                                  style=wx.OK|wx.CENTER|wx.ICON_ERROR)
                    self._client.ClearLastError()
                else:
                    self._connected = True
                    self.cbtn.SetLabel(_("Disconnect"))
                    self.cbtn.SetBitmap(IconFile.Disconnect.GetBitmap())

                    self.RefreshFiles()
                    self.EnableOptions(False)

            self._cbar.Layout()
        elif e_id == wx.ID_PREFERENCES:
            # Show preferences dialog
            app = wx.GetApp()
            win = app.GetWindowInstance(ftpconfig.FtpConfigDialog)
            if win is None:
                config = ftpconfig.FtpConfigDialog(self._mw,
                                                   _("Ftp Configuration"))
                config.CentreOnParent()
                config.Show()
            else:
                win.Raise()
        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handle Choice Control Events"""
        if evt.GetId() == ID_SITES:
            # Change the current Site
            site = self._sites.GetStringSelection()
            password = self._config.GetSitePassword(site)
            user = self._config.GetSiteUsername(site)
            self._username.SetValue(user)
            self._password.SetValue(password)
        else:
            evt.Skip()

    def OnCfgUpdated(self, msg):
        """Update state of control bar when configuration data is updated
        @param msg: ftpconfig.EDMSG_FTPCFG_UPDATED

        """
        # Refresh persistent state
        Profile_Set(CONFIG_KEY, ftpconfig.ConfigData.GetData())

        # Update view for new data
        # XXX: got an odd assertion error about an incorrect dc once
        #      not sure how it could happen other then if the windows was
        #      being deleted when this was called.
        if not self.IsBeingDeleted():
            try:
                self.RefreshControlBar()
            except wx.PyAssertionError:
                pass

    def OnDownload(self, evt):
        """File download has completed
        @param evt: ftpclient.EVT_FTP_DOWNLOAD

        """
        ftppath, path = evt.GetValue()
        self._StartBusy(False)

        if path is None or not os.path.exists(path):
            err = self._client.GetLastError()
            if err is not None:
                err = unicode(err)
            else:
                err = _("Unknown")
            wx.MessageBox(_("Failed to download %(file)s\nError:\n%(err)s") % \
                          dict(file=ftppath, err=err),
                          _("Ftp Download Failed"),
                          style=wx.OK|wx.CENTER|wx.ICON_ERROR)
            self._client.ClearLastError()
        else:
            # Open the downloaded file in the editor
            csel = self._sites.GetStringSelection()
            data = self._config.GetSiteData(csel)
            data['user'] = self._username.GetValue().strip()
            data['pword'] = self._password.GetValue().strip()
            nb = self._mw.GetNotebook()
            fobj = ftpfile.FtpFile(self._client, ftppath, data, path)
            nb.OpenFileObject(fobj)
            self._open.append((path, fobj))
            fobj.SetDisconnectNotifier(self.NotifyFtpFileDeleted)

    def OnItemActivated(self, evt):
        """Handle when items are activated in the list control
        @param evt: wx.EVT_LIST_ITEM_ACTIVATED

        """
        idx = evt.GetIndex()
        if idx < len(self._files):
            item = self._files[idx]
            path = item['name']
            if item['isdir']:
                # Change directory
                self._StartBusy(True)
                self._client.ChangeDirAsync(path)
            else:
                # Retrieve the file
                self.OpenFile(path)

    def OnMenu(self, evt):
        """Handle menu events"""
        e_id = evt.GetId()
        sel = self._list.GetFirstSelected()
        path = None
        item = None
        if sel > -1 and sel < len(self._files):
            item = self._files[sel]
            path = item['name']

        if e_id == ID_EDIT:
            # Open the selected file in the editor
            if path is not None:
                self.OpenFile(path)

        elif e_id == ID_RENAME:
            # Rename the selected file
            if path is not None:
                name = wx.GetTextFromUser(_("Enter the new name"),
                                          _("Rename File"))
                if len(name):
                    self._select = name
                    self._StartBusy(True)
                    self._client.RenameAsync(path, name)

        elif e_id == ID_DELETE:
            # Remove the selected path
            # TODO: add support for removing directories
            if path is not None:
                result = wx.MessageBox(_("Are you sure you want to delete %s?") % path,
                                       _("Delete File?"),
                                       style=wx.YES_NO|wx.CENTER|wx.ICON_WARNING)

                if result == wx.YES:
                    self._client.DeleteFileAsync(path)

        elif e_id == ID_REFRESH:
            # Refresh the file list
            self._select = path
            self.RefreshFiles()

        elif e_id in (ID_NEW_FILE, ID_NEW_FOLDER):
#            if item is not None:
                # TODO: change to create the new file/folder in the subdirectory
                #       when the selected item is a directory.
#                if item['isdir']:
#                    pass
#                else:
#                    pass

            # Prompt for the new name
            if e_id == ID_NEW_FILE:
                name = wx.GetTextFromUser(_("Enter name for new file."),
                                          _("New File"))

                # Check if the file already exists
                found = self._list.FindItem(-1, name)
                if found == wx.NOT_FOUND and len(name):
                    self._select = name
                    self._client.NewFileAsync(name)
            else:
                name = wx.GetTextFromUser(_("Enter name for new directory."),
                                          _("New Directory"))

                # Check if the file already exists
                found = self._list.FindItem(-1, name)
                if found == wx.NOT_FOUND and len(name):
                    self._select = name
                    self._client.NewDirAsync(name)

            if found != wx.NOT_FOUND and len(name):
                wx.MessageBox(_("%s already exists. Please enter a different name." % name),
                              _("%s already exists" % name),
                              style=wx.OK|wx.CENTER|wx.ICON_WARNING)

        elif e_id == ID_COPY_URL:
            # Copy the url of the selected file to the clipboard
            url = u"/".join([u"ftp:/", self._client.GetHostname().lstrip(u"/"),
                             self._client.GetCurrentDirectory().lstrip(u"/"),
                             path.lstrip(u"/")])
            util.SetClipboardText(url)

        # TODO: add general upload and download functionality
        elif e_id == ID_DOWNLOAD:
            pass

        elif e_id == ID_UPLOAD:
            pass

        else:
            evt.Skip()

    def OnRefresh(self, evt):
        """Update the file list when a refresh event is sent by our
        ftp client.
        @param evt: ftpclient.EVT_FTP_REFRESH

        """
        # Only update the list if the event came from an object of the same
        # directory. The directory could be different if the event came
        # from a clone of our client.
        cwd = self._client.GetCurrentDirectory()
        ecwd = evt.GetDirectory()
        if cwd != ecwd:
            self._StartBusy(False)
            return

        # No selection was set so see if one is there now
        if self._select is None:
            sel = self._list.GetFirstSelected()
            path = None
            item = None
            if sel > -1 and sel < len(self._files):
                item = self._files[sel]
                path = item['name']
            self._select = path

        if self._list.GetItemCount():
            self._list.DeleteAllItems()

        # Check for errors
        err = self._client.GetLastError()
        if err is not None:
            wx.MessageBox(_("Error: %s") % err, _("Ftp Error"),
                          style=wx.OK|wx.CENTER|wx.ICON_ERROR)
            self._client.ClearLastError()
            self._StartBusy(False)
            self._client.Disconnect()
            self._HandleDisconnect()
            return

        # Refresh the file list
        self._files = evt.GetValue()
        for item in self._files:
            self._list.AddItem(item)

        self._StartBusy(False)

        # Try to reset the previous selection if there was one
        if self._select is not None:
            index = self._list.FindItem(-1, self._select)
            self._select = None
            if index != wx.NOT_FOUND:
                self._list.EnsureVisible(index)
                self._list.SetItemState(index,
                                        wx.LIST_STATE_SELECTED,
                                        wx.LIST_MASK_STATE)

    def OnThemeChanged(self, msg):
        """Update icons when the theme changes
        @param msg: ed_msg.EDMSG_THEME_CHANGED

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
        pref = self._cbar.FindWindowById(wx.ID_PREFERENCES)
        pref.SetBitmap(bmp)
        self._cbar.Layout()

    def OpenFile(self, path):
        """Open a file from the connected ftp site
        @param path: file name

        """
        ed_msg.PostMessage(ed_msg.EDMSG_UI_SB_TXT,
                                   (ed_glob.SB_INFO,
                                   _("Retrieving file") + u"..."))
        self._StartBusy(True)
        self._client.DownloadAsync(path)

    def RefreshControlBar(self):
        """Refresh the status of the control bar"""
        csel = self._sites.GetStringSelection()
        sites = self._config.GetSites()
        self._sites.SetItems(sites)
        if csel in sites:
            self._sites.SetStringSelection(csel)
        elif len(sites):
            self._sites.SetSelection(0)

        csel = self._sites.GetStringSelection()
        data = self._config.GetSiteData(csel)
        self._username.SetValue(self._config.GetSiteUsername(csel))
        self._password.SetValue(self._config.GetSitePassword(csel))
        self._cbar.Layout()
        self.EnableControls(len(sites))

    def RefreshFiles(self):
        """Refresh the current view"""
        self._StartBusy(True)
        self._client.RefreshPath()

#-----------------------------------------------------------------------------#

class FtpList(listmix.ListCtrlAutoWidthMixin,
              eclib.ListRowHighlighter,
              wx.ListCtrl):
    """Ftp File List
    Displays the list of files in the currently connected ftp site.

    """
    def __init__(self, parent, id_=wx.ID_ANY):
        wx.ListCtrl.__init__(self, parent, id_,
                             style=wx.LC_REPORT|wx.LC_SINGLE_SEL) 
        eclib.ListRowHighlighter.__init__(self)

        # Attributes
        self._il = wx.ImageList(16, 16)
        self._idx = dict()
        self._menu = None

        # Setup
        font = Profile_Get('FONT3', 'font', wx.NORMAL_FONT)
        self.SetFont(font)
        self.SetupImageList()
        self.InsertColumn(0, _("Filename"))
        self.InsertColumn(1, _("Size"))
        self.InsertColumn(2, _("Modified"))

        # Setup autowidth
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(1) # <- NOTE: autowidth mixin starts from index 1

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)

        # Message Handlers
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        ed_msg.Subscribe(self.OnUpdateFont, ed_msg.EDMSG_DSP_FONT)

    def OnDestroy(self, evt):
        """Unsubscribe from messages"""
        if self:
            ed_msg.Unsubscribe(self.OnThemeChanged)
            ed_msg.Unsubscribe(self.OnUpdateFont)
            if self._menu:
                self._menu.Destroy()

    def AddItem(self, item):
        """Add an item to the list
        @param item: dict(isdir, name, size, date)

        """
        self.Append((item['name'], item['size'], item['date']))
        if item['isdir']:
            img = self._idx['folder']
        else:
            img = self._idx['file']
        self.SetItemImage(self.GetItemCount() - 1, img)
        self.resizeLastColumn(self.GetTextExtent(u"Dec 31 24:00:00")[0] + 5)

    def OnContextMenu(self, evt):
        """Show the context menu"""
        if not self.GetSelectedItemCount():
            evt.Skip()
            return

        if self._menu is None:
            # Lazy init menu
            self._menu = wx.Menu()
            item = self._menu.Append(ID_REFRESH, _("Refresh"))
            bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_REFRESH), wx.ART_MENU)
            if not bmp.IsNull():
                item.SetBitmap(bmp)
            self._menu.AppendSeparator()
            self._menu.Append(ID_EDIT, _("Edit"))
            self._menu.Append(ID_RENAME, _("Rename") + u"...")
            item = self._menu.Append(ID_DELETE, _("Delete"))
            bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU)
            if not bmp.IsNull():
                item.SetBitmap(bmp)
            self._menu.AppendSeparator()
            item = self._menu.Append(ID_NEW_FILE, _("New File") + u"...")
            bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_NEW), wx.ART_MENU)
            if not bmp.IsNull():
                item.SetBitmap(bmp)
            item = self._menu.Append(ID_NEW_FOLDER, _("New Folder") + u"...")
            bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU)
            if not bmp.IsNull():
                item.SetBitmap(bmp)
            self._menu.AppendSeparator()
            self._menu.Append(ID_COPY_URL, _("Copy URL"))
#   TODO: Add in Version 0.3
#            self._menu.AppendSeparator()
#            self._menu.Append(ID_DOWNLOAD, _("Download") + u"...")
#            self._menu.Append(ID_UPLOAD, _("Upload") + u"...")

        # Update the menu state for the current selection
        self.UpdateMenuState()
        self.PopupMenu(self._menu)

    def OnThemeChanged(self, msg):
        """Update image list
        @param msg: ed_msg.EDMSG_THEME_CHANGED

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU)
        self._il.Replace(self._idx['folder'], bmp)

        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU)
        self._il.Replace(self._idx['file'], bmp)

        self.Refresh()

    def OnUpdateFont(self, msg):
        """Update the ui font when changed."""
        font = msg.GetData()
        if isinstance(font, wx.Font) and not font.IsNull():
            self.SetFont(font)

    def SetupImageList(self):
        """Setup the image list"""
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU)
        self._idx['folder'] = self._il.Add(bmp)

        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU)
        self._idx['file'] = self._il.Add(bmp)

        self.SetImageList(self._il, wx.IMAGE_LIST_SMALL)

    def UpdateMenuState(self):
        """Update the current state of the context menu"""
        if self._menu is not None:
            idx = self.GetFirstSelected()
            item = None
            isdir = False
            if idx != wx.NOT_FOUND:
                item = self.GetItem(idx)
                isdir = item.GetImage() == self._idx['folder']

            for id_ in (ID_EDIT, ID_DELETE): # ID_DOWNLOAD
                mitem = self._menu.FindItemById(id_)
                mitem.Enable(item and not isdir)

            if item is not None:
                lbl = item.GetText()
                mitem = self._menu.FindItemById(ID_RENAME)
                if isdir and lbl == u"..":
                    mitem.Enable(False)
                else:
                    mitem.Enable(True)
