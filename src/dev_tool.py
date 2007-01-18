############################################################################
#    Copyright (C) 2007 by Cody Precord                                    #
#    staff@editra.org                                                      #
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

""" Development Tools """
__revision__ = "$Id: Exp $"

import os
import time
from ed_glob import PROFILE

#Tools to use during development

def DEBUGP(statement, mode="std", log_lvl="none"):
    """Used to print Debug Statements
    Modes of operation:
       std = stdout
       log = writes to log file
    
    Log Levels:
       none = used with stdout
       INFO = Basic Information
       WARN = Could be a potential problem
       ERROR = Serious problem has occured
       
    """
    # Turn off normal debugging messages when not in Debug mod
    if mode == "std" and PROFILE['MODE'] != 'DEBUG':
        return 0

    # Build time string for tstamp
    now = time.localtime(time.time())
    now = "[" + str(now[3]) + ":" + str(now[4]) + ":" + str(now[5]) + "]"

    # Format Statement
    s_lst = statement.split("\n")
    
    if mode == "std":
        for line in s_lst:
            print now + " " + line
        return 0
    elif mode == "log":
        logfile = os.environ.get('EDITRA_LOG')
        if logfile == None:
            print "EDITRA_LOG enviroment variable not set!!!"
            print "Outputting log information to default log \'editra_tmp.log\'"
            logfile = 'editra_tmp.log'
        file_handle = open(logfile, mode="a")
        if log_lvl != none:
            file_handle.write(log_lvl + ": " + statement + "\n")
        else:
            file_handle.write("MSG: " +  statement + "\n")
        file_handle.close()
        return 0	
    else:
        print "Improper DEBUG MODE: Defaulting to stdout"
        print statement
        return 1


