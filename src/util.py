############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
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

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import wx
import wx.html
import wx.lib.wxpTag
import ed_glob
import dev_tool

#--------------------------------------------------------------------------#


#---- Drag And Drop File Support ----#
class FileDropTarget(wx.FileDropTarget):
    """Impliments Drag and Drop Files Support for the editor"""
    def __init__(self, control, frame):
        """Initialize a Drop Target Object"""
        wx.FileDropTarget.__init__(self)
        self.control   = control # MainWindow Text Control
        self.window    = frame.frame
        self.pathname  = ''
        self.file_path = ''
        self.filename  = ''

    def OnDropFiles(self, x_ord, y_ord, evt):
        """Checks Current condition on recieving window/control and
        Performs proper checking to see if any existing data should
        be saved prior to passing the file handle to the Open function

        """
        #Get Drop File Path from drop event
        self.file_path = evt[0]
        self.filename = GetFileName(self.file_path)
        self.pathname = GetPathName(self.file_path)
        dev_tool.DEBUGP("[fdt_evt] File Dropped: " + self.file_path)

        # Check if file exists and is actually a file
        if (not os.path.exists(self.file_path)) or (not os.path.isfile(self.file_path)):
            self.window.PushStatusText("Invalid file: " + self.file_path, ed_glob.SB_INFO)
        else:
            self.OpenDropFile()

        return
        
    def OpenDropFile(self):
        """Opens dropped text file in a new page"""
        if self.pathname == self.filename or self.pathname == "":
            self.window.nb.OpenPage(self.pathname + GetPathChar(), 
                                    self.filename)
        else:
            self.window.nb.OpenPage(self.pathname, self.filename)

        #Update statusbar
        self.window.PushStatusText("Opened file: " + self.file_path, ed_glob.SB_INFO)

        return self.file_path

#---- End FileDropTarget ----#

#---- About Dialog ----#
class About(wx.Dialog):
    """ Class that impliments an about window """
    text = '''
    <html>
    <body bgcolor="9D2424">
    <center>
    <table bgcolor="#D8D8D8" width="100%%" cellspacing="0"
    cellpadding="0" border="1">
    <tr>
        <td align="center">
        <h2>Editra %s</h2>
        Copyright&#169; 2006 <b>Cody Precord</b><br>
        staff@editra.org<br><br>
        Platform Info: (python %s,%s)<br><br>
        License: GPL v2 (see <i>COPYING.txt</i> for full license)
        </td>
    </tr>
    </table>
    </center>
    <p>
    Editra's implimentation is completely written in <a title="python.org" href="http://python.org">Python</a> utilizing <a href="http://wxpython.org">wxPython</a> Widget Libraries for the bulk of the UI.  
    </p>
    <p>Visit the project homepage at http://editra.org</p>
    </body>
    </html>

    '''
    def __init__(self, parent):

        pre = wx.PreDialog()
        pre.Create(parent, -1, ed_glob.LANG['About'][ed_glob.L_LBL].replace(u"&", u""))
        self.PostCreate(pre)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create html window to hold project info
        html = wx.html.HtmlWindow(self, -1, size=(350, -1))
        if "gtk2" in wx.PlatformInfo:
            html.SetStandardFonts()
        py_version = sys.version.split()[0]
        html.SetPage(self.text % (ed_glob.version,
                                  py_version,
                                  ", ".join(wx.PlatformInfo[1:]),
                                  ))
        html.FindWindowById(wx.ID_OK)
        int_rep = html.GetInternalRepresentation()
        html.SetSize( (int_rep.GetWidth()+25, int_rep.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

        # Put Html window into sizer
        sizer.Add(html, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Add sizer to hold button
        b_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.Button(self, wx.ID_OK, u"Close")
        button.SetDefault()
        b_sizer.Add(button, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        # Add Button to Sizer
        sizer.Add(b_sizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL |
                  wx.ALL, 5)

        # Finish layout of all objects in Dialog
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

#---- End About ----#

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

def HasConfig():
    """ Checks if the user has a config file
    present or not. Returns True if config file
    exists or False if it does not.

    """
    if os.path.exists(wx.GetHomeDir() + GetPathChar() + u"." + 
                      ed_glob.prog_name + GetPathChar() + "profiles"):
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
    found it then Resolves the absolute path of executables 
    directory from the relative execution path. Then resolves 
    the location of the specified directory as it relates to
    the executable directory, and returns that path as a
    string.

    """
    user_config = ( wx.GetHomeDir() + GetPathChar() + "." +
                    ed_glob.prog_name + GetPathChar() + config_dir )

    # First Check for existing config
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
            if pieces[-1] == ed_glob.prog_name or pieces[-1] == u"Editra":
                pass
            else:
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

def GetLanguages():
    """Returns a list of installed language plugins or -1 if the language
    directory is not found."""
    lang_dir = ResolvConfigDir(u"language")
    lang_lst = []
    if not os.path.exists(lang_dir):
        return -1
    else:
        langs = os.listdir(lang_dir)
        for lang in langs:
            if os.path.isdir(lang_dir + lang):
                lang_lst.append(lang.title())

        return lang_lst
 
def StripAccelerators(lang_dict):
    """Strips the & characters from the dictionary items and returns
    the items as a dictionary. This is here so that we only need to 
    have one entry for each word in the dictionary instead of having
    a special entry for menu accelerators"""
    ret_dict = {}
    for key in lang_dict:
        ret_dict[key] = lang_dict[key][ed_glob.L_LBL].replace(u'&', u"")

    return ret_dict

def DeAccel(accel_str):
    """Strips the accelerator character from a string"""
    if isinstance(accel_str, basestring):
        return accel_str.replace(u'&', u'')
    else:
        return accel_str

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

    ret_tu = list()
    for val in tu_str:
        if val.isdigit():
            ret_tu.append(int(val))

    return tuple(ret_tu)

            
