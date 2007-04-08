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
import ed_glob
import ed_i18n
import util
import dev_tool
import ed_main

#--------------------------------------------------------------------------#
class Editra(wx.App):
    """The Editra Application"""
    def OnInit(self):
        """Initialize the Editor"""
        self._log = dev_tool.DEBUGP
        self._log("[main_info] Setting Locale/Language Settings")

        #---- Bind Events ----#
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

        return True

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

