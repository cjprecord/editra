###############################################################################
# Name: cfgdlg.py                                                             #
# Purpose: Configuration Panel for codetemplater                              #
# Author: Erik Tollerud <erik.tollerud@gmail.com>                             #
# Copyright: (c) 2010 Erik Tollerud <erik.tollerud@gmail.com>                 #
# License: wxWindows License                                                  #
###############################################################################

"""codetemplater Configuration Panel"""
__author__ = "Erik Tollerud"

#-----------------------------------------------------------------------------#

import wx       
import plugin
from os import path
from profiler import Profile_Get, Profile_Set
from templates import TemplateEditorDialog
_ = wx.GetTranslation


PROFILE_KEY_POPUP = 'CodeTemplater.Popupshortcut'
if Profile_Get(PROFILE_KEY_POPUP) is None:
    #default followlang to 'Ctrl+Alt+Space'
    Profile_Set(PROFILE_KEY_POPUP, 'Ctrl+Alt+Space')
            
PROFILE_KEY_FOLLOW_LANG = 'CodeTemplater.Followlang'
if Profile_Get(PROFILE_KEY_FOLLOW_LANG) is None:
    #default followlang to True
    Profile_Set(PROFILE_KEY_FOLLOW_LANG, True)

#-----------------------------------------------------------------------------#

class CodeTemplaterConfig(plugin.PluginConfigObject):
    """Plugin configuration object."""
    def GetConfigPanel(self, parent):
        """Get the configuration panel for this plugin
        @param parent: parent window for the panel
        @return: wxPanel
        """
        return CodeTemplaterConfigPanel(parent)
 
    def GetLabel(self):
        """Get the label for this config panel
        @return string
 
        """
        return _("CodeTemplater")

#-----------------------------------------------------------------------------#

ID_POPUP_SHORTCUT = wx.NewId()

class CodeTemplaterConfigPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(CodeTemplaterConfigPanel, self).__init__(parent, *args, **kwargs)

        # Attributes
        profshortcut = Profile_Get(PROFILE_KEY_POPUP)
        self.shortcuttxt = wx.TextCtrl(self, ID_POPUP_SHORTCUT, profshortcut)
        #self.edtempbutton = wx.Button(self, -1,_("Edit Templates"))
        self.followlangcheckbox = wx.CheckBox(self,
                                              wx.ID_ANY,
                                              _("Synchronize language with file type?"))
        self.followlangcheckbox.SetToolTipString(_("Causes the language type used for templates to adjust to the file type whenever a new tab is selected"))
        self.followlangcheckbox.SetValue(Profile_Get(PROFILE_KEY_FOLLOW_LANG))

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_TEXT, self.OnShortcutTextChange)
        #self.Bind(wx.EVT_BUTTON, self.OnEditTemplates,self.edtempbutton)
        self.Bind(wx.EVT_CHECKBOX, self.OnLangCheckBoxChange)

    def __DoLayout(self):
        basesizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, wx.ID_ANY,
                              _("Template Popup shortcut (requires restart):"))
        hsizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        hsizer.Add((5, 5), 0)
        hsizer.Add(self.shortcuttxt, 1,
                   wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL,
                   5)

        basesizer.Add(hsizer, 0, wx.EXPAND|wx.ALIGN_CENTER)
        #basesizer.Add(self.edtempbutton, 0, wx.EXPAND|wx.ALIGN_CENTER)
        basesizer.Add(self.followlangcheckbox, 0,
                      wx.ALL, 5)
        
        self.SetSizer(basesizer)

    def OnShortcutTextChange(self,evt):
        if evt.GetId() == ID_POPUP_SHORTCUT:
            text = self.shortcuttxt.GetValue()
            Profile_Set(PROFILE_KEY_POPUP,text)
        else:
            evt.Skip()
            
    def OnLangCheckBoxChange(self,evt):
        Profile_Set(PROFILE_KEY_FOLLOW_LANG,self.followlangcheckbox.GetValue())
            
#    def OnEditTemplates(self,evt):
#        current_buffer = wx.GetApp().GetCurrentBuffer()
            
#        dlg = TemplateEditorDialog(self,self,-1,_('Code Template Editor'),initiallang=current_buffer.GetLangId())
        
#        dlg.ShowModal()
#        dlg.edpanel.ApplyTemplateInfo()
#        dlg.Destroy()
 

