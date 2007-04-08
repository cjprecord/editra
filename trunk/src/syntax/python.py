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
# FILE: python.py                                                             #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Python.                                      #
#                                                                             #
# TODO:                                                                       #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependancies
import keyword

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Python Keywords
kw = keyword.kwlist
kw.extend(['True', 'False', 'None', 'self'])
py_kw = (0, " ".join(kw))

# Highlighted Identifiers
py_id = (1, "")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_P_DEFAULT', 'default_style'),
                 ('STC_P_CHARACTER', 'char_style'),
                 ('STC_P_CLASSNAME', 'class_style'),
                 ('STC_P_COMMENTBLOCK', 'comment_style'),
                 ('STC_P_COMMENTLINE', 'comment_style'),
                 ('STC_P_DECORATOR', 'default_style'),
                 ('STC_P_DEFNAME', 'keyword3_style'),
                 ('STC_P_IDENTIFIER', 'default_style'),
                 ('STC_P_NUMBER', 'number_style'),
                 ('STC_P_OPERATOR', 'operator_style'),
                 ('STC_P_STRING', 'string_style'),
                 ('STC_P_STRINGEOL', 'stringeol_style'),
                 ('STC_P_TRIPLE', 'string_style'),
                 ('STC_P_TRIPLEDOUBLE', 'string_style'),
                 ('STC_P_WORD', 'keyword_style'),
                 ('STC_P_WORD2', 'default_style')]

#---- Extra Properties ----#
fold = ("fold", "1")
timmy = ("tab.timmy.whinge.level", "1") # Mark Inconsistant indentation

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns Keyword Specifications List"""
    KEYWORDS = [py_kw]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns Syntax Specifications List"""
    return syntax_items

def Properties(type=0):
    """Returns Extra Properties to set"""
    return [ fold, timmy ]

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u'#' ]

#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the keyword string"""
    return py_kw[1]

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
