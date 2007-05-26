###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
#                                                                             #
#    Editra is free software; you can redistribute it and#or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    Edira is distributed in the hope that it will be useful,                 #
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

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependencies
import wx
import wx.stc as stc

#-----------------------------------------------------------------------------#

#---- Language Identifiers Keys ----#
# Used for specifying what dialect/keyword set to load for a specific lexer

# Use LEX_NULL
ID_LANG_TXT  = wx.NewId()

# Use LEX_ADA
ID_LANG_ADA = wx.NewId()

# Use LEX_ASM
ID_LANG_ASM  = wx.NewId()
ID_LANG_68K  = wx.NewId()
ID_LANG_MASM = wx.NewId()
ID_LANG_NASM = wx.NewId()

# Use LEX_BASH
ID_LANG_BOURNE = wx.NewId()
ID_LANG_BASH   = wx.NewId()
ID_LANG_CSH    = wx.NewId()
ID_LANG_KSH    = wx.NewId()

# Use LEX_CPP
ID_LANG_C    = wx.NewId()
ID_LANG_CPP  = wx.NewId()
ID_LANG_JAVA = wx.NewId()

# Use LEX_CSS
ID_LANG_CSS = wx.NewId()
ID_LANG_ESS = wx.NewId()

# Use LEX_F77
ID_LANG_F77 = wx.NewId()

# Use LEX_FORTRAN
ID_LANG_F95 = wx.NewId()

# Use LEX_HTML
ID_LANG_HTML = wx.NewId()
ID_LANG_JS   = wx.NewId()
ID_LANG_VBS  = wx.NewId()
ID_LANG_PHP  = wx.NewId()
ID_LANG_XML  = wx.NewId()
ID_LANG_SGML = wx.NewId()

# Use LEX_LISP
ID_LANG_LISP = wx.NewId()

# Use LEX_LUA
ID_LANG_LUA = wx.NewId()

# Use LEX_MSSQL (Microsoft SQL)
ID_LANG_MSSQL = wx.NewId()

# Use LEX_NSIS
ID_LANG_NSIS = wx.NewId()

# Use LEX_PASCAL
ID_LANG_PASCAL = wx.NewId()

# Use LEX_PERL
ID_LANG_PERL = wx.NewId()

# Use LEX_PS
ID_LANG_PS = wx.NewId()

# Use LEX_PYTHON 
ID_LANG_PYTHON = wx.NewId()

# Use LEX_RUBY
ID_LANG_RUBY = wx.NewId()

# Use LEX_SMALLTALK
ID_LANG_ST = wx.NewId()

# Use LEX_SQL (PL/SQL, SQL*Plus)
ID_LANG_SQL = wx.NewId()

# Use LEX_TCL
ID_LANG_TCL  = wx.NewId()

# Use LEX_TEX
ID_LANG_TEX = wx.NewId()
ID_LANG_LATEX = wx.NewId()

# Use LEX_VB
ID_LANG_VB = wx.NewId()

# Use LEX_VHDL
ID_LANG_VHDL = wx.NewId()

# Use LEX_OTHER (Batch, Makefile)
ID_LANG_BATCH = wx.NewId()
ID_LANG_MAKE  = wx.NewId()

#---- End Language Identifier Keys ----#

