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
# FILE: updater.py                                                         #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#   Provides controls/services that are used in checking and downloading   #
# updates for the editor if they are available. The main control exported  #
# by this module is the UpdateProgress bar it displays the progress of the #
# network action and provides a higher level interface into the            #
# UpdateService.                                                           #
#                                                                          #
# METHODS:                                                                 #
# - UpdateService: Does the actual network lookups and downloads           #
# - UpdateProgress: A Progress bar control which inherits its functionality#
#                   from the UpdateService. It runs the network service on #
#                   a separate thread from the gui to allow for fluid gui  #
#                   response during the long delays that can occure while  #
#                   waiting for the network to respond.                    #
# - DownloadDialog: Uses the UpdateProgress bar and performs the downloads #
#                   in a standalone dialog that can remain running after   #
#                   the app has exited.                                    #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import re
import urllib
import wx
import wx.lib.delayedresult as delayedresult
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
        self._abort = False
        self._progress = (0, 100)

    def Abort(self):
        """Cancel any pending or in progress actions."""
        self._abort = True

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
            url = wx.EmptyString
        return url.strip()

    def GetCurrFileName(self):
        """Returns the name of the file that is currently available for
        download as a string.
        
        """
        url = self.GetCurrFileURL()
        return url.split(u'/')[-1]

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
                blk_sz = 4096
                read = 0
                webfile = urllib.urlopen(dl_path)
                fsize = int(webfile.info()['Content-Length'])
                locfile = open(dl_to, 'wb')
                while read < fsize and not self._abort:
                    locfile.write(webfile.read(blk_sz))
                    read += blk_sz
                    self.UpdaterHook(int(read/blk_sz), blk_sz, fsize)
                locfile.close()
                webfile.close()
            finally:
                self._abort = False
                if os.path.exists(dl_to) and os.stat(dl_to)[6] == fsize:
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
        if done > total_sz:
            done = total_sz
        self._progress = (done, total_sz)

#-----------------------------------------------------------------------------#

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
        self._checking = False
        self._downloading = False
        self._dl_result = False
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
            self.LOG("[updateprog][info] Stopped timer on deletion")
            self._timer.Stop()

    def Abort(self):
        """Overides the UpdateService abort function"""
        self.LOG("[updateprog][info] Aborting action, stopping progress bar")
        UpdateService.Abort(self)
        if self._timer.IsRunning():
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
        self.Start(10)
        self._checking = True
        delayedresult.startWorker(self._ResultNotifier, self._UpdatesCheckThread,
                                  jobID=self.ID_CHECKING)

    def DownloadUpdates(self, dl_loc=wx.EmptyString):
        """Downloads available updates and configures the bar.
        Returns True if the update was successfull or False if
        it was not. The updates will be downloaded to the 
        specified location or to the Users Desktop or Home
        Folder if no location is specified.
        
        """
        self.LOG("[updateprog][evt] Attempting to download updates...")
        if dl_loc == wx.EmptyString:
            dl_loc = wx.GetHomeDir() + util.GetPathChar()
            if os.path.exists(dl_loc + u"Desktop"):
                dl_loc = dl_loc + u"Desktop" + util.GetPathChar()
        self._mode = self.ID_DOWNLOADING
        self.SetValue(0)
        self.Start(50)   #XXX Try this for starters
        self._downloading = True # Mark the work status as busy
        delayedresult.startWorker(self._ResultNotifier, self._DownloadThread, 
                                  wargs=(dl_loc,), jobID=self.ID_DOWNLOADING)

    def GetDownloadResult(self):
        """Returns the status of the last download action. Either
        True for success or False for failure.
        
        """
        return self._dl_result

    def GetDownloadLocation(self):
        """Returns the path that the file will be downloaded to.
        Currently will either return the users Desktop path or the
        users home directory in the case that there is no deskop directory
        
        """
        dl_loc = wx.GetHomeDir() + util.GetPathChar()
        if os.path.exists(dl_loc + u"Desktop"):
            dl_loc = dl_loc + u"Desktop" + util.GetPathChar()
        return dl_loc

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

    def IsDownloading(self):
        """Returns a bool stating whether there is a download
        in progress or not.
        
        """
        return self._downloading

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
                self.UpdaterHook(progress[0]+1, 1, 90)
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
            self.LOG('[updateprog][evt] Starting Clock')
            self.Enable()
            self._timer.Start(msec)
        else:
            pass

    def Stop(self):
        """Stops the progress bar"""
        if self._timer.IsRunning():
            self.LOG('[updateprog][evt] Stopping Clock')
            self._timer.Stop()
            self._mode = 0
        else:
            pass
        self.SetValue(0)
        self.Disable()

    #--- Protected Member Functions ---#
    def _DownloadThread(self, loc):
        """Processes the download and checks that the file has been downloaded
        properly. Then returns either True if the download was succesfull or
        False if it failed in some way.
        
        """
        dl_ok = self.GetUpdateFiles(loc)
        return dl_ok

    def _ResultNotifier(self, delayedResult):
        """Recieves the return from the result of the worker thread and
        notifies the interested party with the result.
        
        """
        id = delayedResult.getJobID()
        self.LOG("[updateprog][info] Worker thread has finished its work. ID = %d" % id)
        self._checking = self._downloading = False # Work has finished
        try:
            result = delayedResult.get()
            if id == self.ID_CHECKING:
                mevt = ed_event.UpdateTextEvent(ed_event.edEVT_UPDATE_TEXT, self.ID_CHECKING)
                wx.PostEvent(self._parent, mevt)
                pass #TODO Need to flag if updates are available or not
            elif id == self.ID_DOWNLOADING:
                self._dl_result = result
            else:
                pass
        except Exception, msg:
            self.LOG("[updateprog][exception] Error on thread exit")
            print msg

    def _UpdatesCheckThread(self):
        """Sets internal status value to the return value from calling
        GetCurrentVersionStr. This function is called on a separate thread
        in the CheckForUpdates function to allow the ui to update properly
        while this function waits for the result from the network. Returns
        True to the consumer if updates are available and false if they
        are not or status is unknown.
        
        """
        self.LOG("[updateprog][evt] Checking for updates")
        self._checking = True
        ret = self.GetCurrentVersionStr()
        self._status = ret
        self.LOG("[updateprog][evt] Finished Checking for updates: result = " + ret)
        if ret[0].isdigit() and CalcVersionValue(ret) > CalcVersionValue(ed_glob.version):
            ret = True
        else:
            ret = False
        return ret

