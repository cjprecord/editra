###############################################################################
# Name: dev_tool.py                                                           #
# Purpose: Provides logging and error tracking utilities                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

""" Editra Development Tools 
@author: Cody Precord
@summary: Utility function for debugging the editor

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

import os
import sys
import platform
import traceback
import codecs
import time
import webbrowser
import wx
import ed_glob

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#
# General Debuging Helper Functions

def DEBUGP(statement, mode="std"):
    """Used to print Debug Statements. Statements should be formated as 
    follows:
    @note: mode variable and message type information in message string are
           not currently used but will be in the future for organizing the
           debug levels.

    1. Formatting
       - [object/module name][msg_type] msg

    2. Modes of operation:
       - std = stdout
       - log = writes to log file
    
    3. Message Type:
       - [err]  : Notes an exception or error condition
       - [warn] : Notes a error that is not severe
       - [info] : General information message
       - [evt]  : Some sort of event related message

    Example: [ed_main][err] File failed to open

    """
    # Turn off normal debugging messages when not in Debug mode
    if mode == "std" and not ed_glob.DEBUG:
        return 0

    # Build time string for tstamp
    now = time.localtime(time.time())
    now = u"[%s:%s:%s]" % (str(now[3]).zfill(2), str(now[4]).zfill(2), 
                           str(now[5]).zfill(2))

    # Format Statement
    statement = unicode(statement)
    s_lst = statement.split(u"\n")
    
    if mode == "std":
        for line in s_lst:
            out = u"%s %s" % (now, line)
            print out.encode('utf-8', 'replace')
    elif mode == "log":
        logfile = os.environ.get('EDITRA_LOG')
        if logfile is None or not os.path.exists(logfile):
            print u"EDITRA_LOG enviroment variable not set!!!"
            print u"Outputting log information to default log editra_tmp.log"
            logfile = 'editra_tmp.log'
        file_handle = file(logfile, mode="ab")
        writer = codecs.lookup('utf-8')[3](file_handle)
        if log_lvl != "none":
            writer.write(u"%s: %s\n" % (log_lvl, statement))
        else:
            writer.write(u"MSG: %s\n" % statement)
        file_handle.close()
    else:
        print u"Improper DEBUG MODE: Defaulting to stdout"
        print statement

def EnvironmentInfo():
    """Returns a string of the systems information
    @return: System information string

    """
    info = list()
    info.append("#---- System Information ----#")
    info.append("%s Version: %s" % (ed_glob.PROG_NAME, ed_glob.VERSION))
    info.append("Operating System: %s" % wx.GetOsDescription())
    if sys.platform == 'darwin':
        info.append("Mac OSX: %s" % platform.mac_ver()[0])
    info.append("Python Version: %s" % sys.version)
    info.append("wxPython Version: %s" % wx.version())
    info.append("wxPython Info: %s" % "\n\t\t".join(wx.PlatformInfo))
    info.append("Python Encoding: Default=%s  File=%s" % \
                (sys.getdefaultencoding(), sys.getfilesystemencoding()))
    info.append("wxPython Encoding: %s" % wx.GetDefaultPyEncoding())
    info.append("System Architecture: %s %s" % (platform.architecture()[0], \
                                                platform.machine()))
    info.append("Byte order: %s" % sys.byteorder)
    info.append("Frozen: %s" % str(getattr(sys, 'frozen', 'False')))
    info.append("#---- End System Information ----#")
    info.append("#---- Runtime Variables ----#")
    from profiler import Profile
    ftypes = list()
    for key, val in Profile().iteritems():
        # Exclude "private" information
        if key.startswith('FILE'):
            continue
        elif key == 'LAST_SESSION' or key == 'FHIST':
            for fname in val:
                if u'.' in fname:
                    ext = fname.split('.')[-1]
                    if ext not in ftypes:
                        ftypes.append(ext)
        else:
            info.append(u"%s=%s" % (key, str(val)))
    info.append(u"FTYPES=%s" % str(ftypes))
    info.append("#---- End Runtime Variables ----#")

    return u"\n".join(info)

def ExceptionHook(exctype, value, trace):
    """Handler for all unhandled exceptions
    @param exctype: Exception Type
    @param value: Error Value
    @param trace: Trace back info

    """
    ftrace = FormatTrace(exctype, value, trace)
    # Ensure that error gets raised to console as well
    print ftrace

    # If abort has been set and we get here again do a more forcefull shutdown
    global ABORT
    if ABORT:
        exit()

    # Prevent multiple reporter dialogs from opening at once
    if not REPORTER_ACTIVE and not ABORT:
        ErrorDialog(ftrace)

def FormatTrace(etype, value, trace):
    """Formats the given traceback
    @return: Formatted string of traceback with attached timestamp

    """
    exc = traceback.format_exception(etype, value, trace)
    exc.insert(0, "*** %s ***%s" % (TimeStamp(), os.linesep))
    return "".join(exc)

def TimeStamp():
    """Create a formatted time stamp of current time
    @return: Time stamp of the current time (Day Month Date HH:MM:SS Year)
    @rtype: string

    """
    now = time.localtime(time.time())
    now = time.asctime(now)
    return now

#-----------------------------------------------------------------------------#

class ErrorReporter(object):
    """Crash/Error Reporter Service
    @summary: Stores all errors caught during the current session and
              is implemented as a singleton so that all errors pushed
              onto it are kept in one central location no matter where
              the object is called from.

    """
    instance = None
    _first = True
    def __init__(self):
        """Initialize the reporter
        @note: The ErrorReporter is a singleton.

        """
        # Ensure init only happens once
        if self._first:
            object.__init__(self)
            self._first = False
            self._sessionerr = list()
        else:
            pass

    def __new__(cls, *args, **kargs):
        """Maintain only a single instance of this object
        @return: instance of this class

        """
        if not cls.instance:
            cls.instance = object.__new__(cls, *args, **kargs)
        return cls.instance

    def AddMessage(self, msg):
        """Adds a message to the reporters list of session errors
        @param msg: The Error Message to save

        """
        if msg not in self._sessionerr:
            self._sessionerr.append(msg)

    def GetErrorStack(self):
        """Returns all the errors caught during this session
        @return: formatted log message of errors

        """
        return "\n\n".join(self._sessionerr)

    def GetLastError(self):
        """Gets the last error from the current session
        @return: Error Message String

        """
        if len(self._sessionerr):
            return self._sessionerr[-1]
        
#-----------------------------------------------------------------------------#

ID_SEND = wx.NewId()
ABORT = False
REPORTER_ACTIVE = False
class ErrorDialog(wx.Dialog):
    """Dialog for showing and and notifying Editra.org should the
    user choose so.

    """
    def __init__(self, message):
        """Initialize the dialog
        @param message: Error message to display

        """
        REPORTER_ACTIVE = True
        wx.Dialog.__init__(self, None, title="Error/Crash Reporter", 
                           style=wx.DEFAULT_DIALOG_STYLE)
        
        # Give message to ErrorReporter
        ErrorReporter().AddMessage(message)

        # Attributes
        self.err_msg = "%s\n\n%s\n%s\n%s" % (EnvironmentInfo(), \
                                             "#---- Traceback Info ----#", \
                                             ErrorReporter().GetErrorStack(), \
                                             "#---- End Traceback Info ----#")
        # Layout
        self._DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Auto show at end of init
        self.CenterOnParent()
        self.ShowModal()

    def _DoLayout(self):
        """Layout the dialog and prepare it to be shown
        @note: Do not call this method in your code

        """
        # Objects
        icon = wx.StaticBitmap(self, 
                               bitmap=wx.ArtProvider.GetBitmap(wx.ART_ERROR))
        mainmsg = wx.StaticText(self, 
                                label=_("Error: Oh no something bad happend\n"
                                        "Help improve Editra by clicking on "
                                        "Report Error\nto send the Error "
                                        "Traceback shown below."))
        t_lbl = wx.StaticText(self, label=_("Error Traceback:"))
        tctrl = wx.TextCtrl(self, value=self.err_msg, style=wx.TE_MULTILINE | 
                                                            wx.TE_READONLY)
        abort_b = wx.Button(self, wx.ID_ABORT, _("Abort"))
        send_b = wx.Button(self, ID_SEND, _("Report Error"))
        send_b.SetDefault()
        close_b = wx.Button(self, wx.ID_CLOSE)

        # Layout
        sizer = wx.GridBagSizer()
        sizer.AddMany([(icon, (1, 1)), (mainmsg, (1, 2), (1, 2)), 
                       ((2, 2), (3, 0)), (t_lbl, (3, 1), (1, 2)),
                       (tctrl, (4, 1), (8, 5), wx.EXPAND), ((5, 5), (4, 6)),
                       ((2, 2), (12, 0)),
                       (abort_b, (13, 1), (1, 1), wx.ALIGN_LEFT),
                       (send_b, (13, 3), (1, 2), wx.ALIGN_RIGHT),
                       (close_b, (13, 5), (1, 1), wx.ALIGN_RIGHT),
                       ((2, 2), (14, 0))])
        self.SetSizer(sizer)
        self.SetInitialSize()

    def OnButton(self, evt):
        """Handles button events
        @param evt: event that called this handler
        @postcondition: Dialog is closed
        @postcondition: If Report Event then email program is opened

        """
        e_id = evt.GetId()
        if e_id == wx.ID_CLOSE:
            self.Close()
        elif e_id == ID_SEND:
            msg = u"mailto:%s?subject=Error Report&body=%s"
            addr = u"bugs@%s" % (ed_glob.HOME_PAGE.lstrip("http://"))
            msg = msg % (addr, self.err_msg)
            msg = msg.replace(u"'", u'')
            webbrowser.open(msg)
            self.Close()
        elif e_id == wx.ID_ABORT:
            global ABORT
            ABORT = True
            # Try a nice shutdown first time through
            wx.CallLater(500, wx.GetApp().OnExit, 
                         wx.MenuEvent(wx.wxEVT_MENU_OPEN, ed_glob.ID_EXIT),
                         True)
            self.Close()
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Cleans up the dialog when it is closed
        @param evt: Event that called this handler

        """
        REPORTER_ACTIVE = False
        self.Destroy()
        evt.Skip()
