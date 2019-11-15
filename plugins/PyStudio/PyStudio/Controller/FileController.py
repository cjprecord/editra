###############################################################################
# Name: FileController.py                                                     #
# Purpose: Project File Manager                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
File Controller Base Class

Defines base interface for file controllers used by the ProjectTree user
interface.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: FileController.py 1533 2012-04-30 19:17:11Z CodyPrecord $"
__revision__ = "$Revision: 1533 $"

#-----------------------------------------------------------------------------#
# Dependencies
import os
import sys
import shutil

# Editra Imports
import ebmlib

#-----------------------------------------------------------------------------#

class FileController(ebmlib.FactoryMixin):
    """Base factory for file controllers which implements all interface
    methods using default filesystem actions.

    """
    def __init__(self):
        super(FileController, self).__init__()

        # Attributes
        
    @classmethod
    def GetMetaDefaults(cls):
        """Return mapping of default meta-data
        base class implements the controller for the operating systems file
        system. Subclasses should define their own nested `meta` class that
        defines the `system` attribute which is used to identify the appropriate
        controller to use.

        """
        return dict(system="OS")

    #---- Interface Implementation ----#

    def CreateFile(self, path, name):
        """Create a new file at the given path
        @param path: directory path
        @param name: file name
        @return: FileOpStatus

        """
        rval = ebmlib.MakeNewFile(path, name)
        return _GetOpStatus(os.path.join(path, name), rval)

    def CreateFolder(self, path, name):
        """Create a new folder at the given path
        @param path: directory path
        @param name: folder name
        @return: FileOpStatus

        """
        rval = ebmlib.MakeNewFolder(path, name)
        return _GetOpStatus(os.path.join(path, name), rval)

    def Delete(self, path):
        """Delete the given path
        @param path: path to delete
        @return: FileOpStatus

        """
        rval = (True, path)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except OSError, err:
            rval = (False, str(err))
        return _GetOpStatus(path, rval)

    def MoveToTrash(self, path):
        """Move the given path to the trash
        @param path: file/folder path

        """
        rval = (True, path)
        try:
            ebmlib.MoveToTrash(path)
        except Exception, err:
            rval = (False, str(err))
        return _GetOpStatus(path, rval)

    def Rename(self, old, new):
        """Rename a file or folder
        @param old: current file path
        @param new: new name (path) for old
        @return: FileOpStatus

        """
        rval = (True, old)
        try:
            os.rename(old, new)
        except OSError, err:
            rval = (False, str(err))
        return _GetOpStatus(old, rval)

#-----------------------------------------------------------------------------#

class FileOpStatus(object):
    """Return object for FileController errors"""
    def __init__(self, path, err=None):
        """Create the error object
        @param path: path
        @param err: exception object

        """
        super(FileOpStatus, self).__init__()

        # Attributes
        self._path = path
        self._err = err

    def __nonzero__(self):
        return self._err != None

    Path = property(lambda self: self._path)
    Error = property(lambda self: self._err)

#-----------------------------------------------------------------------------#

def _GetOpStatus(path, rval):
    """Create a FileOpStatus object from the ebmlib return value
    @param rval: tuple(success, error or path)
    @return: FileOpStatus

    """
    if rval[0]:
        # operation succeeded
        status = FileOpStatus(rval[1], None)
    else:
        # operation failed
        status = FileOpStatus(path, rval[1])
    return status
