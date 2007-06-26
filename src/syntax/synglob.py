###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
#                                                                             #
#    Editra is free software; you can redistribute it and#or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    Editra is distributed in the hope that it will be useful,                #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program; if not, write to the                            #
#    Free Software Foundation, Inc.,                                          #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                #
###############################################################################

"""
#-----------------------------------------------------------------------------#
# FILE: synglob.py                                                            #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Profides configuration and basic API functionality to all the syntax        #
# modules. It also acts more or less as a configuration file for the syntax   #
# managment code.                                                             #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependencies
import wx
import wx.stc as stc

#-----------------------------------------------------------------------------#

#---- Language Identifiers Keys ----#
# Used for specifying what dialect/keyword set to load for a specific lexer

#---- Use LEX_NULL ----#
ID_LANG_TXT  = wx.NewId()
LANG_TXT = u'Plain Text'

#---- Use LEX_ADA ----#
ID_LANG_ADA = wx.NewId()
LANG_ADA = u'Ada'

#---- Use LEX_ASM ----#
ID_LANG_ASM  = wx.NewId()
LANG_ASM = u'Assembly Code'
ID_LANG_68K  = wx.NewId()
LANG_68K = u'68k Assembly'
ID_LANG_MASM = wx.NewId()
LANG_MASM = u'MASM'
ID_LANG_NASM = wx.NewId()
LANG_NASM = u'Netwide Assembler'

# Use LEX_BASH
ID_LANG_BOURNE = wx.NewId()
LANG_BOURNE = u'Bourne Shell Script'
ID_LANG_BASH   = wx.NewId()
LANG_BASH = u'Bash Shell Script'
ID_LANG_CSH    = wx.NewId()
LANG_CSH = u'C-Shell Script'
ID_LANG_KSH    = wx.NewId()
LANG_KSH = u'Korn Shell Script'

# Use LEX_CPP
ID_LANG_C    = wx.NewId()
LANG_C = u'C'
ID_LANG_CPP  = wx.NewId()
LANG_CPP = u'CPP'
ID_LANG_JAVA = wx.NewId()
LANG_JAVA = u'Java'

# Use LEX_CSS
ID_LANG_CSS = wx.NewId()
LANG_CSS = u'Cascading Style Sheet'
ID_LANG_ESS = wx.NewId()
LANG_ESS = u'Editra Style Sheet'

# Use LEX_F77
ID_LANG_F77 = wx.NewId()
LANG_F77 = u'Fortran 77'

# Use LEX_FORTRAN
ID_LANG_F95 = wx.NewId()
LANG_F95 = u'Fortran 95'

# Use LEX_HTML
ID_LANG_HTML = wx.NewId()
LANG_HTML = u'HTML'
ID_LANG_JS   = wx.NewId()
LANG_JS = u'JavaScript'
ID_LANG_VBS  = wx.NewId()
LANG_VBS = u'VB Script'
ID_LANG_PHP  = wx.NewId()
LANG_PHP = u'PHP'
ID_LANG_XML  = wx.NewId()
LANG_XML = u'XML'
ID_LANG_SGML = wx.NewId()

# Use LEX_LISP
ID_LANG_LISP = wx.NewId()
LANG_LISP = u'Lisp'

# Use LEX_LUA
ID_LANG_LUA = wx.NewId()
LANG_LUA = u'Lua'

# Use LEX_MSSQL (Microsoft SQL)
ID_LANG_MSSQL = wx.NewId()
LANG_MSSQL = u'Microsoft SQL'

# Use LEX_NSIS
ID_LANG_NSIS = wx.NewId()
LANG_NSIS = u'Nullsoft Installer Script'

# Use LEX_PASCAL
ID_LANG_PASCAL = wx.NewId()
LANG_PASCAL = u'Pascal'

# Use LEX_PERL
ID_LANG_PERL = wx.NewId()
LANG_PERL = u'Perl'

# Use LEX_PS
ID_LANG_PS = wx.NewId()
LANG_PS = u'Postscript'

# Use LEX_PYTHON 
ID_LANG_PYTHON = wx.NewId()
LANG_PYTHON = u'Python'

# Use LEX_RUBY
ID_LANG_RUBY = wx.NewId()
LANG_RUBY = u'Ruby'

# Use LEX_SMALLTALK
ID_LANG_ST = wx.NewId()
LANG_ST = u'Smalltalk'

# Use LEX_SQL (PL/SQL, SQL*Plus)
ID_LANG_SQL = wx.NewId()
LANG_SQL = u'SQL'

# Use LEX_TCL
ID_LANG_TCL  = wx.NewId()
LANG_TCL = u'Tcl/Tk'

# Use LEX_TEX
ID_LANG_TEX = wx.NewId()
LANG_TEX = u'Tex'
ID_LANG_LATEX = wx.NewId()
LANG_LATEX = u'LaTeX'

# Use LEX_VB
ID_LANG_VB = wx.NewId()
LANG_VB = u'Visual Basic'

# Use LEX_VHDL
ID_LANG_VHDL = wx.NewId()
LANG_VHDL = u'VHDL'

# Use LEX_OTHER (Batch, Makefile)
ID_LANG_BATCH = wx.NewId()
LANG_BATCH = u'DOS Batch Script'
ID_LANG_MAKE  = wx.NewId()
LANG_MAKE = u'Makefile'

#---- End Language Identifier Keys ----#

# Default extensions to file type map
EXT_MAP = {
           '68k asm'            : LANG_68K,
           'ada adb ads a'      : LANG_ADA,
           'bsh sh configure'   : LANG_BASH,
           'bat cmd'            : LANG_BATCH,
           'c h'                : LANG_C,
           'cc c++ cpp cxx hh h++ hpp hxx' : LANG_CPP,
           'csh'                : LANG_CSH,
           'css'                : LANG_CSS,
           'ess'                : LANG_ESS,
           'f for'              : LANG_F77,
           'f90 f95 f2k fpp'    : LANG_F95,
           'ksh'                : LANG_KSH,
           'java'               : LANG_JAVA,
           'js'                 : LANG_JS,
           'htm html shtm shtml xhtml' : LANG_HTML,
           'aux tex sty'        : LANG_LATEX,
           'cl lisp lsp'        : LANG_LISP,
           'lua'                : LANG_LUA,
           'mak makefile'       : LANG_MAKE,
           'masm'               : LANG_MASM,
           'mssql'              : LANG_MSSQL,
           'nasm'               : LANG_NASM,
           'nsi'                : LANG_NSIS,
           'dfm dpk dpr inc p pas pp' : LANG_PASCAL,
           'cgi pl pm pod'      : LANG_PERL,
           'php php3 phtml phtm' : LANG_PHP,
           'ai ps'              : LANG_PS,
           'py pyw python'      : LANG_PYTHON,
           'rb rbw rbx'         : LANG_RUBY,
           'sql'                : LANG_SQL,
           'st'                 : LANG_ST,
           'itcl tcl tk'        : LANG_TCL,
           'txt'                : LANG_TXT,
           'bas cls ctl frm vb' : LANG_VB,
           'vh vhdl'            : LANG_VHDL,
           'axl dtd plist rdf svg xml xrc xsd xsl xslt xul' : LANG_XML
          }

# Maps file types to syntax definitions
LANG_MAP = {LANG_68K    : (ID_LANG_68K,    stc.STC_LEX_ASM,      'asm68k'),
            LANG_ADA    : (ID_LANG_ADA,    stc.STC_LEX_ADA,      'ada'),
            LANG_BASH   : (ID_LANG_BASH,   stc.STC_LEX_BASH,     'sh'),
            LANG_BATCH  : (ID_LANG_BATCH,  stc.STC_LEX_BATCH,    'batch'),
            LANG_C      : (ID_LANG_C,      stc.STC_LEX_CPP,      'cpp'),
            LANG_CPP    : (ID_LANG_CPP,    stc.STC_LEX_CPP,      'cpp'),
            LANG_CSH    : (ID_LANG_CSH,    stc.STC_LEX_BASH,     'sh'),
            LANG_CSS    : (ID_LANG_CSS,    stc.STC_LEX_CSS,      'css'),
            LANG_ESS    : (ID_LANG_ESS,    stc.STC_LEX_CSS,      'editra_ss'),
            LANG_F77    : (ID_LANG_F77,    stc.STC_LEX_F77,      'fortran'),
            LANG_F95    : (ID_LANG_F95,    stc.STC_LEX_FORTRAN,  'fortran'),
            LANG_HTML   : (ID_LANG_HTML,   stc.STC_LEX_HTML,     'html'),
            LANG_JAVA   : (ID_LANG_JAVA,   stc.STC_LEX_CPP,      'java'),
            LANG_JS     : (ID_LANG_JS,     stc.STC_LEX_CPP,      'javascript'), 
            LANG_KSH    : (ID_LANG_KSH,    stc.STC_LEX_BASH,     'sh'),
            LANG_LATEX  : (ID_LANG_LATEX,  stc.STC_LEX_LATEX,    'latex'),
            LANG_LISP   : (ID_LANG_LISP,   stc.STC_LEX_LISP,     'lisp'),
            LANG_LUA    : (ID_LANG_LUA,    stc.STC_LEX_LUA,      'lua'),
            LANG_MAKE   : (ID_LANG_MAKE,   stc.STC_LEX_MAKEFILE, 'make'),
            LANG_MASM   : (ID_LANG_MASM,   stc.STC_LEX_ASM,      'masm'),
            LANG_MSSQL  : (ID_LANG_MSSQL,  stc.STC_LEX_MSSQL,    'mssql'),
            LANG_NASM   : (ID_LANG_NASM,   stc.STC_LEX_ASM,      'nasm'),
            LANG_NSIS   : (ID_LANG_NSIS,   stc.STC_LEX_NSIS,     'nsis'),
            LANG_PASCAL : (ID_LANG_PASCAL, stc.STC_LEX_PASCAL,   'pascal'),
            LANG_PERL   : (ID_LANG_PERL,   stc.STC_LEX_PERL,     'perl'),
            LANG_PHP    : (ID_LANG_PHP,    stc.STC_LEX_HTML,     'php'),
            LANG_PS     : (ID_LANG_PS,     stc.STC_LEX_PS,       'postscript'),
            LANG_PYTHON : (ID_LANG_PYTHON, stc.STC_LEX_PYTHON,   'python'),
            LANG_RUBY   : (ID_LANG_RUBY,   stc.STC_LEX_RUBY,     'ruby'),
            LANG_SQL    : (ID_LANG_SQL,    stc.STC_LEX_SQL,      'sql'),
            LANG_ST     : (ID_LANG_ST,     stc.STC_LEX_SMALLTALK, 'smalltalk'),
            LANG_TCL    : (ID_LANG_TCL,    stc.STC_LEX_TCL,      'tcl'),
            LANG_TXT    : (ID_LANG_TXT,    stc.STC_LEX_NULL,     None),
            LANG_VB     : (ID_LANG_VB,     stc.STC_LEX_VB,       'visualbasic'),
            LANG_VHDL   : (ID_LANG_VHDL,   stc.STC_LEX_VHDL,     'vhdl'),
            LANG_XML    : (ID_LANG_XML,    stc.STC_LEX_XML,      'xml')
            }

# Maps language ID's to File Types
# Used when manually setting lexer from a menu/dialog
ID_MAP = {ID_LANG_68K    : LANG_68K,    ID_LANG_ADA   : LANG_ADA, 
          ID_LANG_ASM    : LANG_ASM,    ID_LANG_BASH  : LANG_BASH, 
          ID_LANG_BATCH  : LANG_BATCH,  ID_LANG_C     : LANG_C, 
          ID_LANG_CPP    : LANG_CPP,    ID_LANG_CSH   : LANG_CSH, 
          ID_LANG_CSS    : LANG_CSS,    ID_LANG_ESS   : LANG_ESS,
          ID_LANG_F77    : LANG_F77,    ID_LANG_F95   : LANG_F95, 
          ID_LANG_HTML   : LANG_HTML,   ID_LANG_JAVA  : LANG_JAVA, 
          ID_LANG_JS     : LANG_JS,     ID_LANG_KSH   : LANG_KSH,
          ID_LANG_LATEX  : LANG_LATEX,  ID_LANG_LISP  : LANG_LISP, 
          ID_LANG_LUA    : LANG_LUA,    ID_LANG_MAKE  : LANG_MAKE, 
          ID_LANG_MASM   : LANG_MASM,   ID_LANG_MSSQL : LANG_MSSQL, 
          ID_LANG_NASM   : LANG_MASM,   ID_LANG_NSIS  : LANG_NSIS, 
          ID_LANG_PASCAL : LANG_PASCAL, ID_LANG_PERL  : LANG_PERL, 
          ID_LANG_PHP    : LANG_PHP,    ID_LANG_PS    : LANG_PS, 
          ID_LANG_PYTHON : LANG_PYTHON, ID_LANG_RUBY  : LANG_RUBY, 
          ID_LANG_SQL    : LANG_SQL,    ID_LANG_ST    : LANG_ST, 
          ID_LANG_VB     : LANG_VB,     ID_LANG_VHDL  : LANG_VHDL, 
          ID_LANG_TCL    : LANG_TCL,    ID_LANG_TXT   : LANG_TXT, 
          ID_LANG_XML    : LANG_XML
}

# Maps file types to Lexer values
FILE_LEXERS = { LANG_ADA    : stc.STC_LEX_ADA,
                LANG_ASM    : stc.STC_LEX_ASM,
                LANG_BASH   : stc.STC_LEX_BASH,
                LANG_BATCH  : stc.STC_LEX_BATCH,
                LANG_C      : stc.STC_LEX_CPP,
                LANG_CPP    : stc.STC_LEX_CPP,
                LANG_CSS    : stc.STC_LEX_CSS,
                LANG_JS     : stc.STC_LEX_HTML,
                LANG_HTML   : stc.STC_LEX_HTML,
                LANG_PHP    : stc.STC_LEX_HTML,
                LANG_LATEX  : stc.STC_LEX_LATEX,
                LANG_LUA    : stc.STC_LEX_LUA,
                LANG_LISP   : stc.STC_LEX_LISP,
                LANG_MAKE   : stc.STC_LEX_MAKEFILE,
                LANG_MSSQL  : stc.STC_LEX_MSSQL,
                LANG_NSIS   : stc.STC_LEX_NSIS,
                LANG_TXT    : stc.STC_LEX_NULL,
                LANG_PASCAL : stc.STC_LEX_PASCAL,
                LANG_PERL   : stc.STC_LEX_PERL,
                LANG_PS     : stc.STC_LEX_PS,
                LANG_PYTHON : stc.STC_LEX_PYTHON,
                LANG_RUBY   : stc.STC_LEX_RUBY,
                LANG_ST     : stc.STC_LEX_SMALLTALK,
                LANG_SQL    : stc.STC_LEX_SQL,
                LANG_VB     : stc.STC_LEX_VB,
                LANG_VHDL   : stc.STC_LEX_VHDL,
                LANG_XML    : stc.STC_LEX_XML,
               } 

# Map Lexers to Module names
LEX_MODULES = {stc.STC_LEX_ADA      : ['ada'], 
               stc.STC_LEX_ASM      : ['asm', 'asm68k', 'masm', 'nasm'],
               stc.STC_LEX_BASH     : ['sh'],
               stc.STC_LEX_BATCH    : ['bat'],
               stc.STC_LEX_CPP      : ['cpp'],
               stc.STC_LEX_CSS      : ['css', 'editra_ss'],
               stc.STC_LEX_HTML     : ['javascript', 'html', 'php'],
               stc.STC_LEX_TEX      : ['latex'],
               stc.STC_LEX_LISP     : ['lisp'],
               stc.STC_LEX_LUA      : ['lua'],
               stc.STC_LEX_MAKEFILE : ['make'],
               stc.STC_LEX_MSSQL    : ['mssql'],
               stc.STC_LEX_NSIS     : ['nsis'],
               stc.STC_LEX_NULL     : None,
               stc.STC_LEX_PASCAL   : ['pascal'],
               stc.STC_LEX_PERL     : ['perl'],
               stc.STC_LEX_PS       : ['postscript'],
               stc.STC_LEX_PYTHON   : ['python'],
               stc.STC_LEX_RUBY     : ['ruby'],
               stc.STC_LEX_SMALLTALK: ['smalltalk'],
               stc.STC_LEX_SQL      : ['sql'],
               stc.STC_LEX_VB       : ['visualbasic'],
               stc.STC_LEX_XML      : ['xml'],
             }
