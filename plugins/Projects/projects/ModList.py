###############################################################################
# Name: ModList.py                                                            #
# Purpose: Enumerate modified, added, deleted files in a list                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008-2011 Cody Precord <staff@editra.org>                    #
# License: wxWindows License                                                  #
###############################################################################

"""
File Modification List

Display component for displaying file status for a repository and allowing for
checking, reverts, ect...

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ModList.py 1405 2011-06-05 18:29:32Z CodyPrecord $"
__revision__ = "$Revision: 1405 $"

#--------------------------------------------------------------------------#
# Imports
import os
import wx

# Local Imports
import FileIcons
import ConfigDialog
import ScCommand
import ProjCmnDlg
from HistWin import HistoryWindow

# Editra Imports
import ed_glob
from profiler import Profile_Get
import ed_msg
import eclib
import ed_basewin
import ed_thread

#--------------------------------------------------------------------------#
# Globals

# Menu Id's
ID_UPDATE              = wx.NewId()
ID_COMPARE_TO_PREVIOUS = wx.NewId()
ID_COMMIT              = wx.NewId()
ID_REVISION_HIST       = wx.NewId()

# Control Id's
ID_REPO_CHOICE = wx.NewId()

# Status Keys used by SourceControl modules
STATUS = { u'modified' : u'M',
           u'added'    : u'A',
           u'deleted'  : u'D',
           u'conflict' : u'C',
           u'unknown'  : u'?' }
           
_ = wx.GetTranslation

#--------------------------------------------------------------------------#

class RepoModBox(ed_basewin.EdBaseCtrlBox):
    """Repository modification list container window"""
    def __init__(self, parent):
        super(RepoModBox, self).__init__(parent)

        # Attributes
        self._list = RepoModList(self)
        self._config = ConfigDialog.ConfigData() # Singleton Config Obj
        self._crepo = 0
        self._ctrl = ScCommand.SourceController(self)
        self._repos = self.FindRepos(self._config['projects'].keys())
        self._repo_ch = None
        self._commit = None # Created in __DoLayout
        self._refresh = None
        self._update = None
        self._revert = None

        # Setup
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, lambda evt: self.DoCommit(), self._commit)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.DoUpdate(), self._update)
        self.Bind(wx.EVT_BUTTON,
                  lambda evt: self.DoStatusRefresh(), self._refresh)
        self.Bind(wx.EVT_BUTTON,
                  lambda evt: self.DoRevert(), self._revert)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, id=ID_REPO_CHOICE)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)
#        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

        # Handlers for projects messages sent over editra message bus
        ed_msg.Subscribe(self.OnProjectAdded, ConfigDialog.MSG_PROJ_ADDED)
        ed_msg.Subscribe(self.OnProjectRemoved, ConfigDialog.MSG_PROJ_REMOVED)

        # Do a refresh when first shown
        wx.CallLater(500, self.DoStatusRefresh)

    def OnDestroy(self, evt):
        """Destructor"""
        if self:
            ed_msg.Unsubscribe(self.OnProjectAdded)
            ed_msg.Unsubscribe(self.OnProjectRemoved)

    def __DoLayout(self):
        """Layout and setup the results screen ui"""
        ctrlbar = self.CreateControlBar(wx.TOP)

        # Repository
        labels = self._RefreshRepos()
        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("Repository") + u":"))
        self._repo_ch = wx.Choice(ctrlbar, ID_REPO_CHOICE, choices=labels)
        if len(self._repos):
            self._repo_ch.SetToolTipString(self._repos[0])
        ctrlbar.AddControl(self._repo_ch)

        ctrlbar.AddStretchSpacer()

        # Refresh Button
        self._refresh = self.AddPlateButton(_("Refresh"),
                                            FileIcons.getScStatusBitmap(),
                                            wx.ALIGN_RIGHT)
        # Update
        self._update = self.AddPlateButton(_("Update"),
                                           FileIcons.getScUpdateBitmap(),
                                           wx.ALIGN_RIGHT)
        # Commit
        self._commit = self.AddPlateButton(_("Commit"),
                                           FileIcons.getScCommitBitmap(),
                                           wx.ALIGN_RIGHT)
        # Clear Button
        self._revert = self.AddPlateButton(_("Revert"),
                                           FileIcons.getScRevertBitmap(),
                                           wx.ALIGN_RIGHT)
        self.SetWindow(self._list)

    def _RefreshRepos(self):
        """Refresh the list of repositories choices
        @note: updates self._repos
        @return: choice label list

        """
        projects = [(x, os.path.basename(x)) for x in self._repos]
        projects.sort(key=lambda x: x[1].lower())
        self._repos = [x[0] for x in projects]
        return [x[1] for x in projects]

    def DoCommit(self):
        """Commit the selected files"""
        self._list.CommitSelectedFiles()

    def DoRevert(self):
        """Revert the selected files"""
        self._list.RevertSelectedFiles()

    def DoStatusRefresh(self):
        """Refresh the status of the currently selected repository"""
        if len(self._repos) > self._crepo:
            path = self._repos[self._crepo]
            self._list.UpdatePathStatus(path)

    def DoUpdate(self):
        """Update the current repisitory"""
        if len(self._repos) > self._crepo:
            path = self._repos[self._crepo]
            self._list.UpdateRepository(path)

    def EnableCommandBar(self, enable=True):
        """Enable or disable the command bar
        @keyword enable: bool

        """
        ctrlb = self.GetControlBar()#.Enable(enable)
        # Workaround Enable not being overridable in by platebtn
        # NOTE: this is fixed in wx2.8.9.2+
        # TODO: Remove when some more wx releases are made
        for child in ctrlb.GetChildren():
            if hasattr(child, 'Enable'):
                child.Enable(enable)

    def FindRepos(self, path_list):
        """Find the top level source repositories under the given list
        of paths.
        @param path_list: list of strings
        @return: list

        """
        rlist = list()
        for path in path_list:
            # Only check existing paths and directories
            if not os.path.exists(path) or not os.path.isdir(path):
                continue

            scsys = self._ctrl.GetSCSystem(path)

            # If the top level project directory is not under source control
            # check the directories one level down to see if they are.
            if scsys is None:
                dirs = [ os.path.join(path, dname)
                         for dname in os.listdir(path)
                         if os.path.isdir(os.path.join(path, dname)) ]

                for dname in dirs:
                    if self._ctrl.GetSCSystem(dname) is not None:
                        rlist.append(dname)
            else:
                rlist.append(path)

        return list(set(rlist))

    def SetFileOpenerHook(self, meth):
        """Set the hook method for handling when items are activated in the
        list. The callable should accept a file path string as an argument.
        @param meth: callable

        """
        self._list.SetFileOpenerHook(meth)

    def OnChoice(self, evt):
        """Handle changes in selection of the current repo"""
        if evt.GetId() == ID_REPO_CHOICE:
            self._crepo = self._repo_ch.GetSelection()
            self._repo_ch.SetToolTipString(self._repos[self._crepo])
            self.DoStatusRefresh()
        else:
            evt.Skip()

    def OnProjectAdded(self, msg):
        """Project added notifier"""
        if self._repo_ch is not None:
            data = msg.GetData()
            repos = self.FindRepos([data[0],])
            if len(repos):
                for repo in repos:
                    if repo not in self._repos:
                        self._repos.append(repo)

                labels = self._RefreshRepos()
                csel = self._repo_ch.GetStringSelection()
                self._repo_ch.SetItems(labels)
                if csel in labels:
                    self._repo_ch.SetStringSelection(csel)
                else:
                    self._repo_ch.SetSelection(0)

            # Refresh the view
            wx.CallLater(250, self.DoStatusRefresh)

    def OnProjectRemoved(self, msg):
        """Project removed notifier"""
        if self._repo_ch is not None:
            data = msg.GetData()
            repo = data[0]

            for repo in data[0]:
                if repo in self._repos:
                    self._repos.remove(repo)

            # Update the choice list
            labels = self._RefreshRepos()
            csel = self._repo_ch.GetStringSelection()
            self._repo_ch.SetItems(labels)
            if csel in labels:
                self._repo_ch.SetStringSelection(csel)
            else:
                self._repo_ch.SetSelection(0)

            # Refresh the view
            wx.CallLater(250, self.DoStatusRefresh)

    def OnUpdateUI(self, evt):
        """Update UI of buttons based on state of list
        @param evt: wx.UpdateUIEvent
        @note: wish there was access to the wx.Window.Enable virtual method
               so that the overridden method would be called.

        """
        e_obj = evt.GetEventObject()
        if e_obj in (self._commit, self._revert):
            evt.Enable(self._list.GetSelectedItemCount())
        elif evt.Id == ID_REPO_CHOICE:
            evt.Enable(self._repo_ch.GetCount())
        elif e_obj is self._refresh:
            evt.Enable(len(self._repo_ch.GetStringSelection()))
        else:
            evt.Skip()

#--------------------------------------------------------------------------#

class RepoModList(eclib.EBaseListCtrl):
    """List for managing and listing files under SourceControl.
    Specifically it displays the summary of modified files under a given
    repository.

    """
    STATUS_COL = 0
    FILENAME_COL = 1
    def __init__(self, parent, id=wx.ID_ANY):
        """Create the list control"""
        super(RepoModList, self).__init__(parent, id, style=wx.LC_REPORT|wx.LC_VRULES|wx.BORDER)

        # Attributes
        self._menu = None
        self._items = list()
        self._path = None
        self._busy = False
        self._ctrl = ScCommand.SourceController(self)
        
        # Interface attributes
        self.fileHook = None

        # Setup
        font = Profile_Get('FONT3', 'font', wx.NORMAL_FONT)
        self.SetFont(font)
        self.InsertColumn(RepoModList.STATUS_COL, _("Status"),
                          wx.LIST_FORMAT_CENTER)
        self.InsertColumn(RepoModList.FILENAME_COL, _("Filename"))

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(ScCommand.EVT_STATUS, self.OnStatus)
        self.Bind(ScCommand.EVT_CMD_COMPLETE, self.OnCommandComplete)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)

        # Editra Message Handlers
        ed_msg.Subscribe(self.OnUpdateFont, ed_msg.EDMSG_DSP_FONT)

    def OnDestroy(self, evt):
        if self and evt.GetEventObject() is self:
            ed_msg.Unsubscribe(self.OnUpdateFont)

    def __ConstructNodes(self):
        """Make the node's list from the selected list items
        @return: list of tuples

        """
        paths = self.GetSelectedPaths()
        nodes = [(None, {'path' : path}) for path in paths]
        return nodes

    def AddFile(self, status, fname):
        """Add a file to the list
        @param status: Status indicator
        @param fname: File name

        """
        self._items.append(dict(status=status, fname=fname))
        self.Append((status, fname))

    def DeleteAllItems(self):
        """Clear the list"""
        for item in range(len(self._items)):
            self._items.pop()
        wx.ListCtrl.DeleteAllItems(self)

    def DoDiff(self):
        """Open the diff between the selected file and its previous version."""
        paths = self.GetSelectedPaths()

        for path in paths:
            # Only do files
            if os.path.isdir(path):
                # TODO: prompt that this cant be done?
                continue

            # Run the actual Diff job
            self._ctrl.CompareRevisions(path)

    def CommitSelectedFiles(self):
        """Commit the selected files"""
        paths = self.GetSelectedPaths()
        if not len(paths):
            return

        nodes = self.__ConstructNodes()
        message = u""

        # Make sure a commit message is entered
        while True:
            parent = self.GetTopLevelParent()
            ted = ProjCmnDlg.CommitDialog(parent, _("Commit Dialog"),
                                          _("Enter your commit message:"),
                                          paths)

            if ted.ShowModal() == wx.ID_OK:
                message = ted.GetValue().strip()
            else:
                return

            ted.Destroy()
            if message:
                break

        self.SetCommandRunning(True)
        self._ctrl.ScCommand(nodes, 'commit', None, message=message)

    def GetSelectedPaths(self):
        """Get the paths of the selected items
        @return: list of strings

        """
        items = list()
        idx = -1
        while True:
            item = self.GetNextItem(idx, state=wx.LIST_STATE_SELECTED)
            if item == wx.NOT_FOUND:
                break
            else:
                items.append(item)
                idx = item

        paths = list()
        for idx in items:
            item = self.GetItem(idx, RepoModList.FILENAME_COL)
            path = item.GetText()
            if path:
                paths.append(path)

        return paths

    def RefreshStatus(self):
        """Refresh the screen with the latest status info from the
        current repository.
        @postcondition: status of current files in repository is refreshed and
                        displayed in the list.

        """
        self.DeleteAllItems()
        if self._path is not None:
            self.UpdatePathStatus(self._path)

    def RevertSelectedFiles(self):
        """Revert the selected files
        @postcondition: selected items in the list are reverted to the
                        repository version.

        """
        nodes = self.__ConstructNodes()
        if not len(nodes):
            return

        self.SetCommandRunning(True)
        self._ctrl.ScCommand(nodes, 'revert')

    def SetCommandRunning(self, running=True):
        """Set whether a commadn is running or not
        @keyword running: bool

        """
        self._busy = running
        self.GetParent().EnableCommandBar(not running)
        fid = self.GetTopLevelParent().GetId()
        if running:
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (fid, True))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (fid, -1, -1))
        else:
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (fid, False))

    def SetFileOpenerHook(self, meth):
        """Set the file opener method hook.
        @param meth: callable (def fhook(path))

        """
        if not callable(meth):
            raise ValueError("meth must be callable")

        self.fileHook = meth

    def ShowRevisionHistory(self):
        """Show the revision history for the selected files
        @postcondition: History dialog is shown for each selected file

        """
        paths = self.GetSelectedPaths()
        pos = wx.DefaultPosition
        win = None

        for path in paths:
            if win is not None:
                pos = win.GetPosition()
                pos = (pos[0] + 22, pos[1] + 22)

            # Log lookup and ScCommands are handled by HistoryWindow
            win = HistoryWindow(self, path, None, dict(path=path))
            win.Show()
            if pos != wx.DefaultPosition:
                win.SetPosition(pos)

    def UpdatePathStatus(self, path):
        """Run an status update job
        @param path: path to check status on

        """
        self.SetCommandRunning(True)
        src_c = self._ctrl.GetSCSystem(path)
        if src_c is not None:
            self._path = path
            ed_thread.EdThreadPool().QueueJob(self._ctrl.StatusWithTimeout,
                                              src_c, None, dict(path=path),
                                              dict(recursive=True))

    def UpdateRepository(self, path):
        """Update the repository
        @param path: repository path

        """
        self.SetCommandRunning(True)
        self._ctrl.ScCommand([(None, {'path' : path})], 'update')

    #---- Event Handlers ----#

    def OnActivated(self, evt):
        """Open the file in the editor when it is activated in the list"""
        if self.fileHook is not None:
            for path in self.GetSelectedPaths():
                self.fileHook(path)
        else:
            evt.Skip()

    def OnCommandComplete(self, evt):
        """Handle when a source control command has completed."""
        self.RefreshStatus()
        self.SetCommandRunning(False)

    def OnContextMenu(self, evt):
        """Show the context menu"""
        if not self.GetSelectedItemCount() or self._busy:
            evt.Skip()
            return

        if self._menu is None:
            # Create the menu once
            self._menu = wx.Menu()
            item = self._menu.Append(wx.ID_REFRESH, _("Refresh status"))
            item.SetBitmap(FileIcons.getScStatusBitmap())
            self._menu.AppendSeparator()
            item = self._menu.Append(ID_COMPARE_TO_PREVIOUS,
                                     _("Compare to previous version"))
            item.SetBitmap(FileIcons.getScDiffBitmap())
            item = self._menu.Append(ID_REVISION_HIST,
                                     _("Show revision history"))
            item.SetBitmap(FileIcons.getScHistoryBitmap())
            self._menu.AppendSeparator()
            item = self._menu.Append(ID_COMMIT, _("Commit changes"))
            item.SetBitmap(FileIcons.getScCommitBitmap())
            self._menu.AppendSeparator()
            item = self._menu.Append(wx.ID_REVERT,
                                     _("Revert to repository version"))
            item.SetBitmap(FileIcons.getScRevertBitmap())

        self.PopupMenu(self._menu)

    def OnMenu(self, evt):
        """Handler for menu events from context menu"""
        e_id = evt.GetId()
        if e_id == ID_COMPARE_TO_PREVIOUS:
            # Do Diff
            self.DoDiff()
        elif e_id == ID_COMMIT:
            # Checkin
            self.CommitSelectedFiles()
        elif e_id == wx.ID_REVERT:
            # Revert changes
            self.RevertSelectedFiles()
        elif e_id == ID_REVISION_HIST:
            # Show the history of the selected file
            self.ShowRevisionHistory()
        elif e_id == wx.ID_REFRESH:
            # Refresh the status
            self.RefreshStatus()
        else:
            evt.Skip()

    def OnStatus(self, evt):
        """Handler for the status command event. Updates the list with
        the status of the files from the selected repository.

        """
        status = evt.Value[1:]

        path = None
        if len(status):
            path = status[0].get('path', None)
            status = status[1]

        if path is None:
            # TODO: notify that the status check failed?
            return

        # Clear the display
        self.DeleteAllItems()

        # Get the interesting items from the update dict
        modlst = list()
        for fname, stat in status.iteritems():
            fstatus = stat.get('status', 'uptodate')
            if fstatus != 'uptodate':
                modlst.append((STATUS.get(fstatus, u'U'),
                               os.path.join(path, fname)))

        # Sort the list
        modlst.sort(key=lambda x: x[1])

        # Update the display
        for stat, fname in modlst:
            self.AddFile(stat, fname)

        self.SetCommandRunning(False)

    def OnUpdateFont(self, msg):
        """Update the ui font when changed."""
        font = msg.GetData()
        if isinstance(font, wx.Font) and not font.IsNull():
            self.SetFont(font)
