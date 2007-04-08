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
# FILE: nasm.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file Netwide Assembly Code                              #
#                                                                             #
# TODO:                                                                       #
#   Add mmx, sse, 3dnow, cyrix, amd instruction sets
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#

# NASM CPU Instructions
nasm_cpu_inst = (0, "CMPS MOVS LCS LODS STOS XLAT AAA AAD AAM ADC AND BOUND "
                    "BSF BSR BSWAP BT BTC BTR BTS CALL CBW CDQ CLC CLD CMC CMP "
                    "CMPSB CMPSD CMPSW CMPXCHG CMPXCHG8B CPUID CWD CWDE DAA "
                    "DAS ENTER INT IRET IRETW JCXZ JECXZ JMP LAHF LDS LEA "
                    "LEAVE LES LFS LGS LODSB LODSD LODSW LOOP LOOPE LOOPNE "
                    "LOOPNZ LOOPZ LSS MOVSB MOVSD MOVSW MOVSX MOVZX NEG NOP "
                    "NOT OR POPA POPAD POPAW POPF POPFD POPFW PUSH PUSHA "
                    "PUSHD PUSHAW PUSHF PUSHFD PUSHFW RCL RCR RETF RET RETN "
                    "ROL ROR SAHF SAL SAR SBB SCASB SCASD SCASW SHL SHLD SHRD "
                    "STC STD STOSB STOSD STOSW TEST XCHG XLATB XOR ARPL LAR "
                    "LSL VERR VERW LLDT SLDT LGDT SGDT LTR STR CLTS LOCK WAIT "
                    "INS OUTS IN INSB INSW INSD OUT OUTSB OUTSW OUTSD CLI STI "
                    "LIDT SIDT HLT INVD LMSW PREFETCHT0 PREFETCHT1 PREFETCHT2 "
                    "PREFETCHNTA RSM SFENCE SMSW SYSENTER SYSEXIT UD2 WBINVD "
                    "INVLPG INT1 INT3 RDMSR RDTSC RDPMC WRMSR ADD DEC DIV IDIV "
                    "IMUL INC MUL SUB XADDF2XM1 "
                    )

# NASM FPU Instructions
nasm_fpu_inst = (1, "FCHS FCLEX FCOM FCOMP FDECSTP FDISI FENI FFREE FICOM FILD "
                    "FINIT FIST FLD FLDCW FLDENV FLDL2E FLDL2E FLDL2T FLDLG2 "
                    "FLDLN2 FLDPI FLDZ FSAVE FSCALE FSETPM FRNDINT FRSTOR FSAVE "
                    "FSCALE FSETPM FSTCW FSTENV FSTS FSTSW FTST FUCOM FUCOMP "
                    "FXAM FXCH FXTRACT FYL2X FYL2XP1"" FABS FADD FADDP FBLD FBSTP"
                    "FCOS FDIV FDIVR FIADD FIDIV FIMUL FISUB FMUL FPATAN FPTAN "
                    "FSIN FSINCOS FSQRT FSUB FSUBR")

# NASM Registers
nasm_registers = (2, "ah al ax bh bl bp bx ch cl cr0 cr2 cr3 cr4 cs cx dh di dl "
                     "dr0 dr1 dr2 dr3 dr6 dr7 ds dx eax ebp ebx ecx edi edx es "
                     "esi esp fs gs si sp ss st tr3 tr4 tr5 tr6 tr7 st0 st1 st2 "
                     "st3 st4 st5 st6 st7 mm0 mm1 mm2 mm3 mm4 mm5 mm6 mm7 xmm0 "
                     "xmm1 xmm2 xmm3 xmm4 xmm5 xmm6 xmm7")

# NASM Directives
nasm_directives = (3, "DF EXTRN FWORD RESF TBYTE FAR NEAR SHORT BYTE WORD DWORD "
                      "QWORD DQWORD HWORD DHWORD TWORD CDECL FASTCALL NONE "
                      "PASCAL STDCALL DB DW DD DQ DDQ DT RESB RESW RESD RESQ "
                      "REST EXTERN GLOBAL COMMON __BITS__ __DATE__ __FILE__ "
                      "__FORMAT__ __LINE__ __NASM_MAJOR__ __NASM_MINOR__ "
                      "__NASM_VERSION__ __TIME__ TIMES ALIGN ALIGNB INCBIN "
                      "EQU NOSPLIT SPLIT ABSOLUTE BITS SECTION SEGMENT "
                      "ENDSECTION ENDSEGMENT __SECT__ ENDPROC EPILOGUE LOCALS "
                      "PROC PROLOGUE USES ENDIF ELSE ELIF ELSIF IF DO ENDFOR "
                      "ENDWHILE FOR REPEAT UNTIL WHILE EXIT ORG EXPORT GROUP "
                      "UPPERCASE SEG WRT LIBRARY _GLOBAL_OFFSET_TABLE_ "
                      "__GLOBAL_OFFSET_TABLE_ ..start ..got ..gotoff ..gotpc "
                      "..pit ..sym %define %idefine %xdefine %xidefine %undef "
                      "%assign %iassign %strlen %substr %macro %imacro "
                      "%endmacro %rotate .nolist %if %elif %else %endif %ifdef "
                      "%ifndef %elifdef %elifndef %ifmacro %ifnmacro %elifmacro "
                      "%elifnmacro %ifctk %ifnctk %elifctk %elifnctk %ifidn "
                      "%ifnidn %elifidn %elifnidn %ifidni %ifnidni %elifidni "
                      "%elifnidni %ifid %ifnid %elifid %elifnid %ifstr %ifnstr "
                      "%elifstr %elifnstr %ifnum %ifnnum %elifnum %elifnnum "
                      "%error %rep %endrep %exitrep %include %push %pop %repl "
                      "struct endstruc istruc at iend align alignb %arg "
                      "%stacksize %local %line bits use16 use32 section "
                      "absolute extern global common cpu org section group "
                      "import export")

nasm_direc_op = (4, "a16 a32 o16 o32 byte word dword nosplit $ $$ seq wrt flat "
                    "large small .text .data .bss near far %0 %1 %2 %3 %4 %5 %6 "
                    "%7 %8 %9")

nasm_ext_inst = (5, "")

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
def Keywords(type=0):
    """Returns List of Keyword Specifications"""
    KEYWORDS = [nasm_cpu_inst, nasm_fpu_inst, nasm_registers, nasm_directives,
                nasm_direc_op]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns a list of Syntax Specifications"""
    SYNTAX = syntax_items
    return SYNTAX

def Properties(type=0):
    """Returns a list of Extra Properties to set"""
    return []

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u';' ]
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String"""
    # Unused by this module, stubbed in for consistancy
    return None

#---- End Syntax Modules Internal Functions ----#
