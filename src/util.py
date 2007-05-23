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
# program uses. Basically a random library of misfit functions.	           #
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
import codecs
import wx
import ed_glob
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

# XXX has some issues with the clipboard on windows under certain
#     conditions. They arent fatal but need fixing.
# Found this while playing around with the PyPe source code finally
# solved the problem of allowing drag n drop text at the same time as
# drag and drop files.
class DropTargetFT(wx.PyDropTarget):
    """Drop target capable of accepting dropped files and text"""
    def __init__(self, window):
        """Initializes the Drop target"""
        wx.PyDropTarget.__init__(self)
        self.window = window
        self.initObjects()

    def initObjects(self):
        """Initializes the text and file data objects"""
        self.data = wx.DataObjectComposite()
        self.textDataObject = wx.TextDataObject()
        self.fileDataObject = wx.FileDataObject()
        self.data.Add(self.textDataObject, True)
        self.data.Add(self.fileDataObject, False)
        self.SetDataObject(self.data)

    def OnEnter(self, x, y, dragResult):
        """Handles the window enter event"""
        return dragResult

    def OnDrop(self, x=0, y=0):
        """Gets the drop cords"""
        return True

    def OnDragOver(self, x, y, dragResult):
        """Gets the drag results/cords"""
        return dragResult

    def OnData(self, x, y, dragResult):
        """Gets and processes the dropped data"""
        if self.GetData():
            files = self.fileDataObject.GetFilenames()
            text = self.textDataObject.GetText()
            
            if len(files) > 0:
                self.window.OnDrop(files)
            elif(len(text) > 0):
                if SetClipboardText(text):
                    win = self.window.GetCurrentCtrl()
                    if True:
                        p = win.PositionFromPointClose(x, y)
                        win.SetSelection(p, p)
                        win.Paste()
            else:
                self.window.SetStatusText("Can't read this dropped data")
        self.initObjects()
#---- End FileDropTarget ----#

#---- Misc Common Function Library ----#
def SetClipboardText(txt):
    """Copies text to the clipboard"""
    do = wx.TextDataObject()
    do.SetText(txt)
    if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(do)
        wx.TheClipboard.Close()
        return 1
    return 0

# File Helper Functions
def EncodeRawText(text):
    """Encodes the given raw text (text read in binary form) and trys
    to encode it into UTF-8. If this fails it will return the plain
    ascii version.

    """
    try:
        txt = unicode(text, 'utf-8', 'replace')
    except:
        txt = text
    return txt

def GetFileReader(file_name):
    """Returns a file stream reader object for reading the
    supplied file name. It returns a utf-8 reader if the host
    system supports it other wise it will return an ascii reader.
    If there is an error in creating the file reader the function 
    will return a negative number.

    """
    try:
        file_h = file(file_name, "rb")
    except:
        dev_tool.DEBUGP("[file_reader] Failed to open file %s" % file_name)
        return -1
    try:
        reader = codecs.lookup('utf-8')[2](file_h)
    except:
        dev_tool.DEBUGP('[file_reader] Failed to get UTF-8 Reader')
        reader = file_h
    return reader

def GetFileWriter(file_name):
    """Returns a file stream writer object for reading the
    supplied file name. It returns a utf-8 reader if the host
    system supports it other wise it will return an ascii reader.
    If there is an error in creating the file reader the function 
    will return a negative number.

    """
    try:
        file_h = file(file_name, "wb")
    except:
        dev_tool.DEBUGP("[file_writer] Failed to open file %s" % file_name)
        return -1
    try:
        writer = codecs.lookup('utf-8')[3](file_h)
    except:
        dev_tool.DEBUGP('[file_writer] Failed to get UTF-8 Writer')
        writer = file_h
    return writer

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

def MakeConfigDir(name):
    """Makes a user config direcotry"""
    config_dir = wx.GetHomeDir() + GetPathChar() + u"." + ed_glob.prog_name
    try:
        os.mkdir(config_dir + GetPathChar() + name)
    finally:
        pass

def CreateConfigDir():
    """ Creates the user config directory its default sub 
    directories and any of the default config files.

    """
    #---- Resolve Paths ----#
    config_dir = wx.GetHomeDir() + GetPathChar() + u"." + ed_glob.prog_name
    profile_dir = config_dir + GetPathChar() + u"profiles"
    config_file = ed_glob.CONFIG['PROFILE_DIR'] + u"default.pp"
    loader = ed_glob.CONFIG['PROFILE_DIR'] + u".loader"
    dest_file = profile_dir + GetPathChar() + u"default.pp"
    ext_cfg = ["cache", "styles", "plugins"]

    #---- Create Directories ----#
    if not os.path.exists(config_dir):
        os.mkdir(config_dir)
    if not os.path.exists(profile_dir):
        os.mkdir(profile_dir)
    for cfg in ext_cfg:
        if not HasConfigDir(cfg):
            MakeConfigDir(cfg)

    #---- Copy Default Config Files ----#
    if os.sys.platform == 'win32':
        os.system(u"copy " + u"\"" + config_file + u"\" \"" + dest_file + u"\"")
        os.system(u"copy " + u"\"" + loader + u"\" \"" + profile_dir + 
                  GetPathChar() + u".loader\"")
    else:
        os.system(u"cp " + config_file + " " + dest_file)
        os.system(u"cp " + loader + " " + profile_dir + 
                  GetPathChar() + u".loader")

    ed_glob.PROFILE["MYPROFILE"] = dest_file
    from profiler import UpdateProfileLoader
    UpdateProfileLoader()

