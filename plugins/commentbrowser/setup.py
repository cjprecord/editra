# -*- coding: utf-8 -*-
# Setup script to build the Comment Browser plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into 
# a directory called dist in the same directory as this script.
""" Setup file for creating the commentbrowser plugin """

__author__ = "DR0ID"

try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='CommentBrowser',
        version='0.4',
        description=__doc__,
        author=__author__,
        author_email="dr0iddr0id@googlemail.com",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['commentbrowser'],
        package_data={'commentbrowser' : ['CHANGELOG.txt',
                                          'locale/*/LC_MESSAGES/*.mo']},
        entry_points='''
        [Editra.plugins]
        CommentBrowser = commentbrowser:CommentBrowserPanel
        '''
        )
