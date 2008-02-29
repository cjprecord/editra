###############################################################################
# Name: prefdlg.py                                                            #
# Purpose: UI for configuring User Profile                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#----------------------------------------------------------------------------#
# FILE: prefdlg.py                                                           #
# LANGUAGE: Python							                                 #
#                                                                            #
# SUMMARY:                                                                   #
#   The classes and functions contained in this file are used for creating   #
#  the preference dialog that allows for dynamically configuring most of the #
#  options and setting of the program by setting values in the Profile.      #
#                                                                            #
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
import profiler
from profiler import Profile_Get, Profile_Set
import ed_i18n
import ed_event
import updater
import util
import syntax.syntax as syntax

#----------------------------------------------------------------------------#
# Globals
ID_CHECK_UPDATE = wx.NewId()
ID_DOWNLOAD     = wx.NewId()
ID_UPDATE_MSG   = wx.NewId()
ID_UPDATE_PAGE  = wx.NewId()
ID_CURR_BOX     = wx.NewId()
ID_LATE_BOX     = wx.NewId()

_ = wx.GetTranslation
#----------------------------------------------------------------------------#
# Class Globals
from wx import ImageFromStream, BitmapFromImage, EmptyIcon
import cStringIO, zlib

def getData():
    """Gets the data of the button background"""
    return zlib.decompress(
'x\xda\x01A\x02\xbe\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\
\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\
\x08d\x88\x00\x00\x01\xf8IDATX\x85\xed\x97?n\x1aA\x14\x87\xbf\xd9Y\xb0\xdd\
\x10\x05\x87\xd2[Q`"\x91\x8a\x03P\xc6\x11R\xdcE.R9F\xb2\x94\x0b87\xc8\x01\\D\
\x91S\xc5\xce\t\x9c.\x17\xa0\n\x8a%\xba\x95\x90\xe8b\x1cX\x8b\xc4\xec<&\x05\
\x7fb\xc0`b0n\xf8I[\xcc\xe8\xcd\xfb}\xf3\xdehF\xab\x18T\x1cx\x96\xc9d\x0e\
\xb5\xd6)\xe6(\x11)\x97J\xa5}\xe0;P\xeb\xcd\xabk1\xbb\xa9T*\x97\xcdfw\xb6\
\x9eo\xb1\xfed}\x9e\xfe\x9c\xff<\xe7\xf4\xeb)\xc5b\xf1\xb8\\.\xbf\x06\xa4\
\x07\xe0D"\x917\x85\xbd\xc2\xfbd2\x19\xf3<o\xae\xc6\xc3\xaaT*\x1c\xbc;\xf8\
\xd0l6\xf7\x01Q@n\xfb\xe5\xf6\xb7|>\x7f\xaf\xc6\xd7U\xadV9\xfatt\xec\xfb\xfe\
[wc\xc3\xdb\xf3<\x8f \xb8\x04\xecB\x00b\xb1Gln\xa6w|\xdf\xff\xe8F\\\xf7U"\
\x91 \x08\x1a\xb7.\xb4\xd6b\xadE)\x85R\xea\xd6\xf8Iz\x9aNsv\xf6\xe3\xd05\xc6\
P\xffU\x9fl\xdc\xad\x8cb6\xd3\x91\xbcm\x9br\x8d\x18\x1aS\xec~|\x16\xb8+\x97\
\x11\x83+"4\x1a\xc1\xdd\x01f\x90\x88\xd0iA}\xb0\x05\x137d\xa7\t\x9a\xbc\xb4\
\'c\x0c\xae\x18\xe12x\xa0\n\x18\xc1\r\x8d\xa1V\xbb@k=\xf3\xc9\x9eV\xd6ZD\x84\
\xd0\x18\x14\xdd\xca\xc4\x1f\xc7\x89F\xa2\xfd \xad5\xd1\xe8\xca\\\x0c[\xad+D\
\xe4\xdf8lQ\xbb\xe8<\x07}\x80ai\xadY\x89\xae\x0e\xcc)\xa5X[]\xc3q\x9c\x91\
\xf8\xb6m\x13\x86!\xc6\x84\xd8\xa1\x8cW\xad?\x03\x00\x039\xc7\x01\x8c\x93\
\xab#@\xe7B\x1a\xa2\xc3ZK\xbb}\xb3\xd18\xfd7\xc0\xbc5Z\xcb%\xc0\x12`\t\xb0\
\x04X\x02,V/\x1c\xe0\xcb\x03\x02\xfc\x06\xc8\xd1y\x90\x16\xfd}\xa6\xf3/\x8a\
\x03\x14\x80\xfa\x02\xcd\xeb\xc0\xeep9\n\x0b\x04(\xdc\xd4\x0f\xa7\xdb\x8e\
\x93{4>\xe9z\xf4\x0f\xff_\x17\xe2 \x06n\xab\xb1\xf7\x00\x00\x00\x00IEND\xaeB\
`\x82\x11\x87\x03\xa2' )

def getBitmap():
    """Gets the bitmap of the button base"""
    return BitmapFromImage(getImage())

def getImage():
    """Gets the image of the button base"""
    stream = cStringIO.StringIO(getData())
    return ImageFromStream(stream)

def MakeThemeTool(tool_id):
    """Makes a themed bitmap for the tool book of the pref dialog.
    @param tool_id: An art identifier id
    @return: 32x32 bitmap

    """
    osize = Profile_Get('ICON_SZ', 'size_tuple', (24, 24))
    Profile_Set('ICON_SZ', (24, 24))
    over = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
    Profile_Set('ICON_SZ', osize)
    mdc = wx.MemoryDC(getBitmap())
    if over.IsOk():
        # Create overlay
        if over.GetSize() != (24, 24):
            over = over.ConvertToImage()
            over.Rescale(24, 24, wx.IMAGE_QUALITY_HIGH)
            over = over.ConvertToBitmap()

        # Draw overlay onto button
        mdc.SetBrush(wx.TRANSPARENT_BRUSH)
        mdc.DrawBitmap(over, 4, 4, True)
    return mdc.GetAsBitmap()

#----------------------------------------------------------------------------#

