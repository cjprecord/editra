###############################################################################
# Name: ed_cmdbar.py                                                          #
# Purpose: Creates a small slit panel that holds small controls for searching #
#          and other actions.                                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: ed_cmdbar.py                                                       #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    This class creates a custom panel that can hide and show different    #
# controls based an id value. The panel is generally between 24-32 pixels  #
# in height but can grow to fit the controls inserted in it. The           #
# the background is painted with a gradient using system defined colors.   #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import re
import wx
import util
import ed_glob
import ed_search

_ = wx.GetTranslation
#--------------------------------------------------------------------------#
# Close Button Bitmap
from wx import ImageFromStream, BitmapFromImage
import cStringIO, zlib

def GetXData():
    """Returns the raw image data for the close button
    @return: raw image data

    """
    return zlib.decompress(
'x\xda\x011\x02\xce\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0e\
\x00\x00\x00\x0e\x08\x02\x00\x00\x00\x90*\xba\x86\x00\x00\x00\x03sBIT\x08\
\x08\x08\xdb\xe1O\xe0\x00\x00\x01\xe9IDAT(\x91m\x92\xbdk\x13a\x18\xc0\x9f\
\xbb\\r\xd7Ks\xb9&\xc6\xd2j\x8f\xc6D\x08\x8a\xa2\xed\xe2G\x87,\x15\xc4\xb5\
\x8bH\x17-]\x02\x85:\x14\x84\xd0\x82J\x07A\x07\xc1\xff\xc1\xc1I\x04\x07\x11\
\x05\x15\x1d\x1cJ\x87\xa2\xd5\x96\x92&49\xe9\x99\xf4\xbc7w\xf7\xbe\xef\xf3:\
\xdcQ:\xf4\x99\x9e\x8f\x1f\xcf\xb7\xf4\xe9\xf1\xc3\xde\xd7\xcfAg/l5\xe08I\
\x9d\xb2\xd4\xe1\x91\xec\xd5)\xe9\xcd\xad\x1b\x93W.\x9bC\x05.\xfc(&h?\xa6h\
\xec\xe9\xb5\xbbk\x9b\xbbJ\xd0\xd93\xc6n\xd2\xfd\x16\xddo\xc7\x00c\x00\x80\
\x9cE\xa6f\x1a\xc6\xe9\x9c\xfasK\x0e[\rP\x12\x9cx\xd2@*=\xbb(\x8d\x8e!g\xc8\
\x99b\x95rs\x0f\xb8\xaa\xf9\xdd\x03\xa6&\xc5_[>\xecI\x9f\xa9\xa9\x95\x89\xec\
\xbd\xbab\x95\x14\xab\x94\x9f_V+\x13\x85\xd9E\x1f\xa9\xc2)\x00(\x00 \x04\x13\
\x10\x90\xf7\xaf\x92\xe3\x15Y\xd3\xf3\xf3\xcb\x00 k:\xfa\xc4y\xfb\xf20\x97\
\x02\x00\xd0%\xc1\xae\xc36\xb6\x83\xe6\xfd\x93+\xcfdM\x07\x00\xf4I\xa3\xbe\
\xe0o\xfd\x00\x00\x9e\x1b\x8dQ\xf6\x8f0/\xa0\xae/\x05\xec\xe8\x9a0\xe4\xcc\
\xf59"w\\\xc1\xb8\x0c\x00"d\x88"u\xf6\xfc\xc8\xea\xf3\xa8.\xfaD\xd6\xf4\xf1\
\'/\xf4s\x17\x00\x00(\x17!\x8d\xc7B\xa4\xd9\xdbw#ng\xa9\xb6\xb3T\x8b\xe8\xfc\
\x9d9\x00\x10,\x00\xc4\xc4LF+_\xbaHl\xdb\xfb\xf2!Y,\xb7\x9e>"\x9b\x1b\xb4\
\xd3\xf6\xd6\xbe\xcb\xb9Bc\xb5.3\xaa\r\x19\x9df[z}}r\xaaz\xad\xff\xc7>\xb0\
\x9b\xcc\x8d\xcf\xc3\x11#%\x91J\x0e\x9a\x99\xf4\xe0\xc0z\xb3\xa7\xe8V\xd1u\
\x1c#sB\xcb\xa4\x01@`\x185\x17\xd5e\x88\t\xce\xdc^\x1fr\xc3\x8aY\x9d\xfe\xf5\
\xf1\x1dY\xff\xe6m\xff>\xf6]\xd2g\xca\xbaU4\xab\xd3\xff\x01\xe3\xf6\xf0\x91\
\xbc\xe0^J\x00\x00\x00\x00IEND\xaeB`\x82\x7fU\x05\xed' )

