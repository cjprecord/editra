###############################################################################
# Name: ed_glob.py                                                            #
# Purpose: Global IDs/objects used throughout Editra                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_glob.py                                                         #
#                                                                          #
# @author: Cody Precord                                                    #
#                                                                          #
# @summary:                                                                #
#   This file contains variables that are or may be used in multiple       #
#   files and libraries within the project. Its pupose is to create a      #
#   globally accessable access point for all common variables in the       #
#   project.                                                               #
#                                                                          #
# METHODS:                                                                 #
#    None                                                                  #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

__all__ = [ 'CONFIG', 'SB_INFO', 'SB_ROWCOL', 'VERSION', 'PROG_NAME',
            'ID_NEW', 'ID_OPEN', 'ID_CLOSE', 'ID_CLOSEALL', 'ID_SAVE',
            'ID_SAVEAS', 'ID_SAVEALL', 'ID_SAVE_PROFILE', 'ID_LOAD_PROFILE',
            'ID_PRINT', 'ID_PRINT_PRE', 'ID_PRINT_SU', 'ID_EXIT', 'ID_UNDO',
            'ID_REDO', 'ID_CUT', 'ID_COPY', 'ID_PASTE', 'ID_SELECTALL',
            'ID_ADD_BM', 'ID_DEL_BM',  'ID_DEL_ALL_BM', 'ID_LINE_AFTER',
            'ID_LINE_BEFORE', 'ID_CUT_LINE', 'ID_COPY_LINE', 'ID_JOIN_LINES',
            'ID_TRANSPOSE', 'ID_FIND', 'ID_FIND_REPLACE', 'ID_QUICK_FIND',
            'ID_PREF', 'ID_ZOOM_OUT', 'HOME_PAGE', 'CONTACT_MAIL',
            'ID_ZOOM_IN', 'ID_ZOOM_NORMAL', 'ID_SHOW_EDGE', 'ID_SHOW_EOL',
            'ID_SHOW_LN', 'ID_SHOW_WS', 'ID_PERSPECTIVES', 'ID_INDENT_GUIDES', 
            'ID_VIEW_TOOL', 'ID_GOTO_LINE', 'ID_NEXT_MARK', 'ID_PRE_MARK', 
            'ID_FONT', 'ID_EOL_MODE', 'ID_EOL_MAC', 'ID_EOL_UNIX', 'ID_EOL_WIN',
            'ID_WORD_WRAP', 'ID_INDENT',  'ID_UNINDENT', 'ID_TO_UPPER', 
            'ID_TO_LOWER', 'ID_SPACE_TO_TAB', 'ID_TAB_TO_SPACE', 'ID_TRIM_WS', 
            'ID_COMMENT', 'ID_UNCOMMENT', 'ID_AUTOCOMP', 'ID_AUTOINDENT', 
            'ID_SYNTAX', 'ID_FOLDING', 'ID_BRACKETHL', 'ID_LEXER', 
            'ID_KWHELPER', 'ID_PLUGMGR', 'ID_STYLE_EDIT', 'ID_MACRO_START', 
            'ID_MACRO_STOP', 'ID_MACRO_PLAY', 'ID_ABOUT', 'ID_HOMEPAGE', 
            'ID_CONTACT', 'ID_COMMAND_BAR', 'ID_DOCUMENTATION', 'ID_COMMAND',
            'ID_CLOSE_WINDOW' 
]

#---- Project Info ----#
AUTHOR = u'Cody Precord'
VERSION = u'0.2.0'
PROG_NAME = u'Editra'
HOME_PAGE = u"http://editra.org"
CONTACT_MAIL = u"staff@editra.org"
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
          'THEME_DIR'   : "",   # Theme Directory
          'LANG_DIR'    : "",   # Locale Data Directory
          'SYS_PLUGIN_DIR' : "", # Editra base plugin dir
          'SYS_STYLES_DIR' : "", # Editra base style sheets
          'TEST_DIR'    : "",   # Test data files dir
}

DEBUG = False

#---- Object ID's ----#
# File Menu IDs
ID_NEW           = wx.ID_NEW
ID_NEW_WINDOW    = wx.NewId()
ID_OPEN          = wx.ID_OPEN
ID_FHIST         = wx.NewId()
ID_CLOSE         = wx.ID_CLOSE
ID_CLOSEALL      = wx.ID_CLOSE_ALL
ID_CLOSE_WINDOW  = wx.NewId()
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
# Using the system ids automatically disables the menus items
# when the dialog is open which is not wanted
if wx.Platform == '__WXMAC__':
    ID_FIND = wx.NewId()
    ID_FIND_REPLACE = wx.NewId()
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
ID_SESSION       = wx.NewId()

# View Menu IDs
ID_ZOOM_OUT      = wx.ID_ZOOM_OUT
ID_ZOOM_IN       = wx.ID_ZOOM_IN
ID_ZOOM_NORMAL   = wx.ID_ZOOM_100
ID_SHOW_EDGE     = wx.NewId()
ID_SHOW_EOL      = wx.NewId()
ID_SHOW_LN       = wx.NewId()
ID_SHOW_WS       = wx.NewId()
ID_SHOW_SHELF    = wx.NewId()
ID_PERSPECTIVES  = wx.NewId()
ID_INDENT_GUIDES = wx.NewId()
ID_VIEW_TOOL     = wx.NewId()
ID_SHELF         = wx.NewId()
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
ID_TO_UPPER      = wx.NewId()
ID_TO_LOWER      = wx.NewId()
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
ID_COMMAND       = wx.NewId()
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
ID_DOCUMENTATION = wx.NewId()
ID_CONTACT       = wx.NewId()

# Misc IDs
ID_APP_SPLASH        = wx.NewId()
ID_BIN_FILE          = ID_COMMAND
ID_CDROM             = wx.NewId()
ID_COMMAND_LINE_OPEN = wx.NewId()
ID_COMMAND_BAR       = wx.NewId()
ID_COMPUTER          = wx.NewId()
ID_DELETE            = wx.NewId()
ID_DOCPROP           = wx.NewId()
ID_DOWN              = wx.ID_DOWN
ID_DOWNLOAD_DLG      = wx.NewId()
ID_FILE              = wx.ID_FILE
ID_FLOPPY            = wx.NewId()
ID_FOLDER            = wx.NewId()
ID_HARDDISK          = wx.NewId()
ID_PACKAGE           = wx.NewId()
ID_REPORTER          = wx.NewId()
ID_THEME             = wx.NewId()
ID_USB               = wx.NewId()
ID_UP                = wx.ID_UP
ID_VI_MODE           = wx.NewId()
ID_WEB               = wx.NewId()

# Statusbar IDs
SB_INFO          = 0
SB_BUFF          = 1
SB_ROWCOL        = 2

#---- Objects ----#

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
             ID_REPORTER          : 'REPORTER',
             ID_SYNTAX            : 'SYNTAX',
             ID_PREF_SYNTHEME     : 'SYNTHEME',
             ID_PREF_TABS         : 'USETABS',
             ID_PREF_TABW         : 'TABWIDTH',
             ID_SESSION           : 'SAVE_SESSION',
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
             ID_PRINT_MODE        : 'PRINT_MODE',
             ID_NEW_WINDOW        : 'OPEN_NW',
             ID_VI_MODE           : 'VI_EMU'
}

# Default Plugins
DEFAULT_PLUGINS = ("generator.Html", "generator.LaTeX", "generator.Rtf",
                   "iface.Shelf", "ed_theme.TangoTheme")
