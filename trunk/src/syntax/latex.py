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

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependancies


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
# There are no keyword settings available for LaTeXt

#---- Syntax Style Specs ----#
# TeX
syntax_items = [ ('STC_TEX_DEFAULT', 'default_style'),
                 ('STC_TEX_COMMAND', 'keyword_style'),
                 ('STC_TEX_GROUP', 'scalar_style'),
                 ('STC_TEX_SPECIAL', 'operator_style'),
                 ('STC_TEX_SYMBOL', 'number_style'),
                 ('STC_TEX_TEXT', 'default_style') ]

#---- Extra Properties ----#
# None
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns Keyword Specifications List"""
    KEYWORDS = [tex_kw]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications List"""
    return syntax_items

def Properties(type=0):
    """Extra Properties"""
    return []

#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the keyword string"""
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
