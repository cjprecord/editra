#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#Name: lbrowser.py                                                           #
#Purpose: UI portion of the MacroBrowser Plugin                            #
#Author: rca <roman.chyla@gmail.com>                                  #
#Copyright: (c) 2008 rca                                                   #
#License: wxWindows License                                                  #
###############################################################################

"""
Provides a macro browser panel and other UI components for Editra's
MacroBrowser Plugin.

The list and panel side of this moduel was inspired by commentbrowser plugin
by DR0ID <dr0iddr0id@googlemail.com>, mainly the CustomListCtrl and stup for the plugin
(do I need to add, that I have taken its code, or is it obvious? ;-))

Cody Precord, Editra master, fixed or helped me to fix quite some parts of the module

"""

__author__ = 'rca <roman.chyla@gmail.com>'
__svnid__ = '$Id: mbrowser.py 1501 2011-11-07 15:53:54Z roman.chyla@gmail.com $'
__revision__ = '$Revision: 1501 $'

#-----------------------------------------------------------------------------#
# Imports
import os.path
import re
import wx
import imp
import stat
import time
import random
import traceback
import wx.lib.mixins.listctrl as listmix
import locale
import codecs

# Editra Library Modules
import syntax
import ed_msg
import profiler
import eclib.ctrlbox as ctrlbox
import util
import ed_glob
import eclib
import eclib.outbuff as outbuff
import ed_basestc
import ed_basewin
import ebmlib


#--------------------------------------------------------------------------#
#Globals

_ = wx.GetTranslation

# Identifiers
PANE_NAME = 'MacroLauncher'
ML_KEY = 'MacroLauncher.Show'
ID_MLAUNCHERPANE = wx.NewId()
ID_MACROLAUNCHER = wx.NewId()  #menu item
ID_ML_SHELF = wx.NewId() # Shelf interface id
ID_TIMER = wx.NewId()

# RightClick actions/buttons
ID_RUN = wx.NewId()
ID_STOP = wx.NewId()
ID_NEW = wx.NewId()
ID_EDIT = wx.NewId()
ID_DELETE = wx.NewId()
ID_RELOAD = wx.NewId()
ID_VIEW = wx.NewId()
ID_RENAME = wx.NewId()

# Event for notifying that a macro task was interrupted (error)
edEVT_TASK_ERROR = wx.NewEventType()
EVT_TASK_ERROR = wx.PyEventBinder(edEVT_TASK_ERROR, 1)

#-----------------------------------------------------------------------------#

def SetMenuBitmap(item, id_):
    bmp = wx.ArtProvider.GetBitmap(str(id_), wx.ART_MENU)
    if not bmp.IsNull():
        item.SetBitmap(bmp)

def doreload():
    """Used for development, reloads modules"""
    pass

#-----------------------------------------------------------------------------#

