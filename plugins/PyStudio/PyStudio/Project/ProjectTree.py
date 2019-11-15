###############################################################################
# Name: ProjectTree.py                                                        #
# Purpose: Project File Tree                                                  #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Project Tree

Shows the project file view

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ProjectTree.py 1546 2012-07-29 18:35:50Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1546 $"

#-----------------------------------------------------------------------------#
# Dependencies
import os
import fnmatch
import wx

# Editra imports
import ed_glob
import util
import eclib
import ebmlib
import ed_msg
import ed_basewin

# Local Imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.Messages import PyStudioMessages
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Controller.FileController import FileController
import PyStudio.Project.ProjectUtil as ProjectUtil

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ProjectTree(ed_basewin.EDBaseFileTree):
    """Provides a tree view of all the files and packages in a project."""
    # Context Menu Ids
    ID_EDIT_FILE   = wx.NewId()
    ID_OPEN_FILE   = wx.NewId()
    ID_REVEL_FILE  = wx.NewId()
    ID_NEW_SUBMENU = wx.NewId()
    ID_NEW_FILE    = wx.NewId()
    ID_NEW_FOLDER  = wx.NewId()
    ID_NEW_PACKAGE = wx.NewId()
    ID_PROPERTIES  = wx.NewId()
    ID_RENAME_FILE = wx.NewId()

    def __init__(self, parent):
        super(ProjectTree, self).__init__(parent)

        # Attributes
        self._proj = None
        self._menu = ebmlib.ContextMenuManager()
        self._monitor = ebmlib.DirectoryMonitor(checkFreq=2000.0)
        self._monitor.SubscribeCallback(self.OnFilesChanged)
        self._monitor.StartMonitoring()

        # Setup
        self.SetupImageList()

        # Event Handlers
        self.Bind(wx.EVT_MENU, self.OnContextMenu)

        # Message Handlers
        ed_msg.Subscribe(self.OnGetProject, PyStudioMessages.PYSTUDIO_PROJECT_GET)

    #---- Properties ----#

    def __GetFileController(self):
        """Get FileController for currently configured filesystem"""
        opt = self._proj.GetOption(u"general", u"filesystem")
        if opt is None:
            # Default to base controller
            opt = u"OS"
        return FileController.FactoryCreate(opt)
    FileController = property(lambda self: self.__GetFileController())
    Project = property(lambda self: self._proj,
                       lambda self, proj: self.LoadProject(proj))

    #---- Overrides ----#

    def DoBeginEdit(self, item):
        """Handle when an item is requested to be edited"""
        # TODO: pass handling to see if the path can be edited to FileController?
        if self.IsProjectRoot(item):
            return False
        return True

    def DoEndEdit(self, item, newlabel):
        """Handle after a user has made changes to a label"""
        path = self.GetPyData(item)
        # TODO: check access rights and validate input
        newpath = os.path.join(os.path.dirname(path), newlabel)
        return self.FileController.Rename(path, newpath)

    def DoItemActivated(self, item):
        """Override to handle item activation
        @param item: TreeItem

        """
        path = self.GetPyData(item)
        if path and os.path.exists(path):
            if not os.path.isdir(path):
                PyStudioUtils.GetEditorOrOpenFile(self.Parent.MainWindow, path)
        # TODO notify failure to open

    def DoItemCollapsed(self, item):
        """Handle when an item is collapsed"""
        d = self.GetPyData(item)
        self._monitor.RemoveDirectory(d)
        super(ProjectTree, self).DoItemCollapsed(item)

    def DoItemExpanding(self, item):
        """Handle when an item is expanding to display the folder contents
        @param item: TreeItem

        """
        busy = wx.BusyCursor()
        d = None
        try:
            d = self.GetPyData(item)
        except wx.PyAssertionError:
            util.Log("[PyStudio][err] ProjectTree.DoItemExpanding")
            return

        if d and os.path.exists(d) and os.access(d, os.R_OK):
            contents = ProjectTree.GetDirContents(d)
            contents = self.FilterFileList(contents)
            with eclib.Freezer(self):
                self.AppendFileNodes(item, contents)
                self.SortChildren(item)

            if not self._monitor.AddDirectory(d):
                self.SetItemImage(item, ProjectUtil.FileIcons.IMG_NO_ACCESS)
                return

    def DoGetFileImage(self, path):
        """Get the image for the given item"""
        iconmgr = ProjectUtil.FileIcons
        if not os.access(path, os.R_OK):
            return iconmgr.IMG_NO_ACCESS
        elif os.path.isdir(path):
            if os.path.exists(os.path.join(path, "__init__.py")):
                return iconmgr.IMG_PACKAGE
            return iconmgr.IMG_FOLDER
        lpath = path.lower()
        fext = ebmlib.GetFileExtension(lpath)
        if fext in ('py', 'pyw'):
            return iconmgr.IMG_PYTHON
        elif fext in ('png', 'gif', 'ico', 'jpg', 'jpeg', 'bmp', 'icns'):
            return iconmgr.IMG_IMAGE
        else:
            return iconmgr.IMG_FILE

    def DoSetupImageList(self):
        """Setup the image list for this control"""
        ProjectUtil.FileIcons.PopulateImageList(self.ImageList)

    def DoShowMenu(self, item):
        """Show a context menu for the selected item
        @param item: TreeItem

        """
        path = self.GetPyData(item)
        self._menu.Clear()
        menu = wx.Menu()
        # Populate menu for current item with standard options
        if not os.path.isdir(path):
            tmpitem = wx.MenuItem(menu, ProjectTree.ID_EDIT_FILE, _("Edit"))
            menu.AppendItem(tmpitem)
        menu.Append(ProjectTree.ID_OPEN_FILE, _("Open..."))
        menu.Append(ProjectTree.ID_REVEL_FILE, _("Open enclosing folder..."))
        menu.AppendSeparator()
        newmenu = wx.Menu()
        for data in ((ProjectTree.ID_NEW_FILE, _("New File..."), ed_glob.ID_NEW),
                     (ProjectTree.ID_NEW_FOLDER, _("New Folder..."), ed_glob.ID_NEW_FOLDER),
                     (ProjectTree.ID_NEW_PACKAGE, _("New Package..."), ed_glob.ID_PACKAGE)):
            mitem = wx.MenuItem(newmenu, data[0], data[1])
            mitem.SetBitmap(wx.ArtProvider_GetBitmap(str(data[2]), wx.ART_MENU))
            newmenu.AppendItem(mitem)
        menu.AppendMenu(ProjectTree.ID_NEW_SUBMENU, _("New"), newmenu)
        menu.AppendSeparator()
        if not self.IsProjectRoot(item):
            if wx.Platform == '__WXMSW__':
                trash_str = _("Move to Recycle Bin")
            else:
                trash_str = _("Move to Trash")
            menu.Append(ed_glob.ID_DELETE, trash_str)
            menu.Append(ProjectTree.ID_RENAME_FILE, _("Rename"))
