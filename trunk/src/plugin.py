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
#
# Some of the code in this document is directly derived from trac
#
# Copyright (C) 2003-2006 Edgewall Software
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#  3. The name of the author may not be used to endorse or promote
#     products derived from this software without specific prior
#     written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
#--------------------------------------------------------------------------#
# FILE: plugin.py
# AUTHOR: Cody Precord
# LANGUAGE: Python
# SUMMARY:
#    This module provides the core functionality of the plugin system for
# Editra. Its design is influenced by the system used in the web based
# project management software Trac (trac.edgewall.org). To create a plugin
# plugin class must derive from Plugin and in the class definintion it
# must state which Interface it Impliments. Interfaces are defined
# throughout various locations in the core Editra code. The interface
# defines the contract that the plugin needs to conform to. 
#
# Plugins consist of python egg files that can be created with the use of
# the setuptools package.
#
#   There are some issues I dont like with how this is currently working
# that I hope to find a work around for in later revisions. Namely I
# dont like the fact that the plugins are loaded and kept in memory
# even when they are not activated. Although the footprint of the non
# activated plugin class members being held in memory is not likely to
# be very large it seems like
#
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import wx
import ed_glob
import util
try:
   import pkg_resources
except ImportError, msg:
    try:
        from extern import pkg_resources
    except ImportError, msg:
        pkg_resources = None

#--------------------------------------------------------------------------#
# Globals
ENTRYPOINT = 'Editra.plugins'
PLUGIN_CONFIG = "plugin.cfg"
_implements = []

#--------------------------------------------------------------------------#

class Interface(object):
    """Base class for defining interfaces. Interface classes are
    used to define the method/contract from which the plugin must
    conform to.
    
    """
    pass

class ExtensionPoint(property):
    """Declares what interface a plugin is extending"""
    def __init__(self, interface):
        property.__init__(self, self.Extensions)
        self.interface = interface

    def __repr__(self):
        return '<ExtensionPoint %s>' % self.interface.__name__

    def Extensions(self, component):
        extensions = PluginMeta._registry.get(self.interface, [])
        return filter(None, [wx.GetApp()._pluginmgr[cls] for cls in extensions])

class PluginMeta(type):
    """Acts as the registration point for plugin entrypoint objects.
    It makes sure that only a single instance of any particular entry
    point is active at one time per plugin manager.

    """
    _plugins = list()
    _registry = dict()
    def __new__(cls, name, bases, d):
        d['_implements'] = _implements[:]
        del _implements[:]
        new_obj = type.__new__(cls, name, bases, d)
        if name == 'Plugin':
            return new_obj
        init = d.get("__init__")
        if not init:
            for init in [b.__init__._original for b in new_obj.mro()
                         if issubclass(b, Plugin) and '__init__' in b.__dict__]:
                break
        PluginMeta._plugins.append(new_obj)
        for interface in d.get('_implements', []):
            PluginMeta._registry.setdefault(interface, []).append(new_obj)
        for base in [base for base in bases if hasattr(base, '_implements')]:
            for interface in base._implements:
                PluginMeta._registry.setdefault(interface, []).append(new_obj)
        return new_obj

class Plugin(object):
    """Base class for all plugin type objects"""
    __metaclass__ = PluginMeta

    def __new__(cls, *args, **kwargs):
        """Only one instance of each plugin is allowed to exist
        per manager. If an instance of this plugin has already be
        initialized, that instance will be returned. If not this will
        initialize a new instance of the plugin.
        
        """
        if issubclass(cls, PluginManager):
            self = super(Plugin, cls).__new__(cls)
            self._pluginmgr = self
            return self

        pluginmgr = args[0]
        self = pluginmgr._plugins.get(cls)
        if self is None:
            self = super(Plugin, cls).__new__(cls)
            self.pluginmgr = pluginmgr
        return self

