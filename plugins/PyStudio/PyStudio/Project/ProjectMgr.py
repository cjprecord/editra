###############################################################################
# Name: ProjectMgr.py                                                         #
# Purpose: Project File Manager                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Project File Manager

Main PyProject UI components for integration into Editra user interface.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ProjectMgr.py 1555 2012-08-15 20:06:57Z CodyPrecord $"
__revision__ = "$Revision: 1555 $"

#-----------------------------------------------------------------------------#
# Dependencies
import os
import wx

# Editra libs
import ed_glob
import util
import ebmlib
import ed_basewin
import syntax.synglob as synglob

# Local libs
from PyStudio.Common import ToolConfig, Images
from PyStudio.Project import ProjectXml, ProjectFile, NewProjectDlg
from PyStudio.Project.ProjectTree import ProjectTree
from PyStudio.Project import ProjectCfgDlg

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ProjectManager(ed_basewin.EdBaseCtrlBox):
    """Main UI component for the Project feature."""
    PANE_NAME = u"PyProject"
    ID_NEW_PROJECT = wx.NewId()
    ID_IMPORT_PROJECT = wx.NewId()
    ID_OPEN_PROJECT = wx.NewId()
    ID_CONF_PROJECT = wx.NewId()
    def __init__(self, parent):
        """Create the manager window
        @param parent: MainWindow instance

        """
        super(ProjectManager, self).__init__(parent)
        util.Log("[PyProject][info] Creating ProjectManager instance")

        # Attributes
        self._mw = parent
        self._tree = ProjectTree(self)

        # Setup
        cbar = self.CreateControlBar(wx.TOP)
        # Setup the project button
        self.projbtn = cbar.AddPlateButton(bmp=Images.Project.Bitmap)
        pmenu = wx.Menu()
        pmenu.Append(ProjectManager.ID_NEW_PROJECT, _("New Project"),
                     _("Create a new project"))
        pmenu.Append(ProjectManager.ID_IMPORT_PROJECT, _("Import Project"),
                     _("Import an existing project"))
        pmenu.Append(ProjectManager.ID_OPEN_PROJECT, _("Open Project"),
                     _("Open an existing PyProject project file"))
         # TODO: Future release
#        pmenu.AppendSeparator()
#        item = wx.MenuItem(pmenu,
#                           ProjectManager.ID_CONF_PROJECT,
#                           _("Project Settings"))
#        item.Bitmap = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
#        pmenu.AppendItem(item)
        self.projbtn.SetMenu(pmenu)
        # Setup additional buttons
        bmp = wx.ArtProvider_GetBitmap(str(synglob.ID_LANG_PYTHON), wx.ART_MENU)
        cbar.AddControl(wx.StaticLine(cbar, size=(1, 16), style=wx.LI_VERTICAL))
        nfilebtn = cbar.AddPlateButton(bmp=bmp)
        nfilebtn.ToolTip = wx.ToolTip(_("New Module"))
        bmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PACKAGE), wx.ART_MENU)
        npkgbtn = cbar.AddPlateButton(bmp=bmp)
        npkgbtn.ToolTip = wx.ToolTip(_("New Package"))
        bmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_NEW_FOLDER), wx.ART_MENU)
        nfolderbtn = cbar.AddPlateButton(bmp=bmp)
        nfolderbtn.ToolTip = wx.ToolTip(_("New Folder"))
        self.SetWindow(self._tree)

        # Post Initialization
        if ToolConfig.GetConfigValue(ToolConfig.TLC_LOAD_LAST_PROJECT, True):
            lproj = ToolConfig.GetConfigValue(ToolConfig.TLC_LAST_PROJECT, None)
            util.Log("[PyProject][info] Loading last project %s" % repr(lproj))
            if lproj and os.path.exists(lproj):
                self.DoOpenProject(lproj)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnNewFile, nfilebtn)
        self.Bind(wx.EVT_BUTTON, self.OnNewPackage, npkgbtn)
        self.Bind(wx.EVT_BUTTON, self.OnNewFolder, nfolderbtn)
        # TODO: enable this code when new version of AUI is in use
        #       current 2.8 version has bug in propagating updateui events.
