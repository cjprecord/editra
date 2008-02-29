###############################################################################
# Name: util.py                                                               #
# Purpose: Misc utility functions used through out Editra                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

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

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import shutil
import stat
import codecs
import mimetypes
import wx
import ed_event
import ed_glob
from syntax.syntax import GetFileExtensions
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class DropTargetFT(wx.PyDropTarget):
    """Drop target capable of accepting dropped files and text
    @todo: has some issues with the clipboard on windows under certain
           conditions. They arent fatal but need fixing.

    """
    def __init__(self, window, textcallback=None, filecallback=None):
        """Initializes the Drop target
        @param window: window to recieve drop objects

        """
        wx.PyDropTarget.__init__(self)
        self.window = window
        self.data = None
        self.file_data_obj = None
        self.text_data_obj = None
        self._tmp = None
        self._lastp = None
        self._tcallb = textcallback
        self._fcallb = filecallback
        self.InitObjects()

    def CreateDragString(self, txt):
        """Creates a bitmap of the text that is being dragged
        @todo: possibly set colors to match highlighting of text
        @todo: generalize this to be usable by other widgets besides stc

        """
        if not issubclass(self.window.__class__, wx.stc.StyledTextCtrl):
            return
        stc = self.window
        txt = txt.split(stc.GetEOLChar())
        longest = (0, 0)
        for line in txt:
            ext = stc.GetTextExtent(line)
            if ext[0] > longest[0]:
                longest = ext
        cords = list()
        for x in xrange(len(txt)):
            cords.append((0, x * longest[1]))
        mdc = wx.MemoryDC(wx.EmptyBitmap(longest[0] + 5, 
                                         longest[1] * len(txt)))
        mdc.SetTextForeground(stc.GetDefaultForeColour())
        mdc.SetFont(stc.GetDefaultFont())
        mdc.DrawTextList(txt, cords)
        self._tmp = wx.DragImage(mdc.GetAsBitmap())

    def InitObjects(self):
        """Initializes the text and file data objects
        @postcondition: all data objects are initialized

        """
        self.data = wx.DataObjectComposite()
        self.text_data_obj = wx.TextDataObject()
        self.file_data_obj = wx.FileDataObject()
        self.data.Add(self.text_data_obj, True)
        self.data.Add(self.file_data_obj, False)
        self.SetDataObject(self.data)

    def OnEnter(self, x_cord, y_cord, drag_result):
        """Called when a drag starts
        @return: result of drop object entering window

        """
        try:
            if self.GetData():
                files = self.file_data_obj.GetFilenames()
                text = self.text_data_obj.GetText()
            else:
                return drag_result
        except wx.PyAssertionError:
            return wx.DragError

        self._lastp = (x_cord, y_cord)
        if len(files):
            self.window.SetCursor(wx.StockCursor(wx.CURSOR_COPY_ARROW))
        else:
            self.CreateDragString(text)
        return drag_result

    def OnDrop(self, x_cord=0, y_cord=0):
        """Gets the drop cords
        @keyword x: x cord of drop object
        @keyword y: y cord of drop object
        @todo: implement snapback when drop is out of range

        """
        self._tmp = None
        self._lastp = None
        return True

    def OnDragOver(self, x_cord, y_cord, drag_result):
        """Called when the cursor is moved during a drag action
        @return: result of drag over
        @todo: For some reason the carrat postion changes which can be seen
               by the brackets getting highlighted. However the actual carrat
               is not moved.

        """
        if self._tmp is None:
            return drag_result
        else:
            stc = self.window
            point = wx.Point(x_cord, y_cord)
            self._tmp.BeginDrag(point - self._lastp, stc)
            self._tmp.Hide()
            stc.GotoPos(stc.PositionFromPoint(point))
            stc.Refresh()
            stc.Update()
            self._tmp.Move(point)
            self._tmp.Show()
            self._tmp.RedrawImage(self._lastp, point, True, True)
            self._lastp = point
            return drag_result

    def OnData(self, x_cord, y_cord, drag_result):
        """Gets and processes the dropped data
        @postcondition: dropped data is processed

        """
        self.window.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        try:
            data = self.GetData()
        except wx.PyAssertionError:
            wx.PostEvent(self.window.GetTopLevelParent(), \
                        ed_event.StatusEvent(ed_event.edEVT_STATUS, -1,
                                             _("Unable to open dropped file or "
                                               "text")))
            data = False
            drag_result = wx.DragError

        if data:
            files = self.file_data_obj.GetFilenames()
            text = self.text_data_obj.GetText()
            if len(files) > 0 and self._fcallb is not None:
                self._fcallb(files)
            elif(len(text) > 0):
                if SetClipboardText(text):
                    win = self.window
                    pos = win.PositionFromPointClose(x_cord, y_cord)
                    if pos != wx.stc.STC_INVALID_POSITION:
                        win.SetSelection(pos, pos)
                        win.Paste()
        self.InitObjects()
        return drag_result

    def OnLeave(self):
        """Handles the event of when the drag object leaves the window
        @postcondition: Cursor is set back to normal state

        """
        self.window.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        if self._tmp is not None:
            self._tmp.EndDrag()