class PreferencesDialog(wx.Frame):
    """Preference dialog for configuring the editor
    @summary: Provides an interface into configuring profile settings

    """
    __name__ = u'PreferencesDialog'

    def __init__(self, parent, id_=wx.ID_ANY,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL):
        """Initialises the preference dialog
        @param parent: The parent window of this window
        @param id_: The id of this window
        @param title: The title of the dialog

        """
        wx.Frame.__init__(self, parent, id_, _("Preferences - Editra"), style=style)
        util.SetWindowIcon(self)

        # Extra Styles
        self.SetTransparent(Profile_Get('ALPHA', 'int', 255))
        if wx.Platform == '__WXMAC__' and Profile_Get('METAL', 'bool', False):
            self.SetExtraStyle(wx.DIALOG_EX_METAL)

        # Attributes
        self._tbook = PrefTools(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Layout
        sizer.Add(self._tbook, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()
        wx.GetApp().RegisterWindow(repr(self), self, True)

        # Bind Events
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SHOW, self.OnShow)

    def OnClose(self, evt):
        """Hanles the window closer event
        @param evt: Event that called this handler

        """
        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()

    def OnShow(self, evt):
        """Hanles the window closer event
        @param evt: Event that called this handler

        """
        self._tbook.OnPageChanged()
        evt.Skip()

#-----------------------------------------------------------------------------#

class PrefTools(wx.Toolbook):
    """Main sections of the configuration pages
    @note: implements the top level book control for the prefdlg
    @todo: when using BK_BUTTONBAR style so that the icons have text
           under them the icons get scaled to larger size on the Mac
           causing them to look poor.

    """
    GENERAL_PG = 0
    APPEAR_PG  = 1
    DOC_PG     = 2
    UPDATE_PG  = 3
    ADV_PG     = 4

    def __init__(self, parent, tbid=wx.ID_ANY, style=wx.BK_BUTTONBAR):
        """Initializes the main book control of the preferences dialog
        @summary: creates the top level notebook control for the prefdlg
                  a toolbar is used for changing pages.
        @todo: there is some nasty dithering/icon rescaling happening on
               osx. need to se why this is.

        """
        wx.Toolbook.__init__(self, parent, tbid, style=style)

        # Attributes
        self.LOG = wx.GetApp().GetLog()
        self._imglst = wx.ImageList(32, 32)
        self._imglst.Add(MakeThemeTool(ed_glob.ID_PREF))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_THEME))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_DOCPROP))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_WEB))
        self.SetImageList(self._imglst)

        self.AddPage(GeneralPanel(self), _("General"), 
                     imageId=self.GENERAL_PG)
        self.AddPage(AppearancePanel(self), _("Appearance"), 
                     imageId=self.APPEAR_PG)
        self.AddPage(DocumentPanel(self), _("Document"), 
                     imageId=self.DOC_PG)
        self.AddPage(UpdatePanel(self), _("Update"),
                     imageId=self.UPDATE_PG)
