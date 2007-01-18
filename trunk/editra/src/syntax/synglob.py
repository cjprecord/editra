###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
#                                                                             #
#    This program is free software; you can redistribute it and#or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
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
# modules                                                                     #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependencies
import wx.stc as stc

#-----------------------------------------------------------------------------#

#---- Language Identifiers Keys ----#
# Used for specifying what dialect/keyword set to load for a specific lexer

# Use LEX_NULL
ID_LANG_TXT  = 10

# Use LEX_ASM
ID_LANG_ASM  = 100
ID_LANG_68K  = 101
ID_LANG_MASM = 102
ID_LANG_NASM = 103

# Use LEX_BASH
ID_LANG_BOURNE = 110
ID_LANG_BASH   = 111
ID_LANG_CSH    = 112
ID_LANG_KSH    = 113

# Use LEX_CPP
ID_LANG_C    = 120
ID_LANG_CPP  = 121
ID_LANG_JAVA = 122

# Use LEX_CSS
ID_LANG_CSS = 140

# Use LEX_HTML
ID_LANG_HTML = 150
ID_LANG_JS   = 151
ID_LANG_VBS  = 152
ID_LANG_PHP  = 153
ID_LANG_XML  = 154
ID_LANG_SGML = 155

# Use LEX_LISP
ID_LANG_LISP = 170

# Use LEX_MSSQL (Microsoft SQL)
ID_LANG_MSSQL = 180

# Use LEX_NSIS
ID_LANG_NSIS = 190

# Use LEX_PASCAL
ID_LANG_PASCAL = 200

# Use LEX_PERL
ID_LANG_PERL = 210

# Use LEX_PS
ID_LANG_PS = 220

# Use LEX_PYTHON 
ID_LANG_PYTHON = 230

# Use LEX_RUBY
ID_LANG_RUBY = 240

# Use LEX_SQL (PL/SQL, SQL*Plus)
ID_LANG_SQL = 250

# Use LEX_TEX
ID_LANG_TEX = 260
ID_LANG_LATEX = 261

# Use LEX_VB
ID_LANG_VB = 270

# Use LEX_VHDL
ID_LANG_VHDL = 280

# Use LEX_OTHER (Batch, Makefile)
ID_LANG_BATCH = 290
ID_LANG_MAKE  = 291

