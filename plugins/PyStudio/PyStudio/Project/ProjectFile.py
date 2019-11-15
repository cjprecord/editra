###############################################################################
# Name: ProjectFile.py                                                        #
# Purpose: Project File Abstraction                                           #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
ProjectFile

Project Data class representing the Project file

@see: ProjectXml

"""

#-----------------------------------------------------------------------------#
# Imports
import os

# Editra imports
import ed_msg
import ebmlib

# Local Imports
from PyStudio.Common.Messages import PyStudioMessages

#-----------------------------------------------------------------------------#

class ProjectFile(object):
    """Project file for use by the ProjectMgr"""
    def __init__(self, pxml, path):
        """
        @param pxml: ProjectXml
        @param path: Xml file path

        """
        super(ProjectFile, self).__init__()

        # Attributes
        self._pxml = pxml  # Project file xml data (serialization)
        self._path = path  # Project file path
        self._dirty = False

        # Setup
        # Ensure base data is available in project xml
        self._pxml.CreateOptionSet(u'general') # Root global option settings container

    #---- Properties ----#

    Path = property(lambda self: self._path)
    ProjectRoot = property(lambda self: os.path.dirname(self.Path))
    ProjectName = property(lambda self: self._pxml.name)
    Dirty = property(lambda self: self._dirty)

    #---- Implementation ---- #

    def Save(self, force=False):
        """Save the project file to disk"""
        if self.Dirty or force:
            self._pxml.Write(self.Path)
            self._dirty = False
            # Post notification for any observers that project settings have
            # been saved to disk.
            ed_msg.PostMessage(PyStudioMessages.PYSTUDIO_PROJECT_SAVED, self)

    #---- Project Data Accessors ----#

    def CreateOptionGrouping(self, domain):
        """Create a sub configuration object for a given set of
        related options. Associating them under a set with the given
        domain.
        @param domain: string

        """
        self._pxml.CreateOptionSet(domain)

    def GetOption(self, domain, optname):
        """Get the value for a project option
        @param domain: option set name 
        @param optname: option name
        @return: option value or None

        """
        option = None
        optionset = self.GetRelatedOptions(domain)
        if optionset is not None:
            option = optionset.get(optname, None)
        return option

    def GetRelatedOptions(self, domain):
        """Get the set of options for a given feature domain
        @param domain: option set name
        @return: dict or None

        """
        optionset = self._pxml.GetOptionSet(domain)
        if optionset is not None:
            tset = dict()
            for opt in optionset.options:
                tset[opt.type] = opt.value
            optionset = tset
        return optionset

    def SetOption(self, domain, optname, value):
        """Set a project option into the configuration
        @param optname: option name
        @param value: option value

        """
        optionset = self._pxml.GetOptionSet(domain)
        if optionset is None:
            # Create the new grouping
            optionset = self._pxml.CreateOptionSet(domain)
            self._dirty = True

        # Set the option value in the option set
        option = optionset.GetOption(optname)
        if option is not None:
            if option.value != value:
                option.value = value
                self._dirty = True
        else:
            # New option
            optionset.SetOption(optname, value)
            self._dirty = True

        # Notify observers
        if self.Dirty:
            ed_msg.PostMessage(PyStudioMessages.PYSTUDIO_PROJECT_MODIFIED,
                               dict(project=self, domain=domain, option=optname))

    #---- Project File Accessors ----#

    def GetAllProjectFiles(self):
        """Get all the source files in the project.
        @return: ebmlib.Directory

        """
        return ebmlib.GetDirectoryObject(self.ProjectRoot)
