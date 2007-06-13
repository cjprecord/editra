############################################################################
#    Copyright (C) 2007 by Cody Precord                                    #
#    cprecord@editra.org                                                   #
#                                                                          #
#    Editra is free software; you can redistribute it and#or modify        #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    Editra is distributed in the hope that it will be useful,             #
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
import codecs
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
    # Turn off normal debugging messages when not in Debug mode
    if mode == "std" and not 'DEBUG' in PROFILE['MODE']:
        return 0

    # Build time string for tstamp
    now = time.localtime(time.time())
    now = u"[%s:%s:%s]" % (str(now[3]).zfill(2), str(now[4]).zfill(2), 
                           str(now[5]).zfill(2))

    # Format Statement
    statement = unicode(statement)
    s_lst = statement.split(u"\n")
    
    if mode == "std":
        for line in s_lst:
            out = u"%s %s" % (now, line)
            print out.encode('utf-8', 'replace')
        return 0
    elif mode == "log":
        logfile = os.environ.get('EDITRA_LOG')
        if logfile == None or not os.path.exists(logfile):
            print u"EDITRA_LOG enviroment variable not set!!!"
            print u"Outputting log information to default log \'editra_tmp.log\'"
            logfile = 'editra_tmp.log'
        file_handle = file(logfile, mode="ab")
        writer = codecs.lookup('utf-8')[3](file_handle)
        if log_lvl != "none":
            writer.write(u"%s: %s\n" % (log_lvl, statement))
        else:
            writer.write(u"MSG: %s\n" % statement)
        file_handle.close()
        return 0	
    else:
        print u"Improper DEBUG MODE: Defaulting to stdout"
        print statement
        return 1


