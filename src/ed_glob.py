############################################################################
#    Copyright (C) 2007 by Cody Precord                                    #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
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
# FILE: ed_glob.py                                                         #
#                                                                          #
# AUTHOR: Cody Precord                                                     #
#                                                                          #
# SUMMARY:                                                                 #
#    This file contains variables that are or may be used in multiple      #
#   files and libraries within the project. Its pupose is to create a      #
#   globally accessable access point for all common variables in the       #
#   project.                                                               #
#                                                                          #
# METHODS:                                                                 #
#    None                                                                  #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#---- Project Info ----#
Author = __Author__  = u'Cody Precord'
version = __version__ = u'0.0.90'
prog_name = u'Editra'
home_page = u"http://editra.org"
contact_mail = u"staff@editra.org"
#---- End Project Info ----#

#---- Imported Libs/Objects ----#
from wx import NewId, ID_PREFERENCES
from wx import ID_ABOUT as wxID_ABOUT
from wx import ID_EXIT as wxID_EXIT
#---- Configuration Locations ----#

# Values set when main loads
CONFIG = { 
          'PROFILE_DIR' : "", 
          'PIXMAPS_DIR' : "",
          'MIME_DIR'    : "",
          'THEME_DIR'   : "",
          'LANG_DIR'    : "",
          'EXTERN_DIR'  : ""
}

#---- Object ID's ----#
# File Menu IDs
ID_NEW           = NewId()
ID_OPEN          = NewId()
ID_FHIST         = NewId()
ID_CLOSE         = NewId()
ID_SAVE          = NewId()
ID_SAVEAS        = NewId()
ID_SAVE_PROFILE  = NewId()
ID_LOAD_PROFILE  = NewId()
ID_PRINT         = NewId()
ID_PRINT_PRE     = NewId()
ID_PRINT_SU      = NewId()
ID_EXIT          = wxID_EXIT

# Edit Menu IDs
ID_UNDO          = NewId()
ID_REDO          = NewId()
ID_CUT           = NewId()
ID_COPY          = NewId()
ID_PASTE         = NewId()
ID_SELECTALL     = NewId()
ID_LINE_EDIT     = NewId()
ID_BOOKMARK      = NewId()
ID_ADD_BM        = NewId()
ID_DEL_BM        = NewId()
ID_DEL_ALL_BM    = NewId()
ID_CUT_LINE      = NewId()
ID_COPY_LINE     = NewId()
ID_JOIN_LINES    = NewId()
ID_TRANSPOSE     = NewId()
ID_FIND          = NewId()
ID_FIND_REPLACE  = NewId()
ID_QUICK_FIND    = NewId()
ID_PREF          = ID_PREFERENCES

# Prefrence Dlg Ids
ID_PREF_LANG     = NewId()
ID_PREF_AALIAS   = NewId()
ID_PREF_SYNTHEME = NewId()
ID_PREF_TABS     = NewId()
ID_PREF_TABW     = NewId()
ID_PREF_METAL    = NewId()
ID_PREF_FHIST    = NewId()
ID_PREF_WSIZE    = NewId()
ID_PREF_WPOS     = NewId()
ID_PREF_ICON     = NewId()
ID_PREF_ICONSZ   = NewId()
ID_PREF_MODE     = NewId()
ID_TRANSPARENCY  = NewId()

# View Menu IDs
ID_ZOOM_OUT      = NewId()
ID_ZOOM_IN       = NewId()
ID_ZOOM_NORMAL   = NewId()
ID_SHOW_EOL      = NewId()
ID_SHOW_WS       = NewId()
ID_INDENT_GUIDES = NewId()
ID_VIEW_TOOL     = NewId()

# Format Menu IDs
ID_FONT          = NewId()
ID_EOL_MODE      = NewId()
ID_EOL_MAC       = NewId()
ID_EOL_UNIX      = NewId()
ID_EOL_WIN       = NewId()
ID_WORD_WRAP     = NewId()
ID_INDENT        = NewId()
ID_UNINDENT      = NewId()
ID_NEXT_MARK     = NewId()
ID_PRE_MARK      = NewId()

# Settings Menu IDs
ID_SYNTAX        = NewId()
ID_SYN_ON        = NewId()
ID_SYN_OFF       = NewId()
ID_BRACKETHL     = NewId()
ID_KWHELPER      = NewId()
ID_LEXER         = NewId()

# Tool Menu IDs
ID_STYLE_EDIT    = NewId()

# Help Menu IDs
ID_ABOUT         = wxID_ABOUT
ID_HOMEPAGE      = NewId()
ID_CONTACT       = NewId()

# Misc IDs
ID_YES           = NewId()
ID_NO            = NewId()
ID_CANCEL        = NewId()
ID_COMMAND_LINE_OPEN = NewId()

# Statusbar IDs
SB_INFO          = 0
SB_ROWCOL        = 1

#---- Objects ----#

# Dictionary to hold the profile
# Always holds default settings incase profile loading fails or file
# is incorrecly formatted/missing values
PROFILE = {
           'ALPHA'      : 255,
           'AALIASING'  : True,
           'BRACKETHL'  : True,
           'DEFAULT'    : False,
           'KWHELPER'   : True,
           'EOL'        : 'Unix (\\n)',
           'FHIST_LVL'  : 5,
           'GUIDES'     : True,
           'ICONS'      : 'Stock',
           'ICON_SZ'    : (32,32),
           'LANG'       : 'Default',
           'MODE'       : 'CODE',
           'MYPROFILE'  : 'default.pp',
           'SHOW_EOL'   : False,
           'SYNTAX'     : True,
           'SYNTHEME'   : 'Default',
           'TABWIDTH'   : 8,
           'THEME'      : 'DEFAULT', 
           'TOOLBAR'    : True,
           'USETABS'    : True,
           'SHOW_WS'    : False,
           'WRAP'       : True,
           'SET_WSIZE'  : True,
           'WSIZE'      : (700, 450),
           'SET_WPOS'   : True
}

# Dictionary to map object ids to Profile keys
ID_2_PROF = {
             ID_PREF_AALIAS       : 'AALIASING',
             ID_BRACKETHL         : 'BRACKETHL',
             ID_KWHELPER          : 'KWHELPER',
             ID_EOL_MODE          : 'EOL',
             ID_PREF_FHIST        : 'FHIST_LVL',
             ID_INDENT_GUIDES     : 'GUIDES',
             ID_PREF_LANG         : 'LANG',
             ID_SYNTAX            : 'SYNTAX',
             ID_PREF_SYNTHEME     : 'SYNTHEME',
             ID_PREF_TABS         : 'USETABS',
             ID_PREF_TABW         : 'TABWIDTH',
             ID_SHOW_EOL          : 'SHOW_EOL',
             ID_SHOW_WS           : 'SHOW_WS',
             ID_TRANSPARENCY      : 'ALPHA',
             ID_WORD_WRAP         : 'WRAP',
             ID_PREF_METAL        : 'METAL',
             ID_PREF_WSIZE        : 'SET_WSIZE',
             ID_PREF_WPOS         : 'SET_WPOS',
             ID_PREF_ICON         : 'ICONS',
             ID_PREF_ICONSZ       : 'ICON_SZ',
             ID_PREF_MODE         : 'MODE'
}
