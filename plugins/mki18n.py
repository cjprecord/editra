#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# 
#   PYTHON MODULE:     MKI18N.PY
#                      =========
# 
#   Abstract: Make Internationalization (i18n) files for an application.
#   Copyright Pierre Rouleau. 2003. Released to public domain.
#   Last update: Saturday, November 8, 2003. @ 15:55:18.
#   File: ROUP2003N01::C:/dev/python/mki18n.py
# 
#   Update history:
#   - File updated: Thursday, January 22, 2008 by Cody Precord
#   - File created: Saturday, June 7, 2003. by Pierre Rouleau
#   - 01/22/08 CJP : Allow specifying where the po files can be output to and
#                    where to find them when compiling mo files.
#   - 07/12/07 CJP : Make it work with current wx code and clean up code
#   - 10/06/03 rcs : RCS Revision 1.1  2003/06/10 10:06:12  PRouleau
#   - 10/06/03 rcs : RCS Initial revision
#   - 23/08/03 rcs : RCS Revision 1.2  2003/06/10 10:54:27  PRouleau
#   - 23/08/03 P.R.: [code:fix] : The strings encoded in this file are encode 
#                                 in iso-8859-1 format.  Added the encoding
#                    notification to Python to comply with Python's 2.3 PEP 263.
#   - 23/08/03 P.R.: [feature:new] : Added the '-e' switch which is used to 
#                                    force the creation of the empty English 
#                                    .mo file.
#   - 22/10/03 P.R.: [code] : incorporated utility functions in here 
#                             to make script self sufficient.
#   - 05/11/03 rcs : RCS Revision 1.4  2003/10/22 06:39:31  PRouleau
#   - 05/11/03 P.R.: [code:fix] : included the unixpath() in this file.
#   - 08/11/03 rcs : RCS Revision 1.5  2003/11/05 19:40:04  PRouleau
# 
#   RCS $Log: $
# 
# 
# -----------------------------------------------------------------------------
"""                                
mki18n allows you to internationalize your software.  You can use it to 
create the GNU .po files (Portable Object) and the compiled .mo files
(Machine Object).

mki18n module can be used from the command line or from within a script (see 
the Usage at the end of this page).

    Table of Contents
    -----------------
    makePO()  -- Build the Portable Object file for the application --
    catPO()   -- Concatenate one or several PO files with the application 
                 domain files.
    makeMO()   -- Compile the Portable Object files into the Machine Object 
                  stored in the right location.
    printUsage   -- Displays how to use this script from the command line --
    Scriptexecution      -- Runs when invoked from the command line --

NOTE:  this module uses GNU gettext utilities.

You can get the gettext tools from the following sites:

   - `GNU FTP site for gettetx`_ where several versions 
     (0.10.40, 0.11.2, 0.11.5 and 0.12.1) are available.
     Note  that you need to use `GNU libiconv`_ to use this. Get it from the 
     `GNU
     libiconv  ftp site`_ and get version 1.9.1 or later. Get the Windows .ZIP
     files and install the packages inside c:/gnu. All binaries will be stored
     inside  c:/gnu/bin.  Just  put c:/gnu/bin inside your PATH. You will need
     the following files: 

      - `gettext-runtime-0.12.1.bin.woe32.zip`_ 
      - `gettext-tools-0.12.1.bin.woe32.zip`_
      - `libiconv-1.9.1.bin.woe32.zip`_ 


.. _GNU libiconv:   http://www.gnu.org/software/libiconv/
.. _GNU libiconv ftp site:  http://www.ibiblio.org/pub/gnu/libiconv/
.. _gettext-runtime-0.12.1.bin.woe32.zip:
        ftp://ftp.gnu.org/gnu/gettext/gettext-runtime-0.12.1.bin.woe32.zip 
.. _gettext-tools-0.12.1.bin.woe32.zip: 
..      ftp://ftp.gnu.org/gnu/gettext/gettext-tools-0.12.1.bin.woe32.zip 
.. _libiconv-1.9.1.bin.woe32.zip: 
        http://www.ibiblio.org/pub/gnu/libiconv/libiconv-1.9.1.bin.woe32.zip

"""
# -----------------------------------------------------------------------------
# Module Import
# -------------
# 
import os
import sys
import wx
# -----------------------------------------------------------------------------
# Global variables
# ----------------
#

__author__ = "Pierre Rouleau"
__version__ = "$Revision: 543 $"

# -----------------------------------------------------------------------------

