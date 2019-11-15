# -*- coding: utf-8 -*-
# Name: PythonSyntaxChecker.py
# Purpose: Syntax Checker plugin
# Author: Giuseppe "Cowo" Corbelli
# Copyright: (c) 2009 Giuseppe "Cowo" Corbelli
# License: wxWindows License
##############################################################################
""" Syntax checker module for Python data """

__version__ = "0.1"
__author__ = "Giuseppe 'Cowo' Corbelli"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import AbstractSyntaxChecker

#-----------------------------------------------------------------------------#

class PythonSyntaxChecker(AbstractSyntaxChecker.AbstractSyntaxChecker):
    @staticmethod
    def Check(fileName):
        try:
            fd = open(fileName, 'r')
            code = fd.read().replace('\r\n', '\n').replace('\r', '\n')
            compile(code, fileName, 'exec')
        except SyntaxError, e:
            return [ ("Syntax Error", e.text.rstrip(), e.lineno) ]
        except IndentationError, e:
            return [ ("Indentation Error", e.text.rstrip(), e.lineno) ]
        except TypeError, e:
            return [ ("Type Error", "Source contains NULL bytes", None) ]
        except Exception, e:
            return [ ("Unknown Error", str(e), None) ]

        return []
