###############################################################################
#    Copyright (C) 2007 Editra Development Team                               #
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
# FILE: editra_ss.py                                                          #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file for Editra Syntax Highlighter Style Sheets.        #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Editra Style Sheet Keywords
ess_keywords = (0, "fore back face size eol bold italic")


#---- Syntax Style Specs ----#
syntax_items = [ ('STC_CSS_DEFAULT', 'default_style'),
                 ('STC_CSS_CLASS', 'global_style'),
                 ('STC_CSS_COMMENT', 'comment_style'),
                 ('STC_CSS_DIRECTIVE', 'directive_style'),
                 ('STC_CSS_DOUBLESTRING', 'string_style'),
                 ('STC_CSS_ID', 'scalar_style'),
                 ('STC_CSS_IDENTIFIER', 'keyword4_style'),
                 ('STC_CSS_IDENTIFIER2', 'keyword3_style'),
                 ('STC_CSS_IMPORTANT', 'error_style'),
                 ('STC_CSS_OPERATOR', 'operator_style'),
                 ('STC_CSS_PSEUDOCLASS', 'scalar_style'),
                 ('STC_CSS_SINGLESTRING', 'string_style'),
                 ('STC_CSS_TAG', 'keyword_style'),
                 ('STC_CSS_UNKNOWN_IDENTIFIER', 'unknown_style'),
                 ('STC_CSS_UNKNOWN_PSEUDOCLASS', 'unknown_style'),
                 ('STC_CSS_VALUE', 'char_style') ]

#---- Extra Properties ----#
fold = ("fold", "1")
#------------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [ess_keywords]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [fold]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return list()
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
