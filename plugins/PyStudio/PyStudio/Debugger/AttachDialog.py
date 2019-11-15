# -*- coding: utf-8 -*-
# Name: AttachDialog.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra attach dialog"""

__author__ = "Mike Rans"
__svnid__ = "$Id: AttachDialog.py 1142 2011-03-19 19:21:26Z rans@email.com $"
__revision__ = "$Revision: 1142 $"

#----------------------------------------------------------------------------#
# Imports
import sys
import wx

# Editra Libraries
import eclib

# Local imports
import rpdb2
from PyStudio.Common.PyStudioUtils import RunProcInThread
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger
from PyStudio.Debugger.PasswordDialog import PasswordDialog

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class AttachDialog(eclib.ECBaseDlg):
    def __init__(self, parent):
        super(AttachDialog, self).__init__(parent, title=_("Attach"))

        # Attributes
        self.m_server_list = None
        self.m_errors = {}
        self.m_index = None

        # Layout
        sizerv = wx.BoxSizer(wx.VERTICAL)

        desc = _("Attach to a script (that has the debugger engine running) on local or remote machine:")
        label = wx.StaticText(self, label=desc, size=(350, -1))
        try:
            label.Wrap(350)
        except:
            # TODO: TRANSLATE _()
            desc = """Attach to a script (that has the debugger engine
running) on local or remote machine:"""
            label.SetLabel(desc)

        sizerv.Add(label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        sizerv.Add(sizerh, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        label = wx.StaticText(self, -1, _("Host:"))
        sizerh.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.m_entry_host = wx.TextCtrl(self, value=self.Parent._lasthost, size = (200, -1))
        self.m_entry_host.SetFocus()
        sizerh.Add(self.m_entry_host, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        btn = wx.Button(self, label = _("Refresh"))
        self.Bind(wx.EVT_BUTTON, self.do_refresh, btn) # for some reason, this must be up here otherwise window hangs
        btn.SetDefault()
        sizerh.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        self.m_listbox_scripts = eclib.EBaseListCtrl(parent=self,
                                                     style=wx.LC_REPORT|wx.LC_SINGLE_SEL, 
                                                     size=(-1, 300))
        self.m_listbox_scripts.InsertColumn(0, _("PID") + u'    ')
        self.m_listbox_scripts.InsertColumn(1, _("Filename"))

        sizerv.Add(self.m_listbox_scripts, 0, wx.EXPAND | wx.ALL, 5)

        btnsizer = self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL)
        sizerv.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizer(sizerv)
        self.SetInitialSize()

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.m_listbox_scripts)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.m_listbox_scripts)
        self.Bind(wx.EVT_UPDATE_UI,
                  lambda evt: evt.Enable(bool(self.m_listbox_scripts.GetSelectedItemCount())),
                  id=wx.ID_OK)
        self.Bind(wx.EVT_SHOW, self.OnShow, self)

    def OnShow(self, event):
        """Show Password entry dialog"""
        def Authenticate():
            pwd_dialog = PasswordDialog(self, self.Parent._lastpwd)
            pos = self.GetPositionTuple()
            pwd_dialog.CenterOnParent()
            if pwd_dialog.ShowModal() != wx.ID_OK:
                pwd_dialog.Destroy()
                self.Close()
                return

            self.Parent._lastpwd = pwd_dialog.get_password()
            pwd_dialog.Destroy()

            RpdbDebugger().set_password(self.Parent._lastpwd)
            self.do_refresh()

        # If showing the dialog popup the authentication dialot
        if event.IsShown():
            wx.CallAfter(Authenticate)
        event.Skip()

    def set_cursor(self, id):
        cursor = wx.StockCursor(id)
        self.SetCursor(cursor)
        self.m_listbox_scripts.SetCursor(cursor)

    def get_server(self):
        return self.m_server_list[self.m_index]

    def do_refresh(self, event=None):
        host = self.m_entry_host.Value
        if not host:
            host = 'localhost'
        self.Parent._lasthost = host
        worker = RunProcInThread("DbgAttach", self._onserverlist,
                                 RpdbDebugger().get_server_list, host)
        worker.start()

    def _onserverlist(self, res):
        """Callback from do_refresh thread"""
        assert wx.Thread_IsMain(), "Must Update UI from Main Thread!!"

        if not res:
            return
        (self.m_server_list, self.m_errors) = res

        if len(self.m_errors) > 0:
            for k, el in self.m_errors.items():
                if k in [rpdb2.AuthenticationBadData, rpdb2.AuthenticationFailure]:
                    self.report_attach_warning(rpdb2.STR_ACCESS_DENIED)

                elif k == rpdb2.EncryptionNotSupported:
                    self.report_attach_warning(rpdb2.STR_DEBUGGEE_NO_ENCRYPTION)

                elif k == rpdb2.EncryptionExpected:
                    self.report_attach_warning(rpdb2.STR_ENCRYPTION_EXPECTED)

                elif k == rpdb2.BadVersion:
                    for (t, v, tb) in el:
                        self.report_attach_warning(rpdb2.STR_BAD_VERSION % {'value': v})

        host = RpdbDebugger().get_host()
        self.m_entry_host.SetValue(host)

        self.m_listbox_scripts.DeleteAllItems()

        # TODO: change this to not use sys.maxint, this is a bad example from
        #       wxPython demo.
        for i, s in enumerate(self.m_server_list):
            index = self.m_listbox_scripts.InsertStringItem(sys.maxint, repr(s.m_pid))
            self.m_listbox_scripts.SetStringItem(index, 1, s.m_filename)
            self.m_listbox_scripts.SetItemData(index, i)

    def report_attach_warning(self, warning):
        dlg = wx.MessageDialog(self, warning, _("Warning"),
                               wx.OK|wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def OnItemSelected(self, event):
        self.m_index = event.GetIndex()
        event.Skip()

    def OnItemActivated(self, event):
        self.m_index = event.GetIndex()
        self.EndModal(wx.ID_OK)
