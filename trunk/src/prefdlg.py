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

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

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
import syntax.syntax as syntax

# On mac use the native control as it looks much nicer
# if wx.Platform == "__WXMAC__":
#      wx.SystemOptions.SetOptionInt("mac.listctrl.always_use_generic", 0)

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
            ed_glob.ID_SYNTAX, ed_glob.ID_INDENT_GUIDES,
            ed_glob.ID_WORD_WRAP, ed_glob.ID_PREF_TABS, ed_glob.ID_PREF_TABW,
            ed_glob.ID_SHOW_WS, ed_glob.ID_PREF_METAL, ed_glob.ID_PREF_FHIST,
            ed_glob.ID_PREF_WSIZE, ed_glob.ID_PREF_WPOS, ed_glob.ID_PREF_ICON,
            ed_glob.ID_PREF_MODE, ed_glob.ID_SHOW_EOL, ed_glob.ID_PREF_SYNTHEME,
            ed_glob.ID_PREF_ICONSZ, ed_glob.ID_EOL_MODE, ed_glob.ID_PRINT_MODE,
            ed_glob.ID_FOLDING, ed_glob.ID_AUTOCOMP, ed_glob.ID_SHOW_LN,
            ed_glob.ID_PREF_SPOS, ed_glob.ID_AUTOINDENT, ed_glob.ID_APP_SPLASH,
            ed_glob.ID_PREF_CHKMOD, ed_glob.ID_PREF_EDGE, ed_glob.ID_SHOW_EDGE,
            ed_glob.ID_PERSPECTIVES]

#----------------------------------------------------------------------------#