# TODO rework this to be a plugin system so we can avoid all these
#      definitions.
# OBJECT NAME: EXT_REG (Extention Register)
# BRIEF:
# Map File Extentions to an ordered tuple used for syntax lookup
# DESCRIPION:
# This Dictionary needs to be updated whenever a new module is added to the syntax 
# directory. This dictionary is used to decide the default lexer data to load for
# each file extention. So if an extention is not in this list the syntax highlighting
# for that file cannot be loaded automatically.
# SPECIFICATION: str extention : (int File Type ID, string Name, int Lexer, str modulename)
#
# Yea, its alittle ugly but works nicely
#            EXT     LANG_ID         DESC_STR                 LEXER            MODULE
EXT_REG = {'68k'  : (ID_LANG_68K,    '68K Assembly',         stc.STC_LEX_ASM,   'asm68k'),
           'adb'  : (ID_LANG_ADA,    'Ada',                  stc.STC_LEX_ADA,   'ada'),
           'ads'  : (ID_LANG_ADA,    'Ada',                  stc.STC_LEX_ADA,   'ada'),
           'asm'  : (ID_LANG_68K,    'MASM',                 stc.STC_LEX_ASM,   'masm'),
           'aux'  : (ID_LANG_LATEX,  'LaTeX',                stc.STC_LEX_LATEX, 'latex'),
           'axl'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
           'bat'  : (ID_LANG_BATCH,  'DOS Batch Script',     stc.STC_LEX_BATCH, 'batch'),            
           'bas'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
           'bsh'  : (ID_LANG_BASH,   'Bash Shell Script',    stc.STC_LEX_BASH,  'sh'),
           'c'    : (ID_LANG_C,      'C',                    stc.STC_LEX_CPP,   'cpp'),
           'cc'   : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'c++'  : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'cgi'  : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,  'perl'),
           'cl'   : (ID_LANG_LISP,   'Lisp',                 stc.STC_LEX_LISP,  'lisp'),
           'cls'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
           'cmd'  : (ID_LANG_BATCH,  'DOS Batch Script',     stc.STC_LEX_BATCH, 'batch'),
           'configure' : (ID_LANG_BASH, 'Bash Shell Script', stc.STC_LEX_BASH,  'sh'),
           'cpp'  : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'csh'  : (ID_LANG_CSH,    'C-Shell Script',       stc.STC_LEX_BASH,  'sh'),
           'css'  : (ID_LANG_CSS,    'Cascading Style Sheet', stc.STC_LEX_CSS,  'css'),
           'ctl'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
           'cxx'  : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'dfm'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
           'dpk'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
           'dpr'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
           'dtd'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
           'ess'  : (ID_LANG_ESS,    'Editra Style Sheet',   stc.STC_LEX_CSS,   'editra_ss'),
           'f90'  : (ID_LANG_F95,    'Fortran 95',           stc.STC_LEX_FORTRAN, 'fortran'),
           'f95'  : (ID_LANG_F95,    'Fortran 95',           stc.STC_LEX_FORTRAN, 'fortran'),
           'f2k'  : (ID_LANG_F95,    'Fortran 95',           stc.STC_LEX_FORTRAN, 'fortran'),
           'f'    : (ID_LANG_F77,    'Fortran 77',           stc.STC_LEX_F77,   'fortran'),
           'for'  : (ID_LANG_F77,    'Fortran 77',           stc.STC_LEX_F77,   'fortran'),
           'frm'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
           'h'    : (ID_LANG_C,      'C',                    stc.STC_LEX_CPP,   'cpp'),
           'hh'   : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'h++'  : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'hpp'  : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'html' : (ID_LANG_HTML,   'HTML',                 stc.STC_LEX_HTML,  'html'),
           'htm'  : (ID_LANG_HTML,   'HTML',                 stc.STC_LEX_HTML,  'html'),
           'hxx'  : (ID_LANG_CPP,    'CPP',                  stc.STC_LEX_CPP,   'cpp'),
           'inc'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
           'itcl' : (ID_LANG_TCL,    'TCL/TK',               stc.STC_LEX_TCL,   'tcl'),
           'java' : (ID_LANG_JAVA,   'Java',                 stc.STC_LEX_CPP,   'java'),
           'js'   : (ID_LANG_JS,     'JavaScript',           stc.STC_LEX_CPP,   'javascript'), 
           'ksh'  : (ID_LANG_KSH,    'Korn Shell Script',    stc.STC_LEX_BASH,  'sh'),
           'lisp' : (ID_LANG_LISP,   'Lisp',                 stc.STC_LEX_LISP,  'lisp'),
           'lsp'  : (ID_LANG_LISP,   'Lisp',                 stc.STC_LEX_LISP,  'lisp'),
           'lua'  : (ID_LANG_LUA,    'Lua',                  stc.STC_LEX_LUA,   'lua'),
           'mak'  : (ID_LANG_MAKE,   'Makefile',             stc.STC_LEX_MAKEFILE, 'make'),
           'makefile' : (ID_LANG_MAKE, 'Makefile',           stc.STC_LEX_MAKEFILE, 'make'),
           'masm' : (ID_LANG_MASM,   'MASM',                 stc.STC_LEX_ASM,   'masm'),
           'mssql' : (ID_LANG_MSSQL, 'Microsoft SQL',        stc.STC_LEX_MSSQL, 'mssql'),
           'nasm' : (ID_LANG_NASM,   'Netwide Assembler',    stc.STC_LEX_ASM,   'nasm'),
           'nsi'  : (ID_LANG_NSIS,   'Nullsoft Installer Script', stc.STC_LEX_NSIS, 'nsis'),
           'pas'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
           'php'  : (ID_LANG_PHP,    'PHP',                  stc.STC_LEX_HTML,   'php'),
           'php3' : (ID_LANG_PHP,    'PHP',                  stc.STC_LEX_HTML,   'php'),
           'phtml': (ID_LANG_PHP,    'PHP',                  stc.STC_LEX_HTML,   'php'),
           'pl'   : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,   'perl'),
           'pm'   : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,   'perl'),
           'pod'  : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,   'perl'),
           'pp'   : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
           'ps'   : (ID_LANG_PS,     'Postscript',           stc.STC_LEX_PS,     'postscript'),
           'py'   : (ID_LANG_PYTHON, 'Python',               stc.STC_LEX_PYTHON, 'python'),
           'pyw'  : (ID_LANG_PYTHON, 'Python',               stc.STC_LEX_PYTHON, 'python'),
           'python' : (ID_LANG_PYTHON, 'Python',             stc.STC_LEX_PYTHON, 'python'),
           'rb'   : (ID_LANG_RUBY,   'Ruby',                 stc.STC_LEX_RUBY,   'ruby'),
           'rbw'  : (ID_LANG_RUBY,   'Ruby',                 stc.STC_LEX_RUBY,   'ruby'),
           'rbx'  : (ID_LANG_RUBY,   'Ruby',                 stc.STC_LEX_RUBY,   'ruby'),
           'rdf'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml'),
           'sh'   : (ID_LANG_BASH,   'Bash Shell Script',    stc.STC_LEX_BASH,   'sh'),
           'shtml': (ID_LANG_HTML,   'HTML',                 stc.STC_LEX_HTML,   'html'),
           'sql'  : (ID_LANG_SQL,    'SQL',                  stc.STC_LEX_SQL,    'sql'),
           'st'   : (ID_LANG_ST,     'Smalltalk',            stc.STC_LEX_SMALLTALK, 'smalltalk'),
           'sty'  : (ID_LANG_LATEX,  'LaTeX',                stc.STC_LEX_LATEX,  'latex'),
           'svg'  : (ID_LANG_XML,    'SVG',                  stc.STC_LEX_XML,    'xml'),
           'tcl'  : (ID_LANG_TCL,    'TCL/TK',               stc.STC_LEX_TCL,    'tcl'),
           'tex'  : (ID_LANG_LATEX,  'LaTeX',                stc.STC_LEX_LATEX,  'latex'),
           'txt'  : (ID_LANG_TXT,    'Plain Text',           stc.STC_LEX_NULL,   None),
           'vb'   : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,     'visualbasic'),
           'vhdl' : (ID_LANG_VHDL,   'VHDL',                 stc.STC_LEX_VHDL,   'vhdl'),
           'vhd'  : (ID_LANG_VHDL,   'VHDL',                 stc.STC_LEX_VHDL,   'vhdl'),
           'xml'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml'),
           'xrc'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml'),
           'xsd'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml'),
           'xsl'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml'),
           'xslt' : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml'),
           'xul'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,    'xml')
           }

