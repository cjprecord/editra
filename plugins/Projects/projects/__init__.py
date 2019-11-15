# -*- coding: utf-8 -*-
###############################################################################
# Name: __int__.py                                                            #
# Purpose: Project Tree View                                                  #
# Author: Kevin D. Smith <Kevin.Smith@sixquickrun.com>                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

""" Adds a sidepanel that incorporates file management and source control """

__author__ = "Kevin D. Smith, Cody Precord"
__revision__ = "$Revision: 1407 $"
__scid__ = "$Id: __init__.py 1407 2011-06-07 02:09:40Z CodyPrecord@gmail.com $"

#-----------------------------------------------------------------------------#
# Imports
import wx 

# Editra Libraries
import plugin 
import ed_glob
import iface
import ed_menu
import util

# Local libraries
import ConfigDialog
from ProjectPane import ProjectPane
from ModList import RepoModBox
import FileIcons

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation
PANE_NAME = ProjectPane.PANE_NAME

# Try and add this plugins message catalogs to the app
try:
    wx.GetApp().AddMessageCatalog('Projects', __name__)
except:
    pass

#-----------------------------------------------------------------------------#

class Projects(plugin.Plugin):
    """Adds a projects pane to the view menu"""
    plugin.Implements(iface.MainWindowI)

    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
        mainw = parent
        if mainw != None:
            util.Log("[projects][info] Installing projects plugin")

            self._projects = ProjectPane(mainw)
            mgr = mainw.GetFrameManager()
            mgr.AddPane(self._projects, wx.aui.AuiPaneInfo().Name(PANE_NAME).\
                        Caption(_("Projects")).Left().Layer(1).\
                        CloseButton(True).MaximizeButton(False).\
                        BestSize(wx.Size(215, 350)))

            mgr.Update()

    def GetMenuHandlers(self):
        """Returns the menu event handlers"""
        return [(ProjectPane.ID_PROJECTS, self._projects.OnShowProjects)]

    def GetMinVersion(self):
        """Get the minimum version of Editra that this plugin supports"""
        return "0.6.48"

    def GetUIHandlers(self):
        """Returns handlers for UpdateUI events"""
        return [(ProjectPane.ID_PROJECTS, self._projects.OnUpdateMenu)]

#-----------------------------------------------------------------------------#

ID_MODLIST = wx.NewId()

class ProjectsModList(plugin.Plugin):
    """Shelf interface implementation for the Repo Modification List"""
    plugin.Implements(iface.ShelfI)

    @property
    def __name__(self):
        return u'Source Control'

    def AllowMultiple(self):
        """ModList allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Returns a log viewer panel"""
        modbox = RepoModBox(parent)
        modbox.SetFileOpenerHook(wx.GetApp().MacOpenFile)
        return modbox

    def GetBitmap(self):
        """Get the tab icon
        @return: wx.Bitmap

        """
        return FileIcons.getScUpdateBitmap()

    def GetId(self):
        """Plugin menu identifier ID"""
        return ID_MODLIST

    def GetMenuEntry(self, menu):
        """Get the menu entry for the log viewer
        @param menu: the menu items parent menu

        """
        item = wx.MenuItem(menu, ID_MODLIST, _("Source Control"),
                           _("Open the Projects source control summary list"))
        item.SetBitmap(self.GetBitmap())
        return item

    def GetName(self):
        """Return the name of this control"""
        return self.__name__

    def IsStockable(self):
        """ModList can be saved in the shelf preference stack"""
        return True

#-----------------------------------------------------------------------------#

def GetConfigObject():
    return ProjectsConfigObject()

class ProjectsConfigObject(plugin.PluginConfigObject):
    """Plugin configuration object. Plugins that wish to provide a
    configuration panel should implement a subclass of this object
    in their __init__ module.

    """
    def GetConfigPanel(self, parent):
        """Get the configuration panel for this plugin
        @param parent: parent window for the panel
        @return: wxPanel

        """
        return ConfigDialog.ConfigNotebook(parent, wx.ID_ANY,
                                           ConfigDialog.ConfigData())

    def GetLabel(self):
        """Get the label for this config panel
        @return string

        """
        return _("Projects")
