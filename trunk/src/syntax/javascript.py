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
# TODO:                                                                       #
# Having trouble with getting html embeded js to highlight                    #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
import synglob
import cpp
#---- Keyword Specifications ----#

# JavaScript Keywords # set to 1 for embeded
js_keywords = (0, "if else while for break continue switch case default new in "
                  "this var const return with function true false abstract and "
                  "array as catch class char debugger delete declare double "
                  "else enum export extend final finally float goto implements "
                  "import instanceof int interface long native null package "
                  "private protected public return short static syncronized "
                  "throw throws transient try typeof void while")

#---- Syntax Style Spec ----#
syntax_items = [ ('STC_HJ_COMMENT', 'comment_style'),
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
def Keywords(type=0):
    """Returns Keyword Settings List"""
    KEYWORDS = [js_keywords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    if type == synglob.ID_LANG_HTML:
        return syntax_items
    else:
        return cpp.syntax_items

def Properties(type=0):
    """Extra Properties"""
    return [("fold", "1")]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns just keyword string"""
    return js_keywords[1]

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