class PrefDlg(wx.Dialog):
    """Preference Dialog Class"""
    def __init__(self, parent):
        """Initialize the Preference Dialog"""
        pre = wx.PreDialog()

        if wx.Platform == '__WXMAC__' and ed_glob.PROFILE.has_key('METAL'):
            if ed_glob.PROFILE['METAL']:
                pre.SetExtraStyle(wx.DIALOG_EX_METAL)

        pre.Create(parent, -1, _('Preferences'))
        self.PostCreate(pre)

        # Attributes
        self.LOG = wx.GetApp().GetLog()
        self.act_ids = []
        self.act_objs = []

        self.LOG("[prefdlg_info] Preference Dialog Initializing...")
        # Create Notebook
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.ntb = PrefPages(self, wx.ID_ANY)
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
    def __init__(self, parent, id_num):
        """Initializes the notebook"""
        wx.Notebook.__init__(self, parent, id_num, size = (PREF_WIDTH, PREF_HEIGHT),
                             style = wx.NB_TOP
                            )
        # Attributes
        self.LOG = wx.GetApp().GetLog()

        # Events
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(ed_event.EVT_UPDATE_TEXT, self.OnUpdateText)

        # Initialize Preference Pages
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
        elif evt_id == ed_glob.ID_PERSPECTIVES:
            main_win = self.GetGrandParent()
            ed_glob.PROFILE['DEFAULT_VIEW'] = evt_obj.GetValue()
            main_win.SetPerspective(ed_glob.PROFILE['DEFAULT_VIEW'])
        else:
            evt.Skip()

    def GeneralPage(self):
        """Creates the general preferences page"""
        gen_panel = wx.Panel(self, wx.ID_ANY)

        info_txt = ["Changes made in this dialog are saved in your current profile.",
                    "Some Items such as Language require the program to be restarted ",
                    "before taking affect."]

        info = wx.StaticText(gen_panel, wx.ID_ANY, "\n".join(info_txt))

    def ProfilePage(self):
        """Creates the profile editor page"""
        prof_panel = wx.Panel(self, wx.ID_ANY)
        border = wx.BoxSizer(wx.VERTICAL)
        # Add Profile Viewer to Panel
        plist = ProfileListCtrl(prof_panel)
        border.Add(plist, 1, wx.EXPAND)
        prof_panel.SetSizer(border)
        self.AddPage(prof_panel, _("Profile Viewer"))

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
                                          size=wx.Size(320, 18))
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
        stat_sz.Add(wx.Size(15, 15))
        stat_sz.Add(cur_sz, 1, wx.ALIGN_LEFT)
        stat_sz.Add(wx.Size(50, 50))
        stat_sz.Add(upd_bsz, 1, wx.ALIGN_RIGHT)

        # Progress Bar
        p_barsz = wx.BoxSizer(wx.HORIZONTAL)
        p_barsz.Add(wx.Size(15, 15))
        p_barsz.Add(e_update, 0, wx.ALIGN_CENTER_VERTICAL)

        # Progress bar control buttons
        btn_sz = wx.BoxSizer(wx.HORIZONTAL)
        btn_sz.Add(wx.Size(15, 15))
        check_b = wx.Button(upd_panel, ID_CHECK_UPDATE, _("Check"))
        btn_sz.Add(check_b, 0, wx.ALIGN_LEFT)
        btn_sz.Add(wx.Size(30, 30))
        dl_b    = wx.Button(upd_panel, ID_DOWNLOAD, _("Download"))
        dl_b.Disable()
        btn_sz.Add(dl_b, 0, wx.ALIGN_RIGHT)
        btn_sz.Add(wx.Size(15, 15))

        v_stack.Add(wx.Size(15, 15))
        v_stack.Add(stat_sz, 0, wx.ALIGN_CENTER)
        v_stack.Add(wx.Size(20, 20))
        v_stack.Add(p_barsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
        v_stack.Add(wx.Size(20, 20))
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
            dl_dlg = updater.DownloadDialog(None, ed_glob.ID_DOWNLOAD_DLG,
                                            _("Downloading Update"), 
                                            size = wx.Size(350, 200))
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

#---- End Function Definitions ----#
#----------------------------------------------------------------------------#

class NewPreferencesDialog(wx.Frame):
    """Preference dialog for configuring the editor"""
    def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL
                     | wx.CLIP_CHILDREN
                     | wx.FULL_REPAINT_ON_RESIZE):
        """Initialises the dialog"""
        wx.Frame.__init__(self, parent, id, title, pos=pos, size=size, style=style)

        # Extra Styles
        self.SetExtraStyle(wx.FRAME_EX_CONTEXTHELP)

        # Attributes
        self._tbook = PrefTools(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Bind Events

        # Layout
        sizer.Add(self._tbook, 1, wx.EXPAND)
        sizer.Add(hsizer, 0, wx.ALIGN_BOTTOM)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

class PrefTools(wx.Toolbook):
    """Main sections of the configuration pages
    @note: implements the top level book control for the prefdlg

    """
    GENERAL_PG = 0
    def __init__(self, parent, tbid, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.BK_DEFAULT | wx.TB_TEXT | 
                                            wx.TB_TOP):
        """Initializes the main book control of the preferences dialog"""
        wx.Toolbook.__init__(self, parent, tbid, pos=pos, \
                             size=size, style=style)

        tb = self.GetToolBar()
        tb.SetWindowStyle(tb.GetWindowStyle() | wx.TB_NODIVIDER)
        self._imglst = wx.ImageList(32, 32)
        self._imgind = dict()
        self._imgind[self.GENERAL_PG] = self._imglst.Add(wx.ArtProvider.GetBitmap( \
                                                   str(ed_glob.ID_PLUGIN_CFG), \
                                                       wx.ART_OTHER))
        self.SetImageList(self._imglst)
        self.AddPage(GeneralPanel(self), _("General"), 
                     imageId=self._imgind[self.GENERAL_PG])
        self.AddPage(AppearancePanel(self), _("Appearance"), 
                     imageId=self._imgind[self.GENERAL_PG])
        self.AddPage(DocumentPanel(self), _("Document"), 
                     imageId=self._imgind[self.GENERAL_PG])

        # Event Handlers
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPageChanged(self, evt):
        """Resizes the dialog based on the pages size
        @todo: animate the resizing so its smoother

        """
        page = evt.GetSelection()
        page = self.GetPage(page)
        page.SetInitialSize()
        parent = self.GetParent()
        psz = page.GetSize()
        tbh = self.GetToolBar().GetSize().GetHeight()
        parent.SetClientSize((psz.GetWidth() + 10, psz.GetHeight() + tbh + 15))
        parent.SendSizeEvent()
        parent.Layout()
        evt.Skip()

    def OnPaint(self, evt):
        """Paint the toolbar's background
        @todo: it would be nice to use a unified toolbar style on osx

        """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
#         col2 = util.AdjustColour(col1, 20)
        col1 = util.AdjustColour(col1, -20)
        rect = self.GetToolBar().GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width, rect.height + 3)

        gc.SetPen(wx.Pen(col1, 1))
