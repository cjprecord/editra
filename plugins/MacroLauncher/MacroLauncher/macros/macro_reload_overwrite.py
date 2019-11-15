# -*- coding: utf-8 -*-

__name__ = 'reload#'
__type__ = 'plugin'
__desc__ = 'reloads all plugins that have the doreload() method'

import wx
import os
import sys

def run(txtctrl, log = None, **kwargs):
  editra_dir = os.path.sep.join(os.path.dirname(__file__).split(os.path.sep)[0:-3])
  if (editra_dir) not in sys.path:
    sys.path.append(editra_dir)

  plgmgr = wx.GetApp().GetPluginManager()
  for plugin in plgmgr.GetPlugins():
      plugin = plgmgr.__getitem__(plugin)

      if plugin:
          if hasattr(plugin, 'doreload'):
              log('Reloading plugin: %s' % str(plugin))
              #plugin.doreload()
              wx.CallAfter(plugin.doreload)
              #wx.CallLater(1000, plugin.doreload)

