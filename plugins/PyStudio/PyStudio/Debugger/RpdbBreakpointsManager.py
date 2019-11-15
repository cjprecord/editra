# -*- coding: utf-8 -*-
# Name: RpdbBreakpointsManager.py
# Purpose: Debug Breakpoints
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" RpdbBreakpointsManager functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: RpdbBreakpointsManager.py 1144 2011-03-20 12:19:07Z rans@email.com $"
__revision__ = "$Revision: 1144 $"

#-----------------------------------------------------------------------------#
# Imports
import os.path

# Editra Libraries
import util

#----------------------------------------------------------------------------#

class RpdbBreakpointsManager(object):
    def __init__(self, rpdb2debugger):
        super(RpdbBreakpointsManager, self).__init__()
        self.rpdb2debugger = rpdb2debugger
    
    def installbreakpoints(self):
        self.rpdb2debugger.load_breakpoints()
        self.rpdb2debugger.clear_breakpoints()
        util.Log("[DbgBp][info] Setting breakpoints: (Path, Line No, Enabled, Expression)")
        for filepath in self.rpdb2debugger.breakpoints:
            linenos = self.rpdb2debugger.breakpoints[filepath]
            for lineno in linenos:
                enabled, exprstr = linenos[lineno]
                if filepath and lineno:
                    if os.path.isfile(filepath):
                        self.rpdb2debugger.set_breakpoint(filepath, lineno, exprstr, enabled)
                linenos[lineno] = enabled, exprstr
                util.Log("[DbgBp][info] %s, %d, %s, %s" % (filepath, lineno, enabled, exprstr))
