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
# FILE: asm.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file GNU Assembly Code                                  #
#                                                                             #
# @todo: Complete Keywords/Registers                                          #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

# GNU Assembly CPU Instructions/Storage Types
asm_cpu_inst = (0, ".long .ascii .asciz .byte .double .float .hword .int .octa "
                   ".quad .short .single .space .string .word")

# GNU FPU Instructions
asm_math_inst = (1, "")

# GNU Registers
asm_register = (2, "")

# GNU Assembly Directives/Special statements/Macros
asm_directives = (3, ".include .macro .endm")

#---- Language Styling Specs ----#
syntax_items = [ ('STC_ASM_DEFAULT', 'default_style'),
                 ('STC_ASM_CHARACTER', 'char_style'),
                 ('STC_ASM_COMMENT', 'comment_style'),
                 ('STC_ASM_COMMENTBLOCK', 'comment_style'),
                 ('STC_ASM_CPUINSTRUCTION', 'keyword_style'),
                 ('STC_ASM_DIRECTIVE', 'keyword3_style'),
                 ('STC_ASM_DIRECTIVEOPERAND', 'default_style'),
                 ('STC_ASM_EXTINSTRUCTION', 'default_style'),
                 ('STC_ASM_IDENTIFIER', 'default_style'),
                 ('STC_ASM_MATHINSTRUCTION', 'keyword_style'),
                 ('STC_ASM_NUMBER', 'number_style'),
                 ('STC_ASM_OPERATOR', 'operator_style'),
                 ('STC_ASM_REGISTER', 'keyword2_style'),
                 ('STC_ASM_STRING', 'string_style'),
                 ('STC_ASM_STRINGEOL', 'stringeol_style') ]
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns List of Keyword Specifications
    @param lang_id: used to select specific subset of keywords

    """
    return [asm_cpu_inst, asm_directives]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return []

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [ u';' ]
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
