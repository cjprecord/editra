# -*- coding: utf-8 -*-
# Name: PhpSyntaxChecker.py
# Purpose: Syntax Checker plugin
# Author: Giuseppe "Cowo" Corbelli
# Copyright: (c) 2009 Giuseppe "Cowo" Corbelli
# License: wxWindows License
##############################################################################

""" Syntax checker module for PHP data """

__version__ = "0.1"
__author__ = "Giuseppe 'Cowo' Corbelli"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import os
import re
import subprocess

# Local imports
import AbstractSyntaxChecker

#-----------------------------------------------------------------------------#

class PhpSyntaxChecker(AbstractSyntaxChecker.AbstractSyntaxChecker):
    reobj = re.compile('PHP\s+Parse\s+error:\s+(?P<type>.+?),\s*(?P<error>.+)\s+in\s+(?P<file>.+)\s+on line\s+(?P<line>\d+).*', re.I)
    @staticmethod
    def Check(fileName):
        try:
            path, fname = os.path.split(fname)
            pipe = subprocess.Popen("php -l %s" % fname,
                                    shell=False,
                                    cwd=path,
                                    stdout=subprocess.PIPE,
                                    stdin=None,
                                    stderr=subprocess.PIPE)
            retcode = pipe.wait()
        except OSError, e:
            return [ ("PHP execution error", str(e), None) ]
        except ValueError, e:
            return [ ("Popen() invalid args", str(e), None) ]
        except Exception, e:
            return [ ("Unknown Error", str(e), None) ]

        #No errors
        if (retcode == 0):
            return []

        errors = []
        for line in pipe.stderr:
            mObj = PhpSyntaxChecker.reobj.match(line.strip())
            if mObj is None:
                continue
            errors.append(
                (mObj.group('type'), mObj.group('error'), mObj.group('line'))
            )
        return errors
