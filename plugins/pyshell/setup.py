# -*- coding: utf-8 -*-
"""Setup script to build the PyShell plugin. To build the plugin
just run setup.py bdist_egg and copy the egg to the plugin directory

"""

try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

__author__ = "Cody Precord <cprecord@editra.org>"
if setup != None:
    setup(
        name='PyShell',
        version='0.1',
        description=__doc__,
        author=__author__,
        packages=['pyshell'],
        entry_points='''
        [Editra.plugins]
        PyShell = pyshell:PyShell
        '''
        )
