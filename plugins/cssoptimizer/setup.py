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
    setup(
        name='CssOptimizer',
        version='0.4',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        package_data={'cssoptimizer' : ['CHANGELOG.txt',
                                        'locale/*/LC_MESSAGES/*.mo']},
        packages=['cssoptimizer'],
        entry_points='''
        [Editra.plugins]
        CssOptimizer = cssoptimizer:CssOptimizer
        '''
        )
