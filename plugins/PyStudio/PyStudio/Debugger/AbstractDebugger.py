# -*- coding: utf-8 -*-
# Name: AbstractDebugger.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Debugger module """

__author__ = "Mike Rans"
__svnid__ = "$Id: AbstractDebugger.py 1141 2011-03-19 15:49:44Z CodyPrecord $"
__revision__ = "$Revision: 1141 $"

#-----------------------------------------------------------------------------#

class AbstractDebugger(object):
    def __init__(self, variabledict, debuggerargs, programargs, 
        filename, debuggeewindow):
        """ Process dictionary of variables that might be
        useful to debugger.
        """
        super(AbstractDebugger, self).__init__()

        # Attributes
        self.filename = filename
        self.variabledict = variabledict
        self.debuggerargs = debuggerargs
        self.programargs = programargs
        self.debuggeewindow = debuggeewindow

    def RunDebuggee(self):
        """Interface method override to run the debuggee
        """
        raise NotImplementedError

    def RunDebugger(self):
        """Interface method override to run the debugger
        """
        raise NotImplementedError

    def Debug(self):
        """Asynchronous method to perform module find
        @param callback: callable(data) callback to receive data

        """
        self.RunDebuggee()

    #---- Properties ----#
    FileName = property(lambda self: self.filename,
                        lambda self, name: setattr(self, 'filename', name))

