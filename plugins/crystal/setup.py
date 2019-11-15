# -*- coding: utf-8 -*-
# Setup script to build the crystal theme. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""Editra Icon theme based on the Crystal Project icons"""
__author__ = "Cody Precord"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='Crystal',
        version='0.2',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="LGPL",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['crystal'],
        package_data={'crystal' : ['pixmaps/readme.txt', 
                                  'pixmaps/menu/*.png', 'pixmaps/toolbar/*.png',
                                  'pixmaps/mime/*.png',]},
        entry_points='''
        [Editra.plugins]
        Crystal = crystal:CrystalTheme
        '''
        )
