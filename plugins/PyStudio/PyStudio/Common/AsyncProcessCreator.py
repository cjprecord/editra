# -*- coding: utf-8 -*-
# Name: AsyncProcessCreator.py
# Purpose: Create asynchronous processes
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Utility functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: AsyncProcessCreator.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#-----------------------------------------------------------------------------#
# Imports
from subprocess import STDOUT

# Local Imports
from PyStudio.Common.ProcessCreator import ProcessCreator

# Editra Libraries
import eclib
#-----------------------------------------------------------------------------#

class AsyncProcessCreator(eclib.ProcessThreadBase, ProcessCreator):
    def __init__(self, parent, textfn, info, parentPath, cmdline, pythonpath=None):
        eclib.ProcessThreadBase.__init__(self, parent)
        ProcessCreator.__init__(self, info, parentPath, cmdline, pythonpath)
        self.AddText = textfn

    def DoPopen(self):
        return self.createprocess(STDOUT)
        
    def GetPID(self):
        return self.Process.pid
        
