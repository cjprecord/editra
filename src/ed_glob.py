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
version = __version__ = u'0.1.28'
prog_name = u'Editra'
home_page = u"http://editra.org"
contact_mail = u"staff@editra.org"
#---- End Project Info ----#

#---- Imported Libs/Objects ----#
import wx

#---- Configuration Locations ----#
# Values set when main loads
CONFIG = {
          'CACHE_DIR'   : "",   # Holds temp data about documents
          'PROFILE_DIR' : "",   # User Profile Direcotry
          'PIXMAPS_DIR' : "",   # Graphics Directory
          'PLUGIN_DIR'  : "",   # User Plugin Dir
          'SYSPIX_DIR'  : "",   # Editras non user graphics
          'MIME_DIR'    : "",   # MIME type graphics
          'THEME_DIR'   : "",   # Theme Directory
          'LANG_DIR'    : "",   # Locale Data Directory
          'SYS_PLUGIN_DIR' : "", # Editra base plugin dir
          'SYS_STYLES_DIR' : "", # Editra base style sheets
          'TEST_DIR'    : "",   # Test data files dir
}

#---- Object ID's ----#
# File Menu IDs
ID_NEW           = wx.ID_NEW
ID_OPEN          = wx.ID_OPEN
ID_FHIST         = wx.NewId()
ID_CLOSE         = wx.ID_CLOSE
ID_CLOSEALL      = wx.ID_CLOSE_ALL
ID_SAVE          = wx.ID_SAVE
ID_SAVEAS        = wx.ID_SAVEAS
ID_SAVEALL       = wx.NewId()
ID_SAVE_PROFILE  = wx.NewId()
ID_LOAD_PROFILE  = wx.NewId()
ID_PRINT         = wx.ID_PRINT
ID_PRINT_PRE     = wx.ID_PREVIEW
ID_PRINT_SU      = wx.NewId()
ID_EXIT          = wx.ID_EXIT

# Edit Menu IDs
ID_UNDO          = wx.ID_UNDO
ID_REDO          = wx.ID_REDO
ID_CUT           = wx.ID_CUT
ID_COPY          = wx.ID_COPY
ID_PASTE         = wx.ID_PASTE
ID_SELECTALL     = wx.ID_SELECTALL
ID_LINE_EDIT     = wx.NewId()
ID_BOOKMARK      = wx.NewId()
ID_ADD_BM        = wx.ID_ADD
ID_DEL_BM        = wx.ID_DELETE
ID_DEL_ALL_BM    = wx.NewId()
ID_LINE_AFTER    = wx.NewId()
ID_LINE_BEFORE   = wx.NewId()
ID_CUT_LINE      = wx.NewId()
ID_COPY_LINE     = wx.NewId()
ID_JOIN_LINES    = wx.NewId()
ID_TRANSPOSE     = wx.NewId()
ID_FIND          = wx.ID_FIND
ID_FIND_REPLACE  = wx.ID_REPLACE
ID_QUICK_FIND    = wx.NewId()
ID_PREF          = wx.ID_PREFERENCES

# Prefrence Dlg Ids
ID_PREF_LANG     = wx.NewId()
ID_PREF_AALIAS   = wx.NewId()
ID_PREF_CHKMOD   = wx.NewId()
ID_PREF_EDGE     = wx.NewId()
ID_PREF_SYNTHEME = wx.NewId()
ID_PREF_TABS     = wx.NewId()
ID_PREF_TABW     = wx.NewId()
ID_PREF_METAL    = wx.NewId()
ID_PREF_FHIST    = wx.NewId()
ID_PREF_WSIZE    = wx.NewId()
ID_PREF_WPOS     = wx.NewId()
ID_PREF_ICON     = wx.NewId()
ID_PREF_ICONSZ   = wx.NewId()
ID_PREF_MODE     = wx.NewId()
ID_PRINT_MODE    = wx.NewId()
ID_TRANSPARENCY  = wx.NewId()
ID_PREF_SPOS     = wx.NewId()
ID_PREF_UPDATE_BAR = wx.NewId()