class PluginData(object):
    """A storage class for representing data about a plugin"""
    def __init__(self, name=u'', descript=u'', author=u'', ver=u''):
        """Create the plugin data object"""
        object.__init__(self)
        self._name = name
        self._description = descript
        self._author = author
        self._version = ver

    def GetName(self):
        """Returns the name of the plugin"""
        return self._name

    def GetDescription(self):
        """Returns the plugins description"""
        return self._description

    def GetAuthor(self):
        """Returns the author of the plugin"""
        return self._author

    def GetVersion(self):
        """Returns the version of the plugin"""
        return self._version

    def SetName(self, name):
        """Returns the name of the plugin"""
        if not isinstance(name, basestring):
            try:
                name = str(name)
            except:
                name = u''
        self._name = name

    def SetDescription(self, descript):
        """Returns the plugins description"""
        if not isinstance(descript, basestring):
            try:
                descript = str(descript)
            except:
                descript = u''
        self._description = descript

    def SetAuthor(self, author):
        """Returns the author of the plugin"""
        if not isinstance(author, basestring):
            try:
                author = str(author)
            except:
                author = u''
        self._author = author

    def SetVersion(self, ver):
        """Returns the version of the plugin"""
        if not isinstance(ver, basestring):
            try:
                ver = str(ver)
            except:
                ver = u''
        self._version = ver

def Implements(*interfaces):
    """Used by plugins to declare the interface that they
    implment/extend.

    """
    _implements.extend(interfaces)

#--------------------------------------------------------------------------#

