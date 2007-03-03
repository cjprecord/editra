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
# FILE: util.py                                                            #
# LANGUAGE: Python                                                         #
#                                                                          #
# SUMMARY:                                                                 #
# This file contains various helper functions and utilities that the       #
# program uses. Basically a random library of misfit functions.	          #
#                                                                          #
# METHODS:                                                                 #
# - FileDropTarget: Is a class that handles drag and drop events for the   #
#                   the interface.                                         #
# - GetPathChar: Returns the character used in building paths '\\' for     #
#                windows and '/' for linux and mac.                        #
# - GetFileName: Returns the name of the file from a given string          #
# - GetExtension: Returns the extension of a file.                         #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import wx
import ed_glob
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#


#---- Drag And Drop File Support ----#
class DropTarget(wx.FileDropTarget):
    """Impliments Drag and Drop Files Support for the editor"""
    def __init__(self, control, frame, log):
        """Initialize a Drop Target Object"""
        wx.FileDropTarget.__init__(self)
        self.control   = control # MainWindow Text Control
        self.window    = frame.frame
        self.LOG       = log

    def OnDropFiles(self, x_ord, y_ord, filenames):
        """Catches the drop file(s), validates, and passes them to the 
        open function.

        """
        # Check file properties and make a "clean" list of file(s) to open
        valid_files = list()
        for fname in filenames:
            self.LOG("[fdt_evt] File(s) Dropped: " + fname)
            if (not os.path.exists(fname)) or (not os.path.isfile(fname)):
                self.window.PushStatusText(_("Invalid file: %s") % fname, ed_glob.SB_INFO)
            else:
                valid_files.append(fname)

        self.OpenDropFiles(valid_files)

        return

    def OpenDropFiles(self, filenames):
        """Opens dropped text file(s)"""
        for fname in filenames:
            pathname = GetPathName(fname)
            the_file = GetFileName(fname)
            self.window.nb.OpenPage(pathname, the_file)
            self.window.PushStatusText(_("Opened file: %s") % fname, ed_glob.SB_INFO)
        return

#---- End FileDropTarget ----#

#---- Misc Common Function Library ----#

# File Helper Functions
def GetPathChar():
    """Returns the path character for the OS running the program"""
    if wx.Platform == '__WXMSW__':
        return u"\\"
    else:
        return u"/"

def GetPathName(path):
    """Gets the path minus filename"""
    path_char = GetPathChar()
    pieces = path.split(path_char)
    p_len = len(pieces)
    if os.path.isabs(path) and len(pieces) <= 2:
        root = []
        if os.sys.platform == 'win32':
            root.append(pieces[0])
            root.append(path_char)
            pieces = root + pieces[1:]
        else:
            root.append(path_char)
            pieces = root + pieces
    rpath = path_char.join(pieces[0:p_len-1])
    return rpath

def GetFileName(path):
    """Gets last atom on end of string as filename"""
    pieces = path.split(GetPathChar())
    filename = pieces[-1]
    return filename

def GetExtension(file_str):
    """Gets last atom at end of string as extension if 
    no extension whole string is returned

    """
    pieces = file_str.split('.')
    extension = pieces[-1]
    return extension

def GetIds(obj_lst):
    """Gets a list of IDs from a list of objects"""
    id_list = []
    for obj in obj_lst:
        id_list.append(obj.GetId())

    return id_list

def ResolvAbsPath(rel_path):
    """Takes a relative path and converts it to an
    absolute path.

    """
    path_char = GetPathChar()
    cwd = os.getcwd()
    pieces = rel_path.split(path_char)
    cut = 0

    for token in pieces:
        if token == "..":
            cut += 1

        if cut > 0:
            rpath = path_char.join(pieces[cut:])
            cut *= -1
            cwd = cwd.split(path_char)
            apath = path_char.join(cwd[0:cut])
        else:
            rpath = rel_path
            apath = cwd

    return apath + path_char + rpath

def HasConfigDir(loc=""):
    """ Checks if the user has a config directory and returns True 
    if the config directory exists or False if it does not.

    """
    if os.path.exists(wx.GetHomeDir() + GetPathChar() + u"." + 
                      ed_glob.prog_name + GetPathChar() + loc):
        return True
    else:
        return False

