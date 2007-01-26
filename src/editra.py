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
# FILE:  editra.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
#   This file is the launcher for the editor. It sets up the configuration #
# options and starts the program.                                          #
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

#--------------------------------------------------------------------------#

#---- Load Configuration Information ----#

# 1. Set Resource location globals
ed_glob.CONFIG['PROFILE_DIR'] = util.ResolvConfigDir("profiles")
ed_glob.CONFIG['PIXMAPS_DIR'] = util.ResolvConfigDir("pixmaps")
ed_glob.CONFIG['MIME_DIR'] = util.ResolvConfigDir("pixmaps/mime")
ed_glob.CONFIG['LANG_DIR'] = util.ResolvConfigDir("locale")

# 2. Load Profile Settings
import profiler
if util.HasConfig():
    profiler.LoadProfile()
else:
    util.CreateConfigDir()
    profiler.LoadProfile()

# 3. Create Application
if ed_glob.PROFILE['MODE'] == u"DEBUG":
    EDITRA = wx.App(False)
else:
    EDITRA = wx.App(False)

# 4. Set up language settings
langid = ed_i18n.GetLangId(ed_glob.PROFILE['LANG'])
the_locale = wx.Locale(langid)
the_locale.AddCatalogLookupPathPrefix(ed_glob.CONFIG['LANG_DIR'])
the_locale.AddCatalog(ed_glob.prog_name)
language = gettext.translation(ed_glob.prog_name, ed_glob.CONFIG['LANG_DIR'],
                                [the_locale.GetCanonicalName()], fallback=True)
language.install()

# 5. Now import main launch application
import ed_main

# 6. Create the Editor
FRAME = ed_main.MainWindow(None, wx.ID_ANY, ed_glob.PROFILE['WSIZE'], ed_glob.prog_name)

# 7. Start Applications Main Loop
EDITRA.MainLoop()

