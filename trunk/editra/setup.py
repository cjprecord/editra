############################################################################
#    Copyright (C) 2006 Editra Development Team   			   #
#    staff@editra.org   						   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

"""
 Editra Setup Script

 Used for building the editra distribution files.

 USAGE:
  Windows:
  	python setup.py py2exe --bundle 2

  MacOSX:
  	python setup.py py2app
"""
__revision__ = "$Id: Exp $"

#---- Imports ----#
import os
import src.ed_glob as ed_glob

#---- System Platform ----#
__platform__ = os.sys.platform

#---- Global Settings ----#
APP = ['src/editra.py']

AUTHOR = "Cody Precord"

AUTHOR_EMAIL = "staff@editra.org"

DATA_FILES = [ 
              ("src", ["src/dev_tool.py", "src/editra.py", "src/ed_glob.py",  
                       "src/ed_main.py", "src/ed_pages.py", "src/ed_stc.py",
                       "src/ed_toolbar.py", "src/__init__.py", "src/prefdlg.py", 
                       "src/profiler.py", "src/setup.py", "src/util.py"]),
	      ("src/extern", ["src/extern/FlatNotebook.py", "src/extern/__init__.py",
			      "src/extern/README"]),
              ("pixmaps", ["pixmaps/editra.png", "pixmaps/editra.ico",
                           "pixmaps/editra.icns"]),
              ("pixmaps/mime", ["pixmaps/mime/c.png", 
                                "pixmaps/mime/cpp.png",
                                "pixmaps/mime/css.png",
                                "pixmaps/mime/header.png",
				"pixmaps/mime/html.png",
				"pixmaps/mime/java.png",
				"pixmaps/mime/makefile.png",
				"pixmaps/mime/perl.png",
				"pixmaps/mime/php.png",
				"pixmaps/mime/python.png",
				"pixmaps/mime/ruby.png",
				"pixmaps/mime/shell.png",
				"pixmaps/mime/tex.png",
				"pixmaps/mime/text.png"]),
              ("templates", ["templates/py"]),
              ("profiles", ["profiles/default.pp",
                            "profiles/.loader", 
                            "profiles/default.pp.sample"]),
	      ("language/english", ["language/english/ed_lang.py"]),
	      ("language/japanese", ["language/japanese/ed_lang.py"]),
              "README.txt","CHANGELOG.txt","COPYING.txt", "setup.py"
	     ]

DESCRIPTION = "Code Editor"

NAME = "Editra"

URL = "http://editra.org"

VERSION = ed_glob.__version__

#---- End Global Settings ----#


#---- Setup Windows EXE ----#
if __platform__ == "win32":
    from distutils.core import setup
    import py2exe

    setup(
        name = NAME, 
        version = VERSION, 
        options = {"py2exe" : {"optimize" : 2 }},
        windows = [{"script": "src/editra.py","icon_resources": [(1, "pixmaps/editra.ico")]}],
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        #packages = [],
      	data_files = DATA_FILES
	)

#---- Setup MacOSX APP ----#
elif __platform__ == "darwin":
    from setuptools import setup

    py2app_options = dict(
                          iconfile = 'pixmaps/editra.icns', 
                          argv_emulation = True,
                         )

    setup(
        app = APP,
        version = VERSION, 
        options = dict( py2app = py2app_options, ),
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        data_files = DATA_FILES,
        setup_requires = ['py2app'],
        )

#---- Unsupported Platform(s) ----#
else:
    print "\nCurrently Unsupported Platform " + __platform__
 
