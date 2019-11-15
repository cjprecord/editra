# -*- coding: utf-8 -*-
# Name: AbstractSyntaxChecker.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################

""" Abstract syntax checker module """

__author__ = "Mike Rans"
__svnid__ = "$Id: AbstractSyntaxChecker.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#-----------------------------------------------------------------------------#
# Imports
from PyStudio.Common.PyStudioUtils import RunAsyncTask

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

    def RunSyntaxCheck(self):
        """Interface method override to perform the syntax check
        and return a list of tuples.
        @return: [ (Type, Error, Line), ]

        """
        raise NotImplementedError

    def Check(self, callback):
        """Asynchronous method to perform syntax check
        @param callback: callable(data) callback to receive data

        """
        RunAsyncTask("Lint", callback, self.RunSyntaxCheck)

    #---- Properties ----#
    FileName = property(lambda self: self.filename,
                        lambda self, name: setattr(self, 'filename', name))

