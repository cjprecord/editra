# -*- coding: utf-8 -*-
""" Platform specific utility functions, posix version 

Importing this module directly is not portable - rather, import platutils 
to use these functions in platform agnostic fashion.

$Id: platutils_posix.py 909 2009-07-26 15:56:46Z CodyPrecord $

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

import sys
import os

ignore_termtitle = False

def _dummy_op(*a, **b):
    """ A no-op function """

def _set_term_title_xterm(title):
    """ Change virtual terminal title in xterm-workalikes """

    if ignore_termtitle:
        return
    
    sys.stdout.write('\033]%d;%s\007' % (0,title))


if os.environ.get('TERM','') == 'xterm':
    set_term_title = _set_term_title_xterm
else:
    set_term_title = _dummy_op

def freeze_term_title():
    global ignore_termtitle
    ignore_termtitle = True
