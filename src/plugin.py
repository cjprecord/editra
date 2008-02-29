###############################################################################
# Name: plugin.py                                                             #
# Purpose: Plugin system architecture                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
#
# Some of the code in this document was derived from trac's plugin architecture
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
# @author: Cody Precord
# LANGUAGE: Python
# @summary:
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
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Dependancies
import os
import sys
import wx
import ed_glob
import util
try:
    import pkg_resources
except ImportError:
    try:
        from extern import pkg_resources
    except ImportError:
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

#-----------------------------------------------------------------------------#

class ExtensionPoint(property):
    """Declares what L{Interface} a plugin is extending"""
    def __init__(self, interface):
        """Initializes the extension point
        @param interface: interface object that the extension point extends

        """
        property.__init__(self, self.Extensions)
        self.interface = interface

    def __repr__(self):
        """@return: string representation of the object"""
        return '<ExtensionPoint %s>' % self.interface.__name__

    def Extensions(self, component):
        """@return: a list of plugins that declare to impliment the
        given extension point.

        """
        component = wx.GetApp().GetPluginManager()
        extensions = PluginMeta._registry.get(self.interface, [])
        return filter(None, [component[cls] for cls in extensions])

#-----------------------------------------------------------------------------#

class PluginMeta(type):
    """Acts as the registration point for plugin entrypoint objects.
    It makes sure that only a single instance of any particular entry
    point is active at one time per plugin manager.

    """
    _plugins = list()
    _registry = dict()
    def __new__(mcs, name, bases, d):
        """@return a new metaclass object"""
        d['_implements'] = _implements[:]
        del _implements[:]
        new_obj = type.__new__(mcs, name, bases, d)
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

#-----------------------------------------------------------------------------#

class Plugin(object):
    """Base class for all plugin type objects"""
    __metaclass__ = PluginMeta

    def __new__(cls, *args, **kwargs):
        """Only one instance of each plugin is allowed to exist
        per manager. If an instance of this plugin has already be
        initialized, that instance will be returned. If not this will
        initialize a new instance of the plugin.
        @return: a new class object or an existing instance if one
                 exists.

        """
        if issubclass(cls, PluginManager):
            self = super(Plugin, cls).__new__(cls)
            self._pluginmgr = self
            return self

        pluginmgr = args[0]
        self = pluginmgr.GetPlugins().get(cls)
        if self is None:
            self = super(Plugin, cls).__new__(cls)
            self.pluginmgr = pluginmgr
        return self

#-----------------------------------------------------------------------------#

class PluginData(object):
    """A storage class for representing data about a Plugin
    @see: L{Plugin}

    """
    def __init__(self, name=u'', descript=u'', author=u'', ver=u''):
        """Create the plugin data object
        @param name: Name of the plugin
        @param descript: Short description of plugin
        @param author: Who made the plugin
        @param ver: Version of the plugin
        @type ver: string
        """
        object.__init__(self)
        self._name = name
        self._description = descript
        self._author = author
        self._version = ver

    def GetName(self):
        """@returns: Plugin's name string"""
        return self._name

    def GetDescription(self):
        """@returns: Plugins description string"""
        return self._description

    def GetAuthor(self):
        """@returns: Author of the plugin"""
        return self._author

    def GetVersion(self):
        """@returns: Plugin's version string"""
        return self._version

    def SetName(self, name):
        """Sets the plugins name string
        @param name: String to name plugin with
        @postcondition: Plugins name string is set

        """
        if not isinstance(name, basestring):
            try:
                name = str(name)
            except (ValueError, TypeError):
                name = u''
        self._name = name

    def SetDescription(self, descript):
        """@returns: Plugins description string"""
        if not isinstance(descript, basestring):
            try:
                descript = str(descript)
            except (ValueError, TypeError):
                descript = u''
        self._description = descript

    def SetAuthor(self, author):
        """Sets the author attribute
        @param author: New Authors name string
        @postcondition: Author attribute is set to new value

        """
        if not isinstance(author, basestring):
            try:
                author = str(author)
            except (ValueError, TypeError):
                author = u''
        self._author = author

    def SetVersion(self, ver):
        """Sets the version attribute of the plugin.
        @param ver: Version string
        @postcondition: Plugins version attribute is set to new value

        """
        if not isinstance(ver, basestring):
            try:
                ver = str(ver)
            except (ValueError, TypeError):
                ver = u''
        self._version = ver

