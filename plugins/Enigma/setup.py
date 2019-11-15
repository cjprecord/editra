# -*- coding: utf-8 -*-
# Setup script to build the Enigma plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into
# the dist directory of this folder.
"""
Text encoder and decoder.

"""
__author__ = "Cody Precord"

try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

import os

if setup != None:
    setup(
        name='Enigma',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['', 'Enigma',],
        entry_points='''
        [Editra.plugins]
        Machine = Enigma:EnigmaPlugin
        '''
        )
