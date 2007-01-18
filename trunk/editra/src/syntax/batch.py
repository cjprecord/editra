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
# FILE: batch.py                                                              #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file for dos/windows batch scripts.                     #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

dosbat_keywords = (0, "goto call exit if else for EQU NEQ LSS LEQ GTR GEQ "
                      "append assoc at attrib break cacls cd chcp chdir chkdsk "
                      "chkntfs cls cmd color comp compact convert copy date del "
                      "dir diskcomp diskcopy doskey echo endlocal erase fc find "
                      "findstr format ftype graftabl help keyb label md mkdir "
                      "mode more move path pause popd print prompt pushd rd "
                      "rem ren rename replace restore rmdir set setlocal shift "
                      "sort start subst time title tree type ver verify vol "
                      "xcopy")

# WinBatch Keywords (TODO still incomplete)
winbat_keywords = (0, "if then else endif break end return exit next while for "
                      "gosub goto switch select to case endselect endwhile "
                      "endswitch aboveicons acc_attrib acc_chng_nt acc_control "
                      "acc_create acc_delete acc_full_95 acc_full_nt acc_list "
                      "acc_pfull_nt acc_pmang_nt acc_print_nt acc_read "
                      "acc_read_95 acc_read_nt acc_write amc arrange ascending "
                      "attr_a attr_a attr_ci attr_ci attr_dc attr_dc attr_di "
                      "attr_di attr_dm attr_dm attr_h attr_h attr_ic attr_ic "
                      "attr_p attr_p attr_ri attr_ri attr_ro attr_ro attr_sh " 
                      "attr_sh attr_sy attr_sy attr_t attr_t attr_x attr_x "
                      "avogadro backscan boltzmann cancel capslock check "
                      "columnscommonformat cr crlf ctrl default default deg2rad "
                      "descending disable drive electric enable eulers false "
                      "faraday float8 fwdscan gftsec globalgroup gmtsec "
                      "goldenratio gravitation hidden icon lbutton lclick "
                      "ldblclick lf lightmps lightmtps localgroup magfield "
                      "major mbokcancel mbutton mbyesno mclick mdblclick minor "
                      "msformat multiple ncsaformat no none none noresize normal "
                      "notify nowait numlock off on open parsec parseonly pi "
                      "planckergs planckjoules printer rad2deg rbutton rclick "
                      "rdblclick regclasses regcurrent regmachine regroot "
                      "regusers rows save scrolllock server shift single sorted "
                      "stack string tab tile true uncheck unsorted wait "
                      "wholesection word1 word2 word4 yes zoomed about abs "
                      "acos addextender appexist appwaitclose asin askfilename "
                      "askfiletext askitemlist askline askpassword askyesno atan "
                      "average beep binaryalloc binarycopy binaryeodget "
                      "binaryeodset binaryfree binaryhashrec binaryincr "
                      "binaryincr2 binaryincr4 binaryincrflt binaryindex "
                      "binaryindexnc binaryoletype binarypeek binarypeek2 "
                      "binarypeek4 binarypeekflt binarypeekstr binarypoke "
                      "binarypoke2 binarypoke4 binarypokeflt binarypokestr "
                      "binaryread binarysort binarystrcnt binarywrite "
                      "boxbuttondraw boxbuttonkill boxbuttonstat boxbuttonwait "
                      "boxcaption boxcolor boxdataclear boxdatatag boxdestroy "
                      "boxdrawcircle boxdrawline boxdrawrect boxdrawtext boxesup "
                      "boxmapmode boxnew boxopen boxpen boxshut boxtext "
                      "boxtextcolor boxtextfont boxtitle boxupdates break "
                      "buttonnames by call callext ceiling char2num clipappend "
                      "clipget clipput continue cos cosh datetime ddeexecute "
                      "ddeinitiate ddepoke dderequest ddeterminate ddetimeout "
                      "debug debugdata decimals delay dialog dialogbox dirattrget "
                      "dirattrset dirchange direxist")

#---- Language Styling Specs ----#
syntax_items = [ ('STC_BAT_DEFAULT', "default_style"),
                 ('STC_BAT_COMMAND', "class_style"),
                 ('STC_BAT_COMMENT', "comment_style"),
                 ('STC_BAT_HIDE', "string_style"),
                 ('STC_BAT_IDENTIFIER', "scalar_style"),
                 ('STC_BAT_LABEL', "class_style"),
                 ('STC_BAT_OPERATOR', "operator_style"),
                 ('STC_BAT_WORD', "keyword_style") ]
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns List of Keyword Specifications"""
    KEYWORDS = [dosbat_keywords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Returns a List of Syntax Item Specifications"""
    SYNTAX = syntax_items
    return SYNTAX

#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String"""
    # Unused by this module, stubbed in for consistancy
    return None

#---- End Syntax Modules Internal Functions ----#
