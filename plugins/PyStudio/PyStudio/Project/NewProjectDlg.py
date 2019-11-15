###############################################################################
# Name: NewProjectDlg.py                                                      #
# Purpose: New Project Dialog class                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
NewProjectDlg

Dialog for creating a new project

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: NewProjectDlg.py 1546 2012-07-29 18:35:50Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1546 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Editra Libraries
import eclib
import ed_basewin

# Local Modules
import PyStudio.Project.ProjectTemplate as ProjectTemplate
import PyStudio.Project.ProjectXml as ProjectXml
from PyStudio.Project.ProjectUtil import FileIcons

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class NewProjectDlg(ed_basewin.EdBaseDialog):
    """Dialog for creating a new project"""
    def __init__(self, parent):
        super(NewProjectDlg, self).__init__(parent,
                                            title=_("Create New Project"),
                                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        # Attributes
        self.Panel = NewProjectPanel(self)

        # Setup
        bszr = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.Sizer.Add((10, 10), 0)
        self.Sizer.Add(bszr, 0, wx.EXPAND | wx.ALL, 5)
        self.SetInitialSize(size=(450, 400))
        self.CenterOnParent()

        # Event Handlers
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateOkBtn, id=wx.ID_OK)

    def OnUpdateOkBtn(self, evt):
        """Enable/Disable the Ok button depending on field state"""
        evt.Enable(self.Panel.IsValid())

#-----------------------------------------------------------------------------#