#         self.AddPage(PrefPanelBase(self), _("Advanced"),
#                      imageId=self.ADV_PG)

        # Event Handlers
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPageChanged(self, evt=None):
        """Resizes the dialog based on the pages size
        @todo: animate the resizing so its smoother

        """
        self.LOG("[prefdlg][toolbook][evt] page changed")
        page = self.GetSelection()
        page = self.GetPage(page)
        page.SetInitialSize()
        parent = self.GetParent()
        psz = page.GetSize()
        tbh = self.GetToolBar().GetSize().GetHeight()
        parent.SetClientSize((psz.GetWidth(), psz.GetHeight() + tbh))
        parent.SendSizeEvent()
        parent.Layout()
        if evt is not None:
            evt.Skip()

    def OnPaint(self, evt):
        """Paint the toolbar's background
        @todo: it would be nice to use a unified toolbar style on osx
        @note: unified toolbar is available in 2.8.5+ maybe create custom
               window using native toolbar to accomidate this.

        """
        # This is odd but I have recieved a number of error reports where
        # wx is being reported as None in this function
        if 'wx' not in globals() or wx is None:
            evt.Skip()
            return

        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        col2 = util.AdjustColour(col1, -20)
        rect = self.GetToolBar().GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width, (rect.height + 3))

        gc.SetPen(wx.Pen(col1, 1))
        grad = gc.CreateLinearGradientBrush(0, 0, 0, rect.height, col1, col2)
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
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL | \
                                              wx.SUNKEN_BORDER)

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        """Paints the panels background
        @param evt: Event that called this handler

        """
        # This is odd but I have recieved a number of error reports where
        # wx is being reported as None in this function requires more 
        # investigation as I cannot reproduce
        if 'wx' not in globals() or wx is None:
            evt.Skip()
            return

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
    """Creates a panel with controls for Editra's general settings
    @summary: Panel with a number of controls that affect the users
              global profile setting for how Editra should operate.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        PrefPanelBase.__init__(self, parent)
        
        # Attributes
        self.LOG = wx.GetApp().GetLog()
        toolt = wx.ToolTip("Changes made in this dialog are saved in your "
                           "current profile. Some Items such as Language "
                           "require the program to be restarted before taking "
                           "affect.")
        self.SetToolTip(toolt)
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_COMBOBOX, self.OnChoice)

    def _DoLayout(self):
        """Add the controls and do the layout
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        # Startup Section
        start_lbl = wx.StaticText(self, label=_("Startup Settings") + u": ")
        mode_lbl = wx.StaticText(self, label=_("Editor Mode") + u": ")
        mode_ch = ExChoice(self, ed_glob.ID_PREF_MODE,
                           choices=['CODE', 'DEBUG', 'GUI_DEBUG'],
                           default=Profile_Get('MODE'))
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([(mode_lbl, 0), ((5, 5), 0), (mode_ch, 0)])
        pmode_lbl = wx.StaticText(self, label=_("Printer Mode") + u": ")
        pmode_ch = ExChoice(self, ed_glob.ID_PRINT_MODE,
                            choices=['Black/White', 'Colour/White', 
                                     'Colour/Default', 'Inverse', 'Normal'],
                            default=Profile_Get('PRINT_MODE'))
        psizer = wx.BoxSizer(wx.HORIZONTAL)
        psizer.AddMany([(pmode_lbl, 0), ((5, 5), 0), (pmode_ch, 0)])
        reporter_cb = wx.CheckBox(self, ed_glob.ID_REPORTER, 
                                  _("Disable Error Reporter"))
        reporter_cb.SetValue(not Profile_Get('REPORTER'))
        session_cb = wx.CheckBox(self, ed_glob.ID_SESSION, 
                                 _("Load Last Session"))
        session_cb.SetValue(Profile_Get('SAVE_SESSION'))
        tt = wx.ToolTip(_("Load files from last session on startup"))
        session_cb.SetToolTip(tt)
        splash_cb = wx.CheckBox(self, ed_glob.ID_APP_SPLASH, 
                                _("Show Splash Screen"))
        splash_cb.SetValue(Profile_Get('APPSPLASH'))

        # File settings
        file_lbl = wx.StaticText(self, label=_("File Settings") + u": ")
        fh_lbl = wx.StaticText(self, label=_("File History Length") + u": ")
        fh_ch = ExChoice(self, ed_glob.ID_PREF_FHIST,
                         choices=['1','2','3','4','5','6','7','8','9'],
                         default=Profile_Get('FHIST_LVL', 'str'))
        fhsizer = wx.BoxSizer(wx.HORIZONTAL)
        fhsizer.AddMany([(fh_lbl, 0), ((5, 5), 0), (fh_ch, 0)])
        win_cb = wx.CheckBox(self, ed_glob.ID_NEW_WINDOW,
                             _("Open files in new windows by default"))
        win_cb.SetValue(Profile_Get('OPEN_NW'))
        pos_cb = wx.CheckBox(self, ed_glob.ID_PREF_SPOS, 
                             _("Remember File Position"))
        pos_cb.SetValue(Profile_Get('SAVE_POS'))
        chkmod_cb = wx.CheckBox(self, ed_glob.ID_PREF_CHKMOD, 
                                _("Check if on disk file has been "
                                  "modified by others"))
        chkmod_cb.SetValue(Profile_Get('CHECKMOD'))

        # Locale
        locale = wx.StaticText(self, label=_("Locale Settings") + u": ")
        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_lbl = wx.StaticText(self, label=_("Language") + u": ")
        lang_c = ed_i18n.LangListCombo(self, ed_glob.ID_PREF_LANG, 
                                       Profile_Get('LANG'))
        lsizer.AddMany([(lang_lbl, 0), ((5, 5), 0), (lang_c, 0)])

        # Layout items
        sizer = wx.GridBagSizer(5, 5)
        sizer.AddMany([((5, 5), (0, 0)),
                       (start_lbl, (1, 1)),
                       (msizer, (1, 2), (1, 2)),
                       (psizer, (2, 2), (1, 2)),
                       (reporter_cb, (3, 2), (1, 2)),
                       (session_cb, (4, 2), (1, 2)),
                       (splash_cb, (5, 2), (1, 2))])
        sizer.AddMany([(file_lbl, (7, 1)),
                       (fhsizer, (7, 2), (1, 2)), (win_cb, (8, 2), (1, 3)),
                       (pos_cb, (9, 2), (1, 3)),
                       (chkmod_cb, (10, 2), (1, 2))])
        sizer.AddMany([(locale, (12, 1)),
                       (lsizer, (12, 2), (1, 3)),
                       ((15, 15), (13, 0))])
        self.SetSizer(sizer)

    def OnCheck(self, evt):
        """Handles events from the check boxes
        @param evt: event that called this handler

        """
        self.LOG("[prefdlg][gen][evt] Check box clicked")
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_APP_SPLASH, ed_glob.ID_PREF_SPOS,
                    ed_glob.ID_PREF_CHKMOD, ed_glob.ID_SESSION,
                    ed_glob.ID_NEW_WINDOW]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
        elif e_id == ed_glob.ID_REPORTER:
            Profile_Set(ed_glob.ID_2_PROF[e_id], not e_obj.GetValue())
        else:
            pass
        evt.Skip()

    def OnChoice(self, evt):
        """Handles events from the choice controls
        @param evt: event that called this handler
        @note: Also handles the Language ComboBox

        """
        self.LOG("[prefldg][gen][evt] Choice event caught")
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_PREF_MODE, ed_glob.ID_PRINT_MODE,
                    ed_glob.ID_PREF_FHIST, ed_glob.ID_PREF_LANG]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
            if e_id == ed_glob.ID_PREF_MODE:
                ed_glob.DEBUG = ('DEBUG' in e_obj.GetValue())
        else:
            evt.Skip()

