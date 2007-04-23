##############################################################################
#    Copyright (C) 2007 Cody Precord                                         #
#    cprecord@editra.org                                                     #
#                                                                            #
#    Editra is free software; you can redistribute it and#or modify          #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation; either version 2 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    Editra is distributed in the hope that it will be useful,               #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with this program; if not, write to the                           #
#    Free Software Foundation, Inc.,                                         #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.               #
##############################################################################

"""
#----------------------------------------------------------------------------#
# FILE: prefdlg.py
# LANGUAGE: Python							   
#
# SUMMARY:
#     The classes and functions contained in this file are used for creating
#     the preference dialog.
#
#----------------------------------
# CLASS: PrefDlg
#
# METHODS:
#     - __init__ : Initializes the preference dialog
#     - OnSize: 
#
#----------------------------------
# CLASS: PrefPages
#
# METHODS:
#    - __init__ :
#    - GeneralPage :
#    - ProfilePage :
#    - StylePage :
#    - UpdatePage :
#
#----------------------------------
# CLASS: ProfileListCtrl
#
# METHODS:
#    - __init__ :
#    - PopulateProfileView : 
#
#----------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#----------------------------------------------------------------------------#
# Dependancies
import wx
import wx.lib.mixins.listctrl as listmix
import sys
import ed_glob
import ed_i18n
import ed_event
import updater
import util

_ = wx.GetTranslation
#----------------------------------------------------------------------------#
# Globals
ID_CHECK_UPDATE = wx.NewId()
ID_DOWNLOAD     = wx.NewId()
ID_UPDATE_MSG   = wx.NewId()
ID_UPDATE_PAGE  = wx.NewId()
ID_CURR_BOX     = wx.NewId()
ID_LATE_BOX     = wx.NewId()

# ID's For Validator
ID_VALS = [ ed_glob.ID_PREF_AALIAS, ed_glob.ID_PREF_LANG, ed_glob.ID_BRACKETHL, 
            ed_glob.ID_KWHELPER, ed_glob.ID_SYNTAX, ed_glob.ID_INDENT_GUIDES,
            ed_glob.ID_WORD_WRAP, ed_glob.ID_PREF_TABS, ed_glob.ID_PREF_TABW,
            ed_glob.ID_SHOW_WS, ed_glob.ID_PREF_METAL, ed_glob.ID_PREF_FHIST,
            ed_glob.ID_PREF_WSIZE, ed_glob.ID_PREF_WPOS, ed_glob.ID_PREF_ICON,
            ed_glob.ID_PREF_MODE, ed_glob.ID_SHOW_EOL, ed_glob.ID_PREF_SYNTHEME,
            ed_glob.ID_PREF_ICONSZ, ed_glob.ID_EOL_MODE, ed_glob.ID_PRINT_MODE,
            ed_glob.ID_FOLDING, ed_glob.ID_AUTOCOMP, ed_glob.ID_SHOW_LN,
            ed_glob.ID_PREF_SPOS, ed_glob.ID_AUTOINDENT]

#----------------------------------------------------------------------------#

class PrefDlg(wx.Dialog):
    """Preference Dialog Class"""
    def __init__(self, parent, log):
        """Initialize the Preference Dialog"""
        pre = wx.PreDialog()

        if wx.Platform == '__WXMAC__' and ed_glob.PROFILE.has_key('METAL'):
            if ed_glob.PROFILE['METAL']:
                pre.SetExtraStyle(wx.DIALOG_EX_METAL)

        pre.Create(parent, -1, _('Preferences'))
        self.PostCreate(pre)

        # Attributes
        self.LOG = log
        self.act_ids = []
        self.act_objs = []

        self.LOG("[prefdlg_info] Preference Dialog Initializing...")
        # Create Notebook
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ntb = PrefPages(self, wx.ID_ANY, log)
        sizer.Add(self.ntb, 0, wx.EXPAND)

        # Create the buttons
        b_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancel_b = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        apply_b = wx.Button(self, wx.ID_APPLY, _("Apply"))
        ok_b = wx.Button(self, wx.ID_OK, _("Ok"))
        ok_b.SetDefault()
        b_sizer.Add(cancel_b, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        b_sizer.Add(apply_b, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        b_sizer.Add(ok_b, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(b_sizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer.Fit(self)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # Styling
        if ed_glob.PROFILE.has_key('ALPHA'):
            self.SetTransparent(ed_glob.PROFILE['ALPHA'])

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnOk, ok_b)
        self.Bind(wx.EVT_BUTTON, self.OnApply, apply_b)
        self.LOG("[prefdlg_info] Preference Dialog Created")

    #---- End Init ----#

    #---- Function Definitions ----#
    def OnOk(self, evt):
        """Checks all pages for changes and applys them"""
        self.LOG("[pref_evt] Clicked Ok, Applying Changes")
        pages = self.ntb.GetChildren()
        # Gather all values that are valid
        for page in pages:
            objects = page.GetChildren()
            items = util.GetIds(objects)
            self.ValidateItems(items, objects)
        if len(self.act_ids) > 0:     
            self.UpdateProfile()
            self.LOG("[pref_info] All changes have been applied")
        parent = self.GetParent()
        parent.nb.UpdateTextControls()
        toolbar = parent.GetToolBar()
        if toolbar != None and (toolbar.GetToolTheme() != ed_glob.PROFILE['ICONS'] \
           or toolbar.GetToolSize() != ed_glob.PROFILE['ICON_SZ']):
            parent.GetToolBar().ReInit()
        evt.Skip()

    def OnApply(self, evt):
        """Applys preference changes"""
        self.LOG("[pref_evt] Clicked Apply, Applying changes on selected page.")
        page = self.ntb.GetSelection()
        page = self.ntb.GetPage(page)
        objects = page.GetChildren()
        items = util.GetIds(objects)
        self.ValidateItems(items, objects)
        if len(self.act_ids) > 0:
            self.UpdateProfile()
            self.GetParent().nb.UpdateTextControls()
            toolbar = self.GetParent().GetToolBar()
            if toolbar != None and \
               (toolbar.GetToolTheme() != ed_glob.PROFILE['ICONS'] \
               or toolbar.GetToolSize() != ed_glob.PROFILE['ICON_SZ']):
                toolbar.ReInit()
            self.LOG("[pref_info] Changes Applied")
        evt.Skip()

    def ValidateItems(self, item_lst, obj_lst):
        """Checks list of Ids for ones that need to be
        checked for value changes. Then maps the Ids to
        object values and sets the prefrence dialogs attributes
        to hold these two values.

        """
        id_to_save = []  # Ids to save
        obj_to_save = []    # objs to save

        # Find Items to save
        for item in item_lst:
            if item in ID_VALS:
                id_to_save.append(item)
                obj_to_save.append(obj_lst[item_lst.index(item)])
        
        self.act_ids.extend(id_to_save)
        self.act_objs.extend(obj_to_save)
        return

    def UpdateProfile(self):
        """Updates the global PROFILE dictionary to reflect
        the changes made in this dialog.

        """
        for obj in self.act_objs:
            value = obj.GetValue()
            ob_id = obj.GetId()
            # TODO This is does not do any value validation
            # If a string value as been set to an empty string ignore it and
            # keep the old value.
            if value == "":
                continue
            if ob_id == ed_glob.ID_PREF_ICONSZ:
                value = (int(value), int(value))
            prof_key = ed_glob.ID_2_PROF[self.act_ids[self.act_objs.index(obj)]]
            ed_glob.PROFILE[prof_key] = value
            if prof_key == 'METAL':
                if ed_glob.PROFILE['METAL']:
                    self.SetExtraStyle(wx.DIALOG_EX_METAL)
                    self.GetParent().SetExtraStyle(wx.FRAME_EX_METAL)
                else:
                    self.SetExtraStyle(wx.DEFAULT_DIALOG_STYLE)
                    self.GetParent().SetExtraStyle(10)
        return 0
    #---- End Function Definitions ----#

#----------------------------------------------------------------------------#
# Class Globals
PREF_WIDTH = 550
PREF_HEIGHT = 350

class PrefPages(wx.Notebook):
    """Notebook to hold pages for Preference Dialog"""
    def __init__(self, parent, id_num, log):
        """Initializes the notebook"""
        wx.Notebook.__init__(self, parent, id_num, size = (PREF_WIDTH, PREF_HEIGHT),
                             style = wx.NB_TOP
                            )
        # Attributes
        self.LOG = log

        # Events
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHOICE, self.OnChoice, id=ed_glob.ID_PREF_SYNTHEME)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(ed_event.EVT_UPDATE_TEXT, self.OnUpdateText)

        # Initialize Preference Pages
        self.GeneralPage()
        self.MiscPage()
        self.CodePage()
        self.TextPage()
        self.UpdatePage()
        self.ProfilePage()

    #---- End Init ----#

    #---- Function Definitions ----#
    def OnChoice(self, evt):
        """Handles Choice Control Actions"""
        evt_id = evt.GetId()
        evt_obj = evt.GetEventObject()
        if evt_id == ed_glob.ID_PREF_SYNTHEME:
            main_win = self.GetGrandParent()
            ed_glob.PROFILE['SYNTHEME'] = evt_obj.GetValue()
            main_win.nb.UpdateTextControls()
        else:
            evt.Skip()

    def OnSetTransparent(self, evt):
        """Sets the transparency of the editor while the slider
        is being dragged.

        """
        if evt.GetId() == ed_glob.ID_TRANSPARENCY:
            grandpappy = self.GetGrandParent() # Main Window
            pappy = self.GetParent()
            trans = evt.GetEventObject()
            value = trans.GetValue()
            grandpappy.SetTransparent(value)
            pappy.SetTransparent(value)
            ed_glob.PROFILE['ALPHA'] = value

    def GeneralPage(self):
        """Creates the general preferences page"""
        gen_panel = wx.Panel(self, wx.ID_ANY)

        info_txt = [ "Most changes made in this dialog currently require the program",
                     "to be restarted before taking effect."]

        info = wx.StaticText(gen_panel, wx.ID_ANY, "\n".join(info_txt))
        
        # Startup Settings
        ## Editor Mode
        mode_lbl = wx.StaticText(gen_panel, wx.ID_ANY, _("Editor Mode") + u": ")
        mode_c = ExChoice(gen_panel, ed_glob.ID_PREF_MODE,
                          choices=['CODE', 'DEBUG', 'GUI_DEBUG'],
                          default=ed_glob.PROFILE['MODE'])
        mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mode_sizer.Add((15, 15))
        mode_sizer.Add(mode_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        mode_sizer.Add((5, 15))
        mode_sizer.Add(mode_c, 0, wx.ALIGN_CENTER_VERTICAL)
        ## Print Mode
        pmode_lbl = wx.StaticText(gen_panel, wx.ID_ANY, _("Printer Mode") + u": ")
        pmode_c = ExChoice(gen_panel, ed_glob.ID_PRINT_MODE,
                           choices=['Black/White', 'Colour/White', 'Colour/Default',
                                    'Inverse', 'Normal'],
                           default=ed_glob.PROFILE['PRINT_MODE'])
        mode_sizer.Add((20, 20))
        mode_sizer.Add(pmode_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        mode_sizer.Add((5, 5))
        mode_sizer.Add(pmode_c, 0, wx.ALIGN_CENTER_VERTICAL)

        # Locale Settings
        lang_lbl = wx.StaticText(gen_panel, wx.ID_ANY, 
                                 _("Language") + u": ", pos=wx.Point(50, 130))
        lang_c = ed_i18n.LangListCombo(gen_panel, ed_glob.ID_PREF_LANG, 
                                       ed_glob.PROFILE['LANG'])
        lang_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_sizer.Add((15, 0))
        lang_sizer.Add(lang_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        lang_sizer.Add((5, 0))
        lang_sizer.Add(lang_c, 0, wx.ALIGN_CENTER_VERTICAL)

        # Build Page
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(info, 0, wx.CENTER)
        sizer.Add((15, 15))
        sizer.Add(self.SectionHead(gen_panel, _("Startup Settings")))
        sizer.Add(mode_sizer, 0, wx.BOTTOM | wx.LEFT, 20)
        sizer.Add((15, 45))
        sizer.Add(self.SectionHead(gen_panel, _("Locale Settings")))
        sizer.Add(lang_sizer, 0, wx.BOTTOM | wx.LEFT, 20)
        gen_panel.SetSizer(sizer)

        self.AddPage(gen_panel, _("General"))

    def ProfilePage(self):
        """Creates the profile editor page"""
        prof_panel = wx.Panel(self, wx.ID_ANY)
        # Bind size evt to this panel
        prof_panel.Bind(wx.EVT_SIZE, self.OnSize)
        # Add Profile Viewer to Panel
        self.list = ProfileListCtrl(prof_panel)

        self.AddPage(prof_panel, _("Profile Viewer"))

    def CodePage(self):
        """Code preference page"""
        code_panel = wx.Panel(self, wx.ID_ANY)

        # Feature Settings
        feat_lbl = self.SectionHead(code_panel, _("Features"))
        ai_cb = wx.CheckBox(code_panel, ed_glob.ID_AUTOINDENT, _("Auto-Indent"))
        ai_cb.SetValue(ed_glob.PROFILE['AUTO_INDENT'])
        br_cb = wx.CheckBox(code_panel, ed_glob.ID_BRACKETHL, _("Bracket Highlighting"))
        br_cb.SetValue(ed_glob.PROFILE['BRACKETHL'])
        kh_cb = wx.CheckBox(code_panel, ed_glob.ID_KWHELPER, _("Keyword Helper"))
        kh_cb.SetValue(ed_glob.PROFILE['KWHELPER'])
        ind_cb = wx.CheckBox(code_panel, ed_glob.ID_INDENT_GUIDES, _("Indentation Guides"))
        ind_cb.SetValue(ed_glob.PROFILE['GUIDES'])
        fold_cb = wx.CheckBox(code_panel, ed_glob.ID_FOLDING, _("Code Folding"))
        fold_cb.SetValue(ed_glob.PROFILE['CODE_FOLD'])
        feat_sizer = wx.BoxSizer(wx.VERTICAL)
        feat_sizer.AddMany([ai_cb, br_cb, fold_cb, ind_cb, kh_cb]) 

        # Syntax / Completion Settings
        syn_lbl = self.SectionHead(code_panel, _("Syntax && Completion"))
        syn_cb = wx.CheckBox(code_panel, ed_glob.ID_SYNTAX, _("Syntax Highlighting"))
        syn_cb.SetValue(ed_glob.PROFILE['SYNTAX'])

        syn_theme_lbl = wx.StaticText(code_panel, wx.ID_ANY, _("Color Scheme") + u": ")
        syn_theme = ExChoice(code_panel, ed_glob.ID_PREF_SYNTHEME,
                              choices=util.GetResourceFiles(u'styles', get_all=True),
                              default=str(ed_glob.PROFILE['SYNTHEME']))
        comp_cb = wx.CheckBox(code_panel, ed_glob.ID_AUTOCOMP, _("Auto-Completion"))
        comp_cb.SetValue(ed_glob.PROFILE['AUTO_COMP'])

        # Build Section
        syn_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        syn_sizer1.Add(syn_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        syn_sizer1.Add((80, 0))
        syn_sizer1.Add(syn_theme_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        syn_sizer1.Add(syn_theme, 0, wx.RIGHT)
        syn_sizer2 = wx.BoxSizer(wx.VERTICAL)
        syn_sizer2.Add(syn_sizer1, 0, wx.RIGHT)
        syn_sizer2.Add(comp_cb, 0, wx.ALIGN_LEFT)

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add((15, 15))
        border.Add(feat_lbl, 0, wx.LEFT)
        border.Add(feat_sizer, 0, wx.BOTTOM | wx.LEFT, 30)
        border.Add((10, 10))
        border.Add(syn_lbl, 0, wx.LEFT)
        border.Add(syn_sizer2, 0, wx.BOTTOM | wx.LEFT, 30)
        code_panel.SetSizer(border)

        self.AddPage(code_panel, _("Code"))

    def TextPage(self):
        """Adds a Text Preferences Page"""
        text_panel = wx.Panel(self, wx.ID_ANY)

        # Format Section Label
        format_lbl = self.SectionHead(text_panel,  _("Format"))
        tw_lbl = wx.StaticText(text_panel, wx.ID_ANY, _("Tab Width") + u":  ")
        tw_cb = ExChoice(text_panel, ed_glob.ID_PREF_TABW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=str(ed_glob.PROFILE['TABWIDTH']))
        ut_cb = wx.CheckBox(text_panel, ed_glob.ID_PREF_TABS, _("Use Tabs Instead of Whitespaces"))
        ut_cb.SetValue(ed_glob.PROFILE['USETABS'])
        tab_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tabw_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tab_sizer.Add(ut_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        tab_sizer.Add((40, 40))
        tabw_sizer.Add(tw_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        tabw_sizer.Add(tw_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        tab_sizer.Add(tabw_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
        eol_lbl = wx.StaticText(text_panel, wx.ID_ANY, _("EOL Mode") + u":  ")
        eol_cb = ExChoice(text_panel, ed_glob.ID_EOL_MODE,
                          choices=[_("Macintosh (\\r)"), _("Unix (\\n)"), _("Windows (\\r\\n)")],
                          default=ed_glob.PROFILE['EOL'])
        eol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        eol_sizer.Add(eol_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        eol_sizer.Add(eol_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        ww_cb = wx.CheckBox(text_panel, ed_glob.ID_WORD_WRAP, _("Word Wrap"))
        ww_cb.SetValue(ed_glob.PROFILE['WRAP'])
        format_sizer = wx.BoxSizer(wx.VERTICAL)
        format_sizer.AddMany([eol_sizer, tab_sizer, ww_cb]) 

        # Misc Section
        misc_lbl = self.SectionHead(text_panel,  _("Misc"))
        aa_cb = wx.CheckBox(text_panel, ed_glob.ID_PREF_AALIAS, _("AntiAliasing"))
        aa_cb.SetValue(ed_glob.PROFILE['AALIASING'])
        seol_cb = wx.CheckBox(text_panel, ed_glob.ID_SHOW_EOL, _("Show EOL Markers"))
        seol_cb.SetValue(ed_glob.PROFILE['SHOW_EOL'])
        sln_cb = wx.CheckBox(text_panel, ed_glob.ID_SHOW_LN, _("Show Line Numbers"))
        sln_cb.SetValue(ed_glob.PROFILE['SHOW_LN'])
        sws_cb = wx.CheckBox(text_panel, ed_glob.ID_SHOW_WS, _("Show Whitespace"))
        sws_cb.SetValue(ed_glob.PROFILE['SHOW_WS'])

        misc_sizer = wx.BoxSizer(wx.VERTICAL)
        misc_sizer.AddMany([aa_cb, seol_cb, sln_cb, sws_cb]) 

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add((15, 15))
        border.Add(format_lbl, 0, wx.LEFT)
        border.Add(format_sizer, 0, wx.BOTTOM | wx.LEFT, 30)
        border.Add((10, 10))
        border.Add(misc_lbl, 0, wx.LEFT)
        border.Add(misc_sizer, 0, wx.BOTTOM | wx.LEFT, 30)
        text_panel.SetSizer(border)
        self.AddPage(text_panel, _("Text"))

    def MiscPage(self):
        """Misc preference page"""
        misc_panel = wx.Panel(self, wx.ID_ANY)

        # Misc Settings Section
        set_lbl = self.SectionHead(misc_panel, _("Settings"))
        fh_lbl = wx.StaticText(misc_panel, wx.ID_ANY, _("File History Depth") + u":  ")
        fh_cb = ExChoice(misc_panel, ed_glob.ID_PREF_FHIST,
                          choices=['1','2','3','4','5','6','7','8','9'],
                          default=str(ed_glob.PROFILE['FHIST_LVL']))
        fh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fh_sizer.Add(fh_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        fh_sizer.Add(fh_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        set_sizer = wx.BoxSizer(wx.VERTICAL)
        set_sizer.Add(fh_sizer, 0, wx.ALIGN_LEFT)
        pos_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_SPOS, _("Remember File Position"))
        pos_cb.SetValue(ed_glob.PROFILE['SAVE_POS'])
        set_sizer.Add(pos_cb, 0, wx.ALIGN_LEFT)

        # Various Appearance Settings
        app_lbl = self.SectionHead(misc_panel, _("Appearance"))
        app_sizer = wx.BoxSizer(wx.VERTICAL)
        tb_icont = wx.StaticText(misc_panel, wx.ID_ANY, _("Icon Theme") + u": ")
        tb_icon = ExChoice(misc_panel, id=ed_glob.ID_PREF_ICON,
                            choices=util.GetResources(u"pixmaps" + util.GetPathChar() + u"theme"), 
                            default=ed_glob.PROFILE['ICONS'].title())
        tb_isz_lbl = wx.StaticText(misc_panel, wx.ID_ANY, _("Icon Size") + u": ")
        tb_isz_ch = ExChoice(misc_panel, id=ed_glob.ID_PREF_ICONSZ,
                              choices=['16', '24', '32'],
                              default=str(ed_glob.PROFILE['ICON_SZ'][0]))
        tbi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tbi_sizer.Add(tb_icont, 0, wx.ALIGN_LEFT)
        tbi_sizer.Add(tb_icon, 0, wx.ALIGN_LEFT)
        tbi_sizer.Add((40, 0))
        tbi_sizer.Add(tb_isz_lbl, 0, wx.RIGHT)
        tbi_sizer.Add(tb_isz_ch, 0, wx.RIGHT)
        app_sizer.Add(tbi_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # MAC and MSW support transparency settings
        if wx.Platform in ['__WXMAC__', '__WXMSW__']:
            trans_sizer = wx.BoxSizer(wx.HORIZONTAL)
            trans_lbl = wx.StaticText(misc_panel, wx.ID_ANY, _("Transparency") + u" ")
            trans = wx.Slider(misc_panel, ed_glob.ID_TRANSPARENCY, 
                              ed_glob.PROFILE['ALPHA'], 100, 255, 
                              style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
            trans.SetTickFreq(5, 1)
            trans_sizer.Add(trans_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
            trans_sizer.Add(trans, 0, wx.ALIGN_LEFT)
            app_sizer.Add((5, 5))
            app_sizer.Add(trans_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
            app_sizer.Add((5, 5))
            self.Bind(wx.EVT_SLIDER, self.OnSetTransparent, id=ed_glob.ID_TRANSPARENCY)

        # Activate Metal Style Windows for OSX
        if wx.Platform == '__WXMAC__':
            m_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_METAL, _("Use Metal Style (OS X Only)"))
            if ed_glob.PROFILE.has_key('METAL'):
                m_cb.SetValue(ed_glob.PROFILE['METAL'])
            else:
                m_cb.SetValue(False)
            app_sizer.Add(m_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        ws_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_WSIZE, _("Remember Window Size on Exit"))
        ws_cb.SetValue(ed_glob.PROFILE['SET_WSIZE'])
        app_sizer.Add(ws_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        wp_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_WPOS, _("Remember Window Position on Exit"))
        wp_cb.SetValue(ed_glob.PROFILE['SET_WPOS'])
        app_sizer.Add(wp_cb, 0, wx.ALIGN_CENTER_VERTICAL)

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add((15, 15))
        border.Add(set_lbl, 0, wx.LEFT)
        border.Add((15, 10))
        border.Add(set_sizer, 0, wx.LEFT, 30)
        border.Add((15, 15))
        border.Add(app_lbl, 0, wx.LEFT)
        border.Add(app_sizer, 0, wx.LEFT, 30)
        misc_panel.SetSizer(border)
        self.AddPage(misc_panel, _("Misc"))

    def UpdatePage(self):
        """Update Status page"""
        upd_panel = wx.Panel(self, ID_UPDATE_PAGE)

        info = self.SectionHead(upd_panel, _("Update Status") + u":")
        cur_box = wx.StaticBox(upd_panel, ID_CURR_BOX, _("Installed Version"))
        cur_sz = wx.StaticBoxSizer(cur_box, wx.HORIZONTAL)
        cur_sz.SetMinSize(wx.Size(150, 40))
        cur_ver = wx.StaticText(upd_panel, wx.ID_ANY,  ed_glob.version)
        cur_sz.Add(cur_ver, 0, wx.ALIGN_CENTER_HORIZONTAL)
        e_update = updater.UpdateProgress(upd_panel, ed_glob.ID_PREF_UPDATE_BAR,
                                          size=wx.Size(320, 50))
        upd_box = wx.StaticBox(upd_panel, ID_LATE_BOX, _("Latest Version"))
        upd_bsz = wx.StaticBoxSizer(upd_box, wx.HORIZONTAL)
        upd_bsz.SetMinSize(wx.Size(150, 40))
        upd_sta = wx.StaticText(upd_panel, ID_UPDATE_MSG, _(e_update.GetStatus()))
        upd_bsz.Add(upd_sta, 0, wx.ALIGN_CENTER_HORIZONTAL)
        upd_bsz.Layout()

        # Build Page Layout (from top to bottom)
        border = wx.BoxSizer(wx.HORIZONTAL) # Main Outer H Sizer
        v_stack = wx.BoxSizer(wx.VERTICAL)  # Main Inner V Sizer
        v_stack.Add((15, 15))
        v_stack.Add(info, 0, wx.ALIGN_CENTER) # page header
        v_stack.Add((15, 15))

        # Status Text
        stat_sz = wx.BoxSizer(wx.HORIZONTAL)
        stat_sz.Add(wx.Size(15,15))
        stat_sz.Add(cur_sz, 1, wx.ALIGN_LEFT)
        stat_sz.Add(wx.Size(50,50))
        stat_sz.Add(upd_bsz, 1, wx.ALIGN_RIGHT)

        # Progress Bar
        p_barsz = wx.BoxSizer(wx.HORIZONTAL)
        p_barsz.Add(wx.Size(15,15))
        p_barsz.Add(e_update, 0, wx.ALIGN_CENTER_VERTICAL)

        # Progress bar control buttons
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)
        btn_sz.Add(wx.Size(15,15))
        check_b = wx.Button(upd_panel, ID_CHECK_UPDATE, _("Check"))
        btn_sz.Add(check_b, 0, wx.ALIGN_LEFT)
        btn_sz.Add(wx.Size(30,30))
        dl_b    = wx.Button(upd_panel, ID_DOWNLOAD, _("Download"))
        dl_b.Disable()
        btn_sz.Add(dl_b, 0, wx.ALIGN_RIGHT)
        btn_sz.Add(wx.Size(15,15))

        v_stack.Add(wx.Size(15,15))
        v_stack.Add(stat_sz, 0, wx.ALIGN_CENTER)
        v_stack.Add(wx.Size(20,20))
        v_stack.Add(p_barsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
        v_stack.Add(wx.Size(20,20))
        v_stack.Add(btn_sz, 0, wx.ALIGN_CENTER_HORIZONTAL)

        border.Add(v_stack, 0, wx.ALIGN_LEFT)

        upd_panel.SetSizer(border)

        self.AddPage(upd_panel, _("Update"))

    def SectionHead(self, parent, title):
        """"Creates a section heading on a given page with a given
        title as a sizer object.

        """
        # Create the return container
        ret_obj = wx.BoxSizer(wx.HORIZONTAL)

        # Build the objects
        heading = wx.StaticText(parent, wx.ID_ANY, title)
        h_width = (int(parent.GetParent().GetSize()[0] * .90) - heading.GetSize()[0])
        divider = wx.StaticLine(parent, wx.ID_ANY, size=(h_width, 2))

        # Build Heading
        ret_obj.Add((15, 0))
        ret_obj.Add(heading, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT)
        ret_obj.Add((10, 0))
        l_sizer = wx.BoxSizer(wx.VERTICAL)
        l_sizer.Add((0, 8))
        l_sizer.Add(divider, 2, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER)
        l_sizer.Add((0, 10))
        ret_obj.Add(l_sizer)
        return ret_obj

    #---- Event Handlers ----#
    def OnButton(self, evt):
        """Event Handler for Buttons"""
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id == ID_CHECK_UPDATE:
            self.LOG("[prefdlg_evt] Check Update Clicked")
            e_obj.Disable()
            prog_bar = self.FindWindowById(ed_glob.ID_PREF_UPDATE_BAR)
            # Note this function returns right away but its result is
            # handled on a separate thread. This window is then notified
            # via a custom event being posted by the control.
            prog_bar.CheckForUpdates()
        elif e_id == ID_DOWNLOAD:
            self.LOG("[prefdlg_evt] Download Updates Clicked")
            e_obj.Disable()
            chk_bt = self.FindWindowById(ID_CHECK_UPDATE)
            chk_bt.Disable()
            dl_dlg = updater.DownloadDialog(None, wx.ID_ANY,
                                            _("Downloading Update"), 
                                            size=wx.Size(350, 200))
            dp_sz = wx.GetDisplaySize()
            dl_dlg.SetPosition(wx.Point((dp_sz[0] - (dl_dlg.GetSize()[0] + 5)), 25))
            dl_dlg.Show()
        else:
            evt.Skip()

    def OnPageChanged(self, evt):
        """Actions to do after a page change"""
        curr = evt.GetSelection()
        txt = self.GetPageText(curr)
        self.LOG("[prefdlg_evt] Page Changed to " + txt)
        evt.Skip()

    def OnUpdateText(self, evt):
        """Handles text update events"""
        e_id = evt.GetId()
        self.LOG("[prefdlg_evt] Updating version status text")
        txt = self.FindWindowById(ID_UPDATE_MSG)
        upd = self.FindWindowById(ed_glob.ID_PREF_UPDATE_BAR)
        if None not in [txt, upd]:
            if e_id == upd.ID_CHECKING:
                txt.SetLabel(upd.GetStatus())
                u_pg = wx.FindWindowById(ID_UPDATE_PAGE)
                dl_bt = chk_bt = None
                if u_pg != None:
                    dl_bt = u_pg.FindWindowById(ID_DOWNLOAD)
                    chk_bt = u_pg.FindWindowById(ID_CHECK_UPDATE)
                    u_pg.Layout()
                if dl_bt != None and upd.GetUpdatesAvailable():
                    dl_bt.Enable()
                if chk_bt != None:
                    chk_bt.Enable()

    def OnSize(self, evt):
        """Resizes the list control to fit the panel"""
        width, height = self.GetClientSizeTuple()
        self.list.SetDimensions(0, 0, width, height)
        evt.Skip()

#---- End Function Definitions ----#

#----------------------------------------------------------------------------#

class ProfileListCtrl(wx.ListCtrl, 
                  listmix.ListCtrlAutoWidthMixin,
                  listmix.TextEditMixin):
    """Class to manage the profile editor"""
    def __init__(self, parent):
        """Initializes the Profile List Control"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, wx.DefaultSize, 
                             style = wx.LC_REPORT | wx.LC_SORT_ASCENDING |
                                     wx.LC_VRULES)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.PopulateProfileView()
        listmix.TextEditMixin.__init__(self)

    def PopulateProfileView(self):
        """Populates the profile view with the profile info"""
        self.InsertColumn(0, _("Item"))
        self.InsertColumn(1, _("Value"))

        prof = []
        for ind in ed_glob.PROFILE:
            prof.append(ind)
        prof.sort()

        for key in prof:
            val = unicode(ed_glob.PROFILE[key])
            index = self.InsertStringItem(sys.maxint, key)
            self.SetStringItem(index, 0, key)
            self.SetStringItem(index, 1, val)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)


    #---- End Function Definitions ----#

#----------------------------------------------------------------------------#
class ExChoice(wx.Choice):
    """Class to extend wx.Choice to have the GetValue
    function. This allows the application function to remain
    uniform in its value retrieval from all objects. This also extends 
    wx.Choice to have a default selected value on init.

    """
    def __init__(self, parent, id, pos=(-1, -1), size=(-1, -1), choices=[], default=None):
        """Constructs a Choice Control"""
        wx.Choice.__init__(self, parent=parent, id=id, pos=pos, size=size, choices=choices)
        if default != None:
            self.SetStringSelection(default)

    def GetValue(self):
        """Gets the Selected Value"""
        val = self.GetStringSelection()
        if val.isalpha():
            val.lower()
        return val

#----------------------------------------------------------------------------#

