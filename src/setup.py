############################################################################
#    Copyright (C) 2007 Editra Development Team   			   #
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
__revision__ = "$Id: $"

#---- Imports ----#
import os
import sys
import glob
import ed_glob

#---- System Platform ----#
__platform__ = os.sys.platform

#---- Global Settings ----#
APP = ['editra.py']

AUTHOR = "Cody Precord"

AUTHOR_EMAIL = "staff@editra.org"

DATA_FILES = [ 
              ("src", ["dev_tool.py", "editra.py", "ed_glob.py",  
                       "ed_main.py", "ed_pages.py", "ed_stc.py", "ed_theme.py",
                       "ed_toolbar.py", "__init__.py", "prefdlg.py", 
                       "profiler.py", "setup.py", "util.py"]),
	      ("src/extern", ["extern/FlatNotebook.py", "extern/__init__.py",
			      "extern/README"]),
	      ("src/syntax", ["syntax/README", "syntax/asm.py", "syntax/asm68k.py",
		      	      "syntax/batch.py", "syntax/cpp.py", "syntax/css.py",
			      "syntax/html.py", "syntax/java.py", "syntax/javascript.py", 
			      "syntax/latex.py", "syntax/lisp.py", "syntax/make.py", "syntax/masm.py",
			      "syntax/mssql.py", "syntax/nasm.py", "syntax/nsis.py",
			      "syntax/pascal.py", "syntax/perl.py", "syntax/php.py",
			      "syntax/postscript.py", "syntax/python.py", "syntax/ruby.py",
			      "syntax/sh.py", "syntax/sql.py", "syntax/synglob.py",
			      "syntax/syntax.py", "syntax/vhdl.py", "syntax/visualbasic.py",
			      "syntax/xml.py", "syntax/__init__.py" ]),
              ("pixmaps", ["../pixmaps/editra.png", "../pixmaps/editra.ico",
                           "../pixmaps/editra.icns"]),
              ("pixmaps/mime", glob.glob("../pixmaps/mime/*.png")),
              ("pixmaps/toolbar/Stock", glob.glob('../pixmaps/toolbar/Nuovo/*')),
              ("templates", ["../templates/py"]),
              ("profiles", ["../profiles/default.pp",
                            "../profiles/.loader", 
                            "../profiles/default.pp.sample"]),
              ("locale/en_US/LC_MESSAGES", ["../locale/en_US/LC_MESSAGES/Editra.mo"]),
              ("locale/ja_JP/LC_MESSAGES", ["../locale/ja_JP/LC_MESSAGES/Editra.mo"]),
              "../README.txt","../CHANGELOG.txt","../COPYING.txt"
	     ]

DESCRIPTION = "Code Editor"

ICON = { 'Win' : "../pixmaps/editra.ico",
          'Mac' : "../pixmaps/editra.icns"
}

INCLUDES = ['syntax.*']

LICENSE = "GPLv2"

NAME = "Editra"

URL = "http://editra.org"

VERSION = ed_glob.__version__

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24
#---- End Global Settings ----#


#---- Setup Windows EXE ----#
if __platform__ == "win32":
    from distutils.core import setup
    try:
        import py2exe
    except:
        print "\n!! You dont have py2exe installed. Cant build a standalone .exe !!\n"
        exit()

    setup(
        name = NAME, 
        version = VERSION, 
        options = {"py2exe" : {"compressed" : 1, "optimize" : 2, "includes" : INCLUDES }},
        windows = [{"script": "editra.py","icon_resources": [(1, ICON['Win'])], "other_resources" : [(RT_MANIFEST, 1, manifest_template % dict(prog=NAME))],}],
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        license = LICENSE,
        url = URL,
        data_files = DATA_FILES
        )

#---- Setup MacOSX APP ----#
elif __platform__ == "darwin":
    try:
        from setuptools import setup
    except:
        print "\n!! You dont have py2app and/or setuptools installed!! Can't build the .app file !!\n"
        exit()

    py2app_options = dict(
                          iconfile = ICON['Mac'], 
                          argv_emulation = True,
                          optimize = True,
                          includes = INCLUDES)

    setup(
        app = APP,
        version = VERSION, 
        options = dict( py2app = py2app_options, ),
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        license = LICENSE,
        url = URL,
        data_files = DATA_FILES,
        #packages = ['syntax', 'extern'],
        setup_requires = ['py2app'],
        )

#---- Other Platform(s) ----#
else:
    print "\nCurrently we dont have a setup script that works for: " + __platform__
    print "\nPlease feel free to write one for us if you want and it will be inluded in future release"
 
