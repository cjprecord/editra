############################################################################
#    Copyright (C) 2007 by Cody Precord                                    #
#    cprecord@editra.org                                                   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
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
version = __version__ = u'0.0.83'
prog_name = u'Editra'
#---- End Project Info ----#

#---- Imported Libs ----#
from wx import stc #TODO Elimitate this some how perhaps populate the dictionary when the stc loads

#---- Configuration Locations ----#
# Values set when main loads
CONFIG = { 
          'PROFILE_DIR' : "", 
          'PIXMAPS_DIR' : "",
          'MIME_DIR'    : "",
          'LANG_DIR'    : "",
          'EXTERN_DIR'  : ""
}

#---- Object ID's ----#
# File Menu IDs
ID_NEW           = 100
ID_OPEN          = 101
ID_FHIST         = 102
ID_CLOSE         = 103
ID_SAVE          = 104
ID_SAVEAS        = 105
ID_SAVE_PROFILE  = 106
ID_LOAD_PROFILE  = 107
ID_PRINT         = 108
ID_EXIT          = 109

# Edit Menu IDs
ID_UNDO          = 200
ID_REDO          = 201
ID_CUT           = 202
ID_COPY          = 203
ID_PASTE         = 204
ID_SELECTALL     = 205
ID_FIND          = 206
ID_FIND_REPLACE  = 207
ID_PREF          = 208

# Prefrence Dlg Ids
ID_PREF_LANG     = 220
ID_PREF_AALIAS   = 221
ID_PREF_TABS     = 222
ID_PREF_TABW     = 223
ID_PREF_METAL    = 224
ID_PREF_FHIST    = 225
ID_PREF_WSIZE    = 226
ID_PREF_WPOS     = 227
ID_PREF_ICON     = 228

# View Menu IDs
ID_ZOOM_OUT      = 300
ID_ZOOM_IN       = 301
ID_ZOOM_NORMAL   = 302
ID_SHOW_WS       = 303
ID_VIEW_TOOL     = 304

# Format Menu IDs
ID_WORD_WRAP     = 400
ID_FONT          = 401

# Settings Menu IDs
ID_SYNTAX        = 500
ID_SYN_ON        = 501
ID_SYN_OFF       = 502
ID_INDENT_GUIDES = 503
ID_BRACKETHL     = 504
ID_KWHELPER      = 505
ID_LANG          = 506

# Language Menu (SUB of Settings) IDs
ID_LANG_ASM      = 600
ID_LANG_ASM68K   = 601
ID_LANG_BATCH    = 602
ID_LANG_C        = 603
ID_LANG_CSH      = 604
ID_LANG_CPP      = 605
ID_LANG_CSS      = 606
ID_LANG_H        = 607
ID_LANG_HTML     = 608
ID_LANG_JAVA     = 609
ID_LANG_JS       = 610
ID_LANG_KSH      = 611
ID_LANG_LISP     = 612
ID_LANG_MASM     = 613
ID_LANG_MAKE     = 614
ID_LANG_NASM     = 615
ID_LANG_NSIS     = 616
ID_LANG_PASCAL   = 617
ID_LANG_PERL     = 618
ID_LANG_PHP      = 619
ID_LANG_PS       = 620
ID_LANG_PYTHON   = 621
ID_LANG_RUBY     = 622
ID_LANG_SHELL    = 623
ID_LANG_SQL      = 624
ID_LANG_TEX      = 625
ID_LANG_VHDL     = 626
ID_LANG_VB       = 627
ID_LANG_XML      = 628

# Help Menu IDs
ID_ABOUT         = 700

# Misc IDs
ID_YES           = 10
ID_NO            = 11
ID_CANCEL        = 12
ID_COMMAND_LINE_OPEN = 13

# Statusbar IDs
SB_INFO          = 0
SB_ROWCOL        = 1

