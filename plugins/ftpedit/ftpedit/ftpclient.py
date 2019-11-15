###############################################################################
# Name: ftpclient.py                                                          #
# Purpose: Ftp client for managing connections, downloads, uploads.           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Ftp Client

Ftp client class for managing connections, uploads, and downloads.

The main class exported by this module is L{FtpClient} it implements an easy
to use FTP client interface with both blocking and non blocking methods. To
use the non-blocking methods the client must be initialized with a window object
to recieve the event callbacks from the Async method calls.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ftpclient.py 834 2009-04-08 04:48:44Z CodyPrecord $"
__revision__ = "$Revision: 834 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import threading
import ftplib
import tempfile
from StringIO import StringIO
import wx

# Editra Libraries
from eclib.infodlg import CalcSize
from util import Log

#-----------------------------------------------------------------------------#

# Event that ftp LIST command has completed value == dict of updates
edEVT_FTP_REFRESH = wx.NewEventType()
EVT_FTP_REFRESH = wx.PyEventBinder(edEVT_FTP_REFRESH, 1)

# Download is complete value == (ftppath, temp file path)
edEVT_FTP_DOWNLOAD = wx.NewEventType()
EVT_FTP_DOWNLOAD = wx.PyEventBinder(edEVT_FTP_DOWNLOAD, 1)

# DownloadTo is complete value == (ftppath, destfile, success)
edEVT_FTP_DOWNLOAD_TO = wx.NewEventType()
EVT_FTP_DOWNLOAD_TO = wx.PyEventBinder(edEVT_FTP_DOWNLOAD_TO, 1)

# Upload is complete value == sucess (bool)
edEVT_FTP_UPLOAD = wx.NewEventType()
EVT_FTP_UPLOAD = wx.PyEventBinder(edEVT_FTP_UPLOAD, 1)

class FtpClientEvent(wx.PyCommandEvent):
    """Event for data transfer and signaling end of actions from Async
    L{FtpClient} calls.

    """
    def __init__(self, etype, value='', path=''):
        """Creates the event object
        @keyword value: generic event data
        @keyword path: current working directory

        """
        wx.PyCommandEvent.__init__(self, etype)

        # Attributes
        self._value = value
        self._dir = path

    def GetDirectory(self):
        """Get the clients current directory
        @return: string

        """
        return self._dir

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value

#-----------------------------------------------------------------------------#
# FtpClient Exception Classes

class FtpClientError(Exception):
    """Base L{FtpClient} exception type"""
    pass

class FtpClientNotConnected(FtpClientError):
    """L{FtpClient} is not connected to a remote site"""
    pass

#-----------------------------------------------------------------------------#