def ResolvConfigDir(config_dir, sys_only=False):
    """Checks for a user config directory and if it is not
    found it then resolves the absolute path of the executables 
    directory from the relative execution path. This is then used 
    to find the location of the specified directory as it relates 
    to the executable directory, and returns that path as a
    string.

    """
    if not sys_only:
        # Try to look for a user dir
        user_config = ( wx.GetHomeDir() + GetPathChar() + "." +
                        ed_glob.prog_name + GetPathChar() + config_dir )
        if os.path.exists(user_config):
            return user_config + GetPathChar()

    # The following lines are used only when Editra is installed as a
    # Python Package. If it fails then editra has been installed and is
    # being run in some other manner.
    base = u''
    for key in sys.path_importer_cache:
        if os.path.basename(key) == 'Editra':
            base = key
            break
    if base != u'':
        return os.path.join(base, config_dir) + GetPathChar()

    # If we get here we need to do some platform dependant lookup
    # to find everything. This is probably much more of a mess than
    # need be.
    path = sys.argv[0] #os.path.dirname(os.path.abspath(sys.argv[0]))
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
        pro_path = ( pro_path + path_char + u"Resources" + path_char +
                     config_dir + path_char )
        if not os.path.exists(pro_path):
            # Path failed try looking relative to the src directory setup
            pro_path = pro_path.split(u"Resources")
            pro_path = "".join(pro_path)
    else:
        pro_path = pro_path + path_char + config_dir + path_char
    pro_path = os.path.normpath(pro_path) + path_char
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

def GetResourceFiles(resource, trim=True, get_all=False):
    """Gets a list of resource files from a directory and trims the
    file extentions from the names if trim is set to True (default).
    If the get_all parameter is set to True the function will return
    a set of unique items by looking up both the user and system level
    files and combining them, the default behavior returns the user
    level files if they exist or the system level files if the
    user ones do not exist.

    """
    rec_dir = ResolvConfigDir(resource)
    if get_all:
        rec_dir2 = ResolvConfigDir(resource, True)
    rec_list = list()
    if not os.path.exists(rec_dir):
        return -1
    else:
        recs = os.listdir(rec_dir)
        if get_all and os.path.exists(rec_dir2):
            recs.extend(os.listdir(rec_dir2))
        for rec in recs:
            if os.path.isfile(rec_dir + rec) or \
              (get_all and os.path.isfile(rec_dir2 + rec)):
                if trim:
                    rec = rec.split(u".")[0]
                rec_list.append(rec.title())
        rec_list.sort()
        return list(set(rec_list))

# GUI helper functions
def AdjustColour(color, percent, alpha=wx.ALPHA_OPAQUE):
    """ Brighten/Darken input colour by percent and adjust alpha
    channel if needed. Returns the modified color.

    """ 
    end_color = wx.WHITE
    rd = end_color.Red() - color.Red()
    gd = end_color.Green() - color.Green()
    bd = end_color.Blue() - color.Blue()
    high = 100

    # We take the percent way of the color from color -. white
    r = color.Red() + ((percent*rd*100)/high)/100
    g = color.Green() + ((percent*gd*100)/high)/100
    b = color.Blue() + ((percent*bd*100)/high)/100
    return wx.Colour(r, g, b, alpha)

# String Manupulation/Conversion Utilities
def StrToTuple(tu_str):
    """Takes a tuple of ints that has been converted to a string format and
    reformats it back to a tuple value.

    """
    if tu_str[0] != u"(":
        return ""

    tu_str = tu_str.strip(u'(,)')
    tu_str = tu_str.replace(u',', u'')
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

class IntValidator(wx.PyValidator):
    """A Generic integer validator"""
    def __init__(self, min=0, max=0):
        wx.PyValidator.__init__(self)
        self._min = min
        self._max = max

        # Event managment
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        """Clones the current validator"""
        return IntValidator(self._min, self._max)

    def Validate(self, win):
        """Validate an window value"""
        ctrl = self.GetWindow()
        val = ctrl.GetValue()      
        return val.isdigit()

    def OnChar(self, event):
        """Process values as they are entered into the control"""
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in '0123456789':
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        return
