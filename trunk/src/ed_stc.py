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

__revision__ = "$Id:  $"

#-------------------------------------------------------------------------#
# Dependencies

import os
import wx, wx.stc
from ed_glob import *
import syntax.syntax as syntax
import util
import ed_style

_ = wx.GetTranslation
#-------------------------------------------------------------------------#

class EDSTC(wx.stc.StyledTextCtrl, ed_style.StyleMgr):
    """Defines a styled text control for editing text in"""
    ED_STC_MASK_MARKERS = ~wx.stc.STC_MASK_FOLDERS

    def __init__(self, parent, win_id,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, log=wx.EmptyString, useDT=True):
        """Initializes a control and sets the default objects for
        Tracking events that occur in the control.

        """
        wx.stc.StyledTextCtrl.__init__(self, parent, win_id, pos, size, style)
        ed_style.StyleMgr.__init__(self, os.path.join(CONFIG['STYLES_DIR'], PROFILE['SYNTHEME'] + u".ess"), log)

        # Set Text Box Attributes
        self.SetWrapMode(PROFILE['WRAP']) 
        self.SetViewWhiteSpace(PROFILE['SHOW_WS'])
        self.SetUseAntiAliasing(PROFILE['AALIASING'])
        self.SetUseTabs(PROFILE['USETABS'])
        self.SetIndent(int(PROFILE['TABWIDTH']))
        self.SetTabWidth(int(PROFILE['TABWIDTH']))
        self.SetIndentationGuides(PROFILE['GUIDES'])
        self.SetEOLFromString(PROFILE['EOL'])
        self.SetViewEOL(PROFILE['SHOW_EOL'])

        #---- Drop Target ----#
        # TODO how can we have a file drop target and text drop at same time
        if useDT:
            self.fdt = util.DropTarget(self, parent, log)
            self.SetDropTarget(self.fdt)

        # Attributes
        self.LOG = log
        self.frame = parent	                # Notebook
        self.filename = ''	                # This controls File
        self.dirname = ''			# Files Directory
        self.path_char = util.GetPathChar()	# Path Character / 0r \
        self.zoom = 0			        # Default Zoom Level
        self.old_pos = -1			# Carat begins at top of file
        self.column = 0
        self.line = 0
        self.brackethl = PROFILE["BRACKETHL"]
        self.kwhelp = PROFILE["KWHELPER"]
        self.highlight = PROFILE["SYNTAX"]
        self.keywords = [ ' ' ]		# Keywords list
        self.syntax_set = list()
        self.lang_id = 0

        # Set Up Margins 
        self.SetMarginType(0, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(0, self.ED_STC_MASK_MARKERS)
        self.SetMarginSensitive(0, True)
        self.SetMarginWidth(0, 12)

        ## Outer Left Margin Line Number Indication
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginMask(1, 0)
        self.SetMarginWidth(1, 30)

        ## Inner Left Margin Setup Folders
        self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        # Set Default Styles used by all documents
        if self.highlight:
            self.UpdateBaseStyles()
        else:
            self.StyleDefault()

        ### Folder Marker Styles
        self.DefineMarkers()

        # Events
        if self.brackethl:
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        if PROFILE["KWHELPER"]:
            self.Bind(wx.EVT_KEY_DOWN, self.KeyWordHelp)
       #---- End Init ----#

    __name__ = u"EditraTextCtrl"

    #---- Begin Function Definitions ----#
    def GetPos(self):
        """ Update Line/Column information """
        pos = self.GetCurrentPos()
        self.line = self.GetCurrentLine()
        self.column = self.GetColumn(pos)
        if (self.old_pos != pos):
            self.old_pos = pos
            return (self.line + 1, self.column)
        else:
            return (-1, -1)

    def DefineMarkers(self):
        """Defines the folder and bookmark icons for this control"""
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

    def KeyWordHelp(self, evt):
        """Bring up Keyword List for Current Language"""
        #HACK this is just a test implimentation
        if self.CallTipActive():
            self.CallTipCancel()
            # key = e.KeyCode()

        # Toggle Autocomp window by pressing button again
        if self.AutoCompActive() and evt.AltDown():
            self.AutoCompCancel()
            return

        if evt.AltDown() and len(self.keywords) > 1:
            pos = self.GetCurrentPos()
            pos2 = self.WordStartPosition(pos, True)
            context = pos - pos2
            self.AutoCompSetIgnoreCase(True)
            self.AutoCompShow(context, self.keywords)

        else:
            evt.Skip()

    def OnUpdateUI(self, evt):
        """Check for matching braces"""
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()<>": 
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in "[]{}()<>":
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
        evt.Skip()

    def OnMarginClick(self, evt):
        """Open and Close Folders as Needed"""
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & \
                   wx.stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)
        elif evt.GetMargin() == 0:
            lineClicked = self.LineFromPosition(evt.GetPosition())
            if self.MarkerGet(lineClicked):
                self.MarkerDelete(lineClicked, 0)
            else:
                self.MarkerAdd(lineClicked, 0)

    def FoldAll(self):
        """Fold Tree In or Out"""
        lineCount = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break

        lineNum = 0

        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG and \
               (level & wx.stc.STC_FOLDLEVELNUMBERMASK) == \
               wx.stc.STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
            else:
                lastChild = self.GetLastChild(lineNum, -1)
                self.SetFoldExpanded(lineNum, False)

                if lastChild > lineNum:
                    self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        """Open the Margin Folder"""
        lastChild = self.GetLastChild(line, level)
        line = line + 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    self.SetFoldExpanded(line, visLevels > 1)
                    line = self.Expand(line, doExpand, force, visLevels-1)
                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1
        return line

    def FindLexer(self, set_ext=0):
        """Sets Text Controls Lexer Based on File Extension"""
        if not self.highlight:
            return 2

        if not isinstance(set_ext, int):
            ext = set_ext.lower()
        else:
            ext = util.GetExtension(self.filename).lower()
        self.ClearDocumentStyle()

        # Configure Lexer from File Extension
        # TODO add more comprehensive file type checking, the use of just
        # the file extension is not always accurate such as in the case of
        # many shell scripts that often dont use file extensions
        self.ConfigureLexer(ext)
        self.Colourise(0, -1)
        return 0

    def ControlDispatch(self, evt):
        """Dispatches events caught from the mainwindow to the
        proper functions in this module.

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        e_type = evt.GetEventType()
        e_map = { ID_COPY  : self.Copy,         ID_CUT  : self.Cut,
                  ID_PASTE : self.Paste,        ID_UNDO : self.Undo,
                  ID_REDO  : self.Redo,         ID_KWHELPER: self.KeyWordHelpOnOff,
                  ID_CUT_LINE : self.LineCut,   ID_BRACKETHL : self.ToggleBracketHL,
                  ID_COPY_LINE : self.LineCopy, ID_SYNTAX : self.SyntaxOnOff,
                  ID_INDENT : self.Tab,         ID_UNINDENT : self.BackTab,
                  ID_TRANSPOSE: self.LineTranspose
        }
        if e_obj.GetClassName() == "wxToolBar":
            self.LOG("[stc_evt] Caught Event Generated by ToolBar")
            if e_map.has_key(e_id):
                e_map[e_id]()
            return

        if e_id in [ID_ZOOM_OUT, ID_ZOOM_IN, ID_ZOOM_NORMAL]:
            zoom_level = self.DoZoom(e_id)
        elif e_map.has_key(e_id):
            e_map[e_id]()
        elif e_id == ID_SHOW_EOL:
            self.SetViewEOL(not self.GetViewEOL())
        elif e_id == ID_SHOW_WS:
            self.SetViewWhiteSpace(not self.GetViewWhiteSpace())
        elif e_id == ID_WORD_WRAP:
            self.SetWrapMode(not bool(self.WrapMode))
        elif e_id in [ ID_NEXT_MARK, ID_PRE_MARK, ID_ADD_BM, ID_DEL_BM,
                     ID_DEL_ALL_BM]:
            n = self.GetCurrentLine()
            if e_id == ID_ADD_BM:
                self.MarkerAdd(n, 0)
                return
            elif e_id == ID_DEL_BM:
                self.MarkerDelete(n, 0)
                return
            elif e_id == ID_DEL_ALL_BM:
                self.MarkerDeleteAll(0)
                return
            elif e_id == ID_NEXT_MARK:
                if self.MarkerGet(n):
                    n += 1
                mark = self.MarkerNext(n, 1)
                if mark == -1:
                    mark = self.MarkerNext(0, 1)
            elif e_id == ID_PRE_MARK:
                if self.MarkerGet(n):
                    n -= 1
                mark = self.MarkerPrevious(n, 1)
                if mark == -1:
                    mark = self.MarkerPrevious(self.GetLineCount(), 1)
            if mark != -1:
                self.GotoLine(mark)
            return
        elif e_id == ID_JOIN_LINES:
            self.SetTargetStart(self.GetSelectionStart())
            self.SetTargetEnd(self.GetSelectionEnd())
            self.LinesJoin()
        elif e_id == ID_INDENT_GUIDES:
            self.SetIndentationGuides(not bool(self.GetIndentationGuides))
        elif e_id in [ID_EOL_MAC, ID_EOL_UNIX, ID_EOL_WIN]:
            self.ConvertLineMode(e_id)
        elif e_id in syntax.SyntaxIds():
            f_ext = syntax.GetExtFromId(e_id)
            self.LOG("[stc_evt] Manually Setting Lexer to " + str(f_ext))
            self.FindLexer(f_ext)
        else:
            evt.Skip()

    def ConvertLineMode(self, mode_id):
        """Converts all line endings in a document to a specified
        format.

        """
        eol_map = { ID_EOL_MAC  : wx.stc.STC_EOL_CR,
                    ID_EOL_UNIX : wx.stc.STC_EOL_LF,
                    ID_EOL_WIN  : wx.stc.STC_EOL_CRLF
                  }
        self.ConvertEOLs(eol_map[mode_id])
        self.SetEOLMode(eol_map[mode_id])

    def GetEOLModeId(self):
        """Gets the id of the eol format"""
        eol_mode = self.GetEOLMode()
        eol_map = { wx.stc.STC_EOL_CR : ID_EOL_MAC,
                    wx.stc.STC_EOL_LF : ID_EOL_UNIX,
                    wx.stc.STC_EOL_CRLF : ID_EOL_WIN
                  }
        return eol_map[eol_mode]

    def SetEOLFromString(self, mode_str):
        """Sets the EOL mode from a string descript"""
        mode_map = { 'Macintosh (\\r\\n)' : wx.stc.STC_EOL_CR,
                     'Unix (\\n)' : wx.stc.STC_EOL_LF,
                     'Windows (\\r\\n)' : wx.stc.STC_EOL_CRLF
                   }
        if mode_map.has_key(mode_str):
            self.SetEOLMode(mode_map[mode_str])
        else:
            self.SetEOLMode(wx.stc.STC_EOL_LF)

    def SyntaxOnOff(self, set=False):
        """Turn Syntax Highlighting on and off"""
        if not self.highlight or set:
            self.LOG("[stc_evt] Syntax Highlighting Turned On")
            self.highlight = True
            self.FindLexer()
        else:
            self.LOG("[stc_evt] Syntax Highlighting Turned Off")
            self.highlight = False
            self.SetLexer(wx.stc.STC_LEX_NULL)
            self.StyleDefault()
        return 0

    def ToggleBracketHL(self, set=False):
        """Toggle Bracket Highlighting On and Off"""
        if not self.brackethl or set:
            self.LOG("[stc_evt] Bracket Highlighting Turned On")
            self.brackethl = True
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        else:
            self.LOG("[stc_evt] Bracket Highlighting Turned Off")
            self.brackethl = False
            self.Unbind(wx.stc.EVT_STC_UPDATEUI)
            
    def KeyWordHelpOnOff(self, set=False):
        """Turns KeyWord Help on and off"""
        if not self.kwhelp or set:
            self.LOG("[stc_evt] Keyword Helper On")
            self.kwhelp = True
            self.Bind(wx.EVT_KEY_DOWN, self.KeyWordHelp)
        else:
            self.LOG("[stc_evt] Keyword Helper Off")
            self.kwhelp = False
            self.Unbind(wx.EVT_KEY_DOWN)
        return 0

    def Save(self):
        """Save Text To File"""
        if self.filename != '':
            path = self.dirname + self.path_char + self.filename
            try:
                self.SaveFile(path)
                self.SetSavePoint()
                result = wx.ID_OK
            except IOError,msg:
                self.LOG("[stc] [exception] " + str(msg))
                result = msg
        return result

    def SaveAs(self, path):
        """Save Text to File using specified name"""
        try:
            self.SaveFile(path)
        except IOError,msg:
            self.LOG("[stc] [exception] Failed to perform SaveAs on File")
            return msg
        self.filename = util.GetFileName(path)
        self.dirname = util.GetPathName(path)
        self.SetSavePoint()
        self.FindLexer()
        return wx.ID_OK

    def DoZoom(self, mode):
        """Zoom control in or out"""
        id_type = mode
        zoomlevel = self.GetZoom()
        if id_type == ID_ZOOM_OUT:
            if zoomlevel > -9:
                self.ZoomOut()
        elif id_type == ID_ZOOM_IN:
            if zoomlevel < 19:
                self.ZoomIn()
        else:
            self.SetZoom(0)
        return self.GetZoom()

    def ConfigureLexer(self, file_ext):
        """Sets Lexer and Lexer Keywords for the specifed file extension"""
        syn_data = syntax.SyntaxData(file_ext)

        # Set the ID of the selected lexer
        try:
           self.lang_id = syn_data[syntax.LANGUAGE]
        except KeyError:
           self.lang_id = 0

        lexer = syn_data[syntax.LEXER]
        # Check for special cases
        if lexer in [ wx.stc.STC_LEX_HTML, wx.stc.STC_LEX_XML]:
            self.SetStyleBits(7)
        elif lexer == wx.stc.STC_LEX_NULL:
            self.SetIndentationGuides(False)
            self.UpdateBaseStyles()
            return 1
        else:
            pass

        try:
            keywords = syn_data[syntax.KEYWORDS]
        except KeyError:
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

        # Set Lexer
        self.SetLexer(lexer)
        # Set Keywords
        self.SetKeyWords(keywords)
        # Set Lexer/Syntax Specifications
        self.SetSyntax(synspec)
        # Set Extra Properties
        self.SetProperties(props)
        return True
     
    def SetKeyWords(self, kw_lst):
        """Sets the keywords from a list of keyword sets
        PARAM: kw_lst [ (KWLVL, "KEWORDS"), (KWLVL2, "KEYWORDS2"), ect...]

        """
        # Parse Keyword Settings List simply ignoring bad values and badly
        # formed lists
        self.keywords = ""
        for kw in kw_lst:
            if len(kw) != 2:
                continue
            else:
                if not isinstance(kw[0], int):
                    continue
                elif not isinstance(kw[1], basestring):
                    continue
                else:
                    self.keywords += kw[1]
                    wx.stc.StyledTextCtrl.SetKeyWords(self, kw[0], kw[1])
        #TODO These next four lines are very expensive for languages with
        # many keywords. 
        kwlist = self.keywords.split()      # Split into a list of words
        kwlist = list(set(kwlist))          # Uniqueify the list
        kwlist.sort()                       # Sort into alphbetical order
        self.keywords = " ".join(kwlist)    # Put back into a string
        return True
 
    def SetSyntax(self, syn_lst):
        """Sets the Syntax Style Specs from a list of specifications
        PARAM: syn_lst = [(STYLE_ID, "STYLE_TYPE"), (STYLE_ID2, "STYLE_TYPE2)]

        """
        # Parses Syntax Specifications list, ignoring all bad values
        valid_settings = list()
        for syn in syn_lst:
            if len(syn) != 2:
                continue
            else:
                if not isinstance(syn[0], basestring) or not hasattr(wx.stc, syn[0]):
                    continue
                elif not isinstance(syn[1], basestring):
                    continue
                else:
                    self.StyleSetSpec(getattr(wx.stc, syn[0]), self.GetStyleByName(syn[1]))
                    valid_settings.append(syn)
        self.syntax_set = valid_settings
        return True

    def SetProperties(self, prop_lst):
        """Sets the Lexer Properties from a list of specifications
        PARAM: prop_lst = [ ("PROPERTY", "VAL"), ("PROPERTY2", "VAL2) ]

        """
        # Parses Property list, ignoring all bad values
        for prop in prop_lst:
            if len(prop) != 2:
                continue
            else:
                if not isinstance(prop[0], basestring) or not isinstance(prop[1], basestring):
                    continue
                else:
                    self.SetProperty(prop[0], prop[1])
        return True

    #---- End Function Definitions ----#

    #---- Style Function Definitions ----#
    def RefreshStyles(self):
        self.Freeze()
        self.StyleClearAll()
        self.UpdateBaseStyles()
        self.SetSyntax(self.syntax_set)
        self.DefineMarkers()
        self.Thaw()
        self.Refresh()

    def StyleDefault(self):
        """Clears the editor styles to default"""
        self.StyleResetDefault()
        self.StyleClearAll()
        self.SetCaretForeground(wx.NamedColor("black"))
        self.Colourise(0,-1)

    def UpdateBaseStyles(self):
        """Updates the base styles of editor to the current settings"""
        self.keywords = [ ' ' ]
        self.StyleDefault()

        self.SetMargins(0, 0)
        # Global default styles for all languages
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, self.GetStyleByName('default_style'))
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, self.GetStyleByName('line_num'))
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, self.GetStyleByName('ctrl_char'))
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, self.GetStyleByName('brace_good'))
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, self.GetStyleByName('brace_bad'))
        self.SetCaretForeground(self.GetDefaultForeColour())
        self.DefineMarkers()

    def UpdateAllStyles(self, spec_style=None):
        """Refreshes all the styles and attributes of the control"""
        if spec_style == None:
            self.LoadStyleSheet(os.path.join(CONFIG['STYLES_DIR'], PROFILE['SYNTHEME'] + u".ess"))
        else:
            self.LoadStyleSheet(os.path.join(CONFIG['STYLES_DIR'], spec_style + u".ess"))
        self.UpdateBaseStyles()
        self.SetSyntax(self.syntax_set)
        self.DefineMarkers()
        self.Refresh()

    #---- End Style Definitions ----#

