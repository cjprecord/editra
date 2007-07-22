############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

"""
#--------------------------------------------------------------------------#
# FILE:	style_editor.py                                                    #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    Provides an editor dialog for editing styles and generating style     #
# sheets to use with editra's styled text controls.                        #
#                                                                          #
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import glob
import wx
import wx.lib.colourselect as  csel
import ed_glob
from profiler import Profile_Get
import ed_stc
from ed_style import StyleItem
import util
import syntax.syntax as syntax

# Function Aliases
_ = wx.GetTranslation

# Global Values
ID_STYLES = wx.NewId()
ID_FORE_COLOR = wx.NewId()
ID_BACK_COLOR = wx.NewId()
ID_BOLD = wx.NewId()
ID_ITALIC = wx.NewId()
ID_EOL = wx.NewId()
ID_ULINE = wx.NewId()
ID_FONT = wx.NewId()
ID_FONT_SIZE = wx.NewId()

SETTINGS_IDS = [ ID_FORE_COLOR, ID_BACK_COLOR, ID_BOLD, ID_ITALIC,
                 ID_EOL, ID_ULINE, ID_FONT, ID_FONT_SIZE ]
#--------------------------------------------------------------------------#

class StyleEditor(wx.Dialog):
    """This class creates the window that contains the controls
    for editing/configuring the syntax highlighting styles.

    """
    def __init__(self, parent, id_=wx.ID_ANY, title=_("Style Editor"),
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RAISED_BORDER):
        """Initializes the Dialog"""
        wx.Dialog.__init__(self, parent, id_, title, style=style)

        # Attributes
        self.LOG = wx.GetApp().GetLog()
        self.preview = ed_stc.EDSTC(self, wx.ID_ANY, size=(-1, 200),
                                    style=wx.SUNKEN_BORDER, use_dt=False)
        self.styles_new = self.preview.GetStyleSet()
        self.styles_orig = self.DuplicateStyleDict(self.styles_new)
        self.settings_enabled = True
        self.OpenPreviewFile('cpp')

        # Main Sizer
        self.SetSizeHints(300, 250)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add((10, 10)) # Spacer

        # Control Panel
        self.ctrl_pane = wx.Panel(self, wx.ID_ANY, style=wx.RAISED_BORDER)
        ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Main Control Sizer
        left_colum = wx.BoxSizer(wx.VERTICAL)    # Left Column
        right_colum = wx.BoxSizer(wx.VERTICAL)   # Right Column

        # Control Panel Left Column
        left_colum.AddMany([((10, 10), 0), 
                            (self.StyleSheets(), 0, wx.ALIGN_LEFT),
                            ((10, 10), 0), 
                            (self.LexerChoice(), 0, wx.ALIGN_LEFT),
                            ((10, 10), 0),
                            (self.StyleTags(), 0, wx.ALIGN_LEFT),
                            ((10, 10), 0)])
        ctrl_sizer.Add(left_colum, 0, wx.ALIGN_LEFT)

        # Divider
        ctrl_sizer.Add(wx.StaticLine(self.ctrl_pane, size=(-1, 2), 
                                     style = wx.LI_VERTICAL), 
                       0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)

        # Control Panel Right Column
        right_colum.Add(self.Settings(), 0, wx.ALIGN_LEFT)
        ctrl_sizer.Add(right_colum, 0, wx.ALIGN_RIGHT)

        # Finish Control Panel Setup
        self.ctrl_pane.SetSizer(ctrl_sizer)
        self.sizer.Add(self.ctrl_pane, 0, wx.ALIGN_CENTER)

        # Preview Area
        pre_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pre_sizer.AddMany([(10, 10), 
                           (wx.StaticText(self, label=_("Preview") + u": "), 
                            0, wx.ALIGN_LEFT)])
        self.sizer.AddMany([((10, 10), 0), (pre_sizer, 0, wx.ALIGN_LEFT),
                            (self.preview, 0, wx.EXPAND | wx.BOTTOM)])

        # Create Buttons
        b_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancel_b = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        cancel_b.SetDefault()
        save_b = wx.Button(self, wx.ID_SAVE, _("Export"))
        ok_b = wx.Button(self, wx.ID_OK, _("Ok"))
        b_sizer.AddMany([cancel_b, save_b, ok_b])
        self.sizer.Add(b_sizer, 0, wx.ALIGN_RIGHT | \
                                   wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # Finish the Layout
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.sizer.Fit(self)
        tags = self.FindWindowById(ID_STYLES)
        tags.SetSize((left_colum.GetSize()[0]*.90, 100))
        self.EnableSettings(False)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id = wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id = wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnExport, id = wx.ID_SAVE)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox)
        self.Bind(csel.EVT_COLOURSELECT, self.OnColor)
        self.preview.Bind(wx.EVT_LEFT_UP, self.OnTextRegion)
        self.preview.Bind(wx.EVT_KEY_UP, self.OnTextRegion)
    #--- End Init ---#

    def DiffStyles(self):
        """Checks if the current style set is different from the
        original set. Used internally to check if a save prompt needs
        to be brought up. Returns True if the style sets are different.
        @return: whether style set has been modified or not
        @rtype: bool

        """
        diff = False
        for key in self.styles_orig:
            if unicode(self.styles_orig[key]) != unicode(self.styles_new[key]):
                diff = True
                break
        result = wx.ID_NO
        if diff:
            dlg = wx.MessageDialog(self, 
                                    _("Some styles have been changed would "
                                      "you like to save before exiting?"),
                                   _("Save Styles"), 
                                   style = wx.YES_NO | wx.YES_DEFAULT | \
                                           wx.CANCEL | wx.ICON_INFORMATION)
            dlg.CenterOnParent()
            result = dlg.ShowModal()
            dlg.Destroy()
        return result

    def DuplicateStyleDict(self, style_dict):
        """Duplicates the style dictionary to make a true copy of
        it, as simply assigning the dictionary to two different variables
        only copies a reference leaving both variables pointing to the 
        same object.
        @param style_dict: dictionary of tags->StyleItems
        @return: a copy of the given styleitem dictionary

        """
        new_dict = dict()
        for tag in style_dict:
            new_dict[tag] = StyleItem()
            new_dict[tag].SetAttrFromStr(unicode(style_dict[tag]))
        return new_dict
        
    def EnableSettings(self, enable = True):
        """Enables/Disables all settings controls
        @keyword enable: whether to enable/disable settings controls

        """
        for sid in SETTINGS_IDS:
            ctrl = self.FindWindowById(sid)
            ctrl.Enable(enable)
        self.settings_enabled = enable

    def ExportStyleSheet(self):
        """Writes the style sheet data out to a style sheet
        @return: whether style sheet was exported properly or not

        """
        if ed_glob.CONFIG['STYLES_DIR'] == ed_glob.CONFIG['SYS_STYLES_DIR']:
            user_config = os.path.join(wx.GetHomeDir(), 
                                        "." + ed_glob.prog_name, 'styles')
            if not os.path.exists(user_config):
                try:
                    os.mkdir(user_config)
                except (OSError, IOError), msg:
                    self.LOG("[style_editor][err] %s" % msg)
                else:
                    ed_glob.CONFIG['STYLES_DIR'] = user_config

        dlg = wx.FileDialog(self, _("Export Style Sheet"),
                            ed_glob.CONFIG['STYLES_DIR'],
                            wildcard=_("Editra Style Sheet") + " (*.ess)|*.ess",
                            style=wx.FD_SAVE | wx.OVERWRITE_PROMPT)
        dlg.CenterOnParent()
        result = dlg.ShowModal()

        if result == wx.ID_OK:
            sheet_path = dlg.GetPath()
            if u'ess' != sheet_path.split(u'.')[-1]:
                sheet_path += u".ess"
            dlg.Destroy()
            writer = util.GetFileWriter(sheet_path)
            try:
                writer.write(self.GenerateStyleSheet())
                writer.close()
                # Update Style Sheet Control
                ss_lst = util.GetResourceFiles(u'styles', get_all=True)
                ss_c = self.FindWindowById(ed_glob.ID_PREF_SYNTHEME)
                sel = ss_c.GetStringSelection()
                ss_c.SetItems(ss_lst)
                ss_c.SetStringSelection(sel)
                self.styles_orig = self.DuplicateStyleDict(self.styles_new)
            except IOError,msg:
                self.LOG('[style_editor][err] Failed to export style sheet')
                self.LOG('[style_editor][sys error] %s' % msg)
        return result

    def GenerateStyleSheet(self):
        """Generates a style sheet from the dialogs style data
        @return: the dictionary of L{StyleItems} formated into a style sheet
                 string

        """
        sty_sheet = list()
        for tag in self.styles_new:
            sty_sheet.append(tag + u" {\n")
            sdat = unicode(self.styles_new[tag])
            sdat = sdat.split(u",")
            stage1 = wx.EmptyString
            for atom in sdat:
                if atom in "bold eol italic underline":
                    stage1 = stage1[0:-1] + u" " + atom + u";"
                else:
                    stage1 = stage1 + atom + u";"
            stage2 = u"\t\t" + stage1[0:-1].replace(u";", u";\n\t\t") + u";"
            sty_sheet.append(stage2)
            sty_sheet.append(u"\n}\n\n")
        return u"".join(sty_sheet)

    def LexerChoice(self):
        """Returns a sizer object containing a choice control with all
        available lexers listed in it.
        @return: sizer item containing a choice control with all available
                 syntax test files available

        """
        lex_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lexer_lbl = wx.StaticText(self.ctrl_pane, wx.ID_ANY, 
                                  _("Syntax Files") + u": ")
        lexer_lst = wx.Choice(self.ctrl_pane, ed_glob.ID_LEXER, 
                              choices=syntax.GetLexerList())
        lexer_lst.SetStringSelection(u"CPP")
        lex_sizer.AddMany([((10, 10)), 
                            (lexer_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                           ((5, 0)), (lexer_lst, 1, wx.ALIGN_CENTER_VERTICAL),
                           ((10, 10))])
        return lex_sizer

    def Settings(self):
        """Returns a sizer object holding all the settings controls
        @return: main panel of configuration controls

        """
        setting_sizer = wx.BoxSizer(wx.VERTICAL)
        setting_top = wx.BoxSizer(wx.HORIZONTAL)

        # Settings top
        setting_sizer.Add((10, 10))
        color_box = wx.StaticBox(self.ctrl_pane, wx.ID_ANY, _("Color") + u":")
        cbox_sizer = wx.StaticBoxSizer(color_box, wx.VERTICAL)
        # Foreground
        fground_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fground_lbl = wx.StaticText(self.ctrl_pane, 
                                    label=_("Foreground") + u": ")
        fground_sel = csel.ColourSelect(self.ctrl_pane, ID_FORE_COLOR,
                                        "#000000", (0, 0, 0), size=(80, 25))
        fground_sizer.AddMany([((5, 5)), 
                               (fground_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                               (fground_sel, 0, wx.ALIGN_CENTER_VERTICAL), 
                               ((5, 5))])
        cbox_sizer.Add(fground_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
        cbox_sizer.Add((10, 10))
        # Background
        bground_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bground_lbl = wx.StaticText(self.ctrl_pane, 
                                    label=_("Background") + u": ")
        bground_sel = csel.ColourSelect(self.ctrl_pane, ID_BACK_COLOR, 
                                        "#FFFFFF", (255, 255, 255), 
                                        size=(80, 25))
        bground_sizer.AddMany([((5, 5)), 
                               (bground_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                               (bground_sel, 0, wx.ALIGN_CENTER_VERTICAL), 
                               ((5, 5))])
        cbox_sizer.Add(bground_sizer, 0, wx.ALIGN_LEFT)
        setting_top.Add(cbox_sizer, 0, wx.ALIGN_TOP)
        # Attrib Box
        setting_top.Add((10, 10))
        attrib_box = wx.StaticBox(self.ctrl_pane, label=_("Attributes") + u":")
        abox_sizer = wx.StaticBoxSizer(attrib_box, wx.VERTICAL)
        # Attributes
        bold_cb = wx.CheckBox(self.ctrl_pane, ID_BOLD, _("bold"))
        eol_cb = wx.CheckBox(self.ctrl_pane, ID_EOL, _("eol"))
        ital_cb = wx.CheckBox(self.ctrl_pane, ID_ITALIC, _("italic"))
        uline_cb = wx.CheckBox(self.ctrl_pane, ID_ULINE, _("underline"))
        abox_sizer.AddMany([(bold_cb, 0, wx.ALIGN_CENTER_VERTICAL),
                            (eol_cb, 0, wx.ALIGN_CENTER_VERTICAL),
                            (ital_cb, 0, wx.ALIGN_CENTER_VERTICAL),
                            (uline_cb, 0, wx.ALIGN_CENTER_VERTICAL)])
        setting_top.Add(abox_sizer, 0, wx.ALIGN_TOP)

        # Font
        fh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        font_box = wx.StaticBox(self.ctrl_pane, label=_("Font Settings") + u":")
        fbox_sizer = wx.StaticBoxSizer(font_box, wx.VERTICAL)
        # Font Face Name
        fsizer = wx.BoxSizer(wx.HORIZONTAL)
        flbl = wx.StaticText(self.ctrl_pane, wx.ID_ANY, _("Font") + u": ")
        fontenum = wx.FontEnumerator()
        fontenum.EnumerateFacenames(fixedWidthOnly=True)
        f_lst = fontenum.GetFacenames()
        f_lst.sort()
        font_lst = ["%(primary)s", "%(secondary)s"]
        font_lst.extend(f_lst)
        fchoice = wx.Choice(self.ctrl_pane, ID_FONT, choices=font_lst)
        fsizer.AddMany([((5, 5)), (flbl, 0, wx.ALIGN_CENTER_VERTICAL),
                        (fchoice, 0, wx.ALIGN_CENTER_VERTICAL), ((5, 5))])
        fbox_sizer.Add(fsizer, 0, wx.ALIGN_LEFT)
        # Font Size
        fsize_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fsize_lbl = wx.StaticText(self.ctrl_pane, wx.ID_ANY, _("Size") + u": ")
        fsizes = ['%(size)d', '%(size2)d']
        for num in range(4, 21):
            fsizes.append(str(num))
        fs_choice = wx.Choice(self.ctrl_pane, ID_FONT_SIZE, 
                              choices = fsizes)
        fsize_sizer.AddMany([((5, 5)), (fsize_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                             (fs_choice, 0, wx.ALIGN_CENTER_VERTICAL), 
                             ((5, 5))])
        fbox_sizer.AddMany([((5, 5)), (fsize_sizer, 0, wx.ALIGN_LEFT)])
        fh_sizer.AddMany([((10, 10)), 
                          (fbox_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL),
                          ((10, 10))])

        # Build Section
        setting_sizer.AddMany([(setting_top, 0, wx.ALIGN_CENTER_HORIZONTAL), 
                               (fh_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)])
        return setting_sizer

    def StyleSheets(self):
        """Returns a sizer item that contains a choice control with
        all the available style sheets listed in it.
        @return: sizer item holding all installed style sheets

        """
        ss_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ss_lbl = wx.StaticText(self.ctrl_pane, wx.ID_ANY,
                               _("Style Theme") + u": ")
        ss_lst = util.GetResourceFiles(u'styles', get_all=True)
        ss_lst.sort()
        ss_choice = wx.Choice(self.ctrl_pane, ed_glob.ID_PREF_SYNTHEME,
                              choices=ss_lst)
        ss_choice.SetStringSelection(Profile_Get('SYNTHEME', 'str'))
        ss_new = wx.CheckBox(self.ctrl_pane, wx.ID_NEW, _("New"))
        ss_sizer.AddMany([((10, 10)), (ss_lbl, 0, wx.ALIGN_CENTER_VERTICAL), 
                          ((5, 0)),
                          (ss_choice, 0, wx.ALIGN_CENTER_VERTICAL), ((10, 0)), 
                          (ss_new, 0, wx.ALIGN_CENTER_VERTICAL), ((10, 10))])
        return ss_sizer

    def StyleTags(self):
        """Returns a sizer object containing a choice control with all
        current style tags in it.
        @return: sizer item containing list of all available style tags

        """
        style_sizer = wx.BoxSizer(wx.HORIZONTAL)
        style_sizer2 = wx.BoxSizer(wx.VERTICAL)
        style_lbl = wx.StaticText(self.ctrl_pane, wx.ID_ANY, 
                                  _("Style Tags") + u": ")
        style_tags = self.styles_orig.keys()
        style_tags.sort()
        style_lst = wx.ListBox(self.ctrl_pane, ID_STYLES, size = (150, 100),
                               choices = style_tags, style = wx.LB_SINGLE)
        style_sizer2.AddMany([(style_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                             (style_lst, 0, wx.ALIGN_CENTER_VERTICAL)])
        style_sizer.AddMany([((10, 10)), 
                             (style_sizer2, 0, 
                              wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND), 
                             ((10, 10))])
        return style_sizer

    def OnCancel(self, evt):
        """Catches the cancel button clicks and checks if anything
        needs to be done before closing the window.
        @param evt: event that called this handler

        """
        self.LOG('[style_editor] [cancel] Cancel Clicked Closing Window')
        evt.Skip()

    def OnCheck(self, evt):
        """Handles Checkbox events
        @param evt: event that called this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id == wx.ID_NEW:
            val = e_obj.GetValue()
            choice = self.ctrl_pane.FindWindowById(ed_glob.ID_PREF_SYNTHEME)
            choice.Enable(not val)
            if val:
                self.preview.StyleDefault()
                self.styles_new = self.preview.BlankStyleDictionary()
                self.styles_orig = self.DuplicateStyleDict(self.styles_new)
                self.preview.SetStyles(self.styles_new, nomerge=True)
                self.preview.DefineMarkers()
            else:
                scheme = choice.GetStringSelection().lower()
                self.preview.UpdateAllStyles(scheme)
        elif e_id in [ID_BOLD, ID_EOL, ID_ULINE, ID_ITALIC]:
            self.UpdateStyleSet(e_id)
        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handles the events generated from the choice controls
        @param evt: event that called this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        val = e_obj.GetStringSelection()
        if e_id == ed_glob.ID_LEXER:
            self.OpenPreviewFile(val)
        elif e_id == ed_glob.ID_PREF_SYNTHEME:
            # TODO Need to check for style changes before switching this
            self.preview.UpdateAllStyles(val)
            self.styles_new = self.preview.GetStyleSet()
            self.styles_orig = self.DuplicateStyleDict(self.styles_new)
            ctrl = self.FindWindowById(ID_STYLES)
            tag = ctrl.GetStringSelection()
            if tag != wx.EmptyString:
                self.UpdateSettingsPane(self.styles_new[tag])
        elif e_id in [ID_FONT, ID_FONT_SIZE]:
            self.UpdateStyleSet(e_id)
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Handles the window closer event
        @param evt: event that called this handler

        """
        self.OnOk(evt)

    def OnColor(self, evt):
        """Handles color selection events
        @param evt: event that called this handler

        """
        e_id = evt.GetId()
        e_obj = self.FindWindowById(e_id)
        e_val = evt.GetValue()[0:3]
        red = hex(e_val[0])
        green = hex(e_val[1])
        blue = hex(e_val[2])
        hex_str = "#%s%s%s" % (red[2:].zfill(2).upper(),
                               green[2:].zfill(2).upper(),
                               blue[2:].zfill(2).upper())
        e_obj.SetLabel(hex_str)
        e_obj.SetValue(wx.Color(e_val[0], e_val[1], e_val[2]))

        # Update The Style data for current tag
        self.UpdateStyleSet(e_id)

    def OnTextRegion(self, evt):
        """Processes clicks in the preview control and sets the style
        selection in the style tags list to the style tag of the area
        the cursor has moved into.
        @param evt: event that called this handler

        """
        style_id = self.preview.GetStyleAt(self.preview.GetCurrentPos())
        tag_lst = self.FindWindowById(ID_STYLES)
        data = self.preview.FindTagById(style_id)
        if data != wx.EmptyString:
            tag_lst.SetStringSelection(data)
            self.UpdateSettingsPane(self.styles_new[data])
            self.EnableSettings()
        evt.Skip()

    def OnListBox(self, evt):
        """Catches the selection of a style tag in the listbox
        and updates the style window appropriatly.
        @param evt: event that called this handler

        """
        e_id = evt.GetId()
        e_obj = self.FindWindowById(e_id)
        tag = e_obj.GetStringSelection()
        if tag != wx.EmptyString:
            self.UpdateSettingsPane(self.styles_new[tag])
            self.EnableSettings()
        else:
            self.EnableSettings(False)

    def OnOk(self, evt):
        """Catches the OK button click and checks if any changes need to be
        saved before the window closes.
        @param evt: event that called this handler

        """
        self.LOG('[style_editor] [Ok] Ok Clicked Closing Window')
        result = self.DiffStyles()
        if result == wx.ID_NO:
            evt.Skip()
        elif result == wx.ID_CANCEL:
            self.LOG('[style_editor] Info Canceled closer')
        else:
            result = self.ExportStyleSheet()
            if result != wx.ID_CANCEL:
                evt.Skip()

    def OnExport(self, evt):
        """Catches save button event
        @param evt: event that called this handler
        @postcondition: export file dialog is opened

        """
        self.LOG('[style_editor] [Save] Saving style changes')
        self.ExportStyleSheet()
        evt.Skip()

    def OpenPreviewFile(self, file_lbl):
        """Opens a file using the names in the Syntax Files choice
        control as a search query.
        @param file_lbl: name of file to open in test data directory

        """
        fname = file_lbl.replace(u" ", u"_").lower()
        fname = fname.replace(u"/", u"_")
        if fname != u"makefile":
            try:
                fname = glob.glob(ed_glob.CONFIG['TEST_DIR'] + fname + ".*")[0]
            except IndexError:
                self.LOG('[style_editor][err] File %s Does not exist' % fname)
                return False
        else:
            fname = ed_glob.CONFIG['TEST_DIR'] + fname

        if fname == '' or fname == None:
            return False

        self.preview.dirname = util.GetPathName(fname)
        self.preview.filename = util.GetFileName(fname)
        self.preview.ClearAll()
        self.preview.LoadFile(fname)
        self.preview.FindLexer()
        self.preview.EmptyUndoBuffer()
        return True

    def UpdateSettingsPane(self, syntax_data):
        """Updates all the settings controls to hold the
        values of the selected tag.
        @param syntax_data: syntax data set to configure panel from

        """
        val_str = str(syntax_data)
        val_map = { ID_FORE_COLOR : syntax_data.GetFore(),
                    ID_BACK_COLOR : syntax_data.GetBack(),
                    ID_BOLD       : "bold" in val_str,
                    ID_ITALIC     : "italic" in val_str,
                    ID_EOL        : "eol" in val_str,
                    ID_ULINE      : "underline" in val_str,
                    ID_FONT       : syntax_data.GetFace(),
                    ID_FONT_SIZE  : syntax_data.GetSize()
                  }
        if u"#" not in val_map[ID_FORE_COLOR]:
            val_map[ID_FORE_COLOR] = self.preview.GetDefaultForeColour(as_hex=True)
        if u"#" not in val_map[ID_BACK_COLOR]:
            val_map[ID_BACK_COLOR] = self.preview.GetDefaultBackColour(as_hex=True)

        for sid in SETTINGS_IDS:
            ctrl = self.FindWindowById(sid)
            c_type = ctrl.GetClassName()
            if c_type == 'wxCheckBox':
                ctrl.SetValue(val_map[sid])
            elif c_type == "wxChoice":
                ctrl.SetStringSelection(val_map[sid])
            elif c_type == "wxBitmapButton":
                # Note: must call set label before set value or the label
                # is not redrawn
                ctrl.SetLabel(val_map[sid][:7])
                ctrl.SetValue(wx.Color(int(val_map[sid][1:3], 16), 
                                       int(val_map[sid][3:5], 16), 
                                       int(val_map[sid][5:7], 16)))
        return True

    def UpdateStyleSet(self, id_):
        """Updates the value of the style tag to reflect any changes
        made in the settings controls.
        @param id: identifier of the style tag in the list

        """
        # Get the tag that has been modified
        tag = self.FindWindowById(ID_STYLES)
        tag = tag.GetStringSelection()
        if tag == None or tag == wx.EmptyString:
            return False

        # Get the modified value
        ctrl = self.FindWindowById(id_)
        ctrl_t = ctrl.GetClassName()
        if ctrl_t == 'wxCheckBox':
            val = ctrl.GetValue()
        elif ctrl_t == 'wxChoice':
            val = ctrl.GetStringSelection()
        elif ctrl_t == 'wxBitmapButton':
            val = ctrl.GetLabel()
        else:
            return False

        # Update the value of the modified tag
        val_map = { ID_FONT       : u'face',
                    ID_FONT_SIZE  : u'size',
                    ID_BOLD       : u"bold",
                    ID_EOL        : u"eol",
                    ID_ITALIC     : u"italic",
                    ID_ULINE      : u"underline",
                    ID_FORE_COLOR : u"fore",
                    ID_BACK_COLOR : u"back"
                  }

        if id_ in [ ID_FONT, ID_FONT_SIZE, ID_FORE_COLOR, ID_BACK_COLOR ]:
            self.styles_new[tag].SetNamedAttr(val_map[id_], val)
        elif id_ in [ ID_BOLD, ID_ITALIC, ID_ULINE, ID_EOL ]:
            self.styles_new[tag].SetExAttr(val_map[id_], val)
        else:
            return False

        # Update the Preview Area
        self.preview.SetStyleTag(tag, self.styles_new[tag])
        self.preview.RefreshStyles()
