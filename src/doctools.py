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
#--------------------------------------------------------------------------#
# FILE: doctools.py                                                        #
# @author: Cody Precord                                                    #
# LANGUAGE: Python                                                         #
# @summary:                                                                #
#  Provides helper functions and classes for managing documents and        #
# and their services.                                                      #
#                                                                          #
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import ed_glob
import util
import dev_tool

#--------------------------------------------------------------------------#

class DocPositionMgr(object):
    """Object for managing the saving and settign of a
    documents position between sessions. Through the use
    of an in memory dictionary during run time and on 
    disk dictionary to use when starting and stopping the editor.

    """
    def __init__(self, book_path):
        """Creates the position manager object
        @param book_path: path to on disk data file

        """
        object.__init__(self)
        self._book = book_path
        self._records = dict()
        if ed_glob.PROFILE['SAVE_POS']:
            if self.LoadBook(book_path):
                dev_tool.DEBUGP("[docpositionmgr] successfully loaded book")
            else:
                dev_tool.DEBUGP("[docpositionmgr] failed to load book")

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
        if self._records.has_key(name):
            return self._records[name]
        else:
            return 0

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
                dev_tool.DEBUGP("[docpositionmgr] %s" % str(msg))
                continue
            else:
                self.AddRecord(vals)
        return True

    def WriteBook(self):
        """Writes the in memory dictionary to the on disk one
        @postcondtion: in memory doc data is written out to disk

        """
        writer = util.GetFileWriter(self.GetBook())
        try:
            for key in self._records:
                writer.write(u"%s=%d\n" % (key, self._records[key]))
            writer.close()
        except (IOError, AttributeError), msg:
            dev_tool.DEBUGP("[docpositionmgr] %s" % str(msg))