#---- End Language Identifier Keys ----#

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
# Yea, its alittle ugly but it will do for now
#            EXT     LANG_ID         DESC_STR                 LEXER            MODULE
EXT_REG = { 'asm'  : (ID_LANG_68K,   'MASM',                 stc.STC_LEX_ASM,   'masm'),
            '68k'  : (ID_LANG_68K,   '68K Assembly',          stc.STC_LEX_ASM,   'asm68k'),
            'masm' : (ID_LANG_MASM,  'MASM',                  stc.STC_LEX_ASM,   'masm'),
            'nasm' : (ID_LANG_NASM,  'Netwide Assembler',     stc.STC_LEX_ASM,   'nasm'),
            'bat'  : (ID_LANG_BATCH, 'DOS Batch Script',      stc.STC_LEX_BATCH, 'batch'),
            'cmd'  : (ID_LANG_BATCH, 'DOS Batch Script',      stc.STC_LEX_BATCH, 'batch'),
            'bsh'  : (ID_LANG_BASH,  'Bash Shell Script',     stc.STC_LEX_BASH,  'sh'),
            'sh'   : (ID_LANG_BASH,  'Bash Shell Script',     stc.STC_LEX_BASH,  'sh'),
            'csh'  : (ID_LANG_CSH,   'C-Shell Script',        stc.STC_LEX_BASH,  'sh'),
            'ksh'  : (ID_LANG_KSH,   'Korn Shell Script',     stc.STC_LEX_BASH,  'sh'),
            'c'    : (ID_LANG_C,     'C',                     stc.STC_LEX_CPP,   'cpp'),
            'cpp'  : (ID_LANG_CPP,   'CPP',                   stc.STC_LEX_CPP,   'cpp'),
            'cxx'  : (ID_LANG_CPP,   'CPP',                   stc.STC_LEX_CPP,   'cpp'),
            'c++'  : (ID_LANG_CPP,   'CPP',                   stc.STC_LEX_CPP,   'cpp'),
            'cc'   : (ID_LANG_CPP,   'CPP',                   stc.STC_LEX_CPP,   'cpp'),
            'h'    : (ID_LANG_CPP,   'Header',                stc.STC_LEX_CPP,   'cpp'),
            'h++'  : (ID_LANG_CPP,   'Header',                stc.STC_LEX_CPP,   'cpp'),
            'hh'   : (ID_LANG_CPP,   'Header',                stc.STC_LEX_CPP,   'cpp'),
            'hpp'  : (ID_LANG_CPP,   'Header',                stc.STC_LEX_CPP,   'cpp'),
            'hxx'  : (ID_LANG_CPP,   'Header',                stc.STC_LEX_CPP,   'cpp'),
            'css'  : (ID_LANG_CSS,   'Cascading Style Sheet', stc.STC_LEX_CSS,   'css'),
            'html' : (ID_LANG_HTML,  'HTML',                  stc.STC_LEX_HTML,  'html'),
            'htm'  : (ID_LANG_HTML,  'HTML',                  stc.STC_LEX_HTML,  'html'),
            'shtml': (ID_LANG_HTML,  'HTML',                  stc.STC_LEX_HTML,  'html'),
            'java' : (ID_LANG_JAVA,  'Java',                  stc.STC_LEX_CPP,   'java'),
            'js'   : (ID_LANG_JS,    'JavaScript',            stc.STC_LEX_CPP,  'javascript'), 
            'php'  : (ID_LANG_PHP,   'PHP',                   stc.STC_LEX_PHP,   'php'),
            'php3' : (ID_LANG_PHP,   'PHP',                   stc.STC_LEX_PHP,   'php'),
            'phtml': (ID_LANG_PHP,   'PHP',                   stc.STC_LEX_PHP,   'php'),
            'tex'  : (ID_LANG_TEX,   'Tex/Latex',             stc.STC_LEX_LATEX,   'latex'),
            'sty'  : (ID_LANG_TEX,   'Tex/Latex',             stc.STC_LEX_LATEX,   'latex'),
            'aux'  : (ID_LANG_LATEX, 'Latex',                 stc.STC_LEX_LATEX, 'latex'),
            'lisp' : (ID_LANG_LISP,  'Lisp',                  stc.STC_LEX_LISP,  'lisp'),
            'cl'   : (ID_LANG_LISP,  'Lisp',                  stc.STC_LEX_LISP,  'lisp'),
            'lsp'  : (ID_LANG_LISP,  'Lisp',                  stc.STC_LEX_LISP,  'lisp'),
            'makefile' : (ID_LANG_MAKE, 'Makefile',           stc.STC_LEX_MAKEFILE, 'make'),
            'configure' : (ID_LANG_MAKE, 'Makefile',          stc.STC_LEX_MAKEFILE, 'make'),
            'mak'  : (ID_LANG_MAKE,  'Makefile',              stc.STC_LEX_MAKEFILE, 'make'),
            'mssql' : (ID_LANG_MSSQL, 'Microsoft SQL',        stc.STC_LEX_MSSQL, 'mssql'),
            'nsi'  : (ID_LANG_NSIS,  'Nullsoft Installer Script', stc.STC_LEX_NSIS, 'nsis'),
            'pp'   : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
            'pas'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
            'dpr'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
            'dpk'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
            'dfm'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
            'inc'  : (ID_LANG_PASCAL, 'Pascal',               stc.STC_LEX_PASCAL, 'pascal'),
            'pl'   : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,  'perl'),
            'pm'   : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,  'perl'),
            'pod'  : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,  'perl'),
            'cgi'  : (ID_LANG_PERL,   'Perl',                 stc.STC_LEX_PERL,  'perl'),
            'ps'   : (ID_LANG_PS,     'Postscript',           stc.STC_LEX_PS,    'postscript'),
            'py'   : (ID_LANG_PYTHON, 'Python',               stc.STC_LEX_PYTHON, 'python'),
            'rb'   : (ID_LANG_RUBY,   'Ruby',                 stc.STC_LEX_RUBY,  'ruby'),
            'rbx'  : (ID_LANG_RUBY,   'Ruby',                 stc.STC_LEX_RUBY,  'ruby'),
            'rbw'  : (ID_LANG_RUBY,   'Ruby',                 stc.STC_LEX_RUBY,  'ruby'),
            'sql'  : (ID_LANG_SQL,    'SQL',                  stc.STC_LEX_SQL,   'sql'),
            'vb'   : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
            'bas'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
            'frm'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
            'cls'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
            'ctl'  : (ID_LANG_VB,     'Visual Basic',         stc.STC_LEX_VB,    'visualbasic'),
            'vhdl' : (ID_LANG_VHDL,   'VHDL',                 stc.STC_LEX_VHDL,  'vhdl'),
            'vhd'  : (ID_LANG_VHDL,   'VHDL',                 stc.STC_LEX_VHDL,  'vhdl'),
            'xml'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'svg'  : (ID_LANG_XML,    'SVG',                  stc.STC_LEX_XML,   'xml'),
            'xsl'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'rdf'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'xslt' : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'xsd'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'xul'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'axl'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'xrc'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'dtd'  : (ID_LANG_XML,    'XML',                  stc.STC_LEX_XML,   'xml'),
            'txt'  : (ID_LANG_TXT,    'Plain Text',           stc.STC_LEX_NULL,  None)
           }

