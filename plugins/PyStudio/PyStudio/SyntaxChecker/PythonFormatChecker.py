# -*- coding: utf-8 -*-
# Name: PythonFormatChecker.py
# Purpose: PEP8 plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" PEP8 module for Python data """

__author__ = "Mike Rans"
__svnid__ = "$Id: PythonFormatChecker.py 1522 2012-03-30 18:53:13Z rans@email.com $"
__revision__ = "$Revision: 1522 $"

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

class PythonFormatChecker(AbstractSyntaxChecker):
    """Python format checker wrapper for Pep8"""
    def __init__(self, variabledict, filename):
        super(PythonFormatChecker, self).__init__(variabledict, filename)

        # Attributes
        self.pythonpath = variabledict.get("PYTHONPATH")
        # TODO: need to make translatable
        self.nopythonerror = u"***  FATAL ERROR: No local Python configured or found"
        self.nopep8error = u"***  FATAL ERROR: No Pep8 configured or found"

    def RunSyntaxCheck(self):
        """Run pep8
        @return: tuple([list_of_rows,], string)

        """

        flag, localpythonpath = ToolConfig.GetPythonExecutablePath("Pep8")

        if not flag:
            # No configured Python
            return ([(u"No Python", localpythonpath, u"NA")], u"None")

        childPath, parentPath = PyStudioUtils.get_packageroot(self.filename)

        # Start pep8 check
        pythoncode = "import sys,pep8;sys.argv=[u'pep8', %s];pep8._main()" % repr(childPath)
        pep8_cmd = [localpythonpath, "-c", pythoncode]
        processcreator = ProcessCreator("Pep8", parentPath, pep8_cmd, self.pythonpath)
        process = processcreator.createprocess()
        stdoutdata, stderrdata = process.communicate()
        processcreator.restorepath()

        util.Log("[Pep8][info] stdout %s" % stdoutdata)
        util.Log("[Pep8][info] stderr %s" % stderrdata)
        stderrlower = stderrdata.lower()
        ind = stderrlower.find("importerror")
        if ind != -1:
            if stderrlower.find("pep8", ind) != -1:
                return ([(u"No Pep8", self.nopep8error, u"NA")], u"None")

        # The parseable line format is:
        #       '%(path)s:%(line)s: [%(sigle)s%(obj)s] %(msg)s'
        regex = re.compile(r"(.*):(.*):(.*): ([A-Z])[0-9]* (.*)%s" % os.linesep)
        rows = []
        # TODO: returned messages need to be translatable
        if self.pythonpath:
            rows.append((u"***", u"Using PYTHONPATH + %s"\
                          % u", ".join(self.pythonpath), u"NA"))
        rows.append((u"***", u"Pep8 command line: %s" % " ".join(pep8_cmd), u"NA"))
        rowsdict = {}
        for matcher in regex.finditer(stdoutdata):
            if matcher is None:
                continue
            mtypeabr = matcher.group(4)
            linenostr = matcher.group(2)
            colnostr = matcher.group(3)
            mtext = matcher.group(5)
            if mtypeabr in (u"E", u"F"):
                mtype = u"Error"
            else: #TODO: add more specific filtering? / do translations on display
                mtype = u"Warning"

            outtext = "%s: %s" % (colnostr, mtext)
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
        
        util.Log("[Pep8][info] Pep8 command finished running")
        return (rows, stdoutdata)
