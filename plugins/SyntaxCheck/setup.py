# -*- coding: utf-8 -*-
# Setup script to build the SyntaxCheck plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into
# the dist directory of this folder.
"""Adds SyntaxCheck results window that can be opened in the Shelf.

"""
__author__ = "Giuseppe \"Cowo\" Corbelli"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='SyntaxCheck',
        version='0.2',
        description=__doc__,
        author=__author__,
        author_email="cowo@lugbs.linux.it",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['SyntaxCheck'],
        entry_points='''
        [Editra.plugins]
        SyntaxCheck = SyntaxCheck:SyntaxCheck
        '''
        )
