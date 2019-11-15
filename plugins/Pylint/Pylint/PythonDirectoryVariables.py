# -*- coding: utf-8 -*-
# Name: PythonDirectoryVariables.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Directory Variables module for Python data """

__author__ = "Mike Rans"
__svnid__ = "$Id: PythonDirectoryVariables.py 1081 2011-02-22 15:52:37Z CodyPrecord $"
__revision__ = "$Revision: 1081 $"

#-----------------------------------------------------------------------------#
# Imports
import os

# Local Imports
from AbstractDirectoryVariables import AbstractDirectoryVariables

#-----------------------------------------------------------------------------#

class PythonDirectoryVariables(AbstractDirectoryVariables):
    def __init__(self):
        super(PythonDirectoryVariables, self).__init__("py")
        self.pythonpath = []

    @staticmethod
    def get_abspath(dirvarfile, path):
        if path != "":
            if path[0] == ".":
                dir, _ = os.path.split(dirvarfile)
                path = os.path.join(dir, path)
        return os.path.abspath(path)

    def recurseup(self, dir):
        dir, rest = os.path.split(dir)
        dirvarfile = os.path.join(dir, self.dirvarfilename)
        if os.path.isfile(dirvarfile):
            return dirvarfile
        if not rest:
            return None
        return self.recurseup(dir)

    def read_dirvarfile(self, filepath):
        dirvarfile = self.recurseup(filepath)
        if not dirvarfile:
            return {}
        dirvarfile = os.path.abspath(dirvarfile)
        file = open(dirvarfile)
        vardict = {}
        vardict["DIRVARFILE"] = dirvarfile
        for line in file:
            if not line or line.find("=") == -1:
                continue
            key, valstr = line.split("=")
            val = valstr.rstrip()
            if key == "PYTHONPATH":
                allnewpaths = val.split(",")
                for path in allnewpaths:
                    self.pythonpath.append(self.get_abspath(dirvarfile, path))
            elif key == "PYLINTRC":
                vardict["PYLINTRC"] = '"%s"' % self.get_abspath(dirvarfile, val)
        vardict["PYTHONPATH"] = self.pythonpath
        return vardict
