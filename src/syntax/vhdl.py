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
# FILE: vhdl.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for VHDL.                                        #
# Very High Scale Integrated Circuit Hardware Description Language            #
#                                                                             #
# TODO:                                                                       #
# Maybe add highlighting for values S0S, S1S, ect..                           #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# VHDL Keywords
vhdl_kw = (0, "access after alias all assert architecture array attribute begin "
              "block body buffer bus case component configuration constant if else "
              "disconnect downto elsif end entity exit file for funciton generate "
              "generic group guarded impure in inertial inout is label library "
              "linkage literal loop map new next null of on open others out "
              "package port postponed procedure process pure range record "
              "register reject report return select severity signal shared "
              "subtype then to transport type unaffected units until use variable "
              "wait when while with note warning error failure true false")
# VHDL Operators
vhdl_op = (1, "and nand or nor xor xnor rol ror sla sll sra srl mod rem abs not ")

# VHDL Attributes
vhdl_at = (2, "'high 'left 'length 'low 'range 'reverse_range 'right 'ascending "
              "'behavior 'structure 'simple_name 'instance_name 'path_name 'foreign "
              "'active 'delayed 'event 'last_active 'last_event 'last_value 'quiet "
              "'stable 'transaction 'driving 'driving_value 'base 'high 'left 'leftof "
              "'low 'pos 'pred 'rightof 'succ 'val 'image 'value")
# Standard Functions
vhdl_stdf = (3, "now readline read writeline write endfile resolved to_bit "
                "to_bitvector to_stdulogic to_stdlogicvector to_stdulogicvector "
                "to_x01 to_x01z to_UX01 rising_edge falling_edge is_x shift_left "
                "shift_right rotate_left rotate_right resize to_integer "
                "to_unsigned to_signed std_match to_01 ")
# Standard Packages
vhdl_stdp = (4, "std ieee work standard textio std_logic_1164 std_logic_arith "
                "std_logic_misc std_logic_signed std_logic_textio std_logic_unsigned "
                "numeric_bit numeric_std math_complex math_real vital_primitives "
                "vital_timing ")
# Standard Types
vhdl_stdt = (5, "bit bit_vector character boolean integer real time string "
                "severity_level positive natural signed unsigned line text "
                "std_logic std_logic_vector std_ulogic std_ulogic_vector "
                "qsim_state qsim_state_vector qsim_12state qsim_12state_vector "
                "qsim_strength mux_bit mux_vector reg_bit reg_vector wor_bit "
                "wor_vector")
# User Words
vhdl_ukw = (6, "")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_VHDL_DEFAULT', 'default_style'),
                 ('STC_VHDL_STRINGEOL', 'stringeol_style'),
                 ('STC_VHDL_COMMENT', 'comment_style'),
                 ('STC_VHDL_COMMENTLINEBANG', 'comment_style'),
                 ('STC_VHDL_IDENTIFIER', 'default_style'),
                 ('STC_VHDL_KEYWORD', 'keyword_style'),
                 ('STC_VHDL_NUMBER', 'default_style'),
                 ('STC_VHDL_OPERATOR', 'operator_style'),
                 ('STC_VHDL_STDFUNCTION', 'funct_style'),
                 ('STC_VHDL_STDOPERATOR', 'operator_style'),
                 ('STC_VHDL_STDPACKAGE', 'pre_style'),
                 ('STC_VHDL_STDTYPE', 'class_style'),
                 ('STC_VHDL_STRING', 'string_style'),
                 ('STC_VHDL_STRINGEOL', 'stringeol_style'),
                 ('STC_VHDL_USERWORD', 'default_style') ]

#---- Extra Property Specifications ----#
fold = ("fold", "1")
fld_comment = ("fold.comment", "1")
fld_compact = ("fold.compact", "1")
fld_atelse  = ("fold.at.else", "1")
fld_atbegin = ("fold.at.Begin", "1")
fld_atparen = ("fold.at.Parenthese", "1")

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    return [vhdl_kw, vhdl_at, vhdl_stdf, vhdl_stdp, vhdl_stdt]

def SyntaxSpec(langId=0):
    """Syntax Specifications
    @param langId: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(langId=0):
    """Returns a list of Extra Properties to set
    @param langId: used to select a specific set of properties

    """
    return [fold]

def CommentPattern(langId=0):
    """Returns a list of characters used to comment a block of code
    @param langId: used to select a specific subset of comment pattern(s)

    """
    return [u'--']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
