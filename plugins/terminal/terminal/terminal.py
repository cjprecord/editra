# -*- coding: utf-8 -*-
###############################################################################
# Name: terminal.py                                                           #
# Purpose: Provides a terminal widget that can be embedded in any wxWidgets   #
#          window or run alone as its own shell window.                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
This script started as an adaption of the vim plugin 'vimsh' by brian m sturk 
but has since been partially reimplemented to take advantage of newer libraries
and the features that wx offers.

It currently should run on any unix like operating system that supports:
    - wxPython
    - Psuedo TTY's

On windows things are basically working now but support is not as good as it is
on unix like operating systems.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: terminal.py 669 2008-12-05 02:18:30Z CodyPrecord $"
__revision__ = "$Revision: 669 $"

#-----------------------------------------------------------------------------#
# Imports

import sys
import os
import signal
#import threading
import re
import time
import wx
import wx.stc

# On windows need to use pipes as pty's are not available
try:
    if sys.platform == 'win32':
        import popen2
        import stat
        import msvcrt
        import ctypes
        USE_PTY = False
    else:
        import pty
        import tty
        import select
        USE_PTY = True
except ImportError, msg:
    print "[terminal] Error importing required libs: %s" % str(msg)

#-----------------------------------------------------------------------------#
# Globals

#---- Variables ----#
DEBUG = True
MAX_HIST = 50       # Max command history to save

if sys.platform == 'win32':
    SHELL = 'cmd.exe'
else:
    if 'SHELL' in os.environ:
        SHELL = os.environ['SHELL']
    else:
        SHELL = '/bin/sh'
#---- End Variables ----#

#---- Callables ----#
_ = wx.GetTranslation

#---- End Callables ----#

#---- ANSI color code support ----#
# ANSI_FORE_BLACK   = 1
# ANSI_FORE_RED     = 2
# ANSI_FORE_GREEN   = 3
# ANSI_FORE_YELLOW  = 4
# ANSI_FORE_BLUE    = 5
# ANSI_FORE_MAGENTA = 6
# ANSI_FORE_CYAN    = 7
# ANSI_FORE_WHITE   = 8

# ANSI_BACK_BLACK
# ANSI_BACK_RED
# ANSI_BACK_GREEN
# ANSI_BACK_YELLOW
# ANSI_BACK_BLUE
# ANSI_BACK_MAGENTA
# ANSI_BACK_CYAN
# ANSI_BACK_WHITE

ANSI = {
        ## Forground colours ##
        '[30m' : (1, '#000000'),
        '[31m' : (2, '#FF0000'),
        '[32m' : (3, '#00FF00'),
        '[33m' : (4, '#FFFF00'),  # Yellow
        '[34m' : (5, '#0000FF'),
        '[35m' : (6, '#FF00FF'),
        '[36m' : (7, '#00FFFF'),
        '[37m' : (8, '#FFFFFF'),
        #'[39m' : default

        ## Background colour ##
        '[40m' : (011, '#000000'),  # Black
        '[41m' : (012, '#FF0000'),  # Red
        '[42m' : (013, '#00FF00'),  # Green
        '[43m' : (014, '#FFFF00'),  # Yellow
        '[44m' : (015, '#0000FF'),  # Blue
        '[45m' : (016, '#FF00FF'),  # Magenta
        '[46m' : (017, '#00FFFF'),  # Cyan
        '[47m' : (020, '#FFFFFF'),  # White
        #'[49m' : default
        }

RE_COLOUR_START = re.compile('\[[34][0-9]m')
RE_COLOUR_FORE = re.compile('\[3[0-9]m')
RE_COLOUR_BLOCK = re.compile('\[[34][0-9]m*.*?\[m')
RE_COLOUR_END = '[m'
RE_CLEAR_ESC = re.compile('\[[0-9]+m')
#---- End ANSI Colour Support ----#

