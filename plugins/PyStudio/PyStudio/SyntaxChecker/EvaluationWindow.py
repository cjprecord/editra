# -*- coding: utf-8 -*-
# Name: EvaluationWindow.py
# Purpose: Pylint plugin
# Author: Mike Rans
# Copyright: (c) 2012 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: EvaluationWindow.py 1463 2011-08-20 11:50:33Z rans@email.com $"
__revision__ = "$Revision: 1463 $"

#----------------------------------------------------------------------------#
# Imports
import wx

# Editra Libraries
import eclib

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class EvaluationWindow(eclib.OutputBuffer):
    """Evaluation Window"""

    def __init__(self, *args, **kwargs):
        super(EvaluationWindow, self).__init__(*args, **kwargs)

    def set_mainwindow(self, mw):
        self._mainw = mw