# Maps language ID's to File extensions
# Used when manually setting lexer from a menu/dialog
EXT_DICT = {ID_LANG_68K : '68k', ID_LANG_ADA : 'ads', 
            ID_LANG_ASM : 'asm', ID_LANG_BASH : 'sh', 
            ID_LANG_BATCH : 'bat', ID_LANG_C : 'c', 
            ID_LANG_CPP : 'cpp', ID_LANG_CSH : 'csh', 
            ID_LANG_CSS : 'css', ID_LANG_ESS : 'ess',
            ID_LANG_F77 : 'for', ID_LANG_F95 : 'f95', 
            ID_LANG_HTML : 'html', ID_LANG_JAVA : 'java', 
            ID_LANG_JS : 'js', ID_LANG_KSH : 'ksh',
            ID_LANG_LATEX : 'tex', ID_LANG_LISP : 'lisp', 
            ID_LANG_LUA : 'lua', ID_LANG_MAKE : 'makefile', 
            ID_LANG_MASM : 'masm', ID_LANG_MSSQL : 'mssql', 
            ID_LANG_NASM : 'nasm', ID_LANG_NSIS : 'nsi', 
            ID_LANG_PASCAL : 'pas', ID_LANG_PERL : 'pl', 
            ID_LANG_PHP : 'php', ID_LANG_PS : 'ps', 
            ID_LANG_PYTHON : 'py', ID_LANG_RUBY : 'rb', 
            ID_LANG_SQL : 'sql', ID_LANG_ST : 'st', 
            ID_LANG_VB : 'vb', ID_LANG_VHDL : 'vhdl', 
            ID_LANG_TCL : 'tcl', ID_LANG_TXT : 'txt', 
            ID_LANG_XML : 'xml',
}

