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
# FILE: haskell.py                                                            #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for the Haskell Programming Language             #
#                                                                             #
# @todo: more custom highlighting                                             #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

import synglob
#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
HA_KEYWORDS = (0, "as case class data default deriving do forall foreign "
                  "hiding if import in infix infixl infixr instance else let "
                  "mdo module newtype of qualified then type where")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [('STC_HA_CAPITAL', 'default_style'),
                ('STC_HA_CHARACTER', 'char_style'),
                ('STC_HA_CLASS', 'class_style'),
                ('STC_HA_COMMENTBLOCK', 'comment_style'),
                ('STC_HA_COMMENTBLOCK2', 'comment_style'),
                ('STC_HA_COMMENTBLOCK3', 'comment_style'),
                ('STC_HA_COMMENTLINE', 'comment_style'),
                ('STC_HA_DATA', 'default_style'),
                ('STC_HA_DEFAULT', 'default_style'),
                ('STC_HA_IDENTIFIER', 'default_style'),
                ('STC_HA_IMPORT', 'default_style'), # possibly use custom style
                ('STC_HA_INSTANCE', 'default_style'),
                ('STC_HA_KEYWORD', 'keyword_style'),
                ('STC_HA_MODULE', 'default_style'),
                ('STC_HA_NUMBER', 'number_style'),
                ('STC_HA_OPERATOR', 'operator_style'),
                ('STC_HA_STRING', 'string_style')]

#---- Extra Properties ----#
FOLD = ('fold', '1')
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @keyword lang_id: used to select specific subset of keywords

    """
    if lang_id == synglob.ID_LANG_HASKELL:
        return [HA_KEYWORDS]
    else:
        return list()

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @keyword lang_id: used for selecting a specific subset of syntax specs

    """
    if lang_id == synglob.ID_LANG_HASKELL:
        return SYNTAX_ITEMS
    else:
        return list()

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @keyword lang_id: used to select a specific set of properties

    """
    if lang_id == synglob.ID_LANG_HASKELL:
        return [FOLD]
    else:
        return list()

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @keyword lang_id: used to select a specific subset of comment pattern(s)

    """
    if lang_id == synglob.ID_LANG_HASKELL:
        return [u'--']
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
