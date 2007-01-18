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

__revision__ = "$Id: Exp $"

#----------------------------------------------------------------------------#
# Dependancies
import wx
import wx.lib.mixins.listctrl as listmix
import sys
import ed_glob
from ed_glob import LANG, L_LBL, L_SB
import util
import dev_tool
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# ID's
ID_VALS = [ ed_glob.ID_PREF_AALIAS, ed_glob.ID_PREF_LANG, ed_glob.ID_BRACKETHL, 
            ed_glob.ID_KWHELPER, ed_glob.ID_SYNTAX, ed_glob.ID_INDENT_GUIDES,
            ed_glob.ID_WORD_WRAP, ed_glob.ID_PREF_TABS, ed_glob.ID_PREF_TABW,
            ed_glob.ID_SHOW_WS, ed_glob.ID_PREF_METAL, ed_glob.ID_PREF_FHIST,
            ed_glob.ID_PREF_WSIZE, ed_glob.ID_PREF_WPOS ]

# Validator Flags
ALPHA_ONLY = 1
DIGIT_ONLY = 2
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

        pre.Create(parent, -1, 'Preferences')
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
        cancel_b = wx.Button(self, wx.ID_CANCEL, "Cancel")
        cancel_b.SetDefault()
        apply_b = wx.Button(self, wx.ID_APPLY, "Apply")
        apply_b.SetDefault()
        ok_b = wx.Button(self, wx.ID_OK, "Ok")
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
        #TODO beef me up, value type checking isbool, ect...
        for obj in self.act_objs:
            value = obj.GetValue()
            # TODO This is wrong but works for now (does not do thorough checking
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

        info = wx.StaticText(gen_panel, wx.ID_ANY, "\n".join(info_txt), (8, 10))
        wx.StaticText(gen_panel, wx.ID_ANY, u"Language:", (15, 250), (75, 18))
        ExChoice(gen_panel, id=ed_glob.ID_PREF_LANG, pos=(90,250), size=(300,-1),
                           choices=util.GetLanguages(), default=ed_glob.PROFILE['LANG'].title())
    #    lang_sizer = wx.BoxSizer(wx.HORIZONTAL)
    #    lang_sizer.Add(lang_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
    #    lang_sizer.Add(lang_c, 0, wx.ALIGN_CENTER_VERTICAL)

        sizer = wx.BoxSizer(wx.VERTICAL)
      #  sizer.Add(info, 0, wx.CENTER)
      #  sizer.Add(lang_sizer, 1, wx.BOTTOM)
      #  sizer.Add(lang_lbl, 10, wx.LEFT | wx.BOTTOM)
       # sizer.Add(lang_c, 10, wx.BOTTOM | wx.LEFT)

        gen_panel.SetSizer(sizer)

        self.AddPage(gen_panel, u"General")

    def ProfilePage(self):
        """Creates the profile editor page"""
        prof_panel = wx.Panel(self, wx.ID_ANY)

        # Bind size evt to this panel
        prof_panel.Bind(wx.EVT_SIZE, self.OnSize)
        
        # Add Profile Editor to Panel
        self.list = ProfileListCtrl(prof_panel)

        self.AddPage(prof_panel, "Profile Viewer")

    def CodePage(self):
        """Code preference page"""
        code_panel = wx.Panel(self, wx.ID_ANY)

        # Feature Settings
        feat_lbl = wx.StaticText(code_panel, wx.ID_ANY, "Features:")
        br_cb = wx.CheckBox(code_panel, ed_glob.ID_BRACKETHL, LANG['BraceHL'][L_LBL])
        br_cb.SetValue(ed_glob.PROFILE['BRACKETHL'])
        cc_cb = wx.CheckBox(code_panel, ed_glob.ID_KWHELPER, LANG['KWHelper'][L_LBL])
        cc_cb.SetValue(ed_glob.PROFILE['KWHELPER'])
        ind_cb = wx.CheckBox(code_panel, ed_glob.ID_INDENT_GUIDES, LANG['IndentG'][L_SB])
        ind_cb.SetValue(ed_glob.PROFILE['GUIDES'])
        feat_sizer = wx.BoxSizer(wx.VERTICAL)
        feat_sizer.AddMany([br_cb, cc_cb, ind_cb]) 

        # Syntax Settings
        syn_lbl = wx.StaticText(code_panel, wx.ID_ANY, "Syntax:")
        syn_cb = wx.CheckBox(code_panel, ed_glob.ID_SYNTAX, LANG['SyntaxHL'][L_LBL])
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

        self.AddPage(code_panel, "Code")

    def TextPage(self):
        """Adds a Text Preferences Page"""
        text_panel = wx.Panel(self, wx.ID_ANY)

        # Format Section Label
        format_lbl = wx.StaticText(text_panel, wx.ID_ANY, util.DeAccel(LANG['Format']+":"))
        tw_lbl = wx.StaticText(text_panel, wx.ID_ANY, u"Tab Width:  ")
        tw_cb = ExChoice(text_panel, ed_glob.ID_PREF_TABW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=ed_glob.PROFILE['TABWIDTH'])
        tabw_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tabw_sizer.Add(tw_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        tabw_sizer.Add(tw_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        ww_cb = wx.CheckBox(text_panel, ed_glob.ID_WORD_WRAP, LANG['WordWrap'][L_LBL])
        ww_cb.SetValue(ed_glob.PROFILE['WRAP'])
        format_sizer = wx.BoxSizer(wx.VERTICAL)
        format_sizer.AddMany([tabw_sizer, ww_cb]) 

        # Misc Section
        misc_lbl = wx.StaticText(text_panel, wx.ID_ANY, u"Misc:")
        aa_cb = wx.CheckBox(text_panel, ed_glob.ID_PREF_AALIAS, u"AntiAliasing")
        aa_cb.SetValue(ed_glob.PROFILE['AALIASING'])
        sws_cb = wx.CheckBox(text_panel, ed_glob.ID_SHOW_WS, LANG['WhiteS'][L_LBL])
        sws_cb.SetValue(ed_glob.PROFILE['SHOW_WS'])
        ut_cb = wx.CheckBox(text_panel, ed_glob.ID_PREF_TABS, u"Use Tabs Instead of Whitespaces")
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
        self.AddPage(text_panel, u"Text")

    def MiscPage(self):
        """Theme preference page"""
        misc_panel = wx.Panel(self, wx.ID_ANY)

        # Misc Settings Section
        set_lbl = wx.StaticText(misc_panel, wx.ID_ANY, u"Settings:  ")
        fh_lbl = wx.StaticText(misc_panel, wx.ID_ANY, u"File History Depth:  ")
        fh_cb = ExChoice(misc_panel, ed_glob.ID_PREF_FHIST,
                          choices=['1','2','3','4','5','6','7','8','9'],
                          default=ed_glob.PROFILE['FHIST_LVL'])
        fh_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fh_sizer.Add(fh_lbl, 0, wx.ALIGN_CENTER_VERTICAL)
        fh_sizer.Add(fh_cb, 1, wx.ALIGN_CENTER_VERTICAL)

        # Various Appearance Settings
        app_lbl = wx.StaticText(misc_panel, wx.ID_ANY, u"Appearance:  ")
        app_sizer = wx.BoxSizer(wx.VERTICAL)
        if wx.Platform == '__WXMAC__':
            m_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_METAL, u"Use Metal Style (OS X Only)")
            if ed_glob.PROFILE.has_key('METAL'):
                m_cb.SetValue(ed_glob.PROFILE['METAL'])
            else:
                m_cb.SetValue(False)
            app_sizer.Add(m_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        ws_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_WSIZE, u"Remember Window Size on Exit")
        ws_cb.SetValue(ed_glob.PROFILE['SET_WSIZE'])
        app_sizer.Add(ws_cb, 1, wx.ALIGN_CENTER_VERTICAL)
        wp_cb = wx.CheckBox(misc_panel, ed_glob.ID_PREF_WPOS, u"Remember Window Position on Exit")
        wp_cb.SetValue(ed_glob.PROFILE['SET_WPOS'])
        app_sizer.Add(wp_cb, 1, wx.ALIGN_CENTER_VERTICAL)

        # Build Page
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(set_lbl, 0, wx.ALL, 10)
        border.Add(fh_sizer, 0, wx.LEFT, 20)
        border.Add(app_lbl, 0, wx.ALL, 10)
        border.Add(app_sizer, 0, wx.LEFT, 20)
        misc_panel.SetSizer(border)
        self.AddPage(misc_panel, "Misc")

    def UpdatePage(self):
        """Update Status page"""
        upd_panel = wx.Panel(self, wx.ID_ANY)

        info = wx.StaticText(upd_panel, wx.ID_ANY, "Update Status:")
        ver_info = wx.StaticText(upd_panel, wx.ID_ANY, "\nYou are running version: " + ed_glob.version)

        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(info, 0, wx.LEFT, 10)
        border.Add(ver_info, 1, wx.LEFT, 10)

        upd_panel.SetSizer(border)

        self.AddPage(upd_panel, "Update")

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
        self.InsertColumn(0, "Item")
        self.InsertColumn(1, "Value")

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

