###############################################################################
# Name: profiler.py                                                           #
# Purpose: Editra's user profile services                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: profiler.py                                                        #
# LANGUAGE: Python                                                         #
#                                                                          #
# @summary:                                                                #
# This module provides the profile object and support functions for        #
# loading and saving user preferences between sessions. The preferences are#
# saved on disk as a cPickle, because of this no objects that cannot be    #
# resolved in the namespace of this module prior to starting the mainloop  #
# must not be put in the Profile as it will cause errors on load. Ths means#
# that only builtin python types should be used and that a translation from#
# that type to the required type should happen during run time.            #
#                                                                          #
# METHODS:                                                                 #
# UpdateProfileLoader: Updates loader after changes to profile	           #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import cPickle
import wx
from ed_glob import CONFIG, PROG_NAME, VERSION
import util
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
# Globals
_DEFAULTS = {
           'ALPHA'      : 255,              # Transparency level
           'AALIASING'  : False,            # Use Anti-Aliasing if availble
           'APPSPLASH'  : True,             # Show splash at startup
           'AUTO_COMP'  : True,             # Use Auto-comp if available
           'AUTO_INDENT': True,             # Use Auto Indent
           'BRACKETHL'  : True,             # Use bracket highlighting
           'CHECKMOD'   : True,             # Auto check file for file mod
           'CODE_FOLD'  : True,             # Use code folding
           'DEFAULT'    : False,            # No longer used I believe
           'DEFAULT_VIEW' : 'Default',      # Default Perspective
           'EDGE'       : 80,               # Edge guide column
           'EOL'        : 'Unix (\\n)',     # EOL mode
           'FHIST'      : list(),           # List of history files
           'FHIST_LVL'  : 9,                # Filehistory length (9 is max)
           'FFILTER'    : 0,                # Last file filter used
           'GUIDES'     : True,             # Use Indentation guides
           'ICONS'      : 'Tango',          # Icon Theme
           'ICON_SZ'    : (24, 24),         # Toolbar Icon Size
           'LANG'       : 'Default',        # UI language
           'MODE'       : 'CODE',           # Overall editor mode
           'MYPROFILE'  : 'default.ppb',    # Path to profile file
           'OPEN_NW'    : False,            # Open files in new windows
           'PRINT_MODE' : 'BLACK/WHITE',    # Printer rendering mode
           'REPORTER'   : True,             # Error Reporter is Active
           'SAVE_POS'   : True,             # Remember Carat positions
           'SAVE_SESSION' : False,          # Load previous session on startup
           'SET_WPOS'   : True,             # Remember window position
           'SET_WSIZE'  : True,             # Remember mainwindow size on exit
           'SHOW_EDGE'  : True,             # Show Edge Guide
           'SHOW_EOL'   : False,            # Show EOL markers
           'SHOW_LN'    : True,             # Show Line Numbers
           'SHOW_WS'    : False,            # Show whitespace markers
           'SYNTAX'     : True,             # Use Syntax Highlighting
           'SYNTHEME'   : 'Default',        # Syntax Highlight color scheme
           'TABWIDTH'   : 8,                # Tab width
           'THEME'      : 'DEFAULT',        # For future use
           'TOOLBAR'    : True,             # Show Toolbar
           'USETABS'    : True,             # Use tabs instead of spaces
           'VI_EMU'     : False,            # Use Vi emulation mode 
           'WRAP'       : False,             # Use Wordwrap
           'WSIZE'      : (700, 450)        # Mainwindow size
          #FONT1 created at runtime by ed_styles as primary font           
          #FONT2 created at runtime by ed_styles as secondary font
}

#--------------------------------------------------------------------------#

