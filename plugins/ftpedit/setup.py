# Setup script for building the Projects egg

from setuptools import setup

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision: 1051 $"
__scid__ = "$Id: setup.py 1051 2011-02-08 20:22:09Z CodyPrecord $"
__doc__ = "FtpEdit"
__version__ = "0.4"

setup(
      name    = "FtpEdit",
      version = __version__,
      description = __doc__,
      author = "Cody Precord",
      author_email = "cprecord@editra.org",
      license = "wxWindows",
      package_data={'ftpedit' : ['locale/*/LC_MESSAGES/*.mo']},
      packages = ['ftpedit'],
      entry_points = '''
      [Editra.plugins]
      FtpEdit = ftpedit:FtpEdit
      ''',
     )