def getlanguageDict():
    """Get a dictionary of the available languages from wx"""
    lang_dict = {}
    app = wx.App()
    for lang in [x for x in dir(wx) if x.startswith("LANGUAGE")]:
        i = wx.Locale(wx.LANGUAGE_DEFAULT).GetLanguageInfo(getattr(wx, lang))
        if i:
            lang_dict[i.CanonicalName] = i.Description
    return lang_dict

# -----------------------------------------------------------------------------
# m a k e P O ( )  -- Build the Portable Object file for the application --
# ^^^^^^^^^^^^^^^
#
def makePO(app_dir,  app_domain=None, verbose=0, src='app.fil', out='messages', podir=''):
    """Build the Portable Object Template file for the application.

    makePO builds the .pot file for the application stored inside 
    a specified directory by running xgettext for all application source 
    files. It finds the name of all files by looking for a file called 
    'app.fil'. 
    If this file does not exists, makePo raises an IOError exception.
    By default the application domain (the application
    name) is the same as the directory name but it can be overridden by the
    'applicationDomain' argument.

    makePO always creates a new file called messages.pot.  If it finds files 
    of the form app_xx.po where 'app' is the application name and 'xx' is one 
    of the ISO 639 two-letter language codes, makePO resynchronizes those 
    files with the latest extracted strings (now contained in messages.pot). 
    This process updates all line location number in the language-specific
    .po files and may also create new entries for translation (or comment out 
    some).  The .po file is not changed, instead a new file is created with 
    the .new extension appended to the name of the .po file.

    By default the function does not display what it is doing.  Set the 
    verbose argument to 1 to force it to print its commands.

    """
    if app_domain is None:
        app_name = fileBaseOf(app_dir, withPath=0)
    else:
        app_name = app_domain

    curr_dir = os.getcwd()
    os.chdir(app_dir)
    if not os.path.exists(src):
        raise IOError(2,'No module file: %s' % src)

    # Steps:                                  
    #  Use xgettext to parse all application modules
    #  The following switches are used:
    #  
    #   -s : sort output by string content 
    #        (easier to use when we need to merge several .po files)
    #   --files-from=app.fil : The list of files is taken from the file: app.fil
    #   --output= : specifies the name of the output file 
    #               (using a .pot extension)
    cmd = "xgettext -s --no-wrap --from-code=utf-8 --files-from=%s --output=%s.pot" % (src, out)
    if verbose: 
        print cmd
    os.system(cmd)                                                
    lang_dict = getlanguageDict()
    for lang_code in lang_dict.keys():
        if lang_code == 'en':
            pass
        else:
            lang_po_filename = "%s/%s_%s.po" % (podir, app_name, lang_code)
            if os.path.exists(lang_po_filename):
                cmd = 'msgmerge -s --no-wrap "%s" messages.pot > "%s.new"' % \
                      (lang_po_filename, lang_po_filename)
                if verbose: 
                    print cmd
                os.system(cmd)
    os.chdir(curr_dir)

# -----------------------------------------------------------------------------
# c a t P O ( ) 
# -- Concatenate one or several PO files with the application domain files. --
# ^^^^^^^^^^^^^
#
def catPO(app_dir, listOf_extraPo, app_domain=None, \
          target_dir=None, verbose=0) :
    """Concatenate one or several PO files with the application domain files.
    """

    if app_domain is None:
        app_name = fileBaseOf(app_dir, withPath=0)
    else:
        app_name = app_domain
    curr_dir = os.getcwd()
    os.chdir(app_dir)

    lang_dict = getlanguageDict()

    for lang_code in lang_dict.keys():
        if lang_code == 'en':
            pass
        else:
            lang_po_fname = "%s_%s.po" % (app_name, lang_code)
            if os.path.exists(lang_po_fname):
                fileList = ''
                for fname in listOf_extraPo:
                    fileList += ("%s_%s.po " % (fname, lang_code))
                cmd = "msgcat -s --no-wrap %s %s > %s.cat" % (lang_po_fname, \
                                                              fileList, \
                                                              lang_po_fname)
                if verbose: 
                    print cmd
                os.system(cmd)
                if target_dir is None:
                    pass
                else:
                    mo_targetDir = "%s/%s/LC_MESSAGES" % (target_dir, lang_code)
                    cmd = "msgfmt --output-file=%s/%s.mo %s_%s.po.cat" % \
                           (mo_targetDir, app_name, app_name, lang_code)
                    if verbose: 
                        print cmd
                    os.system(cmd)
    os.chdir(curr_dir)

