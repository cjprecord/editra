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
# FILE: mssql.py                                                              #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Microsoft SQL.                               #
#                                                                             #
# @todo: too many to list                                                     #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Data Types
MSSQL_DAT = (0, "")
# System Tables
MSSQL_SYS = (1, "")
# Global Variables
MSSQL_GLOB = (2, "")
# Functions
MSSQL_FUNC = (3, "")
# System Stored Procedures
MSSQL_SYSP = (4, "")
# Operators
MSSQL_OPS = (5, "")

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [ ('STC_MSSQL_DEFAULT', 'default_style'),
                 ('STC_MSSQL_COMMENT', 'comment_style'),
                 ('STC_MSSQL_COLUMN_NAME', 'keyword_style'),
                 ('STC_MSSQL_COLUMN_NAME_2', 'keyword_style'),
                 ('STC_MSSQL_DATATYPE', 'keyword2_style'),
                 ('STC_MSSQL_DEFAULT_PREF_DATATYPE', 'class_style'),
                 ('STC_MSSQL_FUNCTION', 'keyword3_style'),
                 ('STC_MSSQL_GLOBAL_VARIABLE', 'global_style'),
                 ('STC_MSSQL_IDENTIFIER', 'default_style'),
                 ('STC_MSSQL_LINE_COMMENT', 'comment_style'),
                 ('STC_MSSQL_NUMBER', 'number_style'),
                 ('STC_MSSQL_OPERATOR', 'operator_style'),
                 ('STC_MSSQL_STATEMENT', 'keyword_style'),
                 ('STC_MSSQL_STORED_PROCEDURE', 'scalar2_style'),
                 ('STC_MSSQL_STRING', 'string_style'),
                 ('STC_MSSQL_SYSTABLE', 'keyword4_style'),
                 ('STC_MSSQL_VARIABLE', 'scalar_style') ]

#---- Extra Properties ----#
FOLD = ("fold", "1")

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return list()

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return SYNTAX_ITEMS

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [FOLD]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [u'--']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
