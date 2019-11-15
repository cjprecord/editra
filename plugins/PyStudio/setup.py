# -*- coding: utf-8 -*-
# Setup script to build the PyStudio plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into
# the dist directory of this folder.
"""
Upgrades Editra into a Python IDE, including syntax checking, module search and debugging

"""
__author__ = "Mike Rans, Cody Precord"

try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='PyStudio',
        version='0.8',
        description=__doc__,
        author=__author__,
        author_email="rans@email.com",
        license="wxWindows",
        url="http://editra.org",
        platforms=["Linux", "OS X", "Windows"],
        package_data={'PyStudio' : ['locale/*/LC_MESSAGES/*.mo']},
        packages=['','PyStudio','PyStudio.Common','PyStudio.SyntaxChecker',
                  'PyStudio.ModuleFinder','PyStudio.Debugger',
                  'PyStudio.Controller',
                  'PyStudio.Project'],
        entry_points='''
        [Editra.plugins]
        SyntaxChecker = PyStudio:PyAnalysis
        ModuleFinder = PyStudio:PyFind
        Debugger = PyStudio:PyDebug
        BreakPoints = PyStudio:PyBreakPoint
        StackThread = PyStudio:PyStackThread
        Variables = PyStudio:PyVariable
        Expressions = PyStudio:PyExpression
        Project = PyStudio:PyProject
        '''
        )
