# -*- coding: utf-8 -*-
# Setup script to build the File Browser plugin. To build the plugin
# just run 'python setup.py' and an egg will be built and put into 
# the plugin directory
"""

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
        name='FileBrowser',
        version='0.1',
        description=__doc__,
        author=__author__,
    author_email="cprecord@editra.org",
    license="GPLv2",
    url="editra.org",
    platforms=["Linux", "OS X", "Windows"],
    packages=['filebrowser'],
        entry_points='''
        [Editra.plugins]
        FileBrowser = filebrowser:FileBrowserPanel
        '''
        )
