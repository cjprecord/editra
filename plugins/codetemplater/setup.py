#!/usr/bin/env python

from setuptools import setup
 
__author__ = "Erik Tollerud"
__doc__ = """A plugin to allow customized code templates for commonly-used patterns"""
__version__ = "0.4"
 
setup(
      name    = "CodeTemplater",    # Plugin Name
      version = __version__,   # Plugin Version
      description = __doc__,   # Short plugin description
      author = __author__,     # Your Name
      author_email = "erik.tollerud@gmail.com",  # Your contact
      license = "wxWindows",       # Plugins licensing info
      packages = ['codetemplater'], # Package directory name(s)
      entry_points = '''
      [Editra.plugins]
      CodeTemplater = codetemplater:CodeTemplater
      '''
     )
