###############################################################################
# Name: Messages.py                                                           #
# Purpose: PyStudio ed_msg impl                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
PyStudio Messages

Definitions of ed_msg message types used by PyStudio components.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: Messages.py 1506 2011-11-19 18:20:39Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1506 $"

#-----------------------------------------------------------------------------#

class PyStudioMessages:
    """Namespace for message type identifiers"""
    ######### PROJECT RELATED MESSAGES #######################################
    # msgdata == ContextMenuManager instance
    # Subscribe to this message to add custom options to the PyProject ProjectTree's
    # context menu. MenuManager user data 'path' contains path of file/folder that
    # was clicked on in the ProjectTree.
    PYSTUDIO_PROJECT_MENU = ('PyStudio', 'Project', 'ContextMenu')

    # msgdata == dict(winid=mainwinid) (sent data)
    #            dict(winid=mainwinid, project=projfile) (return data)
    # Send this message to get the current
    PYSTUDIO_PROJECT_GET = ('PyStudio', 'Project', 'Get')

    # msgdata == ProjectFile
    # The project file was saved to the hard disk
    PYSTUDIO_PROJECT_SAVED = ('PyStudio', 'Project', 'Saved')

    # msgdata == ProjectFile
    # A project was loaded
    PYSTUDIO_PROJECT_LOADED = ('PyStudio', 'Project', 'Loaded')

    # msgdata == dict(project=ProjectFile, option=OPTION_NAME)
    # Context = MainWindow
    # A project option was changed / added
    PYSTUDIO_PROJECT_MODIFIED = ('PyStudio', 'Project', 'Modified')
    ######### END PROJECT RELATED MESSAGES ####################################
