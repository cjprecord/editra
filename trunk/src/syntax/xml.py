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
# FILE: xml.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for XML Files.                                   #
#                                                                             #
# TODO:                                                                       #
# Almost Everything                                                           #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependencies
import synglob

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Xml Keywords
xml_keywords = ("rss atom pubDate channel version title link description "
                 "language generator item")

# SGML Keywords
import html
sgml_keywords = html.KeywordString(synglob.ID_LANG_SGML)

#---- Syntax Style Specs ----#
syntax_items = html.syntax_items

#---- Extra Properties ----#
# See html.py
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns Keyword Specifications List"""
    KEYWORDS = [(5, xml_keywords), (6, sgml_keywords)]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    return syntax_items

def Properties(type=0):
    """Extra Properties"""
    return [ html.fold ]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the keyword string"""
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
