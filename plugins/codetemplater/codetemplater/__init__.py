###############################################################################
# Name: __init__.py                                                           #
# Purpose: CodeTemplater plugin                                               #
# Author: Erik Tollerud <erik.tollerud@gmail.com>                             #
# Copyright: (c) 2010 Erik Tollerud <erik.tollerud@gmail.com>                 #
# License: wxWindows License                                                  #
###############################################################################

"""Applies Code Templates for regularly-used design patterns."""
__author__ = "Erik Tollerud"
__version__ = "0.4"

#-----------------------------------------------------------------------------#

import wx                   
import iface
import plugin
from os import path
from wx.stc import EVT_STC_USERLISTSELECTION
from ed_glob import CONFIG,SB_INFO,ID_RELOAD_ENC
from ed_menu import EdMenu
from ed_msg import Subscribe,EDMSG_UI_STC_USERLIST_SEL,EDMSG_UI_STC_LEXER,EDMSG_UI_NB_CHANGED
from syntax import synglob
from profiler import Profile_Get, Profile_Set
_ = wx.GetTranslation

from templates import TemplateEditorDialog, load_templates
from cfgdlg import CodeTemplaterConfig,PROFILE_KEY_POPUP,PROFILE_KEY_FOLLOW_LANG

ID_EDIT_TEMPLATES  = wx.NewId()
ID_SHOW_TEMPLATES = wx.NewId()

#-----------------------------------------------------------------------------#

class CodeTemplater(plugin.Plugin):
    """Adds an interface to add Code Templates"""
    plugin.Implements(iface.MainWindowI)  
    templates = {}
    currentlang = synglob.ID_LANG_TXT
        
    def PlugIt(self, parent):
        """Implements MainWindowI's PlugIt Method"""
        self._log = wx.GetApp().GetLog()
        self._log("[codetemplater][info] Starting codetemplater")
        
        self.templates = load_templates()

        self.currentlang = synglob.ID_LANG_TXT
        
        self.templatemenu = submenu = EdMenu()
        
        popupshortcut = Profile_Get(PROFILE_KEY_POPUP)
          
        submenu.Append(ID_SHOW_TEMPLATES,
                       _("Show Code Templates") + u'\t' + popupshortcut)
        submenu.AppendSeparator()    
        submenu.Append(ID_EDIT_TEMPLATES,_("Edit Templates..."),
                 _("Open a Dialog to Edit the Templates Currently in Use"))
                    
        toolmenu = parent.GetMenuBar().GetMenuByName("tools")
        toolmenu.AppendSubMenu(submenu,
                               _("Code Templates"),
                               _("Insert Code Templates into Document"))
        
        Subscribe(self.OnTemplate,EDMSG_UI_STC_USERLIST_SEL)
        Subscribe(self.OnLexerChange,EDMSG_UI_STC_LEXER)
        Subscribe(self.OnPageChange,EDMSG_UI_NB_CHANGED)
        
        self._log("[codetemplater][info] Finished loading codetemplater")
        
    def GetMenuHandlers(self):
        return [(ID_EDIT_TEMPLATES,self.OnEdit),
                (ID_SHOW_TEMPLATES,self.OnShow)]
    
    def GetUIHandlers(self):
        return []
            
    def OnShow(self, evt):
        if evt.GetId() == ID_SHOW_TEMPLATES:
            lst = self.templates[self.currentlang].keys()
            
            if len(lst) == 0:
                self._log("[codetemplater][info] Tried to show template list, but no templates present")
            else:
                lst.sort()
                self._log("[codetemplater][info] Showing template list: "+u','.join(lst))
                cbuff = wx.GetApp().GetCurrentBuffer()
                oldsep = cbuff.AutoCompGetSeparator()
                try:
                    cbuff.AutoCompSetSeparator(ord(u'\n'))
                    cbuff.UserListShow(1, u'\n'.join(lst))
                except wx.PyAssertionError, msg:
                    self._log("[codetemplater][err] Fail to show user list: %s" % str(msg))
                finally:
                    cbuff.AutoCompSetSeparator(oldsep)
        else:
            evt.skip()
        
    def OnTemplate(self,msg):
        current_buffer = wx.GetApp().GetCurrentBuffer()
        text = msg.GetData()['text']
        langtemp = self.templates[self.currentlang]
        if text in langtemp:
            langtemp[text].DoTemplate(current_buffer)
        else:
            self._log("[codetemplater][info] tried to find template %s, but none could be found for language %s"%(text,self.currentlang))
        
    def OnLexerChange(self,msg):
        fn,ftype = msg.GetData()
        if Profile_Get(PROFILE_KEY_FOLLOW_LANG):
            self._log("[codetemplater][info] changing to language %s for file %s due to lexer change"%(ftype,fn))
            self.currentlang = ftype
    
    def OnPageChange(self, msg):
        current_buffer = wx.GetApp().GetCurrentBuffer()
        if current_buffer and Profile_Get(PROFILE_KEY_FOLLOW_LANG):
            lid = current_buffer.GetLangId()
            self._log("[codetemplater][info] changing to language %s due to page change"%lid)
            self.currentlang = lid
            
    def OnEdit(self, evt):
        if evt.GetId() == ID_EDIT_TEMPLATES:
            self._log("[codetemplater][info] Loading Editor Dialog")
            current_buffer = wx.GetApp().GetCurrentBuffer()
            ilang = self.currentlang
            dlg = TemplateEditorDialog(wx.GetApp().GetActiveWindow(),
                                       self,
                                       wx.ID_ANY,
                                       _("Code Template Editor"),
                                       initiallang=ilang)
            dlg.CenterOnParent()
            dlg.ShowModal()
            dlg.edpanel.ApplyTemplateInfo()
            dlg.Destroy()
            self._log("[codetemplater][info] Completed Editing")
        else:
            evt.Skip()

# Editra Plugin Configuration Interface
def GetConfigObject():
    return CodeTemplaterConfig()