# View Menu IDs
ID_ZOOM_OUT      = wx.ID_ZOOM_OUT
ID_ZOOM_IN       = wx.ID_ZOOM_IN
ID_ZOOM_NORMAL   = wx.ID_ZOOM_100
ID_SHOW_EDGE     = wx.NewId()
ID_SHOW_EOL      = wx.NewId()
ID_SHOW_LN       = wx.NewId()
ID_SHOW_WS       = wx.NewId()
ID_PERSPECTIVES  = wx.NewId()
ID_INDENT_GUIDES = wx.NewId()
ID_VIEW_TOOL     = wx.NewId()
ID_GOTO_LINE     = wx.NewId()
ID_NEXT_MARK     = wx.ID_FORWARD
ID_PRE_MARK      = wx.ID_BACKWARD

# Format Menu IDs
ID_FONT          = wx.NewId()
ID_EOL_MODE      = wx.NewId()
ID_EOL_MAC       = wx.NewId()
ID_EOL_UNIX      = wx.NewId()
ID_EOL_WIN       = wx.NewId()
ID_WORD_WRAP     = wx.NewId()
ID_INDENT        = wx.ID_INDENT
ID_UNINDENT      = wx.ID_UNINDENT
ID_WS_FORMAT     = wx.NewId()
ID_SPACE_TO_TAB  = wx.NewId()
ID_TAB_TO_SPACE  = wx.NewId()
ID_TRIM_WS       = wx.NewId()
ID_COMMENT       = wx.NewId()
ID_UNCOMMENT     = wx.NewId()

# Settings Menu IDs
ID_AUTOCOMP      = wx.NewId()
ID_AUTOINDENT    = wx.NewId()
ID_SYNTAX        = wx.NewId()
ID_SYN_ON        = wx.NewId()
ID_SYN_OFF       = wx.NewId()
ID_FOLDING       = wx.NewId()
ID_BRACKETHL     = wx.NewId()
ID_LEXER         = wx.NewId()

# Tool Menu IDs
ID_KWHELPER      = wx.NewId()
ID_PLUGMGR       = wx.NewId()
ID_STYLE_EDIT    = wx.ID_EDIT
ID_MACRO_START   = wx.NewId()
ID_MACRO_STOP    = wx.NewId()
ID_MACRO_PLAY    = wx.NewId()
ID_GENERATOR     = wx.NewId()
ID_HTML_GEN      = wx.NewId()
ID_TEX_GEN       = wx.NewId()
ID_RTF_GEN       = wx.NewId()

# Help Menu IDs
ID_ABOUT         = wx.ID_ABOUT
ID_HOMEPAGE      = wx.ID_HOME
ID_CONTACT       = wx.NewId()

# Misc IDs
ID_APP_SPLASH        = wx.NewId()
ID_BIN_FILE          = wx.NewId()
ID_CDROM             = wx.NewId()
ID_COMMAND_LINE_OPEN = wx.NewId()
ID_COMMAND_BAR       = wx.NewId()
ID_COMPUTER          = wx.NewId()
ID_DOWNLOAD_DLG      = wx.NewId()
ID_FILE              = wx.ID_FILE
ID_FLOPPY            = wx.NewId()
ID_FOLDER            = wx.NewId()
ID_HARDDISK          = wx.NewId()
ID_PLUGIN_CFG        = wx.NewId()
ID_PLUGIN_DL         = wx.NewId()
ID_PLUGIN_INST       = wx.NewId()
ID_USB               = wx.NewId()

# Statusbar IDs
SB_INFO          = 0
SB_ROWCOL        = 1

#---- Objects ----#

