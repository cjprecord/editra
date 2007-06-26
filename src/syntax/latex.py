###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
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
# FILE: latex.py                                                              #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Tex/LaTex.                                   #
#                                                                             #
# TODO:                                                                       #
# Fairly poor needs lots of work.                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependancies
import synglob

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Tex Keywords
tex_kw = (0, "Downarrow backslash lceil rceil Uparrow downarrow lfloor rfloor "
             "Updownarrow langle rangle Vert")
# ConTeXt Dutch
dutch = (1, "")
# ConTeXt English
eng = (2, "")
# ConTeXt German
german = (3, "")
# ConTeXt Czech
czech = (4, "")
# ConTeXt Italian
italian = (5, "")
# ConTeXt Romanian
romanian = (6, "")

# LaTeXt
# There are no keyword settings available for LaTeX

#---- Syntax Style Specs ----#
# TeX
syntax_items1 = [ ('STC_TEX_DEFAULT', 'default_style'),
                 ('STC_TEX_COMMAND', 'keyword_style'),
                 ('STC_TEX_GROUP', 'scalar_style'),
                 ('STC_TEX_SPECIAL', 'operator_style'),
                 ('STC_TEX_SYMBOL', 'number_style'),
                 ('STC_TEX_TEXT', 'default_style') ]

# LaTeX
syntax_items2 = [ ('STC_L_DEFAULT', 'default_style'),
                 ('STC_L_COMMAND', 'pre_style'),
                 ('STC_L_COMMENT', 'comment_style'),
                 ('STC_L_MATH', 'operator_style'),
                 ('STC_L_TAG', 'keyword_style')]

#---- Extra Properties ----#
# None
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    if langId == synglob.ID_LANG_TEX:
        return [tex_kw]
    else:
        return list()

def SyntaxSpec(langId=0):
    """Syntax Specifications
    @param langId: used for selecting a specific subset of syntax specs

    """
    if langId == synglob.ID_LANG_TEX:
        return syntax_items1
    else:
        return syntax_items2

def Properties(langId=0):
    """Returns a list of Extra Properties to set
    @param langId: used to select a specific set of properties

    """
    return []

def CommentPattern(langId=0):
    """Returns a list of characters used to comment a block of code
    @param langId: used to select a specific subset of comment pattern(s)

    """
    return [u'%']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
