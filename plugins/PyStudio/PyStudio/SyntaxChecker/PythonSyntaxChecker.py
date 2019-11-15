# -*- coding: utf-8 -*-
# Name: PythonSyntaxChecker.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Pylint module for Python data """

__author__ = "Mike Rans"
__svnid__ = "$Id: PythonSyntaxChecker.py 1529 2012-04-27 18:23:36Z CodyPrecord $"
__revision__ = "$Revision: 1529 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import re

# Local Imports
from PyStudio.Common import ToolConfig
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.ProcessCreator import ProcessCreator
from PyStudio.SyntaxChecker.AbstractSyntaxChecker import AbstractSyntaxChecker

# Editra Libraries
import util

#-----------------------------------------------------------------------------#

class PythonSyntaxChecker(AbstractSyntaxChecker):
    """Python syntax checker wrapper for PyLint"""
    def __init__(self, variabledict, filename):
        super(PythonSyntaxChecker, self).__init__(variabledict, filename)

        # Attributes
        self.dirvarfile = variabledict.get("DIRVARFILE")
        self.pylintargs = ["-f", "parseable"]
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
        # TODO: need to make translatable
        self.nopythonerror = u"***  FATAL ERROR: No local Python configured or found"
        self.nopylinterror = u"***  FATAL ERROR: No Pylint configured or found"

    def RunSyntaxCheck(self):
        """Run pylint"""

        flag, localpythonpath = ToolConfig.GetPythonExecutablePath("PyLint")

        if not flag:
            # No configured Python
            return ([(u"No Python", localpythonpath, u"NA")], u"None")

        childPath, parentPath = PyStudioUtils.get_packageroot(self.filename)

        # Start pylint
        modpath = PyStudioUtils.get_modulepath(childPath)
        allargs = self.pylintargs + [modpath,]
        pythoncode = "from pylint import lint;lint.Run(%s)" % repr(allargs)
        plint_cmd = [localpythonpath, "-c", pythoncode]
        processcreator = ProcessCreator("Pylint", parentPath, plint_cmd, self.pythonpath)
        process = processcreator.createprocess()
        stdoutdata, stderrdata = process.communicate()
        processcreator.restorepath()

        util.Log("[Pylint][info] stdout %s" % stdoutdata)
        util.Log("[Pylint][info] stderr %s" % stderrdata)
        stderrlower = stderrdata.lower()
        ind = stderrlower.find("importerror")
        if ind != -1:
            if stderrlower.find("pylint", ind) != -1:
                return ([(u"No Pylint", self.nopylinterror, u"NA")], u"None")

        # The parseable line format is:
        #       '%(path)s:%(line)s: [%(sigle)s%(obj)s] %(msg)s'
        regex = re.compile(r"(.*):(.*): \[([A-Z])[, ]*(.*)\] (.*)%s" % os.linesep)
        rows = []
        # TODO: returned messages need to be translatable
        if self.pythonpath:
            rows.append((u"***", u"Using PYTHONPATH + %s"\
                          % u", ".join(self.pythonpath), u"NA"))
        rows.append((u"***", u"Pylint command line: %s" % " ".join(plint_cmd), u"NA"))
        rows.append((u"***", u"Directory Variables file: %s" % self.dirvarfile, u"NA"))
        rowsdict = {}
        lastmatchindex = 0
        for matcher in regex.finditer(stdoutdata):
            if matcher is None:
                continue
            mtypeabr = matcher.group(3)
            linenostr = matcher.group(2)
            classmeth = matcher.group(4)
            mtext = matcher.group(5)
            lastmatchindex = matcher.end(5)
            if mtypeabr in (u"E", u"F"):
                mtype = u"Error"
            elif mtypeabr == u"C":
                mtype = u"Convention"
            elif mtypeabr == u"R":
                mtype = u"Refactor"
            else: # TODO: add more specific filtering? / do translations on display
                mtype = u"Warning"

            outtext = mtext
            if classmeth:
                outtext = u"[%s] %s" % (classmeth, outtext)

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

        index = stdoutdata.find("Report", lastmatchindex)
        util.Log("[PyLint][info] Pylint command finished running")
        if index == -1:
            return (rows, "")
        return (rows, stdoutdata[index:].replace("\r", ""))
