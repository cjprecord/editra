# -*- coding: utf-8 -*-
# Name: RpdbVariablesManager.py
# Purpose: Debug State
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" RpdbVariablesManager functions """

__version__ = "0.2"
__author__ = "Mike Rans"
__svnid__ = "$Id: RpdbVariablesManager.py 1465 2011-08-20 14:17:18Z rans@email.com $"
__revision__ = "$Revision: 1465 $"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Local Imports
import rpdb2

#----------------------------------------------------------------------------#

class RpdbVariablesManager(object):
    def __init__(self, rpdb2debugger):
        super(RpdbVariablesManager, self).__init__()
        self.rpdb2debugger = rpdb2debugger

        event_type_dict = {rpdb2.CEventUnhandledException: {}}
        self.rpdb2debugger.register_callback(self.update_unhandled_exception, event_type_dict)
        
        event_type_dict = {rpdb2.CEventNamespace: {}}
        self.rpdb2debugger.register_callback(self.update_variables, event_type_dict)

        self.variableskey_map = {}
        
    def update_unhandled_exception(self, event):
        self.rpdb2debugger.unhandledexception = True
        self.rpdb2debugger.catchunhandledexception()

    def update_variables(self, event):
        wx.CallAfter(self.update_namespace)

    def update_namespace(self):    
        frame_index = self.rpdb2debugger.get_frameindex()
        if frame_index is None:
            self.rpdb2debugger.clearlocalvariables()
            self.rpdb2debugger.clearglobalvariables()
            self.rpdb2debugger.clearexceptions()
            return
        
        key = self.get_local_key(frame_index)
        expressionlist = self.variableskey_map.get(key, None)
        (key0, el0) = self.rpdb2debugger.updatelocalvariables(key, expressionlist)
        self.variableskey_map[key0] = el0
        
        key = self.get_global_key(frame_index)
        expressionlist = self.variableskey_map.get(key, None)
        (key1, el1) = self.rpdb2debugger.updateglobalvariables(key, expressionlist)
        self.variableskey_map[key1] = el1
        
        key = 'exception'
        expressionlist = self.variableskey_map.get(key, None)
        (key1, el1) = self.rpdb2debugger.updateexceptions(key, expressionlist)
        self.variableskey_map[key] = el1

    def get_local_key(self, frame_index):
        c = self.rpdb2debugger.curstack.get(rpdb2.DICT_KEY_CODE_LIST, [])
        key = c[-(1 + frame_index)]
        return key        
            
    def get_global_key(self, frame_index):
        s = self.rpdb2debugger.curstack.get(rpdb2.DICT_KEY_STACK, [])
        key = s[-(1 + frame_index)][0]
        return key