# Dictionary to hold the profile
# Always holds default settings incase profile loading fails or file
# is incorrecly formatted/missing values
PROFILE = {
           'ALPHA'      : 255,              # Transparency level
           'AALIASING'  : True,             # Use Anti-Aliasing if availble
           'APPSPLASH'  : True,             # Show splash at startup
           'AUTO_COMP'  : True,             # Use Auto-comp if available
           'AUTO_INDENT': True,             # Use Auto Indent
           'BRACKETHL'  : True,             # Use bracket highlighting
           'CHECKMOD'   : True,             # Auto check file for file modifications
           'CODE_FOLD'  : True,             # Use code folding
           'DEFAULT'    : False,            # No longer used I believe
           'DEFAULT_VIEW' : 'Default',      # Default Perspective
           'EDGE'       : 80,               # Edge guide column
           'EOL'        : 'Unix (\\n)',     # EOL mode
           'FHIST_LVL'  : 5,                # Filehistory length (9 is max)
           'GUIDES'     : True,             # Use Indentation guides
           'ICONS'      : 'Nuovo',          # Icon Theme
           'ICON_SZ'    : (24,24),          # Toolbar Icon Size
           'LANG'       : 'Default',        # UI language
           'MODE'       : 'CODE',           # Overall editor mode
           'MYPROFILE'  : 'default.pp',     # Path to profile file
           'PRINT_MODE' : 'BLACK/WHITE',    # Printer rendering mode
           'SAVE_POS'   : True,             # Remember Carat positions
           'SHOW_EDGE'  : True,             # Show Edge Guide
           'SHOW_EOL'   : False,            # Show EOL markers
           'SHOW_LN'    : True,             # Show Line Numbers
           'SYNTAX'     : True,             # Use Syntax Highlighting
           'SYNTHEME'   : 'Default',        # Syntax Highlight color scheme
           'TABWIDTH'   : 8,                # Tab width
           'THEME'      : 'DEFAULT',        # For future use
           'TOOLBAR'    : True,             # Show Toolbar
           'USETABS'    : True,             # Use tabs instead of spaces
           'SHOW_WS'    : False,            # Show whitespace markers
           'WRAP'       : True,             # Use Wordwrap
           'SET_WSIZE'  : True,             # Remember mainwindow size on exit
           'WSIZE'      : (700, 450),       # Mainwindow size
           'SET_WPOS'   : True              # Remember window position
}

# Dictionary to map object ids to Profile keys
ID_2_PROF = {
             ID_PREF_AALIAS       : 'AALIASING',
             ID_APP_SPLASH        : 'APPSPLASH',
             ID_AUTOCOMP          : 'AUTO_COMP',
             ID_AUTOINDENT        : 'AUTO_INDENT',
             ID_BRACKETHL         : 'BRACKETHL',
             ID_PREF_CHKMOD       : 'CHECKMOD',
             ID_FOLDING           : 'CODE_FOLD',
             ID_PERSPECTIVES      : 'DEFAULT_VIEW',
             ID_KWHELPER          : 'KWHELPER',
             ID_EOL_MODE          : 'EOL',
             ID_PREF_FHIST        : 'FHIST_LVL',
             ID_INDENT_GUIDES     : 'GUIDES',
             ID_PREF_LANG         : 'LANG',
             ID_SYNTAX            : 'SYNTAX',
             ID_PREF_SYNTHEME     : 'SYNTHEME',
             ID_PREF_TABS         : 'USETABS',
             ID_PREF_TABW         : 'TABWIDTH',
             ID_SHOW_EDGE         : 'SHOW_EDGE',
             ID_SHOW_EOL          : 'SHOW_EOL',
             ID_SHOW_LN           : 'SHOW_LN',
             ID_SHOW_WS           : 'SHOW_WS',
             ID_TRANSPARENCY      : 'ALPHA',
             ID_WORD_WRAP         : 'WRAP',
             ID_PREF_EDGE         : 'EDGE',
             ID_PREF_METAL        : 'METAL',
             ID_PREF_SPOS         : 'SAVE_POS',
             ID_PREF_WSIZE        : 'SET_WSIZE',
             ID_PREF_WPOS         : 'SET_WPOS',
             ID_PREF_ICON         : 'ICONS',
             ID_PREF_ICONSZ       : 'ICON_SZ',
             ID_PREF_MODE         : 'MODE',
             ID_PRINT_MODE        : 'PRINT_MODE'
}

# Default Plugins
DEFAULT_PLUGINS = ("generator.Html", "generator.LaTeX", "generator.Rtf")