def GetXBitmap():
    """Returns a bitmap version of the close button
    @return: bitmap of close button

    """
    return BitmapFromImage(GetXImage())

def GetXImage():
    """Returns an image version of the close button
    @return: image of close button

    """
    stream = cStringIO.StringIO(GetXData())
    return ImageFromStream(stream)

#-----------------------------------------------------------------------------#
# Globals
ID_CLOSE_BUTTON = wx.NewId()
ID_SEARCH_CTRL = wx.NewId()
ID_SEARCH_NEXT = wx.NewId()
ID_SEARCH_PRE = wx.NewId()
ID_MATCH_CASE = wx.NewId()
ID_FIND_LBL = wx.NewId()
ID_LINE_CTRL = wx.NewId()
ID_GOTO_LBL = wx.NewId()
ID_CMD_CTRL = wx.NewId()
ID_CMD_LBL = wx.NewId()

#-----------------------------------------------------------------------------#

class CommandBar(wx.Panel):
    """The command bar is a slim panel that is used to hold various small
    controls for searching jumping to line, ect...
    @todo: make a plugin interface and a management system for showing and
           hiding the various conrols

    """
    def __init__(self, parent, id_, size=(-1, 24), style=wx.TAB_TRAVERSAL):
        """Initializes the bar and its default widgets
        @postcondition: commandbar is created

        """
        wx.Panel.__init__(self, parent, id_, size=size, style=style)

        # Attributes
        self._parent = parent
        self._installed = False
        self._sizers = dict(psizer=parent.GetSizer(),
                            h_sizer=wx.BoxSizer(wx.HORIZONTAL),
                            goto=wx.BoxSizer(),
                            search=wx.BoxSizer(),
                            cmd=wx.BoxSizer())

        # Install Controls
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizers['h_sizer'].Add((8, 8))
        bstyle = wx.BU_EXACTFIT
        if wx.Platform == '__WXGTK__':
            bstyle = wx.NO_BORDER

        self.close_b = wx.BitmapButton(self, ID_CLOSE_BUTTON, \
                                       GetXBitmap(), style=bstyle)
        self._sizers['h_sizer'].Add(self.close_b, 0, wx.ALIGN_CENTER_VERTICAL)
        self._sizers['h_sizer'].Add((12, 12))
        v_sizer.Add((2, 2))
        self._sizers['h_sizer'].Add(v_sizer)
        self.SetSizer(self._sizers['h_sizer'])
        self.SetAutoLayout(True)

        # Bind Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)

    def Hide(self):
        """Hides the control and notifies the parent
        @postcondition: commandbar is hidden

        """
        wx.Panel.Hide(self)
        if self._sizers['psizer'] != None:
            self._sizers['psizer'].Layout()
        self._parent.SendSizeEvent()
        self._parent.nb.GetCurrentCtrl().SetFocus()
        return True

    def InstallCtrl(self, id_):
        """Installs a control into the bar by ID
        @postcondition: control is installed
        @return: requested control or None

        """
        if id_ == ID_SEARCH_CTRL:
            ctrl = self.InstallSearchCtrl()
        elif id_ == ID_LINE_CTRL:
            ctrl = self.InstallLineCtrl()
        elif id_ == ID_CMD_CTRL:
            ctrl = self.InstallCommandCtrl()
        else:
            ctrl = None
        return ctrl

    def InstallLineCtrl(self):
        """Installs the go to line control into the panel.
        @postcondition: GotoLine control is installed in bar.

        """
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((5, 5))
        linectrl = LineCtrl(self, ID_LINE_CTRL, self._parent.nb.GetCurrentCtrl,
                            size=(100, 20))
        v_sizer.Add(linectrl, 0, wx.ALIGN_CENTER_VERTICAL)
        v_sizer.Add((4, 4))
        go_lbl = wx.StaticText(self, ID_GOTO_LBL, _("Goto Line") + ": ")
        if wx.Platform == '__WXMAC__':
            go_lbl.SetFont(wx.SMALL_FONT)
        h_sizer.AddMany([(go_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                         ((5, 5)), (v_sizer)])
        h_sizer.Layout()
        self._sizers['goto'] = h_sizer
        self._sizers['h_sizer'].Add(h_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizers['h_sizer'].Layout()
        return linectrl

    def InstallCommandCtrl(self):
        """Install the sizer containing the command executer control
        into the bar.
        @return: the command control instance

        """
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((5, 5))
        cmdctrl = CommandExecuter(self, ID_CMD_CTRL, size=(150, 20))
        v_sizer.Add(cmdctrl, 0, wx.ALIGN_CENTER_VERTICAL)
        v_sizer.Add((4, 4))
        cmd_lbl = wx.StaticText(self, ID_CMD_LBL, _("Command") + ": ")
        if wx.Platform == '__WXMAC__':
            cmd_lbl.SetFont(wx.SMALL_FONT)
        h_sizer.AddMany([(cmd_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                         ((5, 5)), (v_sizer)])
        h_sizer.Layout()
        self._sizers['cmd'] = h_sizer
        self._sizers['h_sizer'].Add(h_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizers['h_sizer'].Layout()
        return cmdctrl

    def InstallSearchCtrl(self):
        """Installs the search context controls into the panel.
        Other controls should be removed from the panel before calling
        this method.
        @postcondition: search control is installed in bar

        """
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        t_sizer = wx.BoxSizer(wx.VERTICAL)

        v_sizer.Add((5, 5))
        ssize = wx.Size(180, 20)
        if wx.Platform == '__WXGTK__':
            ssize.SetHeight(24)
        search = ed_search.EdSearchCtrl(self, ID_SEARCH_CTRL, 
                                         menulen=5, size=ssize)
        v_sizer.Add(search)
        v_sizer.Add((4, 4))
        f_lbl = wx.StaticText(self, ID_FIND_LBL, _("Find") + u": ")
        ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DOWN), wx.ART_MENU)
        next_btn = wx.BitmapButton(self, ID_SEARCH_NEXT, 
                                   t_bmp, style=wx.NO_BORDER)
        nlbl = wx.StaticText(self, label=_("Next"))

        t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU)
        pre_btn = wx.BitmapButton(self, ID_SEARCH_PRE, 
                                  t_bmp, style=wx.NO_BORDER)
        plbl = wx.StaticText(self, label=_("Previous"))

        match_case = wx.CheckBox(self, ID_MATCH_CASE, _("Match Case"))
        match_case.SetValue(search.IsMatchCase())
        if wx.Platform == '__WXMAC__':
            f_lbl.SetFont(wx.SMALL_FONT)
            match_case.SetFont(wx.SMALL_FONT)
            nlbl.SetFont(wx.SMALL_FONT)
            plbl.SetFont(wx.SMALL_FONT)

        ctrl_sizer.AddMany([(10, 10), (next_btn, 0, wx.ALIGN_CENTER_VERTICAL), 
                            ((3, 3)), (nlbl, 0, wx.ALIGN_CENTER_VERTICAL),
                            ((10, 10)), (pre_btn, 0, wx.ALIGN_CENTER_VERTICAL), 
                            ((3, 3)), (plbl, 0, wx.ALIGN_CENTER_VERTICAL),
                            ((10, 10)), 
                            (match_case, 0, wx.ALIGN_CENTER_VERTICAL)])

        t_sizer.Add((7, 7))
        t_sizer.Add(ctrl_sizer)
        t_sizer.Add((4, 4))

        h_sizer.AddMany([(f_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                         ((5, 5)), (v_sizer), 
                         (ctrl_sizer, 0, wx.ALIGN_CENTER_VERTICAL)])
        self._sizers['search'] = h_sizer
        self._sizers['h_sizer'].Add(h_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self._sizers['h_sizer'].Layout()
        return search

    def OnCheck(self, evt):
        """Check box event handler
        @param evt: Event that called this handler
        @type evt: wx.EVT_CHECKBOX

        """
        e_id = evt.GetId()
        if e_id == ID_MATCH_CASE:
            ctrl = self.FindWindowById(e_id)
            if ctrl != None:
                search = self.FindWindowById(ID_SEARCH_CTRL)
                if search != None:
                    if ctrl.GetValue():
                        search.SetSearchFlag(wx.FR_MATCHCASE)
                    else:
                        search.ClearSearchFlag(wx.FR_MATCHCASE)
        else:
            evt.Skip()

    def OnButton(self, evt):
        """Handles events from the buttons on the bar
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        if e_id == ID_CLOSE_BUTTON:
            self.Hide()
        elif e_id in [ID_SEARCH_NEXT, ID_SEARCH_PRE]:
            search = self.FindWindowById(ID_SEARCH_CTRL)
            if search != None:
                evt = wx.KeyEvent(wx.wxEVT_KEY_UP)
                evt.m_keyCode = wx.WXK_RETURN
                if e_id == ID_SEARCH_PRE:
                    evt.m_shiftDown = True
                else:
                    evt.m_shiftDown = False
                wx.PostEvent(search, evt)
        else:
            evt.Skip()

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
        grad = gc.CreateLinearGradientBrush(0, 1, 0, 29, col2, col1)
        rect = self.GetClientRect()

        pen_col = tuple([min(190, x) for x in util.AdjustColour(col1, -60)])
        gc.SetPen(gc.CreatePen(wx.Pen(pen_col, 1)))
        gc.SetBrush(grad)
        gc.DrawRectangle(0, 1, rect.width - 0.5, rect.height - 0.5)

        evt.Skip()

    def Show(self, id_=0):
        """Shows the control and installs it in the parents
        sizer if not installed already.
        @param id_: Id of control to show in bar

        """
        # Install self in parent
        if not self._installed and self._sizers['psizer'] != None:
            self._installed = True
            self._sizers['psizer'].Add(self, 0, wx.EXPAND)
            self._sizers['psizer'].Layout()
            self._parent.SendSizeEvent()
        wx.Panel.Show(self)

        # HACK YUCK, come back and try again when my brain is working
        # Show specified control
        if id_:
            ctrl = self.FindWindowById(id_)
            if ctrl is None:
                ctrl = self.InstallCtrl(id_)

            # First Hide everything
            for kid in (list(self._sizers['search'].GetChildren()) + 
                        list(self._sizers['goto'].GetChildren()) +
                        list(self._sizers['cmd'].GetChildren())):
                kid.Show(False)

            if id_ == ID_SEARCH_CTRL:
                for kid in self._sizers['search'].GetChildren():
                    kid.Show(True)
                self._sizers['search'].Layout()
            elif id_ == ID_LINE_CTRL:
                for kid in self._sizers['goto'].GetChildren():
                    kid.Show(True)
            elif id_ == ID_CMD_CTRL:
                for kid in self._sizers['cmd'].GetChildren():
                    kid.Show(True)

            self.GetSizer().Layout()
            if ctrl != None:
                ctrl.SetFocus()
                ctrl.SelectAll()

    def UpdateIcons(self):
        """Refresh icons to current theme settings
        @postcondition: all icons are updated

        """
        next = self.FindWindowById(ID_SEARCH_NEXT)
        if next:
            t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DOWN), wx.ART_MENU)
            next.SetBitmapLabel(t_bmp)
            next.SetBitmapHover(t_bmp)
            next.Refresh()
        pre = self.FindWindowById(ID_SEARCH_PRE)
        if pre:
            t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU)
            pre.SetBitmapLabel(t_bmp)
            pre.SetBitmapHover(t_bmp)
            pre.Refresh()

#-----------------------------------------------------------------------------#

class CommandExecuter(wx.SearchCtrl):
    """Part of the Vi emulation, opens a minibuffer to execute EX commands.
    @note: based on search ctrl so we get the nice roudned edges on wxmac.
    
    """
    RE_GO_BUFFER = re.compile('[0-9]*[nN]{1,1}')
    RE_GO_WIN = re.compile('[0-9]*n[wW]{1,1}')
    RE_WGO_BUFFER = re.compile('w[0-9]*[nN]')
    RE_NGO_LINE = re.compile('[+-][0-9]+')
    def __init__(self, parent, id_, size=wx.DefaultSize):
        """Initializes the CommandExecuter"""
        wx.SearchCtrl.__init__(self, parent, id_, size=size, 
                               style=wx.TE_PROCESS_ENTER)

        # Attributes
        self._cmdstack = ['']
        self._histidx = -1
        self._curdir = wx.GetHomeDir() + os.sep
        self._bpath = None
        if not hasattr(sys, 'frozen'):
            self._curdir = os.path.abspath(os.curdir) + os.sep

        # Hide the search button and text
        self.ShowSearchButton(False)
        self.ShowCancelButton(False)
        self.SetDescriptiveText(wx.EmptyString)

        # Event Handlers
        # HACK, needed on Windows to get key events
        if wx.Platform == '__WXMSW__':
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
                    child.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
                    break
        else:
            self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
            self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        self.Bind(wx.EVT_SIZE, self.OnKeyUp)

    def _AdjustSize(self):
        """Checks width of text as its added and dynamically resizes
        the control as needed.

        """
        ext = self.GetTextExtent(self.GetValue())[0]
        curr_w, curr_h = self.GetClientSizeTuple()
        if ext > curr_w * .85:
            max_w = self.GetParent().GetClientSize().GetWidth() * .75
            nwidth = min(ext * 1.15, max_w)
            self.SetClientSize((nwidth, curr_h))
        elif ((curr_w > ext * 1.15) and curr_w > 150):
            nwidth = max(ext * 1.15, 150)
            self.SetClientSize((nwidth, curr_h))
        else:
            pass

    def ChangeDir(self, cmd):
        """Change to a directory based on cd command
        @param cmd: cd path

        """
        path = cmd.replace('cd', '', 1).strip()
        if not os.path.isabs(path):
            if path.startswith('..'):
                path = os.path.abspath(path)
            else:
                path = os.path.join(self._curdir, path)

        if os.path.exists(path) and os.path.isdir(path):
            os.chdir(path)
            self._curdir = os.path.abspath(os.path.curdir) + os.sep
        else:
            self.Clear()
            wx.Bell()
            
    def CommandPush(self, cmd):
        """Push a command to the stack popping as necessary to
        keep stack size less than MAX.
        @param cmd: command string to push
        @todo: redo this to be more like the code in my terminal project

        """
        self._cmdstack.insert(0, cmd)
        if len(self._cmdstack) > 25:
            self._cmdstack.pop()

    def EditCommand(self, cmd):
        """Perform an edit related command
        @param cmd: command string to execute

        """
        # e fname: edit file
        cmd = cmd[1:].strip()
        frame = self.GetTopLevelParent()
        if not os.path.isabs(cmd):
            cmd = os.path.join(self._curdir, cmd)

        if os.path.exists(cmd):
            frame.DoOpen(ed_glob.ID_COMMAND_LINE_OPEN, cmd)
        else:
            frame.nb.OpenPage(util.GetPathName(cmd), util.GetFileName(cmd))

    def ExecuteCommand(self, cmd_str):
        """Interprets and executes a command then hides the control
        @param cmd_str: Command string to execute

        """
        frame = self.GetTopLevelParent()
        cmd = cmd_str.strip().lstrip(':')
        if cmd in ['x', 'ZZ']:
            cmd = 'wq'

        if cmd.startswith(u'w'):
            frame.OnSave(wx.MenuEvent(wx.wxEVT_COMMAND_MENU_SELECTED, 
                                                     ed_glob.ID_SAVE))
            if self.RE_WGO_BUFFER.match(cmd):
                self.GoBuffer(cmd[1:])
            elif cmd == 'wq':
                self.Quit()
        elif cmd.startswith(u'e '):
            self.EditCommand(cmd)
        elif self.RE_GO_WIN.match(cmd):
            self.GoWindow(cmd)
        elif re.match(self.RE_GO_BUFFER, cmd):
            self.GoBuffer(cmd)
        elif cmd.isdigit() or self.RE_NGO_LINE.match(cmd):
            ctrl = frame.nb.GetCurrentCtrl()
            cline = ctrl.GetCurrentLine()
            if cmd[0] in '+-':
                line = eval("%s %s %s" % (str(cline), cmd[0], cmd[1:]))
            else:
                line = int(cmd) - 1
            ctrl.GotoLine(line)
        elif cmd.startswith('cd'):
            self.ChangeDir(cmd)
        elif cmd == 'q':
            self.Quit()
        else:
            wx.Bell()
            return

        self.CommandPush(cmd_str)
        self._histidx = -1
        self.GetParent().Hide()

    def GetHistCommand(self, pre=True):
        """Look up a command from the history of recent commands
        @param pre: Get previous (default) or get Next
        @note: pre moves right in stack, next moves left in stack

        """
        hist_l = len(self._cmdstack) - 1
        if pre:
            self._histidx += 1
            if self._histidx >= hist_l + 1:
                self._histidx = hist_l
            cmd = self._cmdstack[self._histidx]
        else:
            self._histidx -= 1
            if self._histidx < 0:
                cmd = ''
                self._histidx = -1
            else:
                cmd = self._cmdstack[self._histidx]
        self.SetValue(cmd)
        self.SelectAll()

    def GoBuffer(self, cmd):
        """Go to next/previous buffer in notebook
        @param cmd: cmd string [0-9]*[nN]

        """
        count = cmd[0:-1]
        cmd = cmd[-1]
        if count.isdigit():
            count = int(count)
        else:
            count = 1

        frame = self.GetTopLevelParent()
        numpage = frame.nb.GetPageCount()
        for x in xrange(min(count, numpage)):
            cpage = frame.nb.GetPageIndex(frame.nb.GetCurrentPage())
            if (cpage == 0 and cmd == 'N') or \
               (cpage + 1 == numpage and cmd == 'n'):
                break
            frame.nb.AdvanceSelection(cmd == 'n')

    def GoWindow(self, cmd):
        """Go to next/previous open window
        @param cmd: cmd string [0-9]*n[wW]

        """
        count = cmd[0:-1]
        cmd = cmd[-1]
        if count.isdigit():
            count = int(count)
        else:
            count = 1
        wins = wx.GetApp().GetMainWindows()
        pid = self.GetTopLevelParent().GetId()
        widx = 0
        win = 0
        for nwin in xrange(len(wins)):
            if pid == wins[nwin].GetId():
                widx = pid
                win = nwin
                break

        if cmd == 'W':
            widx = win + count
        else:
            widx = win - count

        if widx < 0:
            widx = 0
        elif widx >= len(wins):
            widx = len(wins) - 1
        self.GetParent().Hide()
        wins[widx].Raise()
        wx.CallAfter(wins[widx].nb.GetCurrentCtrl().SetFocus)

    def GetNextDir(self):
        """Get the next directory path from the current cmd path
        @note: used for tab completion of cd, completion is based off cwd
        @todo: finish working on this by starting over
        @note: not currently used

        """
        cmd = self.GetValue()
        if not cmd.startswith('cd '):
            return

        cmd = cmd.replace('cd ', u'', 1).strip()
        if not os.path.exists(self._curdir):
            self._curdir = wx.GetHomeDir()

        if len(cmd) and (cmd[0].isalnum() or cmd.startswith('.')):
            path = self._curdir
            cmd = os.path.join(path, cmd)
        else:
            path = os.path.abspath(cmd)
            if (len(cmd) and cmd[-1] == os.sep) or not len(cmd):
                path = path + os.sep

        if not os.path.exists(path):
            path = self._curdir

        # Filter Directories
        if path[-1] != os.sep:
            path = os.path.join(*os.path.split(path)[:-1]) + os.sep
            if not path.startswith(os.sep):
                path = os.sep + path
        dirs = [ os.path.join(path, x) \
                 for x in os.listdir(path) \
                 if os.path.isdir(os.path.join(path, x)) ]
        dirs.sort()
        if not len(dirs):
            return

        if len(cmd):
            npath = None
            for next in dirs:
                if next.startswith(cmd):
                    if cmd[-1] != os.path.sep and next == cmd:
                        idx = dirs.index(next) + 1
                    else:
                        idx = dirs.index(next)
                    
                    if idx < len(dirs):
                        npath = dirs[idx] #.replace(path, u'', 1)
                    break
            if npath:
                return npath
        else:
            return dirs[0]

    def ListDir(self):
        """List the next directory from the current cmd path
        @note: used for tab completion of cd, completion is based off cwd

        """
        path = self.GetNextDir()
        if path:
            self.SetValue('cd ' + path)

    def ListFile(self):
        """List the next file in the current cmd path
        @note: used for tab completion of e, completion is based off cwd

        """

    def OnEnter(self, evt):
        """Get the currently entered command string and execute it.
        @postcondition: ctrl is cleared and command is executed
        
        """
        cmd = self.GetValue()
        self.Clear()
        self.ExecuteCommand(cmd)

    def OnKeyDown(self, evt):
        """Records the key sequence that has been entered and
        performs actions based on that keysequence.
        @param evt: event that called this handler

        """
        e_key = evt.GetKeyCode()
        cmd = self.GetValue()
        if e_key == wx.WXK_UP:
            self.GetHistCommand(pre=True)
        elif e_key == wx.WXK_DOWN:
            self.GetHistCommand(pre=False)
        elif e_key == wx.WXK_SPACE and not len(cmd):
            # Swallow space key when command is empty
            pass
        elif e_key == wx.WXK_TAB:
            # Provide Tab Completion or swallow key
            if cmd.startswith('e '):
                self.ListFile()
            elif cmd.startswith('cd '):
                self.ListDir()
            else:
                pass
        elif e_key == wx.WXK_ESCAPE:
            self.Clear()
            self.GetParent().Hide()
        else:
            evt.Skip()

    def OnKeyUp(self, evt):
        """Adjust size as needed when characters are entered
        @param evt: event that called this handler

        """
        self._AdjustSize()
        evt.Skip()

    def Quit(self):
        """Tell the editor to exit
        @postcondition: Editor begins exit, confirming file saves

        """
        wx.PostEvent(self.GetTopLevelParent(), 
                     wx.CloseEvent(wx.wxEVT_CLOSE_WINDOW))

    def WriteCommand(self, cstr):
        """Perform a file write related command
        @param cstr: The command string to execute

        """
        # wn: write and edit next
        # wN: write and edit previous
        # wq: write and quit

#-----------------------------------------------------------------------------#

class LineCtrl(wx.SearchCtrl):
    """A custom int control for providing a go To line control
    for the Command Bar.
    @note: The control is subclassed from SearchCtrl so that it gets
           the nice rounded edges on wxMac.

    """
    def __init__(self, parent, id_, get_doc, size=wx.DefaultSize):
        """Initializes the LineCtrl control and its attributes.
        @param get_doc: callback method for retreiving a reference to the
                        current document.

        """
        wx.SearchCtrl.__init__(self, parent, id_, "", size=size,
                             style=wx.TE_PROCESS_ENTER,
                             validator=util.IntValidator(0, 65535))

        # Attributes
        self._last = 0
        self.GetDoc = get_doc

        # Hide the search button and text
        self.ShowSearchButton(False)
        self.ShowCancelButton(False)
        self.SetDescriptiveText(wx.EmptyString)

        # MSW/GTK HACK
        if wx.Platform in ['__WXGTK__', '__WXMSW__']:
            for child in self.GetChildren():
                if isinstance(child, wx.TextCtrl):
                    child.SetValidator(util.IntValidator(0, 65535))

        # Event management
        self.Bind(wx.EVT_TEXT_ENTER, self.OnInput)

    def OnInput(self, evt):
        """Processes the entered line number
        @param evt: Event that called this handler
        @type evt: wx.EVT_TEXT_ENTER

        """
        val = self.GetValue()
        if not val.isdigit():
            return

        val = int(val) - 1
        doc = self.GetDoc()
        lines = doc.GetLineCount()
        if val > lines:
            val = lines
        doc.GotoLine(val)
        doc.SetFocus()
        self.GetParent().Hide()

#-----------------------------------------------------------------------------#
