###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
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
# FILE: visualbasic.py                                                        #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Visual Basic.                                #
#                                                                             #
# TODO:                                                                       #
# Incomplete requires color/kw tuning                                         #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Visual Basic Keywords (Statements)
vb_kw = (0, "AppActivate Base Beep Begin Call Case ChDir ChDrive Const Declare DefBool"
            "DefByte DefCur DefDate DefDbl DefDec DefInt DefLng DefObj DefSng "
            "DefStr Deftype DefVar DeleteSetting Dim Do Else End Enum Erase "
            "Event Exit Explicit FileCopy For ForEach Function Get GoSub GoTo "
            "If Implements Kill Let LineInput Lock LSet MkDir Name Next OnError "
            "On Option Private Property Public Put RaiseEvent Randomize ReDim "
            "Rem Reset Resume Return RmDir RSet SavePicture SaveSetting "
            "SendKeys SetAttr Static Sub Then Type Unlock Wend While Width With "
            "Write Height")
# Visual Basic User Keywords 1 (Functions)
vb_ukw1 = (1, "Abs Array Asc AscB AscW Atn Avg CBool CByte CCur CDate CDbl Cdec "
              "Choose Chr ChrB ChrW CInt CLng Command Cos Count CreateObject "
              "CSng CStr CurDir CVar CVDate CVErr Date DateAdd DateDiff "
              "DatePart DateSerial DateValue Day DDB Dir DoEvents Environ EOF "
              "Error Exp FileAttr FileDateTime FileLen Fix Format FreeFile FV "
              "GetAllStrings GetAttr GetAutoServerSettings GetObject GetSetting "
              "Hex Hour IIf IMEStatus Input InputB InputBox InStr InstB Int "
              "IPmt IsArray IsDate IsEmpty IsError IsMissing IsNull IsNumeric "
              "IsObject LBound LCase Left LeftB Len LenB LoadPicture Loc LOF "
              "Log LTrim Max Mid MidB Min Minute MIRR Month MsgBox Now NPer NPV "
              "Oct Partition Pmt PPmt PV QBColor Rate RGB Right RightB Rnd "
              "RTrim Second Seek Sgn Shell Sin SLN Space Spc Sqr StDev StDevP "
              "Str StrComp StrConv String Switch Sum SYD Tab Tan Time Timer "
              "TimeSerial TimeValue Trim TypeName UBound UCase Val Var VarP "
              "VarType Weekday Year")
# Visual Basic User Keywords 2 (Methods)
vb_ukw2 = (2, "Accept Activate Add AddCustom AddFile AddFromFile AddFromTemplate "
              "AddItem AddNew AddToAddInToolbar AddToolboxProgID Append AppendChunk "
              "Arrange Assert AsyncRead BatchUpdate BeginTrans Bind Cancel "
              "CancelAsyncRead CancelBatch CancelUpdate CanPropertyChange "
              "CaptureImage CellText CellValue Circle Clear ClearFields ClearSel "
              "ClearSelCols Clone Close Cls ColContaining ColumnSize CommitTrans "
              "CompactDatabase Compose Connect Copy CopyQueryDef CreateDatabase "
              "CreateDragImage CreateEmbed CreateField CreateGroup CreateIndex "
              "CreateLink CreatePreparedStatement CreatePropery "
              "CreateQueryCreateQueryDef CreateRelation CreateTableDef CreateUser "
              "CreateWorkspace Customize Delete DeleteColumnLabels DeleteColumns "
              "DeleteRowLabels DeleteRows DoVerb Drag Draw Edit EditCopy EditPaste "
              "EndDoc EnsureVisible EstablishConnection Execute ExtractIcon Fetch "
              "FetchVerbs Files FillCache Find FindFirst FindItem FindLast FindNext "
              "FindPrevious Forward GetBookmark GetChunk GetClipString GetData "
              "GetFirstVisible GetFormat GetHeader GetLineFromChar GetNumTicks "
              "GetRows GetSelectedPart GetText GetVisibleCount GoBack GoForward "
              "Hide HitTest HoldFields Idle InitializeLabels InsertColumnLabels "
              "InsertColumns InsertObjDlg InsertRowLabels InsertRows Item KillDoc "
              "Layout Line LinkExecute LinkPoke LinkRequest LinkSend Listen LoadFile "
              "LoadResData LoadResPicture LoadResString LogEvent MakeCompileFile "
              "MakeReplica MoreResults Move MoveData MoveFirst MoveLast MoveNext "
              "MovePrevious NavigateTo NewPage NewPassword NextRecordset OLEDrag "
              "OnAddinsUpdate OnConnection OnDisconnection OnStartupComplete Open "
              "OpenConnection OpenDatabase OpenQueryDef OpenRecordset OpenResultset "
              "OpenURL Overlay PaintPicture Paste PastSpecialDlg PeekData Play Point "
              "PopulatePartial PopupMenu Print PrintForm PropertyChanged PSet Quit "
              "Raise RandomDataFill RandomFillColumns RandomFillRows "
              "rdoCreateEnvironment rdoRegisterDataSource ReadFromFile ReadProperty "
              "Rebind ReFill Refresh RefreshLink RegisterDatabase Reload Remove "
              "RemoveAddInFromToolbar RemoveItem Render RepairDatabase Reply "
              "ReplyAll Requery ResetCustom ResetCustomLabel ResolveName "
              "RestoreToolbar Resync Rollback RollbackTrans RowBookmark RowContaining "
              "RowTop Save SaveAs SaveFile SaveToFile SaveToolbar SaveToOle1File "
              "Scale ScaleX ScaleY Scroll Select SelectAll SelectPart SelPrint Send "
              "SendData Set SetAutoServerSettings SetData SetFocus SetOption SetSize "
              "SetText SetViewport Show ShowColor ShowFont ShowHelp ShowOpen "
              "ShowPrinter ShowSave ShowWhatsThis SignOff SignOn Size Span "
              "SplitContaining StartLabelEdit StartLogging Stop Synchronize "
              "TextHeight TextWidth ToDefaults TwipsToChartPart TypeByChartType "
              "Update UpdateControls UpdateRecord UpdateRow Upto WhatsThisMode "
              "WriteProperty ZOrder")