#            menu.AppendSeparator()

        ccount = menu.GetMenuItemCount()

        # Menu customization interface
        # Allow other components to add custom menu options
        self._menu.SetUserData('path', path) # path of item that was clicked on
        self._menu.SetUserData('itemId', item)
        ed_msg.PostMessage(PyStudioMessages.PYSTUDIO_PROJECT_MENU,
                           self._menu, self.Parent.MainWindow.Id)

        # Add properties
        # TODO: future release
#        if ccount < menu.GetMenuItemCount():
#            menu.AppendSeparator()
#        mitem = menu.Append(ProjectTree.ID_PROPERTIES, _("Properties"))
#        mitem.SetBitmap(wx.ArtProvider_GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU))

        # Show the popup Menu
        self._menu.Menu = menu
        self._menu.SetUserData('path', path)
        self.PopupMenu(self._menu.Menu)

    #---- Event Handlers ----#

    def OnContextMenu(self, evt):
        """Handle context menu events"""
        e_id = evt.Id
        path = self._menu.GetUserData('path')
        dname = path
        if not os.path.isdir(path):
            dname = os.path.dirname(path)

        if e_id == ProjectTree.ID_EDIT_FILE:
            PyStudioUtils.GetEditorOrOpenFile(self.Parent.MainWindow, path)
        elif e_id in (ProjectTree.ID_OPEN_FILE, ProjectTree.ID_REVEL_FILE):
            self.OpenPathWithFM(path, revel=(e_id == ProjectTree.ID_REVEL_FILE))
        elif e_id == ProjectTree.ID_NEW_FILE:
            self.CreateNewFile(dname)
        elif e_id in (ProjectTree.ID_NEW_FOLDER, ProjectTree.ID_NEW_PACKAGE):
            self.CreateNewFolder(dname, e_id == ProjectTree.ID_NEW_PACKAGE)
        elif e_id == ed_glob.ID_DELETE:
            # TODO need error handling?
            if dname == path:
                cmsg = _("Are you sure you want to delete '%s' and all of its contents?")
            else:
                cmsg = _("Are you sure you want to delete '%s'?")
            name = os.path.basename(path)
            result = wx.MessageBox(cmsg % name, _("Delete?"),
                                   style=wx.YES_NO | wx.CENTER | wx.ICON_QUESTION)
            if result == wx.YES:
                self.FileController.MoveToTrash(path)
        elif e_id == ProjectTree.ID_RENAME_FILE:
            item = self._menu.GetUserData('itemId')
            if item:
                self.EditLabel(item)
        elif e_id == ProjectTree.ID_PROPERTIES:
            pass  # TODO: project properties dialog
        else:
            # Handle Custom Menu options
            handler = self._menu.GetHandler(e_id)
            if handler:
                handler(path)

    def DoOnActivate(self, active):
        """Handle main window activation"""
        if active and self.IsShown():
            self.SuspendChecks(False)  # Resume
        elif not active:
            self.SuspendChecks(True)  # Suspend

    def DoOnDestroy(self):
        """Cleanup when window is destroyed"""
        util.Log("PyProject][info] Doing Cleanup in Destroy...")
        self._menu.Clear()
        ed_msg.Unsubscribe(self.OnGetProject)

    def OnFilesChanged(self, added, deleted, modified):
        """DirectoryMonitor callback - synchronize the view
        with the filesystem.

        """
        nodes = self.GetExpandedNodes()
        visible = list()
        for node in nodes:
            visible.extend(self.GetChildNodes(node))

        # Remove any deleted file objects
        for fobj in deleted:
            for item in visible:
                path = self.GetPyData(item)
                if fobj.Path == path:
                    self.Delete(item)
                    visible.remove(item)
                    break

        # Add any new file objects to the view
        needsort = list()
        added = self.FilterFileList([fobj.Path for fobj in added])
        for fobj in added:
            dpath = os.path.dirname(fobj)
            for item in nodes:
                path = self.GetPyData(item)
                if path == dpath:
                    self.AppendFileNode(item, fobj)
                    if item not in needsort:
                        needsort.append(item)
                    break

        # Resort display
        with eclib.Freezer(self):
            for item in needsort:
                self.SortChildren(item)

        # TODO: pass modification notifications onto FileController interface
        #       to handle.
