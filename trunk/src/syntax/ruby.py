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
# FILE: ruby.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Ruby.                                        #
#                                                                             #
# TODO:                                                                       #
# Default Style Refinement.                                                   #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Ruby Keywords
ruby_kw = (0, "__FILE__ and def end in or self unless __LINE__ begin defined? "
              "ensure module redo super until BEGIN break do false next rescue "
              "then when END case else for nil retry true while alias class elsif "
              "if not return undef yieldr")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_RB_BACKTICKS', 'scalar_style'),
                 ('STC_RB_CHARACTER', 'char_style'),
                 ('STC_RB_CLASSNAME', 'class_style'),
                 ('STC_RB_CLASS_VAR', 'default_style'), # STYLE ME
                 ('STC_RB_COMMENTLINE', 'comment_style'),
                 ('STC_RB_DATASECTION', 'default_style'), # STYLE ME
                 ('STC_RB_DEFAULT', 'default_style'),
                 ('STC_RB_DEFNAME', 'keyword3_style'), # STYLE ME
                 ('STC_RB_ERROR', 'error_style'),
                 ('STC_RB_GLOBAL', 'global_style'),
                 ('STC_RB_HERE_DELIM', 'default_style'), # STYLE ME
                 ('STC_RB_HERE_Q', 'here_style'), 
                 ('STC_RB_HERE_QQ', 'here_style'),
                 ('STC_RB_HERE_QX', 'here_style'),
                 ('STC_RB_IDENTIFIER', 'default_style'),
                 ('STC_RB_INSTANCE_VAR', 'scalar2_style'),
                 ('STC_RB_MODULE_NAME', 'global_style'), # STYLE ME
                 ('STC_RB_NUMBER', 'number_style'),
                 ('STC_RB_OPERATOR', 'operator_style'),
                 ('STC_RB_POD', 'default_style'), # STYLE ME
                 ('STC_RB_REGEX', 'regex_style'), # STYLE ME
                 ('STC_RB_STDIN', 'default_style'), # STYLE ME
                 ('STC_RB_STDOUT', 'default_style'), # STYLE ME
                 ('STC_RB_STRING', 'string_style'),
                 ('STC_RB_STRING_Q', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QQ', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QR', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QW', 'default_style'), # STYLE ME
                 ('STC_RB_STRING_QX', 'default_style'), # STYLE ME
                 ('STC_RB_SYMBOL', 'default_style'), # STYLE ME
                 ('STC_RB_UPPER_BOUND', 'default_style'), # STYLE ME
                 ('STC_RB_WORD', 'keyword_style'),
                 ('STC_RB_WORD_DEMOTED', 'keyword2_style') ]

#---- Extra Properties ----#
fold = ("fold", "1")
timmy = ("fold.timmy.whinge.level", "1")
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns Keyword Specifications List"""
    KEYWORDS = [ruby_kw]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    return syntax_items

def Properties(type=0):
    """Properties"""
    return [ fold, timmy ]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the keyword string"""
    return ruby_kw[1]

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
