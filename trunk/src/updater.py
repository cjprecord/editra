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
# FILE:							   
# AUTHOR:
# LANGUAGE: Python							   
# SUMMARY:
#
#
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import re
import wx.lib.delayedresult as delayedresult
import urllib
import wx
import ed_glob
import ed_event
from profiler import CalcVersionValue
import util
#--------------------------------------------------------------------------#
# Globals
DL_REQUEST = ed_glob.home_page + "/?page=download&dist=%s"
DL_LIN = 'SRC'          # This may need to change in future
DL_MAC = 'Macintosh'
DL_SRC = 'SRC'
DL_WIN = 'Windows'

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

class UpdateService:
    """Defines an updater service object for Editra"""
    def __init__(self):
        """Initializes the Updator Object"""
        self._progress = (0, 100)
        
    def GetCurrFileURL(self):
        """Returns the url for the current version of the program
        for the current operating system, by requesting the data from
        project homepage.
        
        """
        if wx.Platform == '__WXGTK__':
            dist = DL_LIN
        elif wx.Platform == '__WXMAC__':
            dist = DL_MAC
        elif wx.Platform == '__WXMSW__':
            dist = DL_WIN
        else:
            dist = DL_SRC
        url = self.GetPageText(DL_REQUEST % dist)
        url_pat = re.compile('<\s*a id\="CURRENT"[^>]*>(.*?)<\s*/a\s*>')
        url = re.findall(url_pat, url)
        if len(url):
            url = url[0]
        else:
            url = ''
        return url.strip()

    def GetCurrentVersionStr(self):
        """Parses the project website front page for the most
        recent version of the program.
        
        """
        version = re.compile('<\s*a id\="VERSION"[^>]*>(.*?)<\s*/a\s*>')
        page = self.GetPageText(ed_glob.home_page)
        found = re.findall(version, page)
        if len(found):
            return found[0] # Should be the first/only match found
        else:
            return _("Unable to retrieve version info")

    def GetFileSize(self, url):
        """Gets the size of a file by address"""
        size = 0
        try:
            dl_file = urllib.urlopen(url)
            info = dl_file.info()
            size = int(info['Content-Length'])
            dl_file.close()
        finally:
            return size

    def GetPageText(self, url):
        """Gets the text of a url"""
        text = u''
        try:
            h_file = urllib.urlopen(url)
            text = h_file.read()
            h_file.close()
        finally:
            return text

    def GetProgress(self):
        """Returns the current progress/total tuple"""
        return self._progress

    def GetUpdateFiles(self, dl_to=wx.GetHomeDir()):
        """Gets the requested version of the program from the website
        if possible. It will download the current files for the host system to
        location (dl_to). On success it returns True, otherwise it returns
        false.
        
        """
        # Check version to see if update is needed
        # Dont allow update if files are current
        verpat = re.compile('[0-9]+\.[0-9]+\.[0-9]+')
        current = self.GetCurrentVersionStr()
        if not re.match(verpat, current):
            return False

        if CalcVersionValue(ed_glob.version) < CalcVersionValue(current):
            dl_path = self.GetCurrFileURL()
            dl_file = dl_path.split('/')[-1]
            dl_to = dl_to + dl_file
            try:
                urllib.urlretrieve(dl_path, dl_to, self.UpdaterHook)
            finally:
                # XXX should check the amount of blocks written to the file
                #     against what was expected from the download to verify
                #     the validity of the download.
                if os.path.exists(dl_to) and self._progress[0] == self._progress[1]:
                    return True
                else:
                    return False
        else:
            return False

    def UpdaterHook(self, count, block_sz, total_sz):
        """Updates the progress tuple of (amount_done, total) on
        each iterative call during the download.

        """
        done = count * block_sz
        #percent = done / total_sz
        self._progress = (done, total_sz)