class FtpClient(ftplib.FTP):
    """Ftp Client
    Supports both syncronous and asynchronous commands. The asynchronous
    commands are all suffixed with _Async_ and will fire an appropriate
    L{FtpClientEvent} to the owner window when the command completes.

    """
    def __init__(self, parent, host=u'', port=21):
        """Create an ftp client object
        @param parent: owner window (can be None, but no events will be fired)
        @keyword host: host name/ip
        @keyword port: port number

        """
        ftplib.FTP.__init__(self, host)

        # Attributes
        self._parent = parent   # Owner window
        self._default = u'.'    # Default path
        self._curdir = u''      # Current directory
        self._host = host       # Host name
        self._lastlogin = None  # Last used login (user, pass)
        self._port = port       # Port number
        self._active = False    # Connected?
        self._data = list()     # recieved data
        self._lasterr = None    # Last error
        self._mutex = threading.Lock()
        self._busy = threading.Condition(self._mutex)

        # Setup
        self.set_pasv(True) # Use passive mode for now (configurable later)

    def _ProcessException(self, msg):
        """Process exceptions
        @param msg: exception object

        """
        if len(str(msg)):
            self._lasterr = msg

    def _ProcessInput(self, data):
        """Process incoming data
        @param data: string
        @note: for internal use

        """
        processed = ParseFtpOutput(data)

        # Make sure only one thread is modifying the list at a time
        self._busy.acquire()
        self._data.append(processed)
        self._busy.release()

    def _RefreshCommand(self, cmd, args=list()):
        """Run a refresh command
        @param cmd: callable
        @note: Runs cmd and returns result of GetFileList, internal use only.

        """
        cmd(*args)
        return self.GetFileList()

    #---- Public Api ----#

    def ChangeDir(self, path):
        """Change the current working directory and get the list of files
        @return: list

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            self.cwd(path)
            self._curdir = self.pwd()
        except Exception, msg:
            self._lasterr = msg
            Log("[ftpedit][err] ChangeDir: %s" % msg)

        return self.GetFileList()

    def ChangeDirAsync(self, path):
        """Run L{ChangeDir} asynchronously
        @param path: directory to change to
        @note: Generates a refresh event when finished

        """
        ftp_t = FtpThread(self._parent, self.ChangeDir,
                          edEVT_FTP_REFRESH, args=[path,])
        ftp_t.start()

    def CheckConnection(self):
        """Check the connection to see if the client is still logged in.
        @return: bool

        """
        try:
            self.pwd()
        except:
            return False
        else:
            return True

    def ClearLastError(self):
        """Clear the last know error"""
        self._busy.acquire()
        del self._lasterr
        self._lasterr = None
        self._busy.release()

    def Clone(self):
        """Create a copy of this client"""
        nclient = FtpClient(self._parent)
        nclient._default = self._default
        nclient._curdir = self._curdir
        nclient._host = self._host
        nclient._lastlogin = self._lastlogin
        nclient._port = self._port
        nclient._lasterr = self._lasterr
        return nclient

    def Connect(self, user, password):
        """Connect to the site
        @param user: username
        @param password: password

        """
        try:
            # First disconnect if there is an existing connection
            if self.IsActive():
                Log("[ftpedit][warn] Doing disconnect on Connect")
                self.Disconnect()

            # Connect to the server
            self.connect(self._host, int(self._port))
            self.login(user, password)
            self._lastlogin = (user, password)
            self.cwd(self._default)
            self._curdir = self.pwd()
        except Exception, msg:
            Log("[ftpedit][err] Connect: %s" % msg)
            self._ProcessException(msg)
            self._lastlogin = None
            return False
        else:
            self._active = True

        return True

    def Disconnect(self):
        """Disconnect from the site
        @return: bool

        """
        try:
            if self._active:
                self.abort()
            self._active = False
            self.quit()
        except Exception, msg:
            self._ProcessException(msg)
            Log("[ftpedit][err] Disconnect: %s" % msg)
            return False
        return True

    def DeleteFile(self, fname):
        """Delete the given file
        @param fname: string
        @return: bool

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            self.delete(fname)
        except Exception, msg:
            self._ProcessException(msg)
            Log("[ftpedit][err] DeleteFile: %s" % msg)
            return False
        return True

    def DeleteFileAsync(self, fname):
        """Delete the given file asynchronously
        @param fname: string
        @return: bool
        @note: fires EVT_FTP_REFRESH when complete

        """
        ftp_t = FtpThread(self._parent, self._RefreshCommand,
                          edEVT_FTP_REFRESH, args=[self.DeleteFile, [fname,]])
        ftp_t.start()

    def Download(self, fname):
        """Download the file at the given path
        @param fname: string
        @return: (ftppath, temppath)

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        name = None
        try:
            try:
                if not fname.startswith('.') and '.' in fname:
                    pre, suf = fname.rsplit('.', 1)
                    suf = u'.' + suf
                else:
                    pre = fname
                    suf = ''

                fid, name = tempfile.mkstemp(suf, pre, text=True)
                def GetFileData(data, fid=fid):
                    """Write the downloaded data to disk"""
                    os.write(fid, data + u"\n")

                self.retrlines('RETR ' + fname, GetFileData)
            except Exception, msg:
                self._ProcessException(msg)
                Log("[ftpedit][err] Download: %s" % msg)
        finally:
            os.close(fid)

        return (u"/".join([self._curdir, fname]), name)

    def DownloadAsync(self, fname):
        """Do an asynchronous download
        @param fname: filename to download
        @note: EVT_FTP_DOWNLOAD will be fired when complete containing the
               location of the on disk file.

        """
        ftp_t = FtpThread(self._parent, self.Download,
                          edEVT_FTP_DOWNLOAD, args=[fname,])
        ftp_t.start()

    def DownloadTo(self, fname, dest):
        """Download the file from the server to the destination
        @param fname: file on server to download
        @param dest: destination file on local machine

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        ftppath = u"/".join([self._curdir, fname])
        succeed = True
        try:
            try:
                fhandle = open(dest, 'wb')
                self.retrbinary('RETR ' + fname,
                                lambda data: fhandle.write(data))
            except Exception, msg:
                self._ProcessException(msg)
                Log("[ftpedit][err] DownloadTo: %s" % msg)
                succeed = False
        finally:
            fhandle.close()

        return (ftppath, dest, succeed)

    def DownloadToAsync(self, fname, dest):
        """Do an asynchronous download to a specified file.
        @param fname: filename to download
        @param dest: destination file
        @note: EVT_FTP_DOWNLOAD_TO will be fired when complete containing the
               location of the on disk file.

        """
        ftp_t = FtpThread(self._parent, self.DownloadTo,
                          edEVT_FTP_DOWNLOAD_TO, args=[fname, dest])
        ftp_t.start()

    def GetCurrentDirectory(self):
        """Get the current working directory
        @return: string

        """
        return self._curdir

    def GetFileList(self):
        """Get list of files at the given path
        @return: list of dict(isdir, name, size, date)

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            code = self.retrlines('LIST', self._ProcessInput)
        except Exception, msg:
            Log("[ftpedit][err] GetFileList: %s" % msg)
            self._ProcessException(msg)

        #-- Critical section --#
        self._busy.acquire()
        rval = list(self._data)
        del self._data
        self._data = list()
        self._busy.release()
        #-- End Critical Section --#

        # Sort the list (directories, files)
        dirs = list()
        files = list()
        for item in rval:
            if item['isdir']:
                dirs.append(item)
            else:
                files.append(item)

        # Sort dir list by dir name
        dirs.sort(key=lambda x: x['name'])

        # Insert dummy .. entry to allow for navigating backwards with
        dirs.insert(0, dict(name=u'..', isdir=True, size=u'0 bytes', date=u''))

        # Sort file list by file name
        files.sort(key=lambda x: x['name'])

        # Return ordered list of directories followed by files in alphanumeric
        # sorted order.
        return dirs + files

    def GetHostname(self):
        """Get the name of the currently connected host
        @return: string

        """
        return self._host

    def GetLastError(self):
        """Get the last error that occured
        @return: Exception

        """
        return self._lasterr

    def GetLastLogin(self):
        """Get the last used login info
        @return: (user, pass) or None

        """
        return self._lastlogin

    def GetParent(self):
        """Get the clients parent window
        @return: parent window or None

        """
        return self._parent

    def IsActive(self):
        """Does the client have an active connection
        @return: bool

        """
        return self._active

    def Login(self, user, password):
        """Login to the server
        @param user: username
        @param password: password
        @precondition: Connect has already been called
        @return: bool

        """
        try:
            self.login(user, password)
        except ftplib.all_errors, msg:
            self._ProcessException(msg)
            Log("[ftplib][err] Login: %s" % msg)
            return False
        return True

    def MkDir(self, dname):
        """Make a new directory at the current path
        @param dname: string

        """
        raise NotImplementedError

    def NewDir(self, dname):
        """Create a new directory relative to the current path
        @param dname: string

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            self.mkd(dname)
        except Exception, msg:
            self._ProcessException(msg)
            Log("[ftpedit][err] NewDir: %s" % msg)
            return False
        return True

    def NewDirAsync(self, dname):
        """Create a new directory asynchronously and fire an EVT_FTP_REFRESH
        @param dname: string

        """
        ftp_t = FtpThread(self._parent, self._RefreshCommand,
                          edEVT_FTP_REFRESH, args=[self.NewDir, [dname,]])
        ftp_t.start()

    def NewFile(self, fname):
        """Create a new file relative to the current path
        @param fname: string

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            buff = StringIO('')
            self.storlines('STOR ' + fname, buff)
        except Exception, msg:
            self._ProcessException(msg)
            Log("[ftpedit][err] Upload: %s" % msg)
            return False
        return True

    def NewFileAsync(self, fname):
        """Create the new file asynchronously and fire an EVT_FTP_REFRESH upon
        completion.
        @param fname: name of file.

        """
        ftp_t = FtpThread(self._parent, self._RefreshCommand,
                      edEVT_FTP_REFRESH, args=[self.NewFile, [fname,]])
        ftp_t.start()

    def RefreshPath(self):
        """Refresh the current working directory.
        Runs L{GetFileList} asynchronously and returns the results
        in a EVT_FTP_REFRESH event.

        """
        ftp_t = FtpThread(self._parent, self.GetFileList, edEVT_FTP_REFRESH)
        ftp_t.start()

    def Rename(self, old, new):
        """Rename the file
        @param old: old file name
        @param new: new file name
        @return: bool

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            self.rename(old, new)
        except Exception, msg:
            self._ProcessException(msg)
            Log("[ftpedit][err] Rename: %s" % msg)
            return False
        return True

    def RenameAsync(self, old, new):
        """Rename the file asynchronously
        @param old: old file name
        @param new: new file name

        """
        ftp_t = FtpThread(self._parent, self._RefreshCommand,
                          edEVT_FTP_REFRESH, args=[self.Rename, [old, new]])
        ftp_t.start()

    def SetDefaultPath(self, dpath):
        """Set the default path
        @param dpath: string

        """
        self._default = dpath

    def SetHostname(self, hostname):
        """Set the host name
        @param hostname: string

        """
        self._host = hostname

    def SetPort(self, port):
        """Set the port to connect to
        @param port: port number (int)

        """
        self._port = port

    def Upload(self, src, dest):
        """Upload a file to the server
        @param src: source file
        @param dest: destination file on server
        @return: bool

        """
        if not self.IsActive():
            raise FtpClientNotConnected, "FtpClient is not connected"

        try:
            fhandle = open(src, 'r')
            buff = StringIO(fhandle.read())
            fhandle.close()
            self.storlines('STOR ' + dest, buff)
        except Exception, msg:
            self._ProcessException(msg)
            Log("[ftpedit][err] Upload: %s" % msg)
            return False
        return True

    def UploadAsync(self, src, dest):
        """Upload the file asyncronously
        @param src: source file
        @param dest: destination file on server
        @note: completion notified by EVT_FTP_UPLOAD

        """
        ftp_t = FtpThread(self._parent, self.Upload,
                          edEVT_FTP_UPLOAD, args=[src, dest])
        ftp_t.start()

