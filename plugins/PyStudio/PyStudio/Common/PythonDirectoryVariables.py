# -*- coding: utf-8 -*-
# Name: PythonDirectoryVariables.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Directory Variables module for Python data """

__version__ = "0.2"
__author__ = "Mike Rans"
__svnid__ = "$Id: PythonDirectoryVariables.py 1421 2011-07-13 20:54:09Z rans@email.com $"
__revision__ = "$Revision: 1421 $"

#-----------------------------------------------------------------------------#

# Imports
import os

# Local Imports
from PyStudio.Common.AbstractDirectoryVariables import AbstractDirectoryVariables

class PythonDirectoryVariables(AbstractDirectoryVariables):
    def __init__(self):
        super(PythonDirectoryVariables, self).__init__("py")
        self.pythonpath = []

    @staticmethod
    def get_path(dirvarfile, path):
        if path != "":
            if path[0] == ".":
                dir, _ = os.path.split(dirvarfile)
                path = os.path.join(dir, path)
        return path

    @staticmethod
    def get_abspath(dirvarfile, path):
        return os.path.abspath(PythonDirectoryVariables.get_path(dirvarfile, path))

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
                vardict[key] = self.get_abspath(dirvarfile, val)
            elif key == "DEBUGGERARGS":
                parts = val.split(" ")
                for i, part in enumerate(parts):
                    newpart = self.get_path(dirvarfile, part)
                    if newpart != part:
                        parts[i] = '"%s"' % os.path.abspath(newpart)
                vardict[key] = " ".join(parts)
            else:
                vardict[key] = val
        vardict["PYTHONPATH"] = self.pythonpath
        return vardict