class NewProjectPanel(wx.Panel):
    """Main dialog panel"""
    def __init__(self, parent):
        super(NewProjectPanel, self).__init__(parent)

        # Attributes
        self._ptype = ProjectTypePanel(self)
        self._pname = wx.TextCtrl(self)  # TODO validator alpha-numeric only
        self._pname.ToolTip = wx.ToolTip(_("Project directory will be created using this name."))
        self._pdir = wx.DirPickerCtrl(self)  # TODO: default path
        self._pdir.ToolTip = wx.ToolTip(_("Location to create new project."))

        # Setup
        self.__DoLayout()

    def __DoLayout(self):
        """Layout the panel"""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Type Selection Panel
        sizer.Add(self._ptype, 1, wx.EXPAND | wx.ALL, 5)

        hline = wx.StaticLine(self, size=(-1, 1), style=wx.LI_HORIZONTAL)
        sizer.Add(hline, 0, wx.EXPAND | wx.ALL, 5)

        # Project Name / Location
        gszr = wx.FlexGridSizer(2, 2, 3, 3)
        gszr.AddGrowableCol(1, 1)
        nlbl = wx.StaticText(self, label=_("Project Name:"))
        gszr.Add(nlbl, 0, wx.ALIGN_CENTER_VERTICAL)
        gszr.Add(self._pname, 1, wx.EXPAND)
        llbl = wx.StaticText(self, label=_("Project Destination:"))
        gszr.Add(llbl, 0, wx.ALIGN_CENTER_VERTICAL)
        gszr.Add(self._pdir, 1, wx.EXPAND)
        sizer.Add(gszr, 0, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

    @eclib.expose(NewProjectDlg)
    def GetProjectData(self):
        """Get the project data"""
        return ProjectData(self._ptype.GetSelectedTemplate(),
                           self._pname.Value,
                           self._pdir.Path)

    def IsValid(self):
        """Check if all the required fields are valid
        @return: bool

        """
        return all([self._pname.Value,
                    self._pdir.Path,
                    self._ptype.HasSelection()])

#-----------------------------------------------------------------------------#

class ProjectTypePanel(wx.Panel):
    """Sub-Panel for selecting the type of project to create"""
    def __init__(self, parent):
        super(ProjectTypePanel, self).__init__(parent)

        # Attributes
        typeBox = wx.StaticBox(self, label=_("Project Type"))
        self._tbox = wx.StaticBoxSizer(typeBox, wx.VERTICAL)
        descBox = wx.StaticBox(self, label=_("Preview"), size=(300, 200))
        self._dbox = wx.StaticBoxSizer(descBox, wx.VERTICAL)
        self._preview = TemplatePreview(self)
        # TODO: load from user config
        self._templates = ProjectTemplate.GetDefaultTemplates()
        names = self._templates.GetTemplateNames()
        self._tlist = wx.ListBox(self, choices=names, style=wx.LB_SINGLE)

        # Setup
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_LISTBOX, self.OnTypeList, self._tlist)

    def __DoLayout(self):
        """Layout the panel"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Type Selection List
        self._tbox.Add(self._tlist, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self._tbox, 1, wx.EXPAND | wx.ALL, 10)

        # Description Box
        self._dbox.Add(self._preview, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self._dbox, 1, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

    def GetSelectedTemplate(self):
        """Get the template for the selected project
        @return: ProjectTemplate

        """
        tname = self._tlist.StringSelection
        template = self._templates.FindTemplate(tname)
        return template

    def OnTypeList(self, evt):
        """Handle when an item is selected in the type list"""
        tplate = self.GetSelectedTemplate()
        self._preview.DisplayTemplate(tplate)
        # TODO: update project name based on text entry box?

    def HasSelection(self):
        """Check whether a project type has been selected
        @return: bool

        """
        return self._tlist.Selection != -1

#-----------------------------------------------------------------------------#

class TemplatePreview(wx.TreeCtrl):
    """Used for displaying a preview of what the selected project template
    will create.

    """
    def __init__(self, parent):
        super(TemplatePreview, self).__init__(parent,
                                              style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)

        # Setup
        self._il = wx.ImageList(16, 16)
        self.SetImageList(self._il)
        FileIcons.PopulateImageList(self.ImageList)
        self.AddRoot(_("<Project Destination>"), FileIcons.IMG_FOLDER)
        self._projNameId = None

    def DisplayTemplate(self, template):
        """Display the given project template in the control
        @param template: ProjectTemplate

        """
        self.DeleteChildren(self.RootItem)
        def PopulateItems(obj, parent):
            """Recursively walk through the template"""
            # Recurse into each directory object
            dirs = list()
            dirs.extend(obj.folders)
            dirs.extend(obj.packages)
            for dobj in dirs:
                img = FileIcons.IMG_FOLDER
                if isinstance(dobj, ProjectXml.PyPackage):
                    img = FileIcons.IMG_PACKAGE
                name = dobj.name % dict(projName=_("<Project Name>"))
                nparent = self.AppendItem(parent, name, img)
                PopulateItems(dobj, nparent)

            # Create all files
            for fobj in obj.files:
                img = FileIcons.IMG_FILE
                if fobj.name.endswith('.py') or fobj.name.endswith(u'.pyw'):
                    img = FileIcons.IMG_PYTHON
                self.AppendItem(parent, fobj.name, img)

        # Add Main Project Directory
        self._projNameId = self.AppendItem(self.RootItem, _("<Project Name>"),
                                           FileIcons.IMG_PROJECT)
        PopulateItems(template, self._projNameId)
        self.ExpandAll()

    def UpdateProjectName(self, pname):
        """Update the display name for the project in the tree
        @param pname: unicode

        """
        if self._projNameId is not None:
            self.SetItemText(self._projNameId, pname)

#-----------------------------------------------------------------------------#

class ProjectData(object):
    """Simple data container for the new project configuration data"""
    def __init__(self, template, name, path):
        super(ProjectData, self).__init__()

        # Attributes
        self._template = template
        self._name = name
        self._path = path

    ProjectName = property(lambda self: self._name)
    ProjectPath = property(lambda self: os.path.join(self._path, self._name))
    Template = property(lambda self: self._template)

    def CreateProject(self):
        """Create the project
        @return: bool

        """
        return self._template.Create(self._path, self.ProjectName)