#         grad = gc.CreateLinearGradientBrush(0, 0, 0, rect.height, col1, col2)
        grad = gc.CreateBrush(wx.Brush(col1))
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

class PrefPanelBase(wx.Panel):
    """Base of all preference panels
    @summary: Provides a panel with a painted background

    """
    def __init__(self, parent):
        """Default Constructor
        @param parent: The panels parent

        """
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER)

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        """Paints the panels background
        @param evt: Event that called this handler

        """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        col1 = util.AdjustColour(col1, 30)
        brush = gc.CreateBrush(wx.Brush(col1))
        rect = self.GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width, rect.height)

        gc.SetPen(wx.Pen(util.AdjustColour(col1, -60), 1))
        gc.SetBrush(brush)
        gc.DrawPath(path)

        evt.Skip()

class GeneralPanel(PrefPanelBase):
    """Creates a panel with controls for Editra's general settings"""
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        PrefPanelBase.__init__(self, parent)
        
        # Attributes
        self._DoLayout()

    def _DoLayout(self):
        """Add the controls and do the layout"""
        # Startup Section
        mode_ch = ExChoice(self, ed_glob.ID_PREF_MODE,
                           choices=['CODE', 'DEBUG', 'GUI_DEBUG'],
                           default=ed_glob.PROFILE['MODE'])
        pmode_ch = ExChoice(self, ed_glob.ID_PRINT_MODE,
                            choices=['Black/White', 'Colour/White', 'Colour/Default',
                                     'Inverse', 'Normal'],
                            default=ed_glob.PROFILE['PRINT_MODE'])
        splash_cb = wx.CheckBox(self, ed_glob.ID_APP_SPLASH, _("Show Splash Screen"))
        splash_cb.SetValue(ed_glob.PROFILE['APPSPLASH'])

        # File settings
        fh_ch = ExChoice(self, ed_glob.ID_PREF_FHIST,
                         choices=['1','2','3','4','5','6','7','8','9'],
                         default=str(ed_glob.PROFILE['FHIST_LVL']))
        pos_cb = wx.CheckBox(self, ed_glob.ID_PREF_SPOS, 
                             _("Remember File Position"))
        pos_cb.SetValue(ed_glob.PROFILE['SAVE_POS'])
        chkmod_cb = wx.CheckBox(self, ed_glob.ID_PREF_CHKMOD, 
                                _("Check if on disk file has been "
                                  "modified by others"))
        chkmod_cb.SetValue(ed_glob.PROFILE['CHECKMOD'])

        # Locale
        lang_c = ed_i18n.LangListCombo(self, ed_glob.ID_PREF_LANG, 
                                       ed_glob.PROFILE['LANG'])

        # Layout items
        sizer = wx.GridBagSizer(5, 5)
        sizer.AddMany([((5, 5), (0, 0)),
                       (wx.StaticText(self, label=_("Startup Settings") + u": "), (1, 1)),
                       (wx.StaticText(self, label=_("Editor Mode") + u": "), (1, 2)),
                       (mode_ch, (1, 3)),
                       (wx.StaticText(self, label=_("Printer Mode") + u": "), (2, 2)),
                       (pmode_ch, (2, 3), wx.GBSpan(1, 2)),
                       (splash_cb, (3, 2), wx.GBSpan(1, 2))])
        sizer.AddMany([(wx.StaticText(self, label=_("File Settings") + u": "), (5, 1)),
                       (wx.StaticText(self, label=_("File History Length") + u": "), (5, 2)),
                       (fh_ch, (5, 3)), (pos_cb, (6, 2), (1, 2)),
                       (chkmod_cb, (7, 2), (1, 2))])
        sizer.AddMany([(wx.StaticText(self, label=_("Locale Settings") + u": "), (9, 1)),
                       (wx.StaticText(self, label=_("Language") + u": "), (9, 2)),
                       (lang_c, (9, 3), wx.GBSpan(1, 3), wx.ALIGN_CENTER_VERTICAL)])
        self.SetSizer(sizer)