class DocumentPanel(PrefPanelBase):
    """Creates a panel with controls for Editra's editing settings
    @summary: Conatains a L{wx.Notebook} that contains a number of pages
              with setting controls for how documents are handled by the
              L{ed_stc.EditraStc} text control.

    """
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
        """Do the layout of the panel
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        sizer = wx.GridBagSizer()
        self._nb.AddPage(DocGenPanel(self._nb), _("General"))
        self._nb.AddPage(DocCodePanel(self._nb), _("Code"))
        self._nb.AddPage(DocSyntaxPanel(self._nb), _("Syntax Highlighting"))
        sizer.Add(self._nb, (1, 1))
        sizer.Add((5, 5), (2, 2))
        self.SetSizer(sizer)

class DocGenPanel(wx.Panel):
    """Panel used for general document settings in the DocumentPanel's
    notebook.
    @summary: Panel with controls for setting the general attributes of
              how a document is managed.

    """
    ID_FONT_PICKER = wx.NewId()
    ID_FONT_PICKER2 = wx.NewId()

    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)
        
        # Layout
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateEditor)
        self.Bind(wx.EVT_CHOICE, self.OnUpdateEditor)
        self.Bind(ed_event.EVT_NOTIFY, self.OnFontChange)

    def _DoLayout(self):
        """Layout the controls
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        # Format Section
        tabw_lbl = wx.StaticText(self, label=_("Tab Width") + u": ")
        tw_ch = ExChoice(self, ed_glob.ID_PREF_TABW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=Profile_Get('TABWIDTH', 'str'))
        ut_cb = wx.CheckBox(self, ed_glob.ID_PREF_TABS, 
                            _("Use Tabs Instead of Spaces"))
        ut_cb.SetValue(Profile_Get('USETABS', 'bool', False))
        eol_lbl = wx.StaticText(self, label=_("Default EOL Mode") + u": ")
        eol_ch = ExChoice(self, ed_glob.ID_EOL_MODE,
                          choices=[_("Macintosh (\\r)"), _("Unix (\\n)"), 
                                   _("Windows (\\r\\n)")],
                          default=Profile_Get('EOL'))

        # View Options
        view_lbl = wx.StaticText(self, label=_("View Options") + u": ")
        aa_cb = wx.CheckBox(self, ed_glob.ID_PREF_AALIAS, _("AntiAliasing"))
        aa_cb.SetValue(Profile_Get('AALIASING'))
        seol_cb = wx.CheckBox(self, ed_glob.ID_SHOW_EOL, _("Show EOL Markers"))
        seol_cb.SetValue(Profile_Get('SHOW_EOL'))
        sln_cb = wx.CheckBox(self, ed_glob.ID_SHOW_LN, _("Show Line Numbers"))
        sln_cb.SetValue(Profile_Get('SHOW_LN'))
        sws_cb = wx.CheckBox(self, ed_glob.ID_SHOW_WS, _("Show Whitespace"))
        sws_cb.SetValue(Profile_Get('SHOW_WS'))
        ww_cb = wx.CheckBox(self, ed_glob.ID_WORD_WRAP, _("Word Wrap"))
        ww_cb.SetValue(Profile_Get('WRAP'))
        if wx.Platform == '__WXMAC__':
            ww_cb.SetToolTip(wx.ToolTip(_("Turn off for better performance")))

        # Font Options
        font_lbl = wx.StaticText(self, label=_("Primary Font") + u": ")
        fnt = Profile_Get('FONT1', 'font', wx.Font(10, wx.FONTFAMILY_MODERN, 
                                                   wx.FONTSTYLE_NORMAL, 
                                                   wx.FONTWEIGHT_NORMAL))
        fpicker = PyFontPicker(self, self.ID_FONT_PICKER, fnt)
        tt = wx.ToolTip(_("Sets the main/default font of the document"))
        fpicker.SetToolTip(tt)
        font_lbl2 = wx.StaticText(self, label=_("Secondary Font") + u": ")
        fnt = Profile_Get('FONT2', 'font', wx.Font(10, wx.FONTFAMILY_SWISS,
                                                   wx.FONTSTYLE_NORMAL, 
                                                   wx.FONTWEIGHT_NORMAL))
        fpicker2 = PyFontPicker(self, self.ID_FONT_PICKER2, fnt)
        tt = wx.ToolTip(_("Sets a secondary font used for special regions "
                          "when syntax highlighting is in use"))
        fpicker2.SetToolTip(tt)

        # Layout
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add((5, 5), (1, 0))
        sizer.Add(wx.StaticText(self, label=_("Format") + u": "), (1, 1))
        sizer.AddMany([(ut_cb, (1, 2), wx.GBSpan(1, 2)),
                       (tabw_lbl, (2, 2)), (tw_ch, (2, 3), wx.GBSpan(1, 3)),
                       (eol_lbl, (3, 2)), (eol_ch, (3, 3), wx.GBSpan(1, 2)),
                       ((5, 5), (5, 0)), (view_lbl, (5, 1)),
                       (aa_cb, (5, 2)), (seol_cb, (6, 2)), (sln_cb, (7, 2)),
                       (sws_cb, (8, 2)), (ww_cb, (9, 2)),
                       (font_lbl, (11, 1)), 
                       (fpicker, (11, 2), (1, 3), wx.EXPAND), 
                       (font_lbl2, (12, 1)),
                       (fpicker2, (12, 2), (1, 3), wx.EXPAND),
                       ((5, 5), (13, 0))
                       ])
        self.SetSizer(sizer)

    def OnFontChange(self, evt):
        """Handles L{ed_event.EVT_NOTIFY} from the font controls"""
        e_id = evt.GetId()
        if e_id in [self.ID_FONT_PICKER, self.ID_FONT_PICKER2]:
            font = evt.GetValue()
            if not isinstance(font, wx.Font) or font.IsNull():
                return

            if e_id == self.ID_FONT_PICKER:
                Profile_Set('FONT1', font, 'font')
            else:
                Profile_Set('FONT2', font, 'font')

            for main in wx.GetApp().GetMainWindows():
                for stc in main.nb.GetTextControls():
                    stc.SetStyleFont(font, e_id == self.ID_FONT_PICKER)
                    stc.UpdateAllStyles()
        else:
            evt.Skip()

    def OnUpdateEditor(self, evt):
        """Update any open text controls to reflect the changes made in this
        panel from the checkboxes and choice controls.
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_PREF_TABS, ed_glob.ID_PREF_TABW,
                    ed_glob.ID_EOL_MODE, ed_glob.ID_PREF_AALIAS,
                    ed_glob.ID_SHOW_EOL, ed_glob.ID_SHOW_LN,
                    ed_glob.ID_SHOW_WS, ed_glob.ID_WORD_WRAP,
                    ed_glob.ID_PREF_AALIAS]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
            wx.CallLater(25, DoUpdates)
        else:
            evt.Skip()

class DocCodePanel(wx.Panel):
    """Panel used for programming settings
    @summary: Houses many of the controls for configuring the editors features 
              that are related to programming.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)
        
        # Layout
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CHOICE, self.OnCheck)
        self.Bind(wx.EVT_SLIDER, self.OnSlide)

    def _DoLayout(self):
        """Layout the page
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        # Visual Helpers Section
        vis_lbl = wx.StaticText(self, label=_("Visual Helpers") + u": ")
        br_cb = wx.CheckBox(self, ed_glob.ID_BRACKETHL, 
                            _("Bracket Highlighting"))
        br_cb.SetValue(Profile_Get('BRACKETHL'))
        fold_cb = wx.CheckBox(self, ed_glob.ID_FOLDING, _("Code Folding"))
        fold_cb.SetValue(Profile_Get('CODE_FOLD'))
        edge_cb = wx.CheckBox(self, ed_glob.ID_SHOW_EDGE, _("Edge Guide"))
        edge_cb.SetValue(Profile_Get('SHOW_EDGE'))

        edge_size = (-1, -1)
        if wx.Platform == '__WXGTK__':
            edge_size = (150, 15)
        edge_sl = wx.Slider(self, ed_glob.ID_PREF_EDGE, Profile_Get('EDGE'),
                            0, 100, size=edge_size, style=wx.SL_HORIZONTAL | \
                            wx.SL_AUTOTICKS | wx.SL_LABELS)
        edge_sl.SetTickFreq(5, 1)
        if wx.Platform == '__WXMAC__':
            edge_sl.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        ind_cb = wx.CheckBox(self, ed_glob.ID_INDENT_GUIDES, 
                             _("Indentation Guides"))
        ind_cb.SetValue(Profile_Get('GUIDES'))

        # Input Helpers
        comp_cb = wx.CheckBox(self, ed_glob.ID_AUTOCOMP, _("Auto-Completion"))
        comp_cb.SetValue(Profile_Get('AUTO_COMP'))
        ai_cb = wx.CheckBox(self, ed_glob.ID_AUTOINDENT, _("Auto-Indent"))
        ai_cb.SetValue(Profile_Get('AUTO_INDENT'))
        vi_cb = wx.CheckBox(self, ed_glob.ID_VI_MODE, _("Enable Vi Emulation"))
        vi_cb.SetValue(Profile_Get('VI_EMU'))

        # Layout the controls
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add((5, 5), (1, 0))
        sizer.Add(vis_lbl, (1, 1))
        sizer.AddMany([(br_cb, (1, 2)), (fold_cb, (2, 2)),
                       (edge_cb, (3, 2)),
                       (wx.StaticText(self, label=_("Column") + u": "), (3, 3)),
                       (edge_sl, (3, 4), (2, 2), wx.EXPAND), (ind_cb, (4, 2))])
        sizer.Add(wx.StaticText(self, label=_("Input Helpers") + u": "), (6, 1))
        sizer.AddMany([(comp_cb, (6, 2)), (ai_cb, (7, 2)), (vi_cb, (8, 2))])
        self.SetSizer(sizer)

    def OnCheck(self, evt):
        """Handles the events from this panels check boxes
        @param evt: Event that called this handler
        @note: also handles the one choice control event
               in this panel.

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_BRACKETHL, ed_glob.ID_SHOW_EDGE,
                    ed_glob.ID_INDENT_GUIDES, ed_glob.ID_FOLDING,
                    ed_glob.ID_AUTOCOMP, ed_glob.ID_AUTOINDENT,
                    ed_glob.ID_PREF_EDGE, ed_glob.ID_VI_MODE]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
            wx.CallLater(25, DoUpdates)
        else:
            evt.Skip()

    def OnSlide(self, evt):
        """Catch actions from a slider
        @param evt: Event that called this handler.

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id == ed_glob.ID_PREF_EDGE:
            val = e_obj.GetValue()
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)

            for mainw in wx.GetApp().GetMainWindows():
                for stc in mainw.nb.GetTextControls():
                    stc.SetEdgeColumn(val)
        else:
            evt.Skip()

class DocSyntaxPanel(wx.Panel):
    """Document syntax config panel
    @summary: Manages the configuration of the syntax highlighting
              of the documents in the editor.

    """
    def __init__(self, parent):
        """Inialize the config panel
        @param parent: parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Attributes
        self._elist = ExtListCtrl(self)
        self._elist.LoadList()

        # Layout page
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnSynChange)
        self.Bind(wx.EVT_CHOICE, self.OnSynChange)

    def _DoLayout(self):
        """Layout all the controls
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        

        # Syntax Settings
        syn_cb = wx.CheckBox(self, ed_glob.ID_SYNTAX, _("Syntax Highlighting"))
        syn_cb.SetValue(Profile_Get('SYNTAX'))
        syntheme = ExChoice(self, ed_glob.ID_PREF_SYNTHEME,
                            choices=util.GetResourceFiles(u'styles', 
                                                          get_all=True),
                            default=Profile_Get('SYNTHEME', 'str'))

        line = wx.StaticLine(self, size=(-1, 2))
        lsizer = wx.BoxSizer(wx.VERTICAL)
        lsizer.Add(line, 0, wx.EXPAND)
        lst_lbl = wx.StaticText(self, label=_("Filetype Associations") + u": ")

        # Layout the controls
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([(syn_cb, 0, wx.ALIGN_LEFT), ((5, 5), 1, wx.EXPAND),
                        (wx.StaticText(self, label=_("Color Scheme") + u": "), \
                        0, wx.ALIGN_LEFT),
                        (syntheme, 0, wx.EXPAND), ((5, 5), 0)])

        sizer.AddMany([((15, 15), 0), 
                       (hsizer, 0, wx.EXPAND),
                       ((5, 5), 0),
                       (lsizer, 0, wx.EXPAND),
                       ((15, 15), 0),
                       (lst_lbl, 0, wx.ALIGN_LEFT)])


        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add((5, 5), 0)
        hsizer2.Add(self._elist, 1, wx.EXPAND)
        hsizer2.Add((5, 5), 0)

        sizer.Add((10, 10), 0)
        sizer.Add(hsizer2, 1, wx.EXPAND)
        sizer.Add((20, 20), 0)
        sizer.Add(wx.Button(self, wx.ID_DEFAULT, 
                  _("Revert to Default")), 0, wx.ALIGN_LEFT)
        sizer.Add((10, 10), 0)

        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((5, 5), 0), (sizer, 1, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(msizer)

    def OnButton(self, evt):
        """Reset button handler
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        if e_id == wx.ID_DEFAULT:
            syntax.ExtensionRegister().LoadDefault()
            self._elist.UpdateExtensions()
        else:
            evt.Skip()

    def OnSynChange(self, evt):
        """Handles the events from checkbox and choice control for this panel
        @param evt: event that called this handler
        @postcondition: all text controls are updated to reflect the changes
                        made in these controls.

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_SYNTAX, ed_glob.ID_PREF_SYNTHEME]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())

            for mainw in wx.GetApp().GetMainWindows():
                mainw.nb.UpdateTextControls()
        else:
            evt.Skip()

class AppearancePanel(PrefPanelBase):
    """Creates a panel with controls for Editra's appearance settings
    @summary: contains all the controls for configuring the appearance
              related settings in Editra.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        PrefPanelBase.__init__(self, parent)
        
        # Layout
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_SLIDER, self.OnSetTransparent, \
                  id=ed_glob.ID_TRANSPARENCY)

    def _DoLayout(self):
        """Add and layout the widgets
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        # Icons Section
        from ed_theme import BitmapProvider
        icons = ['Default']
        icons.extend(BitmapProvider(wx.GetApp().GetPluginManager()).GetThemes())
        tb_icont = wx.StaticText(self, wx.ID_ANY, _("Icon Theme") + u": ")
        tb_icon = ExChoice(self, ed_glob.ID_PREF_ICON,
                            choices=icons, 
                            default=Profile_Get('ICONS', 'str').title())
        tb_isz_lbl = wx.StaticText(self, wx.ID_ANY, \
                                   _("Toolbar Icon Size") + u": ")
        tb_isz_ch = ExChoice(self, ed_glob.ID_PREF_ICONSZ,
                              choices=['16', '24', '32'],
                              default=str(Profile_Get('ICON_SZ', 'size_tuple')[0]))

        # Layout Section
        perspect_lbl = wx.StaticText(self, wx.ID_ANY, \
                                     _("Default Perspective") + u": ")
        mainw = wx.GetApp().GetActiveWindow()
        if mainw is not None:
            pchoices = mainw.GetPerspectiveList()
        else:
            pchoices = list()
        perspect_ch = ExChoice(self, ed_glob.ID_PERSPECTIVES,
                               choices=pchoices,
                               default=Profile_Get('DEFAULT_VIEW'))
        ws_cb = wx.CheckBox(self, ed_glob.ID_PREF_WSIZE, \
                            _("Remember Window Size on Exit"))
        ws_cb.SetValue(Profile_Get('SET_WSIZE'))
        wp_cb = wx.CheckBox(self, ed_glob.ID_PREF_WPOS, \
                            _("Remember Window Position on Exit"))
        wp_cb.SetValue(Profile_Get('SET_WPOS'))

        # Misc
        trans_size = (-1, -1)
        if wx.Platform == '__WXGTK__':
            trans_size = (200, 15)
        trans_lbl = wx.StaticText(self, wx.ID_ANY, _("Transparency") + u": ")
        trans = wx.Slider(self, ed_glob.ID_TRANSPARENCY, 
                          Profile_Get('ALPHA'), 100, 255, size=trans_size,
                          style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | 
                                wx.SL_LABELS)
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        tsizer.AddMany([(trans_lbl, 0), ((5, 5), 0), (trans, 0)])

        # Activate Metal Style for OSX
        if wx.Platform == '__WXMAC__':
            m_cb = wx.CheckBox(self, ed_glob.ID_PREF_METAL, \
                               _("Use Metal Style"))
            m_cb.SetValue(Profile_Get('METAL', 'bool', False))
            m_cb.SetToolTip(wx.ToolTip(_("Restart Required")))
        else:
            m_cb = (0, 0)

        # Layout
        sizer = wx.GridBagSizer(5, 4)
        sizer.AddMany([((5, 5), (0, 1)),
                       (wx.StaticText(self, label=_("Icons") + u": "), (1, 1)),
                       (tb_icont, (1, 2)), (tb_icon, (1, 3)),
                       (tb_isz_lbl, (2, 2)), (tb_isz_ch, (2, 3)),
                       ((5, 5), (4, 0)),
                       (wx.StaticText(self, label=_("Layout") + u": "), (4, 1))
                      ])
        sizer.AddMany([(perspect_lbl, (4, 2)),
                       (perspect_ch, (4, 3), (1, 2)),
                       (ws_cb, (5, 2), (1, 2)), 
                       (wp_cb, (6, 2), (1, 2))])
        sizer.Add((5, 5), (8, 0))
        sizer.Add(wx.StaticText(self, label=_("Misc") + u": "), (8, 1))
        sizer.AddMany([(tsizer, (8, 2), (1, 2)),
                       (m_cb, (9, 2), (1, 2)),
                       ((15, 15), (10, 2))])
        self.SetSizer(sizer)

    def OnCheck(self, evt):
        """Updates profile based on checkbox actions
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        val = evt.GetEventObject().GetValue()
        if e_id in [ed_glob.ID_PREF_WPOS, ed_glob.ID_PREF_WSIZE]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)
        elif e_id == ed_glob.ID_PREF_METAL:
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)
        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handles selection events from the choice controls
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        val = e_obj.GetValue()
        if e_id in [ed_glob.ID_PREF_ICON, ed_glob.ID_PREF_ICONSZ]:
            if e_id == ed_glob.ID_PREF_ICONSZ:
                val = (int(val), int(val))
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)
            wx.GetApp().ReloadArtProvider()
            for mainw in wx.GetApp().GetMainWindows():
                toolbar = mainw.GetToolBar()
                if toolbar is not None and \
                   (toolbar.GetToolTheme() != Profile_Get('ICONS')) \
                   or (toolbar.GetToolBitmapSize() != Profile_Get('ICON_SZ')):
                    toolbar.ReInit()
                mainw.UpdateToolBar()

                # Update Search Bar
                # TODO for some reason this doesnt work with 2.8.5
                sbar = mainw.FindWindowById(ed_glob.ID_COMMAND_BAR)
                if sbar:
                    sbar.UpdateIcons()

        elif e_id == ed_glob.ID_PERSPECTIVES:
            Profile_Set('DEFAULT_VIEW', e_obj.GetValue())
            for main_win in wx.GetApp().GetMainWindows():
                main_win.SetPerspective(Profile_Get('DEFAULT_VIEW'))
        else:
            evt.Skip()

    def OnSetTransparent(self, evt):
        """Sets the transparency of the editor while the slider
        is being dragged.
        @param evt: Event that called this handler

        """
        if evt.GetId() == ed_glob.ID_TRANSPARENCY:
            trans = evt.GetEventObject()
            value = trans.GetValue()
            for window in wx.GetApp().GetOpenWindows().values():
                win = window[0]
                if hasattr(win, 'SetTransparent'):
                    win.SetTransparent(value)
            Profile_Set('ALPHA', value)
        else:
            evt.Skip()

