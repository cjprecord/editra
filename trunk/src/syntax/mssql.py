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
# TODO:                                                                       #
# Somebody know Microsoft SQL?                                                #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Data Types
mssql_dat = (0, "")
# System Tables
mssql_sys = (1, "")
# Global Variables
mssql_glob = (2, "")
# Functions
mssql_func = (3, "")
# System Stored Procedures
mssql_sysp = (4, "")
# Operators
mssql_ops = (5, "")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_MSSQL_DEFAULT', 'default_style'),
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
fold = ("fold", "1")

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns Keyword Specifications List"""
    KEYWORDS = []
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns a list of syntax specs"""
    return syntax_items

def Properties(type=0):
    """Returns a list of extra properties"""
    return [ fold ]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the keyword string"""
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
