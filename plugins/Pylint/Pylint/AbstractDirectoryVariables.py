# -*- coding: utf-8 -*-
# Name: AbstractDirectoryVariables.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" Directory Variables module """

__author__ = "Mike Rans"
__svnid__ = "$Id: AbstractDirectoryVariables.py 1081 2011-02-22 15:52:37Z CodyPrecord $"
__revision__ = "$Revision: 1081 $"

#-----------------------------------------------------------------------------#

class AbstractDirectoryVariables(object):
    def __init__(self, filetype):
        self.dirvarfilename = "__dirvar_%s__.cfg" % filetype
    
    def read_dirvarfile(self, filepath):
        """ Return a dict of variables for usage by tools eg. pylint"""
        return {}
    
    def set_envvars(self, filepath):
        """ Set any environment variables eg. PYTHONPATH"""
        pass
        
    def restore_envvars(self):
        """ Restore changed environment variables """
        pass
