###############################################################################
# Name: outwin.py                                                             #
# Purpose: Multithreaded/Asynchronous result output window and related        #
#          controls                                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
  The L{OutputWin} is a panel composed of two main control, a control/status bar
on the top and a readonly output buffer on the bottom. The control bar is
created by the L{ConfigBar} class and controls all the data and initiation of
actions in the output buffer by communicating through events. The output buffer
is created by the L{OutputBuffer} class which is a simple text buffer that
offers some color contexting for information and error messages in the output
from the running script.

  The L{OutputWin} uses these two controls to execute and run a python script
from the currently selected buffer in Editra's MainWindow and display the
results. The script is run on a separate thread with subproccess to keep it
from blocking the rest of the ui.

  A running script can be Aborted at anytime by clicking on the Abort button,
the script is then aborted by sending a signal to the process running on the
worker thread.

  The Python executable and command is configurable through the buffer on the
L{ConfigBar}. This command is checked when a run script is action is requested.
If you have pylint installed you can also use this option to run pylint on the
current buffer by changing the command to 'pylint' or '/path/to/pylint'.

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: outwin.py 346 2008-01-12 06:28:47Z CodyPrecord $"
__revision__ = "$Revision: 346 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re
import tempfile
import wx
import wx.stc
import threading
import signal
from subprocess import Popen, PIPE, STDOUT

# Needed for killing processes on windows
if sys.platform.startswith('win'):
    import ctypes

# Editra Imports
import util
from profiler import Profile_Get, Profile_Set
import syntax.synglob as synglob
import extern.flatnotebook as flatnotebook

# Highlight Match Patters
error_re = re.compile('.*File "(.+)", line ([0-9]+)')
info_re = re.compile('[>]{3,3}.*' + os.linesep)

# Function Aliases
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Globals
PYRUN_EXE = 'PyRun.PyExe'   # Profile key for saving prefered python command

#-----------------------------------------------------------------------------#
# Custom Events

# Event for passing output data to buffer
edEVT_UPDATE_TEXT = wx.NewEventType()
EVT_UPDATE_TEXT = wx.PyEventBinder(edEVT_UPDATE_TEXT, 1)

# Event for notifying that the script should be aborted
edEVT_PROCESS_ABORT = wx.NewEventType()
EVT_PROCESS_ABORT = wx.PyEventBinder(edEVT_PROCESS_ABORT, 1)

# Event for clearing output window
edEVT_PROCESS_CLEAR = wx.NewEventType()
EVT_PROCESS_CLEAR = wx.PyEventBinder(edEVT_PROCESS_CLEAR, 1)

# Message that process should be started
edEVT_PROCESS_START = wx.NewEventType()
EVT_PROCESS_START = wx.PyEventBinder(edEVT_PROCESS_START, 1)

# Event for notifying that the script has finished executing
edEVT_PROCESS_EXIT = wx.NewEventType()
EVT_PROCESS_EXIT = wx.PyEventBinder(edEVT_PROCESS_EXIT, 1)

class OutputWinEvent(wx.PyCommandEvent):
    """Event for data transfer and signaling actions in the L{OutputWin}"""
    def __init__(self, etype, eid, value=''):
        """Creates the event object"""
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value

#-----------------------------------------------------------------------------#