#---- End FileDropTarget ----#

#---- Misc Common Function Library ----#
def SetClipboardText(txt):
    """Copies text to the clipboard
    @param txt: text to put in clipboard

    """
    data_o = wx.TextDataObject()
    data_o.SetText(txt)
    if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(data_o)
        wx.TheClipboard.Close()
        return 1
    return 0

# File Helper Functions
BOM = { 'utf-8' : codecs.BOM_UTF8,
        'utf-16-be' : codecs.BOM_UTF16_BE,
        'utf-16-le' : codecs.BOM_UTF16_LE,
        'utf-7' : '+\v8-',
        'latin-1' : '',
        'ascii' : '' }

# When no BOM is present this determines decode test order
ENC = [ 'utf-8', 'utf-7', 'latin-1', 'utf-16-be', 'utf-16-le', 'ascii']
  #      'utf-32-be', 'utf-32-le', 

def DecodeString(str2decode):
    """Decode a given string if possible and return that string
    @param str2decode: the string to decode

    """
    decoded = str2decode
    for enc in ENC:
        try:
            decoded = str2decode.decode(enc)
        except (UnicodeDecodeError, UnicodeWarning):
            continue
        else:
            break

    return decoded

def GetDecodedText(fname):
    """Gets the text from a file and decodes the text using
    a compatible decoder. Returns a tuple of the text and the
    encoding it was decoded from.
    @param fname: name of file to open and get text from
    @return: tuple of (text, encoding string)

    """
    try:
        f_handle = file(fname, 'rb')
        txt = f_handle.read()
        f_handle.close()
    except IOError, msg:
        raise IOError, msg
    except OSError, msg:
        raise OSError, msg
    else:
        decoded = None

        # First look for a bom byte
        bbyte = None
        for e, b in BOM.iteritems():
            if txt.startswith(b) and e not in ['ascii', 'latin-1']:
                bbyte = e

        tenc = ENC
        if bbyte:
            if bbyte in tenc:
                tenc.remove(bbyte)
            tenc.insert(0, bbyte)

        for enc in ENC:
            try:
                decoded = txt.decode(enc)
            except (UnicodeDecodeError, UnicodeWarning):
                continue
            else:
                break

        if 'enc' not in locals():
            enc = u''
        if decoded:
            dev_tool.DEBUGP("[txtdecoder] Decoded text as %s" % enc)
            return decoded, enc
        else:
            dev_tool.DEBUGP("[txtdecoder][err] Decode Failed")
            return txt, enc

