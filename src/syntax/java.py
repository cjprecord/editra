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
# FILE: java.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexter configuration file for Java source files.                            #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependencies

import synglob
#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Java Keywords
java_keywords = (0, "import native package goto const if else switch while for "
                     "do true false null this super new instanceof return throw "
                     "try catch finally assert synchronized throws extends "
                     "implements interface break continue ")

# Java Types/Structures/Storage Classes
java_types = (1, "boolean char byte short int long float double void static "
                  "synchronized transient volatile final strictfp serializable "
                  "class public protected private abstract")

# Documentation Keywords (Doxygen keywords/ect)
doc_keywords = (2, "TODO FIXME XXX \\author \\brief \\bug \\callgraph \\category " 
                   "\\class \\code \\date \\def \\depreciated \\dir \\dot \\dotfile "
                   "\\else \\elseif \\em \\endcode \\enddot \\endif \\endverbatim " 
                   "\\example \\exception \\file \\if \\ifnot \\image \\include \\link " 
                   "\\mainpage \\name \\namespace \\page \\par \\paragraph \\param "
                   "\\return \\retval \\section \\struct \\subpage \\subsection " 
                   "\\subsubsection \\test \\todo \\typedef \\union \\var \\verbatim "
                   "\\version \\warning \\$ \\@ \\~ \\< \\> \\# \\% HACK")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_C_DEFAULT', 'default_style'),
                 ('STC_C_COMMENT', 'comment_style'),
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
def Keywords(type=0):
    """Returns List of Keyword Specifications"""
    KEYWORDS = [java_keywords, java_types, doc_keywords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns a list of syntax specifications"""
    return syntax_items

def Properties(type=0):
    """Returns a list of extra properties to set"""
    return [fold, fold_pre]

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u'//' ]
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String"""
    # Unused by this module, stubbed in for consistancy
    return None

#---- End Syntax Modules Internal Functions ----#
