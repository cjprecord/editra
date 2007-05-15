# -*- coding: utf-8 -*-
# Setup script to build the PyShell plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""Adds an interactive PyShell option to Editra's view menu. When
active the PyShell will be placed in the bottom portion of Editra's
frame, but it is dockable it can be moved to any other part of the frame
or pulled out as a standalone dialog by use of the mouse. This plugin
also interacts with Editra's PROFILE object so that it can remember if
it was active or not in the users last session.

"""

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

__author__ = "Cody Precord"

if setup != None:
    sys.argv.append("bdist_egg")
    sys.argv.append("--dist-dir=../.")
    setup(
        name='PyShell',
        version='0.1',
        description=__doc__,
        author=__author__,
	author_email="cprecord@editra.org",
	license="GPLv2",
	url="editra.org",
	platforms=["Linux", "OS X", "Windows"],
        packages=['pyshell'],
        entry_points='''
        [Editra.plugins]
        PyShell = pyshell:PyShell
        '''
        )