#---- Font Settings ----#
# TODO make configurable from interface
FONT = None
FONT_FACE = None
FONT_SIZE = None
#----- End Font Settings ----#

#-----------------------------------------------------------------------------#

class Xterm(wx.stc.StyledTextCtrl):
    """Creates a graphical terminal that works like the system shell
    that it is running on (bash, command, ect...).

    """
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=0):
        wx.stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        # Attributes
        ##  The lower this number is the more responsive some commands
        ##  may be ( printing prompt, ls ), but also the quicker others
        ##  may timeout reading their output ( ping, ftp )
        self.delay = 0.03
        self._fpos = 0          # First allowed cursor position
        self._exited = False    # Is shell still running
        self._setspecs = [0]
        self._history = dict(cmds=[''], index=-1, lastexe='')  # Command history
        self._menu = None

        # Setup
        self.__Configure()
        self.__ConfigureStyles()
        self.__ConfigureKeyCmds()
        self._SetupPTY()

        #---- Event Handlers ----#
        # General Events
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Stc events
        self.Bind(wx.stc.EVT_STC_DO_DROP, self.OnDrop)

        # Key events
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        # Menu Events
        self.Bind(wx.EVT_MENU, lambda evt: self.Cut(), id=wx.ID_CUT)
        self.Bind(wx.EVT_MENU, lambda evt: self.Copy(), id=wx.ID_COPY)
        self.Bind(wx.EVT_MENU, lambda evt: self.Paste(), id=wx.ID_PASTE)
        self.Bind(wx.EVT_MENU, lambda evt: self.SelectAll(), id=wx.ID_SELECTALL)

        # Mouse Events
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
#         self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

    def __del__(self):
        DebugLog("[terminal][info] Terminal instance is being deleted")
        self._CleanUp()

    def __ConfigureKeyCmds(self):
        """Clear the builtin keybindings that we dont want"""
        self.CmdKeyClear(ord('U'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('Z'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(wx.WXK_BACK, wx.stc.STC_SCMOD_CTRL | \
                                      wx.stc.STC_SCMOD_SHIFT)
        self.CmdKeyClear(wx.WXK_DELETE, wx.stc.STC_SCMOD_CTRL | \
                                        wx.stc.STC_SCMOD_SHIFT)
        self.CmdKeyClear(ord('['), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord(']'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('\\'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('/'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('L'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('D'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('Y'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(ord('T'), wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(wx.WXK_TAB, wx.stc.STC_SCMOD_NORM)

    def __Configure(self):
        """Configure the base settings of the control"""
        if wx.Platform == '__WXMSW__':
            self.SetEOLMode(wx.stc.STC_EOL_CRLF)
        else:
            self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetViewWhiteSpace(False)
        self.SetTabWidth(0)
        self.SetUseTabs(False)
        self.SetWrapMode(True)
        self.SetEndAtLastLine(False)
        self.SetVisiblePolicy(1, wx.stc.STC_VISIBLE_STRICT)

    def __ConfigureStyles(self):
        """Configure the text coloring of the terminal"""
        # Clear Styles
        self.StyleResetDefault()
        self.StyleClearAll()

        # Set margins
        self.SetMargins(4, 4)
        self.SetMarginWidth(wx.stc.STC_MARGIN_NUMBER, 0)

        # Caret styles
        self.SetCaretWidth(4)
        self.SetCaretForeground(wx.NamedColor("white"))

        # Configure text styles
        # TODO make this configurable
        fore = "#FFFFFF" #"#000000"
        back = "#000000" #"#DBE0C4"
        global FONT
        global FONT_SIZE
        global FONT_FACE
        FONT = wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, 
                               wx.FONTWEIGHT_NORMAL)
        FONT_FACE = FONT.GetFaceName()
        FONT_SIZE = FONT.GetPointSize()
        self.StyleSetSpec(0, "face:%s,size:%d,fore:%s,back:%s,bold" % \
                             (FONT_FACE, FONT_SIZE, fore, back))
        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, \
                          "face:%s,size:%d,fore:%s,back:%s,bold" % \
                          (FONT_FACE, FONT_SIZE, fore, back))
        self.StyleSetSpec(wx.stc.STC_STYLE_CONTROLCHAR, \
                          "face:%s,size:%d,fore:%s,back:%s" % \
                          (FONT_FACE, FONT_SIZE, fore, back))
        self.Colourise(0, -1)

    #---- Protected Members ----#
    def _ApplyStyles(self, data):
        """Apply style bytes to regions of text that require them, starting
        at self._fpos and using the postional data as on offset from that point.

        @param data: list of tuples [ (style_start, colour, style_end) ]

        """
        spec = 0
        for pos in data:
            if len(pos[1]) > 1:
                spec = ANSI[pos[1][1]][0] | ANSI[pos[1][0]][0]
            elif len(pos[1]):
                spec = ANSI[pos[1][0]][0]
            else:
                pass

            if spec not in self._setspecs:
                DebugLog("[terminal][styles] Setting Spec: %d" % spec)
                self._setspecs.append(spec)
                if len(pos[1]) > 1:
                    if RE_COLOUR_FORE.match(pos[1][0]):
                        fore = ANSI[pos[1][0]][1]
                        back = ANSI[pos[1][1]][1]
                    else:
                        fore = ANSI[pos[1][1]][1]
                        back = ANSI[pos[1][0]][1]

                    self.StyleSetSpec(spec, 
                                      "fore:%s,back:%s,face:%s,size:%d" % \
                                      (fore, back, FONT_FACE, FONT_SIZE))
                else:
                    self.StyleSetSpec(spec, 
                                      "fore:%s,back:#000000,face:%s,size:%d" % \
                                     (ANSI[pos[1][0]][1], FONT_FACE, FONT_SIZE))

            # Adjust styling start position if necessary
            spos = self._fpos + pos[0]
            if unichr(self.GetCharAt(spos)).isspace():
                spos += 1

            # Set style bytes for a given region
            self.StartStyling(spos, 0xff)
            self.SetStyling(pos[2] - pos[0] + 1, spec)

    def _CheckAfterExe(self):
        """Check std out for anything left after an execution"""
        DebugLog("[terminal][info] Checking after cmd execution")
        self.Read()
        self.CheckForPassword()

    def _CleanUp(self):
        """Cleanup open file descriptors"""
        if self._exited:
            DebugLog("[terminal][exit] Already exited")
            return

        try:
            DebugLog("[terminal][exit] Closing FD and killing process")
            if not USE_PTY:
                os.close(self.ind)
                os.close(self.outd)

            os.close(self.errd)       ##  all the same if pty
            if USE_PTY:
                os.kill(self.pid, signal.SIGKILL)
                time.sleep(self.delay) # give some time for the process to die

        except Exception, msg:
            DebugLog("[terminal][err] %s" % str(msg))

        DebugLog("[terminal][cleanup] Finished Cleanup")

    def _EndRead(self, any_lines_read):
        """Finish up after reading"""
        # Mark earliest valid cursor position in buffer
        self._fpos = self.GetCurrentPos()
        if (not USE_PTY and any_lines_read):
            self.LineDelete()
            DebugLog("[terminal][endread] Deleted trailing line")
            self._fpos = self.GetCurrentPos()

        DebugLog("[terminal][info] Set valid cursor to > %d" % self._fpos)
        self.PrintPrompt()
        self.EnsureCaretVisible()
        self.EnsureVisibleEnforcePolicy(self.GetCurrentLine())

    def _HandleExit(self, cmd):
        """Handle closing the shell connection"""
        ##  Exit was typed, could be the spawned shell, or a subprocess like
        ##  telnet/ssh/etc.
        DebugLog("[terminal][exit] Exiting process")
        if not self._exited:
            try:
                DebugLog("[terminal][exit] Shell still around, trying to close")
                self.Write(cmd + os.linesep)
                self._CheckAfterExe()
            except Exception, msg:            
                DebugLog("[terminal][err] Exception on exit: %s" % str(msg))

                ## shell exited, self._exited may not have been set yet in
                ## sigchld_handler.
                DebugLog("[terminal][exit] Shell Exited is: " + str(self._exited))
                self.ExitShell()

    def _ProcessRead(self, lines):
        """Process the raw lines from stdout"""
        DebugLog("[terminal][info] Processing Read...")
        lines_to_print = lines.split(os.linesep)

        #  Filter out invalid blank lines from begining/end input
        if sys.platform == 'win32':
            m = re.search(re.escape(self._history['lastexe'].strip()), 
                                    lines_to_print[0])
            if m != None or lines_to_print[0] == "":
                DebugLog('[terminal][info] Win32, removing leading blank line')
                lines_to_print = lines_to_print[ 1: ]

        # Check for extra blank line at end
        num_lines = len(lines_to_print)
        if num_lines > 1:
            last_line = lines_to_print[num_lines - 1].strip()

            if last_line == "":
                lines_to_print = lines_to_print[ :-1 ]

        # Look on StdErr for any error output
        errors = self.CheckStdErr()
        if errors:
            DebugLog("[terminal][err] Process Read stderr --> " + '\n'.join(errors))
            lines_to_print = errors + lines_to_print

        return lines_to_print

    def _SetupPTY(self):
        """Setup the connection to the real terminal"""
        if USE_PTY:
            self.master, pty_name = pty.openpty()
            DebugLog("[terminal][info] Slave Pty name: " + str(pty_name))

            self.pid, self.fd = pty.fork()
            print "GRRR", self.fd, self.pid, "WTF"

            self.outd = self.fd
            self.ind  = self.fd
            self.errd = self.fd

#            signal.signal(signal.SIGCHLD, self._SigChildHandler)
            if self.pid == 0:
                attrs = tty.tcgetattr(1)

                attrs[6][tty.VMIN]  = 1
                attrs[6][tty.VTIME] = 0
                attrs[0] = attrs[0] | tty.BRKINT
                attrs[0] = attrs[0] & tty.IGNBRK
                attrs[3] = attrs[3] & ~tty.ICANON & ~tty.ECHO

                tty.tcsetattr(1, tty.TCSANOW, attrs)
#                 cwd = os.path.curdir
                os.chdir(wx.GetHomeDir())
#                 pty.spawn([SHELL, "-l"])
                os.execv(SHELL, [SHELL, '-l'])
#                 os.chdir(cwd)

            else:
                try:
                    attrs = tty.tcgetattr(self.fd)
                    termios_keys = attrs[6]
                except:
                    DebugLog('[terminal][err] tcgetattr failed')
                    return

                #  Get *real* key-sequence for standard input keys, i.e. EOF
                self.eof_key   = termios_keys[tty.VEOF]
                self.eol_key   = termios_keys[tty.VEOL]
                self.erase_key = termios_keys[tty.VERASE]
                self.intr_key  = termios_keys[tty.VINTR]
                self.kill_key  = termios_keys[tty.VKILL]
                self.susp_key  = termios_keys[tty.VSUSP]
        else:
            ##  Use pipes on Win32. not as reliable/nice but 
            ##  works with limitations.
            self.delay = 0.15

            try:
                import win32pipe
                DebugLog('[terminal][info] using windows extensions')
                self.stdin, self.stdout, self.stderr = win32pipe.popen3(SHELL)
            except ImportError:
                DebugLog('[terminal][info] not using windows extensions')
                self.stdout, self.stdin, self.stderr = popen2.popen3(SHELL, -1, 'b')

            self.outd = self.stdout.fileno()
            self.ind  = self.stdin.fileno()
            self.errd = self.stderr.fileno()

            self.intr_key = ''
            self.eof_key  = ''

    def _SigChildHandler(self, sig, frame):
        """Child process signal handler"""
        DebugLog("[terminal][info] caught SIGCHLD")
        self._WaitPid()

    def _WaitPid(self):
        """Mark the original shell process as having gone away if it
        has exited.

        """
        if os.waitpid(self.pid, os.WNOHANG)[0]:
            self._exited = True
            DebugLog("[terminal][waitpid] Shell process has exited")
        else:
            DebugLog("[terminal][waitpid] Shell process hasn't exited")

    #---- End Protected Members ----#

    #---- Public Members ----#
    def AddCmdHistory(self, cmd):
        """Add a command to the history index so it can be quickly
        recalled by using the up/down keys.

        """
        if cmd.isspace():
            return

        if len(self._history['cmds']) > MAX_HIST:
            self._history['cmds'].pop()
        self._history['cmds'].insert(0, cmd)
        self._history['index'] = -1

    def CanCopy(self):
        """Check if copy is possible"""
        return self.GetSelectionStart() != self.GetSelectionEnd()

    def CanCut(self):
        """Check if selection is valid to allow for cutting"""
        s_start = self.GetSelectionStart()
        s_end = self.GetSelectionEnd()
        return s_start != s_end and s_start >= self._fpos and s_end >= self._fpos

    def CheckForPassword(self):
        """Check if the shell is waiting for a password or not"""
        prev_line = self.GetLine(self.GetCurrentLine() - 1)
        for regex in ['^\s*Password:', 'password:', 'Password required']:
            if re.search(regex, prev_line):
                try:
                    print "FIX ME: CheckForPassword"
                except KeyboardInterrupt:
                    return

                # send the password to the 
#                 self.ExecuteCmd([password])

    def CheckStdErr(self):
        """Check for errors in the shell"""
        errors  = ''
        if sys.platform == 'win32':
            err_txt  = self.PipeRead(self.errd, 0)
            errors   = err_txt.split(os.linesep)

            num_lines = len(errors)
            last_line = errors[num_lines - 1].strip()

            if last_line == "":
                errors = errors[:-1]

        return errors

    def ClearScreen(self):
        """Clear the screen so that all commands are scrolled out of
        view and a new prompt is shown on the top of the screen.

        """
        self.AppendText(os.linesep * 5)
        self.Write(os.linesep)
        self._CheckAfterExe()
        self.Freeze()
        wx.PostEvent(self, wx.ScrollEvent(wx.wxEVT_SCROLLWIN_PAGEDOWN, 
                                          self.GetId(), orient=wx.VERTICAL))
        wx.CallAfter(self.Thaw)

    def ExecuteCmd(self, cmd=None, null=True):
        """Run the command entered in the buffer
        @keyword cmd: send a specified command
        @keyword null: should the command be null terminated

        """
        DebugLog("[terminal][exec] Running command: %s" % str(cmd))

        try:
            # Get text from prompt to eol when no command is given
            if cmd is None:
                cmd = self.GetTextRange(self._fpos, self.GetLength())

            # Move output position past input command
            self._fpos = self.GetLength()

            # Process command
            if len(cmd) and cmd[-1] != '\t':
                cmd = cmd.strip()

            if re.search(r'^\s*\bclear\b', cmd) or re.search(r'^\s*\bcls\b', cmd):
                DebugLog('[terminal][exec] Clear Screen')
                self.ClearScreen()
            elif re.search(r'^\s*\exit\b', cmd):
                DebugLog('[terminal][exec] Exit terminal session')
                self._HandleExit(cmd)
                self.SetCaretForeground(wx.BLACK)
            else:
                if null:
                    self.Write(cmd + os.linesep)
                else:
                    self.Write(cmd)

                self._history['lastexe'] = cmd
                self._CheckAfterExe()

            if len(cmd) and cmd != self._history['cmds'][0]:
                self.AddCmdHistory(cmd)
            self._history['lastexe'] = cmd

        except KeyboardInterrupt:
            pass

    def ExitShell(self):
        """Cause the shell to exit"""
        if not self._exited:
            self._CleanUp()

        self.PrintLines(["[process complete]" + os.linesep,])
        self.SetReadOnly(True)

    def GetNextCommand(self):
        """Get the next command from history based on the current
        position in the history list. If the list is already at the
        begining then an empty command will be returned.

        @postcondition: current history postion is decremented towards 0
        @return: string

        """
        if self._history['index'] > -1:
            self._history['index'] -= 1

        index = self._history['index']
        if index == -1:
            return ''
        else:
            return self._history['cmds'][index]

    def GetPrevCommand(self):
        """Get the previous command from history based on the current
        position in the history list. If the list is already at the
        end then the oldest command will be returned.

        @postcondition: current history postion is decremented towards 0
        @return: string

        """
        if self._history['index'] < len(self._history['cmds']) - 1\
           and self._history['index'] < MAX_HIST:
            self._history['index'] += 1

        index = self._history['index']
        return self._history['cmds'][index]

    def NewPrompt(self):
        """Put a new prompt on the screen and make all text from end of
        prompt to left read only.

        """
        self.ExecuteCmd("")

    def OnContextMenu(self, evt):
        """Display the context menu"""
        if self._menu is None:
            self._menu = GetContextMenu()
        print "HELLO", self._menu
        self.PopupMenu(self._menu)

    def OnDrop(self, evt):
        """Handle drop events"""
        if evt.GetPosition() < self._fpos:
            evt.SetDragResult(wx.DragCancel)

    def OnIdle(self, evt):
        """While idle check for more output"""
        if not self._exited:
            self.Read()

    def OnKeyDown(self, evt):
        """Handle key down events"""
        if self._exited:
            return

        key = evt.GetKeyCode()
        if key == wx.WXK_RETURN:
            self.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
            self.ExecuteCmd()
        elif key == wx.WXK_TAB:
            # TODO Tab Completion
#             self.ExecuteCmd(self.GetTextRange(self._fpos, 
#                              self.GetCurrentPos()) + '\t', 0)
            pass
        elif key in [wx.WXK_UP, wx.WXK_NUMPAD_UP]:
            # Cycle through previous command history
            cmd = self.GetPrevCommand()
            self.SetCommand(cmd)
        elif key in [wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN]:
            # Cycle towards most recent commands in history
            cmd = self.GetNextCommand()
            self.SetCommand(cmd)
        elif key in [wx.WXK_LEFT, wx.WXK_NUMPAD_LEFT, 
                     wx.WXK_BACK, wx.WXK_DELETE]:
            if self.GetCurrentPos() > self._fpos:
                evt.Skip()
        elif key == wx.WXK_HOME:
            # Go Prompt Start
            self.GotoPos(self._fpos)
        else:
            evt.Skip()

    def OnChar(self, evt):
        """Handle character enter events"""
        # Dont allow editing of earlier portion of buffer
        if self.GetCurrentPos() < self._fpos:
            return
        evt.Skip()

    def OnKeyUp(self, evt):
        """Handle when the key comes up"""
        key = evt.GetKeyCode()
        sel_s, sel_e = self.GetSelection()
        if evt.ControlDown() and key == ord('C') and sel_s == sel_e:
            self.ExecuteCmd(self.intr_key, null=False)
        else:
            evt.Skip()

    def OnLeftDown(self, evt):
        """Set selection anchor"""
        pos = evt.GetPosition()
        self.SetSelectionStart(self.PositionFromPoint(pos))

    def OnLeftUp(self, evt):
        """Check click position to ensure caret doesn't 
        move to invalid position.

        """
        evt.Skip()
        pos = evt.GetPosition()
        sel_s = self.GetSelectionStart()
        sel_e = self.GetSelectionEnd()
        if (self._fpos > self.PositionFromPoint(pos)) and (sel_s == sel_e):
            wx.CallAfter(self.GotoPos, self._fpos)

    def OnUpdateUI(self, evt):
        """Enable or disable menu events"""
        e_id = evt.GetId()
        if e_id == wx.ID_CUT:
            evt.Enable(self.CanCut())
        elif e_id == wx.ID_COPY:
            evt.Enable(self.CanCopy())
        elif e_id == wx.ID_PASTE:
            evt.Enable(self.CanPaste())
        else:
            evt.Skip()

    def PrintLines(self, lines):
        """Print lines to the terminal buffer
        @param lines: list of strings

        """
        if len(lines) and lines[0].strip() == self._history['lastexe'] .strip():
            lines.pop(0)

        for line in lines:
            DebugLog("[terminal][print] Current line is --> %s" % line)
            m = False
            if len(line) > 2 and "\r" in line[-2:]:
                line = line.rstrip()
                m = True

            # Parse ANSI escape sequences
            need_style = False
            if r'' in line:
                DebugLog('[terminal][print] found ansi escape sequence(s)')
                # Construct a list of [ (style_start, (colours), style_end) ]
                # where the start end positions are offsets of the curent _fpos
                c_items = re.findall(RE_COLOUR_BLOCK, line)
                tmp = line
                positions = list()
                for pat in c_items:
                    ind = tmp.find(pat)
                    colors = re.findall(RE_COLOUR_START, pat)
                    tpat = pat
                    for color in colors:
                        tpat = tpat.replace(color, '')
                    tpat = tpat.replace(RE_COLOUR_END, '')
                    tmp = tmp.replace(pat, tpat, 1).replace(RE_COLOUR_END, '', 1)
                    positions.append((ind, colors, (ind + len(tpat) - 1)))

                # Try to remove any remaining escape sequences
                line = tmp.replace(RE_COLOUR_END, '')
                line = re.sub(RE_COLOUR_START, '', line)
                line = re.sub(RE_CLEAR_ESC, '', line)
                
                need_style = True

            # Put text in buffer
            self.AppendText(line)

            # Apply any colouring that is needed
            if need_style:
                DebugLog('[terminal][print] applying styles to output string')
                self._ApplyStyles(positions)

            # Move cursor to end of buffer
            self._fpos = self.GetLength()
            self.GotoPos(self._fpos)

            ##  If there's a '\n' or using pipes and it's not the last line
            if not USE_PTY or m:
                DebugLog("[terminal][print] Appending new line since ^M or not using pty")
                self.AppendText(os.linesep)

    def PrintPrompt(self):
        """Construct a windows prompt and print it to the screen.
        Has no affect on other platforms as their prompt can be read from
        the screen.

        """
        if wx.Platform != '__WXMSW__':
            return
        else:
            cmd = self._history['lastexe']
            if cmd.lower().startswith('cd '):
                try:
                    os.chdir(cmd[2:].strip())
                except:
                    pass

            self.AppendText(u"%s>" % os.getcwd())
            self._fpos = self.GetLength()
            self.GotoPos(self._fpos)
            self.EnsureCaretVisible()

    def PipeRead(self, pipe, minimum_to_read):
        """Read from pipe, used on Windows. This is needed because select
        can only be used with sockets on Windows and not with any other type
        of file descriptor.
        @param pipe: Pipe to read from
        @param minimum_to_read: minimum bytes to read at one time

        """
        DebugLog("[terminal][pipe] minimum to read is " + str(minimum_to_read))

        time.sleep(self.delay)
        data = u''

        # Take a peek to see if any output is available
        try:
            handle = msvcrt.get_osfhandle(pipe)
            avail = ctypes.c_long()
            ctypes.windll.kernel32.PeekNamedPipe(handle, None, 0, 0,
                                                 ctypes.byref(avail), None)
        except IOError, msg:
            DebugLog("[terminal][err] Pipe read failed: %s" % msg)
            return data

        count = avail.value
        DebugLog("[terminal][pipe] PeekNamedPipe is " + str(count))

        # If there is some output start reading it
        while (count > 0):
            tmp = os.read(pipe, 32)
            data += tmp

            if len(tmp) == 0:
                DebugLog("[terminal][pipe] count %s but nothing read" % str(count))
                break

            #  Be sure to break the read, if asked to do so,
            #  after we've read in a line termination.
            if minimum_to_read != 0 and len(data) > 0 and data[len(data) - 1] == os.linesep:
                if len(data) >= minimum_to_read:
                    DebugLog("[terminal][pipe] read minimum and found termination")
                    break
                else:
                    DebugLog("[terminal][pipe] more data to read: count is " + str(count))

            # Check for more output
            avail = ctypes.c_long()
            ctypes.windll.kernel32.PeekNamedPipe(handle, None, 0, 0,
                                             ctypes.byref(avail), None)
            count = avail.value

        return data

    def Read(self):
        """Read output from stdin"""
        if self._exited:
            return

        num_iterations = 0  #  counter for periodic redraw
        any_lines_read = 0  #  sentinel for reading anything at all

        lines = ''
        while 1:
            if USE_PTY:
                try:
                    r = select.select([self.outd], [], [], self.delay)[0]
                except select.error, msg:
                    DebugLog("[terminal][err] Select failed: %s" % str(msg))
                    r = [1, ]
            else:
                r = [1, ]  # pipes, unused

            for file_iter in r:
                if USE_PTY:
                    tmp = os.read(self.outd, 32)
                else:
                    tmp = self.PipeRead(self.outd, 2048)

                lines += tmp
                if tmp == '':
                    DebugLog('[terminal][read] No more data on stdout Read')
                    r = []
                    break

                any_lines_read  = 1 
                num_iterations += 1

            if not len(r) and len(lines):
                DebugLog('[terminal][read] End of Read, starting processing and printing' )
                lines = self._ProcessRead(lines)
                self.PrintLines(lines)
                self._EndRead(any_lines_read)
                break
            elif not any_lines_read and not num_iterations:
                break
            else:
                pass

    def SetCommand(self, cmd):
        """Set the command that is shown at the current prompt
        @param cmd: command string to put on the prompt

        """
        self.SetTargetStart(self._fpos)
        self.SetTargetEnd(self.GetLength())
        self.ReplaceTarget(cmd)
        self.GotoPos(self.GetLength())

    def Write(self, cmd):
        """Write out command to shell process
        @param cmd: command string to write out to the shell proccess to run

        """
        DebugLog("[terminal][info] Writting out command: " + cmd)
        os.write(self.ind, cmd)

#-----------------------------------------------------------------------------#
# Utility Functions
def DebugLog(errmsg):
    """Print debug messages"""
    if DEBUG:
        print errmsg

def GetContextMenu():
    """Create and return a context menu to override the builtin scintilla
    one. To prevent it from allowing modifications to text that is to the
    left of the prompt.

    """
    menu = wx.Menu()
    menu.Append(wx.ID_CUT, _("Cut"))
    menu.Append(wx.ID_COPY, _("Copy"))
    menu.Append(wx.ID_PASTE, _("Paste"))
    menu.AppendSeparator()
    menu.Append(wx.ID_SELECTALL, _("Select All"))
    menu.AppendSeparator()
    menu.Append(wx.ID_SETUP, _("Preferences"))

    return menu

#-----------------------------------------------------------------------------#
# For Testing

if __name__ == '__main__':
    APP = wx.PySimpleApp(False)
    FRAME = wx.Frame(None, wx.ID_ANY, "Terminal Test")
    TERM = Xterm(FRAME, wx.ID_ANY)
    
    FSIZER = wx.BoxSizer(wx.VERTICAL)
    FSIZER.Add(TERM, 1, wx.EXPAND)
    FRAME.SetSizer(FSIZER)
    
    FRAME.SetSize((600, 400))
    FRAME.Show()
    APP.MainLoop()
