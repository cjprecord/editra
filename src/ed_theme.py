############################################################################
#    Copyright (C) 2005-2007 Cody Precord                                  #
#    cprecord@editra.org                                                   #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
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
# FILE: ed_theme.py                                                        #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#   This module defines and manages the theme of the editor. By default    #
# This doesnt do very much as it lets the system handle themeing so that   #
# the app will look and appear as natural as possible on the host system.  #
# The theme module is only here for those that wish to customize the       #
# appearance of the editor to there own liking.                            #
#                                                                          #
#
#
# METHODS:
#
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id$"
__author__ = "$Author$"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import ed_glob

#--------------------------------------------------------------------------#

class ED_Theme(wx.FileConfig):
    """Creates a Theme Object which is to be used as an
    information provider to the the art provider. It is derived
    from FileConfig so that themes will be defined using ini like
    text files in the base directory of each theme.
    
    """
    def __init__():
        """Initializes the object"""
