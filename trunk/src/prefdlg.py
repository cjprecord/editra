##############################################################################
#    Copyright (C) 2007 Cody Precord                                         #
#    cprecord@editra.org                                                     #
#                                                                            #
#    This program is free software; you can redistribute it and#or modify    #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation; either version 2 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #
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
import util
import dev_tool

_ = wx.GetTranslation
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# ID's
ID_VALS = [ ed_glob.ID_PREF_AALIAS, ed_glob.ID_PREF_LANG, ed_glob.ID_BRACKETHL, 
            ed_glob.ID_KWHELPER, ed_glob.ID_SYNTAX, ed_glob.ID_INDENT_GUIDES,
            ed_glob.ID_WORD_WRAP, ed_glob.ID_PREF_TABS, ed_glob.ID_PREF_TABW,
            ed_glob.ID_SHOW_WS, ed_glob.ID_PREF_METAL, ed_glob.ID_PREF_FHIST,
            ed_glob.ID_PREF_WSIZE, ed_glob.ID_PREF_WPOS, ed_glob.ID_PREF_ICON ]

#----------------------------------------------------------------------------#

class PrefDlg(wx.Dialog):
    """Preference Dialog Class"""
    def __init__(self, parent):
        """Initialize the Preference Dialog"""
        dev_tool.DEBUGP("[prefdlg_info] Preference Dialog Initializing...")
        pre = wx.PreDialog()

        if wx.Platform == '__WXMAC__' and ed_glob.PROFILE.has_key('METAL'):
            if ed_glob.PROFILE['METAL']:
                pre.SetExtraStyle(wx.DIALOG_EX_METAL)

        pre.Create(parent, -1, _('Preferences'))
        self.PostCreate(pre)

        # Attributes
        self.act_ids = []
        self.act_objs = []

        # Create Notebook
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ntb = PrefPages(self, -1)
        sizer.Add(self.ntb, 0, wx.EXPAND)

        # Create the buttons
        b_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancel_b = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
        cancel_b.SetDefault()
        apply_b = wx.Button(self, wx.ID_APPLY, _("Apply"))
        apply_b.SetDefault()
        ok_b = wx.Button(self, wx.ID_OK, _("Ok"))
        ok_b.SetDefault()
        b_sizer.Add(cancel_b, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        b_sizer.Add(apply_b, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        b_sizer.Add(ok_b, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        sizer.Add(b_sizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnOk, ok_b)
        self.Bind(wx.EVT_BUTTON, self.OnApply, apply_b)
        dev_tool.DEBUGP("[prefdlg_info] Preference Dialog Created")

    #---- End Init ----#

    #---- Function Definitions ----#
    def OnOk(self, evt):
        """Checks all pages for changes and applys them"""
        dev_tool.DEBUGP("[pref_evt] Clicked Ok, Applying Changes")
        pages = self.ntb.GetChildren()
        # Gather all values that are valid
        for page in pages:
            objects = page.GetChildren()
            items = util.GetIds(objects)
            self.ValidateItems(items, objects)
        if len(self.act_ids) > 0:     
            self.UpdateProfile()
            dev_tool.DEBUGP("[pref_info] All changes have been applied")
        evt.Skip()
        
    def OnApply(self, evt):
        """Applys preference changes"""
        dev_tool.DEBUGP("[pref_evt] Clicked Apply, Applying changes on selected page.")
        page = self.ntb.GetSelection()
        page = self.ntb.GetPage(page)
        objects = page.GetChildren()
        items = util.GetIds(objects)
        self.ValidateItems(items, objects)
        if len(self.act_ids) > 0:
            self.UpdateProfile()
            dev_tool.DEBUGP("[pref_info] Changes Applied")
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
            # TODO This is does not do any value validation
            prof_key = ed_glob.ID_2_PROF[self.act_ids[self.act_objs.index(obj)]]
            ed_glob.PROFILE[prof_key] = value

        return 0
    #---- End Function Definitions ----#

#----------------------------------------------------------------------------#

class PrefPages(wx.Notebook):
    """Notebook to hold pages for Preference Dialog"""
    def __init__(self, parent, id_num):
        """Initializes the notebook"""
        wx.Notebook.__init__(self, parent, id_num, size = (500, 300),
                             style = wx.NB_TOP
                            )

        # Events
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)

        # Initialize Preference Pages
        self.GeneralPage()
        self.MiscPage()
        self.CodePage()
        self.TextPage()
        self.UpdatePage()
        self.ProfilePage()

    #---- End Init ----#

    #---- Function Definitions ----#

    def GeneralPage(self):
        """Creates the general preferences page"""
        gen_panel = wx.Panel(self, wx.ID_ANY)

        info_txt = [ "Most changes made in this dialog currently require the program",
                     "to be restarted before taking effect."]

        info = wx.StaticText(gen_panel, wx.ID_ANY, "\n".join(info_txt))
        lang_lbl = wx.StaticText(gen_panel, wx.ID_ANY, _("Language: "), pos=wx.Point(50,130))
        lang_c = ed_i18n.LangListCombo(gen_panel, ed_glob.ID_PREF_LANG, ed_glob.PROFILE['LANG'])
#ExChoice(gen_panel, id=ed_glob.ID_PREF_LANG,
#                           choices=util.GetResources(u"locale"), 
#                           default=ed_glob.PROFILE['LANG'].title())
        lang_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_sizer.Add(lang_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        lang_sizer.Add(lang_c, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(info, 0, wx.CENTER)
        sizer.Add(lang_sizer, 80, wx.BOTTOM)
        gen_panel.SetSizer(sizer)

        self.AddPage(gen_panel, u"General")

    def ProfilePage(self):
        """Creates the profile editor page"""
        prof_panel = wx.Panel(self, wx.ID_ANY)
        # Bind size evt to this panel
        prof_panel.Bind(wx.EVT_SIZE, self.OnSize)
        # Add Profile Editor to Panel
        self.list = ProfileListCtrl(prof_panel)

        self.AddPage(prof_panel, _("Profile Viewer"))

    def CodePage(self):
        """Code preference page"""
        code_panel = wx.Panel(self, wx.ID_ANY)

        # Feature Settings
        feat_lbl = wx.StaticText(code_panel, wx.ID_ANY, _("Features") + u":")
        br_cb = wx.CheckBox(code_panel, ed_glob.ID_BRACKETHL, _("Bracket Highlighting"))
        br_cb.SetValue(ed_glob.PROFILE['BRACKETHL'])
        cc_cb = wx.CheckBox(code_panel, ed_glob.ID_KWHELPER, _("Keyword Helper"))
        cc_cb.SetValue(ed_glob.PROFILE['KWHELPER'])
        ind_cb = wx.CheckBox(code_panel, ed_glob.ID_INDENT_GUIDES, _("Indentation Guides"))
        ind_cb.SetValue(ed_glob.PROFILE['GUIDES'])
        feat_sizer = wx.BoxSizer(wx.VERTICAL)
        feat_sizer.AddMany([br_cb, cc_cb, ind_cb]) 

        # Syntax Settings
        syn_lbl = wx.StaticText(code_panel, wx.ID_ANY, _("Syntax") + u":")
        syn_cb = wx.CheckBox(code_panel, ed_glob.ID_SYNTAX, _("Syntax Highlighting"))
        syn_cb.SetValue(ed_glob.PROFILE['SYNTAX'])

        syn_sizer = wx.BoxSizer(wx.VERTICAL)
        syn_sizer.AddMany([syn_cb]) 

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(feat_lbl, 0, wx.ALL, 10)
        border.Add(feat_sizer, 0, wx.LEFT, 20)
        border.Add(syn_lbl, 0, wx.ALL, 10)
        border.Add(syn_sizer, 0, wx.LEFT, 20)
        code_panel.SetSizer(border)

        self.AddPage(code_panel, _("Code"))

    def TextPage(self):
        """Adds a Text Preferences Page"""
        text_panel = wx.Panel(self, wx.ID_ANY)

        # Format Section Label
        format_lbl = wx.StaticText(text_panel, wx.ID_ANY, _("Format") + u":")
        tw_lbl = wx.StaticText(text_panel, wx.ID_ANY, _("Tab Width") + u":  ")
        tw_cb = ExChoice(text_panel, ed_glob.ID_PREF_TABW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=ed_glob.PROFILE['TABWIDTH'])
        tabw_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tabw_sizer.Add(tw_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        tabw_sizer.Add(tw_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        ww_cb = wx.CheckBox(text_panel, ed_glob.ID_WORD_WRAP, _("Word Wrap"))
        ww_cb.SetValue(ed_glob.PROFILE['WRAP'])
        format_sizer = wx.BoxSizer(wx.VERTICAL)
        format_sizer.AddMany([tabw_sizer, ww_cb]) 

        # Misc Section
        misc_lbl = wx.StaticText(text_panel, wx.ID_ANY, _("Misc") + u":")
        aa_cb = wx.CheckBox(text_panel, ed_glob.ID_PREF_AALIAS, _("AntiAliasing"))
        aa_cb.SetValue(ed_glob.PROFILE['AALIASING'])
        sws_cb = wx.CheckBox(text_panel, ed_glob.ID_SHOW_WS, _("Show Whitespace"))
        sws_cb.SetValue(ed_glob.PROFILE['SHOW_WS'])
        ut_cb = wx.CheckBox(text_panel, ed_glob.ID_PREF_TABS, _("Use Tabs Instead of Whitespaces"))
        ut_cb.SetValue(ed_glob.PROFILE['USETABS'])
        misc_sizer = wx.BoxSizer(wx.VERTICAL)
        misc_sizer.AddMany([aa_cb, sws_cb, ut_cb]) 

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(format_lbl, 0, wx.ALL, 10)
        border.Add(format_sizer, 0, wx.LEFT, 20)
        border.Add(misc_lbl, 0, wx.ALL, 10)
        border.Add(misc_sizer, 0, wx.LEFT, 20)
        text_panel.SetSizer(border)
        self.AddPage(text_panel, _("Text"))

    def MiscPage(self):
        """Theme preference page"""
        misc_panel = wx.Panel(self, wx.ID_ANY)

        # Misc Settings Section
        set_lbl = wx.StaticText(misc_panel, wx.ID_ANY, _("Settings") + u":  ")
        fh_lbl = wx.StaticText(misc_panel, wx.ID_ANY, _("File History Depth") + u":  ")
        fh_cb = ExChoice(misc_panel, ed_glob.ID_PREF_FHIST,
                          choices=['1','2','3','4','5','6','7','8','9'],
                          default=ed_glob.PROFILE['FHIST_LVL'])
        fh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fh_sizer.Add(fh_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        fh_sizer.Add(fh_cb, 1, wx.ALIGN_CENTER_VERTICAL)

        # Various Appearance Settings
        app_lbl = wx.StaticText(misc_panel, wx.ID_ANY, _("Appearance") + u":")
        app_sizer = wx.BoxSizer(wx.VERTICAL)
        tb_icont = wx.StaticText(misc_panel, wx.ID_ANY, _("Icon Theme") + u": ")
        tb_icon = ExChoice(misc_panel, id=ed_glob.ID_PREF_ICON,
                            choices=util.GetResources(u"pixmaps" + util.GetPathChar() + u"toolbar"), 
                            default=ed_glob.PROFILE['ICONS'].title())
        tbi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tbi_sizer.Add(tb_icont, 1, wx.ALIGN_CENTER_VERTICAL)
        tbi_sizer.Add(tb_icon, 1, wx.ALIGN_CENTER_VERTICAL)
        app_sizer.Add(tbi_sizer, 1, wx.ALIGN_CENTER_VERTICAL)

        if wx.Platform == '__WXMAC__':
            m_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_METAL, _("Use Metal Style (OS X Only)"))
            if ed_glob.PROFILE.has_key('METAL'):
                m_cb.SetValue(ed_glob.PROFILE['METAL'])
            else:
                m_cb.SetValue(False)
            app_sizer.Add(m_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        ws_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_WSIZE, _("Remember Window Size on Exit"))
        ws_cb.SetValue(ed_glob.PROFILE['SET_WSIZE'])
        app_sizer.Add(ws_cb, 1, wx.ALIGN_CENTER_VERTICAL)
        wp_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_WPOS, _("Remember Window Position on Exit"))
        wp_cb.SetValue(ed_glob.PROFILE['SET_WPOS'])
        app_sizer.Add(wp_cb, 1, wx.ALIGN_CENTER_VERTICAL)

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(set_lbl, 0, wx.ALL, 10)
        border.Add(fh_sizer, 0, wx.LEFT, 20)
        border.Add(app_lbl, 0, wx.ALL, 10)
        border.Add(app_sizer, 0, wx.LEFT, 20)
        misc_panel.SetSizer(border)
        self.AddPage(misc_panel, _("Misc"))

    def UpdatePage(self):
        """Update Status page"""
        upd_panel = wx.Panel(self, wx.ID_ANY)

        info = wx.StaticText(upd_panel, wx.ID_ANY, _("Update Status") + u":")
        ver_info = wx.StaticText(upd_panel, wx.ID_ANY, _("\nYou are running version: %s") % ed_glob.version)

        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(info, 0, wx.LEFT, 10)
        border.Add(ver_info, 1, wx.LEFT, 10)

        upd_panel.SetSizer(border)

        self.AddPage(upd_panel, _("Update"))

    def OnPageChanged(self, evt):
        """Actions to do after a page change"""
        curr = evt.GetSelection()
        txt = self.GetPageText(curr)
        dev_tool.DEBUGP("[prefdlg_evt] Page Changed to " + txt)
        evt.Skip()

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
            val = str(ed_glob.PROFILE[key])
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
    def __init__(self, parent, id, pos=(-1,-1), size=(-1,-1), choices=[], default=None):
        """Constructs a Choice Control"""
        wx.Choice.__init__(self, parent=parent, id=id, pos=pos, size=size, choices=choices,
                            style=wx.CB_SORT)
        if default != None:
            self.SetStringSelection(default)

    def GetValue(self):
        """Gets the Selected Value"""
        val = self.GetStringSelection()
        if val.isalpha():
            val.lower()
        return val

#----------------------------------------------------------------------------#

