# -*- coding: utf-8 -*-
# Name: PasswordDialog.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra password dialog"""

__author__ = "Mike Rans"
__svnid__ = "$Id: PasswordDialog.py 1191 2011-03-27 15:57:44Z rans@email.com $"
__revision__ = "$Revision: 1191 $"

#----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import eclib

# Local imports
import rpdb2
from PyStudio.Common.PyStudioUtils import PyStudioUtils

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class PasswordDialog(eclib.ECBaseDlg):
    def __init__(self, parent, current_password):
        super(PasswordDialog, self).__init__(parent, title=_("Password"))

        # Layout
        sizerv = wx.BoxSizer(wx.VERTICAL)

        pwddesc = _("The password is used to secure communication between the "
                    "debugger console and the debuggee. Debuggees with "
                    "un-matching passwords will not appear in the attach "
                    "query list.")
        label = wx.StaticText(self, label=pwddesc, size=(300, -1))
        try:
            label.Wrap(300)
        except:
            # TODO: TRANSLATE _()
            pwddesc = """The password is used to secure communication
between the debugger console and the debuggee.
Debuggees with un-matching passwords will not
appear in the attach query list."""
            label.SetLabel(pwddesc)

        sizerv.Add(label, 1, wx.ALIGN_LEFT | wx.ALL, 5)

        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        sizerv.Add(sizerh, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        label = wx.StaticText(self, label=_("Set password:"))
        sizerh.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        pwd = [current_password, ''][current_password is None]

        self.m_entry_pwd = wx.TextCtrl(self, value=pwd, size=(200, -1))
        self.m_entry_pwd.SetFocus()
        sizerh.Add(self.m_entry_pwd, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        # Setup Buttons
        btnsizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        sizerv.Add(btnsizer, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

        # Finalize Layout
        self.SetSizer(sizerv)
        self.SetInitialSize()

        # Event Handlers
        self.Bind(wx.EVT_UPDATE_UI,
                  lambda evt: evt.Enable(bool(self.m_entry_pwd.Value)),
                  id=wx.ID_OK)

    def get_password(self):
        pwd = self.m_entry_pwd.GetValue()
        return pwd

    def do_validate(self):
        if rpdb2.is_valid_pwd(self.get_password()):
            return True

        baddpwd = _("The password should begin with a letter and continue "
                    "with any combination of digits, letters or underscores "
                    "(\'_\'). Only English characters are accepted for letters.")
        PyStudioUtils.error_dialog(self, baddpwd)
        return False

    def do_ok(self, event):
        if not self.do_validate():
            return
        event.Skip()
