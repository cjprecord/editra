############################################################################
#    Copyright (C) 2007 by Cody Precord                                    #
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

""" Development Tools 
@author: Cody Precord
@summary: Utility function for debugging the editor

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

import os
import sys
import traceback
import codecs
import time
import webbrowser
import wx
import ed_glob

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#
# General Debuging Helper Functions

def DEBUGP(statement, mode="std", log_lvl="none"):
    """Used to print Debug Statements
    1. Modes of operation:
       - std = stdout
       - log = writes to log file
    
    2. Log Levels:
       - none = used with stdout
       - INFO = Basic Information
       - WARN = Could be a potential problem
       - ERROR = Serious problem has occured
       
    """
    # Turn off normal debugging messages when not in Debug mode
    if mode == "std" and not 'DEBUG' in ed_glob.PROFILE['MODE']:
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
        return 0
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
        return 0	
    else:
        print u"Improper DEBUG MODE: Defaulting to stdout"
        print statement
        return 1

def EnvironmentInfo():
    """Returns a string of the systems information
    @return: System information string

    """
    info = list()
    info.append("#---- System Information ----#")
    info.append("%s Version: %s" % (ed_glob.prog_name, ed_glob.version))
    info.append("Operating System: %s" % wx.GetOsDescription())
    info.append("Python Version: %s" % sys.version)
    info.append("wxPython Version: %s" % wx.version())
    info.append("wxPython Info: %s" % "\n\t\t\t".join(wx.PlatformInfo))
    info.append("Python Encoding: Default=%s  File=%s" % \
                (sys.getdefaultencoding(), sys.getfilesystemencoding()))
    info.append("wxPython Encoding: %s" % wx.GetDefaultPyEncoding())
    info.append("Frozen: %s" % str(hasattr(sys, 'frozen')))
    info.append("#---- End System Information ----#")
    return "\n".join(info)

def ExceptionHook(exctype, value, trace):
    """Handler for all unhandled exceptions
    @param exctype: Exception Type
    @param value: Error Value
    @param trace: Trace back info

    """
    ftrace = FormatTrace(exctype, value, trace)
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
class ErrorDialog(wx.Dialog):
    """Dialog for showing and and notifying Editra.org should the
    user choose so.

    """
    def __init__(self, message):
        """Initialize the dialog
        @param message: Error message to display

        """
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
        send_b = wx.Button(self, ID_SEND, _("Report Error"))
        send_b.SetDefault()
        close_b = wx.Button(self, wx.ID_CLOSE)

        # Layout
        sizer = wx.GridBagSizer()
        sizer.AddMany([(icon, (1, 1)), (mainmsg, (1, 2), (1, 2)), 
                       ((2, 2), (3, 0)), (t_lbl, (3, 1), (1, 2)),
                       (tctrl, (4, 1), (8, 5), wx.EXPAND), ((5, 5), (4, 6)),
                       ((2, 2), (12, 0)), 
                       (send_b, (13, 3), (1, 1), wx.ALIGN_RIGHT),
                       ((3, 3), (13, 4)),
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
            msg = "mailto:%s?subject=Error Report&body=%s"
            addr = "bugs@%s" % (ed_glob.home_page.lstrip("http://"))
            msg = msg % (addr, self.err_msg)
            webbrowser.open(msg)
            self.Close()
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Cleans up the dialog when it is closed
        @param evt: Event that called this handler

        """
        self.Destroy()
