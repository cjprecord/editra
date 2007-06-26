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
# FILE: tcl.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for tcl                                          #
#                                                                             #
# TODO:                                                                       #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

import synglob
#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
tcl_kw = (0, "after append array auto_execok auto_import auto_load auto_load_index "
              "auto_qualify beep bgerror binary break case catch cd clock "
              "close concat continue dde default echo else elseif encoding eof "
              "error eval exec exit expr fblocked fconfigure fcopy file fileevent "
              "flush for foreach format gets glob global history http if incr info "
              "interp join lappend lindex linsert list llength load loadTk lrange "
              "lreplace lsearch lset lsort memory msgcat namespace open package pid "
              "pkg::create pkg_mkIndex Platform-specific proc puts pwd re_syntax "
              "read regexp registry regsub rename resource return scan seek set "
              "socket source split string subst switch tclLog tclMacPkgSearch "
              "tclPkgSetup tclPkgUnknown tell time trace unknown unset update "
              "uplevel upvar variable vwait while")

tk_kw = (1, "bell bind bindtags bitmap button canvas checkbutton clipboard "
             "colors console cursors destroy entry event focus font frame grab "
             "grid image Inter-client keysyms label labelframe listbox lower "
             "menu menubutton message option options pack panedwindow photo place "
             "radiobutton raise scale scrollbar selection send spinbox text tk "
             "tk_chooseColor tk_chooseDirectory tk_dialog tk_focusNext tk_getOpenFile "
             "tk_messageBox tk_optionMenu tk_popup tk_setPalette tkerror tkvars "
             "tkwait toplevel winfo wish wm")

itcl_kw = (2, "@scope body class code common component configbody constructor "
               "define destructor hull import inherit itcl itk itk_component "
               "itk_initialize itk_interior itk_option iwidgets keep method "
               "private protected public")

tkCommands = (3, "tk_bisque tk_chooseColor tk_dialog tk_focusFollowsMouse "
                  "tk_focusNext tk_focusPrev tk_getOpenFile tk_getSaveFile "
                  "tk_messageBox tk_optionMenu tk_popup tk_setPalette tk_textCopy "
                  "tk_textCut tk_textPaste tkButtonAutoInvoke tkButtonDown "
                  "tkButtonEnter tkButtonInvoke tkButtonLeave tkButtonUp "
                  "tkCancelRepeat tkCheckRadioDown tkCheckRadioEnter "
                  "tkCheckRadioInvoke tkColorDialog tkColorDialog_BuildDialog "
                  "tkColorDialog_CancelCmd tkColorDialog_Config tkColorDialog_CreateSelector "
                  "tkColorDialog_DrawColorScale tkColorDialog_EnterColorBar "
                  "tkColorDialog_HandleRGBEntry tkColorDialog_HandleSelEntry "
                  "tkColorDialog_InitValues tkColorDialog_LeaveColorBar "
                  "tkColorDialog_MoveSelector tkColorDialog_OkCmd "
                  "tkColorDialog_RedrawColorBars tkColorDialog_RedrawFinalColor "
                  "tkColorDialog_ReleaseMouse tkColorDialog_ResizeColorBars "
                  "tkColorDialog_RgbToX tkColorDialog_SetRGBValue tkColorDialog_StartMove "
                  "tkColorDialog_XToRgb tkConsoleAbout tkConsoleBind tkConsoleExit "
                  "tkConsoleHistory tkConsoleInit tkConsoleInsert tkConsoleInvoke "
                  "tkConsoleOutput tkConsolePrompt tkConsoleSource tkDarken tkEntryAutoScan "
                  "tkEntryBackspace tkEntryButton1 tkEntryClosestGap tkEntryGetSelection "
                  "tkEntryInsert tkEntryKeySelect tkEntryMouseSelect tkEntryNextWord "
                  "tkEntryPaste tkEntryPreviousWord tkEntrySeeInsert tkEntrySetCursor "
                  "tkEntryTranspose tkEventMotifBindings tkFDGetFileTypes tkFirstMenu "
                  "tkFocusGroup_BindIn tkFocusGroup_BindOut tkFocusGroup_Create "
                  "tkFocusGroup_Destroy tkFocusGroup_In tkFocusGroup_Out tkFocusOK "
                  "tkGenerateMenuSelect tkIconList tkIconList_Add tkIconList_Arrange "
                  "tkIconList_AutoScan tkIconList_Btn1 tkIconList_Config tkIconList_Create "
                  "tkIconList_CtrlBtn1 tkIconList_Curselection tkIconList_DeleteAll "
                  "tkIconList_Double1 tkIconList_DrawSelection tkIconList_FocusIn "
                  "tkIconList_FocusOut tkIconList_Get tkIconList_Goto tkIconList_Index "
                  "tkIconList_Invoke tkIconList_KeyPress tkIconList_Leave1 "
                  "tkIconList_LeftRight tkIconList_Motion1 tkIconList_Reset "
                  "tkIconList_ReturnKey tkIconList_See tkIconList_Select "
                  "tkIconList_Selection tkIconList_ShiftBtn1 tkIconList_UpDown tkListbox "
                  "tkListboxAutoScan tkListboxBeginExtend tkListboxBeginSelect "
                  "tkListboxBeginToggle tkListboxCancel tkListboxDataExtend "
                  "tkListboxExtendUpDown tkListboxKeyAccel_Goto tkListboxKeyAccel_Key "
                  "tkListboxKeyAccel_Reset tkListboxKeyAccel_Set tkListboxKeyAccel_Unset "
                  "tkListboxMotion tkListboxSelectAll tkListboxUpDown tkMbButtonUp "
                  "tkMbEnter tkMbLeave tkMbMotion tkMbPost tkMenuButtonDown tkMenuDownArrow "
                  "tkMenuDup tkMenuEscape tkMenuFind tkMenuFindName tkMenuFirstEntry "
                  "tkMenuInvoke tkMenuLeave tkMenuLeftArrow tkMenuMotion tkMenuNextEntry "
                  "tkMenuNextMenu tkMenuRightArrow tkMenuUnpost tkMenuUpArrow tkMessageBox "
                  "tkMotifFDialog tkMotifFDialog_ActivateDList tkMotifFDialog_ActivateFEnt "
                  "tkMotifFDialog_ActivateFList tkMotifFDialog_ActivateSEnt "
                  "tkMotifFDialog_BrowseDList tkMotifFDialog_BrowseFList "
                  "tkMotifFDialog_BuildUI tkMotifFDialog_CancelCmd tkMotifFDialog_Config "
                  "tkMotifFDialog_Create tkMotifFDialog_FileTypes tkMotifFDialog_FilterCmd "
                  "tkMotifFDialog_InterpFilter tkMotifFDialog_LoadFiles tkMotifFDialog_MakeSList "
                  "tkMotifFDialog_OkCmd tkMotifFDialog_SetFilter tkMotifFDialog_SetListMode "
                  "tkMotifFDialog_Update tkPostOverPoint tkRecolorTree tkRestoreOldGrab "
                  "tkSaveGrabInfo tkScaleActivate tkScaleButton2Down tkScaleButtonDown "
                  "tkScaleControlPress tkScaleDrag tkScaleEndDrag tkScaleIncrement "
                  "tkScreenChanged tkScrollButton2Down tkScrollButtonDown tkScrollButtonDrag "
                  "tkScrollButtonUp tkScrollByPages tkScrollByUnits tkScrollDrag tkScrollEndDrag "
                  "tkScrollSelect \tkScrollStartDrag tkScrollTopBottom tkScrollToPos "
                  "tkTabToWindow tkTearOffMenu tkTextAutoScan tkTextButton1 tkTextClosestGap "
                  "tkTextInsert tkTextKeyExtend \tkTextKeySelect tkTextNextPara tkTextNextPos "
                  "tkTextNextWord tkTextPaste tkTextPrevPara tkTextPrevPos tkTextPrevWord "
                  "tkTextResetAnchor tkTextScrollPages tkTextSelectTo tkTextSetCursor "
                  "tkTextTranspose tkTextUpDownLine tkTraverseToMenu tkTraverseWithinMenu")