class OutputWindow(wx.Panel):
    """Output window that contains the configuration controls and
    output buffer. This is the main object of this module. Its
    constructor returns a ui component that consists of a Panel
    with two subpanels, the top subpanel being a control/status bar
    and the buttom subpanel being an output display buffer.

    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes
        self._log = wx.GetApp().GetLog()    # Log
        self._ctrl = ConfigBar(self)        # Buffer Ctrl Bar
        self._buffer = OutputBuffer(self)   # Script output
        self._worker = None                 # Reference to worker thread
        self._abort = False                 # Flag to abort script
        self._temps = list()                # Temporary files

        # Layout
        self.__DoLayout()

        # Event Handlers
        self._mw = self.__FindMainWindow()
        if self._mw:
            self._mw.GetNotebook().Bind(flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED, 
                                        self.OnBufferChange)
        self.Bind(EVT_PROCESS_ABORT, lambda evt: self.Abort())
        self.Bind(EVT_PROCESS_CLEAR, lambda evt: self.Clear())
        self.Bind(EVT_PROCESS_START, self.OnRunScript)
        self.Bind(EVT_PROCESS_EXIT, self.OnEndScript)
        self._buffer.Bind(wx.stc.EVT_STC_HOTSPOT_CLICK, self.OnHotSpot)

    def __del__(self):
        """Cleanup any running processes on exit"""
        self._log("[PyRun][info] Output window deleted: %d" % self.GetId())

        # Alert any running thread(s) that they need to bail
        self._abort = True

        # Cleanup tempfiles
        self.__CleanupTemp()

        # Remove our event handler from chain of handlers in Editra's notebook
        # Necessary to prevent it from being called after we have been deleted
        # and raise all kinds of PyDeadObjectError's
        if self._mw:
            self._mw.GetNotebook().Unbind(flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED)

    def __DoLayout(self):
        """Layout/Create the windows controls"""
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.AddMany([(self._ctrl, 0, wx.EXPAND, 2), 
                        (self._buffer, 1, wx.EXPAND)])
        msizer.Add(vsizer, 1, wx.EXPAND)
        self.SetSizer(msizer)
        self.SetAutoLayout(True)

    def __CleanupTemp(self):
        """Cleanup any temporary files made by this control"""
        for fname in self._temps:
            try:
                os.remove(fname)
            except:
                continue

    def __DoOneRead(self, proc):
        """Read one line of output and post results. Returns True
        if there is more to read and False if there is not. This is
        a private function called by the worker thread to retrieve
        output.
        @param proc: process to read from

        """
        try:
            result = proc.stdout.readline()
        except (IOError, OSError):
            return False

        if result == "" or result == None:
            return False
        evt = OutputWinEvent(edEVT_UPDATE_TEXT, -1, result)
        wx.CallAfter(wx.PostEvent, self._buffer, evt)
        return True

    def __DoTempFile(self, txt):
        """Make or update a temporary file with the given text
        @param txt: text to write to tempfile
        @return: name of the tempfile to use

        """
        try:
            # Try to reuse an existing tempfile if possible
            if len(self._temps):
                rname = self._temps[0]
                tfile = open(rname, 'wb')
                tfile.write(txt)
                tfile.close()
            else:
                tfile = tempfile.mkstemp(suffix='.py')
                self._temps.append(tfile[1])
                rname = tfile[1]
                os.write(tfile[0], txt)
                os.close(tfile[0])

            self._ctrl.SetCurrentFile(rname)
        except Exception, msg:
            self._log("[PyRun][err] Tempfile create/open failed: %s" % str(msg))
            return ''
        else:
            return rname

    def __FindMainWindow(self):
        """Find the mainwindow of this control
        @return: MainWindow or None

        """
        def IsMainWin(win):
            if getattr(tlw, '__name__', '') == 'MainWindow':
                return True
            else:
                return False

        tlw = self.GetTopLevelParent()
        if IsMainWin(tlw):
            return tlw
        elif hasattr(tlw, 'GetParent'):
            tlw = tlw.GetParent()
            if IsMainWin(tlw):
                return tlw

        return None

    def __KillPid(self, pid):
        """Kill a process by process id
        @param pid: Id of process to kill

        """
        if wx.Platform in ['__WXMAC__', '__WXGTK__']:
            os.kill(pid, signal.SIGABRT)
            os.waitpid(pid, os.WNOHANG)
        else:
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)

    def _DoRunCmd(self, filename, execmd="python"):
        """This is a worker function that runs a python script on
        on a separate thread and posts the output back to the output
        buffer this requires that all interaction with the gui be
        done by posting events as apposed to accessing items directly.
        @param filename: full path to script to run
        @keyword execmd: python to execute script with

        """
        if filename == "":
            return ""

        filedir, filename = os.path.split(filename)
        filename = '"%s"' % filename
        command = "%s %s" % (execmd, filename)
        proc_env = self._PrepEnv()
        
        p = Popen(command, stdout=PIPE, stderr=STDOUT, 
                  shell=True, cwd=filedir, env=proc_env)

        evt = OutputWinEvent(edEVT_UPDATE_TEXT, -1, ">>> %s" % command + os.linesep)
        wx.CallAfter(wx.PostEvent, self._buffer, evt)


        # Read from stdout while there is output from process
        while True:
            if self._abort:
                self.__KillPid(p.pid)
                self.__DoOneRead(p)
                break
            else:
                try:
                    more = self.__DoOneRead(p)
                except wx.PyDeadObjectError:
                    # We are dead so kill process and return
                    self.__KillPid(p.pid)
                    return

                if not more:
                    break

        try:
            result = p.wait()
        except OSError:
            result = -1

        evt = OutputWinEvent(edEVT_UPDATE_TEXT, -1, ">>> Exit code: %d%s" % (result, os.linesep))
        wx.CallAfter(wx.PostEvent, self._buffer, evt)

        # Notify that proccess has exited
        evt = OutputWinEvent(edEVT_PROCESS_EXIT, -1)
        wx.CallAfter(wx.PostEvent, self, evt)

    def _GetEditraBuffTxt(self):
        """Try to get the contents of the currently selected buffer in Editra
        @return: string

        """
        if self._mw:
            return self._mw.GetNotebook().GetCurrentCtrl().GetText()
        else:
            return u''

    def _PrepEnv(self):
        """Create an environment for the process to run in
        @return: dict

        """
        if not hasattr(sys, 'frozen') or wx.Platform == '__WXMSW__':
            proc_env = os.environ.copy()
        else:
            proc_env = dict()

        proc_env['PYTHONUNBUFFERED'] = '1'
        return proc_env

    #---- OutputWin Public Member Functions ----#
    def Abort(self):
        """Abort the current process if one is running"""
        self._log("[PyRun][info] Aborting current script...")
        if self._worker is None:
            return

        # Flag desire to abort for worker thread to notice
        self._abort = True

        # Wait for it to die
        self._worker.join(1)
        if self._worker.isAlive():
            self._log("[PyRun][info] Forcing thread to stop")
            self._worker._Thread__stop()
        self._worker = None

        self._buffer.Stop()
        self._ctrl.Enable()

    def Clear(self):
        """Clears the current contents of the buffer"""
        self._buffer.Clear()

    def IsTempFile(self, fname):
        """Check whether a file is a temporary one or not
        @param fname: name of file to check
        @return: bool

        """
        return fname in self._temps

    def OnBufferChange(self, evt):
        """Update which script is associated with this output window
        @param evt: flatnotebook.EVT_FLATNOTEBOOK_PAGE_CHANGED

        """
        e_obj = evt.GetEventObject()
        cpage = e_obj.GetPage(evt.GetSelection())
        evt.Skip() # Skip early to prevent holding up the chain

        # Only do syncronize when this instance is the current selection
        # in the Shelf and that the buffer is recognized as python.
        if self.GetParent().GetCurrentPage() != self or \
           not _IsPython(cpage.GetLangId(), cpage.GetLine(0)):
            return

        if cpage and hasattr(cpage, 'GetFileName'):
            fname = cpage.GetFileName()
            if len(fname):
                self._ctrl.SetCurrentFile(fname)
            else:
                self.__DoTempFile(cpage.GetText())

    def OnEndScript(self, evt):
        """Handle when the process exits"""
        self._log("[PyRun][info] Script has finished")
        self._buffer.Stop()
        self._ctrl.Enable()

    def OnHotSpot(self, evt):
        """Handle clicks events on hotspots and excute the proper action
        @param evt: wx.stc.EVT_STC_HOTSPOT_CLICK

        """
        if self._mw is None:
            return

        line = self._buffer.LineFromPosition(evt.GetPosition())
        txt = self._buffer.GetLine(line)
        match = error_re.match(txt)
        if match:
            fname = match.group(1)
            try:
                line = max(int(match.group(2)) - 1, 0)
            except:
                line = 0

            if not os.path.isabs(fname):
                dname = os.path.split(self._ctrl.GetLastRun())[0]
                fname = os.path.join(dname, fname)

            nb = self._mw.GetNotebook()
            buffers = [ page.GetFileName() for page in nb.GetTextControls() ]
            if fname in buffers:
                page = buffers.index(fname)
                nb.SetSelection(page)
                nb.GetPage(page).GotoLine(line)
            else:
                nb.OnDrop([fname])
                nb.GetPage(nb.GetSelection()).GotoLine(line)

    def OnRunScript(self, evt):
        """Handle events posted by control bar to re-run the script"""
        script = evt.GetValue()
        if not len(script) or self.IsTempFile(script):
            script = self.__DoTempFile(self._GetEditraBuffTxt())
        self._log("[PyRun][info] Starting Script: %s..." % script)
        self.RunScript(script)
        self._ctrl.SetLastRun(script)

    def RunScript(self, fname):
        """Start the worker thread that runs the python script"""
        self._abort = False
        self._buffer.Clear()
        self._ctrl.SetCurrentFile(fname)
        self._ctrl.Disable()
        pyexe = self._ctrl.GetPythonCommand()
        if len(pyexe):
            Profile_Set(PYRUN_EXE, pyexe)
        else:
            pyexe = Profile_Get(PYRUN_EXE, 'str', 'python')

        # Start the worker thread
        self._log("[PyRun][info] Running script with command: %s" % pyexe)
        self._worker = threading.Thread(target=self._DoRunCmd, args=[fname, pyexe])
        self._worker.start()

        self._ctrl.SetLastRun(fname)
        self.Layout()
        wx.CallLater(150, self._buffer.Start, 300)

    def SetScript(self, fname):
        """Set the script that the window is currently associated with
        @param fname: path to script

        """
        self._ctrl.SetCurrentFile(fname)

#-----------------------------------------------------------------------------#

class OutputBuffer(wx.stc.StyledTextCtrl):
    """Output buffer to display results of running a script"""

    # OutputBuffer Style Specs
    STYLE_DEFAULT = 0
    STYLE_INFO    = 1
    STYLE_ERROR   = 2

    def __init__(self, parent):
        wx.stc.StyledTextCtrl.__init__(self, parent, style=wx.BORDER_SUNKEN)

        # Attributes
        self._log = wx.GetApp().GetLog()
        self._updates = list()
        self._timer = wx.Timer(self)

        # Setup
        self.__ConfigureSTC()

        # Event Handlers
        self.Bind(EVT_UPDATE_TEXT, self.OnUpdate)
        self.Bind(wx.EVT_TIMER, self.OnTimer)

    def __del__(self):
        """Ensure timer is cleaned up when we are deleted"""
        if self._timer.IsRunning():
            self._log("[PyRun][info] Stopping timer for %d" % self.GetId())
            self._timer.Stop()

    def __ConfigureSTC(self):
        """Setup the stc to behave/appear as we want it to 
        and define all styles used for giving the output context.

        """
        self.SetMargins(3, 3)
        self.SetMarginWidth(0, 0)
        self.SetMarginWidth(1, 0)

        self.SetLayoutCache(wx.stc.STC_CACHE_DOCUMENT)
        self.SetReadOnly(True)
        
        #self.SetEndAtLastLine(False)
        self.SetVisiblePolicy(1, wx.stc.STC_VISIBLE_STRICT)

        # Define Styles
        font = wx.Font(11, wx.FONTFAMILY_MODERN, 
                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        face = font.GetFaceName()
        size = font.GetPointSize()
        back = "#FFFFFF"
        
        # Custom Styles
        self.StyleSetSpec(self.STYLE_DEFAULT, 
                          "face:%s,size:%d,fore:#000000,back:%s" % (face, size, back))
        self.StyleSetSpec(self.STYLE_INFO,
                          "face:%s,size:%d,fore:#0000FF,back:%s" % (face, size, back))
        self.StyleSetSpec(self.STYLE_ERROR, 
                          "face:%s,size:%d,fore:#FF0000,back:%s" % (face, size, back))
        self.StyleSetHotSpot(self.STYLE_ERROR, True)

        # Default Styles
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, \
                          "face:%s,size:%d,fore:#000000,back:%s" % (face, size, back))
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, \
                          "face:%s,size:%d,fore:#000000,back:%s" % (face, size, back))
        self.Colourise(0, -1)

    def __PutText(self, txt, ind):
        """Needed for doing a callafter to reduce CGContext warnings on mac
        @param txt: String to append
        @param ind: index in update buffer

        """
        self.SetReadOnly(False)
        start = self.GetCurrentPos()
        self.AppendText(txt)
        self.GotoPos(self.GetLength())
        self._updates = self._updates[ind:]
        self.ApplyStyles(start, txt)
        self.SetReadOnly(True)

    def ApplyStyles(self, start, txt):
        """Apply coloring to text starting at start position
        @param start: start position in buffer
        @param txt: text to locate styling point in

        """
        for group in error_re.finditer(txt):
            sty_s = start + group.start()
            sty_e = start + group.end()
            self.StartStyling(sty_s, 0xff)
            self.SetStyling(sty_e - sty_s, self.STYLE_ERROR)
        else:
            for info in info_re.finditer(txt):
                sty_s = start + info.start()
                sty_e = start + info.end()
                self.StartStyling(sty_s, 0xff)
                self.SetStyling(sty_e - sty_s, self.STYLE_INFO)

    def Clear(self):
        """Clear the Buffer"""
        self.SetReadOnly(False)
        self.SetText('')
        self.SetReadOnly(False)

    def OnTimer(self, evt):
        """Process and display text from the update buffer
        @note: this gets called many times while running thus needs to
               return quickly to avoid blocking the ui.

        """
        ind = len(self._updates)
        if ind:
            # CallAfter is mostly for Mac to avoid CG errors
            wx.CallAfter(self.__PutText, ''.join(self._updates), ind)
        else:
            pass

    def OnUpdate(self, evt):
        """Buffer output before adding to window"""
        self._updates.append(evt.GetValue())
        
    def Start(self, interval):
        """Start the window's timer to check for updates
        @param interval: interval in milliseconds to do updates

        """
        self._log("[PyRun][info] Starting output to buffer on timer")
        self._timer.Start(interval)

    def Stop(self):
        """Stop the update process of the buffer"""
        self._log("[PyRun][info] Process Finished, stopping timer")

        # Dump any output still left in tmp buffer before stopping
        self.OnTimer(None)
        self._timer.Stop()
        self.SetReadOnly(True)

#-----------------------------------------------------------------------------#
ID_RUN_BTN = wx.NewId()
ID_CLEAR_BTN = wx.NewId()
class ConfigBar(wx.Panel):
    """Small configuration bar for showing what python is being
    used to run the script, as well as allowing it to be changed,
    and allows for re-running the script.

    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(-1, 28))

        # Attributes
        pyexe = Profile_Get(PYRUN_EXE, 'str', 'python')
        if not len(pyexe):
            pyexe = 'python'
        self._pbuff = wx.TextCtrl(self, value=pyexe)
        self._pbuff.SetMinSize((150, -1))
        self._pbuff.SetMaxSize((-1, 20))
        self._pbuff.SetToolTipString(_("Path to Python executable or name of executable to use"))
        self._fname = ''                                # Current File
        self._lastexec = ''                             # Last Run File
        self._needs_update = False                      # Label needs update?
        self._cfile = wx.StaticText(self, label='')     # Current File Display
        self._run = wx.Button(self, ID_RUN_BTN, _("Run Script"))
        self._clear = wx.Button(self, ID_CLEAR_BTN, label=_("Clear"))
        if wx.Platform == '__WXMAC__':
            self._pbuff.SetFont(wx.SMALL_FONT)
            self._pbuff.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._run.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._clear.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, id=ID_RUN_BTN)
        self.Bind(wx.EVT_BUTTON, self.OnButton, id=ID_CLEAR_BTN)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def __DoLayout(self):
        """Layout the controls in the bar"""
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        lbl = wx.StaticText(self, label=_("Python Executable") + u':')

        if wx.Platform == '__WXMAC__':
            lbl.SetFont(wx.SMALL_FONT)
            self._cfile.SetFont(wx.SMALL_FONT)

        hsizer.AddMany([((20, 28)), (lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5)), (self._pbuff, 0, wx.ALIGN_CENTER_VERTICAL),
                        ((20, 15)), (self._cfile, 0, wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5), 1, wx.EXPAND), (self._run, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
                        ((5,5)), (self._clear, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
                        ((8, 8))])
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

    def _UpdateFileDisplay(self):
        """Update the file name displayed in bar
        @note: update only takes place if bar enabled otherwise a flag is
               set to tell the bar to update when it is next enabled.

        """
        if self.IsEnabled():
            script = os.path.split(self._fname)[1]
            self._cfile.SetLabel(_("Current Script: %s") % script)
            self.GetParent().Layout()
            self.Layout()
        else:
            self._needs_update = True

    def Disable(self):
        """Disable the panel except for the button which is
        changed to an abort button.

        """
        for child in self.GetChildren():
            c_id = child.GetId()
            if c_id == ID_CLEAR_BTN:
                continue
            elif c_id == ID_RUN_BTN:
                child.SetLabel(_("Abort"))
            else:
                child.Disable()

    def Enable(self, enable=True):
        """Enable all items in the bar and change the button back
        to Run Script.

        """
        for child in self.GetChildren():
            if child.GetId() == ID_RUN_BTN:
                child.SetLabel(_("Run Script"))
            else:
                child.Enable(enable)

        if self._needs_update:
            self._needs_update = False
            self._UpdateFileDisplay()

    def GetCurrentFile(self):
        """Get the current file that is shown in the display
        @return: string

        """
        return self._fname

    def GetLastRun(self):
        """Get the path to the file of the last script that was run
        or set by L{SetLastRun}.
        @return: string of path to file

        """
        return self._lastexec

    def GetPythonCommand(self):
        """Get the command that is set in the text control or
        the default value if nothing is set.
        @return: python command string

        """
        cmd = self._pbuff.GetValue().strip()
        if not len(cmd):
            return Profile_Get(PYRUN_EXE, 'str', 'python')
        else:
            return cmd

    def IsEnabled(self):
        """Check whether the control is active and ready to recieve input"""
        for state in [ child.IsEnabled() for child in self.GetChildren() ]:
            if not state:
                return False

        return True

    def OnButton(self, evt):
        """Post an event to request the script be run again or aborted"""
        e_id = evt.GetId()
        lbl = evt.GetEventObject().GetLabel()
        if e_id == ID_RUN_BTN:
            if lbl == _("Run Script"):
                sevt = OutputWinEvent(edEVT_PROCESS_START, self.GetId(), self._fname)
            else:
                sevt = OutputWinEvent(edEVT_PROCESS_ABORT, self.GetId())
        elif e_id == ID_CLEAR_BTN:
            sevt = OutputWinEvent(edEVT_PROCESS_CLEAR, self.GetId())
        else:
            evt.Skip()
            return

        wx.PostEvent(self.GetParent(), sevt)

    def OnPaint(self, evt):
        """Paints the background of the bar with a nice gradient.
        @param evt: Event that called this handler
        @type evt: wx.PaintEvent

        """
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        col2 = util.AdjustColour(col1, 50)
        col1 = util.AdjustColour(col1, -60)
        grad = gc.CreateLinearGradientBrush(0, 1, 0, 24, col2, col1)
        rect = self.GetClientRect()

        pen_col = tuple([min(190, x) for x in util.AdjustColour(col1, -60)])
        gc.SetPen(gc.CreatePen(wx.Pen(pen_col, 1)))
        gc.SetBrush(grad)
        gc.DrawRectangle(0, 1, rect.width - 0.5, rect.height - 0.5)

        evt.Skip()

    def SetCurrentFile(self, fname):
        """Set the name of the current file for the display
        @param fname: name of script to change to
        @note: the update of the display is delayed if a script is currently
               running, the display will update once the script has halted.

        """
        self._fname = fname
        self._UpdateFileDisplay()

    def SetLastRun(self, fname):
        """Set the value of the last run script
        @param fname: name of script that was last run

        """
        self._lastexec = fname

#-----------------------------------------------------------------------------#
# Misc Utility Functions
def _IsPython(lang, line):
    """Try to determin if the passed in buffer is python or not
    @param page: ref to a text buffer in Editra.

    """
    if lang == synglob.ID_LANG_PYTHON or \
       line.startswith('#!') and 'python' in line.lower():
        return True
    else:
        return False
