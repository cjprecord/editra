# -*- coding: utf-8 -*-
# Name: RpdbThreadsManager.py
# Purpose: Debug State
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" RpdbThreadsManager functions """

__version__ = "0.2"
__author__ = "Mike Rans"
__svnid__ = "$Id: RpdbThreadsManager.py 1165 2011-03-24 21:55:29Z rans@email.com $"
__revision__ = "$Revision: 1165 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import rpdb2

#----------------------------------------------------------------------------#

class RpdbThreadsManager(object):
    def __init__(self, rpdb2debugger):
        super(RpdbThreadsManager, self).__init__()
        self.rpdb2debugger = rpdb2debugger
        
        event_type_dict = {rpdb2.CEventThreads: {}}
        self.rpdb2debugger.register_callback(self.update_threads, event_type_dict)

        event_type_dict = {rpdb2.CEventNoThreads: {}}
        self.rpdb2debugger.register_callback(self.update_no_threads, event_type_dict)

        event_type_dict = {rpdb2.CEventThreadBroken: {}}
        self.rpdb2debugger.register_callback(self.update_thread_broken, event_type_dict)

    def update_threads(self, event):
        wx.CallAfter(self.rpdb2debugger.updatethreadlist, event.m_current_thread, event.m_thread_list)

    def update_no_threads(self, event):
        wx.CallAfter(self.rpdb2debugger.clear_all)

    def update_thread_broken(self, event):
        wx.CallAfter(self.rpdb2debugger.updatethread, event.m_tid, event.m_name, True)
