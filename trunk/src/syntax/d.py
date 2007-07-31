###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    staff@editra.org                                                         #
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
# FILE: d.py                                                                  #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for D programming language                       #
#                                                                             #
# @todo:                                                                      #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

import synglob
#-----------------------------------------------------------------------------#
#---- Keyword Definitions ----#
D_KEYWORDS = (0, "abstract alias align asm assert auto body break case cast "
                 "catch cent class continue debug default delegate delete "
                 "deprecated do else enum export extern false final finally "
                 "for foreach foreach_reverse function goto if import in inout "
                 "interface invariant is lazy mixin module new null out "
                 "override package pragma private protected public return "
                 "scope short struct super switch synchronized template this "
                 "throw true try union unittest version void while with")

D_TYPES = (1, "bool byte cdouble cfloat char const creal dchar double float "
              "idouble ifloat ireal int real long static typeof typedef typeid "
              "ubyte ucent uint ulong ushort volatile wchar")

DOC_KEYWORDS = (2, "TODO FIXME XXX \\author \\brief \\bug \\callgraph "
                   "\\category \\class \\code \\date \\def \\depreciated \\dir "
                   "\\dot \\dotfile \\else \\elseif \\em \\endcode \\enddot "
                   "\\endif \\endverbatim \\example \\exception \\file \\if "
                   "\\ifnot \\image \\include \\link \\mainpage \\name "
                   "\\namespace \\page \\par \\paragraph \\param \\return "
                   "\\retval \\section \\struct \\subpage \\subsection " 
                   "\\subsubsection \\test \\todo \\typedef \\union \\var "
                   "\\verbatim \\version \\warning \\$ \\@ \\~ \\< \\> \\# \\% "
                   "HACK ")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [ ('STC_C_DEFAULT', 'default_style'),
                 ('STC_C_COMMENT', 'comment_style'),
                 ('STC_C_COMMENTLINE', 'comment_style'),
                 ('STC_C_COMMENTDOC', 'comment_style'),
                 ('STC_C_COMMENTDOCKEYWORD', 'dockey_style'),
                 ('STC_C_COMMENTDOCKEYWORDERROR', 'error_style'),
                 ('STC_C_COMMENTLINE', 'comment_style'),
                 ('STC_C_COMMENTLINEDOC', 'comment_style'),
                 ('STC_C_CHARACTER', 'char_style'),
                 ('STC_C_GLOBALCLASS', 'global_style'),
                 ('STC_C_IDENTIFIER', 'default_style'),
                 ('STC_C_NUMBER', 'number_style'),
                 ('STC_C_OPERATOR', 'operator_style'),
                 ('STC_C_PREPROCESSOR', 'pre_style'),
                 ('STC_C_REGEX', 'pre_style'),
                 ('STC_C_STRING', 'string_style'),
                 ('STC_C_STRINGEOL', 'stringeol_style'),
                 ('STC_C_UUID', 'pre_style'),
                 ('STC_C_VERBATIM', "number2_style"),
                 ('STC_C_WORD', 'keyword_style'),
                 ('STC_C_WORD2', 'keyword2_style') ]

#---- Extra Properties ----#
FOLD = ("fold", "1")
FOLD_PRE = ("styling.within.preprocessor", "0")
FOLD_COM = ("fold.comment", "1")
FOLD_COMP = ("fold.compact", "1")
FOLD_ELSE = ("fold.at.else", "0")
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @keyword lang_id: used to select specific subset of keywords

    """
    if lang_id == synglob.ID_LANG_D:
        return [D_KEYWORDS, D_TYPES, DOC_KEYWORDS]
    else:
        return list()

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @keyword lang_id: used for selecting a specific subset of syntax specs

    """
    if lang_id == synglob.ID_LANG_D:
        return SYNTAX_ITEMS
    else:
        return list()

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @keyword lang_id: used to select a specific set of properties

    """
    if lang_id == synglob.ID_LANG_D:
        return [FOLD, FOLD_PRE]
    else:
        return list()

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @keyword lang_id: used to select a specific subset of comment pattern(s)

    """
    if lang_id == synglob.ID_LANG_D:
        return [u'//']
    else:
        return list()

#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