def FilterFiles(file_list):
    """Filters a list of paths and returns a list of paths
    that are valid, not directories, and not seemingly not binary.
    @param file_list: list of files/folders to filter for good files in
    @todo: find a better way to check for files that can be opened

    """
    good = list()
    for path in file_list:
        if not os.path.exists(path) or os.path.isdir(path):
            continue
        else:
            # Check for binary files
            # 1. Keep all files types we know about and all that have a mime
            #    type of text.
            mime = mimetypes.guess_type(path)
            if GetExtension(path) in GetFileExtensions() or \
               (mime[0] and u'text' in mime[0]):
                good.append(path)
            # 2. Throw out common filetypes we cant open...HACK
            elif GetExtension(path).lower() in ['gz', 'tar', 'bz2', 'zip',
                                                'rar', 'ace', 'png', 'jpg', 
                                                'gif', 'jpeg', 'exe', 'pyc',
                                                'pyo', 'psd']:
                continue
            # 3. Try to judge if we can open the file or not by sampling
            #    some of the data, if 10% of the data is bad, drop the file.
            else:
                try:
                    fhandle = file(path, "rb")
                    tmp = fhandle.read(1500)
                    fhandle.close()
                except IOError:
                    continue
                bad = 0
                for bit in xrange(len(tmp)):
                    val = ord(tmp[bit])
                    if (val < 8) or (val > 13 and val < 32) or (val > 255):
                        bad = bad + 1
                if not len(tmp) or (float(bad)/float(len(tmp))) < 0.1:
                    good.append(path)
    return good

def GetFileModTime(file_name):
    """Returns the time that the given file was last modified on
    @param file_name: path of file to get mtime of

    """
    try:
        mod_time = os.path.getmtime(file_name)
    except EnvironmentError:
        mod_time = 0
    return mod_time

def GetFileReader(file_name, enc='utf-8'):
    """Returns a file stream reader object for reading the
    supplied file name. It returns a file reader using the encoding
    (enc) which defaults to utf-8. If lookup of the reader fails on
    the host system it will return an ascii reader.
    If there is an error in creating the file reader the function 
    will return a negative number.
    @param file_name: name of file to get a reader for
    @keyword enc: encoding to use for reading the file
    @return file reader, or int if error.

    """
    try:
        file_h = file(file_name, "rb")
    except (IOError, OSError):
        dev_tool.DEBUGP("[file_reader] Failed to open file %s" % file_name)
        return -1
    try:
        reader = codecs.lookup(enc)[2](file_h)
    except (LookupError, IndexError):
        dev_tool.DEBUGP('[file_reader] Failed to get %s Reader' % enc)
        reader = file_h
    return reader

def GetFileWriter(file_name, enc='utf-8'):
    """Returns a file stream writer object for reading the
    supplied file name. It returns a file writer in the supplied
    encoding if the host system supports it other wise it will return 
    an ascii reader. The default will try and return a utf-8 reader.
    If there is an error in creating the file reader the function 
    will return a negative number.
    @param file_name: path of file to get writer for
    @keyword enc: encoding to write text to file with

    """
    try:
        file_h = file(file_name, "wb")
    except IOError:
        dev_tool.DEBUGP("[file_writer] Failed to open file %s" % file_name)
        return -1
    try:
        writer = codecs.lookup(enc)[3](file_h)
    except (LookupError, IndexError):
        dev_tool.DEBUGP('[file_writer] Failed to get %s Writer' % enc)
        writer = file_h
    return writer

def GetPathChar():
    """Returns the path character for the OS running the program
    @return: character used as file path separator
    """
    if wx.Platform == '__WXMSW__':
        return u"\\"
    else:
        return u"/"

def GetUniqueName(path, name):
    """Make a file name that will be unique in case a file of the
    same name already exists at that path.
    @param path: Root path to download folder
    @param name: desired file name base
    @return: string

    """
    tmpname = os.path.join(path, name)
    if os.path.exists(tmpname):
        ext = name.split('.')[-1]
        fbase = name[:-1 * len(ext) - 1]
        inc = len([x for x in os.listdir(path) if x.startswith(fbase)])
        tmpname = os.path.join(path, "%s-%d.%s" % (fbase, inc, ext))
        while os.path.exists(tmpname):
            inc = inc + 1
            tmpname = os.path.join(path, "%s-%d.%s" % (fbase, inc, ext))

    return tmpname

def GetPathName(path):
    """Gets the path minus filename
    @param path: full path to get base of

    """
    pieces = os.path.split(path)
    return pieces[0]

