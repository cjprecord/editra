############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
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
# FILE: profiler.py                                                        #
# LANGUAGE: Python	                                                        #
#                                                                          #
# SUMMARY:                                                                 #
# This collection of functions handle user profiles for the editor.        #
# It provides support for customization of settings and preferences to be  #
# saved in between sessions.                                               #
#                                                                          #
# SPECIFICATIONS:                                                          #
# The format of the profile file is                                        #
#                                                                          #
# LABLE [<TAB(S)> or <SPACE(S)>] VALUE                                     #
#                                                                          #
# Comment lines are denoted by a '#' mark.                                 #
#                                                                          #
# Only one value can be set per line all other statements                  #
# after the first one will be ignored.                                     #
#                                                                          #
# EOF marks the end of file, no configuration data will be read past       #
# this keyword.                                                            #
#                                                                          #
#   LABLES		VALUES                                         #
# ----------------------------------------                                 #
#  MODE			CODE, DEBUG                                    #
#  THEME	                   DEFAULT                                        #
#  ICONS                    STOCK, ...                                     #
#  LANG			ENGLISH, JAPANESE                              #
#  WRAP                     On, Off	                                     #
#  SYNTAX                   On, Off	                                     #
#  GUIDES                   On, Off                                        #
#  KWHELPER                 On, Off	                                      #
#  TOOLBAR                  On, Off                                        #
#  LASTFILE                 path/to/file                                   #
#                                                                          #
# METHODS:                                                                 #
# ReadProfile: Reads a profile into the profile dictionary                 #
# WriteProfile: Writes a profile dictionary to a file	                   #
# LoadProfile: Checks loader for last used profile	                   #
# UpdateProfileLoader: Updates loader after changes to profile	          #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id:  Exp $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
from ed_glob import CONFIG
from ed_glob import PROFILE
from ed_glob import prog_name
import util
import dev_tool

_ = wx.GetTranslation
#--------------------------------------------------------------------------#

#---- Begin Function Definitions ----#
def GetLoader():
    """Finds the loader to use"""

    user_home = wx.GetHomeDir() + util.GetPathChar()
    rel_prof_path = ("." + prog_name + util.GetPathChar() + 
                     "profiles" + util.GetPathChar() + ".loader")

    if os.path.exists(user_home + rel_prof_path):
        LOADER = user_home + rel_prof_path
    else:
        LOADER = CONFIG['PROFILE_DIR'] + ".loader"

    return LOADER

def LoadProfile():
    """Loads Last Used Profile"""

    LOADER = GetLoader()

    try:
        file_handle = open(LOADER, mode="r")
    except IOError:
        dev_tool.DEBUGP("[profiler] [exception] Failed to open profile loader")
        # So try the default
        ReadProfile(CONFIG['PROFILE_DIR'] + "default.pp")
        dev_tool.DEBUGP("[prof_info] Loaded Default Profile")
        return 1

    profile = file_handle.readline()
    profile = profile.split("\n")[0] # strip newline from end

    file_handle.close()

    if profile == "":
        profile = "default.pp"

    if os.path.isabs(profile):
        retval = ReadProfile(profile)
    else:
        retval = ReadProfile(CONFIG['PROFILE_DIR'] + profile)
    return retval

def ReadProfile(profile):
    """Reads profile settings from a file into the
    profile dictionary.

    """

    try:
        file_handle = open(profile, mode="r")
    except IOError:
        dev_tool.DEBUGP("[profiler] [exception] Loading Profile: " + profile +
                        "\n[prof_warn] Loaded Default Profile Settings")
        PROFILE['MYPROFILE'] = "default.pp"
        return 1

    lable = ""
    val = ""
    values = []
    invalid_line = 0

    # Parse File
    while 1:
        line = file_handle.readline()

        if line != "" and line[0] != "#":
            values = line.split()

            # Populate Profile Dictionary
            #TODO should do value validation and default to ed_glob on invalid
            #     values, to prevent errors from improperly editted profiles.
            if len(values) >= 2:
                lable = values[0]
                val = " ".join(values[1:])
                # If val is a bool convert it from string
                if val in [u"True", u"On"]:
                    val = True
                elif val in [u"False", u"Off"]:
                    val = False
                else:
                    pass

                if lable == 'WSIZE' or lable == 'WPOS':
                    val = util.StrToTuple(val)

                PROFILE[lable] = val
        else:
            invalid_line += 1
      
        # Check end of file condition
        if len(values) > 0 and values[0] == "EOF":
            break
        elif invalid_line > 100:  # Bail after 100 lines
            break
        else:
            pass

    # Save this profile as my profile
    PROFILE['MYPROFILE'] = profile
    file_handle.close()
    dev_tool.DEBUGP("[prof_info] Loaded Profile: " + profile)
    return 0

def UpdateProfileLoader():
    """Updates Loader File"""

    LOADER = GetLoader()

    try:
        file_handle = open(LOADER, mode="w")
    except IOError:
        dev_tool.DEBUGP("[profiler] [exception] Failed to open profile loader for writting")
        return 1

    file_handle.write(PROFILE['MYPROFILE'])
    file_handle.close()
    return 0

def WriteProfile(profile):
    """Writes a profile to a file"""
    file_handle = open(profile, mode="w")
    header = "# " + profile + "\n# Editra Profile\n" \
              + "\n# Lable\t\t\tValue #" + \
              "\n#-----------------------------#\n"

    file_handle.write(header)
    file_handle.close()

    file_handle = open(profile, mode="a")
    prof_keys = PROFILE.keys()
    prof_keys.sort()

    if not PROFILE['SET_WSIZE']:
        if 'WSIZE' in prof_keys:
            prof_keys.remove('WSIZE')
    if not PROFILE['SET_WPOS']:
        if 'WPOS' in prof_keys:
            prof_keys.remove('WPOS')

    for item in prof_keys:
        file_handle.write(str(item) + "\t\t" + str(PROFILE[item]) + "\n")

    file_handle.write("\n\nEOF\n")
    dev_tool.DEBUGP("[prof_info] Wrote out Profile: " + profile)

    PROFILE['MYPROFILE'] = profile
    return 0

def AddFileHistoryToProfile(file_history):
    """Manages work of adding a file from the profile in order
    to allow the top files from the history to be available 
    the next time the user opens the program.

    """
    size = file_history.GetNoHistoryFiles()
    file_key = "FILE"
    i = 0

    while size > i:
        key = file_key + str(i)
        file_path = file_history.GetHistoryFile(i)
        PROFILE[key] = file_path
        i += 1
    return i
