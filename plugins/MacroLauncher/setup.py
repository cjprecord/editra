# -*- coding: utf-8 -*-
# Setup script to build the sembrowser plugin. To build the plugin
# the dist directory of this folder.
"""Adds an interactive macro browser

"""
__author__ = "rca"

import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='MacroLauncher',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="roman.chyla@gmail.com",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['MacroLauncher'],
        entry_points='''
        [Editra.plugins]
        mlauncher = MacroLauncher:MacroLauncher
        ''',
        package_data = {
        # include macros into the .egg
        'macros': ['macro_*.py',],
        # But do not install them
        },
        exclude_package_data = { 'macros': ['macro_*.py'] },

        ),
        
    