class MacroLauncherPane(ed_basewin.EdBaseCtrlBox):
    """Creates a Macro Launcher panel"""
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, menu=None):
        """ Initializes the MacroLauncherPane class"""
        super(MacroLauncherPane, self).__init__(parent, id, pos, size, style)


        #---- main configuration ----#
        if not util.HasConfigDir('macros'):
            util.MakeConfigDir('macros')
        self.macropath = os.path.abspath(os.path.join(ed_glob.CONFIG['CONFIG_DIR'], 'macros'))
        self._macros = {}

        #---- private attr ----#
        self._mainwin = ed_basewin.FindMainWindow(self)
        self._mi = menu
        self.__log = wx.GetApp().GetLog()
        self._timer = wx.Timer(self, ID_TIMER)
        self._intervall = 500  # milli seconds
        self._filterChoices = ['']
        self._threadsIdx = {}
        self._threads = {}
        self._running = 0
        self._completed = 0
        self._cancelled = 0

        #---- Gui ----#

        ctrlbar = self.CreateControlBar(wx.TOP)
        self._listctrl = CustomListCtrl(self)
        self.SetWindow(self._listctrl)

        # ----- Elements layout -----#
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tools_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.GridSizer(3, 6, 1, 1)  # rows, cols, vgap, hgap

        ctrlbar.AddControl(main_sizer, wx.ALIGN_LEFT)
        main_sizer.Add(tools_sizer)
        main_sizer.Add(button_sizer)


        # ---- Filter toolbox ----#
        self._taskFilter = wx.Choice(ctrlbar, choices=self._filterChoices, style = wx.EXPAND | wx.ADJUST_MINSIZE)
        self._taskFilter.SetStringSelection(self._filterChoices[0])
        self._taskFilter.SetToolTipString(_("Filter macros by their type"))
        self._taskRelaxedCheckBox = wx.CheckBox(ctrlbar, -1)
        self._taskRelaxedCheckBox.SetToolTipString(_("Relaxed filtering - will list also partial matches"))

        if wx.Platform == '__WXMAC__':
            self._taskFilter.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
            self._taskRelaxedCheckBox.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        tools_sizer.Add(self._taskFilter, 1, wx.EXPAND|wx.ADJUST_MINSIZE|wx.ALL, 3)


        #------ Buttons ------#

        btn_update = eclib.PlateButton(ctrlbar,
                                       bmp=wx.ArtProvider.GetBitmap(str(wx.ID_REFRESH), wx.ART_MENU),
                                       style=eclib.PB_STYLE_NOBG)
        btn_update.SetToolTipString(_("Refresh list, reload macros if necessary"))

        btn_edit = eclib.PlateButton(ctrlbar,
                                     bmp=wx.ArtProvider.GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU),
                                     style=eclib.PB_STYLE_NOBG)
        btn_edit.SetToolTipString(_("Edit macro"))

        btn_new = eclib.PlateButton(ctrlbar,
                                    bmp=wx.ArtProvider.GetBitmap(str(ed_glob.ID_NEW), wx.ART_MENU),
                                    style=eclib.PB_STYLE_NOBG)
        btn_new.SetToolTipString(_("New macro"))

        btn_run = eclib.PlateButton(ctrlbar,
                                    bmp=wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU),
                                    style=eclib.PB_STYLE_NOBG)
        btn_run.SetToolTipString(_("Run macro"))

        btn_del = eclib.PlateButton(ctrlbar,
                                    bmp=wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU),
                                    style=eclib.PB_STYLE_NOBG)
        btn_del.SetToolTipString(_("Delete macro"))

        button_sizer.Add(self._taskRelaxedCheckBox, 1, wx.TOP, 5)
        a = (1, wx.TOP, 2)
        for btn in (btn_update, btn_run, btn_new, btn_edit, btn_del):
            button_sizer.Add(btn, *a)

        #---- Status Bar -----#

        statusctrl = self.CreateControlBar(wx.BOTTOM)
        self._statusMsgBox = wx.StaticText(statusctrl, label='')
        self._statusMsgBox.SetToolTipString(_("R: running, F: finished, C: cancelled or failed"))
        statusctrl.AddControl(self._statusMsgBox)
        self.SetStatusMsg(_('MLauncher Initialized'))
        wx.CallLater(1000, self.SetStatusMsg, '')
        statusctrl.Layout()

        #---- Bind events ----#

        self.Bind(wx.EVT_TIMER, lambda evt: self.UpdateMacroBrowser(), self._timer)
        self.Bind(wx.EVT_CHOICE, lambda evt: self.UpdateMacroBrowser(), self._taskFilter)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.UpdateMacroBrowser(show_everything = True), btn_update)
        self.Bind(wx.EVT_CHECKBOX, lambda evt: self.UpdateMacroBrowser(), self._taskRelaxedCheckBox)

        self.Bind(wx.EVT_BUTTON, lambda evt: self.OnNewMacro(), btn_new)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.OnEditMacro(), btn_edit)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.OnDelMacro(), btn_del)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.OnRunMacro(), btn_run)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy, self)

        #threads (started macros)
        self.Bind(outbuff.EVT_TASK_START, self._OnTaskStart)
        self.Bind(EVT_TASK_ERROR, self._OnTaskError)
        self.Bind(outbuff.EVT_TASK_COMPLETE, self._OnTaskComplete)

        # File action messages
        ed_msg.Subscribe(self.OnFileSave, ed_msg.EDMSG_FILE_SAVED)

        self.UpdateMacroBrowser()

    def OnDestroy(self, evt):
        if self:
            ed_msg.Unsubscribe(self.OnFileSave)

    #-------------------------- Methods -------------------------#

    def template(self):
        template = r'''# -*- coding: utf-8 -*-

__name__ = u'%(__name__)s'
__type__ = u'%(__type__)s'
__desc__ = u'%(__desc__)s'

"""
Example:
def run(txtctrl=None, log=None, **kwargs):
    rows = split(txtctrl.GetText())
    txtctrl.SetText("\n".join(rows)) #this will be inserted into the txtctrl

If you want to start macro in a separate thread, put it inside
run_thread() - but be careful not to call some operations from the
thread. Use wx.CallAfter() for that purpose

def run_thread(txtctrl, **kwargs):
    rows ....

Current arguments are:
  txtctrl: wx.stc current editor-
  nbook: notebook instance
  win: the main window
  log: log method for writing into the Editra log
  mlauncher: macro launcher instance (plugin)
"""

def run(txtctrl=None, log=None, **kwargs):
    pass
'''
        return template

    def GetMacroModTime(self, fullpath):
        """ Return mtime of the macro file """
        if hasattr(util, 'GetFileModTime'):
            return util.GetFileModTime(fullpath)
        else:
            return ebmlib.GetFileModTime(fullpath)

    def GetMacroContents(self, macro_name):
        """Returns the contents of the macro file, loading it directly
        from the file system but the macro must be already registered

        """
        contents = u''
        if macro_name in self._macros:
            fullpath = self._macros[macro_name]['fullpath']
            try:
                fileobj = codecs.open(fullpath, 'r', 'utf-8')
                contents = fileobj.read()
                fileobj.close()
            except:
                try:
                    fileobj = open(fullpath, 'r')
                    contents = fileobj.read()
                    fileobj.close()
                except:
                    pass
        return contents

    def GetMacroByID(self, fname):
        """Returns macro item searching by macro id
        this can return at max 1 item (or None)
        @param fname: the filename (the base) fo the macro

        """
        if fname in self._macros:
            try:
                return self._macros[fname]['module']
            except:
                pass

    def GetMacrosByName(self, name):
        """Returns list of tuples of (name, macro) from the registry.
        Name is coming from the macros themselves, so this method can return
        1>n items or []
        If nothing is found, returns empty tuple ('', '')

        """
        ret = list()
        for key, macro in self._macros.items():
            try:
                module = macro['module']
                if module.__name__ == name:
                    ret.append( (key, module) )
            except:
                pass
        return ret

    def GetMacrosByType(self, type, relaxed_matching = False):
        """Returns list of tuples of (name, macro) from the registry.
        Name is coming from the macros themselves, so this method can return
        1>n items or []

        """
        ret = list()
        if relaxed_matching:
            match_function = lambda t1, t2: t1.lower() in t2.lower()
        else:
            match_function = lambda t1, t2: t1 == t2

        for key, macro in self._macros.items():
            try:
                module = macro['module']
                if match_function(type, module.__type__):
                    ret.append( (key, module) )
            except:
                pass
        return ret

    def GetMacroByFullPath(self, fullpath):
        """Returns tuple (name, macro) searching by macro's fullpath
        this can return at max 1 item (or None)
        @param fname: the filename (the base) fo the macro

        """
        fullpath = os.path.normpath(fullpath)
        for key, macro in self._macros.items():
            if macro['fullpath'] == fullpath:
                try:
                    return (key, macro['module'])
                    break
                except:
                    pass

    def LoadMacro(self, fname, name):
        """ Initializes module into a separate object (not included in sys) """
        x = imp.new_module(name)
        x.__file__ = fname
        x.__id__ = name
        x.__builtins__ = __builtins__

        old_cwd = os.getcwd()
        try:
            try:
                #execfile(fname, x.__dict__) #problems if filepath contains accents
                filedir, filename = os.path.split(fname)
                os.chdir(filedir)
                execfile(filename, x.__dict__)

                for a in ['__name__', '__desc__', '__type__']:
                    if not hasattr(x, a):
                        setattr(x, a, '')
                x.__successful_load__ = True
            except Exception, excp:
                self._log('[error] ' + str(excp.message))
                self._log(traceback.format_exc())
                x.__desc__ = str(excp.message)
                x.__type__ = 'error'
                x.__successful_load__ = False
        finally:
            os.chdir(old_cwd)

        return x

    def UpdateMacroBrowser(self, show_everything = False):
        """ Updates the entries of the current page in the macro list.
        @param show_everything: if True, will display all the macros,
                                otherwise will honour the filter

        """
        # stop the timer if it is running
        if self._timer.IsRunning():
            self._timer.Stop()

        # get the filter value
        filter_value = ''
        if not show_everything:
            filter_value = self._taskFilter.GetStringSelection()

        # get all the macros
        try:
            macro_files = os.listdir(self.macropath)
        except:
            return

        for file in macro_files:
            if (file.endswith('.py') or file.endswith('.pyw')):
                name, ext = file.rsplit('.', 1)
                full_path = os.path.normpath(os.path.join(self.macropath, file))

                try:
                    mtime = self.GetMacroModTime(full_path)
                except Exception, excp:
                    self._log('[error] ' + str(excp.message))
                    continue

                if file in self._macros and self._macros[file]['mtime'] == mtime:
                    #the file hasn't changed
                    continue

                self._register_macro(full_path, mtime)

        # remove the deleted files
        present_macros = dict.fromkeys(macro_files, 1)
        for k in self._macros.keys():
            if not k in present_macros:
                del self._macros[k]

        self.UpdateList(filter = filter_value)

    def _register_macro(self, fullpath, mtime = None):
        """Loads and registers macro
        @param fullpath: path to the file .py(w) to be loaded
        @param mtime: if present, will be set as the modified time for this macro
                      if not present, mtime will be get for the file
        @return: True on successful load

        """

        file = os.path.split(fullpath)[-1]
        name, ext = file.rsplit('.', 1)

        if mtime == None:
            mtime = self.GetMacroModTime(fullpath)

        module = self.LoadMacro(fullpath, name)
        self._macros[file] = {'mtime': mtime,
                              'module': module,
                              'fullpath':fullpath}
        return bool(module.__successful_load__)

    def ReloadMacroIfChanged(self, macro_name=u''):
        """Checks if the macro is registered, is modified
        if yes, then reloads it
        @param macro_name: name of the macro (its base filename)

        """
        if macro_name in self._macros:
            mtime = self.IsModifiedMacro(self._macros[macro_name]['fullpath'])
            if mtime:
                self._register_macro(self._macros[macro_name]['fullpath'], mtime)

    def ForceMacroReload(self, macro_name=u''):
        """Reloads macro without checking for mtime, called from context menu
        usually from user-driven action

        """
        if macro_name in self._macros:
            self._register_macro(self._macros[macro_name]['fullpath'])

    def UpdateMacroBrowserByOne(self, fullpath, show_everything=False):
        """Updates the macro list adding one entry, but only if the macro
        is already registered and the mtime has changed
        @param fullpath: path to the file (possible macro)
        @param show_everything: if true, will force show of all the macros

        """
        filter_value = None
        if not show_everything:
            filter_value = self._taskFilter.GetStringSelection()

        mtime = self.IsModifiedMacro(fullpath)
        if mtime:
            self._register_macro(fullpath, mtime)
            self.UpdateList(filter = filter_value)

    def IsModifiedMacro(self, fullpath):
        """Checks whether the fullpath points to the existing registered macro
        and if it has been modified since last load
        @return: last modified value if the file is modified and is macro

        """
        name = os.path.split(fullpath)[-1]
        mtime = self.GetMacroModTime(fullpath)
        if name in self._macros and self._macros[name]['mtime'] != mtime:
            return mtime

    def GetMacroData(self):
        """ Constructs the structure to register macros in the CtrlList """
        macrodata = {}
        for key, value in self._macros.items():
            m = value['module']
            macro = []
            macrodata[key] = macro
            for k in ['__name__', '__type__', '__desc__']:
                if hasattr(m, k):
                    macro.append(getattr(m, k))
                else:
                    macro.append('')
            macro.append(os.path.split(m.__file__)[-1])
        return macrodata

    def RefreshFilterChoices(self, choices):
        """Replaces the filter with new values, and selects the old previously
        selected value. Makes sure that the "select all" ie an empty string
        is there too
        @param choices: list of text values

        """
        if not isinstance(choices, list):
            choices = ['']

        if choices[0] != '':
            choices.insert(0, '')
        old_choice = self._taskFilter.GetStringSelection()
        self._filterChoices = choices
        self._taskFilter.Clear()
        for item in choices:
            self._taskFilter.Append(item)
        if old_choice in choices:
            self._taskFilter.SetStringSelection(old_choice)
        else:
            self._taskFilter.SetStringSelection(self._filterChoices[0])

    def UpdateList(self, macrodata=None, filter=u''):
        """Repaints the ListCtrl with new values
        @keyword macrodata: the same tuple as for AddEntries

        """
        relaxed_filtering = self._taskRelaxedCheckBox.GetValue()

        if macrodata == None:
            macrodata = self.GetMacroData()
            if not len(macrodata): #no macros at all
                self._listctrl.ClearEntries()
                self._listctrl.Refresh()
                self.RefreshFilterChoices([''])

        if not len(macrodata):
            return

        all_filters = dict.fromkeys(map(lambda x: x[1], macrodata.values())).keys()
        all_filters.sort()

        # remove some entries
        if relaxed_filtering:
            compare_func = lambda x,y: x in y
        else:
            compare_func = lambda x,y: x == y

        if filter:
            tmp = {}
            for k, v in macrodata.items():
                if compare_func(filter, v[1]):
                    tmp[k] = v
            macrodata = tmp

        # Update the list
        self._listctrl.Freeze()
        self._listctrl.ClearEntries()
        self._listctrl.AddEntries(macrodata)
        self.RefreshFilterChoices(all_filters)
        self._listctrl.Thaw()
        self._listctrl.SortItems() # SortItems() calls Refresh()
        self._taskFilter.SetStringSelection(filter)


    def GetMainWindow(self):
        """ Get them main window that owns this instance """
        return self._mainwin

    def IsActive(self):
        """Check whether this browser is active or not"""
        return self._mainwin.IsActive()

    def OnListUpdate(self, event):
        """Callback if EVT_TIMER, EVT_BUTTON or EVT_CHOICE is fired.
        @param event: wxEvent

        """
        if not self.IsActive():
            return

        self.UpdateMacroBrowser()

    def OnFileSave(self, msg):
        """Callback when a page is saved.
        @param event: Message Object (notebook, page index)

        """
        if not self.IsActive():
            return

        nbook, page = msg.GetData()
        wx.CallAfter(self.UpdateMacroBrowserByOne, nbook)

    def OnShow(self, evt):
        """Shows the Macro Browser
        @param event: wxEvent

        """
        if evt.GetId() == ID_MACROLAUNCHER:
            mgr = self._mainwin.GetFrameManager()
            pane = mgr.GetPane(PANE_NAME)
            if pane.IsShown():
                pane.Hide()
                profiler.Profile_Set(ML_KEY, False)
            else:
                pane.Show()
                profiler.Profile_Set(ML_KEY, True)
            mgr.Update()
        else:
            evt.Skip()

    def OnUpdateMenu(self, evt):
        """UpdateUI handler for the panels menu item, to update the check
        mark.
        @param evt: wx.UpdateUIEvent

        """
        pane = self._mainwin.GetFrameManager().GetPane(PANE_NAME)
        evt.Check(pane.IsShown())


    #   ----------------- Macros -------------------#


    def OnNewMacro(self):
        """ Creates a new macro file and opens it in the editor """
        template = self.template()

        type = self._taskFilter.GetStringSelection()

        try:
            fname = ebmlib.GetUniqueName(self.macropath, 'macro.py')
        except:
            fname = os.path.join(self.macropath,
                             'macro_%i_%i.py' % (int(time.time()), random.randrange(65536)))


        template = template % {'__name__':'', '__type__':type, '__desc__':''}

        try:
            f = open(fname, 'w')
            f.write(template)
            f.close()
        except Exception, excp:
            self._log("[err] %s" % excp)
        else:
            self.OpenFiles([fname])
            self._register_macro(fname)
            self.UpdateList(filter = type)

    def OnViewMacro(self):
        """Shows the macro in a quick view"""
        macros = self._listctrl.GetSelectedMacros()
        if not len(macros):
            return

        for macro in macros:
            contents = self.GetMacroContents(macro['File'])

            dlg = QuickViewDialog(self, wx.ID_ANY,
                                  _("Quick view: %s") % macro['File'],
                                  contents=contents)
            dlg.ShowModal()
            dlg.Destroy()

    def OnEditMacro(self):
        """ Opens the selected macro into the editor """
        macros = self._listctrl.GetSelectedMacros()
        if not len(macros):
            return

        to_open = []
        for macro in macros:
            if '#' in macro['Name']:
                contents = self.GetMacroContents(macro['File'])
                dlg = QuickViewDialog(self, wx.ID_ANY,
                                      _("The macro is protected, you can view it only: %s") % macro['File'],
                                      contents=contents)

                dlg.ShowModal()
                dlg.Destroy()
                continue

            source = os.path.normpath(os.path.join(self.macropath, macro['File']))

            try:
                win = wx.GetApp().GetActiveWindow()
                if win:
                    nbook = win.GetNotebook()
                else:
                    nbook = self.GetParent().GetNotebook() #must fail, but...
                ctrls = nbook.GetTextControls()
                for ctrl in ctrls:
                    if source == ctrl.GetFileName():
                        nbook.SetSelection(nbook.GetPageIndex(ctrl))
                else:
                    to_open.append(source)
            except Exception, excp:
                self._log("[error] %s" % excp)

        if to_open:
            self.OpenFiles(to_open)

    def OnDelMacro(self):
        """ Deletes the selected macro from the filesystem. Asks for confirmation """
        macros = self._listctrl.GetSelectedMacros()
        if not len(macros):
            return

        dlg = wx.MessageDialog(self,
                               _("Are you sure you want to delete the selected macros?"),
                               _("Are you sure?"),
                               wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
        retr = dlg.ShowModal()
        dlg.Destroy()

        if retr != wx.ID_OK:
            mainw = self.GetMainWindow()
            mainw.SetStatusText(_("Macro deletion cancelled"))
            return

        for macro in macros:
            if '#' in macro['Name']:
                dlg = wx.MessageDialog(self,
                        _("Sorry, the macro '%s' is protected" % macro['Name']),
                        _("Sorry"),
                        wx.OK|wx.ICON_WARNING)
                dlg.ShowModal()
                dlg.Destroy()
                continue

            source = os.path.normpath(os.path.join(self.macropath, macro['File']))
            try:
                win = wx.GetApp().GetActiveWindow()
                if win:
                    nbook = win.GetNotebook()
                else:
                    nbook = self.GetMainWindow().GetNotebook()

                ctrls = nbook.GetTextControls()
                for ctrl in ctrls:
                    if source == ctrl.GetFileName():
                        index = nbook.GetPageIndex(ctrl)
                        if ctrl.GetModify():
                            ctrl.SetSavePoint()
                        nbook.SetSelection(index)
                        nbook.ClosePage()

                os.remove(source)
                del self._macros[macro['File']]
            except Exception, excp:
                self._log("[error] %s" % excp)

        filter_value = self._taskFilter.GetStringSelection()
        self.UpdateList(filter = filter_value)

    def OnRenameMacro(self):
        """ Rename the selected macro from the filesystem. Asks for confirmation """
        macros = self._listctrl.GetSelectedMacros()
        if not len(macros):
            return

        for macro in macros:
            if '#' in macro['Name']:
                dlg = wx.MessageDialog(self,
                        _("Sorry, the macro '%s' is protected" % macro['Name']),
                        _("Sorry"),
                        wx.OK|wx.ICON_WARNING)
                dlg.ShowModal()
                dlg.Destroy()
                continue

            source = os.path.normpath(os.path.join(self.macropath, macro['File']))
            base, file = os.path.split(source)
            new_filename = ''

            dlg = wx.TextEntryDialog(self,
                                     _("Rename %s to:") % file,
                                     _("Rename macro"), file)

            if dlg.ShowModal() == wx.ID_OK:
                new_filename = dlg.GetValue()
                if file == new_filename: # no change
                    dlg.Destroy()
                    continue

                dlg.Destroy()
            else:
                dlg.Destroy()
                continue

            try:
                win = wx.GetApp().GetActiveWindow()
                if win:
                    nbook = win.GetNotebook()
                else:
                    nbook = self.GetMainWindow().GetNotebook()
                
                page_closed = False
                ctrls = nbook.GetTextControls()
                for ctrl in ctrls:
                    if source == ctrl.GetFileName():
                        index = nbook.GetPageIndex(ctrl)
                        if ctrl.GetModify():
                            ctrl.SetSavePoint()
                        self._log("[info] closing macro before rename operation")
                        nbook.SetSelection(index)
                        nbook.ClosePage()
                        page_closed = True

                target = os.path.normpath(os.path.join(base, new_filename))
                
                if os.path.exists(target):
                    dlg = wx.MessageDialog(self,
                        _("The file '%s' already exists. Do you want to overwrite it?") % target,
                        _("Overwrite?"),
                        wx.YES_NO|wx.ICON_WARNING)
                    answ = dlg.ShowModal()
                    dlg.Destroy()
                    if answ != wx.ID_YES:
                        return
                
                os.rename(source, target)
                del self._macros[macro['File']]
                self._register_macro(target)
                
                # reopen the macro if it was opened before
                if page_closed:
                    self.OpenFiles([target])
                    
            except Exception, excp:
                self._log("[error] %s" % excp)

        filter_value = self._taskFilter.GetStringSelection()
        self.UpdateList(filter = filter_value)

    def OnStopMacro(self, macro_id):
        """Stops the running macro"""
        for thread in self.GetAllThreadsByMacro(macro_id):
            thread.Cancel()

    def OnRunMacro(self):
        """ Fires up the selected macro """
        macros = self._listctrl.GetSelectedMacros()
        if not len(macros):
            return
        self.RunMacros(macros)
        
    def RunMacros(self, macros):
        """Runs all the macros in the list
        @var macros: list of macro objects
        @return: nothing
        """
        if not self.SomethingIsRunning():
            self.ResetTaskCounter()
            wx.CallAfter(self.SetStatusMsg, '')

        win = wx.GetApp().GetActiveWindow()
        nbook = txtctrl = None
        if win:
            nbook = win.GetNotebook()
            txtctrl = nbook.GetCurrentCtrl()

        #if not txtctrl:
        #    return

        kwargs = {
                  'log' : self._log,
                  'txtctrl': txtctrl,
                  'nbook': nbook,
                  'win' : win,
                  'mlauncher': self,
                  }

        for macro in macros:
            self.ReloadMacroIfChanged(macro['File'])
            try:
                module = self._macros[macro['File']]['module']
            except:
                self.SetStatusMsg(msg = 'Macro %s not properly loaded' % macro['File'])
                continue

            if hasattr(module, 'run'):
                dlg = None
                try:
                    try:
                        #this is useless if the run_blocking is not in separate thread
                        #and besides it is crashing threads
                        """
                        dlg = wx.ProgressDialog(u"%s" % macro['File'],
                                   "Please wait...",
                                   maximum = 500,
                                   parent=self.GetMainWindow(),
                                   )

                        dlg.AppendUpdate = lambda s: dlg.Pulse()
                        updater = ProgressBarUpdater(self.GetMainWindow(), dlg)
                        controller = TaskThread(dlg, updater.run, timeout=0.1)
                        controller.start()
                        dlg.Show()
                        """

                        self.RegisterThread(module, macro['File'])
                        self.TaskCounter(1)
                        self.SetStatusMsg(msg=_("Macro %s is running") % macro['File'])

                        busy = wx.BusyInfo(_("Wait please..."))
                        module.run(**kwargs)
                        del busy

                        self.TaskCounter(-1, 1, 0)
                        self.SetStatusMsg(msg=_("Macro %s finished") % macro['File'])
                        #controller.Cancel()
                        #dlg.Destroy()
                    except Exception, msg:
                        self._log("[err] %s" % str(msg))
                        self._log(traceback.format_exc())
                        self.TaskCounter(-1, 0, 1)
                        self.SetStatusMsg(msg=_("Macro %s crashed") % macro['File'])
                finally:
                    self.UnRegisterThread(module)

            elif hasattr(module, 'run_thread'):
                try:
                    #TODO - the consumer should be in a separate thread probably
                    #       not self as now
                    task = MacroTaskThread(self, module.run_thread, **kwargs)
                    self.RegisterThread(task, macro['File'])
                    wx.CallAfter(task.start)
                except Exception, msg:
                    self._log("[err] %s" % str(msg))
                    self._log(traceback.format_exc())
            else:
                self._log('[err] Macro "%s" does not have function run or run_thread' % macro['File'])

    def _OnTaskStart(self, evt):
        """ Called from the MacroTaskThread when the worker is starting """
        self.TaskCounter(1)
        thread = evt.GetClientObject()
        macro_id = self.GetMacroIdByThread(thread)
        self.SetStatusMsg(u"Starting: %s" % macro_id)
        self._listctrl.RefreshListDisplay()
        wx.CallAfter(wx.CallLater, 500, self.SetStatusMsg,
                     u"%s is running" % macro_id)

    def _OnTaskError(self, evt):
        """ Called after the thread finished (with error) """
        thread, exception_msg, tracbk = evt.GetClientData()
        macro_id = self.GetMacroIdByThread(thread)

        self._log("[err] %s" % tracbk)
        self._log("[err] %s" % str(exception_msg))

        self.UnRegisterThread(thread)
        self.TaskCounter(-1, 0, 1)
        self._listctrl.RefreshListDisplay()
        self.SetStatusMsg('%s failed' % macro_id)
        wx.CallAfter(wx.CallLater, 500, self.SetStatusMsg, u"%s failed" % macro_id)

    def _OnTaskComplete(self, evt):
        """ Called after the thread finished (either killed or finished) """
        thread = evt.GetClientObject()
        macro_id = self.GetMacroIdByThread(thread)

        self.UnRegisterThread(thread)
        self.TaskCounter(-1, 1)
        self._listctrl.RefreshListDisplay()
        self.SetStatusMsg(u"%s finished" % macro_id)
        wx.CallAfter(wx.CallLater, 3000, self.SetStatusMsg, u'')

    def MacroIsRunning(self, idx):
        """Finds out whether the macro in question is in a running state
        @param ids: id of the macro (filename with suffix)
        @return: thread object

        """
        for thread, macro_id in self.GetAllThreads():
            if macro_id == idx:
                return thread
        return False

    def GetMacroIdByThread(self, thread):
        """Returns the macro_id for this thread instance, if thre is one"""
        for t, macro_id in self.GetAllThreads():
            if t is thread:
                return macro_id

    def GetAllThreadsByMacro(self, macro_id):
        """Returns all thread instances
        @param macro_id: filename of the macro
        @return: iterator

        """
        for thread, m_id in self.GetAllThreads():
            if macro_id == m_id:
                yield thread

    def GetAllThreads(self):
        """Returns dictionary with all registered (started) threads"""
        for thread_id, macro_id in self._threadsIdx.items():
            yield self._threads[thread_id], macro_id

    def SomethingIsRunning(self):
        """Just helper function, returns true if some threads are there"""
        return self._running

    def RegisterThread(self, thread, macro_id):
        """registers thread id and macro_id in the dictionary
        @param thread: thread instance
        @param macro_id: id of the macro (its filename)

        """
        self._threadsIdx[id(thread)] = macro_id
        self._threads[id(thread)] = thread

    def UnRegisterThread(self, thread):
        """Unregisters thread from the registry, returns the removed macro object"""
        try:
            del self._threadsIdx[id(thread)]
            return self._threads.pop(id(thread))
        except:
            return None

    def TaskCounter(self, running = 0, completed = 0, cancelled = 0):
        """Keeps track of number of task running, finished, cancelled"""
        self._running += running
        self._completed += completed
        self._cancelled += cancelled

    def ResetTaskCounter(self):
        self._running = 0
        self._completed = 0
        self._cancelled = 0

    def Consume(self, thread, result):
        """Receives results from the thread
        @param thread: thread that is working
        @param result: anything that the macro is returning

        """
        #print thread, result
        pass

    @staticmethod
    def OpenFiles(files):
        """Open the list of files in Editra for editing
        @param files: list of file names

        """
        to_open = list()
        for fname in files:
            try:
                res = os.stat(fname)[0]
                if stat.S_ISREG(res) or stat.S_ISDIR(res):
                    to_open.append(fname)
            except (IOError, OSError), msg:
                util.Log("[mlauncher][err] %s" % str(msg))

        win = wx.GetApp().GetActiveWindow()
        if win:
            win.GetNotebook().OnDrop(to_open)

    def SetStatusMsg(self, msg = ''):
        """Sets the status msg in the statusbar of the panel along with
        the counter of R: , F: C:
        """
        if msg:
            msg = '"%s"' % msg
        txt = u'R: % 2d, F: % 2d, C: % 2d  %s' % (self._running, self._completed, self._cancelled, msg)

        self._statusMsgBox.SetLabel(txt)
        self._statusMsgBox.Update()

    #---- Private Methods ----#

    def __FindMainWindow(self):
        """Find the mainwindow of this control. The mainwindow will either be
        the Top Level Window or if the panel is undocked it will be the parent
        of the miniframe the panel is in.
        @return: MainWindow or None

        """
        def IsMainWin(win):
            """Is the window a mainwindow"""
            return getattr(win, '__name__', '') == 'MainWindow'

        tlw = self.GetTopLevelParent()
        if IsMainWin(tlw):
            return tlw
        elif hasattr(tlw, 'GetParent'):
            tlw = tlw.GetParent()
            if IsMainWin(tlw):
                return tlw

        return None

    def _log(self, msg):
        """Writes a log message to the app log
        @param msg: message to write to the log

        """
        self.__log('[mlauncher] ' + str(msg))

    def __del__(self):
        """Stops the timer when the object gets deleted
        if it is still running

        """
        ed_msg.Unsubscribe(self.OnFileSave)
        self._log('__del__(): stopping timer')
        self._timer.Stop()

#---------------------------------------------------------------------------- #

class CustomListCtrl(wx.ListCtrl,
                     listmix.ListCtrlAutoWidthMixin,
                     listmix.ColumnSorterMixin):
    """The list ctrl used for the list"""

    def __init__(self, parent, id_=wx.ID_ANY,
                 pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.BORDER_NONE|wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES|
                       wx.LC_VIRTUAL|wx.LC_SORT_DESCENDING):
        """Init the CustomListCtrl"""
        wx.ListCtrl.__init__(self, parent, id_, pos, size, style)

        self.__log = wx.GetApp().GetLog()

        #---- Images used by the list ----#
        self._menu = None
        self._img_list = None
        self.sm_up = None
        self.sm_dn = None
        self._SetupImages()

        self._colSort = 0
        self._ascending = True

        #---- Set Columns Headers ----#
        self.col_names = ["Name", "Type", "Description", "File"]
        for i in range(len(self.col_names)):
            self.InsertColumn(i, _(self.col_names[i]))

        self.SetColumnWidth(0, 130)
        self.SetColumnWidth(1, 69)
        self.SetColumnWidth(2, 429)
        self.SetColumnWidth(3, 117)

        #---- data ----#
        # This attribute ist required by listmix.ColumnSorterMixin
        # {1:(prio, task, description, file, line, fullname), etc.}
        self.itemDataMap = {}

        # [key1, key2, key3, ...]
        self.itemIndexMap = self.itemDataMap.keys()
        self.SetItemCount(len(self.itemDataMap))

        # Holds last selected macro_id
        self._selectedMacro = None

        # Needed to hold a reference (otherwise it would be
        # garbagecollected too soon causing a crash)
        self._attr = None
        self._max_prio = 0

        #---- init base classes ----#
        # Hast to be after self.itemDataMap has been initialized and the
        # setup of the columns, but before sorting
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 5)

        #---- Events ----#
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnItemRightClick)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED,
                  lambda evt: self.GetParent().OnRunMacro())

        ed_msg.Subscribe(self._SetupImages, ed_msg.EDMSG_THEME_CHANGED)

        # Set initial sort order
        # sort by prio (column 0), descending order (0)
        self.SortListItems(0, 1)

    def __del__(self):
        ed_msg.Unsubscribe(self._SetupImages)
        super(CustomListCtrl, self).__del__()

    def _log(self, msg):
        """Writes a log message to the app log
        @param msg: message to write to the log

        """
        self.__log('[mlauncher] ' + str(msg))

    def _MakeMenu(self):
        """Make the context menu"""
        if self._menu is not None:
            self._menu.Destroy()
        else:
            parent = self.GetParent()
            self.Bind(wx.EVT_MENU, lambda evt: parent.OnNewMacro(), id=ID_NEW)
            self.Bind(wx.EVT_MENU, lambda evt: parent.OnEditMacro(), id=ID_EDIT)
            self.Bind(wx.EVT_MENU, lambda evt: parent.OnRunMacro(), id=ID_RUN)
            self.Bind(wx.EVT_MENU, lambda evt: parent.OnDelMacro(), id=ID_DELETE)
            self.Bind(wx.EVT_MENU, lambda evt: parent.OnRenameMacro(), id=ID_RENAME)
            self.Bind(wx.EVT_MENU, self.OnForceReloadMacro, id=ID_RELOAD)
            self.Bind(wx.EVT_MENU, self.OnStopMacro, id=ID_STOP)
            self.Bind(wx.EVT_MENU, lambda evt: parent.OnViewMacro(), id=ID_VIEW)

        # Make the menu
        menu = wx.Menu()
        item = menu.Append(ID_RUN,  _("Run"))
        SetMenuBitmap(item, ed_glob.ID_BIN_FILE)
        item = menu.Append(ID_STOP, _("Stop"))
        SetMenuBitmap(item, ed_glob.ID_STOP)
        menu.AppendSeparator()
        item = menu.Append(ID_EDIT, _("Edit"))
        SetMenuBitmap(item, ed_glob.ID_FILE)
        item = menu.Append(ID_NEW, _("New"))
        SetMenuBitmap(item, ed_glob.ID_NEW)
        item = menu.Append(ID_DELETE, _("Delete"))
        SetMenuBitmap(item, ed_glob.ID_DELETE)
        menu.AppendSeparator()
        menu.Append(ID_RENAME, _("Rename"))
        menu.Append(ID_RELOAD, _("Force reload"))
        menu.Append(ID_VIEW, _("Quick View"))
        self._menu = menu

    #---- Eventhandler ----#

    def OnItemRightClick(self, evt):
        """Callback when an item of the list has been clicked with the right
        mouse button.
        @param event: wx.Event

        """
        # If the menu has not been created yet do it now.
        self._selectedMacro = self.itemIndexMap[evt.m_itemIndex]

        if self._menu is None:
            self._MakeMenu()

        # Update Menu State
        macro_id = self.itemIndexMap[evt.m_itemIndex]
        self._selectedMacro = macro_id
        if self.GetParent().MacroIsRunning(self._selectedMacro):
            self._menu.Enable(ID_STOP, True) # Enable the stop item
            self._menu.SetLabel(ID_RUN, _("Run another"))
        else:
            self._menu.Enable(ID_STOP, False) # Disable the stop item
            self._menu.SetLabel(ID_RUN, _("Run"))

        self.PopupMenu(self._menu)
        evt.Skip()

    def OnStopMacro(self, evt):
        if self._selectedMacro:
            self.GetParent().OnStopMacro(self._selectedMacro)
        self._selectedMacro = None

    def OnForceReloadMacro(self, evt):
        if self._selectedMacro:
            self.GetParent().ForceMacroReload(self._selectedMacro)
        self._selectedMacro = None

    def _SetupImages(self, msg=None):
        """Setup the images and respond to theme change messages
        @keyword msg: Message Object or None

        """
        isize = (8, 8)
        self._img_list = wx.ImageList(8, 8)

        ups = wx.ArtProvider_GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU, isize)
        if not ups.IsOk():
            ups = wx.ArtProvider_GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR, isize)
        self.sm_up = self._img_list.Add(ups)

        down = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DOWN),
                                        wx.ART_MENU, isize)
        if not down.IsOk():
            down = wx.ArtProvider_GetBitmap(wx.ART_GO_DOWN,
                                            wx.ART_TOOLBAR, isize)
        self.sm_dn = self._img_list.Add(down)
        self.SetImageList(self._img_list, wx.IMAGE_LIST_SMALL)

        # Recreate menu if need be
        if self._menu is not None:
            self._MakeMenu()

        self.Refresh()

    def GetSelectedMacros(self):
        """Get all the ids of the selected rows
        @return: list (perhaps empty)

        """
        item = -1
        selected = []
        while 1:
            item = self.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1:
                break
            else:
                selected.append(item)
        return self.ParseItemIntoDict(selected)

    def ParseItemIntoDict(self, ids):
        """For all the ids gets their values into the dict
        @param ids: list of ids
        @return: list with dictionary of values

        """
        ret = []
        for id in ids:
            vals = {}
            for col in range(self.GetColumnCount()):
                vals[self.col_names[col]] = self.GetItem(id, col).GetText()
            ret.append(vals)
        return ret

    def AddEntries(self, entrydict):
        """Adds all entries from the entrydict. The entries must be a tuple
        containing
        entrytuple = (prio, tasktype, description, file, line, fullname)
        Refresh is not called.
        @param entrydict: a dictionary containing {key:entrytuple}

        """
        self.itemDataMap = dict(entrydict)
        self.itemIndexMap = self.itemDataMap.keys()
        self.SetItemCount(len(self.itemDataMap))
        try:
            self._max_prio = max([item[0]
                                  for item in self.itemDataMap.values()])
        except Exception, msg:
            self._log("[err] %s" % msg)

    def ClearEntries(self):
        """Removes all entries from list ctrl, refresh is not called"""
        self.itemDataMap.clear()
        self.itemIndexMap = []
        self.SetItemCount(0)

    def RefreshListDisplay(self):
        """Rechecks all the items' graphical features"""
        for idx in range(len(self.itemIndexMap)):
            macro_id = self.itemIndexMap[idx]
            data = self.itemDataMap[macro_id]
            item = self.GetItem(idx)
            if data[1] == 'error':
                item.SetBackgroundColour(wx.RED)
            elif self.GetParent().MacroIsRunning(macro_id):
                item.SetBackgroundColour(wx.GREEN)
            else:
                item.SetBackgroundColour(wx.WHITE)

        self.Refresh()

    #---- special methods used by the mixinx classes ----#

    #Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        """ this method is required by listmix.ColumnSorterMixin"""
        return self

    #---------------------------------------------------
    #Matt C, 2006/02/22
    #Here's a better SortItems() method --
    #the ColumnSorterMixin.__ColumnSorter() method already handles the
    #ascending/descending, and it knows to sort on another column if the chosen
    #columns have the same value.
    def SortItems(self, sorter=cmp):
        """This method is required by the
        wx.lib.mixins.listctrl.ColumnSorterMixin, for internal usage only

        """
        sorter = self.SpecialSorter # always use the special sorter
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items

        #redraw the list
        self.Refresh()

    def GetColumnSorter(self):
        """Overwrites the default GetColumnSorter of the mixin.
        @returns: a compare function object that takes two arguments:
        func(key1, key2)

        """
        return self.SpecialSorter

    def GetSecondarySortValues(self, col, key1, key2):
        """Overwrites the default GetSecondarySortValues. It uses the
        SpecialSorter to return a result.
        @param col: column index
        @param key1: first item index to compare
        @param key2: second item index to compare
        @returns: a tuple of the keys either (key1, key2) or (key2, key1)

        """
        cval = self.SpecialSorter(key1, key2)
        if 0 < cval:
            return (key2, key1)
        return (key1, key2)

    def SpecialSorter(self, key1, key2):
        """SpecialSorter sorts the list depending on which column should be
        sorted. It sorts automatically also by other columns.
        @param key1: first key to compare
        @param key2: second key to compare
        @returns: -1, 0 or 1 like the compare function

        """
        col = self._col
        ascending = self._colSortFlag[col]
        # (prio, task, description, file, line, fullname)
        if 0 == col: # prio -> sortorder: prio task file line
            _sortorder = [col, 1, 3, 4]
        elif 1 == col: # task -> sortorder: task prio, file , line
            _sortorder = [col, 0, 3, 4]
        elif 2 == col: # descr -> sortorder: descr, prio, task
            _sortorder = [col, 0, 1, 3, 4]
        elif 3 == col : # file -> sortorder: file, prio line
            _sortorder = [col, 0, 4]
        elif 4 == col: # line number -> sortorder: file, line
            _sortorder = [3, 4]

        cmpval = 0
        _idx = 0
        while( 0 == cmpval and _idx < len(_sortorder) ):
            item1 = self.itemDataMap[key1][ _sortorder[_idx] ]
            item2 = self.itemDataMap[key2][ _sortorder[_idx] ]
            #--- Internationalization of string sorting with locale module
            if type(item1) == type('') or type(item2) == type(''):
                cmpval = locale.strcoll(item1, item2)
            else:
                cmpval = cmp(item1, item2)
            #---
            _idx += 1

        # in certain cases always ascending/descending order is prefered
        if 0 == _sortorder[_idx-1] and 0 != col: # prio
            ascending = 0
        elif 4 == _sortorder[_idx-1] and 4 != col: # linenumber
            ascending = 1
        elif 3 == _sortorder[_idx-1] and 4 == col: # filename
            ascending = 1

        if ascending:
            return cmpval
        else:
            return -cmpval

    #Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        """This method is required by the
        wx.lib.mixins.listctrl.ColumnSorterMixin, for internal usage only

        """
        return (self.sm_dn, self.sm_up)

    #---- special listctrl eventhandlers ----#
        # These methods are callbacks for implementing the
        # "virtualness" of the list...

    def OnGetItemText(self, idx, col):
        """Virtual ListCtrl have to define this method, returns the text of the
        requested item.
        @param itemIdx: a int defining the item
        @param col: column
        @returns: text as a string for the item and column

        """
        index = self.itemIndexMap[idx]
        text = self.itemDataMap[index][col]
        return text

    @staticmethod
    def OnGetItemImage(item):
        """Virtual ListCtrl have to define this method, should return an image
        for the item, but since we have no images it always returns -1.
        @param item: itemindex (not used)
        @returns: always -1 because we have no images for the items.

        """
        return -1

    def OnGetItemAttr(self, idx):
        """Virtual ListCtrl have to define this method, should return item
        attributes
        @param itemIdx: index of an item for which we want the attributes
        @returns: a wx.ListItemAttr if the prio of the item is high enough,
        None otherwise

        """
        #return None

        #TODO - could use this to set colour for types
        idx = self.itemIndexMap[idx]
        type = self.itemDataMap[idx][1]
        if type == 'error':
            self._attr = wx.ListItemAttr(wx.NullColor,
                                         wx.RED,
                                         wx.NullFont)
            return self._attr
        elif self.GetParent().MacroIsRunning(idx):
            self._attr = wx.ListItemAttr(wx.NullColor,
                                         wx.GREEN,
                                         wx.NullFont)
            return self._attr
        return None

#-----------------------------------------------------------------------------#

class MacroTaskThread(outbuff.TaskThread):
    """Run a task in its own thread.
    This is a slighty modified version of the src.eclib.outbuff.TaskThread
    I needed to know which thread was returning results

    """
    def __init__(self, *args, **kwargs):
        """Initialize the TaskThread. All *args and **kwargs are passed
        to the task.
        @param parent: Parent Window/EventHandler to recieve the events
                       generated by the process.
        @param task: callable should be a generator object and must be iterable

        """
        outbuff.TaskThread.__init__(self, *args, **kwargs)

    def run(self):
        """Start running the task"""
        # Notify that task is begining
        evt = outbuff.OutputBufferEvent(outbuff.edEVT_TASK_START, self._parent.GetId())
        evt.SetClientObject(self)
        wx.PostEvent(self._parent, evt)
        time.sleep(.5) # Give the event a chance to be processed

        # Run the task and post the results
        try:
            m_iterator = self.task(*self._args, **self._kwargs)
            if type(m_iterator).__name__ == 'generator':
                for result in m_iterator:
                    self._parent.Consume(self, result)
                    if self.cancel:
                        break
            else:
                self._parent.Consume(self, m_iterator)
        except Exception, msg:
            evt = outbuff.OutputBufferEvent(edEVT_TASK_ERROR, self._parent.GetId())
            #evt.SetClientObject(self)
            evt.SetClientData((self, msg, traceback.format_exc()))
            wx.PostEvent(self._parent, evt)
        else:
            # Notify that the task is finished
            evt = outbuff.OutputBufferEvent(outbuff.edEVT_TASK_COMPLETE, self._parent.GetId())
            evt.SetClientObject(self)
            wx.PostEvent(self._parent, evt)

#-----------------------------------------------------------------------------#


class ProgressBarUpdater(object):
    """Class that handles the progress dialog Gauge.
    It is just used to move the gauge periodically
    step further"""
    def __init__(self, parent, dialog):
        object.__init__(self)
        self._parent = parent
        self._dialog = dialog

    def GetId(self):
        return self._parent.GetId()

    def run(self, timeout = 0.5):
        """Iterator that just sends signals back to the ProgressBarDialog"""
        while 1:
            time.sleep(timeout)
            yield 1

class QuickViewDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title,
            size=wx.DefaultSize,
            pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE|wx.CLOSE_BOX|wx.THICK_FRAME,
            contents=''
            ):
        """
        Dialog for QuickView instead of src.lib.ScrolledMessage which is not available
        in the binary Editra version.

        """
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)

        # layout
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        btnsizer = wx.StdDialogButtonSizer()

        txt = ed_basestc.EditraBaseStc(self, -1)
        txt.SetText(contents)
        txt.SetReadOnly(True)
        txt.SetLexer(wx.stc.STC_LEX_PYTHON)
        #txt.UpdateAllStyles()
        txt.FindLexer(set_ext=u'py')

        mainSizer.Add(txt, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5)

        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        self.SetSizer(mainSizer)
        self.SetInitialSize((650, 350))

        self.CenterOnScreen()
