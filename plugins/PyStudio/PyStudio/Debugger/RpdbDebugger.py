# -*- coding: utf-8 -*-
# Name: RpdbDebugger.py
# Purpose: Debug Client
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" RpdbDebugger functions """

__author__ = "Mike Rans"
__svnid__ = "$Id: RpdbDebugger.py 1465 2011-08-20 14:17:18Z rans@email.com $"
__revision__ = "$Revision: 1465 $"

#-----------------------------------------------------------------------------#
# Imports
import traceback
from time import sleep
import wx

# Editra Libraries
import util
from profiler import Profile_Get
import ed_msg
import ebmlib

# Local Imports
import rpdb2
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Debugger.RpdbStateManager import RpdbStateManager
from PyStudio.Debugger.RpdbBreakpointsManager import RpdbBreakpointsManager
from PyStudio.Debugger.RpdbStackFrameManager import RpdbStackFrameManager
from PyStudio.Debugger.RpdbThreadsManager import RpdbThreadsManager
from PyStudio.Debugger.RpdbVariablesManager import RpdbVariablesManager

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class RpdbDebugger(object):
    __metaclass__ = ebmlib.Singleton

    fAllowUnencrypted = True
    fRemote = False
    host = "localhost"
    fAttach = True
    fchdir = False
    password = "editra123"

    def __init__(self):
        super(RpdbDebugger, self).__init__()

        # Setup
        self.sessionmanager = rpdb2.CSessionManager(RpdbDebugger.password, \
            RpdbDebugger.fAllowUnencrypted, RpdbDebugger.fRemote, RpdbDebugger.host)
        self.breakpointmanager = RpdbBreakpointsManager(self)
        self.statemanager = RpdbStateManager(self)
        self.stackframemanager = RpdbStackFrameManager(self)
        self.threadmanager = RpdbThreadsManager(self)
        self.variablesmanager = RpdbVariablesManager(self)
        
        # attributes that will be set later
        self.attached = False
        self.analyzing = False
        self.broken = False
        self.mainwindow = None
        self.processcreator = None
        self.breakpoints = {}
        self.breakpoints_installed = False
        self.curstack = {}
        self.unhandledexception = False
        self.debuggerattachedtext = None
        self.debuggerdetachedtext = None
        self.remoteprocess = False
        self.abortattach = False
        
        # functions that will be set later

        # message handler
        self.conflictingmodules = lambda x:None
        self.setstepmarker = lambda x,y:None        
        self.clearstepmarker = lambda:None
        self.setstepmarker = lambda x,y:None
        self.restorestepmarker = lambda x:None      
        # debuggee shelf
        self.debugbuttonsupdate = lambda:None
        self.disabledebugbuttons = lambda:None
        # breakpoints shelf
        self.saveandrestorebreakpoints = lambda:None
        # stackframe shelf
        self.clearframe = lambda:None
        self.selectframe = lambda x:None
        self.updatestacklist = lambda x:None
        # thread shelf
        self.clearthread = lambda:None
        self.updatethread = lambda x,y,z:None
        self.updatethreadlist = lambda x,y:None
        # variables shelf
        self.clearlocalvariables = lambda:None
        self.clearglobalvariables = lambda:None
        self.clearexceptions = lambda:None
        self.updatelocalvariables = lambda x,y:(None,None)
        self.updateglobalvariables = lambda x,y:(None,None)
        self.updateexceptions = lambda x,y:(None,None)
        self.catchunhandledexception = lambda:None
        self.updateanalyze = lambda:None
        # expressions shelf
        self.setexpression = lambda x,y:None
        self.restoreexpressions = lambda:None
        self.saveandrestoreexpressions = lambda:None
        self.clearexpressionvalues = lambda:None

    def clear_all(self):
        self.breakpoints_installed = False
        self.curstack = {}
        self.unhandledexception = False
        self.abortattach = False
        self.attached = False
        self.analyzing = False
        self.broken = False
        self.processcreator = None
        self.debuggerattachedtext = None
        self.debuggerdetachedtext = None
        self.clearstepmarker()
        self.clearframe()
        self.clearthread()
        self.clearlocalvariables()
        self.clearglobalvariables()
        self.clearexceptions()
        self.clearexpressionvalues()
        self.saveandrestoreexpressions()
        self.saveandrestorebreakpoints()
        self.updateanalyze()
        
    def isrpdbbreakpoint(self, filepath, lineno):
        if filepath.find("rpdb2.py") == -1:
            return False
        bpinfile = self.breakpoints.get(filepath)
        if not bpinfile:
            return True
        if not bpinfile.get(lineno):
            return True
        return False
    
    def attach(self, processcreator):
        if not processcreator:
            return
        self.processcreator = processcreator
        pid = str(processcreator.GetPID())
        tries = 0
        ex = None
        
        while tries != 5:
            sleep(1)
            util.Log("[PyDbg][info] Trying to Attach")
            ex = None
            try:
                if self.abortattach:
                    self.do_abort()
                    break
                self.sessionmanager.attach(pid, encoding = rpdb2.detect_locale())
                self.attached = True
                break
            except Exception, ex:
                tries = tries + 1
        ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_SHOW, (self.mainwindow.GetId(), False))
        if ex:
            self.do_abort()
            err = rpdb2.g_error_mapping.get(type(ex), repr(ex))
            err = "Failed to attach. Error: %s" % err
            util.Log("[PyDbg][err] %s" % err)
            wx.CallAfter(self.printerror, processcreator, err)
            PyStudioUtils.error_dialog(self.mainwindow, err)
            return
        util.Log("[PyDbg][info] Running")
        processcreator.AddText(self.debuggerattachedtext)

    def printerror(self, processcreator, err):
        processcreator.AddText(_("\n%s\n" % err))
    
    def attached_callsessionmanagerfn(self, fn, *args, **kwargs):
        if not self.attached:
            return None
        ex = None
        try:
            return fn(*args, **kwargs)
        except rpdb2.NotAttached, ex:
            self.attached = False
        except Exception, ex:
            util.Log("[PyDbg][err] %s" % traceback.format_exc())
        if self.mainwindow:
            err = rpdb2.g_error_mapping.get(type(ex), repr(ex))
            PyStudioUtils.error_dialog(self.mainwindow, err)
        return None
    
    def callsessionmanagerfn(self, fn, *args, **kwargs):
        ex = None
        try:
            return fn(*args, **kwargs)
        except Exception, ex:
            util.Log("[PyDbg][err] %s" % traceback.format_exc())
        if self.mainwindow:
            err = rpdb2.g_error_mapping.get(type(ex), repr(ex))
            PyStudioUtils.error_dialog(self.mainwindow, err)
        return None

    def do_abort(self):
        self.do_detach()
        self.abortattach = False
        if not self.processcreator:
            return
        self.attached = False
        self.analyzing = False
        self.broken = False
        self.debugbuttonsupdate()
        self.clearstepmarker()
        self.processcreator.Abort()
        
    def do_detach(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.detach)

    def get_host(self):
        return self.callsessionmanagerfn(self.sessionmanager.get_host)
    
    def set_default_host(self):
        self.callsessionmanagerfn(self.sessionmanager.set_host, RpdbDebugger.host)
        
    def calc_server_list(self, host):
        self.sessionmanager.set_host(host)
        return self.sessionmanager.calc_server_list()
    
    def get_server_list(self, host):
        return self.callsessionmanagerfn(self.calc_server_list, host)
        
    def get_password(self):
        return self.callsessionmanagerfn(self.sessionmanager.get_password)
        
    def set_password(self, pwd):
        self.callsessionmanagerfn(self.sessionmanager.set_password, pwd)
        
    def set_default_password(self):
        self.callsessionmanagerfn(self.sessionmanager.set_password, RpdbDebugger.password)
        
    def register_callback(self, func, event_type_dict, fSingleUse = False):
        self.sessionmanager.register_callback(func, event_type_dict, fSingleUse = fSingleUse)

    def install_breakpoints(self):
        self.breakpointmanager.installbreakpoints()
            
    def set_frameindex(self, index):
        self.attached_callsessionmanagerfn(self.sessionmanager.set_frame_index, index)
            
    def get_frameindex(self):
        return self.attached_callsessionmanagerfn(self.sessionmanager.get_frame_index)
    
    def update_stack(self):
        stacklist = self.attached_callsessionmanagerfn(self.sessionmanager.get_stack, [], True)
        if stacklist is not None:
            self.stackframemanager.do_update_stack(stacklist[0])

    def get_thread_list(self):
        res = self.attached_callsessionmanagerfn(self.sessionmanager.get_thread_list)
        if res is not None:
            return res
        return (None, {})
    
    def set_thread(self, tid):
        self.attached_callsessionmanagerfn(self.sessionmanager.set_thread, tid)
            
    def execute(self, suite):
        return self.attached_callsessionmanagerfn(self.sessionmanager.execute, suite)

    def evaluate(self, suite):
        return self.attached_callsessionmanagerfn(self.sessionmanager.evaluate, suite)

    def update_namespace(self):
        self.variablesmanager.update_namespace()

    def catchexc_get_namespace(self, expressionlist, filterlevel):
        if not self.attached:
            return None
        ex = None
        try:
            return self.sessionmanager.get_namespace(expressionlist, filterlevel)
        except rpdb2.NotAttached, ex:
            self.attached = False
        except (rpdb2.ThreadDone, rpdb2.NoThreads):
            self.clearlocalvariables()
            self.clearglobalvariables()
            self.clearexceptions()
            return
        except Exception, ex:
            util.Log("[PyDbg][err] %s" % traceback.format_exc())
        if self.mainwindow:
            err = rpdb2.g_error_mapping.get(type(ex), repr(ex))
            PyStudioUtils.error_dialog(self.mainwindow, err)
        return None
    
    def get_namespace(self, expressionlist, filterlevel):
        return self.attached_callsessionmanagerfn(self.sessionmanager.get_namespace, expressionlist, filterlevel)

    def set_synchronicity(self, synchronicity):
        self.callsessionmanagerfn(self.sessionmanager.set_synchronicity, synchronicity)
        
    def get_synchronicity(self):
        return self.callsessionmanagerfn(self.sessionmanager.get_synchronicity)
        
    def set_trap_unhandled_exceptions(self, trap):
        self.callsessionmanagerfn(self.sessionmanager.set_trap_unhandled_exceptions, trap)
        
    def get_trap_unhandled_exceptions(self):
        return self.callsessionmanagerfn(self.sessionmanager.get_trap_unhandled_exceptions)
        
    def set_fork_mode(self, forkmode, autofork):
        self.callsessionmanagerfn(self.sessionmanager.set_fork_mode, forkmode, autofork)
        
    def get_fork_mode(self):
        return self.callsessionmanagerfn(self.sessionmanager.get_fork_mode)
        
    def set_encoding(self, encoding, escaping):
        self.callsessionmanagerfn(self.sessionmanager.set_fork_mode, encoding, escaping)
        
    def get_encoding(self):
        return self.callsessionmanagerfn(self.sessionmanager.get_encoding)
        
    def set_analyze(self, analyze):
        self.attached_callsessionmanagerfn(self.sessionmanager.set_analyze, analyze)

    def do_shutdown(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.shutdown)
        self.clearstepmarker()
    
    def do_stop(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.stop_debuggee)
        self.clearstepmarker()

    def do_restart(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.restart)
        self.clearstepmarker()

    def do_jump(self, lineno):
        self.attached_callsessionmanagerfn(self.sessionmanager.request_jump, lineno)
        self.clearstepmarker()

    def do_go(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.request_go)
        self.clearstepmarker()

    def do_break(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.request_break)

    def do_step(self): # Step In
        self.attached_callsessionmanagerfn(self.sessionmanager.request_step)
        self.clearstepmarker()

    def do_next(self): # Step Over
        self.attached_callsessionmanagerfn(self.sessionmanager.request_next)
        self.clearstepmarker()

    def do_return(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.request_return)
        self.clearstepmarker()

    def run_toline(self, filename, lineno):
        self.attached_callsessionmanagerfn(self.sessionmanager.request_go_breakpoint, filename, '', lineno)
        self.clearstepmarker()

    def disable_breakpoint(self, bpid):
        self.attached_callsessionmanagerfn(self.sessionmanager.disable_breakpoint, [bpid], False)

    def enable_breakpoint(self, bpid):
        self.attached_callsessionmanagerfn(self.sessionmanager.enable_breakpoint, [bpid], False)

    def load_breakpoints(self):
        try:
            self.sessionmanager.load_breakpoints()
        except rpdb2.NotAttached:
            pass
        except IOError:
            pass
        except rpdb2.CException:
            pass
    
    def clear_breakpoints(self):
        self.attached_callsessionmanagerfn(self.sessionmanager.delete_breakpoint, [], True)
        
    def set_breakpoint(self, filepath, lineno, exprstr = "", enabled=True):
        return self.attached_callsessionmanagerfn(self.sessionmanager.set_breakpoint, filepath, '', lineno, enabled, exprstr)

    def get_breakpoints(self):
        return self.attached_callsessionmanagerfn(self.sessionmanager.get_breakpoints)

    def delete_breakpoint(self, filepath, lineno):
        bps = self.get_breakpoints()
        if not bps:
            return
        for bp in bps.values():            
            if bp.m_lineno == lineno and bp.m_filename == filepath:
                self.attached_callsessionmanagerfn(self.sessionmanager.delete_breakpoint, [bp.m_id], False)
