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
# FILE: ada.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for ada                                          #
#                                                                             #
# TODO: styles, keywords, testing                                             #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
ada_keywords = (0, "abort abstract accept access aliased all array at begin "
                    "body case constant declare delay delta digits do else "
                    "elsif end entry exception exit for function generic goto "
                    "if in is limited loop new null of others out package pragma "
                    "private procedure protected raise range record renames "
                    "requeue return reverse select separate subtype tagged task "
                    "terminate then type until use when while with")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
syntax_items = [('STC_ADA_CHARACTER', 'char_style'),
                 ('STC_ADA_CHARACTEREOL', 'stringeol_style'),
                 ('STC_ADA_COMMENTLINE', 'comment_style'),
                 ('STC_ADA_DEFAULT', 'default_style'),
                 ('STC_ADA_DELIMITER', 'operator_style'),
                 ('STC_ADA_IDENTIFIER', 'default_style'),
                 ('STC_ADA_ILLEGAL', 'error_style'),
                 ('STC_ADA_LABEL', 'keyword2_style'),   #TODO
                 ('STC_ADA_NUMBER', 'number_style'),
                 ('STC_ADA_STRING', 'string_style'),
                 ('STC_ADA_STRINGEOL', 'stringeol_style'),
                 ('STC_ADA_WORD', 'keyword_style')]

#---- Extra Properties ----#

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns Specified Keywords List"""
    KEYWORDS = [ada_keywords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    return syntax_items

def Properties(type=0):
    """Property Settings"""
    return []
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String"""
    # Unused by this module, stubbed in for consistancy
    return None

#---- End Syntax Modules Internal Functions ----#
