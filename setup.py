#!/usr/bin/env python
###############################################################################
# Name: setup.py                                                              #
# Purpose: Setup/build script for Editra                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
 Editra Setup Script

 @summary: Used for building the editra distribution files and installations

 USAGE:
 1) Windows:
    - python setup.py py2exe --bundle 2

 2) MacOSX:
    - python setup.py py2app

 3) Boil an Egg
    - python setup.py bdist_egg

 4) Install as a python package
    - python setup.py install

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#---- Imports ----#
import os
import sys
import glob
import src.ed_glob as ed_glob
import src.syntax.syntax as syntax # So we can get file extensions

#---- System Platform ----#
__platform__ = os.sys.platform

#---- Global Settings ----#
APP = ['src/Editra.py']
AUTHOR = "Cody Precord"
AUTHOR_EMAIL = "staff@editra.org"
YEAR = 2007

CLASSIFIERS = [
            'Development Status :: 3 - Alpha',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Natural Language :: Japanese',
            'Natural Language :: Spanish',
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

DATA_FILES = [("include/python2.5", 
               glob.glob("include/python2.5/%s/*" % __platform__)),
              ("pixmaps", ["pixmaps/editra.png", "pixmaps/editra.ico",
                           "pixmaps/editra.icns", "pixmaps/editra_doc.icns",
                           "pixmaps/editra_doc.png", "pixmaps/blk_btn.png"]),
              ("pixmaps/theme/Default", ["pixmaps/theme/Default/README"]),
               ("pixmaps/theme/Tango",["pixmaps/theme/Tango/AUTHORS",
                                      "pixmaps/theme/Tango/COPYING"]),
              ("pixmaps/theme/Tango/toolbar", 
               glob.glob("pixmaps/theme/Tango/toolbar/*.png")),
              ("pixmaps/theme/Tango/menu", 
               glob.glob("pixmaps/theme/Tango/menu/*.png")),
              ("pixmaps/theme/Tango/mime", 
               glob.glob("pixmaps/theme/Tango/mime/*.png")),
              ("plugins", glob.glob("plugins/*.egg")),
              ("templates", glob.glob("templates/*")),
              ("profiles", ["profiles/default.ppb",
                            "profiles/.loader2"]), 
              ("locale/en_US/LC_MESSAGES", 
               ["locale/en_US/LC_MESSAGES/Editra.mo"]),
              ("locale/ja_JP/LC_MESSAGES", 
               ["locale/ja_JP/LC_MESSAGES/Editra.mo"]),
              ("locale/es_ES/LC_MESSAGES", 
               ["locale/es_ES/LC_MESSAGES/Editra.mo"]),
              ("styles", glob.glob("styles/*.ess")),
              ("tests", glob.glob("tests/*")),
              ("docs", glob.glob("docs/*.txt")), "AUTHORS", "FAQ", "INSTALL",
              "README","CHANGELOG","COPYING", "NEWS", "THANKS", "TODO",
              "setup.cfg", "pixmaps/editra_doc.icns"
             ]

DATA = [ "src/*.py", "src/syntax/*.py", "src/autocomp/*.py", "docs/*.txt",
         "pixmaps/*.png", "pixmaps/editra.ico", 'Editra', "src/extern/*.py",
         "pixmaps/*.icns", "pixmaps/theme/Default/README",
         "pixmaps/theme/Tango/AUTHOR", "pixmaps/theme/Tango/COPYING", 
         "pixmaps/theme/Tango/toolbar/*.png", "pixmaps/theme/Tango/menu/*.png",
         "pixmaps/theme/Tango/mime/*.png",
         "pixmaps/theme/Default/README", "profiles/default.ppb",
         "profiles/.loader2", "locale/en_US/LC_MESSAGES/Editra.mo",
         "locale/ja_JP/LC_MESSAGES/Editra.mo", 
         "locale/es_ES/LC_MESSAGES/Editra.mo", "styles/*.ess", "tests/*", 
         "AUTHORS", "CHANGELOG","COPYING", "FAQ", "INSTALL", "NEWS", "README",
         "THANKS", "TODO", "setup.cfg", "plugins/*.egg"
]

DESCRIPTION = "Developer's Text Editor"

LONG_DESCRIPT = \
r"""
========
Overview
========
Editra is a multi-platform text editor with an implementation that focuses on 
creating an easy to use interface and features that aid in code development. 
Currently it supports syntax highlighting and variety of other useful features 
for over 40 programing languages. For a more complete list of features and
screenshots visit the projects homepage at `Editra.org
<http://www.editra.org/>`_.

============
Dependancies
============
  * Python 2.4+
  * wxPython 2.8+ (Unicode build suggested)
  * setuptools 0.6+

"""

ICON = { 'Win' : "pixmaps/editra.ico",
         'Mac' : "pixmaps/Editra.icns"
}

# Excplicitly include some libraries that are either loaded dynamically
# or otherwise not able to be found by py2app/exe
INCLUDES = ['syntax.*']
if not sys.platform.startswith('win'):
    INCLUDES.extend(['pty', 'tty'])

LICENSE = "GPLv2"

NAME = "Editra"

URL = "http://editra.org"

VERSION = ed_glob.VERSION

MANIFEST_TEMPLATE = '''
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
    except ImportError:
        print "\n!! You dont have py2exe installed. !!\n"
        exit()

    # put package on path for py2exe
    sys.path.append(os.path.abspath('src/'))

    setup(
        name = NAME, 
        version = VERSION, 
        options = {"py2exe" : {"compressed" : 1, "optimize" : 2, 
                               "includes" : INCLUDES }},
        windows = [{"script": "src/Editra.py",
                    "icon_resources": [(1, ICON['Win'])], 
                    "other_resources" : [(RT_MANIFEST, 1, 
                                          MANIFEST_TEMPLATE % dict(prog=NAME))],
                  }],
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
    # Check for setuptools and ask to download if it is not available
    import src.extern.ez_setup as ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

    PLIST = dict(CFBundleName = ed_glob.PROG_NAME,
             CFBundleIconFile = 'Editra.icns',
             CFBundleShortVersionString = ed_glob.VERSION,
             CFBundleGetInfoString = ed_glob.PROG_NAME + " " + ed_glob.VERSION,
             CFBundleExecutable = ed_glob.PROG_NAME,
             CFBundleIdentifier = "org.editra.%s" % ed_glob.PROG_NAME.title(),
             CFBundleDocumentTypes = [dict(CFBundleTypeExtensions=syntax.GetFileExtensions(),
                                           CFBundleTypeIconFile='editra_doc',
                                           CFBundleTypeRole="Editor"
                                          ),
                                     ],
       #      NSAppleScriptEnabled="YES",
             NSHumanReadableCopyright = u"Copyright %s 2005-%d" % (AUTHOR, YEAR)
             )
 
    PY2APP_OPTS = dict(iconfile = ICON['Mac'], 
                       argv_emulation = True,
                       optimize = True,
                       includes = INCLUDES,
                       plist = PLIST)

    setup(
        app = APP,
        version = VERSION, 
        options = dict( py2app = PY2APP_OPTS),
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
    # Force optimization
    if 'install' in sys.argv and ('O1' not in sys.argv or '02' not in sys.argv):
        sys.argv.append('-O2')

    if 'bdist_egg' in sys.argv:
        try:
            from setuptools import setup
        except ImportError:
            print "To build an egg setuptools must be installed"
    else:
        from distutils.core import setup

    setup(
        name = NAME,
        scripts = ['Editra'],
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPT,
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
        )
