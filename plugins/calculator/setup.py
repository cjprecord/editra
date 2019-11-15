# -*- coding: utf-8 -*-
# Setup script to build the calculator plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""The calculator plugin creates a simple calculator"""

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

__author__ = "Cody Precord"

if setup != None:
    setup(
        name='Calculator',
        version='0.6',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        package_data={'calculator' : ['locale/*/LC_MESSAGES/*.mo']},
        packages=['calculator'],
        entry_points='''
        [Editra.plugins]
        Calculator = calculator:Calculator
        '''
        )