#-----------------------------------------------------------------------------#

#XXX Status bar is sometimes not wide enough to display all data.
class DownloadDialog(wx.Frame):
    """Creates a standalone download window"""
    ID_PROGRESS_BAR = wx.NewId()
    ID_TIMER        = wx.NewId()
    SB_DOWNLOADED   = 0
    SB_INFO         = 1
    
    def __init__(self, parent, id, title, pos = wx.DefaultPosition, 
                 size = wx.DefaultSize, 
                 style = wx.DEFAULT_DIALOG_STYLE | wx.MINIMIZE_BOX):
        """Creates a standalone window that is used for downloading
        updates for the editor.
        
        """
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        try:
            if wx.Platform == "__WXMSW__":
                ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.ico"
                self.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_ICO))
            else:
                ed_icon = ed_glob.CONFIG['SYSPIX_DIR'] + u"editra.png"
                self.SetIcon(wx.Icon(ed_icon, wx.BITMAP_TYPE_PNG))
        finally:
            pass

        #---- Attributes/Objects ----#
        self.LOG = wx.GetApp().GetLog()
        self._parent = parent
        self._progress = UpdateProgress(self, self.ID_PROGRESS_BAR)
        fname = self._progress.GetCurrFileName()
        floc = self._progress.GetDownloadLocation()
        dl_file = wx.StaticText(self, wx.ID_ANY, _("Downloading: %s") % fname)
        dl_loc = wx.StaticText(self, wx.ID_ANY, 
                               _("Downloading To: %s") % floc)
        self._cancel_bt = wx.Button(self, wx.ID_CANCEL)
        self._timer = wx.Timer(self, id=self.ID_TIMER)
        self._proghist = list()

        #---- Layout ----#
        self.CreateStatusBar(2)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(wx.Size(15,15))

        hdr = wx.BoxSizer(wx.HORIZONTAL)
        hdr.Add(wx.Size(5,5))
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DOWNLOAD_DLG), wx.ART_OTHER)
        bmp = wx.StaticBitmap(self, wx.ID_ANY, bmp)
        hdr.Add(bmp, 0, wx.ALIGN_LEFT)
        hdr.Add(wx.Size(5,5))
        shdr = wx.BoxSizer(wx.VERTICAL)
        df_sz = wx.BoxSizer(wx.HORIZONTAL)
        df_sz.Add(dl_file, 0, wx.ALIGN_LEFT)
        df_sz.Add(wx.Size(5,5))
        shdr.Add(df_sz, 0, wx.ALIGN_LEFT)
        shdr.Add(wx.Size(5,5))
        dl_sz = wx.BoxSizer(wx.HORIZONTAL)
        dl_sz.Add(dl_loc, 0, wx.ALIGN_LEFT)
        dl_sz.Add(wx.Size(5,5))
        shdr.Add(dl_sz, 0, wx.ALIGN_LEFT)
        hdr.Add(shdr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizer.Add(hdr, 0, wx.ALIGN_LEFT)
        self._sizer.Add(wx.Size(20,20))
        self._sizer.Add(self._progress, 0, wx.ALIGN_CENTER)
        self._sizer.Add(wx.Size(15,15))
        self._sizer.Add(self._cancel_bt, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizer.Add(wx.Size(15, 15))
        self.SetSizer(self._sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()

        # Adjust progress bar and status widths
        sz = self.GetSize()
        if wx.Platform == '__WXMSW__':
            wd = sz.GetWidth()
            if wd < 375:
                wd = 375
            self.SetSize(wx.Size(wd, sz.GetHeight()))
            self.SendSizeEvent()
        self._progress.SetSize(wx.Size(int(sz[0]*.80), 18))
        self.SetStatusWidths([-1, 100])
        self.SetStatusText(_("Downloading..."), self.SB_INFO)

        #---- Bind Events ----#
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnUpdate, id=self.ID_TIMER)

    def __del__(self):
        """Cleans up on exit"""
        if self._timer.IsRunning():
            self.LOG('[update-dlg][info] Stopping timer on deletion')
            self._timer.Stop()

    def CalcDownRate(self):
        """Calculates and returns the approximate download rate
        in Kb/s
        
        """
        dlist = list()
        last = 0
        for item in self._proghist:
            val = item - last
            dlist.append(val)
            last = item
        return round((float(sum(dlist) / len(self._proghist)) / 1024), 2)
            
    def OnButton(self, evt):
        """Handles events that are generated when buttons are pushed."""
        e_id = evt.GetId()
        if e_id == wx.ID_CANCEL:
            self.LOG("[download-dlg] [evt] Cancel was pressed, aborting download")
            self._progress.Abort()
            self._cancel_bt.Disable()
            self.SetStatusText(_("Canceled"), self.SB_INFO)
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Handles the window closer event"""
        self.LOG("[download-dlg] [evt] Closing Download Dialog")
        self._progress.Abort()
        # Wait till thread has halted before exiting
        while self._progress.IsDownloading():
            wx.Yield()
        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()
        
    def OnUpdate(self, evt):
        """Updates the status text on each pulse from the timer"""
        e_id = evt.GetId()
        if e_id == self.ID_TIMER:
            prog = self._progress.GetProgress()
            self._proghist.append(prog[0])
            speed = self.CalcDownRate()
            if self._progress.IsDownloading():
                self.SetStatusText(_("Downloaded: ") + str(prog[0]) + \
                                    u"/" + str(prog[1]) + u" | " + \
                                    _("Rate: %.2f Kb/s") % speed, self.SB_DOWNLOADED)
            else:
                self.LOG("[download-dlg][evt] Download finished")
                self.SetStatusText(_("Downloaded: ") + str(prog[0]) + \
                                    u"/" + str(prog[1]), self.SB_DOWNLOADED)
                if self._progress.GetDownloadResult():
                    self.LOG("[download-dlg][info] Download Successful")
                    self.SetStatusText(_("Finished"), self.SB_INFO)
                else:
                    self.LOG("[download-dlg][info] Download Failed")
                    self.SetStatusText(_("Failed"), self.SB_INFO)
                self._progress.Enable()
                self._progress.SetValue(self._progress.GetProgress()[0])
                self._timer.Stop()
                self._cancel_bt.Disable()
        else:
            evt.Skip()

    def Show(self):
        """Shows the Dialog and starts downloading the updates"""
        # Tell the main loop we are busy
        wx.GetApp().RegisterWindow(repr(self), self, True)
        self._timer.Start(1000) # One pulse every second
        self._progress.DownloadUpdates()  #TODO Allow setting of download location
        wx.Frame.Show(self)
