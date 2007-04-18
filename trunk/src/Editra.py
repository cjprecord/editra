#!/usr/bin/env python
############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and/or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

"""
#--------------------------------------------------------------------------#
# FILE:  Editra.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
#   This file holds the main method for running the editor.                #
#                                                                          #
# METHODS:                                                                 #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import gettext
import wx

# Make sure we can run properly before importing the rest
def CheckVersions():
    """Checks if the proper system libraries are available on the
    system.

    """
    REQUIRED_WX = "2.8" # or higher
    REQUIRED_PY = "2.4" # or higher
    REQUIRED_ENC = "Unicode"
    wxVer = "%d.%d" % (wx.MAJOR_VERSION, wx.MINOR_VERSION)
    pyVer = "%d.%d" % (sys.version_info[0], sys.version_info[1])
    wxEnc = wx.PlatformInfo[2].title()
    if wxEnc != REQUIRED_ENC:
        print ("\n!! It is suggested to use a Unicode build of wxPython "
               "when running Editra. \n!! You are using a %s build of wxPython "
               "and this may cause some runtime problems. \n!! Editra will try to "
               "launch now but if you experience problems you should install "
               "\n!! a Unicode build of wxPython and try again. \n") % wxEnc
    if wxVer < REQUIRED_WX or pyVer < REQUIRED_PY:
        msg = ("\nTo run properly Editra requires the following libraries to be installed:\n"
              "---------------------------------------\n"
              "| REQUIRED\t\t|\tFOUND |\n"
              "---------------------------------------\n"
              "Python: %s or higher\t|\t%s\n"
              "wxPython: %s or higher\t|\t%s\n\n"
              "Would you like to try anyway? [y/n]: ") % \
              (REQUIRED_PY, pyVer, REQUIRED_WX, wxVer)
        ret = raw_input(msg)
        if ret == 'n':
            exit()
        else:
            pass
# CheckVersions()

import ed_glob
import ed_i18n
import util
import dev_tool
import ed_main
import ed_art

#--------------------------------------------------------------------------#
# Global Variables

#--------------------------------------------------------------------------#
class Editra(wx.App):
    """The Editra Application"""
    def OnInit(self):
        """Initialize the Editor"""
        self._log = dev_tool.DEBUGP
        self._log("[main_info] Setting Locale/Language Settings")
        wx.ArtProvider.PushProvider(ed_art.ED_Art())
        
        #---- Bind Events ----#
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

        return True

    def MacOpenFile(self, filename):
        """Macintosh Specific code for opening files that are associated
        with the editor and double clicked on after the editor is already
        running.
        
        """
        window = self.GetTopWindow()
        if window != None:
            try:
                window.DoOpen(wx.ID_ANY, filename)
            finally:
                pass
        else:
            pass

    def OnActivate(self, evt):
        """Activation Event Handler"""
        if evt.GetActive():
            self._log("[main_app] [info] I'm Awake!!")
         #   if self._frame.CanSetTransparent():
         #       self._frame.SetTransparent(ed_glob.PROFILE['ALPHA'])
        else:
            self._log("[main_app] [info] Going to sleep")
          #  if self._frame.CanSetTransparent():
          #      self._frame.SetTransparent(int(.85 * ed_glob.PROFILE['ALPHA']))
        evt.Skip()

    def ReloadArtProvider(self):
        """Reloads the custom art provider onto the artprovider stack"""
        try:
            wx.ArtProvider.PopProvider()
        finally:
            wx.ArtProvider.PushProvider(ed_art.ED_Art())

    def GetLog(self):
        """Returns the logging function used by the app"""
        return self._log

def InitConfig():
    """Initializes the configuration data"""
    # 1. Set Resource location globals
    ed_glob.CONFIG['PROFILE_DIR'] = util.ResolvConfigDir("profiles")
    ed_glob.CONFIG['PIXMAPS_DIR'] = util.ResolvConfigDir("pixmaps")
    ed_glob.CONFIG['MIME_DIR'] = util.ResolvConfigDir(os.path.join("pixmaps", "mime"))
    ed_glob.CONFIG['THEME_DIR'] = util.ResolvConfigDir(os.path.join("pixmaps", "theme"))
    ed_glob.CONFIG['LANG_DIR'] = util.ResolvConfigDir("locale", True)
    ed_glob.CONFIG['STYLES_DIR'] = util.ResolvConfigDir("styles")
    ed_glob.CONFIG['SYS_STYLES_DIR'] = util.ResolvConfigDir("styles", True)
    ed_glob.CONFIG['TEST_DIR'] = util.ResolvConfigDir("test_data", True)
    if not util.HasConfigDir("cache"):
        util.MakeConfigDir("cache")
    ed_glob.CONFIG['CACHE_DIR'] = util.ResolvConfigDir("cache")

def Main():
    """Configures and Runs an instance of Editra"""
    # 1. Set Resource location globals
    InitConfig()

    # 2. Load Profile Settings
    import profiler
    PROFILE_UPDATED = False
    if util.HasConfigDir():
        if profiler.ProfileIsCurrent():
            profiler.LoadProfile()
        else:
            dev_tool.DEBUGP("[main_info] Updating Profile to current version")
            profiler.WriteProfile(profiler.GetProfileStr())
            profiler.LoadProfile()
            PROFILE_UPDATED = True
    else:
        util.CreateConfigDir()
        InitConfig()

    # 3. Create Application
    dev_tool.DEBUGP("[main_info] Initializing Application...")
    if ed_glob.PROFILE['MODE'] == u"GUI_DEBUG":
        EDITRA = Editra(True)
    else:
        EDITRA = Editra(False)

    # 4. Initialize the Language Settings
    langid = ed_i18n.GetLangId(ed_glob.PROFILE['LANG'])
    the_locale = wx.Locale(langid)
    the_locale.AddCatalogLookupPathPrefix(ed_glob.CONFIG['LANG_DIR'])
    the_locale.AddCatalog(ed_glob.prog_name)
    language = gettext.translation(ed_glob.prog_name, ed_glob.CONFIG['LANG_DIR'],
                                    [the_locale.GetCanonicalName()], fallback=True)
    language.install()

    if PROFILE_UPDATED:
        alert = wx.MessageBox(_("Your profile has been updated to the latest version"),
                              _("Profile Updated"))

    _frame = ed_main.MainWindow(None, wx.ID_ANY, ed_glob.PROFILE['WSIZE'], 
                                    ed_glob.prog_name, EDITRA.GetLog())
    EDITRA.SetTopWindow(_frame)

    # 5. Start Applications Main Loop
    dev_tool.DEBUGP("[main_info] Starting MainLoop...")
    EDITRA.MainLoop()

#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    Main()

