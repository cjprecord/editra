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
# FILE: plugin.py
# AUTHOR: Cody Precord
# LANGUAGE: Python
# SUMMARY:
#
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
    """foo"""
    pass

class Plugin(object):
    """Base class for all plugin type objects"""
    def __new__(cls, *args, **kwargs):
        """Only one instance of each plugin is allowed to exist
        per manager. If an instance of this plugin has already be
        initialized, that instance will be returned. If not this will
        initialize a new instance of the plugin.
        
        """
        

def Implements(*interfaces):
    """Used by plugins to declare the interface that they
    implment/extend.

    """
    _implements.extend(interfaces)


#--------------------------------------------------------------------------#

class PluginManager(object):
    """The PluginManger keeps track of the active plugins. It
    also provides an interface into loading and unloading plugins.

    """
    def __init__(self):
        """Initializes a PluginManager object"""
        object.__init__(self)
        self.LOG = wx.GetApp().GetLog()
        self._config = self.LoadPluginConfig() # Enabled/Disabled Plugins
        self._pi_path = [ed_glob.CONFIG['PLUGIN_DIR'], 
                         ed_glob.CONFIG['SYS_PLUGIN_DIR']]
        sys.path.extend(self._pi_path)
        self._env = pkg_resources.Environment(self._pi_path)
        self.InitPlugins(self._env)

    def __contains__(self, cobj):
        """Returns True if"""
        

    def GetAvailPlugins(self):
        """Returns a list of all available plugins. This list is
        made up of the plugins available in a users config directory
        as well as the plugins installed in the application data
        directory.

        """
        

    def InitPlugins(self, env):
        """Initializes the plugins that are contained in the given
        enviroment.
        
        """
        pkg_env = env
        plugins = {}
        for name in pkg_env:
            egg = pkg_env[name][0]
            egg.activate()
            modules = []
            
            for name in egg.get_entry_map(ENTRYPOINT):
                try:
                    entry_point = egg.get_entry_info(ENTRYPOINT, name)
                    cls = entry_point.load()
                    if not hasattr(cls, 'capabilities'):
                        cls.capabilities = []
                    instance = cls()
                    for c in cls.capabilities:
                        plugins.setdefault(c, []).append(instance)
                except ImportError, e:
                    pass
        return plugins

    def LoadPluginByName(self, name):
        """Loads a named plugin"""
        
    def LoadPluginConfig(self):
        """Loads the plugin config file for the current user if
        it exists. The configuration file contains which plugins
        are active and which ones are not.

        """
        config = dict()
        reader = util.GetFileReader(os.path.join(ed_glob.CONFIG['CACHE_DIR'],
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

    def UnloadPluginByName(self, name):
        """Unloads a named plugin"""
        
    def WritePluginConfig(self):
        """Writes out the plugin config"""
        writer = util.GetFileWriter(os.path.join(ed_glob.CONFIG['CACHE_DIR'],
                                                 PLUGIN_CONFIG))
        if writer == -1:
            self.LOG("[plugin_mgr][exception] Failed to write plugin config")
            return
        writer.write("# Editra %s Plugin Config\n#\n" % ed_glob.version)
        for item in self._config:
            writer.write("%s=%s" % (item, str(self._config[item])))
        writer.write("# EOF\n")
        writer.close()
        return
