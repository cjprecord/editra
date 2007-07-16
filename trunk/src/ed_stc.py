###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
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
# FILE: ed_stc.py                                                             #
# LANGUAGE: Python                                                            #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# This file contains the definition of the text control class                 #
# The text control is responsible for keeping reference to the file that      #
# is currently being edited in it.                                            #
#                                                                             #
# The class also contains the definitions of all the styles for fonts and     #
# highlighting in the context of code editing.                                #
#                                                                             #
# METHODS:                                                                    #
# - ED_STC: Main class object definition, based on wx.stc                     #
# - GetPos: Returns line and column information of carat                      #
# - OnUpdateUI: Checks brackets after each change to the screen.              #
# - OnMarginClick: Margin Event handler                                       #
# - OnFoldAll: Opens or closes a folder tree                                  #
# - Expand: Opens margin folders                                              #
# - FindLexer: Finds the approriate lexer based on file extentsion            #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-------------------------------------------------------------------------#
# Dependencies

import os
import wx, wx.stc
import ed_event
import ed_glob
from syntax import syntax
from autocomp import autocomp
import util
import ed_style

_ = wx.GetTranslation
MARK_MARGIN = 0
NUM_MARGIN  = 1
FOLD_MARGIN = 2
#-------------------------------------------------------------------------#
class EDSTC(wx.stc.StyledTextCtrl, ed_style.StyleMgr):
    """Defines a styled text control for editing text
    @summary: Custom subclass of L{wx.stc.StyledTextCtrl} and
              L{ed_style.StyleMgr}. Manages the documents display
              and input.

              """
    ED_STC_MASK_MARKERS = ~wx.stc.STC_MASK_FOLDERS
    def __init__(self, parent, id_,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, use_dt=True):
        """Initializes a control and sets the default objects for
        Tracking events that occur in the control.
        @keyword use_dt: wheter to use a drop target or not

        """
        wx.stc.StyledTextCtrl.__init__(self, parent, id_, pos, size, style)
        ed_style.StyleMgr.__init__(self, self.GetStyleSheet())

        self.SetModEventMask(wx.stc.STC_PERFORMED_UNDO | \
                             wx.stc.STC_PERFORMED_REDO | \
                             wx.stc.STC_MOD_DELETETEXT | \
                             wx.stc.STC_MOD_INSERTTEXT | \
                             wx.stc.STC_PERFORMED_USER)

        self.CmdKeyAssign(ord('-'), wx.stc.STC_SCMOD_CTRL, \
                          wx.stc.STC_CMD_ZOOMOUT)
        self.CmdKeyAssign(ord('+'), wx.stc.STC_SCMOD_CTRL | \
                          wx.stc.STC_SCMOD_SHIFT, wx.stc.STC_CMD_ZOOMIN)
        #---- Drop Target ----#
        if use_dt:
            self.SetDropTarget(util.DropTargetFT(self, None, parent.OnDrop))

        # Attributes
        self.LOG = wx.GetApp().GetLog()

        # File Attributes
        self.filename = ''	                # This controls File
        self.dirname = ''                   # Files Directory
        self.encoding = u'utf-8'            # Default Encoding
        self._hasbom = False                # Write BOM bit or not
        self.modtime = 0

        # Macro Attributes
        self._macro = list()
        self.recording = False

        # Command/Settings Attributes
        self.old_pos = -1
        self._autocomp_svc = autocomp.AutoCompService(self)
        self._use_autocomp = ed_glob.PROFILE['AUTO_COMP']
        self._autoindent = ed_glob.PROFILE['AUTO_INDENT']
        self.brackethl = ed_glob.PROFILE["BRACKETHL"]
        self.folding = ed_glob.PROFILE['CODE_FOLD']
        self.highlight = ed_glob.PROFILE["SYNTAX"]
        self._synmgr = syntax.SyntaxMgr(ed_glob.CONFIG['CACHE_DIR'])
        self.keywords = [ ' ' ]		# Keywords list
        self.syntax_set = list()
        self._comment = list()
        self.lang_id = 0        # Language ID from syntax module

        # Set Up Margins 
        self.SetMarginType(MARK_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(MARK_MARGIN, self.ED_STC_MASK_MARKERS)
        self.SetMarginSensitive(MARK_MARGIN, True)
        self.SetMarginWidth(MARK_MARGIN, 12)

        ## Outer Left Margin Line Number Indication
        self.SetMarginType(NUM_MARGIN, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginMask(NUM_MARGIN, 0)

        ## Inner Left Margin Setup Folders
        self.SetMarginType(FOLD_MARGIN, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(FOLD_MARGIN, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(FOLD_MARGIN, True)

        # Set Default Styles used by all documents
        self.Configure()
        self.UpdateBaseStyles()

        # Configure Autocompletion
        # NOTE: must be done after syntax configuration
        if self._use_autocomp:
            self.ConfigureAutoComp()

        ### Folder Marker Styles
        self.DefineMarkers()

        # Events
        if self.brackethl:
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(wx.stc.EVT_STC_MACRORECORD, self.OnRecordMacro)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        self.Bind(wx.stc.EVT_STC_MODIFIED, self.OnModified)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
       #---- End Init ----#

    __name__ = u"EditraTextCtrl"

    def _BuildMacro(self):
        """Constructs a macro script from items in the macro
        record list.
        @status: in limbo

        """
        return
#         if not len(self._macro):
#             return

#         # Get command mappings
#         cmds = list()
#         for x in dir(wx.stc):
#             if x.startswith('STC_CMD_'):
#                 cmds.append(x)
#         cmdvals = [getattr(wx.stc, x) for x in cmds]
#         cmds = [x.replace('STC_CMD_', u'') for x in cmds]
#         # Get the commands names used in the macro
#         named = list()
#         for x in self._macro:
#             if x[0] in cmdvals:
#                 named.append(cmds[cmdvals.index(x[0])])
#         code = list()
#         stc_dict = wx.stc.StyledTextCtrl.__dict__
#         for cmd in named:
#             for attr in stc_dict:
#                 if attr.upper() == cmd:
#                     code.append(attr)
#                     break
#         code_txt = u''
#         for fun in code:
#             code_txt += "    self.%s()\n" % fun
#         code_txt += "    print \"Executed\""    #TEST
#         code_txt = "def macro(self):\n" + code_txt
#         code = compile(code_txt, self.__module__, 'exec')
#         exec code in self.__dict__ # Inject new code into this namespace

    def PlayMacro(self):
        """Send the list of built up macro messages to the editor
        to be played back.
        @postcondition: the macro of this control has been played back

        """
        self.BeginUndoAction()
        for msg in self._macro:
            if msg[0] == 2170:
                self.AddText(msg[2])
            elif msg[0] == 2001:
                self.AddText(self.GetEOLChar() + u' ' * (msg[1] - 1))
            else:
                self.SendMsg(msg[0], msg[1], msg[2])
        self.EndUndoAction()

    #---- Begin Function Definitions ----#
    def AddLine(self, before=False):
        """Add a new line to the document
        @param before: whether to add the line before current pos or not
        @postcondition: a new line is added to the document

        """
        line = self.LineFromPosition(self.GetCurrentPos())
        if before:
            line = line - 1
            if line < 0:
                line = 0
        if line or not before:
            pos = self.GetLineEndPosition(line)
            curr = len(self.GetEOLChar())
        else:
            pos = 0
            curr = 0
        self.InsertText(pos, self.GetEOLChar())
        self.GotoPos(pos + curr)

    def Bookmark(self, action):
        """Handles bookmark actions
        @param action: An event ID that describes what is to be done
        @return: None

        """
        lnum = self.GetCurrentLine()
        mark = -1
        if action == ed_glob.ID_ADD_BM:
            self.MarkerAdd(lnum, MARK_MARGIN)
        elif action == ed_glob.ID_DEL_BM:
            self.MarkerDelete(lnum, MARK_MARGIN)
        elif action == ed_glob.ID_DEL_ALL_BM:
            self.MarkerDeleteAll(MARK_MARGIN)
        elif action == ed_glob.ID_NEXT_MARK:
            if self.MarkerGet(lnum):
                lnum += 1
            mark = self.MarkerNext(lnum, 1)
            if mark == -1:
                mark = self.MarkerNext(0, 1)
        elif action == ed_glob.ID_PRE_MARK:
            if self.MarkerGet(lnum):
                lnum -= 1
            mark = self.MarkerPrevious(lnum, 1)
            if mark == -1:
                mark = self.MarkerPrevious(self.GetLineCount(), 1)
        if mark != -1:
            self.GotoLine(mark)

    def Configure(self):
        """Configures the editors settings by using profile values
        @postcondition: all profile dependant attributes are configured

        """
        self.SetWrapMode(ed_glob.PROFILE['WRAP']) 
        self.SetViewWhiteSpace(ed_glob.PROFILE['SHOW_WS'])
        self.SetUseAntiAliasing(ed_glob.PROFILE['AALIASING'])
        self.SetUseTabs(ed_glob.PROFILE['USETABS'])
        self.SetIndent(int(ed_glob.PROFILE['TABWIDTH']))
        self.SetTabWidth(int(ed_glob.PROFILE['TABWIDTH']))
        self.SetIndentationGuides(ed_glob.PROFILE['GUIDES'])
        self.SetEOLFromString(ed_glob.PROFILE['EOL'])
        self.SetViewEOL(ed_glob.PROFILE['SHOW_EOL'])
        self.SyntaxOnOff(ed_glob.PROFILE['SYNTAX'])  # <- do before autocomp
        self.SetAutoComplete(ed_glob.PROFILE['AUTO_COMP'])
        self.FoldingOnOff(ed_glob.PROFILE['CODE_FOLD'])
        self.ToggleAutoIndent(ed_glob.PROFILE['AUTO_INDENT'])
        self.ToggleBracketHL(ed_glob.PROFILE['BRACKETHL'])
        self.ToggleLineNumbers(ed_glob.PROFILE['SHOW_LN'])
        self.SetViewEdgeGuide(ed_glob.PROFILE['SHOW_EDGE'])

    def Comment(self, uncomment=False):
        """(Un)Comments a line or a selected block of text
        in a document.
        @param uncomment: uncomment selection

        """
        if len(self._comment):
            sel = self.GetSelection()
            start = self.LineFromPosition(sel[0])
            end = self.LineFromPosition(sel[1])
            c_start = self._comment[0] + " "
            c_end = u''
            if len(self._comment) > 1:
                c_end = " " + self._comment[1]
            if end > start and self.GetColumn(sel[1]) == 0:
                end = end - 1
            self.BeginUndoAction()
            try:
                nchars = 0
                lines = range(start, end+1)
                lines.reverse()
                for line_num in lines:
                    lstart = self.PositionFromLine(line_num)
                    lend = self.GetLineEndPosition(line_num)
                    text = self.GetTextRange(lstart, lend)
                    if len(text.strip()):
                        if not uncomment:
                            text = c_start + text + c_end
                            nchars = nchars + len(c_start + c_end)
                        else:
                            text = text.replace(c_start, u'', 1)
                            text = text.replace(c_end, u'', 1)
                            nchars = nchars - len(c_start + c_end)
                        self.SetTargetStart(lstart)
                        self.SetTargetEnd(lend)
                        self.ReplaceTarget(text)
            finally:
                self.EndUndoAction()
                if sel[0] != sel[1]:
                    self.SetSelection(sel[0], sel[1] + nchars)
                else:
                    if len(self._comment) > 1:
                        nchars = nchars - len(self._comment[1])
                    self.GotoPos(sel[0] + nchars)

    def ConvertCase(self, to_upper=False):
        """Converts the case of the selected text to either all lower
        case(default) or all upper case.
        @keyword to_upper: Flag whether conversion is to upper case or not.

        """
        txt = self.GetSelectedText()
        if to_upper:
            txt = txt.upper()
        else:
            txt = txt.lower()
        self.ReplaceSelection(txt)

    def GetAutoIndent(self):
        """Returns whether auto-indent is being used
        @return: whether autoindent is active or not
        @rtype: bool

        """
        return self._autoindent

    def GetLangId(self):
        """Returns the language identifer of this control
        @return: language identifier of document
        @rtype: int

        """
        return self.lang_id

    def GetPos(self, key):
        """Update Line/Column information
        @param key: KeyEvent object

        """
        pos = self.GetCurrentPos()
        line = self.GetCurrentLine()
        column = self.GetColumn(pos)
        if (self.old_pos != pos):
            self.old_pos = pos
            if self._use_autocomp and key.GetEventType() != wx.wxEVT_LEFT_UP:
                key_code = key.GetKeyCode()
                if key_code == wx.WXK_RETURN:
                    self._autocomp_svc.UpdateNamespace(True)
            return (line + 1, column)
        else:
            return (-1, -1)

    def DefineMarkers(self):
        """Defines the folder and bookmark icons for this control
        @postcondition: all margin markers are defined

        """
        back = self.GetDefaultForeColour()
        fore = self.GetDefaultBackColour()
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN, 
                          wx.stc.STC_MARK_BOXMINUS, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,
                          wx.stc.STC_MARK_BOXPLUS,  fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,     
                          wx.stc.STC_MARK_VLINE, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,
                          wx.stc.STC_MARK_LCORNER, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,
                          wx.stc.STC_MARK_BOXPLUSCONNECTED, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, 
                          wx.stc.STC_MARK_BOXMINUSCONNECTED, fore, back)
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, 
                          wx.stc.STC_MARK_TCORNER, fore, back)
        self.MarkerDefine(0, wx.stc.STC_MARK_SHORTARROW, fore, back)
        self.SetFoldMarginHiColour(True, fore)
        self.SetFoldMarginColour(True, fore)

    def FindTagById(self, style_id):
        """Find the style tag that is associated with the given
        Id. If not found it returns an empty string.
        @param style_id: id of tag to look for
        @return: style tag string

        """
        for data in self.syntax_set:
            if style_id == getattr(wx.stc, data[0]):
                return data[1]
        return 'default_style'

    def GetAutoComplete(self):
        """Is Autocomplete being used by this instance
        @return: whether autocomp is active or not

        """
        return self._use_autocomp

    def GetFileName(self):
        """Returns the full path name of the current file
        @return: full path name of document

        """
        return "".join([self.dirname, util.GetPathChar(), self.filename])

    def GetStyleSheet(self, sheet_name=None):
        """Finds the current style sheet and returns its path. The
        Lookup is done by first looking in the users config directory
        and if it is not found there it looks for one on the system
        level and if that fails it returns None.
        @param sheet_name: style sheet to look for
        @return: full path to style sheet

        """
        if sheet_name:
            style = sheet_name
            if sheet_name.split(u'.')[-1] != u"ess":
                style += u".ess"
        elif ed_glob.PROFILE['SYNTHEME'].split(u'.')[-1] != u"ess":
            style = (ed_glob.PROFILE['SYNTHEME'] + u".ess").lower()
        else:
            style = ed_glob.PROFILE['SYNTHEME'].lower()
        user = os.path.join(ed_glob.CONFIG['STYLES_DIR'], style)
        sys = os.path.join(ed_glob.CONFIG['SYS_STYLES_DIR'], style)
        if os.path.exists(user):
            return user
        elif os.path.exists(sys):
            return sys
        else:
            return None

    def OnKeyDown(self, evt):
        """Handles keydown events, currently only deals with
        auto indentation.
        @param evt: event that called this handler
        @type evt: wx.KeyEvent

        """
        k_code = evt.GetKeyCode()
        if self._autoindent and k_code == wx.WXK_RETURN:
            if self.GetSelectedText():
                self.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
                return
            line = self.GetCurrentLine()
            text = self.GetTextRange(self.PositionFromLine(line), \
                                     self.GetCurrentPos())
            if text.strip() == u'':
                self.AddText(self.GetEOLChar() + text)
                self.EnsureCaretVisible()
                return
            indent = self.GetLineIndentation(line)
            i_space = indent / self.GetTabWidth()
            ndent = self.GetEOLChar() + self.GetIndentChar() * i_space
            self.AddText(ndent + \
                         ((indent - (self.GetTabWidth() * i_space)) * u' '))
            self.EnsureCaretVisible()
        else:
            evt.Skip()

    def OnChar(self, evt):
        """Handles Char events that arent caught by the
        KEY_DOWN event.
        @param evt: event that called this handler
        @type evt: wx.EVT_CHAR
        @todo: autocomp/calltip lookup can be very cpu intesive it may
               be better to try and process it on a separate thread to
               prevent a slow down in the input of text into the buffer

        """
        if not self._use_autocomp:
            evt.Skip()
            return True
        key_code = evt.GetKeyCode()
        if key_code in self._autocomp_svc.GetAutoCompKeys():
            if self.AutoCompActive():
                self.AutoCompCancel()
            command = self.GetCommandStr() + chr(key_code)
            self.AddText(chr(key_code))
            if self._use_autocomp:
                self.ShowAutoCompOpt(command)
        elif key_code in self._autocomp_svc.GetCallTipKeys():
            if self.AutoCompActive():
                self.AutoCompCancel()
            command = self.GetCommandStr()
            self.AddText(chr(key_code))
            if self._use_autocomp:
                self.ShowCallTip(command)
        else:
            evt.Skip()
        return

    def OnRecordMacro(self, evt):
        """Records macro events
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        if self.IsRecording():
            msg = evt.GetMessage()
            if msg == 2170:
                lparm = self.GetTextRange(self.GetCurrentPos()-1, \
                                          self.GetCurrentPos())
            else:
                lparm = evt.GetLParam()
            mac = (msg, evt.GetWParam(), lparm)
            self._macro.append(mac)
            print mac
#             if mac[0] != 2170:
#                 self._macro.append(mac)
        else:
            evt.Skip()
            
    def GetCommandStr(self):
        """Gets the command string to the left of the autocomp
        activation character.
        @return: the command string to the left of the autocomp char

        """
        curr_pos = self.GetCurrentPos()
        start = curr_pos - 1
        col = self.GetColumn(curr_pos)
        cmd_lmt = list(self._autocomp_svc.GetAutoCompStops())
        for key in self._autocomp_svc.GetAutoCompKeys():
            if chr(key) in cmd_lmt:
                cmd_lmt.remove(chr(key))
        while self.GetTextRange(start, curr_pos)[0] not in cmd_lmt \
              and col - (curr_pos - start) > 0:
            start -= 1
        s_col = self.GetColumn(start)
        if s_col != 0:
            start += 1
        cmd = self.GetTextRange(start, curr_pos)
        return cmd.strip()

    def ShowAutoCompOpt(self, command):
        """Shows the autocompletion options list for the command
        @param command: command to look for autocomp options for

        """
        lst = self._autocomp_svc.GetAutoCompList(command)
        if len(lst):
            options = u' '.join(lst)
            self.AutoCompShow(0, options)

    def ShowCallTip(self, command):
        """Shows call tip for given command
        @param command: command to  look for calltips for

        """
        if self.CallTipActive():
            self.CallTipCancel()
        tip = self._autocomp_svc.GetCallTip(command)
        if len(tip):
            curr_pos = self.GetCurrentPos()
            tip_pos = curr_pos - (len(command) + 1)
            fail_safe = curr_pos - self.GetColumn(curr_pos)
            tip_pos = max(tip_pos, fail_safe)
            self.CallTipShow(tip_pos, tip)

    def ShowKeywordHelp(self):
        """Displays the keyword helper
        @postcondition: shows keyword helper list control

        """
        if self.AutoCompActive():
            self.AutoCompCancel()
        elif len(self.keywords) > 1:
            pos = self.GetCurrentPos()
            pos2 = self.WordStartPosition(pos, True)
            context = pos - pos2
            self.AutoCompShow(context, self.keywords)
        return

    def OnModified(self, evt):
        """Handles updates that need to take place after
        the control has been modified.
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        mevt = ed_event.UpdateTextEvent(ed_event.edEVT_UPDATE_TEXT, \
                                        self.GetId())
        wx.PostEvent(self.GetParent(), mevt)

    def OnUpdateUI(self, evt):
        """Check for matching braces
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        brace_at_caret = -1
        brace_opposite = -1
        char_before = None
        caret_pos = self.GetCurrentPos()

        if caret_pos > 0:
            char_before = self.GetCharAt(caret_pos - 1)

        # check before
        if char_before and chr(char_before) in "[]{}()<>": 
            brace_at_caret = caret_pos - 1

        # check after
        if brace_at_caret < 0:
            char_after = self.GetCharAt(caret_pos)
            if char_after and chr(char_after) in "[]{}()<>":
                brace_at_caret = caret_pos

        if brace_at_caret >= 0:
            brace_opposite = self.BraceMatch(brace_at_caret)

        if brace_at_caret != -1  and brace_opposite == -1:
            self.BraceBadLight(brace_at_caret)
        else:
            self.BraceHighlight(brace_at_caret, brace_opposite)
        evt.Skip()

    def OnMarginClick(self, evt):
        """Open and Close Folders as Needed
        @param evt: event that called this handler
        @type evt: wx.stc.StyledTextEvent

        """
        if evt.GetMargin() == FOLD_MARGIN:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                line_clicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(line_clicked) & \
                   wx.stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(line_clicked, True)
                        self.Expand(line_clicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(line_clicked):
                            self.SetFoldExpanded(line_clicked, False)
                            self.Expand(line_clicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(line_clicked, True)
                            self.Expand(line_clicked, True, True, 100)
                    else:
                        self.ToggleFold(line_clicked)
        elif evt.GetMargin() == MARK_MARGIN:
            line_clicked = self.LineFromPosition(evt.GetPosition())
            if self.MarkerGet(line_clicked):
                self.MarkerDelete(line_clicked, MARK_MARGIN)
            else:
                self.MarkerAdd(line_clicked, MARK_MARGIN)

    def FoldAll(self):
        """Fold Tree In or Out
        @postcondition: code tree is folded open or closed

        """
        line_count = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for line_num in xrange(line_count):
            if self.GetFoldLevel(line_num) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(line_num)
                break
        line_num = 0

        while line_num < line_count:
            level = self.GetFoldLevel(line_num)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG and \
               (level & wx.stc.STC_FOLDLEVELNUMBERMASK) == \
               wx.stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(line_num, True)
                    line_num = self.Expand(line_num, True)
                    line_num = line_num - 1
            else:
                last_child = self.GetLastChild(line_num, -1)
                self.SetFoldExpanded(line_num, False)

                if last_child > line_num:
                    self.HideLines(line_num + 1, last_child)
            line_num = line_num + 1

    def Expand(self, line, do_expand, force=False, vis_levels=0, level=-1):
        """Open the Margin Folder
        @postcondition: the selected folder is expanded

        """
        last_child = self.GetLastChild(line, level)
        line = line + 1

        while line <= last_child:
            if force and not (vis_levels > 0):
                self.HideLines(line, line)
            else:
                if do_expand or vis_levels > 0:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    self.SetFoldExpanded(line, vis_levels > 1)
                    line = self.Expand(line, do_expand, force, vis_levels - 1)
                else:
                    if do_expand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, vis_levels - 1)
                    else:
                        line = self.Expand(line, False, force, vis_levels - 1)
            else:
                line = line + 1
        return line

    def FindLexer(self, set_ext=u''):
        """Sets Text Controls Lexer Based on File Extension
        @param set_ext: explicit extension to use in search
        @postcondition: lexer is configured for file

        """
        if not self.highlight:
            return 2

        if set_ext != u'':
            ext = set_ext.lower()
        else:
            ext = util.GetExtension(self.filename).lower()
        self.ClearDocumentStyle()

        # Configure Lexer from File Extension
        self.ConfigureLexer(ext)

        # If syntax auto detection fails from file extension try to
        # see if there is an interpreter line that can be parsed.
        if self.GetLexer() in [0, wx.stc.STC_LEX_NULL]:
            interp = self.GetLine(0)
            if interp != wx.EmptyString:
                interp = interp.split(u"/")[-1]
                interp = interp.strip().split()
                if len(interp) and interp[-1][0] != "-":
                    interp = interp[-1]
                elif len(interp):
                    interp = interp[0]
                else:
                    interp = u''
                ex_map = { "python" : "py", "wish" : "tcl", "ruby" : "rb",
                           "bash" : "sh", "csh" : "csh", "perl" : "pl",
                           "ksh" : "ksh", "php" : "php" }
                self.ConfigureLexer(ex_map.get(interp, interp))
        self.Colourise(0, -1)

        # Configure Autocompletion
        # NOTE: must be done after syntax configuration
        if self._use_autocomp:
            self.ConfigureAutoComp()
        return 0

    def ControlDispatch(self, evt):
        """Dispatches events caught from the mainwindow to the
        proper functions in this module.
        @param evt: event that was posted to this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        e_map = { ed_glob.ID_COPY  : self.Copy, ed_glob.ID_CUT  : self.Cut,
                  ed_glob.ID_PASTE : self.Paste, ed_glob.ID_UNDO : self.Undo,
                  ed_glob.ID_REDO  : self.Redo, ed_glob.ID_INDENT : self.Tab,
                  ed_glob.ID_KWHELPER: self.ShowKeywordHelp,
                  ed_glob.ID_CUT_LINE : self.LineCut, 
                  ed_glob.ID_COPY_LINE : self.LineCopy,
                  ed_glob.ID_BRACKETHL : self.ToggleBracketHL,
                  ed_glob.ID_SYNTAX : self.SyntaxOnOff,
                  ed_glob.ID_UNINDENT : self.BackTab,
                  ed_glob.ID_TRANSPOSE : self.LineTranspose, 
                  ed_glob.ID_SELECTALL: self.SelectAll,
                  ed_glob.ID_FOLDING : self.FoldingOnOff, 
                  ed_glob.ID_SHOW_LN : self.ToggleLineNumbers,
                  ed_glob.ID_COMMENT : self.Comment, 
                  ed_glob.ID_AUTOINDENT : self.ToggleAutoIndent,
                  ed_glob.ID_LINE_AFTER : self.AddLine, 
                  ed_glob.ID_TRIM_WS : self.TrimWhitespace,
                  ed_glob.ID_MACRO_START : self.StartRecord, 
                  ed_glob.ID_MACRO_STOP : self.StopRecord,
                  ed_glob.ID_MACRO_PLAY : self.PlayMacro
        }
        
        e_idmap = { ed_glob.ID_ZOOM_OUT : self.DoZoom,
                    ed_glob.ID_ZOOM_IN  : self.DoZoom,
                    ed_glob.ID_ZOOM_NORMAL : self.DoZoom,
                    ed_glob.ID_EOL_MAC  : self.ConvertLineMode,
                    ed_glob.ID_EOL_UNIX : self.ConvertLineMode,
                    ed_glob.ID_EOL_WIN  : self.ConvertLineMode,
                    ed_glob.ID_SPACE_TO_TAB : self.ConvertWhitespace,
                    ed_glob.ID_TAB_TO_SPACE : self.ConvertWhitespace,
                    ed_glob.ID_NEXT_MARK : self.Bookmark,
                    ed_glob.ID_PRE_MARK  : self.Bookmark,
                    ed_glob.ID_ADD_BM    : self.Bookmark,
                    ed_glob.ID_DEL_BM    : self.Bookmark,
                    ed_glob.ID_DEL_ALL_BM : self.Bookmark}
                    
        if e_obj.GetClassName() == "wxToolBar" or e_map.has_key(e_id):
            if e_map.has_key(e_id):
                e_map[e_id]()
            return

        if e_id in e_idmap:
            e_idmap[e_id](e_id)
        elif e_id == ed_glob.ID_SHOW_EDGE:
            self.SetViewEdgeGuide(not self.GetEdgeMode())
        elif e_id == ed_glob.ID_SHOW_EOL:
            self.SetViewEOL(not self.GetViewEOL())
        elif e_id == ed_glob.ID_SHOW_WS:
            self.SetViewWhiteSpace(not self.GetViewWhiteSpace())
        elif e_id == ed_glob.ID_WORD_WRAP:
            self.SetWrapMode(not self.GetWrapMode())
        elif e_id == ed_glob.ID_JOIN_LINES:
            self.SetTargetStart(self.GetSelectionStart())
            self.SetTargetEnd(self.GetSelectionEnd())
            self.LinesJoin()
        elif e_id == ed_glob.ID_INDENT_GUIDES:
            self.SetIndentationGuides(not bool(self.GetIndentationGuides()))
        elif e_id in syntax.SyntaxIds():
            f_ext = syntax.GetExtFromId(e_id)
            self.LOG("[stc_evt] Manually Setting Lexer to %s" % str(f_ext))
            self.FindLexer(f_ext)
        elif e_id == ed_glob.ID_AUTOCOMP:
            self.SetAutoComplete(not self.GetAutoComplete())
        elif e_id == ed_glob.ID_UNCOMMENT:
            self.Comment(True)
        elif e_id == ed_glob.ID_LINE_BEFORE:
            self.AddLine(before=True)
        elif e_id in [ed_glob.ID_TO_UPPER, ed_glob.ID_TO_LOWER]:
            self.ConvertCase(e_id == ed_glob.ID_TO_UPPER)
        else:
            evt.Skip()

    def CheckEOL(self):
        """Checks the EOL mode of the opened document. If the mode
        that the document was saved in is different than the editors
        current mode the editor will switch modes to preserve the eol
        type of the file, if the eol chars are mixed then the editor
        will toggle on eol visibility.
        @postcondition: eol mode is configured to best match file
        @todo: Is showing line endings the best way to show mixed?

        """
        mixed = diff = False
        eol_map = {"\n" : wx.stc.STC_EOL_LF, 
                   "\r\n" : wx.stc.STC_EOL_CRLF,
                   "\r" : wx.stc.STC_EOL_CR}
        eol = chr(self.GetCharAt(self.GetLineEndPosition(0)))
        if eol == "\r":
            tmp = chr(self.GetCharAt(self.GetLineEndPosition(0) + 1))
            if tmp == "\n":
                eol += tmp
        if eol != self.GetEOLChar():
            diff = True
        for line in range(self.GetLineCount() - 1):
            end = self.GetLineEndPosition(line)
            tmp = chr(self.GetCharAt(end))
            if tmp == "\r":
                tmp2 = chr(self.GetCharAt(self.GetLineEndPosition(0) + 1))
                if tmp2 == "\n":
                    tmp += tmp2
            if tmp != eol:
                mixed = True
                break
        if mixed or diff:
            if mixed:
                self.SetViewEOL(True)
            else:
                self.SetEOLMode(eol_map.get(eol, wx.stc.STC_EOL_LF))
        else:
            pass

    def ConvertLineMode(self, mode_id):
        """Converts all line endings in a document to a specified
        format.
        @param mode_id: id of eol mode to set

        """
        eol_map = { ed_glob.ID_EOL_MAC  : wx.stc.STC_EOL_CR,
                    ed_glob.ID_EOL_UNIX : wx.stc.STC_EOL_LF,
                    ed_glob.ID_EOL_WIN  : wx.stc.STC_EOL_CRLF
                  }
        self.ConvertEOLs(eol_map[mode_id])
        self.SetEOLMode(eol_map[mode_id])

    def ConvertWhitespace(self, mode_id):
        """Convert whitespace from using tabs to spaces or visa versa
        @param mode_id: id of conversion mode

        """
        if mode_id not in (ed_glob.ID_TAB_TO_SPACE, ed_glob.ID_SPACE_TO_TAB):
            return
        tabw = self.GetIndent()
        pos = self.GetCurrentPos()
        sel = self.GetSelectedText()
        if mode_id == ed_glob.ID_TAB_TO_SPACE:
            cmd = (u"\t", u" " * tabw)
            tabs = False
        else:
            cmd = (" " * tabw, u"\t")
            tabs = True

        if sel != wx.EmptyString:
            self.ReplaceSelection(sel.replace(cmd[0], cmd[1]))
        else:
            self.BeginUndoAction()
            part1 = self.GetTextRange(0, pos).replace(cmd[0], cmd[1])
            tmptxt = self.GetTextRange(pos, self.GetLength()).replace(cmd[0], \
                                                                      cmd[1])
            self.SetText(part1 + tmptxt)
            self.GotoPos(len(part1))
            self.SetUseTabs(tabs)
            self.EndUndoAction()
            del part1

    def GetEOLChar(self):
        """Gets the eol character used in document
        @returns the character used for eol in this document

        """
        m_id = self.GetEOLModeId()
        if m_id == ed_glob.ID_EOL_MAC:
            return u'\r'
        elif m_id == ed_glob.ID_EOL_WIN:
            return u'\r\n'
        else:
            return u'\n'

    def GetIndentChar(self):
        """Gets the indentation char used in document
        @return: indentation char used either space or tab

        """
        if self.GetUseTabs():
            return u'\t'
        else:
            return u' ' * self.GetTabWidth()

    def GetEncoding(self):
        """Returns the encoding of the current document
        @return: the encoding of the document

        """
        return self.encoding

    def GetEOLModeId(self):
        """Gets the id of the eol format
        @return: id of the eol mode of this document

        """
        eol_map = { wx.stc.STC_EOL_CR : ed_glob.ID_EOL_MAC,
                    wx.stc.STC_EOL_LF : ed_glob.ID_EOL_UNIX,
                    wx.stc.STC_EOL_CRLF : ed_glob.ID_EOL_WIN
                  }
        return eol_map.get(self.GetEOLMode(), ed_glob.ID_EOL_UNIX)

    def HasBom(self):
        """Returns whether the loaded file had a BOM byte or not
        @return: whether file had a bom byte or not

        """
        return self._hasbom

    def IsBracketHlOn(self):
        """Returns whether bracket highlighting is being used by this
        control or not.
        @return: status of bracket highlight activation

        """
        return self.brackethl

    def IsFoldingOn(self):
        """Returns whether code folding is being used by this
        control or not.
        @return: whether folding is on or not

        """
        return self.folding

    def IsHighlightingOn(self):
        """Returns whether syntax highlighting is being used by this
        control or not.
        @return: whether syntax highlighting is on or not

        """
        return self.highlight

    def IsRecording(self):
        """Returns whether the control is in the middle of recording
        a macro or not.
        @return: whether recording macro or not

        """
        return self.recording

    def SetAutoComplete(self, value):
        """Turns Autocompletion on and off
        @param value: use autocomp or not
        @type value: bool

        """
        if isinstance(value, bool):
            self._use_autocomp = value
            if value:
                self._autocomp_svc.LoadCompProvider(self.GetLexer())

    def SetEncoding(self, enc):
        """Sets the encoding of the current document
        @param enc: encoding to set for document

        """
        self.encoding = enc

    def SetEOLFromString(self, mode_str):
        """Sets the EOL mode from a string descript
        @param mode_str: eol mode to set
        @todo: get rid of this somehow

        """
        mode_map = { 'Macintosh (\\r\\n)' : wx.stc.STC_EOL_CR,
                     'Unix (\\n)' : wx.stc.STC_EOL_LF,
                     'Windows (\\r\\n)' : wx.stc.STC_EOL_CRLF
                   }
        mode = mode_map.get(mode_str, wx.stc.STC_EOL_LF)
        self.SetEOLMode(mode)

    def SetViewEdgeGuide(self, switch=None):
        """Toggles the visibility of the edge guide
        @keyword switch: force a particular setting

        """
        if (switch is None and not self.GetEdgeMode()) or switch:
            self.SetEdgeColumn(int(ed_glob.PROFILE.get("EDGE", 80)))
            self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        else:
            self.SetEdgeMode(wx.stc.STC_EDGE_NONE)

    def StartRecord(self):
        """Starts recording all events
        @return: None

        """
        self.recording = True
        wx.GetApp().GetMainWindow().SetStatusText(_("Recording Macro") + \
                                                  u"...", ed_glob.SB_INFO)
        wx.stc.StyledTextCtrl.StartRecord(self)

    def StopRecord(self):
        """Stops the recording and builds the macro script
        @postcondition: macro recording is stopped

        """
        self.recording = False
        wx.stc.StyledTextCtrl.StopRecord(self)
        wx.GetApp().GetMainWindow().SetStatusText(_("Recording Finished"), \
                                                  ed_glob.SB_INFO)
        self._BuildMacro()

    def TrimWhitespace(self):
        """Trims trailing whitespace from all lines in the document.
        @postcondition: all trailing whitespace is removed from document

        """
        txt = u''
        cpos = self.GetCurrentPos()
        cline = self.GetCurrentLine()
        for line in xrange(self.GetLineCount()):
            tmp = self.GetLine(line)
            if len(tmp):
                eol = tmp[-1]
                if not eol.isspace():
                    eol = u''
            else:
                eol = u''            
            if line == cline:
                npos = cpos - (abs(len(self.GetTextRange(0, \
                                       self.GetLineEndPosition(cline-1))) - \
                                   len(txt)) + 1)
                next = cpos - 1
                while self.GetTextRange(next, cpos).isspace() and next > 0:
                    next = next - 1
                cpos = npos - ((cpos - next) - 1)
            txt = txt + tmp.rstrip() + eol
        self.SetText(txt)
        self.GotoPos(cpos)
        del txt

    def FoldingOnOff(self, switch=None):
        """Turn code folding on and off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self.folding) or switch:
            self.LOG("[stc_evt] Code Folding Turned On")
            self.folding = True
            self.SetMarginWidth(FOLD_MARGIN, 12)
        else:
            self.LOG("[stc_evt] Code Folding Turned Off")
            self.folding = False
            self.SetMarginWidth(FOLD_MARGIN, 0)

    def SyntaxOnOff(self, switch=None):
        """Turn Syntax Highlighting on and off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self.highlight) or switch:
            self.LOG("[stc_evt] Syntax Highlighting Turned On")
            self.highlight = True
            self.FindLexer()
        else:
            self.LOG("[stc_evt] Syntax Highlighting Turned Off")
            self.highlight = False
            self.SetLexer(wx.stc.STC_LEX_NULL)
            self.ClearDocumentStyle()
            self.UpdateBaseStyles()
        return 0

    def ToggleAutoIndent(self, switch=None):
        """Toggles Auto-indent On and Off
        @keyword switch: force a particular setting

        """
        if (switch is None and not self._autoindent) or switch:
            self._autoindent = True
        else:
            self._autoindent = False

    def ToggleBracketHL(self, switch=None):
        """Toggle Bracket Highlighting On and Off
        @keyword switch: force a particular setting
        @todo: Why must the UI event be unbound twice

        """
        if (switch is None and not self.brackethl) or switch:
            self.LOG("[stc_evt] Bracket Highlighting Turned On")
            self.brackethl = True
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        else:
            self.LOG("[stc_evt] Bracket Highlighting Turned Off")
            self.brackethl = False
            self.Unbind(wx.stc.EVT_STC_UPDATEUI)
            self.Unbind(wx.stc.EVT_STC_UPDATEUI)

    def ToggleLineNumbers(self, switch=None):
        """Toggles the visibility of the line number margin
        @keyword switch: force a particular setting

        """
        if (switch is None and not self.GetMarginWidth(NUM_MARGIN)) or switch:
            self.LOG("[stc_evt] Showing Line Numbers")
            self.SetMarginWidth(NUM_MARGIN, 30)
        else:
            self.LOG("[stc_evt] Hiding Line Numbers")
            self.SetMarginWidth(NUM_MARGIN, 0)

    def ReloadFile(self):
        """Reloads the current file, returns True on success and
        False if there is a failure.
        @return: whether file was reloaded or not
        @rtype: bool

        """
        cfile = os.path.join(self.dirname, self.filename)
        if os.path.exists(cfile):
            try:
                self.BeginUndoAction()
                cpos = self.GetCurrentPos()
                reader = util.GetFileReader(cfile, self.encoding)
                self.SetText(reader.read())
                reader.close()
                self.modtime = util.GetFileModTime(cfile)
                self.EndUndoAction()
                self.SetSavePoint()
            except (OSError, IOError):
                self.LOG("[stc][err] Failed to Reload %s" % cfile)
                return False
            else:
                self.GotoPos(cpos)
                return True
        else:
            self.LOG("[stc][err] %s does not exists, cannot reload it." % cfile)
            return False

    def SaveFile(self, path):
        """Save buffers contents to disk
        @param path: path of file to save
        @return: whether file was written or not
        @rtype: bool

        """
        result = True
        try:
            writer = util.GetFileWriter(path, enc=self.encoding)
            if self.HasBom():
                bom = unicode(util.BOM.get(self.encoding, u''), self.encoding)
            else:
                bom = u''
            writer.write(bom + self.GetText())
            writer.close()
        except IOError:
            writer.close()
            result = False
            self.LOG("[stc][err]There was an error saving %s" % path)
        if result:
            self.SetSavePoint()
            self.modtime = util.GetFileModTime(path)
            self.OnModified(wx.ID_ANY)
            self.filename = util.GetFileName(path)
            self.dirname = util.GetPathName(path)
        return result

    # With utf-16 encoded text need to remove the BOM prior to setting
    # the text or there is alignment issues in the display of the first line 
    # of text. Potentially a BUG in scintilla or wxStyledTextCtrl
    def SetText(self, txt, enc=u'utf-8'):
        """Sets the text of the control and the encoding to use for
        writting the file with.
        @keyword enc: encoding to use for decoding text

        """
        bom = util.BOM.get(enc, u'')
        bom = unicode(bom, enc)
        if len(txt) > len(bom):
            if txt[:len(bom)] == bom:
                self.LOG("[stc][info] Stripped BOM from text")
                self._hasbom = True
                txt = txt.replace(bom, u'', 1)
        wx.stc.StyledTextCtrl.SetText(self, txt)
        self.encoding = enc

    def DoZoom(self, mode):
        """Zoom control in or out
        @param mode: either zoom in or out
        @type mode: int id value

        """
        id_type = mode
        zoomlevel = self.GetZoom()
        if id_type == ed_glob.ID_ZOOM_OUT:
            if zoomlevel > -9:
                self.ZoomOut()
        elif id_type == ed_glob.ID_ZOOM_IN:
            if zoomlevel < 19:
                self.ZoomIn()
        else:
            self.SetZoom(0)
        return self.GetZoom()

    def ConfigureAutoComp(self):
        """Sets up the Autocompleter, the autocompleter
        configuration depends on the currently set lexer
        @postcondition: autocomp is configured

        """
        self.AutoCompSetAutoHide(False)
        self._autocomp_svc.LoadCompProvider(self.GetLexer())
        case = self._autocomp_svc.GetIgnoreCase()
        self.AutoCompSetIgnoreCase(case)
        stops = self._autocomp_svc.GetAutoCompStops()
        self.AutoCompStops(stops)
        self._autocomp_svc.UpdateNamespace(True)

    def ConfigureLexer(self, file_ext):
        """Sets Lexer and Lexer Keywords for the specifed file extension
        @param file_ext: a file extension to configure the lexer from

        """
        syn_data = self._synmgr.SyntaxData(file_ext)

        # Set the ID of the selected lexer
        try:
            self.lang_id = syn_data[syntax.LANGUAGE]
        except KeyError:
            self.LOG("[stc][err] Failed to get Lang Id from Syntax package")
            self.lang_id = 0

        lexer = syn_data[syntax.LEXER]
        # Check for special cases
        if lexer in [ wx.stc.STC_LEX_HTML, wx.stc.STC_LEX_XML]:
            self.SetStyleBits(7)
        elif lexer == wx.stc.STC_LEX_NULL:
            self.SetStyleBits(5)
            self.SetIndentationGuides(False)
            self.SetLexer(lexer)
            self.ClearDocumentStyle()
            self.UpdateBaseStyles()
            return True
        else:
            self.SetStyleBits(5)

        try:
            keywords = syn_data[syntax.KEYWORDS]
        except KeyError:
            self.LOG("[stc][err] No Keywords Data Found")
            keywords = []
       
        try:
            synspec = syn_data[syntax.SYNSPEC]
        except KeyError:
            self.LOG("[stc] [exception] Failed to get Syntax Specifications")
            synspec = []

        try:
            props = syn_data[syntax.PROPERTIES]
        except KeyError:
            self.LOG("[stc] [exception] No Extra Properties to Set")
            props = []

        try:
            comment = syn_data[syntax.COMMENT]
        except KeyError:
            self.LOG("[stc] [exception] No Comment Pattern to set")
            comment = []

        # Set Lexer
        self.SetLexer(lexer)
        # Set Keywords
        self.SetKeyWords(keywords)
        # Set Lexer/Syntax Specifications
        self.SetSyntax(synspec)
        # Set Extra Properties
        self.SetProperties(props)
        # Set Comment Pattern
        self._comment = comment
        return True

    def SetKeyWords(self, kw_lst):
        """Sets the keywords from a list of keyword sets
        @param kw_lst: [ (KWLVL, "KEWORDS"), (KWLVL2, "KEYWORDS2"), ect...]
        @todo: look into if the uniquifying of the list has a more optimal
               solution.

        """
        # Parse Keyword Settings List simply ignoring bad values and badly
        # formed lists
        self.keywords = ""
        for keyw in kw_lst:
            if len(keyw) != 2:
                continue
            else:
                if not isinstance(keyw[0], int):
                    continue
                elif not isinstance(keyw[1], basestring):
                    continue
                else:
                    self.keywords += keyw[1]
                    wx.stc.StyledTextCtrl.SetKeyWords(self, keyw[0], keyw[1])

        kwlist = self.keywords.split()      # Split into a list of words
        kwlist = list(set(kwlist))          # Uniqueify the list
        kwlist.sort()                       # Sort into alphbetical order
        self.keywords = " ".join(kwlist)    # Put back into a string
        return True
 
    def SetSyntax(self, syn_lst):
        """Sets the Syntax Style Specs from a list of specifications
        @param syn_lst: [(STYLE_ID, "STYLE_TYPE"), (STYLE_ID2, "STYLE_TYPE2)]

        """
        # Parses Syntax Specifications list, ignoring all bad values
        self.UpdateBaseStyles()
        valid_settings = list()
        for syn in syn_lst:
            if len(syn) != 2:
                self.LOG("[ed_stc][warn] Error setting syntax spec")
                continue
            else:
                if not isinstance(syn[0], basestring) or \
                   not hasattr(wx.stc, syn[0]):
                    self.LOG("[ed_stc][warn] Unknown syntax region: %s" % \
                             str(syn[0]))
                    continue
                elif not isinstance(syn[1], basestring):
                    self.LOG("[ed_stc][warn] Poorly formated styletag: %s" % \
                             str(syn[1]))
                    continue
                else:
                    self.StyleSetSpec(getattr(wx.stc, syn[0]), \
                                      self.GetStyleByName(syn[1]))
                    valid_settings.append(syn)
        self.syntax_set = valid_settings
        return True

    def SetProperties(self, prop_lst):
        """Sets the Lexer Properties from a list of specifications
        @param prop_lst: [ ("PROPERTY", "VAL"), ("PROPERTY2", "VAL2) ]

        """
        # Parses Property list, ignoring all bad values
        for prop in prop_lst:
            if len(prop) != 2:
                continue
            else:
                if not isinstance(prop[0], basestring) or not \
                   isinstance(prop[1], basestring):
                    continue
                else:
                    self.SetProperty(prop[0], prop[1])
        return True

    #---- End Function Definitions ----#

    #---- Style Function Definitions ----#
    def RefreshStyles(self):
        """Refreshes the colorization of the window by reloading any 
        style tags that may have been modified.
        @postcondition: all style settings are refreshed in the control

        """
        self.Freeze()
        self.StyleClearAll()
        self.UpdateBaseStyles()
        self.SetSyntax(self.syntax_set)
        self.DefineMarkers()
        self.Thaw()
        self.Refresh()

    def StyleDefault(self):
        """Clears the editor styles to default
        @postcondition: style is reset to default

        """
        self.StyleResetDefault()
        self.StyleClearAll()
        self.SetCaretForeground(wx.NamedColor("black"))
        self.Colourise(0, -1)

    def UpdateBaseStyles(self):
        """Updates the base styles of editor to the current settings
        @postcondtion: base style info is updated

        """
        self.StyleDefault()
        self.SetMargins(0, 0)
        # Global default styles for all languages
        self.StyleSetSpec(0, self.GetStyleByName('default_style'))
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, \
                          self.GetStyleByName('default_style'))
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, \
                          self.GetStyleByName('line_num'))
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, \
                          self.GetStyleByName('ctrl_char'))
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, \
                          self.GetStyleByName('brace_good'))
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, \
                          self.GetStyleByName('brace_bad'))
        calltip = self.GetItemByName('calltip')
        self.CallTipSetBackground(calltip.GetBack())
        self.CallTipSetForeground(calltip.GetFore())
        self.SetCaretForeground(self.GetDefaultForeColour())
        self.DefineMarkers()
        self.Colourise(0, -1)

    def UpdateAllStyles(self, spec_style=None):
        """Refreshes all the styles and attributes of the control
        @param spec_style: style scheme name
        @postcondtion: style scheme is set to specified style

        """
        self.LoadStyleSheet(self.GetStyleSheet(spec_style))
        self.UpdateBaseStyles()
        self.SetSyntax(self.syntax_set)
        self.DefineMarkers()
        self.Refresh()

    #---- End Style Definitions ----#
