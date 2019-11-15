# -*- coding: utf-8 -*-
# Setup script to build the Oxygen theme. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""Editra Icon theme based on the Oxygen Icons for KDE4"""
__author__ = "Cody Precord"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='Oxygen',
        version='0.4',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="by-sa-3.0",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['oxygen'],
        package_data={'oxygen' : ['pixmaps/AUTHORS', 'pixmaps/COPYING', 
                                  'pixmaps/menu/*.png', 'pixmaps/toolbar/*.png',
                                  'pixmaps/mime/*.png',]},
        entry_points='''
        [Editra.plugins]
        Oxygen = oxygen:OxygenTheme
        '''
        )
