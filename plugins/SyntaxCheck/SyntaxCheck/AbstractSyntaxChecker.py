# -*- coding: utf-8 -*-
##############################################################################
# Name: php.py
# Purpose: Syntax Checker plugin
# Author: Giuseppe "Cowo" Corbelli
# Copyright: (c) 2009 Giuseppe "Cowo" Corbelli
# License: wxWindows License
##############################################################################

""" Abstract syntax checker module """

__author__ = "Giuseppe 'Cowo' Corbelli"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

class AbstractSyntaxChecker(object):
    @staticmethod
    def Check(fileName):
        """ Return a list of
            [ (Type, error, line), ... ]
        """
        pass