class Profile(dict):
    """Class for managing profile data. All data is stored as builtin
    python objects (i.e. str, tuple, list, ect...) however on a request
    for data the object can be transformed in to a requested type where
    applicable. The profile saves itself to disk using the cPickle module
    to preserve data types and allow for easy loading.

    """
    _instance = None
    _created = False
    
    def __init__(self):
        """Initialize the profile"""
        if not self._created:
            dict.__init__(self)
        else:
            pass

    def __new__(cls, *args, **kargs):
        """Maintain only a single instance of this object
        @return: instance of this class

        """
        if cls._instance is None:
            cls._instance = dict.__new__(cls, *args, **kargs)
        return cls._instance

    #---- End Private Members ----#

    #---- Protected Members ----#

    #---- Begin Public Members ----#
    def DeleteItem(self, item):
        """Removes an entry from the profile
        
        @param item: items name
        @type item: string

        """
        if self.has_key(item):
            del self[item]
        else:
            pass

    def Get(self, index, fmt=None, default=None):
        """Gets the specified item from the data set
        
        @param index: index of item to get
        @keyword fmt: format the item should be in
        @keyword default: Default value to return if index is
                          not in profile.

        """
        if self.has_key(index):
            val = self.__getitem__(index)
        else:
            return default

        if fmt is None:
            return val
        else:
            return _ToObject(index, val, fmt)

    def Load(self, path):
        """Load the profiles data set with data from the given file
        @param path: path to file to load data from
        @note: The files data must have been written with a pickler

        """
        if os.path.exists(path):
            try:
                fhandle = open(path, 'rb')
                val = cPickle.load(fhandle)
                fhandle.close()
            except (IOError, SystemError, OSError, 
                    cPickle.UnpicklingError), msg:
                dev_tool.DEBUGP("[profile][err] %s" % str(msg))
            else:
                if isinstance(val, dict):
                    self.update(val)
                    self.Set('MYPROFILE', path)
                    dev_tool.DEBUGP("[profile][info] Loaded %s" % path)
        else:
            dev_tool.DEBUGP("[profile][err] %s does not exist" % path)
            dev_tool.DEBUGP("[profile][info] Loading defaults")
            self.LoadDefaults()
            self.Set('MYPROFILE', path)
            return False

        # Update profile to any keys that are missing
        for key in _DEFAULTS:
            if key not in self:
                self.Set(key, _DEFAULTS[key])
        return True

    def LoadDefaults(self):
        """Loads the default values into the profile
        @return: None

        """
        self.clear()
        self.update(_DEFAULTS)

    def Set(self, index, val, fmt=None):
        """Set the value of the given index
        @param index: Index to set
        @param val: Value to set
        @keyword fmt: Format to convert to string from

        """
        if fmt is None:
            self.__setitem__(index, val)
        else:
            tmp = _FromObject(val, fmt)
            self.__setitem__(index, tmp)

    def Write(self, path):
        """Write the dataset of this profile as a pickle
        @param path: path to where to write the pickle
        @return: True on success/ False on failure

        """
        try:
            self.Set('MYPROFILE', path)
            fhandle = open(path, 'wb')
            cPickle.dump(self, fhandle, cPickle.HIGHEST_PROTOCOL)
            fhandle.close()
            UpdateProfileLoader()
        except (IOError, cPickle.PickleError), msg:
            dev_tool.DEBUGP("[profile][err] %s" % str(msg))
            return False
        else:
            return True

    #---- End Public Members ----#

# Profile convinience functions
def Profile_Del(item):
    """Removes an item from the profile
    
    @param item: items name

    """
    Profile().DeleteItem(item)

def Profile_Get(index, fmt=None, default=None):
    """Convinience for Profile().Get()
    @param index: profile index to retrieve
    @keyword fmt: format to get value as
    @keyword default: default value to return if not found

    """
    return Profile().Get(index, fmt, default)

def Profile_Set(index, val, fmt=None):
    """Convinience for Profile().Set()
    @param index: profile index to set
    @param val: value to set index to
    @keyword fmt: format to convert object from

    """
    return Profile().Set(index, val, fmt)

def _FromObject(val, fmt):
    """Convert the given value to a to a profile compatible value
    @param val: value to convert
    @param fmt: Format to convert to
    @type fmt: string

    """
    if fmt == u'font' and isinstance(val, wx.Font):
        return "%s,%s" % (val.GetFaceName(), val.GetPointSize())
    else:
        return val

