#!/usr/bin/env python

from setuptools import setup
 
__author__ = "Erik Tollerud"
__doc__ = """A plugin to test regular expressions in the Editra shelf"""
__version__ = "0.1"
 
setup(
      name    = "RegexCheck",    # Plugin Name
      version = __version__,   # Plugin Version
      description = __doc__,   # Short plugin description
      author = __author__,     # Your Name
      author_email = "erik.tollerud@gmail.com",  # Your contact
      license = "wxWindows",       # Plugins licensing info
      packages = ['regexcheck'], # Package directory name(s)
      entry_points = '''
      [Editra.plugins]
      RegexCheck = regexcheck:RegexCheck
      '''
     )
