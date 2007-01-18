# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2006 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
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
# FILE:   lang_english.py                                                  #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
#   English Language Definitions for the program menus and dialogs.        #
#  This file is here as a template to show how to create language plugins  #
#  for editor. English language is built in to editor as the default and   #
#  also as a failsafe incase another language file fails to load for some  #
#  unforseen reason.                                                       #
#                                                                          #
#  The method for creating a language plugin is quite simple. Here we      #
#  discuss how to make a language plugin.                                  #
#  The file must reside in a directory that is named for the language it   #
#  is using, this file must be in the 'language' directory and contatin a  #
#  file named ed_lang.py.                                                  #
#                                                                          #
#  For Example:                                                            #
#      English  => language/english/ed_lang.py                             #
#      French   => language/french/ed_lang.py                              #
#      Japanese => language/japanese/ed_lang.py                            #
#                                                                          #
#  The file ed_lang.py is structured exactly like this file. It is simply  #
#  a list of keys and items. To create a custom file all that needs to be  #
#  done is to modify the items to the RIGHT of the '=' sign to be in the   #
#  language of choice.                                                     #
#                                                                          #
#  For Example:                                                            #
#      LANG['File'] = u"Translation Here"                                  #
#                                                                          #
#  After a language file is installed into the language directory Editra   #
#  will automatically check the next time it is started. Then the language #
#  can be changed either by directly changing the user profile or in the   #
#  preferences window.                                                     #
#                                                                          #
# METHODS:                                                                 #
#    None                                                                  #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies
from ed_glob import LANG # Language Dictionary

#--------------------------------------------------------------------------#

#---- Main Menus ----#

#--- File Menu ---#
LANG['File']     = [u"&File", u""]
LANG['New']      = [u"&New", u"Start a New File"]
LANG['Open']     = [u"&Open", u"Open a File"]
LANG['OpenR']    = [u"Open Recent", u"Recently Opened Files"]
LANG['Close']    = [u"&Close Page", u"Close Current Page"]
LANG['Save']     = [u"&Save", u"Save"]
LANG['SaveAs']   = [u"Save &As", u"Save As"]
LANG['SavePro']  = [u"Save Profile", u"Save Current Settings to New Profile"]
LANG['LoadPro']  = [u"Load Profile", u"Load a Custom Profile"]
LANG['Print']    = [u"&Print", u"Print Current File"]
LANG['Exit']     = [u"E&xit", u"Exit the Program"]

#--- Edit Menu ---#
LANG['Edit']     = [u"&Edit", u""]
LANG['Undo']     = [u"&Undo", u"Undo Last Action"]
LANG['Redo']     = [u"Re&do", u"Redo Last Undo"]
LANG['Cut']      = [u"Cu&t", u"Cut Selected Text From Document"]
LANG['Copy']     = [u"&Copy", u"Copy Selected Text to Clipboard"]
LANG['Paste']    = [u"&Paste", u"Paste Text from Clipboard to Document"]
LANG['SelectA']  = [u"Select &All", u"Select All Text In Document"]
LANG['Find']     = [u"&Find", u"Find Text"]
LANG['FReplace'] = [u"Find/&Replace", u"Find & Replace"]
LANG['Pref']     = [u"Preferences", u"Edit Preferences / Settings"]

#--- View Menu ---#
LANG['View']     = u"&View"
LANG['ZoomO']    = u"Zoom Out"
LANG['ZoomI']    = u"Zoom In"
LANG['ZoomD']    = u"Zoom Default"
LANG['WhiteS']   = [u"Show Whitespace", u"Show Whitespace Markers"]
LANG['IndentG']  = [u"Indentation Guides", u"Show Indentation Guides"]
LANG['Toolbar']  = [u"Toolbar", u"Show Toolbar"]

#--- Format Menu ---#
LANG['Format']   = u"F&ormat"
LANG['WordWrap'] = [u"&Word Wrap", u"Wrap Text Horizontally"]
LANG['Font']     = [u"Fon&t", u"Change Font Settings"]

#--- Settings Menu ---#
LANG['Settings'] = u"&Settings"
LANG['SyntaxHL'] = [u"Syntax Highlighting", u"Color Highlight Code Syntax"]
LANG['BraceHL']  = [u"Bracket Highlighting", u"Highlight Braces"]
LANG['KWHelper'] = [u"Keyword Helper", u"Provides a Contextual Help Menu Listing Standard Keywords/Functions"]
LANG['Lexer']    = [u"Lexers", u"Manually Set a Lexer"]

#--- Help Menu ---#
LANG['Help']     = u"&Help"
LANG['About']    = [u"&About", u"Information About this Program"]

#---- End Main Menus ----#

#---- Status Bar ----#
LANG['Line']   = u"Line"
LANG['Column'] = u"Column"

#---- Dialogs ----#
LANG['SavedF']   = u"Saved File"
LANG['SaveLoc']  = u"Choose a save location"
LANG['ChooseF']  = u"Choose a File"
LANG['SaveChg']  = [u"Save Changes?", u"Would you like to save the changes"]
LANG['Profile']  = u"Profile"
LANG['ProLoad']  = u"Profile Loaded"
LANG['NotFound'] = u"Not Found"

