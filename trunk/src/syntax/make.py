###############################################################################
#    Copyright (C) 2007 Editra Development Team                               #
#    staff@editra.org                                                         #
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
# FILE: make.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Makefiles.                                   #
#                                                                             #
# TODO:                                                                       #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# No keywords

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_MAKE_DEFAULT', 'default_style'),
                 ('STC_MAKE_COMMENT', 'comment_style'),
                 ('STC_MAKE_IDENTIFIER', "scalar_style"),
                 ('STC_MAKE_IDEOL', 'ideol_style'),
                 ('STC_MAKE_OPERATOR', 'operator_style'),
                 ('STC_MAKE_PREPROCESSOR', "pre_style"),
                 ('STC_MAKE_TARGET', 'keyword_style') ]

#--- Extra Properties ----#
# None

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Keyword Lists"""
    KEYWORDS = []
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    return syntax_items

def Properties(type=0):
    """Property Settings"""
    return []

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u'#' ]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
