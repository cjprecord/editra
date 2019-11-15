# -*- coding: utf-8 -*-
# Name: FindTabMenu.py
# Purpose: ModuleFinder plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Find Tab Menu"""

__author__ = "Mike Rans"
__svnid__ = "$Id: FindTabMenu.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import re
import wx

# Editra Libraries
import ebmlib
import util
import ed_msg
from syntax import syntax
import syntax.synglob as synglob

# Local imports
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.ModuleFinder.PythonModuleFinder import PythonModuleFinder

# Globals
_ = wx.GetTranslation

ID_COPY_MODULEPATH = wx.NewId()
ID_OPEN_MODULE = wx.NewId()

#-----------------------------------------------------------------------------#

class FindTabMenu(object):
    """Handles customization of buffer tab menu"""
    __metaclass__ = ebmlib.Singleton
    def __init__(self):
        super(FindTabMenu, self).__init__()

        # Attributes
        self._modname = None
        self._finder = None
        self._import = re.compile(r'import\s+([a-zA-Z0-9\._]+)')
        self._fromimport = re.compile(r'from\s+([a-zA-Z0-9\._]+)\s+import\s+([a-zA-Z0-9_]+)')

        # Editra Message Handlers
        ed_msg.Subscribe(self.OnTabMenu, ed_msg.EDMSG_UI_NB_TABMENU)
        ed_msg.Subscribe(self.OnBufferMenu, ed_msg.EDMSG_UI_STC_CONTEXT_MENU)

    def __del__(self):
        self.Unsubscription()

    def Unsubscription(self):
        ed_msg.Unsubscribe(self.OnTabMenu)
        ed_msg.Unsubscribe(self.OnBufferMenu)

    #---- Tab Context Menu ----#

    def OnTabMenu(self, msg):
        editor = wx.GetApp().GetCurrentBuffer()
        if editor:
            langid = getattr(editor, 'GetLangId', lambda: -1)()
            if langid == synglob.ID_LANG_PYTHON:
                contextmenumanager = msg.GetData()
                menu = contextmenumanager.GetMenu()
                menu.Append(ID_COPY_MODULEPATH, _("Copy Module Path"))
                contextmenumanager.AddHandler(ID_COPY_MODULEPATH, self.OnCopyModulePath)

    def OnCopyModulePath(self, editor, evt):
        path = os.path.normcase(editor.GetFileName())
        if path is not None:
            childPath, foo = PyStudioUtils.get_packageroot(path)
            modulepath = PyStudioUtils.get_modulepath(childPath)
            util.SetClipboardText(modulepath)

    #---- Buffer Right Click Context Menu ----#

    def OnBufferMenu(self, msg):
        """Handles customizing right click menu in buffer to add
        open module option when right clicking on import statements.

        """
        ctxmgr = msg.GetData()
        editor = ctxmgr.GetUserData('buffer')
        # Only show for Python files and
        if not editor or \
           editor.GetLangId() != synglob.ID_LANG_PYTHON or \
           editor.IsNonCode(ctxmgr.Position):
            return

        # Check if right clicking on an import statement
        lnum = editor.LineFromPosition(ctxmgr.Position)
        line = editor.GetLine(lnum)
        modname = self.GetModuleName(line)
        if modname:
            self._modname = modname
            ctxmgr.Menu.Insert(0, ID_OPEN_MODULE, _("Open module '%s'") % modname)
            ctxmgr.Menu.Insert(1, wx.ID_SEPARATOR)
            ctxmgr.AddHandler(ID_OPEN_MODULE, self.OnOpenModule)

    def OnOpenModule(self, editor, evt):
        """Handle open module context menu event"""
        if self._modname:
            vardict = dict()
            path = os.path.dirname(editor.GetFileName())
            self._finder = PythonModuleFinder(vardict, self._modname,
                                              quickfind=True, localpath=path)
            self._finder.Find(self.DoOpenModule) # Async call

    def DoOpenModule(self, data):
        """Callback for module finder job
        @param data: FindResultData

        """
        assert wx.Thread_IsMain(), "Not on Main Thread!"
        app = wx.GetApp()
        if len(data.Results) == 1:
            path = list(data.Results)[0]
            util.Log("[Finder][info] Opening Module file in editor: %s" % path)
            app.OpenFile(path)
        else:
            util.Log("[Finder][warn] Failed to find module to open")

    def GetModuleName(self, line):
        """Get the name of the module to open from the given line
        @return: string

        """
        mobj = self._import.match(line)
        mname = u''
        if mobj:
            mname = mobj.group(1)
        if not mname:
            mobj = self._fromimport.match(line)
            if mobj:
                mname = mobj.group(1)
        return mname

    def IsImportStatement(self, line):
        """Is the given line an import statement
        import foo
        from foo import bar
        import foo.bar
        import foo.bar as bar
        from foo.bar import foobar

        @param line: line text
        @return: bool

        """
        return bool(self._import.match(line) or self._fromimport.match(line))