# Maps file types to Lexer values
FILE_LEXERS = { 'Assembly Code'            : stc.STC_LEX_ASM,
                 'Shell Scripts'            : stc.STC_LEX_BASH,
                 'Batch Files'              : stc.STC_LEX_BATCH,
                 'C/CPP'                    : stc.STC_LEX_CPP,
                 'Cascading Style Sheets'   : stc.STC_LEX_CSS,
                 'JavaScript'               : stc.STC_LEX_HTML,
                 'HTML'                     : stc.STC_LEX_HTML,
                 'PHP'                      : stc.STC_LEX_PHP,
                 'LaTex'                    : stc.STC_LEX_LATEX,
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
                 'PL/SQL'                   : stc.STC_LEX_SQL,
                 'Visual Basic'             : stc.STC_LEX_VB,
                 'VHDL'                     : stc.STC_LEX_VHDL,
                  'XML'                     : stc.STC_LEX_XML,
                 'Other'                    : stc.STC_LEX_NULL
               } 

# Map Lexers to Module names
LEX_MODULES = { stc.STC_LEX_ASM     : ['asm', 'asm68k', 'masm', 'nasm'],
                stc.STC_LEX_BASH     : ['sh'],
                stc.STC_LEX_BATCH    : ['bat'],
                stc.STC_LEX_CPP      : ['cpp'],
                stc.STC_LEX_CSS      : ['css'],
                stc.STC_LEX_HTML     : ['javascript', 'html'],
                stc.STC_LEX_PHP      : ['php'],
                stc.STC_LEX_TEX      : ['latex'],
                stc.STC_LEX_LISP     : ['lisp'],
                stc.STC_LEX_MAKEFILE : ['make'],
                stc.STC_LEX_MSSQL    : ['mssql'],
                stc.STC_LEX_NSIS     : ['nsis'],
                stc.STC_LEX_NULL     : None,
                stc.STC_LEX_PASCAL   : ['pascal'],
                stc.STC_LEX_PERL     : ['perl'],
                stc.STC_LEX_PS       : ['postscript'],
                stc.STC_LEX_PYTHON   : ['python'],
                stc.STC_LEX_RUBY     : ['ruby'],
                stc.STC_LEX_SQL      : ['sql'],
                stc.STC_LEX_VB       : ['visualbasic'],
                stc.STC_LEX_XML      : ['xml'],
              }
