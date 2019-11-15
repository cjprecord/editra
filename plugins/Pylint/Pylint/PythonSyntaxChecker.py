# -*- coding: utf-8 -*-
# Name: PythonSyntaxChecker.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Pylint module for Python data """

__author__ = "Mike Rans"
__svnid__ = "$Id: PythonSyntaxChecker.py 1067 2011-02-15 01:35:28Z CodyPrecord $"
__revision__ = "$Revision: 1067 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re

# Local Imports
from AbstractSyntaxChecker import AbstractSyntaxChecker
from PyToolsUtils import PyToolsUtils
from ProcessRunner import ProcessRunner
import ToolConfig

# Editra Imports
import util
import ebmlib

#-----------------------------------------------------------------------------#

class PythonSyntaxChecker(AbstractSyntaxChecker):
    def __init__(self, variabledict, filename):
        super(PythonSyntaxChecker, self).__init__(variabledict, filename)

        # Attributes
        self.dirvarfile = variabledict.get("DIRVARFILE")
        self.pylintargs = ["-f", "parseable", "-r", "n"]
        pylintrc = variabledict.get("PYLINTRC")
        if pylintrc:
            pylintrc = ["--rcfile=%s" % pylintrc]
            self.pylintargs += pylintrc
        else:
            # Use built-in configuration
            dlist = ToolConfig.GetConfigValue(ToolConfig.TLC_DISABLED_CHK)
            if dlist is not None and len(dlist):
                if len(dlist) > 1:
                    disable = ",".join(dlist)
                else:
                    disable = dlist[0]
                self.pylintargs += ["-d", disable]
        self.pythonpath = variabledict.get("PYTHONPATH")
        self.nopythonerror = u"***  FATAL ERROR: No local Python configured or found"
        self.nopylinterror = u"***  FATAL ERROR: No Pylint configured or found"

    def DoCheck(self):
        """Run pylint"""

        # Figure out what Python to use
        # 1) First check configuration
        # 2) Second check for it on the path
        localpythonpath = ToolConfig.GetConfigValue(ToolConfig.TLC_PYTHON_PATH)
        if not localpythonpath:
            localpythonpath = PyToolsUtils.GetDefaultPython()

        # No configured Python
        if not localpythonpath:
            return [(u"No Python", self.nopythonerror, u"NA"),]
        util.Log("[PyLint][info] Using Python: %s" % localpythonpath)

        childPath, parentPath = PyToolsUtils.get_packageroot(self.filename)

        # Start pylint
        modpath = PyToolsUtils.get_modulepath(childPath)
        if ebmlib.IsUnicode(modpath):
            # Convert to string
            modpath = modpath.encode(sys.getfilesystemencoding())
        allargs = self.pylintargs + [modpath,]
        pythoncode = "from pylint import lint;lint.Run(%s)" % repr(allargs)
        plint_cmd = [localpythonpath, "-c", pythoncode]
        util.Log("[PyLint][info] Starting command: %s" % repr(plint_cmd))
        util.Log("[Pylint][info] Using CWD: %s" % parentPath)
        processrunner = ProcessRunner(self.pythonpath)
        processrunner.runprocess(plint_cmd, parentPath)
        stdoutdata, stderrdata = processrunner.getalloutput()
        processrunner.restorepath()

        util.Log("[Pylint][info] stdout %s" % stdoutdata)
        util.Log("[Pylint][info] stderr %s" % stderrdata)
        stderrlower = stderrdata.lower()
        ind = stderrlower.find("importerror")
        if ind != -1:
            if stderrlower.find("pylint", ind) != -1:
                return [(u"No Pylint", self.nopylinterror, u"NA"),]

        # The parseable line format is '%(path)s:%(line)s: [%(sigle)s%(obj)s] %(msg)s'
        # NOTE: This would be cleaner if we added an Emacs reporter to pylint.reporters.text ..
        regex = re.compile(r"(.*):(.*): \[([A-Z])[, ]*(.*)\] (.*)%s" % os.linesep)
        rows = []
        if self.pythonpath:
            rows.append((u"***", u"Using PYTHONPATH + %s"\
                          % u", ".join(self.pythonpath), u"NA"))
        rows.append((u"***", u"Pylint command line: %s" % " ".join(plint_cmd), u"NA"))
        rows.append((u"***", u"Directory Variables file: %s" % self.dirvarfile, u"NA"))
        rowsdict = {}
        for matcher in regex.finditer(stdoutdata):
            if matcher is None:
                continue
            mtypeabr = matcher.group(3)
            linenostr = matcher.group(2)
            classmethod = matcher.group(4)
            mtext = matcher.group(5)
            if mtypeabr == u"E" or mtypeabr == u"F":
                mtype = u"Error"
            else:
                mtype = u"Warning"
            outtext = mtext
            if classmethod:
                outtext = u"[%s] %s" % (classmethod, outtext)
            try:
                lineno = int(linenostr)
                mtyperows = rowsdict.get(mtype)
                if not mtyperows:
                    mtyperows = {}
                    rowsdict[mtype] = mtyperows
                linenorows = mtyperows.get(lineno)
                if not linenorows:
                    linenorows = set()
                    mtyperows[lineno] = linenorows
                linenorows.add(outtext)
            except:
                rows.append((mtype, outtext, linenostr))
        for mtype in sorted(rowsdict):
            mtyperows = rowsdict[mtype]
            for lineno in sorted(mtyperows):
                linenorows = mtyperows[lineno]
                for outtext in sorted(linenorows):
                    rows.append((mtype, outtext, lineno))

        util.Log("[PyLint][info] Pylint command finished running")
        return rows