expand = (4, "")

user1_kw = (5, "")

user2_kw = (6, "")

user3_kw = (7, "")

user4_kw = (8, "")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
syntax_items = [('STC_TCL_BLOCK_COMMENT', 'comment_style'),
                 ('STC_TCL_COMMENT', 'comment_style'),
                 ('STC_TCL_COMMENTLINE', 'comment_style'),
                 ('STC_TCL_COMMENT_BOX', 'comment_style'),
                 ('STC_TCL_DEFAULT', 'default_style'),
                 ('STC_TCL_EXPAND', 'default_style'), # TODO
                 ('STC_TCL_IDENTIFIER', 'default_style'),
                 ('STC_TCL_IN_QUOTE', 'string_style'),
                 ('STC_TCL_MODIFIER', 'default_style'), # TODO
                 ('STC_TCL_NUMBER', 'number_style'),
                 ('STC_TCL_OPERATOR', 'operator_style'),
                 ('STC_TCL_SUBSTITUTION', 'scalar_style'),
                 ('STC_TCL_SUB_BRACE', 'default_style'), # TODO
                 ('STC_TCL_WORD', 'keyword_style'),        # tcl_kw
                 ('STC_TCL_WORD2', 'keyword2_style'),      # tk_kw
                 ('STC_TCL_WORD3', 'keyword3_style'),      # itcl_kw
                 ('STC_TCL_WORD4', 'keyword4_style'),      # tkCommands
                 ('STC_TCL_WORD5', 'default_style'),
                 ('STC_TCL_WORD6', 'default_style'),
                 ('STC_TCL_WORD7', 'default_style'),
                 ('STC_TCL_WORD8', 'default_style'),
                 ('STC_TCL_WORD_IN_QUOTE', 'default_style')]

#---- Extra Properties ----#
fold = ("fold", 1)
fold_comment = ("fold.comment", 1)

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    return [tcl_kw, tk_kw, itcl_kw, tkCommands]

def SyntaxSpec(langId=0):
    """Syntax Specifications
    @param langId: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(langId=0):
    """Returns a list of Extra Properties to set
    @param langId: used to select a specific set of properties

    """
    return [fold, fold_comment]

def CommentPattern(langId=0):
    """Returns a list of characters used to comment a block of code
    @param langId: used to select a specific subset of comment pattern(s)

    """
    return [u'#']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
