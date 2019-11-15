# -*- coding: utf-8 -*-
# Name: __init__.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

# Plugin Metadata
"""
Adds Python syntax checking using Pylint with results in a Shelf window.

"""

__version__ = "0.1"
__author__ = "Mike Rans"
__svnid__ = "$Id: __init__.py 1092 2011-02-26 22:31:48Z CodyPrecord $"
__revision__ = "$Revision: 1092 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra imports
import ed_glob
import iface
import plugin
import util

# Local Imports
from ShelfWindow import ShelfWindow
import ToolConfig

#-----------------------------------------------------------------------------#
from wx.lib.embeddedimage import PyEmbeddedImage

Lint = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAABl0"
    "RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKXSURBVDiNlZJLaJRnFIaf75uZ"
    "6EwSm9tIQpNIvNWoFCsmiwrSgotKS3aCl4WL0Y2CIvwLBV0YFwYckFIQhI7GhWBLdaEL6Y0W"
    "MS20aTQxijGNmnFGSZPJZcw/80/+//uOK0VjIfisz/twzstRR75gczjEBRGixrL31A35kfdA"
    "hzTfr22OrdqworwxpLl6dJva+l4CYHFFVLO0KsLHLbFYSHP29H6lU0nVmUqq2gUFVugcfFJ0"
    "fSPU15QRXazqqxrpBY4DSxcUiPCN65mLtwbz7kzJp6mdypWtGzfE400vgLqFBEpEAOjap07E"
    "V3L8k7bPVXNLOz2nu73pf8Zy7FSTxsglEc4nHBn/X0EqqXZprb79dHNHtK6ugX+//punVx+y"
    "/ux2atdVkR7t9+7f/UOM9b4zRo4lHMnOF+zRmmRTfWs5lyRqJl22dG9lUY0GFYVQNX5Qzr3B"
    "X/2B/t8N4v9gDCng5usTUkm1KHKOOxXNtas6Lh8Oaf0cQg1gxsBksUEez7bgzdWQyQzI45EB"
    "d2oyW9SvVkk4UvJ301V7sLGkI2VgZyEYAZMF8x9e4RmzuevMjJ0jXo3a1P5VhVZKwm81UsHP"
    "2UxaW6tQ/ggiPv6ch1eapViYoVCYRkTQ4UrST3oDlPym38wnHHnmz02PpNN3mXFjTEyMksul"
    "mcxlcN0pRIRY9TYKRc3Qg/6SMThvCQACI4f6en8p+qzGdT2KxTzWBuhwDZXxHeTdmNy6eSVv"
    "TPBlwpHM6xLfpPuM6ln9UXvb8hWtES//J2WxNejIMh4N9wRDQ33j1vJZwpGHAOF30oAxdAw9"
    "+Ot25ZKGDz+oatOjo/f84eGfAmu869ZyIOHIxDufOJ9UUi1Tij6lEOCatZxMOPJ4/txLfgdD"
    "CCiEEtoAAAAASUVORK5CYII=")

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Implementation
class Pylint(plugin.Plugin):
    """Script Launcher and output viewer"""
    plugin.Implements(iface.ShelfI)
    ID_PYLINT = wx.NewId()
    INSTALLED = False
    SHELF = None

    @property
    def __name__(self):
        return u'Pylint'

    def AllowMultiple(self):
        """PyLint allows multiple instances"""
        return True

    def CreateItem(self, parent):
        """Create a PyLint panel"""
        util.Log("[PyLint][info] Creating Pylint instance for Shelf")
        return ShelfWindow(parent)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        return Lint.Bitmap

    def GetId(self):
        """The unique identifier of this plugin"""
        return self.ID_PYLINT

    def GetMenuEntry(self, menu):
        """This plugins menu entry"""
        item = wx.MenuItem(menu, Pylint.ID_PYLINT, self.__name__,
                           _("Show Pylint checker"))
        item.SetBitmap(self.GetBitmap())
        return item

    def GetMinVersion(self):
        """Minimum version of Editra this plugin is compatible with"""
        return "6.01"

    def GetName(self):
        """The name of this plugin"""
        return self.__name__

    def InstallComponents(self, mainw):
        """Install extra menu components
        param mainw: MainWindow Instance

        """
        pass

    def IsInstalled(self):
        """Check whether PyLint has been installed yet or not
        @note: overridden from Plugin
        @return bool

        """
        return Pylint.INSTALLED

    def IsStockable(self):
        """This item can be reloaded between sessions"""
        return True

#-----------------------------------------------------------------------------#
# Configuration Interface

def GetConfigObject():
    return ConfigObject()

class ConfigObject(plugin.PluginConfigObject):
    """Plugin configuration object for PyLint
    Provides configuration panel for plugin dialog.

    """
    def GetConfigPanel(self, parent):
        """Get the configuration panel for this plugin
        @param parent: parent window for the panel
        @return: wxPanel

        """
        return ToolConfig.ToolConfigPanel(parent)

    def GetLabel(self):
        """Get the label for this config panel
        @return string

        """
        return _("PyLint")