#        for btn in (nfilebtn, npkgbtn, nfolderbtn):
#            btn.Bind(wx.EVT_UPDATE_UI, self.OnUpdateButtons)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Bind(wx.EVT_SHOW, self.OnShow)

    #---- Properties ----#

    MainWindow = property(lambda self: self._mw)
    Tree = property(lambda self: self._tree)

    #---- Implementation ----#

    def DoOpenProject(self, path):
        """Open the project file and display it in the L{ProjectTree}
        @param path: PyStudio Project file path

        """
        pxml = ProjectXml.ProjectXml.Load(path)
        pfile = ProjectFile.ProjectFile(pxml, path)
        self.Tree.LoadProject(pfile)

    def OnNewFolder(self, evt):
        """Create a new folder in the project"""
        paths = self.Tree.GetSelectedFiles()
        if len(paths):
            path = paths[0]
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            self.Tree.CreateNewFolder(path, False)

    def OnNewPackage(self, evt):
        """Create a new package in the project"""
        paths = self.Tree.GetSelectedFiles()
        if len(paths):
            path = paths[0]
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            self.Tree.CreateNewFolder(path, True)

    def OnNewFile(self, evt):
        """Create a new file in the project"""
        paths = self.Tree.GetSelectedFiles()
        if len(paths):
            path = paths[0]
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            self.Tree.CreateNewFile(path)

    def OnMenu(self, evt):
        """Handles menu events for the Project Manager"""
        actions = {ProjectManager.ID_NEW_PROJECT: self.NewProject,
                    ProjectManager.ID_IMPORT_PROJECT: self.ImportProject,
                    ProjectManager.ID_OPEN_PROJECT: self.OpenProject,
                    ProjectManager.ID_CONF_PROJECT: self.ShowConfig}
        actions.get(evt.Id, evt.Skip)()

    def OnShow(self, evt):
        """Activate/deactivate processing when window is shown/hidden"""
        if self and self._tree:
            self._tree.SuspendChecks(not evt.IsShown())
        evt.Skip()

    def OnUpdateButtons(self, evt):
        """UpdateUI handler for file/folder/package button"""
        hassel = len(self.Tree.GetSelections()) > 0
        evt.Enable(hassel)

    def ImportProject(self):
        """Prompt the user to import an existing project"""
        cbuf = wx.GetApp().GetCurrentBuffer()
        if cbuf and hasattr(cbuf, 'GetFileName'):
            fname = cbuf.GetFileName()
            dname = os.path.dirname(fname)
        # TODO: Enhancement - support loading/import other project types (i.e pydev)
        dlg = wx.DirDialog(self.MainWindow, _("Import Project Directory"),
                           dname)
        if dlg.ShowModal() == wx.ID_OK:
            proj = dlg.Path
            projName = os.path.basename(proj)
            pxml = ProjectXml.ProjectXml(name=projName)
            # Write out the new project file
            ppath = os.path.join(proj, u"%s.psp" % projName)
            if ebmlib.PathExists(ppath):
                result = wx.MessageBox(_("The project '%s' already exists.\nDo you wish to overwrite it?") % projName,
                                       _("Project Exists"),
                                       style=wx.ICON_WARNING | wx.YES_NO)
                if result == wx.ID_NO:
                    return
            pfile = ProjectFile.ProjectFile(pxml, ppath)
            pfile.Save(force=True)
            self.Tree.LoadProject(pfile)  # Load the view

    def NewProject(self):
        """Create a new project"""
        dlg = NewProjectDlg.NewProjectDlg(self.MainWindow)
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            proj = dlg.GetProjectData()
            if proj.CreateProject():
                # Create the project file
                pxml = ProjectXml.ProjectXml(name=proj.ProjectName)
                pxml.folders = proj.Template.folders
                pxml.packages = proj.Template.packages
                def CleanFiles(fold):
                    """Remove template files from project configuration"""
                    for d in fold:
                        d.files = list()
                        CleanFiles(d.folders)
                        CleanFiles(d.packages)
                CleanFiles(pxml.folders)
                CleanFiles(pxml.packages)
                # Write the project file out to the new project directory
                ppath = os.path.join(proj.ProjectPath, u"%s.psp" % proj.ProjectName)
                util.Log("[PyStudio][info] New Project File: %s" % ppath)
                pfile = ProjectFile.ProjectFile(pxml, ppath)
                pfile.Save(force=True)
                self.Tree.LoadProject(pfile)  # Load the view
            else:
                pass  # TODO: error handling
        dlg.Destroy()

    def OpenProject(self):
        """Show the project open dialog"""
        dname = u""
        cbuf = wx.GetApp().GetCurrentBuffer()
        if cbuf and hasattr(cbuf, 'GetFileName'):
            fname = cbuf.GetFileName()
            dname = os.path.dirname(fname)
        dlg = wx.FileDialog(self.MainWindow, _("Open Project"),
                            defaultDir=dname,
                            wildcard=u"PyStudio Project (*.psp)|*.psp",
                            style=wx.FD_OPEN)
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.DoOpenProject(dlg.Path)
        dlg.Destroy()

    def ShowConfig(self):
        """Show the configuration for the current project"""
        # TODO: stub...
        dlg = ProjectCfgDlg.ProjectCfgDlg(self, title=_("Project Settings"))
        dlg.ShowModal()
