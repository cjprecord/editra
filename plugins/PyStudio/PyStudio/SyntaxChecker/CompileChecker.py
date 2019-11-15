# -*- coding: utf-8 -*-
# Name: CompileChecker.py
# Purpose: Performs a compilation check on saved buffer
# Author: Cody Precord <cprecord@editra.org>
# Copyright: (c) 2011 Cody Precord
# License: wxWindows License
###############################################################################

"""CompileChecker"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: CompileChecker.py 1538 2012-06-06 19:35:52Z CodyPrecord $"
__revision__ = "$Revision: 1538 $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import re

# Editra imports
import ed_msg
import ed_marker
import ebmlib
import syntax.synglob as synglob
import util

# PyStudio imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.PyStudioUtils import RunAsyncTask, PyStudioUtils
from PyStudio.Common.ProcessCreator import ProcessCreator

#-----------------------------------------------------------------------------#

class CompileEntryPoint(object):
    """Entry point object for controlling compile checker"""
    __metaclass__ = ebmlib.Singleton
    def __init__(self):
        super(CompileEntryPoint, self).__init__()

        # Attributes
        self._errdata = dict() # file -> (linenum, errmsg)

        # Message Handlers
        ed_msg.Subscribe(self.OnFileSaved, ed_msg.EDMSG_FILE_SAVED)
        ed_msg.Subscribe(self.OnDwellStart, ed_msg.EDMSG_UI_STC_DWELL_START)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnFileSaved)
        ed_msg.Unsubscribe(self.OnDwellStart)

    def OnFileSaved(self, msg):
        """Performs file saved checks"""
        data = msg.GetData()
        if not data[0] or data[1] != synglob.ID_LANG_PYTHON:
            return

        buff = None
        for mw in wx.GetApp().GetMainWindows():
            if mw.Id == msg.Context:
                buff = PyStudioUtils.GetEditorForFile(mw, data[0])
                break

        if not buff:
            return

        buff.RemoveAllMarkers(ed_marker.ErrorMarker())
        if data[0] in self._errdata:
            del self._errdata[data[0]]

        if ToolConfig.GetConfigValue(ToolConfig.TLC_COMPILE_ON_SAVE, True):
            # Run the compilation check
            RunAsyncTask("CompileCheck", self.OnCheckComplete, self.DoCompileCheck, data[0])

    def OnDwellStart(self, msg):
        """Show calltips for the error if dwelling over a line"""
        data = msg.GetData()
        buf = data.get('stc', None)
        if buf:
            lineno = data.get('line', -1)
            fname = buf.GetFileName()
            errdata = self._errdata.get(fname, (-1, ""))
            if errdata[1] and lineno == errdata[0]+1:
                data['rdata'] = u" ".join(errdata[1].split())

    #--- Async Task Functions ----#

    def DoCompileCheck(self, path):
        """Run a compilation check on the given path
        @return: tuple(path, output)

        """
        flag, pypath = ToolConfig.GetPythonExecutablePath("CompileCheck")
        if not flag:
            # No configured Python
            return (None, u"No Python") # TODO translations (send error code)
        # run 'python -m py_compile fname'
        parentPath = ebmlib.GetPathName(path)
        fname = ebmlib.GetFileName(path)
        cmd = [pypath, '-m', 'py_compile', fname]
        # TODO: pythonpath?
        processcreator = ProcessCreator("CompileCheck", parentPath, cmd)
        process = processcreator.createprocess()
        stdoutdata, stderrdata = process.communicate()
        processcreator.restorepath()
        return (path, stderrdata)

    def OnCheckComplete(self, data):
        """Callback for when compile check"""
        if len(data) != 2:
            util.Log("[PyTools][err] OnCheckComplete Invalid Data %s" % repr(data))
            return

        path = data[0]
        err = data[1]
        if err:
            pat = re.compile("\('.*', ([0-9]+),")
            matchs = pat.findall(err)
            if len(matchs) and matchs[0].isdigit():
                line = max(0, int(matchs[0])-1)
                mw = wx.GetApp().GetActiveWindow()
                buff = PyStudioUtils.GetEditorForFile(mw, path)
                if buff:
                    self._errdata[path] = (line, err)
                    buff.AddMarker(ed_marker.ErrorMarker(), line)
                    buff.GotoLine(line)
