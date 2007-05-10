# -*- coding: utf-8 -*-
"""Adds a PyShell to the MainWindow's View Menu"""
__author__ = "Cody Precord"
__version__ = "0.01"

import wx
from wx.py import shell
import ed_glob
import ed_main
import ed_menu
import plugin

ID_PYSHELL = wx.NewId()

class PyShell(plugin.Plugin):
    """Adds a PyShell to the MainWindow's View Menu"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
        """Adds the view menu entry and registers the event handler"""
	mw = parent
	if mw != None:
	    mb = mw.GetMenuBar()
	    if not ed_glob.PROFILE.has_key('VIEW_PYSHELL'):
	        ed_glob.PROFILE['VIEW_PYSHELL'] = False
	    hm = mb.GetMenuByName("view")
	    pysh = hm.InsertAlpha(ID_PYSHELL, _("PyShell"), _("Show A Python Shell"), 
		      wx.ITEM_CHECK, after=ed_glob.ID_PRE_MARK)
	    pysh.Check(ed_glob.PROFILE['VIEW_PYSHELL'])
	    pyshell = shell.Shell(mw, ID_PYSHELL, size=wx.Size(-1, 250))
	    mw.GetSizer().Add(pyshell, 0, wx.EXPAND)
	    if ed_glob.PROFILE['VIEW_PYSHELL']:
		pyshell.Show()
		mw.Layout()
	    else:
		pyshell.Hide()
		mw.Layout()
	    mw.Bind(wx.EVT_MENU, self.OnShowShell, id = ID_PYSHELL)

    def OnShowShell(self, evt):
	"""Shows the python shell frame"""
	mo = evt.GetEventObject()
	mw = wx.GetApp().GetMainWindow()
	if evt.GetId() == ID_PYSHELL:
            pyshell = mw.FindWindowById(ID_PYSHELL)
            if mo.IsChecked(ID_PYSHELL):
		ed_glob.PROFILE['VIEW_PYSHELL'] = True
		pyshell.Show()
		mw.Layout()
	    else:
		ed_glob.PROFILE['VIEW_PYSHELL'] = False
		pyshell.Hide()
		mw.Layout()
	else:
	    evt.Skip()

