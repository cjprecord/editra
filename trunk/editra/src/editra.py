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

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import wx
import ed_glob
import util

#--------------------------------------------------------------------------#

#---- Load Configuration Information ----#

# 1. Set Non-Profile Dependant Resource location globals
ed_glob.CONFIG['PROFILE_DIR'] = util.ResolvConfigDir("profiles")
ed_glob.CONFIG['PIXMAPS_DIR'] = util.ResolvConfigDir("pixmaps")
ed_glob.CONFIG['MIME_DIR'] = util.ResolvConfigDir("pixmaps/mime")

# 2. Load Profile Settings
import profiler
if util.HasConfig():
    profiler.LoadProfile()
else:
    util.CreateConfigDir()
    profiler.LoadProfile()

# 3. Setup Language Settings
# TODO it is typically not a good idea to be changing the path like this
# Must set this after loading Profile so we know what language to use
ed_glob.CONFIG['LANG_DIR'] = util.ResolvConfigDir("language" + util.GetPathChar() + ed_glob.PROFILE['LANG'].lower())
if os.path.exists(ed_glob.CONFIG['LANG_DIR']) and ed_glob.PROFILE['LANG'].lower() != 'english':
    sys.path.insert(0,ed_glob.CONFIG['LANG_DIR'])
    import ed_lang
else:
    # External Language Resource is missing/notfound so use builtin from ed_glob instead
    pass

#---- End Configuration Setup ----#

# Now import main launch application
import ed_main

# Create Application
if ed_glob.PROFILE['MODE'] == u"DEBUG":
    EDITRA = wx.App()
else:
    EDITRA = wx.PySimpleApp()

# Create the Editor
FRAME = ed_main.MainWindow(None, wx.ID_ANY, ed_glob.PROFILE['WSIZE'], ed_glob.prog_name)

# Start Application
EDITRA.MainLoop()