#-----------------------------------------------------------------------------#

def Implements(*interfaces):
    """Used by L{Plugin}s to declare the interface that they
    implment/extend.
    @param interfaces: list of interfaces the plugin implements

    """
    _implements.extend(interfaces)

#--------------------------------------------------------------------------#

class PluginManager(object):
    """The PluginManger keeps track of the active plugins. It
    also provides an interface into loading and unloading plugins.
    @status: Allows for dynamic loading of plugins but they can not
             be called/used until the editor has been restarted.
    @todo: complete functions for allowing dynamic loading and unloading of
           of plugins. As well as allowing loaded but inactive plugins to be
           initiated without needing to restart the editor.

    """
    def __init__(self):
        """Initializes a PluginManager object.
        @postcondition: Plugin manager and plugins are initialized

        """
        object.__init__(self)
        self.LOG = wx.GetApp().GetLog()
        self._config = self.LoadPluginConfig() # Enabled/Disabled Plugins
        self._pi_path = list(set([ed_glob.CONFIG['PLUGIN_DIR'], 
                             ed_glob.CONFIG['SYS_PLUGIN_DIR']]))
        sys.path.extend(self._pi_path)
        self._env = self.CreateEnvironment(self._pi_path)
        self._plugins = dict()      # Set of available plugins
        self._enabled = dict()      # Set of enabled plugins
        self.InitPlugins(self._env)
        self.RefreshConfig()
        # Enable/Disable plugins based on config data
        self.UpdateConfig()

    def __contains__(self, cobj):
        """Returns True if a plugin is currently loaded and being
        managed by this manager.
        @param cobj: object to look for in loaded plugins

        """
        return cobj in self._plugins

    def __getitem__(self, cls):
        """Gets and returns the instance of given class if it has
        already been activated.
        @param cls: class object to get from metaregistery
        @return: returns either None or the intialiazed class object

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
            except (AttributeError, TypeError), msg:
                self.LOG("[pluginmgr][err] Unable in initialize plugin")
                self.LOG("[pluginmgr][err] %s" % str(msg))
        return plugin

    def CallPluginOnce(self, plugin):
        """Makes a call to a given plugin
        @status: currently not implemented

        """
        pass

    def CreateEnvironment(self, path):
        """Creates the environment based on the passed
        in path list
        @param path: path(s) to scan for extension points
        @type path: list of path strings

        """
        if pkg_resources != None:
            env = pkg_resources.Environment(path)
        else:
            self.LOG("[pluginmgr][warn] setup tools is not installed")
            env = dict()
        return env

    def DisablePlugin(self, plugin):
        """Disables a named plugin.
        @precondition: plugin must be managed by this manager instance
        @postcondition: plugin is disabled and will not be activated on 
                        next reload.

        """
        self._config[plugin] = False
        for cls in self._enabled:
            pmod = cls.__module__
            if pmod == plugin:
                self._enabled[cls] = False

    def EnablePlugin(self, plugin):
        """Enables a named plugin.
        @precondition: plugin must be managed by this manager instance
        @postcondtion: plugin is added to activate list for activation on
                       next program start.

        """
        self._config[plugin] = True
        for cls in self._enabled:
            pmod = cls.__module__
            if pmod == plugin:
                self._enabled[cls] = True
        
    def GetConfig(self):
        """Returns a dictionary of plugins and there configuration
        state.
        @return: the mapped set of available plugins
        @rtype: dict

        """
        self.RefreshConfig()
        return self._config

    def GetEnvironment(self):
        """Returns the evironment that the plugin manager was 
        initiated in.
        @return: the managers environment

        """
        return self._env

    def GetPlugins(self):
        """Returns a the dictionary of plugins managed by this manager
        @return: all plugins managed by this manger
        @rtype: dict
        """
        return self._plugins

    def InitPlugins(self, env):
        """Initializes the plugins that are contained in the given
        enviroment. After calling this the list of available plugins
        can be obtained by calling GetAvailPlugins.
        @note: plugins must emit the L{ENTRY_POINT} defined in this file
        @postcondition: all plugins in the environment are initialized

        """
        if pkg_resources == None:
            return
        pkg_env = env
        for name in pkg_env:
            egg = pkg_env[name][0]  # egg is of type Distrobution
            egg.activate()
            for name in egg.get_entry_map(ENTRYPOINT):
                try:
                    entry_point = egg.get_entry_info(ENTRYPOINT, name)
                    cls = entry_point.load()
                except Exception, msg:
                    self.LOG("[pluginmgr][err] Couldn't Load %s: %s" % \
                                                          (str(name), str(msg)))
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
        """Loads a named plugin.
        @status: currently not implemented

        """
        
    def LoadPluginConfig(self):
        """Loads the plugin config file for the current user if
        it exists. The configuration file contains which plugins
        are active and which ones are not.
        @return: configuration dictionary

        """
        config = dict()
        reader = util.GetFileReader(os.path.join(ed_glob.CONFIG['CONFIG_DIR'],
                                                 PLUGIN_CONFIG))
        if reader == -1:
            self.LOG("[plugin_mgr][err] Failed to read plugin config file")
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
        @postcondition: entries that could not be loaded or do not
                        exist any longer are removed from the config

        """
        plugins = list()
        for plugin in self._plugins:
            plugins.append(plugin.__module__)
        config = dict()
        for item in self._config:
            if item in plugins:
                config[item] = self._config[item]
        self._config = config

    def RefreshEnvironment(self):
        """Refreshes the current environment to include any
        plugins that may have been added since init.
        @postcondition: environment is refreshed

        """
        self._env = self.CreateEnvironment(self._pi_path)

    def ReInit(self):
        """Reinitializes the plugin environment and all plugins
        in the environment as well as the configuration data.
        @postcondition: the manager is reinitialized to reflect
                        any configuration or environment changes
                        that may have occured.

        """
        self.RefreshEnvironment()
        self.InitPlugins(self.GetEnvironment())
        self.RefreshConfig()
        self.UpdateConfig()

    def UnloadPluginByName(self, name):
        """Unloads a named plugin.
        @status: currently not implemented

        """
        
    def UpdateConfig(self):
        """Updates the in memory config data to recognize
        any plugins that may have been added or initialzed
        by a call to InitPlugins.
        @postcondition: plugins are enabled or disabled based
                        on the configuration data.

        """
        for plugin in self._plugins:
            if self._config.get(self._plugins[plugin].__module__):
                self._enabled[plugin] = True
            else:
                self._config[self._plugins[plugin].__module__] = False
                self._enabled[plugin] = False

    def WritePluginConfig(self):
        """Writes out the plugin config.
        @postcondition: the configuration data is saved to disk

        """
        writer = util.GetFileWriter(os.path.join(ed_glob.CONFIG['CONFIG_DIR'],
                                                 PLUGIN_CONFIG))
        if writer == -1:
            self.LOG("[plugin_mgr][exception] Failed to write plugin config")
            return
        writer.write("# Editra %s Plugin Config\n#\n" % ed_glob.VERSION)
        for item in self._config:
            writer.write("%s=%s\n" % (item, str(self._config[item])))
        writer.write("\n# EOF\n")
        writer.close()
        return