def CreateConfigDir():
    """ Creates the config directory its sub directories
    and any of the default config files.

    """

    #---- Resolve Paths ----#
    config_dir = wx.GetHomeDir() + GetPathChar() + u"." + ed_glob.prog_name
    profile_dir = config_dir + GetPathChar() + u"profiles"
    config_file = ed_glob.CONFIG['PROFILE_DIR'] + u"default.pp"
    loader = ed_glob.CONFIG['PROFILE_DIR'] + u".loader"
    dest_file = profile_dir + GetPathChar() + u"default.pp"

    #---- Create Directories ----#
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)
    if not os.path.exists(profile_dir):
        os.mkdir(profile_dir)

    dev_tool.DEBUGP("[util_info] Config_Dir: " + config_file)
    dev_tool.DEBUGP("[util_info] DEST: " + dest_file)
    dev_tool.DEBUGP("[util_info] Loader: " + loader)
    
    #---- Copy Default Config Files ----#
    if os.sys.platform == 'win32':
        os.system(u"copy " + u"\"" + config_file + u"\" \"" + dest_file + u"\"")
        os.system(u"copy " + u"\"" + loader + u"\" \"" + profile_dir + 
                  GetPathChar() + u".loader\"")
    else:
        os.system(u"cp " + config_file + " " + dest_file)
        os.system(u"cp " + loader + " " + profile_dir + 
                  GetPathChar() + u".loader")

    dev_tool.DEBUGP("[util_info] Copied config data to " + dest_file)
    ed_glob.PROFILE["MYPROFILE"] = dest_file
    from profiler import UpdateProfileLoader
    UpdateProfileLoader()

def ResolvConfigDir(config_dir):
    """Checks for a user config directory and if it is not
    found it then resolves the absolute path of the executables 
    directory from the relative execution path. This is then used 
    to find the location of the specified directory as it relates 
    to the executable directory, and returns that path as a
    string.

    """
    user_config = ( wx.GetHomeDir() + GetPathChar() + "." +
                    ed_glob.prog_name + GetPathChar() + config_dir )

    # First Check for existing user config
    if os.path.exists(user_config):
        return user_config + GetPathChar()

    #---- Begin Resolve Config Directory ----#
    path = sys.argv[0]
    path_char = GetPathChar()

    # If it is a link get the real path
    if os.path.islink(path):
        path = os.path._resolve_link(path)

    # Tokenize path
    pieces = path.split(path_char)

    if os.sys.platform == 'win32':
        # On Windows the exe is in same dir as config directories
        pro_path = path_char.join(pieces[:-1])

        if os.path.isabs(pro_path):
            pass
        elif pro_path == "":
            pro_path = os.getcwd()
            pieces = pro_path.split(path_char)
            pro_path = path_char.join(pieces[:-1])
        else:
            pro_path = ResolvAbsPath(pro_path)

    else:
        pro_path = path_char.join(pieces[:-2])

        if pro_path.startswith(path_char):
            pass
        elif pro_path == "":
            pro_path = os.getcwd()
            pieces = pro_path.split(path_char)
            if pieces[-1] not in [ed_glob.prog_name.lower(), ed_glob.prog_name]:
                pro_path = path_char.join(pieces[:-1])
        else:
            pro_path = ResolvAbsPath(pro_path)

    if os.sys.platform == "darwin":
        # On OS X the config directories are in the applet under Resources
        pro_path = ( os.path.normpath(pro_path) +
                     path_char + u"Resources" + path_char +
                     config_dir + path_char )
        if not os.path.exists(pro_path):
            # Path failed try looking relative to the src directory setup
            pro_path = pro_path.split(u"Resources")
            pro_path = "".join(pro_path)
    else:
        pro_path = ( os.path.normpath(pro_path) + 
                     path_char + config_dir + path_char )

    return pro_path

def GetResources(resource):
    """Returns a list of resource directories from a given toplevel config dir"""
    rec_dir = ResolvConfigDir(resource)
    rec_lst = list()
    if not os.path.exists(rec_dir):
        return -1
    else:
        recs = os.listdir(rec_dir)
        for rec in recs:
            if os.path.isdir(rec_dir + rec) and rec[0] != u".":
                rec_lst.append(rec.title())

        return rec_lst

def GetResourceFiles(resource, trim=True):
    """Gets a list of resource files from a directory and trims the
    file extentions from the names if trim is set to True (default).

    """
    rec_dir = ResolvConfigDir(resource)
    rec_list = list()
    if not os.path.exists(rec_dir):
        return -1
    else:
        recs = os.listdir(rec_dir)
        for rec in recs:
            if os.path.isfile(rec_dir + rec):
                if trim:
                    rec = rec.split(u".")[0]
                rec_list.append(rec.title())
        rec_list.sort()
        return rec_list

# String Manupulation/Conversion Utilities
def StrToTuple(tu_str):
    """Takes a tuple of ints that has been converted to a string format and
    reformats it back to a tuple value.

    """
    if tu_str[0] != "(":
        return ""

    tu_str = tu_str.strip('(,)')
    tu_str = tu_str.replace(',', '')
    tu_str = tu_str.split()
    neg = False
    
    ret_tu = list()
    for val in tu_str:
        # workaround of negative numbers
        if val[0] == u'-':
            neg = True

        if val.isdigit() or neg:
            if neg:
                neg = False
                ret_tu.append(int(val)*-1)
            else:
                ret_tu.append(int(val))

    return tuple(ret_tu)

            
