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
# FILE: ed_i18n.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY: This file is a module for managing translations and the         #
#          internationalization of the program.                            #
#                                                                          #
# METHODS:                                                                 #
# GetAvailLocales: Returns a list of canonical names of available locales  #
# GetLocaleDict: Returns a dictionary consisting of canonical names for    #
#                keys and language ids for values.                         #
#
#----------------------------------                                        #
# CLASS: LangListCombo                                                     #
#                                                                          #
# METHODS:
#
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
from wx.lib import langlistctrl
import wx.combo
import glob
import ed_glob
import dev_tool

#----------------------------------------------------------------------------#
# Global Variables
OPT_NO_OP    = 0
OPT_DESCRIPT = 1

#----------------------------------------------------------------------------#

#---- Helper Functions used by the classes in this module ----#
def GetAvailLocales():
    """Gets a list of the available locales that have been installed
    for the editor. Returning a list of strings that represent the 
    canonical names of each language.

    """
    avail_loc = list()
    loc = glob.glob(os.path.join(ed_glob.CONFIG['LANG_DIR'], "*"))
    for path in loc:
        the_path = os.path.join(path, "LC_MESSAGES", ed_glob.prog_name + ".mo")
        if os.path.exists(the_path):
            avail_loc.append(os.path.basename(path))
    return avail_loc

def GetLocaleDict(loc_list, opt=OPT_NO_OP):
    """Takes a list of cannonical locale names and by default returns a 
    dictionary of available language values using the canonical name as 
    the key. Supplying the Option OPT_DESCRIPT will return a dictionary
    of language id's with languages description as the key.

    """
    lang_dict = dict()
    for lang in [x for x in dir(wx) if x.startswith("LANGUAGE")]:
        loc_i = wx.Locale(wx.LANGUAGE_DEFAULT).GetLanguageInfo(getattr(wx, lang))
        if loc_i:
            if loc_i.CanonicalName in loc_list:
                if opt == OPT_DESCRIPT:
                    lang_dict[loc_i.Description] = getattr(wx, lang)
                else:
                    lang_dict[loc_i.CanonicalName] = getattr(wx, lang)
    return lang_dict

def GetLangId(lang_n):
    """Gets the ID of a language from the description string. If the 
    language cannot befound the function simply returns the default language
    
    """
    lang_desc = GetLocaleDict(GetAvailLocales(), OPT_DESCRIPT)
    if(lang_desc.has_key(lang_n)):
        return lang_desc[lang_n]
    else:
        return wx.LANGUAGE_DEFAULT

#---- Language List Combo Box----#
class LangListCombo(wx.combo.BitmapComboBox):
    """Combines the data from a LangLstCtrl into a combo select box.
    Populates it self with the available translations for the editor on init.

    """
    def __init__(self, parent, id, default=None):
        """Initializes the combobox"""
        self.default = default
        lang_ids = GetLocaleDict(GetAvailLocales()).values()
        if wx.LANGUAGE_DEFAULT not in lang_ids:
            lang_ids.append(wx.LANGUAGE_DEFAULT)
        lang_items = langlistctrl.CreateLanguagesResourceLists(langlistctrl.LC_ONLY, lang_ids)
        wx.combo.BitmapComboBox.__init__(self, parent, id, 
                                         size=wx.Size(320, 26), 
                                         style=wx.CB_READONLY)
        for lang_d in lang_items[1]:
            bit_m = lang_items[0].GetBitmap(lang_items[1].index(lang_d))
            self.Append(lang_d, bit_m)
        if default:
            self.SetValue(default)

        # Bind Events
        # wxMacBug? clicking outside of control to close the selection list 
        #      causes the value of the control to be set to None/Empty String.
        #      Also clicking on the drop down button and releasing it without
        #      making a new selection also causes this behavior. So need to
        #      catch these events and reset the selection when it gets set to
        #      an empty string. The event handler that these events are
        #      sent to catch most conditions except if the inital click on the
        #      the drop button and then click off. The BitmapComboBox is 
        #      currently stated as being "abit klunky" on the Mac so this may 
        #      be clarified in a future update.
        self.Bind(wx.EVT_LEFT_UP, self.OnComboClick, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnComboClick, self)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnComboClick, self)

    def OnComboClick(self, evt):
        """Event handler for clicks in the combo box"""
        sel = self.GetValue()
        if sel == "" or sel == None:
            self.SetValue(self.default)
        dev_tool.DEBUGP("[ed_i18n] [obj_evt] LangListCombo Clicked")
        evt.Skip()
        
