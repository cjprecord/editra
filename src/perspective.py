###############################################################################
# Name: perspectives.py                                                       #
# Purpose: Editra's view management service                                   #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: perspective.py                                                     #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    Provides a perspective management class for saving and loading custom #
# perspectives in the MainWindow.                                          #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
import util
import ed_menu
from profiler import Profile_Get

#--------------------------------------------------------------------------#
# Globals
DATA_FILE = u'perspectives'
LAST_KEY = u'**LASTVIEW**'
ID_DELETE_PERSPECTIVE = wx.NewId()
ID_SAVE_PERSPECTIVE = wx.NewId()

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class PerspectiveManager(object):
    """Creates a perspective manager for the given aui managed window.
    It supports saving and loading of on disk perspectives as created by
    calling SavePerspective from the AuiManager.

    """
    def __init__(self, auimgr, base):
        """Initializes the perspective manager. The auimgr parameter is
        a reference to the windows AuiManager instance, base is the base
        path to where perspectives should be loaded from and saved to.
        @param auimgr: AuiManager to use
        @param base: path to configuration cache

        """
        object.__init__(self)

        # Attributes
        self._window = auimgr.GetManagedWindow()    # Managed Window
        self._mgr = auimgr                          # Window Manager
        self._ids = list()                          # List of menu ids
        self._base = os.path.join(base, DATA_FILE)  # Path to config
        self._viewset = dict()                      # Set of Views
        self.LoadPerspectives()
        self._menu = ed_menu.ED_Menu()              # Control menu
        self._currview = None                       # Currently used view

        # Setup Menu
        self._menu.Append(ID_SAVE_PERSPECTIVE, _("Save Current View"),
                    _("Save the current window layout"))
        self._menu.Append(ID_DELETE_PERSPECTIVE, _("Delete Saved View"))
        self._menu.AppendSeparator()
        for name in self._viewset:
            self.AddPerspectiveMenuEntry(name)

        # Restore the managed windows previous position and alpha
        # preferences if they are available.
        self._window.SetTransparent(Profile_Get('ALPHA', default=255))
        if Profile_Get('SET_WPOS') and Profile_Get('WPOS', "size_tuple", False):
            self._window.SetPosition(Profile_Get('WPOS'))
        else:
            self._window.CenterOnParent()

        # Event Handlers
        self._window.Bind(wx.EVT_MENU, self.OnPerspectiveMenu)

    def AddPerspective(self, name, p_data=None):
        """Add a perspective to the view set. If the p_data parameter
        is not set then the current view will be added with the given name.
        @param name: name for new perspective
        @keyword p_data: perspective data from auimgr

        """
        if not len(name):
            return
        if self.HasPerspective(name.strip()):
            menu = False
        else:
            menu = True

        if not p_data:
            self._viewset[name.strip()] = self._mgr.SavePerspective()
        else:
            self._viewset[name.strip()] = p_data
        self._currview = name.strip()
        if menu:
            self.AddPerspectiveMenuEntry(name)
        self.SavePerspectives()

    def AddPerspectiveMenuEntry(self, name):
        """Adds an entry to list of perpectives in the menu for this manager.
        @param name: name of perspective to add to menu

        """
        if not len(name):
            return
        per_id = wx.NewId()
        self._ids.append(per_id)
        self._menu.InsertAlpha(per_id, name, _("Change view to \"%s\"") % name, 
                               after=ID_DELETE_PERSPECTIVE)

    def GetPerspectiveControls(self):
        """Returns the control menu for the manager
        @return: menu of this manager

        """
        return self._menu

    def GetPerspective(self):
        """Returns the name of the current perspective used
        @return: name of currently active perspective

        """
        return self._currview

    def GetPerspectiveData(self, name):
        """Returns the given named perspectives data string
        @param name: name of perspective to fetch data from

        """
        return self._viewset.get(name, None)
            
    def GetPerspectiveList(self):
        """Returns a list of all the loaded perspectives. The
        returned list only provides the names of the perspectives
        and not the actual data.
        @return: list of all managed perspectives

        """
        views = self._viewset.keys()
        views.sort()
        return views

    def HasPerspective(self, name):
        """Returns True if there is a perspective by the given name
        being managed by this manager, or False otherwise.
        @param name: name of perspective to look for
        @return: whether perspective is managed by this manager or not

        """
        return self._viewset.has_key(name)

    def LoadPerspectives(self):
        """Loads the perspectives data into the manager. Returns 
        the number of perspectives that were successfully loaded.
        @return: number of perspectives loaded

        """
        reader = util.GetFileReader(self._base)
        if reader == -1:
            return 0

        try:
            for line in reader.readlines():
                label, val = line.split(u"=", 1)
                if not len(label.strip()):
                    continue
                self._viewset[label.strip()] = val.strip()
            reader.close()
        finally:
            if self._viewset.has_key(LAST_KEY):
                self._currview = self._viewset[LAST_KEY]
                del self._viewset[LAST_KEY]
            return len(self._viewset)

    def OnPerspectiveMenu(self, evt):
        """Handles menu events generated by the managers control
        menu.
        @param evt: event that called this handler
        
        """
        e_id = evt.GetId()
        if e_id in [ID_SAVE_PERSPECTIVE, ID_DELETE_PERSPECTIVE]:
            if e_id == ID_SAVE_PERSPECTIVE:
                name = wx.GetTextFromUser(_("Perspective Name"), \
                                          _("Save Perspective"))
                if name:
                    self.AddPerspective(name, p_data=None)
                    self.SavePerspectives()

                    for mainw in wx.GetApp().GetMainWindows():
                        mainw.AddPerspective(name, self._viewset[name])

            elif e_id == ID_DELETE_PERSPECTIVE:
                name = wx.GetSingleChoice(_("Perspective to Delete"), 
                                          _("Delete Perspective"),
                                          self._viewset.keys())
                if name:
                    self.RemovePerspective(name)
                    self.SavePerspectives()
                    for mainw in wx.GetApp().GetMainWindows():
                        mainw.RemovePerspective(name)
            else:
                pass

            # Update all windows data sets
            for mainw in wx.GetApp().GetMainWindows():
                mainw.LoadPerspectives()
        elif e_id in self._ids:
            self.SetPerspectiveById(e_id)
        else:
            evt.Skip()

    def RemovePerspective(self, name):
        """Removes a named perspective from the managed set
        @param name: name of perspective to remove/delete

        """
        if self._viewset.has_key(name):
            del self._viewset[name]
            rem_id = self._menu.RemoveItemByName(name)
            if rem_id:
                self._ids.remove(rem_id)

    def SavePerspectives(self):
        """Writes the perspectives out to disk. Returns
        True if all data was written and False if there
        was an error.
        @return: whether save was successfull
        @rtype: bool

        """
        writer = util.GetFileWriter(self._base)
        if writer == -1:
            return False

        try:
            self._viewset[LAST_KEY] = self._currview
            for perspect in self._viewset:
                writer.write(u"%s=%s\n" % (perspect, self._viewset[perspect]))
            del self._viewset[LAST_KEY]
        except (IOError, OSError):
            return False
        else:
            return True

    def SetPerspective(self, name):
        """Sets the perspective of the managed window, returns
        True on success and False on failure.
        @param name: name of perspectve to set
        @return: whether perspective was set or not
        @rtype: bool

        """
        if self._viewset.has_key(name):
            self._currview = name
            self._mgr.LoadPerspective(self._viewset[name])
            self._mgr.Update()
            self.SavePerspectives()
            return True
        elif name == u"Default":
            self.AddPerspective(name)
        else:
            return False

    def SetPerspectiveById(self, per_id):
        """Sets the perspective using the given control id
        @param perId: id of requested perspective
        @return: whether perspective was set or not
        @rtype: bool

        """
        name = None
        for pos in range(self._menu.GetMenuItemCount()):
            item = self._menu.FindItemByPosition(pos)
            if per_id == item.GetId():
                name = item.GetLabel()
                break
        if name:
            return self.SetPerspective(name)
        else:
            return False
