# -*- coding: utf-8 -*-
# Setup script to build the pydebugger plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""The pydebugger plugin creates a simple calculator that can be docked
anywhere in the mainwindow by implementing the MainWindowI.

"""

try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

__author__ = "Cody Precord"

if setup != None:
    setup(
        name='PyDebugger',
        version='0.1',
        description=__doc__,
        author=__author__,
        author_email="cprecord@editra.org",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        package_data={'pydebugger' : ['locale/*/LC_MESSAGES/*.mo']},
        packages=['pydebugger'],
        entry_points='''
        [Editra.plugins]
        PyDebugger = pydebugger:PyDebugger
        '''
        )
