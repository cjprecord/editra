###############################################################################
# Name: ProjCmnDlg.py                                                         #
# Purpose: Common dialogs                                                     #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Projects Common Dialogs

Common Dialog functions and classes

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ProjCmnDlg.py 925 2009-11-07 17:18:59Z CodyPrecord $"
__revision__ = "$Revision: 925 $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import os

# Editra Imports
import eclib

#-----------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Message Dialogs

def RetrievalErrorDlg(parent):
    """Show an error dialog for a retrieval error
    @param parent: parent window
    @return: ID_OK

    """
    dlg = wx.MessageDialog(parent,
                            _('The requested file could not be retrieved from '
                              'the source control system.'),
                            _('Could not retrieve file'),
                            style=wx.OK|wx.ICON_ERROR)
    rval = dlg.ShowModal()
    dlg.Destroy()
    return rval

#-----------------------------------------------------------------------------#

class CommitDialog(wx.Dialog):
    """Dialog for entering commit messages"""
    MAX_MESSAGE = 20
    RECENT_MESSAGES = [u'', ]
    _TEASER_LIST = [u'', ]

    def __init__(self, parent, title=u'', caption=u'', default=list()):
        """Create the Commit Dialog
        @keyword default: list of file names that are being committed

        """
        wx.Dialog.__init__(self, parent, title=title,
                           style=wx.DEFAULT_DIALOG_STYLE)

        # Attributes
        self._msgbox = wx.StaticBox(self, label=_("Message") + u":")
        self._mbxsizer = wx.StaticBoxSizer(self._msgbox)
        self._recent = wx.Choice(self, choices=CommitDialog._TEASER_LIST)
        self._commit = wx.Button(self, wx.ID_OK, _("Commit"))
        self._commit.SetDefault()
        self._cancel = wx.Button(self, wx.ID_CANCEL)

        self._entry = wx.TextCtrl(self, size=(400, 250), \
                                  style=wx.TE_MULTILINE|wx.TE_RICH2)
        font = self._entry.GetFont()
        if wx.Platform == '__WXMAC__':
            font.SetPointSize(12)
            self._entry.MacCheckSpelling(True)
            self._recent.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        else:
            font.SetPointSize(10)
        self._entry.SetFont(font)

        self._DefaultMessage(default)
        self._entry.SetFocus()

        # Layout
        self._DoLayout()
        self.CenterOnParent()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)

    def _DefaultMessage(self, files):
        """
        Put the default message in the dialog and the given list of files

        """
        msg = list()
        msg.append(u': ' + (u'-' * 40))
        msg.append(u": Lines beginning with `:' are removed automatically")
        msg.append(u": Modified Files:")
        for path in files:
            tmp = ":\t%s" % path
            msg.append(tmp)
        msg.append(u': ' + (u'-' * 40))
        msg.extend([u'', u''])
        msg = os.linesep.join(msg)
        self._entry.SetValue(msg)
        self._entry.SetInsertionPoint(self._entry.GetLastPosition())

    def _DoLayout(self):
        """ Used internally to layout dialog before being shown """
        msizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        bsizer = wx.StdDialogButtonSizer()
        esizer = wx.BoxSizer(wx.HORIZONTAL)
        rsizer = wx.BoxSizer(wx.HORIZONTAL)

        msizer.Add((10, 10), 0)

        # Message section
        rtxt = wx.StaticText(self, label=_("Recent Messages") + u":")
        rsizer.AddMany([((5, 5), 0),
                        (rtxt, 0, wx.ALIGN_CENTER_VERTICAL, 5),
                        ((5, 5), 0), (self._recent, 1, wx.EXPAND),
                        ((5, 5), 0)])
        self._recent.Enable(self._recent.GetCount() > 1)
        sizer.Add(rsizer, 1, wx.EXPAND)
        sizer.Add((10, 10), 0)

        esizer.AddMany([((5, 5), 0),
                        (self._entry, 1, wx.EXPAND),
                        ((5, 5), 0)])
        sizer.Add(esizer, 0, wx.EXPAND)
        self._mbxsizer.Add(sizer, 1, wx.EXPAND)

        # Buttons
        bsizer.AddButton(self._cancel)
        bsizer.AddButton(self._commit)
        bsizer.Realize()

        # Final Layout
        msizer.Add(self._mbxsizer, 0, wx.EXPAND, 5)
        msizer.Add((8, 8), 1, wx.EXPAND)
        msizer.Add(bsizer, 0, wx.ALIGN_RIGHT)
        msizer.Add((8, 8), 0)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((5, 5), 0), (msizer, 1, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(hsizer)
        self.SetInitialSize()

    def GetValue(self):
        """Return the value of the commit message"""
        txt = self._entry.GetValue().strip()
        txt = txt.replace('\r\n', '\n')
        return os.linesep.join([ x for x in txt.split('\n')
                                 if not x.lstrip().startswith(':') ])

    def OnChoice(self, evt):
        """Insert message from recently selected list"""
        idx = evt.GetSelection()
        if idx < len(CommitDialog.RECENT_MESSAGES):
            msg = CommitDialog.RECENT_MESSAGES[idx]
            self.SetCommitMessage(msg)
        else:
            evt.Skip()

    def OnOk(self, evt):
        """Handle click events from the commit button"""
        txt = self.GetValue()
        if txt and txt not in CommitDialog.RECENT_MESSAGES:
            CommitDialog.RECENT_MESSAGES.insert(1, txt)
            if len(txt) > 25:
                teaser = txt[:25] + u"..."
            else:
                teaser = txt
            CommitDialog._TEASER_LIST.insert(1, teaser)

            if len(CommitDialog.RECENT_MESSAGES) > CommitDialog.MAX_MESSAGE:
                CommitDialog.RECENT_MESSAGES.pop()
                CommitDialog._TEASER_LIST.pop()

        evt.Skip()

    def SetCommitMessage(self, msg):
        """Set the commit message
        @param msg: string

        """
        # Get the header
        txt = self._entry.GetValue().strip()
        txt = txt.replace('\r\n', '\n')
        header = os.linesep.join([x for x in txt.split('\n')
                                  if x.strip().startswith(':')])
        self._entry.SetValue(header + os.linesep + msg)
        self._entry.SetInsertionPoint(self._entry.GetLastPosition())

#-----------------------------------------------------------------------------#

class UpdateStatusDialog(wx.Frame):
    """Dialog to show output status from a SourceControl.update command"""
    def __init__(self, parent, title):
        """Dialog constructor
        @param parent: parent window
        @param title: dialog title

        """
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(550, 350))

        # Attributes
        self._panel = _UpdateDialogPanel(self)
        self.out = self._panel.OutputBuffer

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton, id=wx.ID_CLOSE)

    def __DoLayout(self):
        """Layout the window"""
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize((300, 200))
        self.SetAutoLayout(True)

    def OnButton(self, evt):
        """Handle button clicks"""
        self.Close(True)

    def OutputHook(self, line):
        """Output hook to display output from a command
        @param line: string or None to quit

        """
        self.out.AppendUpdate(line)

    def Show(self, show=True):
        """Show or hide the window
        @keyword show: bool

        """
        super(UpdateStatusDialog, self).Show(show)
        self.out.Start(200)

