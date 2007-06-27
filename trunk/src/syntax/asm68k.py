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
# FILE: asm68k.py                                                             #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file 68k Assembly Code                                  #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#

asm_cpu_inst = (0, "andi and as b beq bg b bl bne bge bpl bchg bclr bfchg bfclr "
                   "bfexts bfextu bfffo bfins bfset bftst bkpt bra bset bsr "
                   "btst callm cas2 cas chk2 chk clr cmpa cmpi cmpm cmp dbcc "
                   "dbcs dbvc dbvs dbeq dbf dbt dbge dbgt dbhi dbmi dble dbls "
                   "dblt dbne dbpl dbra eori eor exg extb ext illegaljmp jsr "
                   "lea link ls mm movea movec movem movep moveq moves move nbcd "
                   "negx neg nop not ori or pack pea reset ro rox rt sbcd seq "
                   "sne spl swap tas trap tst unlk unpk")

asm_math_inst = (1, "adda addi addq addx add div mul suba subi subq subx sub "
                     "tdiv")

asm_register = (2, "a0 a1 a2 a3 a4 a5 a6 a7 d0 d1 d2 d3 d4 d5 d6 d7 pc sr "
                   "ccr sp usp ssp vbr sfc sfcr dfc dfcr msp isp zpc cacr "
                   "caar za0 za1 za2 za3 za4 za5 za6 za7 zd0 zd1 zd2 zd3 "
                   "zd4 zd5 zd6 zd7 crp srp tc ac0 ac1 acusr tt0 tt1 mmusr "
                   "dtt0 dtt1 itt0 itt1 urp cal val scc crp srp drp tc ac psr "
                   "pcsr bac0 bac1 bac2 bac3 bac4 bac5 bac6 bac7 bad0 bad1 "
                   "bad2 bad3 bad4 bad5 bad6 bad7 fp0 fp1 fp2 fp3 fp4 fp5 fp6 "
                   "fp7 control status iaddr fpcr fpsr fpiar ")

asm_directives = (3, "ALIGN CHIP COMLINE COMMON DC DCB DS END EQU FEQU FAIL "
                     "FOPT IDNT LLEN MASK2 NAME NOOBJ OFFSET OPT ORG PLEN REG "
                     "RESTORE SAVE SECT SECTION SET SPC TTL XCOM XDEF XREF")
 
#---- Language Styling Specs ----#
syntax_items = [ ('STC_ASM_DEFAULT', 'default_style'),
                 ('STC_ASM_CHARACTER', 'char_style'),
                 ('STC_ASM_COMMENT', 'comment_style'),
                 ('STC_ASM_COMMENTBLOCK', 'comment_style'),
                 ('STC_ASM_CPUINSTRUCTION', 'keyword_style'),
                 ('STC_ASM_DIRECTIVE', 'keyword3_style'),
                 ('STC_ASM_DIRECTIVEOPERAND', 'keyword4_style'),
                 ('STC_ASM_EXTINSTRUCTION', 'funct_style'),
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
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [asm_cpu_inst, asm_math_inst, asm_register, asm_directives]

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