def GetFileName(path):
    """Gets last atom on end of string as filename
    @param path: full path to get filename from

    """
    pieces = os.path.split(path)
    filename = pieces[-1]
    return filename

def GetExtension(file_str):
    """Gets last atom at end of string as extension if 
    no extension whole string is returned
    @param file_str: path or file name to get extension from

    """
    pieces = file_str.split('.')
    extension = pieces[-1]
    return extension

def GetIds(obj_lst):
    """Gets a list of IDs from a list of objects
    @param obj_lst: list of objects to get ids from
    @return: list of ids
    @note: I believe this is no longer used anywhere and may be removed soon

    """
    return [obj.GetId() for obj in obj_lst]

def ResolvAbsPath(rel_path):
    """Takes a relative path and converts it to an
    absolute path.
    @param rel_path: path to construct absolute path for

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

def HasConfigDir(loc=u""):
    """ Checks if the user has a config directory and returns True 
    if the config directory exists or False if it does not.
    @return: whether config dir in question exists on an expected path

    """
    pchar = GetPathChar()
    if os.path.exists(u"%s%s.%s%s%s" % (wx.GetHomeDir(), pchar,
                                        ed_glob.PROG_NAME, pchar, loc)):
        return True
    else:
        return False

def MakeConfigDir(name):
    """Makes a user config direcotry
    @param name: name of config directory to make in user config dir

    """
    config_dir = wx.GetHomeDir() + GetPathChar() + u"." + ed_glob.PROG_NAME
    try:
        os.mkdir(config_dir + GetPathChar() + name)
    finally:
        pass

def CreateConfigDir():
    """ Creates the user config directory its default sub 
    directories and any of the default config files.
    @postcondition: all default configuration files/folders are created

    """
    #---- Resolve Paths ----#
    pchar = GetPathChar()
    prof_dir = ed_glob.CONFIG['PROFILE_DIR']
    config_dir = u"%s%s.%s" % (wx.GetHomeDir(), pchar, ed_glob.PROG_NAME)
    profile_dir = u"%s%sprofiles" % (config_dir, pchar)
    config_file = u"%sdefault.ppb" % prof_dir
    loader =  u"%s.loader2" % prof_dir
    dest_file = u"%s%sdefault.ppb" % (profile_dir, pchar)
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
    shutil.copyfile(config_file, dest_file)
    shutil.copyfile(loader, profile_dir + pchar + u".loader2")

    import profiler
    profiler.Profile().Load(dest_file)
    profiler.Profile_Set("MYPROFILE", dest_file)
    profiler.UpdateProfileLoader()

def ResolvConfigDir(config_dir, sys_only=False):
    """Checks for a user config directory and if it is not
    found it then resolves the absolute path of the executables 
    directory from the relative execution path. This is then used 
    to find the location of the specified directory as it relates 
    to the executable directory, and returns that path as a
    string.
    @param config_dir: name of config directory to resolve
    @keyword sys_only: only get paths of system config directory or user one

    """
    path_char = GetPathChar()
    if not sys_only:
        # Try to look for a user dir
        user_config = u"%s%s.%s%s%s" % (wx.GetHomeDir(), path_char,
                                        ed_glob.PROG_NAME, path_char, 
                                        config_dir)
        if os.path.exists(user_config):
            return user_config + path_char

    # The following lines are used only when Editra is being run as a
    # source package. If the found path does not exist then Editra is
    # running as as a built package.
    path = __file__
    path = path_char.join(path.split(path_char)[:-2])
    path =  path + path_char + config_dir + path_char
    if os.path.exists(path):
        return path

    # If we get here we need to do some platform dependant lookup
    # to find everything. This is probably much more of a mess than
    # need be.
    path = sys.argv[0]

    # If it is a link get the real path
    if os.path.islink(path):
        path = os.path.realpath(path)

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
            if pieces[-1] not in [ed_glob.PROG_NAME.lower(), ed_glob.PROG_NAME]:
                pro_path = path_char.join(pieces[:-1])
        else:
            pro_path = ResolvAbsPath(pro_path)

    if os.sys.platform == "darwin":
        # On OS X the config directories are in the applet under Resources
        pro_path = u"%s%sResources%s%s%s" % (pro_path, path_char, path_char,
                                             config_dir, path_char)
    else:
        pro_path = pro_path + path_char + config_dir + path_char
    pro_path = os.path.normpath(pro_path) + path_char
    return pro_path

def GetResources(resource):
    """Returns a list of resource directories from a given toplevel config dir
    @param resource: config directory name
    @return: list of resource directory that exist under the given resource path

    """
    rec_dir = ResolvConfigDir(resource)
    rec_lst = []
    if os.path.exists(rec_dir):
        recs = os.listdir(rec_dir)
        for rec in recs:
            if os.path.isdir(rec_dir + rec) and rec[0] != u".":
                rec_lst.append(rec.title())
        return rec_lst
    else:
        return -1

def GetResourceFiles(resource, trim=True, get_all=False):
    """Gets a list of resource files from a directory and trims the
    file extentions from the names if trim is set to True (default).
    If the get_all parameter is set to True the function will return
    a set of unique items by looking up both the user and system level
    files and combining them, the default behavior returns the user
    level files if they exist or the system level files if the
    user ones do not exist.
    @param resource: name of config directory
    @keyword trim: trim file extensions or not
    @keyword get_all: get a set of both system/user files or just user level
    

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