class UpdateProgress(wx.Gauge, UpdateService):
    """Creates a progress bar that is controlled by the UpdateService"""
    ID_CHECKING = wx.NewId()
    ID_DOWNLOADING = wx.NewId()
    ID_TIMER = wx.NewId()

    def __init__(self, parent, id, range=100, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.GA_HORIZONTAL | wx.GA_PROGRESSBAR):
        """Initiliazes the bar in a disabled state."""
        wx.Gauge.__init__(self, parent, id, range, pos, size, style)
        UpdateService.__init__(self)

        #---- Attributes ----#
        self.LOG = wx.GetApp().GetLog()
        self._abortevt = delayedresult.AbortEvent()
        self._checking = False
        self._downloading = False
        self._mode = 0
        self._parent = parent
        self._range = range
        self._status = _("Status Unknown")
        self._timer = wx.Timer(self, id=self.ID_TIMER)

        #---- Bind Events ----#
        self.Bind(wx.EVT_TIMER, self.OnUpdate, id=self.ID_TIMER)
        
        # Disable bar till caller is ready to use it
        self.Disable()

    def __del__(self):
        """Cleans up when the control is destroyed"""
        if self._timer.IsRunning():
            self.LOG("[updater][info] Stopped timer on deletion")
            self._timer.Stop()

    def CheckForUpdates(self):
        """Checks for updates and activates the bar. In order to keep the
        UI from freezing while checking for updates the actual work is carried
        out on another thread. When the thread exits it will set the _checking
        attribute to false and set the _status attribute (See GetStatus) to the
        return value of the check function which is either a version string or
        an appropriate error message.
        
        Also See: _UpdatesCheckThread

        """
        # Set bar to Checking mode so it knows to simulate update progress
        self._mode = self.ID_CHECKING
        self.SetValue(0)
        self.Start(25)
        self._checking = True
        delayedresult.startWorker(self._ResultCatcher, self._UpdatesCheckThread)

    def DownloadUpdates(self, dl_loc=wx.EmptyString):
        """Downloads available updates and configures the bar.
        Returns True if the update was successfull or False if
        it was not. The updates will be downloaded to the 
        specified location or to the Users Desktop or Home
        Folder if no location is specified.
        
        """
        self.LOG("[updater-evt] Attempting to download updates...")
        if dl_loc == wx.EmptyString:
            dl_loc = wx.GetHomeDir() + util.GetPathChar()
            if os.path.exists(dl_loc + u"Desktop"):
                dl_loc = dl_loc + u"Desktop" + util.GetPathChar()
        self._mode = self.ID_DOWNLOADING
        self.SetValue(0)
        self.Start(50)   #XXX Try this for starters
        self._downloading = True # Mark the work status as busy
        delayedresult.startWorker(self._ResultCatcher, self._DownloadThread, wargs=(dl_loc,))

    def GetMode(self):
        """Returns the current mode of operation or 0 if the bar
        is currently inactive.
        
        """
        return self._mode

    def GetStatus(self):
        """Returns the status attribute string"""
        return self._status

    def GetUpdatesAvailable(self):
        """Compares the status against the version of the running
        program to see if updates are available. It is expected
        that CheckForUpdates has been called prior to calling this
        function. Returns True if Available and False otherwise.
        
        """
        if self._status[0].isdigit():
            return CalcVersionValue(self._status) > CalcVersionValue(ed_glob.version)
        else:
            return False

    def OnUpdate(self, evt):
        """Timer Event Handler Updates the progress bar
        on each cycle of the timer
        
        """
        mode = self.GetMode()
        progress = self.GetProgress()
        range = self.GetRange()
        if mode == self.ID_CHECKING:
            # Simulate updates
            if progress[0] < range:
                self.UpdaterHook(progress[0]+1, 1, 100)
                progress = self.GetProgress()
            if not self._checking and progress[0] >= range:
                self.Stop()

        if mode == self.ID_DOWNLOADING:
            if not self._downloading and progress[0] >= range:
                self.Stop()

        # Update Range if need be
        if range != progress[1]:
            self.SetRange(progress[1])

        # Update Progress
        if progress[0] < progress[1]:
            self.SetValue(progress[0])
        elif progress[0] == progress[1]:
            self.Pulse()
        else:
            pass

    def Start(self, msec=100):
        """Starts the progress bar and timer if not already active"""
        if not self._timer.IsRunning():
            self.LOG('[updater-evt] Starting Clock')
            self.Enable()
            self._timer.Start(msec)
        else:
            pass

    def Stop(self):
        """Stops the progress bar"""
        if self._timer.IsRunning():
            self.LOG('[updater-evt] Stopping Clock')
            self._timer.Stop()
            self._mode = 0
            self._progress = (0, 100)
            # TODO save reference to this id in ed_glob should be the Id of the
            #      text object to update. but since there is only one right now
            mevt = ed_event.UpdateTextEvent(ed_event.edEVT_UPDATE_TEXT, self.ID_CHECKING)
            wx.PostEvent(self._parent, mevt)
        else:
            pass
#         self.SetValue(0)
        self.Disable()

    def _DownloadThread(self, loc):
        """Processes the download"""
     #   size = self.GetFileSize(self.GetCurrFileURL())
    #    self.SetRange(size)
     #   self.SetValue(0)
        dl_ok = self.GetUpdateFiles(loc)
        self._downloading = False

    def _ResultCatcher(self, delayedResult):
        """Recieves the return from the result of the worker thread"""
        id = delayedResult.getJobID()
        try:
            delayedResult.get()
        except Exception, msg:
            self.LOG("[updater][exception] Error on thread exit")
            print msg   # TESTO

    def _UpdatesCheckThread(self):
        """Sets internal status value to the return value from calling
        GetCurrentVersionStr. This function is called on a separate thread
        in the CheckForUpdates function to allow the ui to update properly
        while this function waits for the result from the network.
        
        """
        self.LOG("[updater-evt] Checking for updates")
        self._checking = True
        ret = self.GetCurrentVersionStr()
        self._status = ret
        self._checking = False # Notify that thread is exiting
        self.LOG("[updater-evt] Finished Checking for updates: result = " + ret)
        return 0
