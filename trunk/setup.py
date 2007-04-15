#!/usr/bin/env python
############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
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
__revision__ = "$Revision$"

#---- Imports ----#
import os
import sys
import glob
import src.ed_glob as ed_glob
import src.syntax.syntax as syntax # So we can get file extensions
from distutils.command.build_ext import build_ext
from distutils.command.install import install
from distutils.command.install_lib import install_lib
#---- System Platform ----#
__platform__ = os.sys.platform

#---- Global Settings ----#
APP = ['src/Editra.py']
AUTHOR = "Cody Precord"
AUTHOR_EMAIL = "staff@editra.org"
YEAR = 2007

CLASSIFIERS = [
            'Development Status :: 2 - Alpha',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'Intended Audience :: End Users/Desktop',
            'OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Natural Language :: Japanese',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Text Editors'
            ]

SRC_SCRIPTS = [ ("src", glob.glob("src/*.py")),
                ("src/autocomp", glob.glob("src/autocomp/*.py")),
                ("src/extern", ["src/extern/__init__.py", "src/extern/README"]),
                ("src/syntax", glob.glob("src/syntax/*.py")),
                ("scripts", ["scripts/clean_dir.sh"]),
                ("scripts/i18n", glob.glob("scripts/i18n/*.po")),
]

DATA_FILES = [ 
              ("pixmaps", ["pixmaps/editra.png", "pixmaps/editra.ico",
                           "pixmaps/editra.icns", "pixmaps/editra_doc.icns"]),
              ("pixmaps/mime", glob.glob("pixmaps/mime/*.png")),
              ("pixmaps/theme/Stock",["pixmaps/theme/Stock/AUTHORS",
               "pixmaps/theme/Stock/COPYING",
               "pixmaps/theme/Stock/DONATE",
               "pixmaps/theme/Stock/README"]),
              ("pixmaps/theme/Stock/toolbar", glob.glob("pixmaps/theme/Stock/toolbar/*.png")),
              ("pixmaps/theme/Stock/menu", glob.glob("pixmaps/theme/Stock/menu/*.png")),
              ("templates", glob.glob("templates/*")),
              ("profiles", ["profiles/default.pp",
                            "profiles/.loader", 
                            "profiles/default.pp.sample"]),
              ("locale/en_US/LC_MESSAGES", ["locale/en_US/LC_MESSAGES/Editra.mo"]),
              ("locale/ja_JP/LC_MESSAGES", ["locale/ja_JP/LC_MESSAGES/Editra.mo"]),
              ("styles", glob.glob("styles/*.ess")),
              ("test_data", glob.glob("test_data/*")),
              ("docs", glob.glob("docs/*.txt")),
              "README.txt","CHANGELOG.txt","COPYING.txt", "pixmaps/editra_doc.icns"
            ]

DATA = [ "src/*.py", "src/syntax/*.py", "src/autocomp/*.py",
         "pixmaps/editra.png", "pixmaps/editra.ico", 'Editra',
         "pixmaps/*.icns", "pixmaps/mime/*.png", "pixmaps/theme/Stock/AUTHOR",
         "pixmaps/theme/Stock/COPYING", "pixmaps/theme/Stock/DONATE",
         "pixmaps/theme/README",
         "pixmaps/theme/Stock/toolbar/*.png", "pixmaps/theme/Stock/menu/*.png", 
         "profiles/default.pp", "profiles/.loader", "profiles/default.pp.sample",
         "locale/en_US/LC_MESSAGES/Editra.mo", "locale/ja_JP/LC_MESSAGES/Editra.mo", 
         "styles/*.ess", "test_data/*", "README.txt","CHANGELOG.txt","COPYING.txt"
]

DESCRIPTION = "Code Editor"

ICON = { 'Win' : "pixmaps/editra.ico",
         'Mac' : "pixmaps/Editra.icns"
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
if __platform__ == "win32" and 'py2exe' in sys.argv:
    from distutils.core import setup
    try:
        import py2exe
    except:
        print "\n!! You dont have py2exe installed. Cant build a standalone .exe !!\n"
        exit()

    # Hack for py2exe
    sys.path.append(os.path.abspath('src/'))

    setup(
        name = NAME, 
        version = VERSION, 
        options = {"py2exe" : {"compressed" : 1, "optimize" : 2, "includes" : INCLUDES }},
        windows = [{"script": "src/Editra.py",
                    "icon_resources": [(1, ICON['Win'])], 
                    "other_resources" : [(RT_MANIFEST, 1, manifest_template % dict(prog=NAME))],}],
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        maintainer = AUTHOR,
        maintainer_email = AUTHOR_EMAIL,
        license = LICENSE,
        url = URL,
        data_files = DATA_FILES,
        )

#---- Setup MacOSX APP ----#
elif __platform__ == "darwin" and 'py2app' in sys.argv:
    try:
        from setuptools import setup
    except:
        print "\n!! You dont have py2app and/or setuptools installed!! Can't build the .app file !!\n"
        exit()

    PLIST = dict(CFBundleName = ed_glob.prog_name,
             CFBundleIconFile = 'Editra.icns',
             CFBundleShortVersionString = ed_glob.version,
             CFBundleGetInfoString = ed_glob.prog_name + " " + ed_glob.version,
             CFBundleExecutable = ed_glob.prog_name,
             CFBundleIdentifier = "org.editra.%s" % ed_glob.prog_name.title(),
             CFBundleDocumentTypes = [dict(CFBundleTypeExtensions=syntax.GetFileExtensions(),
                                           CFBundleTypeIconFile='editra_doc',
                                           CFBundleTypeRole="Editor"
                                          ),
                                     ],
             NSHumanReadableCopyright = u"Copyright %s 2005-%d" % (AUTHOR, YEAR)
             )
 
    py2app_options = dict(
                          iconfile = ICON['Mac'], 
                          argv_emulation = True,
                          optimize = True,
                          includes = INCLUDES,
                          plist = PLIST)

    setup(
        app = APP,
        version = VERSION, 
        options = dict( py2app = py2app_options, ),
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        maintainer = AUTHOR,
        maintainer_email = AUTHOR_EMAIL,
        license = LICENSE,
        url = URL,
        data_files = DATA_FILES,
        setup_requires = ['py2app'],
        )

#---- Other Platform(s)/Source module install ----#
else:
    from distutils.core import setup
    try:
        import distutils.command.register
    except ImportError:
        kwds = {}
    else:
        kwds = {"classifiers" : CLASSIFIERS}

    # Force optimization
    if 'install' in sys.argv and ('O1' not in sys.argv or '02' not in sys.argv):
        sys.argv.append('-O2')

    setup(
        name = NAME,
        scripts = ['Editra'],
        version = VERSION,
        description = DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        maintainer = AUTHOR,
        maintainer_email = AUTHOR_EMAIL,
        url = URL,
        download_url = "http://editra.org/?page=download",
        license = LICENSE,
        platforms = [ "Many" ],
        packages = [ NAME ],
        package_dir = { NAME : '.' },
        package_data = { NAME : DATA},
        classifiers= CLASSIFIERS,
    #    requires = ['wx'],
        )
