###############################################################################
# Name: ftpfile.py                                                            #
# Purpose: Ftp file layer                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Ftp File

Classes and utilities for abstracting files operations over ftp.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ftpfile.py 834 2009-04-08 04:48:44Z CodyPrecord $"
__revision__ = "$Revision: 834 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Editra Libraries
import ed_glob
import ed_msg
import ed_txt
from util import Log

# Local Imports
import ftpclient

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class FtpFile(ed_txt.EdFile):
    """Editra file implementation that hooks uploading saves to the ftp
    site the file was opened from.

    """
    def __init__(self, client, ftppath, sitedata, path='', modtime=0):
        """Create the FtpFile.
        Implementation Note: This file object is only associated with the
        ftppath as long as it is alive, if the on disk file's name is changed
        or the in memory instance of this object is deleted the file passed in
        as path will be automatically removed, as it is intended to be a
        TEMPORARY file with the real file existing on the ftp server. Do not 
        pass in non temporary files for the path keyword or it will be DELETED 
        when this object is destroyed!

        @param client: ftp client that opened the file
        @param ftppath: path to file on ftp server
        @param sitedata: site login data
        @keyword path: on disk path (used by EdFile)
        @keyword modtime: last mod time (used by EdFile)

        """
        ed_txt.EdFile.__init__(self, path, modtime)

        # Attributes
        self._client = client
        self._ftp = True
        self.ftppath = ftppath
        self._site = sitedata   # dict(url, port, user, pword, path, enc)
        self._notifier = None
        self._window = None
        self._pid = None

        window = self._client.GetParent()
        if isinstance(window, wx.Window):
            self._window = window.GetTopLevelParent()
            self._pid = self._window.GetId()

        # Setup
        self.SetEncoding(self._site['enc'])

    def __del__(self):
        """Cleanup the temp file"""
        self.CleanUp()

    def _Busy(self, busy=True):
        """Start/stop the frames busy indicato
        @keyword busy: bool

        """
        if busy:
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (self._pid, True))
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (self._pid, -1, -1))
        else:
            ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (self._pid, False))

    def _NotifyError(self):
        """Notify of errors"""
        if isinstance(self._window, wx.Frame):
            msg = self._client.GetLastError()
            wx.MessageBox(unicode(msg), _("Ftp Save Error"),
                          wx.OK|wx.CENTER|wx.ICON_ERROR)

    @staticmethod
    def _PostStatusMsg(msg):
        """Post a message to update the status text to inform of file changes"""
        ed_msg.PostMessage(ed_msg.EDMSG_UI_SB_TXT, (ed_glob.SB_INFO, msg))

    def CleanUp(self):
        """Cleanup the file object"""
        path = self.GetPath()
        if self._ftp:
            # Only remove if its the temp file
            os.remove(path)
            self._ftp = False

        if self._notifier is not None:
            self._notifier(path)
            self._notifier = None

    def ClearFtpStatus(self):
        """Disassociate this file object with ftp callbacks"""
        self.SetDisconnectNotifier(None)
        self.SetClient(None)
        self._ftp = False

    def DoFtpUpload(self):
        """Upload the contents of the on disk temp file to the server"""
        if self._client is None:
            return

        # Cant reuse ftp ojects...
        self._client = self._client.Clone()
        self._client.SetHostname(self._site['url'])
        self._client.SetPort(self._site['port'])
        connected = self._client.Connect(self._site['user'],
                                         self._site['pword'])

        if not connected:
            # TODO: report error to upload in ui
            err = self._client.GetLastError()
            Log("[ftpedit][err] DoFtpUpload: %s" % err)
            wx.CallAfter(self._NotifyError)
            wx.CallAfter(self._PostStatusMsg, _("Ftp upload failed: %s") % self.ftppath)
        else:
            wx.CallAfter(self._Busy, True)
            success = self._client.Upload(self.GetPath(), self.ftppath)
            if not success:
                wx.CallAfter(self._NotifyError)
                wx.CallAfter(self._PostStatusMsg, _("Ftp upload failed: %s") % self.ftppath)
            else:
                wx.CallAfter(self._PostStatusMsg, _("Ftp upload succeeded: %s") % self.ftppath)
                parent = self._client.GetParent()
                if parent is not None:
                    files = self._client.GetFileList()
                    evt = ftpclient.FtpClientEvent(ftpclient.edEVT_FTP_REFRESH, files)
                    wx.PostEvent(parent, evt)
            self._client.Disconnect()
            wx.CallAfter(self._Busy, False)

    def GetCurrentDirectory(self):
        """Hack for compatibility with FtpThread"""
        return self._client.GetCurrentDirectory()

    def GetFtpPath(self):
        """Get the ftp path
        @return: string

        """
        return self.ftppath

    def GetSiteData(self):
        """Get the ftp site data that this file belongs to
        @return: dict(url, port, user, pword, path, enc)

        """
        return self._site

    def SetClient(self, client):
        """Set the ftp client this file uses for doing uploads.
        @param client: instance of ftpclient or None

        """
        self._client = client

    def SetDisconnectNotifier(self, notifier):
        """Set the client callback notifier for when this object is
        deleted or disassociated from the client.

        """
        self._notifier = notifier

    def SetFilePath(self, path):
        """Change the file path. Changing the path on an ftp file will 
        disassociate it with the ftp site turning it into a regular file.
        @param path: string

        """
        cpath = self.GetPath()
        if path != cpath:
            # Cleanup the tempfile now
            try:
                self.CleanUp()
            except OSError, msg:
                Log("[ftpfile][err] SetFilePath: %s" % msg)

            super(FtpFile, self).SetFilePath(path)
            self._ftp = False

    def Write(self, value):
        """Override EdFile.Write to trigger an upload
        @param value: string

        """
        # Save the local file
        super(FtpFile, self).Write(value)

        # Upload the file to the server
        if self._ftp:
            ftp_t = ftpclient.FtpThread(None, self.DoFtpUpload,
                                    ftpclient.EVT_FTP_UPLOAD)
            ftp_t.start()

#-----------------------------------------------------------------------------#


