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
# FILE: javascript.py                                                         #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for JavaScript.                                  #
#                                                                             #
# @todo: Having trouble with getting html embeded js to highlight             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
import synglob
import cpp
#---- Keyword Specifications ----#

# JavaScript Keywords # set to 1 for embeded
JS_KEYWORDS = (0, "if else while for break continue switch case default new in "
                  "this var const return with function true false abstract and "
                  "array as catch class char debugger delete declare double "
                  "else enum export extend final finally float goto implements "
                  "import instanceof int interface long native null package "
                  "private protected public return short static syncronized "
                  "throw throws transient try typeof void while")

#---- Syntax Style Spec ----#
SYNTAX_ITEMS = [ ('STC_HJ_COMMENT', 'comment_style'),
                 ('STC_HJ_COMMENTDOC', 'dockey_style'),
                 ('STC_HJ_COMMENTLINE', 'comment_style'),
                 ('STC_HJ_DEFAULT', 'default_style'),
                 ('STC_HJ_DOUBLESTRING', 'string_style'),
                 ('STC_HJ_KEYWORD', 'keyword_style'),
                 ('STC_HJ_NUMBER', 'number_style'),
                 ('STC_HJ_REGEX', 'scalar_style'), # STYLE ME
                 ('STC_HJ_SINGLESTRING', 'string_style'),
                 ('STC_HJ_START', 'scalar_style'),
                 ('STC_HJ_STRINGEOL', 'stringeol_style'),
                 ('STC_HJ_SYMBOLS', 'array_style'),
                 ('STC_HJ_WORD', 'class_style'),
                 ('STC_HJA_COMMENT', 'comment_style'),
                 ('STC_HJA_COMMENTDOC', 'dockey_style'),
                 ('STC_HJA_COMMENTLINE', 'comment_style'),
                 ('STC_HJA_DEFAULT', 'default_style'),
                 ('STC_HJA_DOUBLESTRING', 'string_style'),
                 ('STC_HJA_KEYWORD', 'keyword_style'),
                 ('STC_HJA_NUMBER', 'number_style'),
                 ('STC_HJA_REGEX', 'scalar_style'), # STYLE ME
                 ('STC_HJA_SINGLESTRING', 'string_style'),
                 ('STC_HJA_START', 'scalar_style'),
                 ('STC_HJA_STRINGEOL', 'stringeol_style'),
                 ('STC_HJA_SYMBOLS', 'array_style'),
                 ('STC_HJA_WORD', 'class_style') ]

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [JS_KEYWORDS]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    if lang_id == synglob.ID_LANG_HTML:
        return SYNTAX_ITEMS
    else:
        return cpp.SYNTAX_ITEMS

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [("fold", "1")]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [u'//']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @param option: specific subset of keywords to get

    """
    return JS_KEYWORDS[1]

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
