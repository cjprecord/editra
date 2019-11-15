# -*- coding: utf-8 -*-
# Setup script to build the Pylint plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into
# the dist directory of this folder.
"""Adds Pylint results window that can be opened in the Shelf.

"""
__author__ = "Mike Rans"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='Pylint',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="rans@email.com",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['Pylint'],
        entry_points='''
        [Editra.plugins]
        Pylint = Pylint:Pylint
        '''
        )
