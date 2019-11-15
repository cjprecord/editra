# Setup script for building the Projects egg

from setuptools import setup

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision: 992 $"
__scid__ = "$Id: setup.py 992 2010-11-11 19:04:42Z CodyPrecord $"
__doc__ = "TheDailyWtf"
__version__ = "0.1"

setup(
      name    = "TheDailyWtf",
      version = __version__,
      description = __doc__,
      author = "Cody Precord",
      author_email = "cprecord@editra.org",
      license = "wxWindows",
      package_data={'dailywtf' : ['locale/*/LC_MESSAGES/*.mo']},
      packages = ['dailywtf'],
      entry_points = '''
      [Editra.plugins]
      TheDailyWtf = dailywtf:TheDailyWtf
      ''',
     )
