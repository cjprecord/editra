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
# FILE: masm.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file Microsoft Assembly Code                            #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#

# MASM CPU Instructions/Operators
masm_cpu_inst = (0, "AAA AAD AAM AAS ADC AND ARPL BOUND BSF BSR BSWAP BT BTC "
                    "BTR BTS CALL CDW CDQ CLC CLD CLI CLTS CMC CMP CMPS CMPSB "
                    "CMPSW CMPSD CMPXCHG CWD CWDE DAA DAS ENTER IN INS INSB "
                    "INSW INSD INT INTO INVD INVLPG IRET IRETD JA JAE JB JBE "
                    "JC JCXZ JECXZ JE JZ JG JGE JL JLE JNA JNAE JNB JNBE JNC "
                    "JNE JNG JNGE JNL JNLE JNO JNP JNS JNZ JO JP JPE JPO JS JZ "
                    "JMP LAHF LAR LEA LEAVE LGDT LIDT LGS LSS LFS LODS LODSB "
                    "LODSW LODSD LOOP LOOPE LOOPZ LOONE LOOPNE RETF RETN LDS "
                    "LES LLDT LMSW LOCK LSL LTR MOV MOVS MOVSB MOVSW MOVSD "
                    "MOVSX MOVZX NEG NOP NOT OR OUT OUTS OUTSB OUTSW OUTSD "
                    "POP POPA POPD POPF POPFD PUSH PUSHA PUSHAD PUSHF PUSHFD "
                    "RCL RCR ROL RORO REP REPE REPZ REPNE REPNZ RET SAHF SAL "
                    "SAR SHL SHR SBB SCAS SCASB SCASW SCASD SETA SETAE SETB "
                    "SETBE SETC SETE SETG SETGE SETL SETLE SETNA SETNAE SETNB "
                    "SETNBE SETNC SETNE SETNG SETNGE SETNL SETNLE SETNO SETNP "
                    "SETNS SETNZ SETO SETP SETPE SETPO SES SETZ SGDT SIDT SHLD "
                    "SHRD SLDT SMSW STC STD STI STOS STOSB STOSW STOSD STR "
                    "TEST VERR VERW WAIT WBINVD XCHG XLAT XLATB XOR ADD DEC DIV "
                    "IDIV IMUL INC MUL SUB XADD "
                    # MMX/SSE/SSE2 Instructions
                    "cflush cpuid emms femms cmovo cmovno cmovb cmovc cmovnae "
                    "cmovae cmovnb cmovnc cmove cmovz cmovne cmovnz cmovbe "
                    "cmovna cmova cmovnbe cmovs cmovns cmovp cmovpe cmovnp "
                    "cmovpo cmovl cmovnge cmovge cmovnl cmovle cmovng cmovg "
                    "cmovnle cmpxchg486 cmpxchg8b loadall loadall286 ibts icebp "
                    "int1 int3 int01 int03 iretw popaw popfw pushaw pushfw rdmsr "
                    "rdpmc rdshr rdtsc rsdc rsldt rsm rsts salc smi smint "
                    "smintold svdc svldt svts syscall sysenter sysexit sysret "
                    "ud0 ud1 ud2 umov xbts wrmsr wrshr")

# floating point instructions
masm_fpu_inst = (1, "f2xm1 fabs fadd faddp fbld fbstp fchs fclex fcom fcomp "
                    "fcompp fdecstp fdisi fdiv fdivp fdivr fdivrp feni ffree "
                    "fiadd ficom ficomp fidiv fidivr fild fimul fincstp finit "
                    "fist fistp fisub fisubr fld fld1 fldcw fldenv fldenvw fldl2e "
                    "fldl2t fldlg2 fldln2 fldpi fldz fmul fmulp fnclex fndisi "
                    "fneni fninit fnop fnsave fnsavew fnstcw fnstenv fnstenvw "
                    "fnstsw fpatan fprem fptan frndint frstor frstorw fsave fsavew "
                    "fscale fsqrt fst fstcw fstenv fstenvw fstp fstsw fsub fsubp "
                    "fsubr fsubrp ftst fwait fxam fxch fxtract fyl2x fyl2xp1 fsetpm "
                    "fcos fldenvd fnsaved fnstenvd fprem1 frstord fsaved fsin "
                    "fsincos fstenvd fucom fucomp fucompp fcomi fcomip ffreep "
                    "fcmovb fcmove fcmovbe fcmovu fcmovnb fcmovne fcmovnbe fcmovnu ")

masm_registers = (2, "ah al ax bh bl bp bx ch cl cr0 cr2 cr3 cr4 cs cx dh di dl "
                     "dr0 dr1 dr2 dr3 dr6 dr7 ds dx eax ebp ebx ecx edi edx es "
                     "esi esp fs gs si sp ss st tr3 tr4 tr5 tr6 tr7 st0 st1 st2 "
                     "st3 st4 st5 st6 st7 mm0 mm1 mm2 mm3 mm4 mm5 mm6 mm7 xmm0 "
                     "xmm1 xmm2 xmm3 xmm4 xmm5 xmm6 xmm7")