class DocumentPanel(PrefPanelBase):
    """Creates a panel with controls for Editra's editing settings"""
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        PrefPanelBase.__init__(self, parent)
        
        # Attributes
        self._nb = wx.Notebook(self)
        self._DoLayout()
        self.SetAutoLayout(True)

    def _DoLayout(self):
        """Do the layout of the panel"""
        sizer = wx.GridBagSizer()
        self._nb.AddPage(DocGenPanel(self._nb), _("General"))
        self._nb.AddPage(DocCodePanel(self._nb), _("Code"))
        self._nb.AddPage(DocSyntaxPanel(self._nb), _("Syntax Highlighting"))
        sizer.Add(self._nb, (1, 1))
        self.SetSizer(sizer)

class DocGenPanel(wx.Panel):
    """Panel used for general document settings in the DocumentPanel's
    notebook.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)
        
        # Layout
        self._DoLayout()

    def _DoLayout(self):
        """Layout the controls"""
        # Format Section
        tw_ch = ExChoice(self, ed_glob.ID_PREF_TABW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=str(ed_glob.PROFILE['TABWIDTH']))
        ut_cb = wx.CheckBox(self, ed_glob.ID_PREF_TABS, 
                            _("Use Tabs Instead of Whitespaces"))
        ut_cb.SetValue(ed_glob.PROFILE['USETABS'])
        eol_ch = ExChoice(self, ed_glob.ID_EOL_MODE,
                          choices = [_("Macintosh (\\r)"), _("Unix (\\n)"), 
                                   _("Windows (\\r\\n)")],
                          default = ed_glob.PROFILE['EOL'])
        ww_cb = wx.CheckBox(self, ed_glob.ID_WORD_WRAP, _("Word Wrap"))
        ww_cb.SetValue(ed_glob.PROFILE['WRAP'])

        # View Options
        aa_cb = wx.CheckBox(self, ed_glob.ID_PREF_AALIAS, _("AntiAliasing"))
        aa_cb.SetValue(ed_glob.PROFILE['AALIASING'])
        seol_cb = wx.CheckBox(self, ed_glob.ID_SHOW_EOL, _("Show EOL Markers"))
        seol_cb.SetValue(ed_glob.PROFILE['SHOW_EOL'])
        sln_cb = wx.CheckBox(self, ed_glob.ID_SHOW_LN, _("Show Line Numbers"))
        sln_cb.SetValue(ed_glob.PROFILE['SHOW_LN'])
        sws_cb = wx.CheckBox(self, ed_glob.ID_SHOW_WS, _("Show Whitespace"))
        sws_cb.SetValue(ed_glob.PROFILE['SHOW_WS'])

        # Layout
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add((5, 5), (1, 0))
        sizer.Add(wx.StaticText(self, label=_("Format") + u": "), (1, 1))
        sizer.AddMany([(ut_cb, (1, 2), wx.GBSpan(1, 2)),
                       (wx.StaticText(self, label=_("Tab Width") + u": "), (2, 2)),
                       (tw_ch, (2, 3), wx.GBSpan(1, 3)),
                       (wx.StaticText(self, label=_("Default EOL Mode") + u": "), (3, 2)),
                       (eol_ch, (3, 3), wx.GBSpan(1, 2)),
                       (ww_cb, (4, 2)), ((5, 5), (6, 0)),
                       (wx.StaticText(self, label=_("View Options") + u": "), (6, 1)),
                       (aa_cb, (6, 2)), (seol_cb, (7, 2)), (sln_cb, (8, 2)),
                       (sws_cb, (9, 2))
                       ])
        self.SetSizer(sizer)

class DocCodePanel(wx.Panel):
    """Panel used for programming settings"""
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)
        
        # Layout
        self._DoLayout()

    def _DoLayout(self):
        """Layout the page"""
        # Visual Helpers Section
        br_cb = wx.CheckBox(self, ed_glob.ID_BRACKETHL, 
                            _("Bracket Highlighting"))
        br_cb.SetValue(ed_glob.PROFILE['BRACKETHL'])
        fold_cb = wx.CheckBox(self, ed_glob.ID_FOLDING, _("Code Folding"))
        fold_cb.SetValue(ed_glob.PROFILE['CODE_FOLD'])
        edge_cb = wx.CheckBox(self, ed_glob.ID_SHOW_EDGE, _("Edge Guide"))
        edge_cb.SetValue(ed_glob.PROFILE['SHOW_EDGE'])
        
        edge_ch = ExChoice(self, ed_glob.ID_PREF_EDGE,
                           choices=range(40, 101),
                           default=str(ed_glob.PROFILE['EDGE']))
        ind_cb = wx.CheckBox(self, ed_glob.ID_INDENT_GUIDES, 
                             _("Indentation Guides"))
        ind_cb.SetValue(ed_glob.PROFILE['GUIDES'])

        # Input Helpers
        comp_cb = wx.CheckBox(self, ed_glob.ID_AUTOCOMP, _("Auto-Completion"))
        comp_cb.SetValue(ed_glob.PROFILE['AUTO_COMP'])
        ai_cb = wx.CheckBox(self, ed_glob.ID_AUTOINDENT, _("Auto-Indent"))
        ai_cb.SetValue(ed_glob.PROFILE['AUTO_INDENT'])

        # Layout the controls
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add((5, 5), (1, 0))
        sizer.Add(wx.StaticText(self, label=_("Visual Helpers") + u": "), (1, 1))
        sizer.AddMany([(br_cb, (1, 2)), (fold_cb, (2, 2)),
                       (edge_cb, (3, 2)),
                       (wx.StaticText(self, label=_("Column") + u": "), (3, 3)),
                       (edge_ch, (3, 4)), (ind_cb, (4, 2))])
        sizer.Add(wx.StaticText(self, label=_("Input Helpers") + u": "), (6, 1))
        sizer.AddMany([(comp_cb, (6, 2)), (ai_cb, (7, 2))])
        self.SetSizer(sizer)

class DocSyntaxPanel(wx.Panel):
    """Document syntax config panel"""
    def __init__(self, parent):
        """Inialize the config panel
        @param parent: parent window of this panel

        """
        wx.Panel.__init__(self, parent)
        
        # Layout page
        self._DoLayout()

    def _DoLayout(self):
        """Layout all the controls"""
        # Syntax Settings
        syn_cb = wx.CheckBox(self, ed_glob.ID_SYNTAX, _("Syntax Highlighting"))
        syn_cb.SetValue(ed_glob.PROFILE['SYNTAX'])
        syntheme = ExChoice(self, ed_glob.ID_PREF_SYNTHEME,
                            choices=util.GetResourceFiles(u'styles', get_all=True),
                            default=str(ed_glob.PROFILE['SYNTHEME']))
        elist = ExtListCtrl(self)
        elist.LoadList()

        # Layout the controls
        sizer = wx.GridBagSizer()
        sizer.Add((5, 5), (0, 0))
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([(syn_cb, 0, wx.ALIGN_LEFT), ((5, 5), 1, wx.EXPAND),
                        (wx.StaticText(self, label=_("Color Scheme") + u": "), 0, wx.ALIGN_LEFT),
                        (syntheme, 0, wx.ALIGN_LEFT)])
        sizer.AddMany([(hsizer, (1, 1), (1, 4), wx.EXPAND), ((5, 5), (1, 5), (1, 3), wx.EXPAND),
                       (wx.StaticLine(self), (2, 1), (1, 4), wx.EXPAND),
                       (wx.StaticText(self, label=_("Filetype Associations") + u": "), (4, 1))])
        sizer.Add(elist, (5, 1), (12, 4), wx.EXPAND)
        sizer.Add((5, 5), (17, 1))
        self.SetSizer(sizer)

class AppearancePanel(PrefPanelBase):
    """Creates a panel with controls for Editra's appearance settings"""
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        PrefPanelBase.__init__(self, parent)
        
        # Layout
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_SLIDER, self.OnSetTransparent, \
                  id=ed_glob.ID_TRANSPARENCY)

    def _DoLayout(self):
        """Add and layout the widgets"""
        # Icons Section
        tb_icont = wx.StaticText(self, wx.ID_ANY, _("Icon Theme") + u": ")
        tb_icon = ExChoice(self, ed_glob.ID_PREF_ICON,
                            choices=util.GetResources(u"pixmaps" + \
                                                      util.GetPathChar() + \
                                                      u"theme"), 
                            default=ed_glob.PROFILE['ICONS'].title())
        tb_isz_lbl = wx.StaticText(self, wx.ID_ANY, \
                                   _("Toolbar Icon Size") + u": ")
        tb_isz_ch = ExChoice(self, ed_glob.ID_PREF_ICONSZ,
                              choices=['16', '24', '32'],
                              default=str(ed_glob.PROFILE['ICON_SZ'][0]))

        # Layout Section
        perspect_lbl = wx.StaticText(self, wx.ID_ANY, \
                                     _("Default Perspective") + u": ")
        perspect_ch = ExChoice(self, ed_glob.ID_PERSPECTIVES,
                               choices=wx.GetApp().GetMainWindow().GetPerspectiveList(),
                               default=ed_glob.PROFILE['DEFAULT_VIEW'])
        ws_cb = wx.CheckBox(self, ed_glob.ID_PREF_WSIZE, \
                            _("Remember Window Size on Exit"))
        ws_cb.SetValue(ed_glob.PROFILE['SET_WSIZE'])
        wp_cb = wx.CheckBox(self, ed_glob.ID_PREF_WPOS, \
                            _("Remember Window Position on Exit"))
        wp_cb.SetValue(ed_glob.PROFILE['SET_WPOS'])

        # Misc
        trans_lbl = wx.StaticText(self, wx.ID_ANY, _("Transparency") + u": ")
        trans = wx.Slider(self, ed_glob.ID_TRANSPARENCY, 
                          ed_glob.PROFILE['ALPHA'], 100, 255, 
                          style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        # Activate Metal Style Windows for OSX
        if wx.Platform == '__WXMAC__':
            m_cb = wx.CheckBox(self, ed_glob.ID_PREF_METAL, \
                               _("Use Metal Style (OS X Only)"))
            m_cb.SetValue(ed_glob.PROFILE.get('METAL', False))
        else:
            m_cb = (0, 0)

        # Layout
        sizer = wx.GridBagSizer(5, 4)
        sizer.Add((5, 5), (0, 1))
        sizer.Add(wx.StaticText(self, label=_("Icons") + u": "), (1, 1))
        sizer.Add(tb_icont, (1, 2))
        sizer.Add(tb_icon, (1, 3))
        sizer.Add(tb_isz_lbl, (2, 2))
        sizer.Add(tb_isz_ch, (2, 3))
        sizer.Add((5, 5), (4, 0))
        sizer.Add(wx.StaticText(self, label=_("Layout") + u": "), (4, 1))
        sizer.AddMany([(perspect_lbl, (4, 2)),
                       (perspect_ch, (4, 3), wx.GBSpan(1, 2)),
                       (ws_cb, (5, 2), wx.GBSpan(1, 2)), 
                       (wp_cb, (6, 2), wx.GBSpan(1, 2))])
        sizer.Add((5, 5), (8, 0))
        sizer.Add(wx.StaticText(self, label=_("Misc") + u": "), (8, 1))
        sizer.AddMany([(trans_lbl, (8, 2)), (trans, (8, 3), wx.GBSpan(1, 3)),
                       (m_cb, (9, 2), wx.GBSpan(1, 2))])
        self.SetSizer(sizer)

    def OnSetTransparent(self, evt):
        """Sets the transparency of the editor while the slider
        is being dragged.
        @param evt: Event that called this handler

        """
        if evt.GetId() == ed_glob.ID_TRANSPARENCY:
            grandpa = self.GetGrandParent() # Main Window
            greatgrandpa = grandpa.GetParent()
            trans = evt.GetEventObject()
            value = trans.GetValue()
            grandpa.SetTransparent(value)
            greatgrandpa.SetTransparent(value)
            ed_glob.PROFILE['ALPHA'] = value

# Utilities
def SectionHead(window, title):
    """"Creates a section heading for a panel. The heading consists
    of a title on the left and a horzontal line that fills from the
    edge of the text to the edge of the window.
    @param window: window that the section heading will belong to
    @param title: text to label the section with
    @return: sizer item containing the heading

    """
    # Create the return container
    ret_obj = wx.BoxSizer(wx.HORIZONTAL)

    # Build the objects
    heading = wx.StaticText(window, wx.ID_ANY, title)
    h_width = (int(window.GetParent().GetSize()[0] * .90) - heading.GetSize()[0])
    divider = wx.StaticLine(window, wx.ID_ANY, size=(h_width, 2))

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

#----------------------------------------------------------------------------#

class ProfileListCtrl(wx.ListCtrl, 
                      listmix.ListCtrlAutoWidthMixin):
    """Class to manage the profile editor"""
    def __init__(self, parent):
        """Initializes the Profile List Control"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, wx.DefaultSize, 
                             style = wx.LC_REPORT | wx.LC_SORT_ASCENDING |
                                     wx.LC_VRULES)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.PopulateProfileView()

    def PopulateProfileView(self):
        """Populates the profile view with the profile info"""
        self.InsertColumn(0, _("Item"))
        self.InsertColumn(1, _("Value"))

        prof = ed_glob.PROFILE.keys()
        prof.sort()

        for key in prof:
            val = unicode(ed_glob.PROFILE[key])
            index = self.InsertStringItem(sys.maxint, key)
            self.SetStringItem(index, 0, key)
            self.SetStringItem(index, 1, val)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    #---- End Function Definitions ----#
class ExtListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.TextEditMixin):
    """Class to manage the profile editor"""
    FILE_COL = 0
    EXT_COL = 1
    def __init__(self, parent):
        """Initializes the Profile List Control"""
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition,wx.DefaultSize, 
                             style = wx.LC_REPORT | wx.LC_SORT_ASCENDING | wx.LC_VRULES)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.TextEditMixin.__init__(self)
        self.InsertColumn(self.FILE_COL, _("Lexer"))
        self.InsertColumn(self.EXT_COL, _("Extensions (space separated, no dots)"))
        self._extreg = syntax.ExtensionRegister()
        self._editing = None

    def CloseEditor(self, evt=None):
        """Update list and extension register after edit window
        closes.

        """
        listmix.TextEditMixin.CloseEditor(self, evt)
        def UpdateRegister(itempos):
            """Update teh ExtensionRegister"""
            vals = self.GetItem(itempos[1], itempos[0]).GetText()
            ftype = self.GetItem(itempos[1], self.FILE_COL).GetText()
            self._editing = None
            self._extreg.SetAssociation(ftype, vals)
        if self._editing != None:
            wx.CallAfter(UpdateRegister, self._editing)
        wx.CallAfter(self.UpdateExtensions)

    def LoadList(self):
        """Loads the list of filetypes to file extension mappings into the
        list control.

        """
        keys = self._extreg.keys()
        keys.sort()
        for key in keys:
            index = self.InsertStringItem(sys.maxint, key)
            self.SetStringItem(index, self.FILE_COL, key)
            self.SetStringItem(index, self.EXT_COL, u'  ' + u' '.join(self._extreg[key]))
            if not index % 2:
                syscolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DLIGHT)
                color = util.AdjustColour(syscolor, 75)
                self.SetItemBackgroundColour(index, color)

        self.SetColumnWidth(self.FILE_COL, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(self.EXT_COL, wx.LIST_AUTOSIZE)

    def OpenEditor(self, col, row):
        """Disable the editor for the first column"""
        if col == self.FILE_COL:
            return
        else:
            self._editing = (col, row)
            listmix.TextEditMixin.OpenEditor(self, col, row)

    def UpdateExtensions(self):
        """Updates the values in the EXT_COL to reflect changes
        in the ExtensionRegister.

        """
        for row in xrange(self.GetItemCount()):
            ftype = self.GetItem(row, self.FILE_COL).GetText()
            self.SetStringItem(row, self.EXT_COL, u'  ' + u' '.join(self._extreg[ftype]))

#----------------------------------------------------------------------------#
class ExChoice(wx.Choice):
    """Class to extend wx.Choice to have the GetValue
    function. This allows the application function to remain
    uniform in its value retrieval from all objects. This also extends 
    wx.Choice to have a default selected value on init.

    """
    def __init__(self, parent, cid, pos = (-1, -1), \
                 size = (-1, -1), choices = [''], default = None):
        """Constructs a Choice Control"""
        if len(choices) and isinstance(choices[0], int):
            for ind in range(len(choices)):
                choices[ind] = str(choices[ind])
        wx.Choice.__init__(self, parent, cid, pos, size, choices)
        if default != None:
            self.SetStringSelection(default)

    def GetValue(self):
        """Gets the Selected Value"""
        val = self.GetStringSelection()
        if val.isalpha():
            val.lower()
        return val

#----------------------------------------------------------------------------#