# TODO complete functions for allowing dynamic loading and unloading of
#      of plugins. As well as allowing loaded but inactive plugins to be
#      initiated without needing to restart the editor. 
class PluginManager(object):
    """The PluginManger keeps track of the active plugins. It
    also provides an interface into loading and unloading plugins.

    """
    def __init__(self):
        """Initializes a PluginManager object"""
        object.__init__(self)
        self.LOG = wx.GetApp().GetLog()
        self._config = self.LoadPluginConfig() # Enabled/Disabled Plugins
        self._pi_path = list(set([ed_glob.CONFIG['PLUGIN_DIR'], 
                         ed_glob.CONFIG['SYS_PLUGIN_DIR']]))
        sys.path.extend(self._pi_path)
        if pkg_resources != None:
            self._env = pkg_resources.Environment(self._pi_path)
        else:
            self.LOG("[pluginmgr][warn] setup tools is not installed")
            self._env = dict()
        self._plugins = dict()      # Set of available plugins
        self._enabled = dict()      # Set of enabled plugins
        self.InitPlugins(self._env)
        self.RefreshConfig()
        # Enable/Disable plugins based on config data
        for pi in self._plugins:
            if self._config.get(self._plugins[pi].__module__):
                self._enabled[pi] = True
            else:
                self._config[self._plugins[pi].__module__] = False
                self._enabled[pi] = False

    def __contains__(self, cobj):
        """Returns True if a plugin is currently loaded and being
        managed by this manager.
        
        """
        return cobj in self._plugins

    def __getitem__(self, cls):
        """Gets and returns the instance of given class if it has
        already been activated.
        
        """
        nspace = cls.__module__ + "." + cls.__name__
        if nspace in ed_glob.DEFAULT_PLUGINS:
            self._enabled[cls] = True
        if cls not in self._enabled:
            self._enabled[cls] = False # If its a new plugin disable by default
        if not self._enabled[cls]:
            return None
        plugin = self._plugins.get(cls)
        if not plugin:
            if cls not in PluginMeta._plugins:
                self.LOG("[pluginmgr][err] %s Not Registered" % cls.__name__)
            try:
                plugin = cls(self)
            except TypeError, msg:
                self.LOG("[pluginmgr][err] Unable in initialize plugin")
        return plugin

    def CallPluginOnce(self, plugin):
        """Makes a call to a given plugin"""

    def DisablePlugin(self, plugin):
        """Disables a named plugin"""
        self._config[plugin] = False
        for cls in self._enabled:
            pmod = cls.__module__
            if pmod == plugin:
                self._enabled[cls] = False

    def EnablePlugin(self, plugin):
        """Enables a named plugin"""
        self._config[plugin] = True
        for cls in self._enabled:
            pmod = cls.__module__
            if pmod == plugin:
                self._enabled[cls] = True

    def GetAvailPlugins(self):
        """Returns a list of all available plugins. This list is
        made up of the plugins available in a users config directory
        as well as the plugins installed in the application data
        directory.

        """
        
    def GetConfig(self):
        """Returns a dictionary of plugins and there configuration
        state.

        """
        self.RefreshConfig()
        return self._config

    def InitPlugins(self, env):
        """Initializes the plugins that are contained in the given
        enviroment. After calling this the list of available plugins
        can be obtained by calling GetAvailPlugins
        
        """
        if pkg_resources == None:
            return
        pkg_env = env
        plugins = {}
        for name in pkg_env:
            egg = pkg_env[name][0]  # egg is of type Distrobution
            egg.activate()
            modules = []
            for name in egg.get_entry_map(ENTRYPOINT):
                try:
                    entry_point = egg.get_entry_info(ENTRYPOINT, name)
                    cls = entry_point.load() # Loaded entry points call Impliments
                except ImportError, e:
                    self.LOG("[pluginmgr][err] Failed to load plugin %s from %s" % \
                             (name, egg.location))
                else:
                    try:
                        self._plugins[cls] = cls(self)
                    finally:
                        pass

        # Activate all default plugins
        for d_pi in ed_glob.DEFAULT_PLUGINS:
            obj = d_pi.split(".")
            mod = ".".join(obj[:-1])
            entry = __import__(mod, globals(), globals(), ['__name__'])
            if hasattr(entry, obj[-1]):
                entry = getattr(entry, obj[-1])
                entry(self)

        return True

    def LoadPluginByName(self, name):
        """Loads a named plugin"""
        
    def LoadPluginConfig(self):
        """Loads the plugin config file for the current user if
        it exists. The configuration file contains which plugins
        are active and which ones are not.

        """
        config = dict()
        reader = util.GetFileReader(os.path.join(ed_glob.CONFIG['CONFIG_DIR'],
                                                 PLUGIN_CONFIG))
        if reader == -1:
            self.LOG("[plugin_mgr][exception] Failed to read plugin config file")
            return config

        reading = True
        while reading:
            data = reader.readline()
            if data == u"":
                reading = False
            data = data.strip()
            if len(data) and data[0] == u"#":
                continue
            data = data.split(u"=")
            if len(data) == 2:
                if data[1].lower() == u"true":
                    data[1] = True
                else:
                    data[1] = False
                config[data[0]] = data[1]
            else:
                continue
        reader.close()
        return config

    def RefreshConfig(self):
        """Refreshes the config data comparing the loadable
        plugins against the config data and removing any entries
        that dont exist in both from the configuration data.

        """
        plugins = list()
        for pi in self._plugins:
            plugins.append(pi.__module__)
        config = dict()
        for item in self._config:
            if item in plugins:
                config[item] = self._config[item]
        self._config = config

    def UnloadPluginByName(self, name):
        """Unloads a named plugin"""
        
    def WritePluginConfig(self):
        """Writes out the plugin config"""
        writer = util.GetFileWriter(os.path.join(ed_glob.CONFIG['CONFIG_DIR'],
                                                 PLUGIN_CONFIG))
        if writer == -1:
            self.LOG("[plugin_mgr][exception] Failed to write plugin config")
            return
        writer.write("# Editra %s Plugin Config\n#\n" % ed_glob.version)
        for item in self._config:
            writer.write("%s=%s\n" % (item, str(self._config[item])))
        writer.write("\n# EOF\n")
        writer.close()
        return