masm_directives = (3, ".186 .286 .286c .286p .287 .386 .386c .386p .387 .486 "
                      ".486p .8086 .8087 .alpha .break .code .const .continue "
                      ".cref .data .data? .dosseg .else .elseif .endif .endw "
                      ".err .err1 .err2 .errb .errdef .errdif .errdifi .erre "
                      ".erridn .erridni .errnb .errndef .errnz .exit .fardata "
                      ".fardata? .if .lall .lfcond .list .listall .listif "
                      ".listmacro .listmacroall  .model .no87 .nocref .nolist "
                      ".nolistif .nolistmacro .radix .repeat .sall .seq "
                      ".sfcond .stack .startup .tfcond .type .until .untilcxz "
                      ".while .xall .xcref .xlist alias align assume catstr "
                      "comm comment db dd df dosseg dq dt dup dw echo else "
                      "elseif elseif1 elseif2 elseifb elseifdef elseifdif "
                      "elseifdifi elseife elseifidn elseifidni elseifnb "
                      "elseifndef end endif endm endp ends eq equ even exitm "
                      "extern externdef extrn for forc ge goto group gt high "
                      "highword if if1 if2 ifb ifdef ifdif ifdifi ife ifidn "
                      "ifidni ifnb ifndef include includelib instr invoke irp "
                      "irpc label le length lengthof local low lowword lroffset "
                      "lt macro mask mod .msfloat name ne offset opattr option "
                      "org %out page popcontext proc proto ptr public purge "
                      "pushcontext record repeat rept seg segment short size "
                      "sizeof sizestr struc struct substr subtitle subttl "
                      "textequ this title type typedef union while width")

masm_direc_op = (4, "$ ? @b @f addr basic byte c carry? dword far far16 fortran "
                    "fword near near16 overflow? parity? pascal qword real4 real8 "
                    "real10 sbyte sdword sign? stdcall sword syscall tbyte vararg "
                    "word zero? flat near32 far32 abs all assumes at casemap common "
                    "compact cpu dotname emulator epilogue error export expr16 "
                    "expr32 farstack flat forceframe huge language large listing "
                    "ljmp loadds m510 medium memory nearstack nodotname noemulator "
                    "nokeyword noljmp nom510 none nonunique nooldmacros nooldstructs "
                    "noreadonly noscoped nosignextend nothing notpublic oldmacros "
                    "oldstructs os_dos para private prologue radix readonly req "
                    "scoped setif2 smallstack tiny use16 use32 uses")

masm_ext_inst = (5, "addpd addps addsd addss andpd andps andnpd andnps cmpeqpd "
                    "cmpltpd cmplepd cmpunordpd cmpnepd cmpnltpd cmpnlepd cmpordpd "
                    "cmpeqps cmpltps cmpleps cmpunordps cmpneps cmpnltps cmpnleps "
                    "cmpordps cmpeqsd cmpltsd cmplesd cmpunordsd cmpnesd cmpnltsd "
                    "cmpnlesd cmpordsd cmpeqss cmpltss cmpless cmpunordss cmpness "
                    "cmpnltss cmpnless cmpordss comisd comiss cvtdq2pd cvtdq2ps "
                    "cvtpd2dq cvtpd2pi cvtpd2ps cvtpi2pd cvtpi2ps cvtps2dq cvtps2pd "
                    "cvtps2pi cvtss2sd cvtss2si cvtsd2si cvtsd2ss cvtsi2sd cvtsi2ss "
                    "cvttpd2dq cvttpd2pi cvttps2dq cvttps2pi cvttsd2si cvttss2si "
                    "divpd divps divsd divss fxrstor fxsave ldmxscr lfence mfence "
                    "maskmovdqu maskmovdq maxpd maxps paxsd maxss minpd minps minsd "
                    "minss movapd movaps movdq2q movdqa movdqu movhlps movhpd movhps "
                    "movd movq movlhps movlpd movlps movmskpd movmskps movntdq movnti "
                    "movntpd movntps movntq movq2dq movsd movss movupd movups mulpd "
                    "mulps mulsd mulss orpd orps packssdw packsswb packuswb paddb "
                    "paddsb paddw paddsw paddd paddsiw paddq paddusb paddusw pand "
                    "pandn pause paveb pavgb pavgw pavgusb pdistib pextrw pcmpeqb "
                    "pcmpeqw pcmpeqd pcmpgtb pcmpgtw pcmpgtd pf2id pf2iw pfacc pfadd "
                    "pfcmpeq pfcmpge pfcmpgt pfmax pfmin pfmul pmachriw pmaddwd "
                    "pmagw pmaxsw pmaxub pminsw pminub pmovmskb pmulhrwc pmulhriw "
                    "pmulhrwa pmulhuw pmulhw pmullw pmuludq pmvzb pmvnzb pmvlzb "
                    "pmvgezb pfnacc pfpnacc por prefetch prefetchw prefetchnta "
                    "prefetcht0 prefetcht1 prefetcht2 pfrcp pfrcpit1 pfrcpit2 "
                    "pfrsqit1 pfrsqrt pfsub pfsubr pi2fd pf2iw pinsrw psadbw pshufd "
                    "pshufhw pshuflw pshufw psllw pslld psllq pslldq psraw psrad "
                    "psrlw psrld psrlq psrldq psubb psubw psubd psubq psubsb psubsw "
                    "psubusb psubusw psubsiw pswapd punpckhbw punpckhwd punpckhdq "
                    "punpckhqdq punpcklbw punpcklwd punpckldq punpcklqdq pxor rcpps "
                    "rcpss rsqrtps rsqrtss sfence shufpd shufps sqrtpd sqrtps "
                    "sqrtsd sqrtss stmxcsr subpd subps subsd subss ucomisd ucomiss "
                    "unpckhpd unpckhps unpcklpd unpcklps xorpd xorps")

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
    KEYWORDS = [masm_cpu_inst, masm_fpu_inst, masm_registers, masm_directives,
                 masm_direc_op, masm_ext_inst]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns a list of syntax specifications"""
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
