# -*- coding: utf-8 -*-
# Name: PyStudioUtils.py
# Purpose: Utility functions
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Utility functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: PyStudioUtils.py 1564 2012-09-06 14:29:41Z CodyPrecord $"
__revision__ = "$Revision: 1564 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path
import codecs
import threading
import wx
from wx.stc import STC_INDIC2_MASK

# Editra Libraries
import ed_msg
import ed_thread
import ebmlib
import ed_txt
import util

# Local Imports
from PyStudio.Common.Messages import PyStudioMessages

# Globals
_ = wx.GetTranslation

class PyStudioUtils():

    @staticmethod
    def get_packageroot(filepath):
        # traverse downwards until we are out of a python package
        fullPath = os.path.abspath(filepath)
        parentPath, childPath = os.path.dirname(fullPath), os.path.basename(fullPath)

        while parentPath != "/" and os.path.exists(os.path.join(parentPath, '__init__.py')):
            childPath = os.path.join(os.path.basename(parentPath), childPath)
            parentPath = os.path.dirname(parentPath)
        return (childPath, parentPath)

    @staticmethod
    def get_modulepath(childPath):
        return os.path.splitext(childPath)[0].replace(os.path.sep, ".")

    @staticmethod
    def get_unicodevalue(_value):
        if not isinstance(_value, basestring):
            _value = repr(_value)
        _value = ed_txt.DecodeString(_value)
        if not ebmlib.IsUnicode(_value):
            # Give up and do what we can
            _value = unicode(_value, 'latin1', errors='replace')
        return _value

    @staticmethod
    def GetDefaultPython():
        if wx.Platform == "__WXMSW__":
            pythonpath = ebmlib.Which("python.exe")
        else:
            pythonpath = ebmlib.Which("python")
        if pythonpath:
            return pythonpath
        return u""

    @staticmethod
    def GetDefaultScript(script, pythonpath=None):
        if wx.Platform == "__WXMSW__":
            path = ebmlib.Which("%s.bat" % script)
        else:
            path = ebmlib.Which(script)
        if path:
            return path
        if pythonpath:
            path = os.path.dirname(pythonpath)
            if wx.Platform == "__WXMSW__":
                path = os.path.join(path, "Scripts", script)
            else:
                path = "/usr/local/bin/%s" % script
            if os.path.isfile(path):
                return path
        return u""

    @staticmethod
    def GetEditorForFile(mainw, fname):
        """Return the EdEditorView that's managing the file, if available
        @param fname: File name to open
        @param mainw: MainWindow instance to open the file in
        @return: Text control managing the file
        @rtype: ed_editv.EdEditorView

        """
        if mainw and hasattr(mainw, 'GetNotebook'):
            nb = mainw.GetNotebook()
            filepath = os.path.normcase(fname)
            if nb:
                for page in nb.GetTextControls():
                    tabfile = os.path.normcase(page.GetFileName())
                    if tabfile == filepath:
                        return page
        else:
            util.Log("[PyStudio][warn] invalid object in GetEditorForFile %s" % repr(mainw))

        return None

    @staticmethod
    def GetEditorOrOpenFile(mainw, fname):
        """Get an existing editor instance for the file or open it
        if it isn't currently open.

        """
        editor = PyStudioUtils.GetEditorForFile(mainw, fname)
        nb = mainw.GetNotebook()
        if editor:
            nb.ChangePage(editor.GetTabIndex())
        else:
            nb.OnDrop([fname])
        return PyStudioUtils.GetEditorForFile(mainw, fname)

    @staticmethod
    def GetProjectFile(mainw):
        """Get the currently open project file for the given MainWindow
        instance. PyProject interface method.
        @param mainw: MainWindow instance
        @return: ProjectFile or None

        """
        data = dict(project=None)
        ed_msg.PostMessage(PyStudioMessages.PYSTUDIO_PROJECT_GET, data, mainw.Id)
        return data.get('project', None)

    @staticmethod
    def set_indic(lineNo, editor):
        """Highlight a word by setting an indicator

        @param lineNo: line to set indicator starts
        @type lineNo: int
        """

        start = editor.PositionFromLine(lineNo)
        text = editor.GetLineUTF8(lineNo)
        editor.StartStyling(start, STC_INDIC2_MASK)
        editor.SetStyling(len(text), STC_INDIC2_MASK)
        return True

    @staticmethod
    def unset_indic(editor):
        """Remove all the indicators"""
        if not editor:
            return
        editor.StartStyling(0, STC_INDIC2_MASK)
        end = editor.GetTextLength()
        editor.SetStyling(end, 0)

    @staticmethod
    def error_dialog(parent, error):
        if error == '':
            return
        dlg = wx.MessageDialog(parent, error, _("Error"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

#-----------------------------------------------------------------------------#

class RunProcInThread(threading.Thread):
    """Background thread to run task in"""
    def __init__(self, desc, target, fn, *args, **kwargs):
        """@param fn: function to run
        @param target: callable(data) To receive output data
        @param desc: description of task
        """
        super(RunProcInThread, self).__init__()

        # Attributes
        self.desc = desc
        self.target = target
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.param = None

        self.setDaemon(True)

    def pass_parameter(self, param):
        self.param = param

    def run(self):
        try:
            data = self.fn(*self.args, **self.kwargs)
        except Exception, msg:
            util.Log("[%s][err] %s Failure: %s" % (self.desc, self.desc, msg))
            data = [(u"Error", unicode(msg), -1)]
        if self.target:
            if self.param is not None:
                wx.CallAfter(self.target, data, self.param)
            else:
                wx.CallAfter(self.target, data)

def RunAsyncTask(desc, target, fn, *args, **kwargs):
    """Delegate a long running task to Editra's threadpool"""
    def DoTask():
        try:
            data = fn(*args, **kwargs)
        except Exception, msg:
            util.Log("[%s][err] %s Failure: %s" % (desc, desc, msg))
            data = [(u"Error", unicode(msg), -1)]
        if target:
            wx.CallAfter(target, data)
    ed_thread.EdThreadPool().QueueJob(DoTask)
