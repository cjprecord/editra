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
@summary: mostly unimplemented
#--------------------------------------------------------------------------#
# FILE: ed_theme.py                                                        #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#   Provide an interface for creating icon themes for Editra. This will    #
#  allow for themes to be created, installed, and managed as plugins,      #
#  which means that they can be installed as single file instead of        #
#  dozens of individual image files.                                       #
#                                                                          #
# METHODS:                                                                 #
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import ed_glob
import plugin

#--------------------------------------------------------------------------#

class ThemeI(plugin.Interface):
    """Interface for defining an icon theme in Editra

    """

class IconProvider(plugin.Plugin):
    """Plugin that fetches requested icons from the current active theme.

    """
    observers = plugin.ExtensionPoint(ThemeI)
