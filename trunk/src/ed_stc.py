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
# - FindLexer: Finds the approriate lexer based on filetype                   #
# - Set**Style: CPP, CSS, Default, Lisp, Makefile, Perl, Python, SQL          #
#               Set the style for a particular language.                      #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id:  Exp $"

#-------------------------------------------------------------------------#
# Dependencies

import os
import wx, wx.stc, keyword 
from ed_glob import PROFILE, ID_ZOOM_IN, ID_ZOOM_OUT, ID_ZOOM_NORMAL, ID_SYNTAX, LANG
import syntax.syntax as syntax
import util
import dev_tool

#-------------------------------------------------------------------------#
# Font Settings
if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Monaco', #'Courier',
              'helv' : 'Helvetica',
              'other': 'Bitstream Vera Sans',
              'size' : 10,
              'size2': 8,
             }
#-------------------------------------------------------------------------#
# Common Style Strings
# HACK till a proper style provider/editor can be implimented
# Defaults
brace_good = "fore:#FFFFFF,back:#0000FF,bold"
brace_bad = "fore:#000000,back:#FF0000,bold"
ctrl_char = "face:%(mono)s,back:#F6F6F6"
line_num = "back:#C0C0C0,face:%(other)s,size:%(size2)d"

array_style = "fore:#EE8B02,bold,face:%(other)s,back:#F6F6F6,size:%(size)d"
btick_style = "fore:#8959F6,bold,size:%(size)d"
default_style = "fore:#000000,face:%(mono)s,back:#F6F6F6,size:%(size)d"
char_style = "fore:#FF3AFF,face:%(mono)s,size:%(size)d"
class_style = "fore:#2E8B57,bold,back:#F6F6F6,size:%(size)d"
class2_style = "fore:#2E8B57,bold,size:%(size)d"
comment_style = "fore:#838383,face:%(mono)s,back:#F6F6F6,size:%(size)d"
directive_style = "fore:#0000FF,bold,face:%(other)s,size:%(size)d"
dockey_style = "fore:#0000FF,size:%(size)d"
error_style = "fore:#DD0101,bold,face:%(other)s,size:%(size)d"
funct_style = "fore:#008B8B,italic,back:#F6F6F6,size:%(size)d"
global_style = "fore:#007F7F,bold,face:%(other)s,size:%(size)d" 
here_style = "fore:#CA61CA,bold,face:%(other)s,size:%(size)d"
ideol_style = "fore:#E0C0E0,face:%(other)s,size:%(size)d"
keyword_style = "fore:#A52B2B,bold,back:#F6F6F6,size:%(size)d"
keyword2_style = "fore:#2E8B57,bold,back:#F6F6F6,size:%(size)d"
keyword3_style = "fore:#008B8B,bold,back:#F6F6F6,size:%(size)d"
keyword4_style = "fore:#9D2424,size:%(size)d"
number_style = "fore:#DD0101,face:%(mono)s,back:#F6F6F6,size:%(size)d"
number2_style = "fore:#DD0101,bold,face:%(mono)s,back:#F6F6F6,size:%(size)d"
operator_style = "fore:#000000,face:%(mono)s,bold,back:#F6F6F6,size:%(size)d"
pre_style =  "fore:#AB39F2,bold,size:%(size)d"
pre2_style =  "fore:#AB39F2,bold,back:#F6F6F6,size:%(size)d"
regex_style = "fore:#008B8B,size:%(size)d"
scalar_style = "fore:#AB37F2,bold,face:%(other)s,size:%(size)d"
scalar2_style = "fore:#AB37F2,face:%(other)s,size:%(size)d"
string_style = "fore:#FF3AFF,bold,face:%(mono)s,size:%(size)d"
stringeol_style = "fore:#000000,bold,face:%(other)s,back:#EEC0EE,eol,size:%(size)d"
unknown_style = "fore:#FFFFFF,bold,face:%(other)s,back:#DD0101,size:%(size)d"
# blue 2828FF
STYLE = { "array_style" : array_style, "default_style" : default_style,
          "char_style" : char_style, "class_style" : class_style,
          "comment_style" : comment_style, "dockey_style" : dockey_style,
          "error_style" : error_style, "funct_style"  : funct_style,
          "global_style" : global_style, "here_style" : here_style,
          "keyword_style" : keyword_style, "keyword2_style" : keyword2_style,
          "keyword3_style" : keyword3_style, "number_style" : number_style,
          "operator_style" : operator_style, "pre_style" : pre_style,
          "scalar_style" : scalar_style, "scalar2_style" : string_style,
          "string_style" : string_style, "stringeol_style" : stringeol_style,
          "unknown_style" : unknown_style, "keyword4_style" : keyword4_style,
          "number2_style" : number2_style, "directive_style" : directive_style,
          "ideol_style" : ideol_style, 'class2_style' : class2_style,
          "pre2_style" : pre2_style, 'btick_style' : btick_style,
          "regex_style" : regex_style }
