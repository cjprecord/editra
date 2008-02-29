###############################################################################
# Name: doctools.py                                                           #
# Purpose: Tools for managing document services                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
#--------------------------------------------------------------------------#
# FILE: doctools.py                                                        #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#  Provides helper functions and classes for managing documents and        #
# and their services.                                                      #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import util
from profiler import Profile_Get

#--------------------------------------------------------------------------#

class DocPositionMgr(object):
    """Object for managing the saving and setting of a collection of
    documents positions between sessions. Through the use of an in memory 
    dictionary during run time and on disk dictionary to use when starting 
    and stopping the editor.
    @note: saves config to ~/.Editra/cache/

    """
    def __init__(self, book_path):
        """Creates the position manager object
        @param book_path: path to on disk data file

        """
        object.__init__(self)
        self._book = book_path
        self._records = dict()
        if Profile_Get('SAVE_POS'):
            self.LoadBook(book_path)

    def AddRecord(self, vals):
        """Adds a record to the dictionary from a list of the
        filename vals[0] and the position value vals[1].
        @param vals: file path, cursor postion
        @type vals: tuple (str, int)

        """
        if len(vals) == 2:
            self._records[vals[0]] = vals[1]
            return True
        else:
            return False

    def GetBook(self):
        """Returns the current book used by this object
        @return: path to book used by this manager

        """
        return self._book

    def GetPos(self, name):
        """Get the position record for a given filename
        returns 0 if record is not found.
        @return: postion value for the given filename

        """
        return self._records.get(name, 0)

    def LoadBook(self, book):
        """Loads a set of records from an on disk dictionary
        the entries are formated as key=value with one entry
        per line in the file.
        @return: whether book was loaded or not
        @rtype: boolean

        """
        # If file does not exist create it and return
        if not os.path.exists(book):
            try:
                tfile = util.GetFileWriter(book)
                tfile.close()
            except (IOError, OSError):
                util.Log("[docpositionmgr] failed to load book")
                return False

        reader = util.GetFileReader(book)
        lines = reader.readlines()
        reader.close()
        for line in lines:
            line = line.strip()
            vals = line.split(u'=')
            if len(vals) != 2 or not os.path.exists(vals[0]):
                continue

            try:
                vals[1] = int(vals[1])
            except (TypeError, ValueError), msg:
                util.Log("[docpositionmgr] %s" % str(msg))
                continue
            else:
                self.AddRecord(vals)

        util.Log("[docpositionmgr] successfully loaded book")
        return True

    def WriteBook(self):
        """Writes the collection of files=pos to the config file
        @postcondtion: in memory doc data is written out to disk

        """
        writer = util.GetFileWriter(self.GetBook())
        try:
            for key in self._records:
                writer.write(u"%s=%d\n" % (key, self._records[key]))
            writer.close()
        except (IOError, AttributeError), msg:
            util.Log("[docpositionmgr] %s" % str(msg))
