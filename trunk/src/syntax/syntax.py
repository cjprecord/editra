###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
#                                                                             #
#    Editra is free software; you can redistribute it and#or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    Editra is distributed in the hope that it will be useful,                #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program; if not, write to the                            #
#    Free Software Foundation, Inc.,                                          #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                #
###############################################################################

"""
#-----------------------------------------------------------------------------#
# FILE: syntax.py                                                             #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Toolkit for managing the importing of syntax modules and providing the data #
# to the requesting text control.                                             #
#                                                                             #
# DETAIL:                                                                     #
# Since in Python Modules are only loaded once and maintain a single instance #
# across a single program. This module is used as a storage place for         #
# checking what syntax has already been loaded to facilitate a speedup of     #
# setting lexer values.                                                       #
#                                                                             #
# The use of this system also keeps the program from preloading all syntax    #
# data for all supported languages. The use of Python modules for the config  #
# files was made because Python is dynamic so why not use that feature to     #
# dynamically load configuration data. Since they are Python modules they can #
# also supply some basic functions for this module to use in loading different#
# dialects of a particular language.                                          #
#                                                                             #
# One of the driving reasons to move to this system was that the user of the  #
# editor is unlikely to be editting source files for all supported languages  #
# at one time, so there is no need to preload all data for all languages when #
# the editor starts up. Also in the long run this will be a much easier to    #
# maintain and enhance component of the editor than having all this data      #
# crammed into the text control class. The separation of data from control    #
# will also allow for user customization and modification to highlighting     #
# styles.                                                                     #
#                                                                             #
# METHODS:                                                                    #
# - IsModLoaded: Check if specified syntax module has been loaded.            #
# - SyntaxData: Returns the required syntax/lexer related data for setting up #
#               and configuring the lexer for a particular language.          #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependencies
import wx
import sys
import synglob

#-----------------------------------------------------------------------------#
# Data Objects / Constants

# Used to index the tuple returned by getting data from EXT_REG
LANG_ID     = 0
DESC_STR    = 1
LEXER_ID    = 2
MODULE      = 3

# Constants for getting values from SyntaxData's return dictionary
KEYWORDS = 0    # Keyword set(s)
LEXER    = 1    # Lexer to use
SYNSPEC  = 2    # Highligter specs
PROPERTIES = 3  # Extra Properties
LANGUAGE = 4    # Language ID
COMMENT = 5     # Gets the comment characters pattern

# Dynamically loaded modules are put here to keep them accessable to all text
# controls that access this module, so that they dont need to be reloaded.
LOADED_SYN = {}

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

# TODO this class will replace the library eventually
class SyntaxMgr:
    """Class Object for managing loaded syntax data"""
    def __init__(self):
        self.loaded_syn = []

def IsModLoaded(modname):
    """Checks if a module has already been loaded"""
    # First Check Globals then the Locals if necessary
    if modname in sys.modules or modname in LOADED_SYN:
        return True
    else:
        return False

def LoadModule(modname):
    """Dynamically loads a module by name."""
    if modname == None:
        return False
    if IsModLoaded(modname):
       pass
    else:
        try:
            LOADED_SYN[modname] = __import__(modname, globals(), locals(), [''])
        except ImportError:
            return False
    return True

def SyntaxData(langstr):
    """Fetches the language data based on a file extention string.
    The file extension is used to look up the default lexer actions from the
    EXT_REG dictionary (see synglob.py).
    
    PARAMETER: langstr, a string representing the file extension
    RETURN: Returns a Dictionary of Lexer Config Data

    """
    # The Return Value
    syn_data = dict()

    # Check if this file is a registered type
    if synglob.EXT_REG.has_key(langstr):
        lex_cfg = synglob.EXT_REG[langstr]
    else:
        # Unknown so set Plain Text Settings
        lex_cfg = synglob.EXT_REG['txt']

    syn_data[LEXER] = lex_cfg[LEXER_ID]
    if lex_cfg[LANG_ID] == synglob.ID_LANG_TXT:
        syn_data[LANGUAGE] = lex_cfg[LANG_ID]

    # Check if module is loaded and load if necessary
    if not LoadModule(lex_cfg[MODULE]):
        # Bail out as nothing else can be done at this point
        return syn_data

    # This little bit of code fetches the keyword/syntax spec set(s) from the specified module
    mod = LOADED_SYN[lex_cfg[MODULE]]  #HACK
    syn_data[KEYWORDS] = mod.Keywords(lex_cfg[LANG_ID])
    syn_data[SYNSPEC] = mod.SyntaxSpec(lex_cfg[LANG_ID])
    syn_data[PROPERTIES] = mod.Properties(lex_cfg[LANG_ID])
    syn_data[LANGUAGE] = lex_cfg[LANG_ID]
    syn_data[COMMENT] = mod.CommentPattern(lex_cfg[LANG_ID])
    return syn_data

def GenLexerMenu():
    """Generates a menu of available syntax configurations"""
    lex_menu = wx.Menu()
    
    f_types = dict()
    for key in synglob.EXT_REG:
        f_types[synglob.EXT_REG[key][DESC_STR]] = synglob.EXT_REG[key][LANG_ID]
    f_order = list(f_types)
    f_order.sort()

    for lang in f_order:
        lex_menu.Append(f_types[lang], lang, 
                         _("Switch Lexer to %s") % lang, wx.ITEM_CHECK)

    return lex_menu

def GenFileFilters():
    """Generates a list of file filters"""
    # Build dictionary of File types and associated extensions
    f_dict = dict()
    for key in synglob.EXT_REG:
        ftype = synglob.EXT_REG[key][DESC_STR]
        if f_dict.has_key(ftype):
            f_dict[ftype].append(key)
        else:
            f_dict[ftype] = [key]

    # Convert extention list into a formated string
    for key in f_dict:
        f_dict[key].sort()
        f_dict[key] = u";*.".join(f_dict[key])
        f_dict[key] = u";*." + f_dict[key]

    # Build the final list of properly formated strings
    filters = list()
    for key in f_dict:
        tmp = u" (%s)|%s|" % (f_dict[key][1:], f_dict[key][1:])
        filters.append(key + tmp)
    filters.sort()
    filters.insert(0, u"All Files (*.*)|*.*|")
    filters[-1] = filters[-1][:-1] # IMPORTANT trim last '|' from item in list
    return filters

def GetFileExtensions():
    """Gets a sorted list of all file extensions the editor is configured
    to handle.
    """
    ext = synglob.EXT_REG.keys()
    ext.sort()
    return ext

def GetLexerList():
    """Gets a list of unique file lexer configurations available""" 
    f_types = dict()
    for key in synglob.EXT_REG:
        f_types[synglob.EXT_REG[key][DESC_STR]] = synglob.EXT_REG[key][LANG_ID]
    f_order = list(f_types)
    f_order.sort()
    return f_order

def SyntaxIds():
    """Gets a list of all Syntax Ids and returns it"""
    s_glob = dir(synglob)
    s_ids = list()
    for item in s_glob:
        if len(item) > 2 and item[0:2] == "ID":
            s_ids.append(item)
    
    # Fetch actual values
    ret_ids = list()
    for id in s_ids:
        ret_ids.append(getattr(synglob, id))

    return ret_ids

def GetExtFromId(id):
    """Takes a language ID and fetches an appropriate file extension string"""
    if synglob.EXT_DICT.has_key(id):
        return synglob.EXT_DICT[id]
    else:
        return "txt"

