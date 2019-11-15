###############################################################################
# Name: __ini__.py                                                            #
# Purpose: Launcher Plugin allows you to run your python scripts              #
# Author: rca <roman.chyla@gmail.com>                                         #
# Copyright: (c) 2008 rca <roman.chyla@gmail.com>                             #
# License: wxWindows License                                                  #
###############################################################################

# Plugin Meta
"""Create and control running of python scripts from inside Editra"""
__author__ = "rca"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import wx
import wx.aui

# Editra Libraries
import ed_glob
import iface
import plugin
from profiler import Profile_Get, Profile_Set
import ed_event
import os 
import shutil
import zipfile
import codecs


# Local imports
import mbrowser


#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface implementation
class MacroLauncher(plugin.Plugin):
    """Adds a Launcher to the view menu"""
    plugin.Implements(iface.MainWindowI, iface.ShelfI)

    @property
    def __name__(self):
        return mbrowser.PANE_NAME

    def AllowMultiple(self):
        """Shelf interface"""
        return False

    def CreateItem(self, parent):
        """Shelf Interface"""
        return mbrowser.MacroLauncherPane(parent)

    def GetId(self):
        """Shelf Interface"""
        return mbrowser.ID_ML_SHELF

    def GetMenuEntry(self, menu):
        """Shelf Interface"""
        return wx.MenuItem(menu, mbrowser.ID_ML_SHELF, _("MacroLauncher"))

    def GetName(self):
        """Shelf Interface"""
        return _("MacroLauncher")

    def IsStockable(self):
        """Shelf Interface"""
        return True

    ### MainWindowI Implemention ###
    def PlugIt(self, parent):
        """ Adds the view menu entry and registers the event handler"""
        self._mainwin = parent
        self._log = wx.GetApp().GetLog()
        if self._mainwin != None:
            self._log("[macrolauncher] Installing macrolauncher plugin")

            #---- Add Menu Items ----#
            viewm = self._mainwin.GetMenuBar().GetMenuByName('view')
            self._menuitem = viewm.InsertAlpha(mbrowser.ID_MACROLAUNCHER,
                                   _('Macro Launcher'),
                                   _('Open Macro Launcher Sidepanel'),
                                   wx.ITEM_CHECK,
                                   after=ed_glob.ID_PRE_MARK)

            #---- Make the Panel ----#
            self._mbrowser = mbrowser.MacroLauncherPane(self._mainwin, 
                                                         mbrowser.ID_MLAUNCHERPANE,
                                                         menu=self._menuitem)
            mgr = self._mainwin.GetFrameManager()
            mgr.AddPane(self._mbrowser, 
                        wx.aui.AuiPaneInfo().Name(mbrowser.PANE_NAME).\
                        Caption(_("Macro Launcher")).Right().Layer(1).\
                        CloseButton(True).MaximizeButton(True).\
                        BestSize(wx.Size(200, 200)))

            # Get settings from profile
            if Profile_Get(mbrowser.ML_KEY, 'bool', False):
                mgr.GetPane(mbrowser.PANE_NAME).Show()
            else:
                mgr.GetPane(mbrowser.PANE_NAME).Hide()

            self.install_macros(self._mbrowser)
            mgr.Update()
            
    def GetMenuHandlers(self):
        """Pass event handler for menu item to main window for management"""
        return [(mbrowser.ID_MACROLAUNCHER, self._mbrowser.OnShow)]

    def GetUIHandlers(self):
        """Pass Ui handlers to main window for management"""
        return [(mbrowser.ID_MACROLAUNCHER, self._mbrowser.OnUpdateMenu)]
    
    def install_macros(self, macro_launcher):
        """Checks and installs macros, that are supplied together with mlauncher
        It will not overwrite the existing macros, unless the macro has in name
        "_overwrite." """
        macropath = macro_launcher.macropath
        curr_dir = os.path.sep.join(os.path.dirname(__file__).split(os.path.sep))
        
        # get all the macros
        installed_macros = {}
        try:
            macro_files = os.listdir(macropath)
            for file in macro_files:
                if (file.endswith('.py') or file.endswith('.pyw')):
                    full_path = os.path.normpath(os.path.join(macropath, file))
                    installed_macros[file] = full_path
        except Exception, msg:
            #print msg
            pass

        available_macros = {}
        source_zip = None
        try:
            if '.egg' in curr_dir:
                egg_file = os.path.sep.join(curr_dir.split(os.path.sep)[0:-1])
                source_zip = zipfile.ZipFile(egg_file, 'r')
                for file in source_zip.namelist():
                    if '/macro_' in file and (file.endswith('.py') or file.endswith('.pyw')):
                        filename = file.split('/')[-1]
                        available_macros[filename] = file
            else:
                for d in (curr_dir, os.path.join(curr_dir, 'macros')):
                    macro_files = os.listdir(d)
                    for file in macro_files:
                        if file[:6] == 'macro_' and (file.endswith('.py') or file.endswith('.pyw')):
                            full_path = os.path.normpath(os.path.join(d, file))
                            available_macros[file] = full_path
        except Exception, msg:
            #print msg
            pass
        
        
        installed = 0
        for name, fullpath in available_macros.items():
            if '_overwrite.' in name or name not in installed_macros:
                try:
                    if source_zip: #we deal with egg file
                        fname = os.path.join(macropath, name)
                        fo = codecs.open(fname, 'w', 'utf-8')
                        cont = source_zip.read(fullpath)
                        fo.write(cont)
                        fo.flush()
                        fo.close()
                    else:
                        shutil.copyfile(fullpath, os.path.join(macropath, name))
                    installed += 1
                except Exception, msg:
                    #print msg
                    pass
        
        if installed:
            macro_launcher.UpdateMacroBrowser(show_everything = True)
        if source_zip:
            source_zip.close()
        
    def doreload(self):
        """Development function - reloads the plugins from GUI"""
        reload(mbrowser)
        if hasattr(mbrowser, 'reload'):
            mbrowser.doreload()
        self._mbrowser = mbrowser.MacroLauncherPane(self._mainwin, 
                                                    mbrowser.ID_MLAUNCHERPANE,
                                                    menu=self._menuitem)
        mgr = self._mainwin.GetFrameManager()
        pane = mgr.GetPane(mbrowser.PANE_NAME)
        pane.DestroyOnClose(True)
        mgr.DetachPane(pane.window)
        pane.window.Destroy()
    
        mgr.AddPane(self._mbrowser, 
                    wx.aui.AuiPaneInfo().Name(mbrowser.PANE_NAME).\
                    Caption(_("Macro Launcher")).Right().Layer(1).\
                    CloseButton(True).MaximizeButton(True).\
                    BestSize(wx.Size(200, 200)))

        # Get settings from profile
        if Profile_Get(mbrowser.ML_KEY, 'bool', False):
            mgr.GetPane(mbrowser.PANE_NAME).Show()
        else:
            mgr.GetPane(mbrowser.PANE_NAME).Hide()
        
        #self.install_macros(self._mbrowser)
        mgr.Update()
