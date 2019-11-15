###############################################################################
# Name: __init__.py                                                           #
# Purpose: RegexCheck plugin                                                  #
# Author: Erik Tollerud <erik.tollerud@gmail.com>                             #
# Copyright: (c) 2010 Erik Tollerud <erik.tollerud@gmail.com>                 #
# License: wxWindows License                                                  #
###############################################################################

"""Adds a regular expression testing panel to the Editra shelf."""
__author__ = "Erik Tollerud"
__version__ = "0.1"

#-----------------------------------------------------------------------------#

import wx                   
import iface
import plugin

from regexcheckui import RegexCheckPanel

_ = wx.GetTranslation

class RegexCheck(plugin.Plugin):
    """Adds a regular expression tester to the shelf"""
    plugin.Implements(iface.ShelfI) 
    
    ID_REGEX_CHECKER = wx.NewId()
    __name__=u'Regex Checker'
    
    def AllowMultiple(self):
        """This method is used to check if multiple instances of this
        item are allowed to be open at one time.
        @return: True/False
        @rtype: boolean
 
        """
        return True
 
    def CreateItem(self, parent):
        """This is the method used to open the item in the L{Shelf}
        It should return an object that is a Panel or subclass of a Panel.
        @param parent: The would be parent window of this panel
        @return: wx.Panel
 
        """
        return RegexCheckPanel(parent)
 
#    def GetBitmap(self):
#        """Get the bitmap to show in the shelf for this item
#        @return: wx.Bitmap
#        @note: this method is optional
 
#        """
#        return wx.NullBitmap
 
    def GetId(self):
        """Return the id that identifies this item (same as the menuid)
        @return: Item ID
        @rtype: int
 
        """
        return self.ID_REGEX_CHECKER
 
    def GetMenuEntry(self, menu):
        """Returns the menu entry associated with this item
        @param menu: The menu this entry will be added to
        @return: wx.MenuItem
 
        """
        return wx.MenuItem(menu, self.ID_REGEX_CHECKER,self.__name__, 
                           _("Open a regular expressions testing panel"))
 
    def GetName(self):
        """Return the name of this shelf item. This should be the
        same as the MenuEntry's label.
        @return: name of item
        @rtype: string
 
        """
        return self.__name__
 
#    def InstallComponents(self, mainw):
#        """Called by the Shelf when the plugin is created to allow it
#        to install any extra components that it may have that fall outside
#        the normal interface. This method is optional and does not need
#        to be implimented if it is not needed.
#        @param mainw: MainWindow Instance
 
#        """
#        pass
 
    def IsStockable(self):
        """Return whether this item type is stockable. The shelf saves
        what pages it had open the last time the program was run and then
        reloads the pages the next time the program starts. If this
        item can be reloaded between sessions return True otherwise return
        False.
 
        """
        return True

#def GetConfigObject():
#    return RegexTesterConfig()

