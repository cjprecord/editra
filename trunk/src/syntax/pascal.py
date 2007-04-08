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
# FILE: pascal.py                                                             #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Pacal.                                       #
#                                                                             #
# TODO:                                                                       #
# Currently configured for Traditional Pascal add Support for Turbo Pascal    #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Pascal Keywords
pas_keywords = (0, "and array asm begin case cdecl class const constructor "
                   "default destructor div do downto else end end. except exit "
                   "exports external far file finalization finally for function "
                   "goto if implementation in index inherited initialization "
                   "inline interface label library message mod near nil not "
                   "object of on or out overload override packed pascal private "
                   "procedure program property protected public published raise "
                   "read record register repeat resourcestring safecall set shl "
                   "shr stdcall stored string then threadvar to try type unit "
                   "until uses var virtual while with write xor")

# Pascal Classwords (Types)
pas_classwords = (1, "array boolean char integer file pointer real set string "
                    "text variant write read default public protected private "
                    "property published stored")

# Pascal Std Functions
pas_funct = ("pack unpack Dispose New Abs Arctan Cos Exp Ln Sin Sqr Sqrt Eof "
             "Eoln Write Writeln Input Output Get Page Put Odd Pred Succ Chr "
             "Ord Round Trunc")

#---- Syntax Style Specs ----#
# Pascal Lexer Uses C values, but need to adjust styles accordingly
# TODO test these styles the are probably a bit off
syntax_items = [ ('STC_C_DEFAULT', 'default_style'),
                 ('STC_C_COMMENT', 'comment_style'),
                 ('STC_C_COMMENTDOC', 'comment_style'),
                 ('STC_C_COMMENTDOCKEYWORD', 'dockey_style'),
                 ('STC_C_COMMENTDOCKEYWORDERROR', 'error_style'),
                 ('STC_C_COMMENTLINE', 'comment_style'),
                 ('STC_C_COMMENTLINEDOC', 'comment_style'),
                 ('STC_C_CHARACTER', 'char_style'),
                 ('STC_C_GLOBALCLASS', 'global_style'),
                 ('STC_C_IDENTIFIER', 'default_style'),
                 ('STC_C_NUMBER', 'number_style'),
                 ('STC_C_OPERATOR', 'operator_style'),
                 ('STC_C_PREPROCESSOR', 'pre_style'),
                 ('STC_C_REGEX', 'pre_style'),
                 ('STC_C_STRING', 'string_style'),
                 ('STC_C_STRINGEOL', 'stringeol_style'),
                 ('STC_C_UUID', 'pre_style'),
                 ('STC_C_VERBATIM', "number2_style"),
                 ('STC_C_WORD', 'keyword_style'),
                 ('STC_C_WORD2', 'keyword2_style') ]

#---- Extra Properties ----#
fld_comment = ("fold.comment", "1")

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns a list of keyword parameters"""
    KEYWORDS = [pas_keywords, pas_classwords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns a list of Syntax Style Specifications"""
    return syntax_items

def Properties(type=0):
    """Returns a list of extra properties to set"""
    return [ fld_comment ]

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u'{', u'}' ]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