#        for fobj in modified:
#            pass

    def OnCompareItems(self, item1, item2):
        """Handle SortItems"""
        data = self.GetPyData(item1)
        if data is not None:
            path1 = int(not os.path.isdir(data))
        else:
            path1 = 0
        tup1 = (path1, data.lower())

        data2 = self.GetPyData(item2)
        if data2 is not None:
            path2 = int(not os.path.isdir(data2))
        else:
            path2 = 0
        tup2 = (path2, data2.lower())

        if tup1 < tup2:
            return -1
        elif tup1 == tup2:
            return 0
        else:
            return 1

    def GetMainWindow(self):
        """Get this controls MainWindow. Used for mwcontext interface"""
        return self.Parent.MainWindow

    @ed_msg.mwcontext
    def OnGetProject(self, msg):
        """Return the project file reference to the client that
        requested it.

        """
        msg.Data['project'] = self.Project

    def IsProjectRoot(self, item):
        """Is the given item the current project root
        @param item: TreeItem
        @return: bool

        """
        path = self.GetPyData(item)
        if self.Project and self.Project.ProjectRoot:
            return path == self.Project.ProjectRoot
        return False

    #---- Implementation ----#

    def LoadProject(self, proj):
        """Load the given project
        @param proj: ProjectFile instance or None to clear

        """
        self.DeleteChildren(self.RootItem)
        if self.Project and self.Project.ProjectRoot:
            self.RemoveWatchDirectory(self._proj.ProjectRoot)
        self._proj = proj
        if not self.Project:
            return  # cleared/closed current project

        # Repopulate root of tree
        item = self.AddWatchDirectory(self.Project.ProjectRoot)
        if item:
            iconmgr = ProjectUtil.FileIcons
            self.SetItemImage(item, iconmgr.IMG_PROJECT)
            self.Expand(item)
            # Update last project info
            ToolConfig.SetConfigValue(ToolConfig.TLC_LAST_PROJECT, self.Project.Path)
            ed_msg.PostMessage(PyStudioMessages.PYSTUDIO_PROJECT_LOADED,
                               self.Project, self.Parent.MainWindow.Id)
        else:
            wx.MessageBox(_("Unable to load project: %s") % self.Project.ProjectName,
                          _("PyStudio Error"), style=wx.OK | wx.CENTER | wx.ICON_ERROR)
            return

    def OpenPathWithFM(self, path, revel=False):
        """Open the given path with the systems file manager
        @param path: path to open
        @keyword revel: revel path in file manager?

        """
        if revel:
            path = ebmlib.GetPathName(path)
        ebmlib.OpenWithFileManager(path)

    def CreateNewFile(self, dirname):
        """Prompt user for new file to create in given directory
        @param dirname: directory path to create file in

        """
        assert os.path.exists(dirname)
        name = wx.GetTextFromUser(_("Enter file name:"), _("New File"),
                                  parent=self.Parent.MainWindow)
        if name:
            self.FileController.CreateFile(dirname, name)

    def CreateNewFolder(self, dirname, package=False):
        """Prompt user for new name to create a new folder or Python package
        @param dirname: directory to create it in
        @keyword package: create a python package

        """
        assert os.path.exists(dirname)
        if not package:
            msg = _("Enter folder name:")
            caption = _("New Folder")
        else:
            msg = _("Enter package name:")
            caption = _("New Package")
        name = wx.GetTextFromUser(msg, caption,
                                  parent=self.Parent.MainWindow)
        if name:
            self.FileController.CreateFolder(dirname, name)
            # TODO need return val from CreateFolder
            if package:
                path = os.path.join(dirname, name)
                self.FileController.CreateFile(path, "__init__.py")

    def FilterFileList(self, paths):
        """Filter a list of files returning only the ones that are valid to
        display in the tree. Optimized for large lists of paths.
        @param paths: list of paths
        @return: filtered list

        """
        filters = ("*.pyc", "*.pyo", "*.psp")  # TODO: add filter configuration
        isHidden = ebmlib.IsHidden
        rval = list()
        rAdd = rval.append
        getBase = os.path.basename
        for path in paths:
            if isHidden(path):  # TODO: support show hidden files
                continue
            name = getBase(path)
            if filter(lambda x: fnmatch.fnmatchcase(name, x), filters):
                continue
            rAdd(path)
        return rval

    def SuspendChecks(self, suspend=True):
        """Suspend/Continue background monitoring"""
        self._monitor.Suspend(suspend)