#-------------------------------------------------------------------------#

class EDSTC(wx.stc.StyledTextCtrl):
    """Defines a styled text control that is the main pane for the editor"""
    def __init__(self, parent, win_id,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        """Initializes a control and sets the default objects for
        Tracking events that occur in the control.
        Default Settings (w/o profile):
        WordWrap:		On
        AntiAliasing:	On
        EOL Marker:	LF ONLY (Unix Style)
        Tab Width:		8 spaces
        Indentation Guides:	On
        Keyword Helper:	On
        Syntax Highlight:	On
        Foldering:		On
        Font Size:		10pt
        Font:		Courier New (MSW)
                            Monaco (GTK/MAC)

        """
        wx.stc.StyledTextCtrl.__init__(self, parent, win_id, pos, size, style)

        #Text Box Attributes
        self.SetWrapMode(PROFILE['WRAP']) 
        self.SetViewWhiteSpace(PROFILE['SHOW_WS'])
        self.SetUseAntiAliasing(PROFILE['AALIASING'])
        self.SetUseTabs(PROFILE['USETABS'])
        self.SetIndent(int(PROFILE['TABWIDTH']))
        self.SetTabWidth(int(PROFILE['TABWIDTH']))
        self.SetIndentationGuides(PROFILE['GUIDES'])
        self.SetEOLMode(wx.stc.STC_EOL_LF) # Use Unix style EOL characters

        #---- Text Box Drop Target ----#
        # TODO this should really be parented by the frame or notebook
        self.dt = util.FileDropTarget(self, parent)
        self.SetDropTarget(self.dt)

        # Attributes
        self.frame = parent	                  # Notebook
        self.window = parent.frame           # Frame
        self.filename = ''	                  # This controls File
        self.dirname = ''			# Files Directory
        self.path_char = util.GetPathChar()	# Path Character / 0r \
        self.zoom = 0			# Default Zoom Level TODO ditch this for GetZoom
        self.old_pos = -1			# Carat begins at top of file
        self.column = 0
        self.line = 0
        self.brackethl = PROFILE["BRACKETHL"]
        self.kwhelp = PROFILE["KWHELPER"]
        self.highlight = PROFILE["SYNTAX"]
        self.keywords = [ ' ' ]		# Keywords list

        # Set Up Margins 
        ## Outer Left Margin Line Number Indication
        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 30)

        ## Inner Left Margin Setup Folders
        self.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        ### Folder Marker Styles
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN, 
                          wx.stc.STC_MARK_BOXMINUS, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,
                          wx.stc.STC_MARK_BOXPLUS,  "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,     
                          wx.stc.STC_MARK_VLINE, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,
                          wx.stc.STC_MARK_LCORNER, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,
                          wx.stc.STC_MARK_BOXPLUSCONNECTED, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, 
                          wx.stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
        self.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, 
                          wx.stc.STC_MARK_TCORNER, "white", "black")

        # Set Default Styles used by all documents
        self.SetDefaultStyle()

        # Events
        if self.brackethl:
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(wx.stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        if PROFILE["KWHELPER"]:
            self.Bind(wx.EVT_KEY_DOWN, self.KeyWordHelp)
       #---- End Init ----#

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

        #if key == 32 and event.ControlDown():
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
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)

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
        # many shell scripts that often dont even have file extensions
        self.ConfigureLexer(ext)
        self.Colourise(0, -1)
        return 0

    def SyntaxOnOff(self, set=0):
        """Turn Syntax Highlighting on and off"""
        if not self.highlight:
            dev_tool.DEBUGP("[stc_evt] Syntax Highlighting Turned On")
            self.highlight = True
            self.FindLexer()
        else:
            dev_tool.DEBUGP("[stc_evt] Syntax Highlighting Turned Off")
            self.highlight = False
            self.SetLexer(wx.stc.STC_LEX_NULL)
            self.SetDefaultStyle()
            self.Colourise(0, -1)
        return 0

    def ToggleBracketHL(self, set=0):
        """Toggle Bracket Highlighting On and Off"""
        if not self.brackethl or set == 1:
            dev_tool.DEBUGP("[stc_evt] Bracket Highlighting Turned On")
            self.brackethl = True
            self.Bind(wx.stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        else:
            dev_tool.DEBUGP("[stc_evt] Bracket Highlighting Turned Off")
            self.brackethl = False
            self.Unbind(wx.stc.EVT_STC_UPDATEUI)
            
    def KeyWordHelpOnOff(self, set=0):
        """Turns KeyWord Help on and off"""
        if not self.kwhelp or set == 1:
            dev_tool.DEBUGP("[stc_evt] Keyword Helper On")
            self.kwhelp = True
            self.Bind(wx.EVT_KEY_DOWN, self.KeyWordHelp)
        else:
            dev_tool.DEBUGP("[stc_evt] Keyword Helper Off")
            self.kwhelp = False
            self.Unbind(wx.EVT_KEY_DOWN)
        return 0

    def IndentGuideOnOff(self, set=0):
        """Turns Indentation Guides on and off"""
        if not self.GetIndentationGuides() or set == 1:
            dev_tool.DEBUGP("[stc_evt] Indentation Guides Turned On")
            self.SetIndentationGuides(1)
        else:
            dev_tool.DEBUGP("[stc_evt] Indentation Guides Turned Off")
            self.SetIndentationGuides(0)
        return 0

    #TODO Save functions should do exception handling
    def Save(self):
        """Save Text To File"""
        if self.filename != '':
            path = self.dirname + self.path_char + self.filename
            content = self.GetText()
            try:
                file_handle = open(path, 'wb')
                file_handle.write(content)
                self.SetSavePoint()
                file_handle.close()
                result = wx.ID_OK
            except IOError,msg:
                dev_tool.DEBUGP("[stc] [exception] " + str(msg))
                result = msg
        return result

    def SaveAs(self, path):
        """Save Text to File using specified name"""
        content = self.GetText()
        try:
            file_handle = open(path, 'wb')
            file_handle.write(content)
            file_handle.close()
        except IOError,msg:
            dev_tool.DEBUGP("[stc] [exception] Failed to perform SaveAs on File")
            return msg
        self.filename = util.GetFileName(path)
        self.dirname = util.GetPathName(path)
        self.window.filehistory.AddFileToHistory(os.path.join(self.dirname, self.filename))
        self.SetSavePoint()
        self.FindLexer()
        return wx.ID_OK

    def WrapOnOff(self, set=0):
        """Turn word wrap on or off"""
        if not self.GetWrapMode() or set == 1:
            dev_tool.DEBUGP("[stc_evt] Word Wrap Turned On")
            self.SetWrapMode(True)
        else:
            dev_tool.DEBUGP("[stc_evt] Word Wrap Turned Off")
            self.SetWrapMode(False)
        return 0

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
        
        lexer = syn_data[syntax.LEXER]
        # Check for special cases
        if lexer in [ wx.stc.STC_LEX_HTML, wx.stc.STC_LEX_XML]:
            self.SetStyleBits(7)
        elif lexer == wx.stc.STC_LEX_NULL:
            self.SetIndentationGuides(False)
            self.SetDefaultStyle()
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
            dev_tool.DEBUGP("[stc] [exception] Failed to get Syntax Specifications")
            synspec = []

        try:
            props = syn_data[syntax.PROPERTIES]
        except KeyError:
            dev_tool.DEBUGP("[stc] [exception] No Extra Properties to Set")
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
        PARAM: kw_lst [ (KWLVL, "KEWORDS"), (KWLVL2, "KEYWORDS2") ]

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
        kwlist = self.keywords.split(" ")      # Split into a list of words
        kwlist = list(set(kwlist))             # Uniqueify the list
        kwlist.sort()                           # Sort into alphbetical order
        self.keywords = " ".join(kwlist)        # Put back into a string
        return True
 
    def SetSyntax(self, syn_lst):
        """Sets the Syntax Style Specs from a list of specifications
        PARAM: syn_lst = [(STYLE_ID, "STYLE_TYPE"), (STYLE_ID2, "STYLE_TYPE 2)]

        """
        # Parses Syntax Specifications list, ignoring all bad values
        stc_specs = wx.stc.__dict__
        for syn in syn_lst:
            if len(syn) != 2:
                continue
            else:
                if not isinstance(syn[0], basestring) or not stc_specs.has_key(syn[0]):
                    continue
                elif not isinstance(syn[1], basestring):
                    continue
                else:
                    self.StyleSetSpec(stc_specs[syn[0]], STYLE[syn[1]] % faces)
        return True

    def SetProperties(self, prop_lst):
        """Sets the Lexer Properties from a list of specifications
        PARAM: syn_lst = [ ("PROPERTY", "VAL"), ("PROPERTY2", "VAL2) ]

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
    def SetDefaultStyle(self):
        """Global default styles for all languages"""
        self.keywords = [ ' ' ]

        self.StyleClearAll()  # Reset all styles
        self.SetMargins(0, 0)
        # Global default styles for all languages
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, default_style % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER, line_num  % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, ctrl_char % faces)
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT, brace_good)
        self.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD, brace_bad)

    #---- End Style Definitions ----#

