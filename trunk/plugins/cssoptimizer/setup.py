# -*- coding: utf-8 -*-
# Setup script to build the CssOptimizer plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""Creates an Editra Generator for optimizing CSS Files"""

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
        name='CssOptimizer',
        version='0.2',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="GPLv2",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['cssoptimizer'],
        entry_points='''
        [Editra.plugins]
        CssOptimizer = cssoptimizer:CssOptimizer
        '''
        )
