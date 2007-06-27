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
# FILE: cpp.py                                                                #
# @author: Cody Precord                                                       #
#                                                                             #
# SUMMARY:                                                                    #
# Lexter configuration file for C/C++ source files.                           #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependencies
import synglob

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# C Keywords
c_keywords = ("goto break return continue asm case default if else switch "
              "while for do sizeof typeof ")

# C Types/Structures/Storage Classes
c_types = ("int long short char void signed unsigned float double "
           "size_t ssize_t wchar_t ptrdiff_t sig_atomic_t fpos_t "
           "clock_t time_t va_list jmp_buf FILE DIR div_t ldiv_t "
           "mbstate_t wctrans_t wint_t wctype_t bool complex int8_t "
           "int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t "
           "int_least8_t int_least16_t int_least32_t int_least64_t "
           "uint_fast8_t uint_fast16_t uint_fast32_t uint_fast64_t "
           "intptr_t uintptr_t intmax_t uintmax_t __label__ __complex__ "
           "__volatile__ struct union enum typedef static register auto "
           "volatile extern const inline __attribute__ ")

# C/CPP Documentation Keywords (includes Doxygen keywords)
doc_keywords = (2, "TODO FIXME XXX \\author \\brief \\bug \\callgraph \\category " 
                   "\\class \\code \\date \\def \\depreciated \\dir \\dot \\dotfile "
                   "\\else \\elseif \\em \\endcode \\enddot \\endif \\endverbatim " 
                   "\\example \\exception \\file \\if \\ifnot \\image \\include \\link " 
                   "\\mainpage \\name \\namespace \\page \\par \\paragraph \\param "
                   "\\return \\retval \\section \\struct \\subpage \\subsection " 
                   "\\subsubsection \\test \\todo \\typedef \\union \\var \\verbatim "
                   "\\version \\warning \\$ \\@ \\~ \\< \\> \\# \\% HACK ")

# CPP Keyword Extensions
cpp_keywords = ("new delete this friend using throw try catch opperator "
                "typeid and bitor or xor compl bitand and_eq or_eq xor_eq "
                "not not_eq const_cast static_cast dynamic_cast "
                "reinterpret_cast true false ")

# CPP Type/Structure/Storage Class Extensions
cpp_types = ("public protected private inline virtual explicit export bool "
             "wchar_t mutable class typename template namespace ")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_C_DEFAULT', 'default_style'),
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
fold = ("fold", "1")
fold_pre = ("styling.within.preprocessor", "0")
fold_com = ("fold.comment", "1")
fold_comp = ("fold.compact", "1")
fold_else = ("fold.at.else", "0")
#------------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    keywords= list()
    kw1_str = [c_keywords]
    kw2_str = [c_types]
    if lang_id == synglob.ID_LANG_CPP:
        kw1_str.append(cpp_keywords)
        kw2_str.append(cpp_types)
    keywords.append((0, " ".join(kw1_str)))
    keywords.append((1, " ".join(kw2_str)))
    keywords.append(doc_keywords)
    return keywords

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [fold, fold_pre]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    if type == synglob.ID_LANG_CPP:
        return [ u'//' ]
    else:
        return [ u'/*', u'*/' ]

#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
