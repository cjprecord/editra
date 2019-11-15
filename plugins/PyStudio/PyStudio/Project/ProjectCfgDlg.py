###############################################################################
# Name: ProjectCfgDlg.py                                                      #
# Purpose: Project Configuration Dialog                                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2012 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Project Configuration Dialog

User interface to project configuration

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision: $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libs
import ed_basewin

#-----------------------------------------------------------------------------#

_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class ProjectCfgDlg(ed_basewin.EdBaseDialog):
    def __init__(self, parent, title=u""):
        super(ProjectCfgDlg, self).__init__(parent, title=title)

        # Attributes
        self.Panel = ProjectCfgPanel(self)

        # Setup
        self.SetInitialSize((450,400))

#-----------------------------------------------------------------------------#

class ProjectCfgPanel(wx.Panel):
    def __init__(self, parent):
        super(ProjectCfgPanel, self).__init__(parent)

        # Attributes
        self._book = ProjectCfgBook(self)

        # Layout
        sizer = wx.BoxSizer()
        sizer.Add(self._book, 1, wx.EXPAND)
        self.SetSizer(sizer)

#-----------------------------------------------------------------------------#

class ProjectCfgBook(wx.Treebook):
    def __init__(self, parent):
        super(ProjectCfgBook, self).__init__(parent, wx.ID_ANY)

        # Attributes
        
        # Events
        self.Bind(wx.EVT_TREEBOOK_PAGE_CHANGED, self.OnPageChange)

    def OnPageChange(self, evt):
        """Handle page change events"""
        evt.Skip()
