# -*- coding: utf-8 -*-
# Name: findmodule.py
# Purpose: Components to find modules source files by name
# Author: Rudi Pettazzi <rudi.pettazzi@gmail.com>
# Copyright: (c) 2010 Rudi Pettazzi
# License: wxWindows License
##############################################################################
""" Components to find modules source files by name """

__author__ = "Rudi Pettazzi <rudi.pettazzi@gmail.com>"
__svnid__ = "$Id: findmodule.py 1219 2011-04-02 03:37:19Z CodyPrecord $"
__revision__ = "$Revision: 1219 $"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import re

#--------------------------------------------------------------------------#
# Globals

class ModuleFinder(object):
    """
    This component finds the source file of all the modules matching
    a given name, using one of the following strategies:
    1) loading the module with __import__ (0 or 1 results).
    This strategy is limited because it doesn't work if Editra is
    run from the binary installer and it can search only within
    the same python version that is actually running the editor.
    2) traversing the filesystem starting at a given search path
    (0 or N results) and matching files and packages using various
    criteria described below. This is the default strategy.

    For maximum execution and correctness performance, in the future, we could
    use a persistent index to lookup the modules.

    """

    _SRC_EXT = '.py', '.pyw'
    _BYTECODE_EXT = '.pyc', '.pyo'

    # a path we can safely skip for better performance
    _WXLOCALE = os.path.join('wx', 'locale')

    def __init__(self, searchpath=None, firstmatch=False):
        """
        @param searchpath: list of modules search path
        """
        super(ModuleFinder, self).__init__()

        if searchpath is None:
            searchpath = list(sys.path) # copy
        assert isinstance(searchpath, list)
        self._searchpath = searchpath
        self._sources = []
        self._exit_on_first = firstmatch

    def Find(self, text):
        """ Find the source files of modules matching text.
        @param text: the module name
        @return: a list with the module sources path if any, an empty list
        otherwise
        """
        rval = list()
        if text:
            rval = self._Find(text);
        return rval

    def _Find(self, text):
        """Find pure python modules matching text by walking the search path
        and doing a prefix match (case insensitive).
        If text contains the module package - for ex: 'compiler.ast' - the search
        is narrowed to that package/subdirectory, otherwise a free search is
        executed.

        Examples:
            find compiler.ast => compiler/ast.py
            find ast.py => compiler/ast.py
            find compiler.email => no result
            find string => string.py, StringIO.py, et al.
            find os.string => None
            find email.mime => email/mime/__init__.py
            find mime => email/mime/__init__.py, mimetools.py, et al.

        @param text: the module name
        @return: a list of source files matching text, an empty list if no
        source has been found.
        """
        parts = text.split('.')
        text = parts[-1]
        pattern = re.compile(text, re.I)

        self._sources = []

        for path in self._searchpath:
            if os.path.isdir(path):
                #print 'Analyzing search path %s' % path
                pkgs = parts[:-1]
                if pkgs:
                    self._PackageSearch(path, pattern, text, pkgs)
                else:
                    self._FreeSearch(path, pattern, text)
        return self._sources

    def _FreeSearch(self, path, pattern, text):
        """Traverse the given path looking for a module matching text.
        The possible matches are:
        1) **/text*.py
        2) **/text/__init__.py (ex: ctypes => ctypes/__init__.py)

        @param path: the current directory absolute path
        @param text: the module name to match
        """
        join = os.path.join # optimization
        exists = os.path.exists
        if self._exit_on_first and len(self._sources):
            return
        for filename in os.listdir(path):
            fqdn = join(path, filename)
            if os.path.isfile(fqdn) and self._IsPatternMatch(filename, pattern):
                self._sources.append(fqdn)
            elif os.path.isdir(fqdn) and not self._Skip(fqdn):
                pkgsource = join(fqdn, '__init__.py')
                if filename == text and exists(pkgsource):
                    self._sources.append(pkgsource)
                else:
                    self._FreeSearch(fqdn, pattern, text)

    def _PackageSearch(self, path, pattern, text, ns):
        """ Traverse the given path looking for a module matching text
        into the namespace ns. The possible matches are:
        1) ns.text*.py
        2) ns.text/__init__.py
        3) ns.py (ex: os.path => os.py)
        4) ns/__init__.py

        XXX: maybe 3) and 4) should be added to the result only if nothing
        matches 1) or 2)

        @param path: the current directory absolute path
        @param text: the module name to match (if the user entered a
                     dotted module, text contains only the last token).
        @param ns:   a list with the namespace parts relative to current path
                     For example, if text is 'email.mime.audio', ns should be
                     [ 'email', 'mime' ]
        """
        if ns:
            pkg = ns.pop(0)
        else:
            pkg = None

        join = os.path.join # optimization
        exists = os.path.exists
        for filename in os.listdir(path):
            fqdn = join(path, filename)
            if os.path.isfile(fqdn):
                if not pkg and self._IsPatternMatch(filename, pattern) or self._IsExactMatch(filename, pkg):
                    self._sources.append(fqdn)
            elif os.path.isdir(fqdn) and not self._Skip(fqdn):
                pkgsource = join(fqdn, '__init__.py')
                if filename == text and exists(pkgsource):
                    self._sources.append(pkgsource)
                    break # definitely looking for this
                elif filename == pkg:
                    self._PackageSearch(fqdn, pattern, text, ns)

    def _IsExactMatch(self, filename, text):
        """@return: true if filename is a source module and its name
        without extension is equals to text
        """
        parts = os.path.splitext(filename)
        return parts[1] in ModuleFinder._SRC_EXT and text == parts[0]

    def _IsPatternMatch(self, filename, pattern):
        """@return: True if filename is a source module and its name
        without extension matches pattern
        """
        parts = os.path.splitext(filename)
        return parts[1] in ModuleFinder._SRC_EXT and pattern.match(parts[0])

    def _Skip(self, path):
        return path in self._searchpath or path.endswith(ModuleFinder._WXLOCALE)

#--------------------------------------------------------------------------#
# Main
if __name__ == '__main__':
    # TODO: more proper command line argument handling...
    # modulefinder localdir modulename
    # modulefinder modulename
    path = list(sys.path)
    firstmatch = False
    if 'firstmatch' in sys.argv:
        firstmatch = True
        sys.argv.remove('firstmatch')
    if len(sys.argv) == 3:
        dpath = sys.argv[1]
        assert os.path.isdir(dpath)
        path.insert(0, dpath)
        sys.argv.pop(1)
    mf = ModuleFinder(path, firstmatch)
    result = mf.Find(sys.argv[1])
    print result
