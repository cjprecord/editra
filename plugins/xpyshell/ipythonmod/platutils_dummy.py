# -*- coding: utf-8 -*-
""" Platform specific utility functions, dummy version 

This has empty implementation of the platutils functions, used for 
unsupported operating systems.

$Id: platutils_dummy.py 909 2009-07-26 15:56:46Z CodyPrecord $


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


def _dummy(*args,**kw):
    pass

set_term_title = _dummy

