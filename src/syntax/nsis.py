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
# FILE: nsis.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Nullsoft Installer Scripts.                  #
#                                                                             #
# @todo: Add User Defined KW                                                  #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# NSIS Functions
nsis_funct = (0, "!addincludedir !addplugindir MakeNSIS Portions Contributors: "
                 "Abort AddBrandingImage AddSize AutoCloseWindow BGFont BGGradient "
                 "BrandingText BringToFront Call CallInstDLL Caption ChangeUI "
                 "ClearErrors ComponentText GetDLLVersion GetDLLVersionLocal "
                 "GetFileTime GetFileTimeLocal CopyFiles CRCCheck CreateDirectory "
                 "CreateFont CreateShortCut SetDatablockOptimize DeleteINISec "
                 "DeleteINIStr DeleteRegKey DeleteRegValue Delete DetailPrint "
                 "DirText DirShow DirVar DirVerify GetInstDirError "
                 "AllowRootDirInstall CheckBitmap EnableWindow EnumRegKey "
                 "EnumRegValue Exch Exec ExecWait ExecShell ExpandEnvStrings "
                 "FindWindow FindClose FindFirst FindNext File FileBufSize "
                 "FlushINI ReserveFile FileClose FileErrorText FileOpen FileRead "
                 "FileWrite FileReadByte FileWriteByte FileSeek Function FunctionEnd "
                 "GetDlgItem GetFullPathName GetTempFileName HideWindow Icon IfAbort "
                 "IfErrors IfFileExists IfRebootFlag IfSilent InstallDirRegKey "
                 "InstallColors InstallDir InstProgressFlags InstType IntOp IntCmp "
                 "IntCmpU IntFmt IsWindow Goto LangString LangStringUP LicenseData "
                 "LicenseForceSelection LicenseLangString LicenseText LicenseBkColor "
                 "LoadLanguageFile LogSet LogText MessageBox Nop Name OutFile Page "
                 "PageCallbacks PageEx PageExEnd Pop Push Quit ReadINIStr "
                 "ReadRegDWORD ReadRegStr ReadEnvStr Reboot RegDLL Rename Return "
                 "RMDir Section SectionEnd SectionIn SubSection SectionGroup "
                 "SubSectionEnd SectionGroupEnd SearchPath SectionSetFlags "
                 "SectionGetFlags SectionSetInstTypes SectionGetInstTypes "
                 "SectionGetText SectionSetText SectionGetSize SectionSetSize "
                 "GetCurInstType SetCurInstType InstTypeSetText InstTypeGetText "
                 "SendMessage SetAutoClose SetCtlColors SetBrandingImage SetCompress "
                 "SetCompressor SetCompressorDictSize SetCompressionLevel "
                 "SetDateSave SetDetailsView SetDetailsPrint SetErrors SetErrorLevel "
                 "GetErrorLevel SetFileAttributes SetFont SetOutPath SetOverwrite "
                 "SetPluginUnload SetRebootFlag SetShellVarContext SetSilent "
                 "ShowInstDetails ShowUninstDetails ShowWindow SilentInstall "
                 "SilentUnInstall Sleep StrCmp StrCpy StrLen SubCaption "
                 "UninstallExeName UninstallCaption UninstallIcon UninstPage "
                 "UninstallText UninstallSubCaption UnRegDLL WindowIcon WriteINIStr "
                 "WriteRegBin WriteRegDWORD WriteRegStr WriteRegExpandStr "
                 "WriteUninstaller XPStyle !packhdr !system !execute !AddIncludeDir "
                 "!include !cd !ifdef !ifndef !endif !define !undef !else !echo "
                 "!warning !error !verbose !macro !macroend !insertmacro !ifmacrodef "
                 "!ifmacrondef MiscButtonText DetailsButtonText UninstallButtonText "
                 "InstallButtonText SpaceTexts CompletedText GetFunctionAddress "
                 "GetLabelAddress GetCurrentAddress !AddPluginDir InitPluginsDir "
                 "AllowSkipFiles Var VIAddVersionKey VIProductVersion LockWindow "
                 "ShowUnInstDetails WriteIniStr")