# Visual Basic User Keywords 3 (Events)
vb_ukw3 = (3, "AccessKeyPress AfterAddFile AfterChangeFileName AfterCloseFile "
              "AfterColEdit AfterColUpdate AfterDelete AfterInsert AfterLabelEdit "
              "AfterRemoveFile AfterUpdate AfterWriteFile AmbienChanged "
              "ApplyChanges Associate AsyncReadComplete AxisActivated "
              "AxisLabelActivated AxisLabelSelected AxisLabelUpdated AxisSelected "
              "AxisTitleActivated AxisTitleSelected AxisTitleUpdated AxisUpdated "
              "BeforeClick BeforeColEdit BeforeColUpdate BeforeConnect BeforeDelete "
              "BeforeInsert BeforeLabelEdit BeforeLoadFile BeforeUpdate ButtonClick "
              "ButtonCompleted ButtonGotFocus ButtonLostFocus Change ChartActivated "
              "ChartSelected ChartUpdated Click ColEdit Collapse ColResize "
              "ColumnClick Compare ConfigChageCancelled ConfigChanged "
              "ConnectionRequest DataArrival DataChanged DataUpdated DblClick "
              "Deactivate DeviceArrival DeviceOtherEvent DeviceQueryRemove "
              "DeviceQueryRemoveFailed DeviceRemoveComplete DeviceRemovePending "
              "DevModeChange Disconnect DisplayChanged Dissociate DoGetNewFileName "
              "Done DonePainting DownClick DragDrop DragOver DropDown EditProperty "
              "EnterCell EnterFocus ExitFocus Expand FootnoteActivated "
              "FootnoteSelected FootnoteUpdated GotFocus HeadClick InfoMessage "
              "Initialize IniProperties ItemActivated ItemAdded ItemCheck "
              "ItemClick ItemReloaded ItemRemoved ItemRenamed ItemSeletected "
              "KeyDown KeyPress KeyUp LeaveCell LegendActivated LegendSelected "
              "LegendUpdated LinkClose LinkError LinkNotify LinkOpen Load LostFocus "
              "MouseDown MouseMove MouseUp NodeClick ObjectMove OLECompleteDrag "
              "OLEDragDrop OLEDragOver OLEGiveFeedback OLESetData OLEStartDrag "
              "OnAddNew OnComm Paint PanelClick PanelDblClick PathChange "
              "PatternChange PlotActivated PlotSelected PlotUpdated PointActivated "
              "PointLabelActivated PointLabelSelected PointLabelUpdated "
              "PointSelected PointUpdated PowerQuerySuspend PowerResume "
              "PowerStatusChanged PowerSuspend QueryChangeConfig QueryComplete "
              "QueryCompleted QueryTimeout QueryUnload ReadProperties Reposition "
              "RequestChangeFileName RequestWriteFile Resize ResultsChanged "
              "RowColChange RowCurrencyChange RowResize RowStatusChanged SelChange "
              "SelectionChanged SendComplete SendProgress SeriesActivated "
              "SeriesSelected SeriesUpdated SettingChanged SplitChange StateChanged "
              "StatusUpdate SysColorsChanged Terminate TimeChanged TitleActivated "
              "TitleSelected TitleActivated UnboundAddData UnboundDeleteRow "
              "UnboundGetRelativeBookmark UnboundReadData UnboundWriteData Unload "
              "UpClick Updated Validate ValidationError WillAssociate WillChangeData "
              "WillDissociate WillExecute WillUpdateRows WriteProperties")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_B_ASM', 'asm_style'),
                 ('STC_B_BINNUMBER', 'default_style'), # TODO
                 ('STC_B_COMMENT', 'comment_style'),
                 ('STC_B_CONSTANT', 'const_style'),
                 ('STC_B_DATE', 'default_style'), #TODO
                 ('STC_B_DEFAULT', 'default_style'),
                 ('STC_B_ERROR', 'error_style'),
                 ('STC_B_HEXNUMBER', 'number_style'),
                 ('STC_B_IDENTIFIER', 'default_style'),
                 ('STC_B_KEYWORD', 'keyword_style'),
                 ('STC_B_KEYWORD2', 'class_style'),   #TODO
                 ('STC_B_KEYWORD3', 'funct_style'), #TODO
                 ('STC_B_KEYWORD4', 'scalar_style'), #TODO
                 ('STC_B_LABEL', 'directive_style'), #TODO
                 ('STC_B_NUMBER', 'number_style'),
                 ('STC_B_OPERATOR', 'operator_style'),
                 ('STC_B_PREPROCESSOR', 'pre_style'),
                 ('STC_B_STRING', 'string_style'),
                 ('STC_B_STRINGEOL', 'stringeol_style')
               ]

#---- Extra Properties ----#
fold = ("fold", "1")

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    keywords = list()
    tmp = [vb_kw, vb_ukw1, vb_ukw2, vb_ukw3]
    for kw in tmp:
        keywords.append((kw[0], kw[1].lower()))
    return keywords

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
    return [u'\'']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
