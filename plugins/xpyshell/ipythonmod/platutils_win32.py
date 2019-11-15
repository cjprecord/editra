# -*- coding: utf-8 -*-
""" Platform specific utility functions, win32 version

Importing this module directly is not portable - rather, import platutils 
to use these functions in platform agnostic fashion.

$Id: platutils_win32.py 909 2009-07-26 15:56:46Z CodyPrecord $

"""


#*****************************************************************************
#       Copyright (C) 2001-2006 Fernando Perez <fperez@colorado.edu>
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#*****************************************************************************

from IPython import Release
__author__  = '%s <%s>' % Release.authors['Ville']
__license__ = Release.license

import os

ignore_termtitle = 0

try:
    import ctypes
    SetConsoleTitleW=ctypes.windll.kernel32.SetConsoleTitleW
    SetConsoleTitleW.argtypes=[ctypes.c_wchar_p]
    def _set_term_title(title):
        """ Set terminal title using the ctypes"""
        SetConsoleTitleW(title)

except ImportError:
    def _set_term_title(title):
        """ Set terminal title using the 'title' command """
        curr=os.getcwd()
        os.chdir("C:") #Cannot be on network share when issuing system commands
        ret = os.system("title " + title)
        os.chdir(curr)
        if ret:
            ignore_termtitle = 1

def set_term_title(title):
    """ Set terminal title using the 'title' command """
    global ignore_termtitle

    if ignore_termtitle:
        return
    _set_term_title(title)

def freeze_term_title():
    global ignore_termtitle
    ignore_termtitle = 1