# NSIS Variables/Constants
nsis_var = (1, "$0 $1 $2 $3 $4 $5 $6 $7 $8 $9 $R0 $R1 $R2 $R3 $R4 $R5 $R6 $R7 $R8 "
               "$R9 $\t $\" $\' $\` $VARNAME $0, $INSTDIR $OUTDIR $CMDLINE $LANGUAGE "
               "$PROGRAMFILES $COMMONFILES $DESKTOP $EXEDIR ${NSISDIR} $WINDIR "
               "$SYSDIR $TEMP $STARTMENU $SMPROGRAMS $SMSTARTUP $QUICKLAUNCH "
               "$DOCUMENTS $SENDTO $RECENT $FAVORITES $MUSIC $PICTURES $VIDEOS "
               "$NETHOOD $FONTS $TEMPLATES $APPDATA $PRINTHOOD $INTERNET_CACHE "
               "$COOKIES $HISTORY $PROFILE $ADMINTOOLS $RESOURCES $RESOURCES_LOCALIZED "
               "$CDBURN_AREA $HWNDPARENT $PLUGINSDIR $$ $\r $\n")

# NSIS Lables (Attributes)
nsis_lbl = (2, "ARCHIVE FILE_ATTRIBUTE_ARCHIVE FILE_ATTRIBUTE_HIDDEN "
               "FILE_ATTRIBUTE_NORMAL FILE_ATTRIBUTE_OFFLINE FILE_ATTRIBUTE_READONLY "
               "FILE_ATTRIBUTE_SYSTEM FILE_ATTRIBUTE_TEMPORARY HIDDEN HKCC HKCR "
               "HKCU HKDD HKEY_CLASSES_ROOT HKEY_CURRENT_CONFIG HKEY_CURRENT_USER "
               "HKEY_DYN_DATA HKEY_LOCAL_MACHINE HKEY_PERFORMANCE_DATA HKEY_USERS "
               "HKLM HKPD HKU IDABORT IDCANCEL IDIGNORE IDNO IDOK IDRETRY IDYES "
               "MB_ABORTRETRYIGNORE MB_DEFBUTTON1 MB_DEFBUTTON2 MB_DEFBUTTON3 "
               "MB_DEFBUTTON4 MB_ICONEXCLAMATION MB_ICONINFORMATION MB_ICONQUESTION "
               "MB_ICONSTOP MB_OK MB_OKCANCEL MB_RETRYCANCEL MB_RIGHT "
               "MB_SETFOREGROUND MB_TOPMOST MB_YESNO MB_YESNOCANCEL NORMAL OFFLINE "
               "READONLY SW_SHOWMAXIMIZED SW_SHOWMINIMIZED SW_SHOWNORMAL SYSTEM "
               "TEMPORARY auto colored false force hide ifnewer nevershow normal off "
               "on show silent silentlog smooth true try lzma zlib bzip2 none listonly "
               "textonly both top left bottom right license components directory "
               "instfiles uninstConfirm custom all leave current ifdiff lastused LEFT "
               "RIGHT CENTER dlg_id ALT CONTROL EXT SHIFT open print manual alwaysoff")

# NSIS User Defined (Not sure need help)
nsis_def = (3, "")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_NSIS_DEFAULT', 'default_style'),
                 ('STC_NSIS_COMMENT', 'comment_style'),
                 ('STC_NSIS_FUNCTION', 'funct_style'),
                 ('STC_NSIS_FUNCTIONDEF', 'keyword_style'),
                 ('STC_NSIS_IFDEFINEDEF', 'pre_style'),
                 ('STC_NSIS_LABEL', 'class_style'),
                 ('STC_NSIS_MACRODEF', 'pre_style'),
                 ('STC_NSIS_NUMBER', 'number_style'),
                 ('STC_NSIS_SECTIONDEF', 'keyword_style'),
                 ('STC_NSIS_STRINGDQ', 'string_style'),
                 ('STC_NSIS_STRINGLQ', 'string_style'),
                 ('STC_NSIS_STRINGRQ', 'string_style'),
                 ('STC_NSIS_STRINGVAR', 'string_style'),
                 ('STC_NSIS_SUBSECTIONDEF', 'keyword_style'),
                 ('STC_NSIS_USERDEFINED', 'pre_style'),
                 ('STC_NSIS_VARIABLE', 'scalar_style') ]

#---- Extra Properties ----#
fold = ("fold", "1")
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [nsis_funct, nsis_var, nsis_lbl]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [fold]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [u';']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
