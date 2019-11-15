# -*- coding: utf-8 -*-
# Setup script to build the Terminal plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""Adds a graphical terminal that can be opened in the Shelf. Multiple
instances can be opened in the Shelf at once.

"""

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

__author__ = "Cody Precord"

if setup != None:
    setup(
        name='Terminal',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['terminal'],
        entry_points='''
        [Editra.plugins]
        Terminal = terminal:Terminal
        '''
        )