def _ToObject(index, val, fmt):
    """Convert the given value to a different object
    @param index: fallback to retrieve item from defaults
    @param val: value to convert
    @param fmt: Format to convert to
    @type fmt: string
    @todo: exception handling, 

    """
    if not isinstance(fmt, basestring):
        raise TypeError, "_ToObject expects a string for parameter 2"
    else:
        tmp = fmt.lower()
        if tmp == u'font':
            fnt = val.split(',')
            rval = wx.FFont(int(fnt[1]), wx.DEFAULT, face=fnt[0])
        elif tmp == u'bool':
            if isinstance(val, bool):
                rval = val
            else:
                rval = _DEFAULTS.get(index, False)
        elif tmp == u'size_tuple':
            if len(val) == 2 and \
               isinstance(val[0], int) and isinstance(val[1], int):
                rval = val
            else:
                rval = _DEFAULTS.get(index, wx.DefaultSize)
        elif tmp == u'str':
            rval = unicode(val)
        elif tmp == u'int':
            if isinstance(val, int):
                rval = val
            elif isinstance(val, basestring) and val.isdigit():
                rval = int(val)
            else:
                rval = _DEFAULTS.get(index)
        else:
            return val
        return rval

#---- Begin Function Definitions ----#
def AddFileHistoryToProfile(file_history):
    """Manages work of adding a file from the profile in order
    to allow the top files from the history to be available 
    the next time the user opens the program.
    @param file_history: add saved files to history list

    """
    files = list()
    for fnum in xrange(file_history.GetNoHistoryFiles()):
        files.append(file_history.GetHistoryFile(fnum))
    Profile_Set('FHIST', files)

def CalcVersionValue(ver_str="0.0.0"):
    """Calculates a version value from the provided dot-formated string

    1) SPECIFICATION: Version value calculation AA.BBB.CCC
         - major values: < 1     (i.e 0.0.85 = 0.850)
         - minor values: 1 - 999 (i.e 0.1.85 = 1.850)
         - micro values: >= 1000 (i.e 1.1.85 = 1001.850)

    """
    ver_lvl = ver_str.split(u".")
    if len(ver_lvl) < 3:
        return 0
    major = int(ver_lvl[0]) * 1000
    minor = int(ver_lvl[1])
    if len(ver_lvl[2]) <= 2:
        ver_lvl[2] += u'0'
    micro = float(ver_lvl[2]) / 1000
    return float(major) + float(minor) + micro

def GetLoader():
    """Finds the loader to use"""
    user_home = wx.GetHomeDir() + util.GetPathChar()
    rel_prof_path = ("." + PROG_NAME + util.GetPathChar() + 
                     "profiles" + util.GetPathChar() + ".loader2")

    if os.path.exists(user_home + rel_prof_path):
        loader = user_home + rel_prof_path
    else:
        loader = CONFIG['PROFILE_DIR'] + ".loader2"

    return loader

def GetProfileStr():
    """Reads the profile string from the loader and returns it.
    The profile string must be the first line in the loader file.
    @return: path of profile used in last session

    """
    reader = util.GetFileReader(GetLoader())
    if reader == -1:
        # So return the default
        return CONFIG['PROFILE_DIR'] + u"default.ppb"

    profile = reader.readline()
    profile = profile.split("\n")[0] # strip newline from end
    reader.close()
    return profile

def ProfileIsCurrent():
    """Checks if profile is compatible with current editor version
    and returns a bool stating if it is or not.
    @return: whether profile on disk was written with current program version

    """
    if CalcVersionValue(ProfileVersionStr()) >= CalcVersionValue(VERSION):
        return True
    else:
        return False

def ProfileVersionStr():
    """Checks the Loader for the profile version string and
    returns the version string. If there is an error or the
    string is not found it returns a zero version string.
    @return: the version string value from the profile loader file

    """
    loader = GetLoader()
    reader = util.GetFileReader(loader)
    if reader == -1:
        return "0.0.0"

    ret_val = "0.0.0"
    count = 0
    while True:
        count += 1
        value = reader.readline()
        value = value.split()
        if len(value) > 0:
            if value[0] == u'VERSION':
                ret_val = value[1]
                break
        # Give up after 20 lines if version string not found
        if count > 20:
            break
    reader.close()

    return ret_val

def UpdateProfileLoader():
    """Updates Loader File
    @postcondition: on disk profile loader is updated
    @return: 0 if no error, non zero for error condition

    """
    writer = util.GetFileWriter(GetLoader())
    if writer == -1:
        return 1

    prof_name = Profile_Get('MYPROFILE')
    if not prof_name:
        prof_name = CONFIG['PROFILE_DIR'] + 'default.ppb'

    prof_name = prof_name.encode(sys.getfilesystemencoding())
    writer.write(prof_name)
    writer.write(u"\nVERSION\t" + VERSION)
    writer.close()
    return 0

