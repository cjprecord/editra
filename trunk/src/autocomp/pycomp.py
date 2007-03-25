############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
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

"""
#--------------------------------------------------------------------------#
# FILE: pycomp.py                                                          #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    Provides completion and calltip support for python documents          #
#                                                                          #
# METHODS:
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import sys
import imp
from wx.py import introspect

#--------------------------------------------------------------------------#
# XXX This approach is fairly fast, but suffers from a number of other
#     draw backs. May need to look into writing a parser or even better
#     a static lexer. But brain is tired so think about it and come back.
#
# TODO this file was hacked together in a rather fast manner need to do
#      a code cleanup in the near future.
#
# BUGS: While trying to balance performance and uselfullness its left me
#       with a bit to think about. Currently if any imports in the source
#       buffer fail the autocomplete will fail as well.
#
#       Also if an import launches an application (i.e wx.App.MainLoop) the
#       application will open. Then when it comes time to close Editra it will
#       cause it to lock and crash due to missing references.
#
#       Autocompletion pops up when inside of comment blocks. This probably
#       should be the case.

# XXX currently supports autocompletion only for imported libraries and their
#     decendants. The code is in place but currently dissabled to allow for
#     the autcompletion of local objects, due to some troublesome bugs that
#     come up in certain cases.
class Completer:
    """Code completer provider"""
    def __init__(self, stc_buffer):
        """Initiliazes the completer"""
        self._buffer = stc_buffer
        self._autocomp_keys = [ord('.')]
        self._autocomp_stop = ' .,;:([)]}\'"\\<>%^&+-=*/|`'
        self._calltip_keys = [ord('(')]
        self._case_sensitive = False
        self._collector = list() #dict()    # Collects important atoms from the document
        self._namespaces = dict()   # Collection of namespace dictionaries
        self._locals = dict()
        self._modules = sys.modules.keys()
        self._syspath = sys.path[:]
        self._syspath.insert(0, self._buffer.dirname) # Adjust working path to documents path
        while True:
            try:
                self._syspath.remove('')
            except ValueError:
                break
        while True:
            try:
                self._syspath.remove('.')
            except ValueError:
                break

        # Need to set these two values in sys for introspect
        # to function properly.
        sys.ps1 = '>>> '
        sys.ps2 = '... '

    def CollectNamespace(self):
        """Analyzes the buffer and collects available namespace
        data into the collector.
        Note: Only collects import statements

        """
        self._collector = list()        # Clear the collector TEMP
        for line in range(0, self._buffer.GetLineCount()):
            text = self._buffer.GetLine(line)
            if text not in self._collector and 'import ' in text:
                self._collector.append(text)
        tmp = list()
        for item in self._collector:
            pieces = item.split()
            if pieces[0] not in "import from":
                tmp.append(item)
        for item in tmp:
            self._collector.remove(item)
        return
                    
    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.

        """
        if hasattr(self, "_autocomp_keys"):
            return self._autocomp_keys
        else:
            return list()

    def GetAutoCompList(self, command, namespace=None):
        """Returns the list of possible completions for a 
        command string. If namespace is not specified the lookup
        is based on the locals namespace

        """
        if not len(self._locals) and namespace == None:
            self.UpdateNamespace(True)
        namespace = self._locals
        lst = introspect.getAutoCompleteList(command, namespace)
        return lst

    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.

        """
        if hasattr(self, '_autocomp_stop'):
            return self._autocomp_stop
        else:
            return u''

    def GetCallTip(self, command, namespace=None):
        """Returns the formated calltip string for the command.
        If the namespace command is unset the locals namespace is used.

        """
        if not len(self._locals) and namespace == None:
            self.UpdateNamespace(True)
        namespace = self._locals
        calltip = introspect.getCallTip(command, namespace)
        return calltip[2]

    def GetCallTipKeys(self):
        """Returns the list of keys to activate a calltip on"""
        if hasattr(self, '_calltip_keys'):
            return self._calltip_keys
        else:
            return list()

    def GetCaseSensitive(self):
        """Returns whether the autocomp commands are case sensitive
        or not.

        """
        if hasattr(self, '_case_sensitive'):
            return self._case_sensitive
        else:
            return False

    def SetCaseSensitive(self, value):
        """Sets whether the completer should be case sensitive
        or not, and returns True if the value was set.

        """
        if isinstance(value, bool):
            self._case_sensitve = value
            return True
        else:
            return False

    def UpdateNamespace(self, imports_only=False):
        """Updates the namespace to search for autocompletion lists
        and calltips in.

        """
        if imports_only:
            self.CollectNamespace()
            tmp = list()
            for item in self._collector:
                tmp.append(item.strip())
            text = "\n".join(tmp)
        else:
            if not hasattr(self._buffer, 'GetText'):
                return False
            text = self._buffer.GetText()
        if self._buffer.dirname not in self._syspath:
            self._syspath.insert(0, self.buffer._dirname)
        syspath = sys.path
        sys.path = self._syspath
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        name = self._buffer.dirname or self._buffer.filename
        module = imp.new_module(name)
        newspace = module.__dict__.copy()
        try:
            try:
                code = compile(text, name, 'exec')
            except:
                #raise
                return False
            try:
                exec code in newspace
            except:
                #raise
                return False
            else:
                # No problems, so update the namespace.
                self._locals.clear()
                self._locals.update(newspace)
                return True
        finally:
            del module # Free some memory
            sys.path = syspath
            for m in sys.modules.keys():
                if m not in self._modules:
                    del sys.modules[m]
#-----------------------------------------------------------------------------#