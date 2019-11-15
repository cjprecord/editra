# -*- coding: utf-8 -*-
# Setup script to build the PyRun plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into 
# the dist directory of this folder.
"""Runs current python script and displays output in the Shelf. 
"""
__author__ = "Fred Lionetti"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='PyRun',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="flionetti@gmail.com",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['PyRun'],
        entry_points='''
        [Editra.plugins]
        PyRun = PyRun:PyRun
        '''
        )
