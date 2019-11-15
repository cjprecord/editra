# -*- coding: utf-8 -*-
# Name: AbstractSyntaxChecker.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################

""" Abstract syntax checker module """

__author__ = "Mike Rans"
__svnid__ = "$Id: AbstractSyntaxChecker.py 1081 2011-02-22 15:52:37Z CodyPrecord $"
__revision__ = "$Revision: 1081 $"

#-----------------------------------------------------------------------------#
# Imports
import wx
import threading

# Editra Libraries
import util

#-----------------------------------------------------------------------------#

class SyntaxCheckThread(threading.Thread):
    """Background thread to run checker task in"""
    def __init__(self, checker, target):
        """@param checker: SyntaxChecker object instance
        @param target: callable(data) To receive output data
        """
        super(SyntaxCheckThread, self).__init__()

        # Attributes
        self.checker = checker
        self.target = target

    def run(self):
        try:
            data = self.checker.DoCheck()
        except Exception, msg:
            util.Log("[PyLint][err] Pylint Failure: %s" % msg)
            data = [(u"Error", unicode(msg), -1)]
        wx.CallAfter(self.target, data)

#-----------------------------------------------------------------------------#

class AbstractSyntaxChecker(object):
    def __init__(self, variabledict, filename):
        """ Process dictionary of variables that might be 
        useful to syntax checker.
        """
        super(AbstractSyntaxChecker, self).__init__()

        # Attributes
        self.filename = filename
        self.variabledict = variabledict

    def DoCheck(self):
        """Interface method override to perform the syntax check
        and return a list of tuples.
        @return: [ (Type, Error, Line), ]

        """
        raise NotImplementedError

    def Check(self, callback):
        """Asynchronous method to perform syntax check
        @param callback: callable(data) callback to receive data

        """
        worker = SyntaxCheckThread(self, callback)
        worker.start()

    #---- Properties ----#
    FileName = property(lambda self: self.filename,
                        lambda self, name: setattr(self, 'filename', name))

