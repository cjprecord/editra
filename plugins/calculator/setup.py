# -*- coding: utf-8 -*-
# Setup script to build the calculator plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""The calculator plugin creates a simple calculator that can be docked
anywhere in the mainwindow by implementing the MainWindowI.

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
        name='Calculator',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="GPLv2",
        url="editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['calculator'],
        entry_points='''
        [Editra.plugins]
        Calculator = calculator:Calculator
        '''
        )