def Log(msg):
    """Push the message to the apps log
    @param msg: message string to log

    """
    wx.GetApp().GetLog()(msg)

# GUI helper functions
def AdjustColour(color, percent, alpha=wx.ALPHA_OPAQUE):
    """ Brighten/Darken input colour by percent and adjust alpha
    channel if needed. Returns the modified color.
    @param color: color object to adjust
    @type color: wx.Color
    @param percent: percent to adjust +(brighten) or -(darken)
    @type percent: int
    @keyword alpha: amount to adjust alpha channel

    """ 
    end_color = wx.WHITE
    rdif = end_color.Red() - color.Red()
    gdif = end_color.Green() - color.Green()
    bdif = end_color.Blue() - color.Blue()
    high = 100

    # We take the percent way of the color from color -. white
    red = color.Red() + ((percent * rdif) / high)
    green = color.Green() + ((percent * gdif) / high)
    blue = color.Blue() + ((percent * bdif) / high)
    return wx.Colour(max(red, 0), max(green, 0), max(blue, 0), alpha)

def HexToRGB(hex_str):
    """Returns a list of red/green/blue values from a
    hex string.
    @param hex_str: hex string to convert to rgb
    
    """
    hexval = hex_str
    if hexval[0] == u"#":
        hexval = hexval[1:]
    ldiff = 6 - len(hexval)
    hexval += ldiff * u"0"
    # Convert hex values to integer
    red = int(hexval[0:2], 16)
    green = int(hexval[2:4], 16)
    blue = int(hexval[4:], 16)
    return [red, green, blue]

def SetWindowIcon(window):
    """Sets the given windows icon to be the programs
    application icon.
    @param window: window to set app icon for

    """
    try:
        if wx.Platform == "__WXMSW__":
            ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.ico"
            window.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_ICO))
        else:
            ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.png"
            window.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_PNG))
    finally:
        pass

# String Manupulation/Conversion Utilities
def StrToTuple(tu_str):
    """Takes a tuple of ints that has been converted to a string format and
    reformats it back to a tuple value.
    @param tu_str: a string of a tuple of ints i.e '(1, 4)'
    @return: string turned into the tuple it represents

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
    def __init__(self, min_=0, max_=0):
        """Initialize the validator
        @keyword min: min value to accept
        @keyword max: max value to accept

        """
        wx.PyValidator.__init__(self)
        self._min = min_
        self._max = max_

        # Event managment
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        """Clones the current validator
        @return: clone of this object

        """
        return IntValidator(self._min, self._max)

    def Validate(self, win):
        """Validate an window value
        @param win: window to validate

        """
        ctrl = self.GetWindow()
        val = ctrl.GetValue()      
        return val.isdigit()

    def OnChar(self, event):
        """Process values as they are entered into the control
        @param event: event that called this handler

        """
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
