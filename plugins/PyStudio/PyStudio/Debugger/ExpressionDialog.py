# -*- coding: utf-8 -*-
# Name: ExpressionDialog.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra expression dialog"""

__author__ = "Mike Rans"
__svnid__ = "$Id: ExpressionDialog.py 1526 2012-03-30 20:44:03Z rans@email.com $"
__revision__ = "$Revision: 1526 $"

#----------------------------------------------------------------------------#
# Imports
import os.path
import wx

# Editra Libraries
import eclib

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class ExpressionDialog(eclib.ECBaseDlg):
    def __init__(self, parent, default_value, title, description, labeltext, ctrlsize, style=wx.TE_MULTILINE):
        super(ExpressionDialog, self).__init__(parent, wx.ID_ANY, title)    
        
        label = wx.StaticText(self, -1, description)
        self.Sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        sizerh = wx.BoxSizer(wx.HORIZONTAL)
        self.Sizer.Add(sizerh, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        if labeltext:
            label = wx.StaticText(self, -1, labeltext)
            sizerh.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        self.m_entry_expr = wx.TextCtrl(self, value = default_value, style=style, size = ctrlsize)
        self.m_entry_expr.SetFocus()
        self.Bind(wx.EVT_TEXT, self.OnText, self.m_entry_expr)
        sizerh.Add(self.m_entry_expr, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        
        btnsizer = wx.StdDialogButtonSizer()
        self.Sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        self.m_ok = wx.Button(self, wx.ID_OK)
        self.m_ok.SetDefault()
        self.m_ok.Disable()
        btnsizer.AddButton(self.m_ok)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        self.Sizer.Fit(self)        

    def OnText(self, evt):
        if evt.GetString() == '':
            self.m_ok.Disable()
        else:
            self.m_ok.Enable()
                   
    def get_expression(self):
        expr = self.m_entry_expr.GetValue()
        return unicode(expr)