class UpdatePanel(PrefPanelBase):
    """Creates a panel with controls for updating Editra
    @summary: Panel with three controls, L{updater.UpdateProgress} bar,
              and two L{wx.Button} for checking and downloading updates.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        PrefPanelBase.__init__(self, parent)
        
        # Attributes
        self.LOG = wx.GetApp().GetLog()
        self._DoLayout()
        
        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(ed_event.EVT_UPDATE_TEXT, self.OnUpdateText)

    def _DoLayout(self):
        """Do the layout of the panel
        @note: Controls are layed out using L{wx.GridBagSizer}

        """
        # Status text and bar
        cur_box = wx.StaticBox(self, ID_CURR_BOX, _("Installed Version"))
        cur_sz = wx.StaticBoxSizer(cur_box, wx.HORIZONTAL)
        cur_sz.SetMinSize(wx.Size(150, 40))
        cur_ver = wx.StaticText(self, wx.ID_ANY,  ed_glob.VERSION)
        cur_sz.Add(cur_ver, 0, wx.ALIGN_CENTER_HORIZONTAL)
        e_update = updater.UpdateProgress(self, ed_glob.ID_PREF_UPDATE_BAR)
        upd_box = wx.StaticBox(self, ID_LATE_BOX, _("Latest Version"))
        upd_bsz = wx.StaticBoxSizer(upd_box, wx.HORIZONTAL)
        upd_bsz.SetMinSize(wx.Size(150, 40))
        upd_sta = wx.StaticText(self, ID_UPDATE_MSG, _(e_update.GetStatus()))
        upd_bsz.Add(upd_sta, 0, wx.ALIGN_CENTER_HORIZONTAL)
        upd_bsz.Layout()

        # Control buttons
        check_b = wx.Button(self, ID_CHECK_UPDATE, _("Check"))
        dl_b = wx.Button(self, ID_DOWNLOAD, _("Download"))
        dl_b.Disable()

        # Layout Controls
        statsz = wx.BoxSizer(wx.HORIZONTAL)
        statsz.AddMany([((15, 15), 0),
                        (cur_sz, 0),
                        ((20, 10), 1),
                        (upd_bsz, 0),
                        ((15, 15), 0)])
        sizer = wx.GridBagSizer()
        sizer.AddMany([(statsz, (1, 1), (2, 5), wx.EXPAND),
                       (e_update, (4, 1), (1, 5), wx.EXPAND),
                       (check_b, (6, 2), (1, 1)), (dl_b, (6, 4), (1, 1)),
                       ((15, 15), (7, 2)), ((5, 5), (7, 7))])
        self.SetSizer(sizer)

    def OnButton(self, evt):
        """Handles events generated by the panels buttons
        @param evt: event that called this handler

        """
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
                                            _("Downloading Update"))
            dp_sz = wx.GetDisplaySize()
            dl_dlg.SetPosition(((dp_sz[0] - (dl_dlg.GetSize()[0] + 5)), 25))
            dl_dlg.Show()
        else:
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
                dl_bt = chk_bt = None
                dl_bt = self.FindWindowById(ID_DOWNLOAD)
                chk_bt = self.FindWindowById(ID_CHECK_UPDATE)
                if dl_bt is not None and upd.GetUpdatesAvailable():
                    dl_bt.Enable()
                if chk_bt is not None:
                    chk_bt.Enable()
        self.Layout()
        curr_pg = self.GetParent().GetSelection()
        nbevt = wx.NotebookEvent(wx.wxEVT_COMMAND_TOOLBOOK_PAGE_CHANGED, 
                                 0, curr_pg, curr_pg)
        wx.PostEvent(self.GetParent(), nbevt)
        self.Refresh()

#----------------------------------------------------------------------------#
# Custom controls for the Preference dialog

class ProfileListCtrl(wx.ListCtrl, 
                      listmix.ListCtrlAutoWidthMixin):
    """Displays the contents of the current users profile in a list control.
    @note: uses L{wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin}

    """
    def __init__(self, parent):
        """Initializes the Profile List Control
        @param parent: The parent window of this control

        """
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, wx.DefaultSize, 
                             style = wx.LC_REPORT | wx.LC_SORT_ASCENDING |
                                     wx.LC_VRULES)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.PopulateProfileView()

    def PopulateProfileView(self):
        """Populates the profile view with the profile info
        @postcondition: The control is populated with all data found in
                        the users running profile

        """
        self.InsertColumn(0, _("Item"))
        self.InsertColumn(1, _("Value"))

        prof = profiler.Profile().keys()
        prof.sort()

        for key in prof:
            val = unicode(Profile_Get(key))
            index = self.InsertStringItem(sys.maxint, key)
            self.SetStringItem(index, 0, key)
            self.SetStringItem(index, 1, val)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    #---- End Function Definitions ----#
class ExtListCtrl(wx.ListCtrl, 
                  listmix.ListCtrlAutoWidthMixin, 
                  listmix.TextEditMixin):
    """Class to manage the file extension associations
    @summary: Creates a list control for showing file type to file extension
              associations as well as providing an interface to editing these
              associations

    """
    FILE_COL = 0
    EXT_COL = 1
    def __init__(self, parent):
        """Initializes the Profile List Control
        @param parent: The parent window of this control

        """
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, 
                             wx.DefaultPosition, wx.DefaultSize, 
                             style=wx.LC_REPORT | wx.LC_SORT_ASCENDING | \
                                   wx.LC_VRULES | wx.BORDER)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.TextEditMixin.__init__(self)
        self.InsertColumn(self.FILE_COL, _("Lexer"))
        self.InsertColumn(self.EXT_COL, \
                          _("Extensions (space separated, no dots)"))
        self._extreg = syntax.ExtensionRegister()
        self._editing = None

    def CloseEditor(self, evt=None):
        """Update list and extension register after edit window
        closes.
        @keyword evt: Action that triggered this function

        """
        listmix.TextEditMixin.CloseEditor(self, evt)
        def UpdateRegister(itempos):
            """Update the ExtensionRegister
            @param itempos: position of the item to base updates on

            """
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
        @postcondition: The running configuration data that is kept by the
                        syntax manager that relates to file associations is
                        loaded into the list control in alphabetical order

        """
        keys = self._extreg.keys()
        keys.sort()
        for key in keys:
            index = self.InsertStringItem(sys.maxint, key)
            self.SetStringItem(index, self.FILE_COL, key)
            self.SetStringItem(index, self.EXT_COL, \
                               u'  %s' % u' '.join(self._extreg[key]))
            if not index % 2:
                syscolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DLIGHT)
                color = util.AdjustColour(syscolor, 75)
                self.SetItemBackgroundColour(index, color)

        self.SetColumnWidth(self.FILE_COL, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(self.EXT_COL, wx.LIST_AUTOSIZE)

    def OpenEditor(self, col, row):
        """Disable the editor for the first column
        @param col: Column to edit
        @param row: Row to edit

        """
        if col == self.FILE_COL:
            return
        else:
            self._editing = (col, row)
            listmix.TextEditMixin.OpenEditor(self, col, row)

    def UpdateExtensions(self):
        """Updates the values in the EXT_COL to reflect changes
        in the ExtensionRegister.
        @postcondition: Any configuration changes made in the control are
                        set in the Extension register.
        @see: L{syntax.syntax.ExtensionRegister}

        """
        for row in xrange(self.GetItemCount()):
            ftype = self.GetItem(row, self.FILE_COL).GetText()
            self.SetStringItem(row, self.EXT_COL, \
                               u'  ' + u' '.join(self._extreg[ftype]))

#----------------------------------------------------------------------------#
class ExChoice(wx.Choice):
    """Class to extend wx.Choice to have the GetValue
    function. This allows the application function to remain
    uniform in its value retrieval from all objects. This also extends 
    wx.Choice to have a default selected value on init.

    """
    def __init__(self, parent, cid=wx.ID_ANY, pos=(-1, -1), \
                 size=(-1, -1), choices=list(), default=None):
        """Constructs a Choice Control
        @param parent: The parent window of this control

        """
        if len(choices) and isinstance(choices[0], int):
            for ind in range(len(choices)):
                choices[ind] = str(choices[ind])
        wx.Choice.__init__(self, parent, cid, pos, size, choices)
        if default != None:
            self.SetStringSelection(default)

    def GetValue(self):
        """Gets the Selected Value
        @return: the value of the currently selected item
        @rtype: string

        """
        val = self.GetStringSelection()
        if val.isalpha():
            val.lower()
        return val

class PyFontPicker(wx.Panel):
    """A slightly enhanced L{wx.FontPickerCtrl} that displays the
    choosen font in the text control using the choosen font
    as well as the font's size using nicer formatting.

    """
    def __init__(self, parent, id_=-1, default=wx.NullFont):
        """Initializes the PyFontPicker
        @param default: The font to initialize as selected in the control

        """
        wx.Panel.__init__(self, parent, id_, style=wx.NO_BORDER)

        # Attributes
        if default == wx.NullFont:
            self._font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        else:
            self._font = default
        self._text = wx.TextCtrl(self, style=wx.TE_CENTER | wx.TE_READONLY)
        self._text.SetFont(default)
        self._text.SetValue(u"%s - %dpt" % (self._font.GetFaceName(), \
                                            self._font.GetPointSize()))
        self._button = wx.Button(self, label=_("Set Font") + u'...')
        
        # Layout
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._sizer.Add(self._text, 1, wx.ALIGN_LEFT)
        self._sizer.Add((5, 5), 0)
        self._sizer.Add(self._button, 0, wx.ALIGN_RIGHT)
        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)
        
        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, self._button)
        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.OnChange)

    def GetFont(self):
        """Gets the currently choosen font
        @return: wx.Font

        """
        return self._font

    def GetTextCtrl(self):
        """Gets the widgets text control
        @return: wx.TextCtrl

        """
        return self._text

    def OnButton(self, evt):
        """Opens the FontDialog and processes the result
        @param evt: Event that called this handler

        """
        fdata = wx.FontData()
        fdata.SetInitialFont(self._font)
        fdlg = wx.FontDialog(self.GetParent(), fdata)
        fdlg.ShowModal()
        fdata = fdlg.GetFontData()
        fdlg.Destroy()
        wx.PostEvent(self, wx.FontPickerEvent(self, self.GetId(), 
                                              fdata.GetChosenFont()))

    def OnChange(self, evt):
        """Updates the text control using our custom stylings after
        the font is changed.
        @param evt: The event that called this handler

        """
        font = evt.GetFont()
        if font.IsNull():
            return
        self._font = font
        self._text.Clear()
        self._text.SetFont(self._font)
        self._text.SetValue(u"%s - %dpt" % (font.GetFaceName(), \
                                            font.GetPointSize()))
        evt = ed_event.NotificationEvent(ed_event.edEVT_NOTIFY, 
                                         self.GetId(), self._font, self)
        wx.PostEvent(self.GetParent(), evt)

    def SetButtonLabel(self, label):
        """Sets the buttons label"""
        self._button.SetLabel(label)
        self._button.Refresh()

    def SetToolTip(self, tip):
        """Sets the tooltip of the window
        @param tip: wx.ToolTip

        """
        # Need to make copies of the tooltip or the program
        # will crash when the dialog is closed and is doing cleanup
        self._text.SetToolTip(tip)
        tip = wx.ToolTip(tip.GetTip())
        self._button.SetToolTip(tip)
        tip = wx.ToolTip(tip.GetTip())
        wx.Panel.SetToolTip(self, tip)

#-----------------------------------------------------------------------------#
# Utility Functions

def DoUpdates():
    """Update all open text controls"""
    for mainw in wx.GetApp().GetMainWindows():
        mainw.nb.UpdateTextControls()