#---- Objects ----#
# Maps language ID's to Lexer Values
LANG_DICT = {ID_LANG_ASM : stc.STC_LEX_ASM, ID_LANG_BATCH : stc.STC_LEX_BATCH,
             ID_LANG_C : stc.STC_LEX_CPP, ID_LANG_CPP : stc.STC_LEX_CPP,
             ID_LANG_CSS : stc.STC_LEX_CSS, ID_LANG_H : stc.STC_LEX_CPP,
             ID_LANG_HTML : stc.STC_LEX_HTML, ID_LANG_JAVA : stc.STC_LEX_CPP,
             ID_LANG_LISP : stc.STC_LEX_LISP, 
             ID_LANG_MAKE : stc.STC_LEX_MAKEFILE,
             ID_LANG_NSIS : stc.STC_LEX_NSIS, 
             ID_LANG_PASCAL : stc.STC_LEX_PASCAL,
             ID_LANG_PERL : stc.STC_LEX_PERL, ID_LANG_PHP : stc.STC_LEX_HTML,
             ID_LANG_PS : stc.STC_LEX_PS, ID_LANG_PYTHON : stc.STC_LEX_PYTHON,
             ID_LANG_RUBY : stc.STC_LEX_RUBY, ID_LANG_SHELL : stc.STC_LEX_BASH,
             ID_LANG_SQL : stc.STC_LEX_MSSQL, ID_LANG_TEX : stc.STC_LEX_TEX,
             ID_LANG_VHDL : stc.STC_LEX_VHDL, ID_LANG_VB : stc.STC_LEX_VB
}

# Maps language ID's to File extensions
EXT_DICT = {ID_LANG_ASM : 'asm', ID_LANG_BATCH : 'bat',
            ID_LANG_C : 'c', ID_LANG_CPP : 'cpp',
            ID_LANG_CSS : 'css', ID_LANG_H : 'h',
            ID_LANG_HTML : 'html', ID_LANG_JAVA : 'java',
            ID_LANG_LISP : 'lisp', ID_LANG_MAKE : 'makefile',
            ID_LANG_NSIS : 'nsi', ID_LANG_PASCAL : 'p',
            ID_LANG_PERL : 'pl', ID_LANG_PHP : 'php',
            ID_LANG_PS : 'ps', ID_LANG_PYTHON : 'py',
            ID_LANG_RUBY : 'rb', ID_LANG_SHELL : 'sh',
            ID_LANG_SQL : 'sql', ID_LANG_TEX : 'tex',
            ID_LANG_VHDL : 'vhdl', ID_LANG_VB : 'vb',
            ID_LANG_XML : 'xml', ID_LANG_ASM68K : '68k',
            ID_LANG_MASM : 'masm', ID_LANG_NASM : 'nasm',
            ID_LANG_CSH : 'csh', ID_LANG_KSH : 'ksh',
            ID_LANG_JS : 'js'
}

# Dictionary to hold the profile
# Always holds default settings incase profile loading fails or file
# is incorrecly formatted/missing values
PROFILE = { 
           'AALIASING'  : True,
           'BRACKETHL'  : True,
           'DEFAULT'    : False,
           'KWHELPER'   : True,
           'FHIST_LVL'  : '5',
           'GUIDES'     : True,
           'ICONS'      : 'Stock',
           'LANG'       : 'Default', # Use System Default Language by default
           'MODE'       : 'DEBUG',
           'MYPROFILE'  : 'default.pp',
           'SYNTAX'     : True,
           'TABWIDTH'   : '8',
           'THEME'      : 'DEFAULT', 
           'TOOLBAR'    : True,
           'USETABS'    : True,
           'SHOW_WS'    : False,
           'WRAP'       : True,
           'SET_WSIZE'  : True,
           'WSIZE'      : (700, 450),
           'SET_WPOS'   : True
}

# Global localization object
# This is populated with 
#LOCALE = { 
#          'Current' : wx.LANGUAGE_DEFAULT,
#          'Previous' : wx.LANGUAGE_DEFAULT,
#          'FailSafe' : wx.LANGUAGE_DEFAULT
#}

# Dictionary to map object ids to Profile keys
ID_2_PROF = {
             ID_PREF_AALIAS       : 'AALIASING',
             ID_BRACKETHL         : 'BRACKETHL',
             ID_KWHELPER          : 'KWHELPER',
             ID_PREF_FHIST        : 'FHIST_LVL',
             ID_INDENT_GUIDES     : 'GUIDES',
             ID_PREF_LANG         : 'LANG',
             ID_SYNTAX            : 'SYNTAX',
             ID_PREF_TABS         : 'USETABS',
             ID_PREF_TABW         : 'TABWIDTH',
             ID_SHOW_WS           : 'SHOW_WS',
             ID_WORD_WRAP         : 'WRAP',
             ID_PREF_METAL        : 'METAL',
             ID_PREF_WSIZE        : 'SET_WSIZE',
             ID_PREF_WPOS         : 'SET_WPOS',
             ID_PREF_ICON         : 'ICONS'
}