#-----------------------------------------------------------------------------#

class FtpThread(threading.Thread):
    """Thread for running asyncronous ftp jobs"""
    def __init__(self, parent, funct, etype, args=list()):
        """Create the thread object
        @param parent: Parent window to recieve event(s) (can be None)
        @param funct: method to run in a thread
        @param etype: event type
        @keyword args: list of args to pass to funct

        """
        threading.Thread.__init__(self)

        # Attributes
        self._parent = parent
        self._funct = funct
        self._etype = etype
        self._args = args

    def run(self):
        """Run the command"""
        result = self._funct(*self._args)

        # HACK: too lazy to fix now...
        cdir = self._funct.im_self.GetCurrentDirectory()

        # Fire a notification event if we have a parent
        if self._parent is not None:
            evt = FtpClientEvent(self._etype, result, cdir)
            wx.PostEvent(self._parent, evt)

#-----------------------------------------------------------------------------#
# Utility

def ParseFtpOutput(line):
    """Parse output from the ftp RETR/LIST commands and render a dictionary
    of tokens.
    @param line: line from ftp list.
    @return: dict(isdir, size, modified, fname)

    """
    rval = dict()
    parts = line.split(None, 9)
    state = 0
    dstring = u''
    for part in parts:
        # Permissions / type
        if state == 0:
            rval['isdir'] = part.startswith('d')
            state += 1
            continue

        # Size
        elif state == 4 and part.isdigit():
            val = int(part.strip())
            rval['size'] = CalcSize(val)
            state += 1

        # Last modified
        elif state >= 5 and state < 8:
            dstring = dstring + u" " + part
            if state == 7:
                rval['date'] = dstring.strip()
            state += 1

        # Filename
        elif state == 8:
            rval['name'] = part
            break

        else:
            state += 1

    return rval