# Maps file types to Lexer values
FILE_LEXERS = { 'Ada'                      : stc.STC_LEX_ADA,
                'Assembly Code'            : stc.STC_LEX_ASM,
                'Shell Scripts'            : stc.STC_LEX_BASH,
                'Batch Files'              : stc.STC_LEX_BATCH,
                'C/CPP'                    : stc.STC_LEX_CPP,
                'Cascading Style Sheets'   : stc.STC_LEX_CSS,
                'JavaScript'               : stc.STC_LEX_HTML,
                'HTML'                     : stc.STC_LEX_HTML,
                'PHP'                      : stc.STC_LEX_HTML,
                'Tex/LaTex'                : stc.STC_LEX_LATEX,
                'Lua'                      : stc.STC_LEX_LUA,
                'Lisp'                     : stc.STC_LEX_LISP,
                'Makefile'                 : stc.STC_LEX_MAKEFILE,
                'Microsoft SQL'            : stc.STC_LEX_MSSQL,
                'Nullsoft Installer Script': stc.STC_LEX_NSIS,
                'Plain Text'               : stc.STC_LEX_NULL,
                'Pascal'                   : stc.STC_LEX_PASCAL,
                'Perl'                     : stc.STC_LEX_PERL,
                'PostScript'               : stc.STC_LEX_PS,
                'Python'                   : stc.STC_LEX_PYTHON,
                'Ruby'                     : stc.STC_LEX_RUBY,
                'Smalltalk'                : stc.STC_LEX_SMALLTALK,
                'PL/SQL'                   : stc.STC_LEX_SQL,
                'Visual Basic'             : stc.STC_LEX_VB,
                'VHDL'                     : stc.STC_LEX_VHDL,
                'XML'                     : stc.STC_LEX_XML,
                'Other'                    : stc.STC_LEX_NULL
               } 

# Map Lexers to Module names
LEX_MODULES = {stc.STC_LEX_ADA     : ['ada'], 
                stc.STC_LEX_ASM     : ['asm', 'asm68k', 'masm', 'nasm'],
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