class _UpdateDialogPanel(wx.Panel):
    """Panel to show output status from a SourceControl.update command"""
    def __init__(self, parent):
        """Dialog constructor
        @param parent: parent window
        @param title: dialog title

        """
        wx.Panel.__init__(self, parent)

        # Attributes
        self._output = eclib.OutputBuffer(self)
        self._output.SetWrapMode(wx.stc.STC_WRAP_WORD)

        # Setup
        self.__DoLayout()

        # Event Handlers

    def __DoLayout(self):
        """Layout the window"""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Button Sizer
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.AddMany([((-1, 5), 1, wx.EXPAND),
                        (wx.Button(self, wx.ID_CLOSE, _("Close")), 0),
                        ((12, 8), 0)])

        # Output buffer
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((5, 5), 0), (self._output, 1, wx.EXPAND), ((5, 5), 0)])

        # Final layout
        sizer.AddMany([((5, 5), 0), (hsizer, 1, wx.EXPAND), ((5, 5), 0),
                      (bsizer, 0, wx.EXPAND), ((5, 5), 0)])

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    @property
    def OutputBuffer(self):
        """Windows OutputBuffer"""
        return self._output

#-----------------------------------------------------------------------------#

# XXX: Doesn't seem to be used
class ExecuteCommandDialog(wx.Dialog):
    """ Creates a dialog for getting a shell command to execute """
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, _('Execute command on files'))

        sizer = wx.BoxSizer(wx.VERTICAL)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self, -1,
            _('Enter a command to be executed on all selected files ' \
              'and files in selected directories.')))

        sizer.Add(hsizer)
        sizer.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), wx.ALIGN_RIGHT)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