# -----------------------------------------------------------------------------
# m a k e M O ( ) Compile the POfiles into the MO stored in the right location.
# ^^^^^^^^^^^^^^^
# 
def makeMO(applicationDirectoryPath, targetDir='./locale', 
           applicationDomain=None, verbose=0, forceEnglish=0, podir='') :
    """Compile the Portable Object files into the Machine Object stored in the 
    right location.

    makeMO converts all translated language-specific PO files located inside 
    the  application directory into the binary .MO files stored inside the 
    LC_MESSAGES sub-directory for the found locale files.

    makeMO searches for all files that have a name of the form 'app_xx.po' 
    inside the application directory specified by the first argument.  The 
    'app' is the application domain name (that can be specified by the 
    applicationDomain argument or is taken from the directory name). The 'xx' 
    corresponds to one of the ISO 639 two-letter language codes.

    makeMo stores the resulting files inside a sub-directory of `targetDir`
    called xx/LC_MESSAGES where 'xx' corresponds to the 2-letter language
    code.
    """
    if targetDir is None:
        targetDir = './locale'
    if verbose:
        print "Target directory for .mo files is: %s" % targetDir

    if applicationDomain is None:
        applicationName = fileBaseOf(applicationDirectoryPath, withPath=0)
    else:
        applicationName = applicationDomain
    currentDir = os.getcwd()
    os.chdir(applicationDirectoryPath)

    languageDict = getlanguageDict()

    for langCode in languageDict.keys():
        if (langCode == 'en') and (forceEnglish==0):
            pass
        else:
            langPOfileName = "%s/%s_%s.po" % (podir, applicationName, langCode)
            if os.path.exists(langPOfileName):
                mo_targetDir = "%s/%s/LC_MESSAGES" % (targetDir, langCode) 
                if not os.path.exists(mo_targetDir):
                    mkdir(mo_targetDir)
                cmd = 'msgfmt --output-file="%s/%s.mo" "%s/%s_%s.po"' % \
                      (mo_targetDir, applicationName, podir, applicationName, langCode)
                if verbose: 
                    print cmd
                os.system(cmd)
    os.chdir(currentDir)
   
# -----------------------------------------------------------------------------

def printUsage(errorMsg=None):
    """Displays how to use this script from the command line."""
    print """
    ###########################################################################
    #   mki18n : Make internationalization files.                             #
    #            Uses the GNU gettext system to create PO (Portable Object)   #
    #            files from source code, compile PO into MO (Machine Object)  #
    #            files.                                                       #
    #            Supports C, C++, and Python source files.                    #
    #                                                                         #
    #   Usage: mki18n {OPTION} [appDirPath]                                   #
    #                                                                         #
    #   Options:                                                              #
    #     -h               : prints this help                                 #
    #     -m               : make MO from existing PO files                   #
    #     -p               : make PO, update PO files: Creates a new          #
    #                        messages.pot file. Creates a dom_xx.po.new for   #
    #                        every existing language specific .po file.       #
    #                        ('xx' stands for the ISO639 two-letter language  #
    #                        code and 'dom' stands for the application domain #
    #                        name).                                           #
    #     --domain=appName : Specify a specific folder to generate for the    #
    #                        default is to check and generate for all folders #
    #                        found in the same directory as this one.         #
    #                                                                         #
    #   You must specify one of the -p or -m option to perform the work. You  #
    #   can specify the path of the target application.  If you leave it out  #
    #   mki18n will use the current directory as the application main         #
    #   directory.                                                            #
    ###########################################################################
    """
    if errorMsg:
        print "\n   ERROR: %s" % errorMsg

# -----------------------------------------------------------------------------
# f i l e B a s e O f ( )         -- Return base name of filename --
# ^^^^^^^^^^^^^^^^^^^^^^^
# 
def fileBaseOf(filename, withPath=0) :
    """fileBaseOf(filename,withPath) ---> string

    Return base name of filename. The returned string never includes the 
    extension.
    Use os.path.basename() to return the basename with the extension.  The 
    second argument is optional.  If specified and if set to 'true' (non zero)
    the string returned contains the full path of the file name.  Otherwise the
    path is excluded.

    """            
    pos = filename.rfind('.')             
    if pos > 0:
        filename = filename[:pos]
    if withPath:
        return filename
    else:
        return os.path.basename(filename)

