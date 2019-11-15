###############################################################################
# Name: testfinder.py
# Purpose: Unittest for PyStudio.finder
# Author: Rudi Pettazzi <rudi.pettazzi@gmail.com>
# Copyright: (c) 2009 Cody Precord <staff@editra.org>
# License: wxWindows License
###############################################################################

__author__ = "Rudi Pettazzi <rudi.pettazzi@gmail.com>"
__svnid__ = "$Id: testfinder.py 1352 2011-05-14 05:32:55Z rans@email.com $"
__revision__ = "$Revision: 1352 $"

#-----------------------------------------------------------------------------#
# Imports
import unittest
import StringIO
import os
import sys

sys.path.insert(0, os.path.abspath('../PyStudio'))

import finder

#-----------------------------------------------------------------------------#

class TestModuleFinder(unittest.TestCase):
    def setUp(self):
        self.finder = finder.ModuleFinder(finder.GetSearchPath())
        if sys.platform == 'win32':
            self.base = sys.prefix
        else:
            self.base = '%s/lib/python%s' % (sys.prefix, sys.version[:3])

    def tearDown(self):
        pass

    def testFind1(self):
        """Empty input"""
        self.assertEquals(self.finder.Find(''), [])

    def testFind2(self):
        """None input"""
        self.assertEquals(self.finder.Find(None), [])

    def testFind3(self):
        """Case insensitive input"""
        res = self.finder.Find('stringio')
        self.check(res, [ os.path.join(self.base, 'StringIO.py') ])

    def testFind4(self):
        """Find module init"""
        res = self.finder.Find('ctypes')
        self.check(res, [ os.path.join(self.base, 'ctypes', '__init__.py') ])

    def testFind5(self):
        """Multiple results"""
        res = self.finder.Find('string')
        self.assertTrue(
            os.path.join(self.base, 'string.py') in res and
            os.path.join(self.base, 'StringIO.py') in res)

    def testFind6(self):
        """Package defined into .pth file"""
        res = self.finder.Find('wx.lib')
        patt = os.path.join('wx', 'lib', '__init__.py')
        self.assertTrue(res[0].endswith(patt))
    
    def testFind7(self):
        """Package match"""
        res = self.finder.Find('email.mime')
        self.assertTrue(os.path.join(
            self.base, 'email', 'mime', '__init__.py') in res)
        self.assertTrue(os.path.join(self.base, 'mimetools.py') not in res)
        
    def testFind8(self):
        """One more test with multiple results"""
        res = self.finder.Find('mime')
        self.assertTrue(os.path.join(
            self.base, 'email', 'mime', '__init__.py') in res)
        self.assertTrue(os.path.join(self.base, 'MimeWriter.py') in res)
        self.assertTrue(os.path.join(self.base, 'mimetypes.py') in res)
        self.assertTrue(os.path.join(self.base, 'mimetools.py') in res)

    def testFind9(self):
        """module defined into parent package. ex: os.path is 
        defined into os.py
        """
        res = self.finder.Find('os.path')
        self.assertTrue(len(res) == 1 and os.path.join(self.base, 'os.py') in res)

    def testFindUseImport(self):
        res = self.finder.Find('string', True)
        self.assertEquals(res[0], os.path.join(self.base, 'string.py'))

    def check(self, lst1, lst2):
        lst1 = lst1.sort()
        lst2 = lst2.sort()
        self.assertEqual(lst1, lst2)

if __name__ == '__main__':
    unittest.main()