# -----------------------------------------------------------------------------
# m k d i r ( )   -- Create a directory (and possibly the entire tree) --
# ^^^^^^^^^^^^^
# 
def mkdir(directory) :
    """Create a directory (and possibly the entire tree).

    The os.mkdir() will fail to create a directory if one of the
    directory in the specified path does not exist.  mkdir()
    solves this problem.  It creates every intermediate directory
    required to create the final path. Under Unix, the function 
    only supports forward slash separator, but under Windows and MacOS
    the function supports the forward slash and the OS separator (backslash
    under windows).
    """ 
    # translate the path separators
    directory = unixpath(directory)

    # build a list of all directory elements
    elem_list = filter(lambda x: len(x) > 0, directory.split('/'))
    the_len = len(elem_list)

    # if the first element is a Windows-style disk drive
    # concatenate it with the first directory
    if elem_list[0].endswith(':'):
        if the_len > 1:
            elem_list[1] = elem_list[0] + '/' + elem_list[1]
            del elem_list[0]      
            the_len -= 1     

    # if the original directory starts at root,
    # make sure the first element of the list 
    # starts at root too
    if directory[0] == '/':     
        elem_list[0] = '/' + elem_list[0]

    # Now iterate through the list, check if the 
    # directory exists and if not create it
    the_dir = ''
    for i in range(the_len):
        the_dir += elem_list[i]
        if not os.path.exists(the_dir):
            os.mkdir(the_dir)
        the_dir += '/'   
      
# -----------------------------------------------------------------------------
# u n i x p a t h ( ) -- Return a path name that contains Unix separator. --
# ^^^^^^^^^^^^^^^^^^^
# 
def unixpath(path) :
    r"""Return a path name that contains Unix separator.

    [Example]
    >>> unixpath(r"d:\test")
    'd:/test'
    >>> unixpath("d:/test/file.txt")
    'd:/test/file.txt'
    >>> 
    """
    path = os.path.normpath(path)
    if os.sep == '/':
        return path
    else:
        return path.replace(os.sep, '/')

# ----------------------------------------------------------------------------- 
# S c r i p t   e x e c u t i o n  -- Runs when invoked from the command line --
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# 
if __name__ == "__main__":
    import getopt     # command line parsing
    argc = len(sys.argv)
    if argc == 1:
        printUsage('Missing argument: specify at least one of -m or -p '
                   '(or both).')
        sys.exit(1)
    # If there is some arguments, parse the command line
    valid_opts = "ehmpv"
    valid_lopts = ['domain=', 'moTarget=', 'podir=']             
    option = {}
    option['forceEnglish'] = 0
    option['mo'] = 0
    option['po'] = 0        
    option['verbose'] = 0
    option['domain'] = None
    option['moTarget'] = None
    try:
        optionList, pargs = getopt.getopt(sys.argv[1:], valid_opts, valid_lopts)
    except getopt.GetoptError, e:
        printUsage(e[0])
        sys.exit(1)       
    for (opt, val) in optionList:
        if  (opt == '-h'):    
            printUsage()
            sys.exit(0) 
        elif (opt == '-e'):
            option['forceEnglish'] = 1
        elif (opt == '-m'):
            option['mo'] = 1
        elif (opt == '-p'):
            option['po'] = 1
        elif (opt == '-v'):
            option['verbose'] = 1
        elif (opt == '--domain'):
            option['domain'] = val
        elif (opt == '--moTarget'):
            option['moTarget'] = val
        elif (opt == '--podir'):
            option['podir'] = val

    if len(pargs) == 0:
        app_dir_path = os.getcwd()
        if option['verbose']:
            print "No project directory given. Using current one:  %s" % \
                                                                    app_dir_path
    elif len(pargs) == 1:
        app_dir_path = pargs[0]
    else:
        printUsage(('Too many arguments (%u). Use double quotes if you have '
                   'space in directory name') % len(pargs))
        sys.exit(1)

    if option['domain'] is None:
        # If no domain specified, use the name of the target directory
        option['domain'] = fileBaseOf(app_dir_path)

    if option['verbose']:
        print "Application domain used is: '%s'" % option['domain']

    if option['po']:
        try:
            makePO(app_dir_path, option['domain'], option['verbose'], podir=option['podir'])
        except IOError, e:
            printUsage(e[1] + ('\n   You must write a file app.fil that '
                              'containsthe list of all files to parse.'))
    if option['mo']:
        makeMO(app_dir_path, option['moTarget'], option['domain'], 
               option['verbose'], option['forceEnglish'], podir=option['podir'])
    sys.exit(1)              
            
# -----------------------------------------------------------------------------
