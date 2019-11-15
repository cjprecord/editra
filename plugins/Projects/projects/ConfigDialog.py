###############################################################################
# Name: ConfigDialog.py                                                       #
# Purpose: Projects Configuration Dialgo                                      #
# Author: Kevin D. Smith <Kevin.Smith@sixquickrun.com>                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Configuration Dialog for the Projects Plugin

"""

__author__ = "Kevin D. Smith <Kevin.Smith@sixquickrun.com>"
__revision__ = "$Revision: 1402 $"
__scid__ = "$Id: ConfigDialog.py 1402 2011-06-05 17:13:42Z CodyPrecord $"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import stat
import wx
import wx.lib.mixins.listctrl as listmix

# Local Imports
import projects.FileIcons as FileIcons
import projects.SVN as SVN
import projects.CVS as CVS
import projects.GIT as GIT
import projects.BZR as BZR
import projects.HG as HG
import projects.crypto as crypto

# Editra Libraries
import ed_glob
import util
import ed_msg
import eclib
import ebmlib

#-----------------------------------------------------------------------------#
# Globals

_ = wx.GetTranslation

# Messages for synchronizing views
# msgdata == path of project
MSG_PROJ_ADDED = ('Projects', 'Added')
MSG_PROJ_REMOVED = ('Projects', 'Removed')

#-----------------------------------------------------------------------------#

class ConfigDialog(wx.Frame):
    """Dialog for configuring the Projects plugin settings"""
    def __init__(self, parent, id_, data, size=wx.DefaultSize):
        super(ConfigDialog, self).__init__(parent, id_, _("Projects Configuration"), 
                                           size=size, style=wx.DEFAULT_DIALOG_STYLE|wx.CLOSE_BOX)

        # Set title bar icon win/gtk
        util.SetWindowIcon(self)

        # Attributes
        panel = wx.Panel(self, size=(1, 5))
        self._notebook = ConfigNotebook(panel, wx.ID_ANY, data)
        self._data = data

        # Layout
        psizer = wx.BoxSizer(wx.HORIZONTAL)
        psizer.AddMany([((10, 10)), (self._notebook, 1, wx.EXPAND), ((10, 10))])
        pvsizer = wx.BoxSizer(wx.VERTICAL)
        pvsizer.AddMany([((10, 10)), (psizer, 1, wx.EXPAND), ((10, 10))])
        panel.SetSizer(pvsizer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetInitialSize()
        self.CenterOnParent()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        """ Notify watchers that the config data has changed """
        # HACK: fix crashes related to picker control and focus
        #       events on wxMac 2.8.9. Setting the focus away from
        #       any of the picker controls avoids the crash.
        self._notebook.SetFocus()

        evt.Skip()

#-----------------------------------------------------------------------------#

class ConfigNotebook(wx.Notebook):
    """Main configuration dialog notebook"""
    def __init__(self, parent, id_, data):
        """Create the notebook and initialize the two pages"""
        super(ConfigNotebook, self).__init__(parent, id_, 
                                             size=(450, -1), 
                                             style=wx.BK_DEFAULT )
        self.AddPage(GeneralConfigTab(self, -1, data), _("General"))
        self.AddPage(SourceControlConfigTab(self, -1, data),
                     _("Source Control"))
        self.data = data

        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)

    def OnDestroy(self, evt):
        """Notify of closer"""
        if self and evt.GetEventObject() is self:
            self.data.save()

#-----------------------------------------------------------------------------#

class GeneralConfigTab(wx.Panel):
    """General configuration page"""
    ID_FILE_FILTERS = wx.NewId()
    ID_SYNC_WITH_NOTEBOOK = wx.NewId()
    ID_DIFF_PROGRAM = wx.NewId()
    ID_BUILTIN_DIFF = wx.NewId()
    ID_EXTERNAL_DIFF = wx.NewId()

    def __init__(self, parent, id_, data):
        """Create the General configuration page"""
        super(GeneralConfigTab, self).__init__(parent, id_)
        self._data = data
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((10, 10))
        flags = wx.SizerFlags().Left().Expand().Border(wx.ALL, 6)
        ceflags = wx.SizerFlags().Center().Expand()
        sizer.AddF(wx.StaticText(self, -1, _('File Filters')), flags)
        filters = wx.TextCtrl(self, self.ID_FILE_FILTERS, 
                              ' '.join(data.getFilters()),
                              size=(-1, 100), style=wx.TE_MULTILINE)
        sizer.AddF(filters, flags)
        if wx.Platform == '__WXMAC__':
            filters.MacCheckSpelling(False)
        filters.SetToolTipString(_("Space separated list of files patterns to "
                                   "exclude from view\nThe use of wildcards "
                                   "(*) are permitted."))

        sizer.AddF(wx.StaticLine(self, -1, size=(-1, 1)),
                   ceflags.Border(wx.TOP|wx.BOTTOM, 10))
        sync = wx.CheckBox(self, self.ID_SYNC_WITH_NOTEBOOK,
                           _('Keep project tree synchronized with editor notebook'))
        sync.SetValue(data.getSyncWithNotebook())
        sizer.AddF(sync, flags)
        sizer.AddF(wx.StaticLine(self, -1, size=(-1, 1)),
                   ceflags.Border(wx.TOP|wx.BOTTOM, 10))
        sizer.AddF(wx.StaticText(self, -1, _('Diff Program')), flags)
        builtin = wx.RadioButton(self, self.ID_BUILTIN_DIFF, _('Built-in'))
        builtin.SetValue(data.getBuiltinDiff())
        sizer.AddF(builtin, flags.Border(wx.TOP|wx.LEFT, 6))
        sizer.Add((3, 3))
        
        # Radio button with file selector
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        external = wx.RadioButton(self, self.ID_EXTERNAL_DIFF, '')
        external.SetValue(not data.getBuiltinDiff())
        hsizer.AddF(external, wx.SizerFlags().Left().Border(wx.TOP|wx.BOTTOM|wx.LEFT, 6))
        if wx.Platform == '__WXMSW__':
            hsizer.Add((3, 3))

        diff_pkr = wx.FilePickerCtrl(self, self.ID_DIFF_PROGRAM,
                                     data.getDiffProgram(),
                                     message=_("Select diff program"),
                                     style=wx.FLP_USE_TEXTCTRL)
        diff_pkr.SetToolTipString(_("Use a specified diff program"))
        hsizer.AddF(diff_pkr, wx.SizerFlags(1).Left().Expand())
        sizer.AddF(hsizer, wx.SizerFlags().Left().Expand())
        
        # Extra space at bottom of panel
        sizer.AddF(wx.Panel(self, -1), wx.SizerFlags().Border(wx.TOP, 10))

        # Add space around the sides
        outsizer = wx.BoxSizer(wx.HORIZONTAL)
        outsizer.AddF(wx.Panel(self, -1, size=(10, 5)), wx.SizerFlags(0))
        outsizer.AddF(sizer, wx.SizerFlags(1).Expand())
        outsizer.AddF(wx.Panel(self, -1, size=(10, 5)), wx.SizerFlags(0))
        
        self.SetSizer(outsizer)
        self.SetInitialSize()
        
        # Event Handlers
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFileChange)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnSelect)
        self.Bind(wx.EVT_TEXT, self.OnTextChange)
        
    def OnFileChange(self, evt):
        """Update value of the diff program"""
        if evt.GetId() == self.ID_DIFF_PROGRAM:
            path = evt.GetEventObject().GetPath()
            if path:
                self._data.setDiffProgram(path)
            self.FindWindowById(self.ID_EXTERNAL_DIFF).SetValue(not(not(path)))
            self.FindWindowById(self.ID_BUILTIN_DIFF).SetValue(not(path))
        else:
            evt.Skip()
            
    def OnTextChange(self, evt):
        """ Update file filters value """
        if evt.GetId() == self.ID_FILE_FILTERS:
            obj = evt.GetEventObject()
            self._data.setFilters([x.strip() for x in obj.GetValue().split()
                                   if x.strip()])        
        else:
            evt.Skip()

    def OnCheck(self, evt):
        """ Handle checkbox events """
        if evt.GetId() == self.ID_SYNC_WITH_NOTEBOOK:
            obj = evt.GetEventObject()
            self._data.setSyncWithNotebook(obj.GetValue())
        else:
            evt.Skip()

    def OnSelect(self, evt):
        """Toggle the radio buttons to only allow one selection at a time"""
        e_id = evt.GetId()
        if e_id == self.ID_BUILTIN_DIFF:
            self._data.setBuiltinDiff(True)
            self.FindWindowById(self.ID_EXTERNAL_DIFF).SetValue(False)
        elif e_id == self.ID_EXTERNAL_DIFF:
            self._data.setBuiltinDiff(False)
            self.FindWindowById(self.ID_BUILTIN_DIFF).SetValue(False)
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

class SourceControlConfigTab(wx.Panel):
    """ Configuration page for configuring source control options """
    ID_SC_CHOICE = wx.NewId()
    ID_SC_COMMAND = wx.NewId()
    ID_SC_REP_CHOICE = wx.NewId()
    ID_SC_USERNAME = wx.NewId()
    ID_SC_PASSWORD = wx.NewId()
    ID_SC_ENVIRONMENT = wx.NewId()
    ID_SC_ADD_ENV = wx.NewId()
    ID_SC_REMOVE_ENV = wx.NewId()

    def __init__(self, parent, id_, data):
        """Create the Source control configuration page"""
        super(SourceControlConfigTab, self).__init__(parent, id_)

        # Attributes
        self._data = data
        
        # Layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((10, 10))
        flags = wx.SizerFlags().Left().Border(wx.ALL, 6)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sc_choice = wx.Choice(self, self.ID_SC_CHOICE,
                              choices=sorted([x for x in data.getSCSystems()]))
        sc_choice.SetSelection(0)
        sc_choice.SetToolTipString(_("Source control system"))
        hsizer.AddF(sc_choice, flags.Border(wx.ALL, 5))
        exe_picker = wx.FilePickerCtrl(self, self.ID_SC_COMMAND,
                                       style=wx.FLP_USE_TEXTCTRL)
        exe_picker.SetToolTipString(_("Executable Path"))
        hsizer.Add(exe_picker, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hsizer, 0, wx.EXPAND)
        
        # Repository configuration box
        sbox = wx.StaticBox(self, label=_('Repository Configuration'))
        repsizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        # Repository selector
        repsizer.AddF(wx.Choice(self, self.ID_SC_REP_CHOICE), flags.Expand())
        
        # Username and password
        userpass = wx.FlexGridSizer(3, 2)
        userpass.AddGrowableCol(1, 1)
        userpass.AddF(wx.StaticText(self, label=_('Username') + u':'), flags)
        userpass.AddF(wx.TextCtrl(self, self.ID_SC_USERNAME), flags.Center())
        userpass.AddF(wx.StaticText(self, label=_('Password') + u':'), flags)
        userpass.AddF(wx.TextCtrl(self, self.ID_SC_PASSWORD, 
                                  style=wx.TE_PASSWORD), flags)
        repsizer.AddF(userpass, wx.SizerFlags(1).Expand())
        repsizer.AddF(wx.StaticLine(self, wx.ID_ANY, size=(-1, 1)),
                                    wx.SizerFlags().Center().Expand().Border(wx.TOP|wx.BOTTOM, 10))

        # Environment variables
        repsizer.AddF(wx.StaticText(self, label=_('Environment Variables')), flags)
        env = AutoWidthListCtrl(self, self.ID_SC_ENVIRONMENT, size=(-1, 80), 
                                style=wx.LC_REPORT|wx.LC_SORT_ASCENDING|\
                                      wx.LC_VRULES|wx.LC_EDIT_LABELS)
        env.InsertColumn(0, _("Name"))
        env.InsertColumn(1, _("Value"))
        repsizer.AddF(env, flags.Expand())

        # Add env variable buttons
        envbtns = wx.BoxSizer(wx.HORIZONTAL)
        envbtns.Add(wx.BitmapButton(self, self.ID_SC_ADD_ENV, 
                                    FileIcons.getPlusBitmap()), 0)
        envbtns.Add(wx.BitmapButton(self, self.ID_SC_REMOVE_ENV,
                                    FileIcons.getMinusBitmap()), 0)
        repsizer.AddF(envbtns, flags.Expand())

        sizer.AddF(repsizer, flags)

        # Extra space at bottom of panel
        #sizer.AddF(wx.Panel(self, -1), wx.SizerFlags().Border(wx.TOP, 5))

        # Add space around the sides
        outsizer = wx.BoxSizer(wx.HORIZONTAL)
        outsizer.AddF(wx.Panel(self, wx.ID_ANY, size=(10, 5)), wx.SizerFlags(0))
        outsizer.AddF(sizer, wx.SizerFlags(1).Expand())
        outsizer.AddF(wx.Panel(self, wx.ID_ANY, size=(10, 5)), wx.SizerFlags(0))

        self.SetSizer(outsizer)
        self.SetInitialSize()
        
        # Initialize controls
        self.populateSystemOptions()
        
        # Set up event handlers
        self.Bind(wx.EVT_CHOICE, self.OnChoiceSelected)
        self.Bind(wx.EVT_TEXT, self.OnTextChange)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFileChange)
        self.Bind(wx.EVT_BUTTON, self.OnButtonPress)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndEdit)

    @property
    def currentSystem(self):
        """Return the currently selected source control system"""
        return self.FindWindowById(self.ID_SC_CHOICE).GetStringSelection()

    @property
    def currentRepository(self):
        """Return the currently selected repository"""
        return self.FindWindowById(self.ID_SC_REP_CHOICE).GetStringSelection()
    
    def populateSystemOptions(self):
        """Populate the controls with the source control system option data"""
        sc = self.currentSystem
        self.populateRepositoryList()
        try:
            command = self._data.getSCCommand(sc)
        except KeyError:
            command = ''
        self.FindWindowById(self.ID_SC_COMMAND).SetPath(command)

    def populateEnvironment(self):
        """Populate the environmental variable list with the values from
        the current config data.

        """
        sc, rep = self.currentSystem, self.currentRepository
        envlist = self.FindWindowById(self.ID_SC_ENVIRONMENT)
        envlist.DeleteAllItems()        
        try:
            env = self._data.getSCEnvVars(sc, rep)
        except KeyError:
            env = {}

        for name, value in sorted(env.items()):
            index = envlist.InsertStringItem(sys.maxint, '')
            envlist.SetStringItem(index, 0, name)
            envlist.SetStringItem(index, 1, value)

    def populateUserInfo(self):
        """Populate the username and password information"""
        sc, rep = self.currentSystem, self.currentRepository
        try:
            username = self._data.getSCUsername(sc, rep)
        except KeyError:
            username = ''

        self.FindWindowById(self.ID_SC_USERNAME).SetValue(username)
        try: 
            password = self._data.getSCPassword(sc, rep)
            if password:
                password = crypto.Decrypt(password, self._data.salt)
        except KeyError:
            password = ''
        self.FindWindowById(self.ID_SC_PASSWORD).SetValue(password)

    def populateRepositoryList(self):
        """ Populate the list of repositories that are under the currently
        selected control system.

        """
        sc = self.currentSystem
        rep = self.FindWindowById(self.ID_SC_REP_CHOICE)
        rep.Clear()
        items = [_("Default")] + \
                sorted([x.strip() 
                        for x in self._data.getSCRepositories(sc).keys()
                        if x != _("Default")]) + \
                ['',_("Add Repository..."),_("Remove Repository...")]
        rep.AppendItems(items)
        rep.SetSelection(0)
        self.populateEnvironment()
        self.populateUserInfo()
    
    def OnTextChange(self, evt):
        """ Update username/password in config data """
        obj, e_id = evt.GetEventObject(), evt.GetId()
        sc, rep = self.currentSystem, self.currentRepository
        # Change username
        if e_id == self.ID_SC_USERNAME:
            value = obj.GetValue().strip()
            if not value:
                self._data.removeSCUsername(sc, rep)
            else:
                self._data.setSCUsername(sc, rep, value)
        # Change password
        elif e_id == self.ID_SC_PASSWORD:
            value = obj.GetValue().strip()
            if not value:
                self._data.removeSCPassword(sc, rep)
            else:
                self._data.setSCPassword(sc, rep, value)
        else:
            evt.Skip()
        
    def OnFileChange(self, evt):
        """ Update config data with the source control command value """
        obj, e_id = evt.GetEventObject(), evt.GetId()
        if e_id == self.ID_SC_COMMAND:
            sc = self.currentSystem
            self._data.setSCCommand(sc, obj.GetPath().strip())
        else:
            evt.Skip()
    
    def OnButtonPress(self, evt):
        """ Add and Remove environmental variables """
        e_id = evt.GetId()
        if e_id == self.ID_SC_ADD_ENV:
            env = self.FindWindowById(self.ID_SC_ENVIRONMENT)
            index = env.InsertStringItem(sys.maxint, '')
            env.SetStringItem(index, 0, _('*NAME*'))
            env.SetStringItem(index, 1, _('*VALUE*'))
        elif e_id == self.ID_SC_REMOVE_ENV:
            env = self.FindWindowById(self.ID_SC_ENVIRONMENT)
            item = -1
            items = []
            while True:
                item = env.GetNextItem(item, wx.LIST_NEXT_ALL,
                                       wx.LIST_STATE_SELECTED)
                if item == -1:
                    break
                items.append(item)
            for item in reversed(sorted(items)):
                env.DeleteItem(item)
            self.saveEnvironmentVariables()
        else:
            evt.Skip()
            
    def OnEndEdit(self, evt):
        """ Save settings when edit finishes """
        wx.CallAfter(self.saveEnvironmentVariables)

    def saveEnvironmentVariables(self):
        """ Update config data with current values """
        sc, rep = self.currentSystem, self.currentRepository
        env = self.FindWindowById(self.ID_SC_ENVIRONMENT)
        evars = self._data.getSCEnvVars(sc, rep)
        evars.clear()
        item = -1
        while True:
            item = env.GetNextItem(item)
            if item == -1:
                break
            name = env.GetItem(item, 0).GetText().strip()
            value = env.GetItem(item, 1).GetText().strip()
            evars[name] = value
    
    def OnChoiceSelected(self, evt):
        """Handle EVT_CHOICE"""
        obj, e_id = evt.GetEventObject(), evt.GetId()
        sc = self.currentSystem
        if e_id == self.ID_SC_CHOICE:
            self.populateSystemOptions()
        elif e_id == self.ID_SC_REP_CHOICE:
            # Empty selection
            if not obj.GetStringSelection().strip():
                obj.SetSelection(0)
                
            # Remove repository
            elif obj.GetSelection() == (obj.GetCount() - 1):
                # Default - Blank - Add - Remove: if only 4, there's nothing to remove
                if obj.GetCount() == 4:
                    obj.SetSelection(0)
                else:
                    choices = sorted([x for x in self._data.getSCRepositories(sc).keys() if x != 'Default'])
                    scd = wx.SingleChoiceDialog(self, _('Select the repository path to remove'),
                        _('Remove repository'), choices, style=wx.DEFAULT_DIALOG_STYLE|wx.OK|wx.CANCEL|wx.CENTER)
                    if scd.ShowModal() == wx.ID_OK:
                        value = scd.GetStringSelection().strip()
                        self._data.removeSCRepository(sc, value)
                    self.populateRepositoryList()

            # Add repository
            elif obj.GetSelection() == (obj.GetCount() - 2):
                ted = wx.TextEntryDialog(self, _('Please enter a repository path.  Partial paths may also be entered.'),
                     _('Add a New Repository Path'), style=wx.OK|wx.CANCEL|wx.CENTER)
                ted.SetSize((300, -1))
                if ted.ShowModal() == wx.ID_OK:
                    value = ted.GetValue().strip()
                    if value:
                        try: 
                            self._data.getSCRepository(self.currentSystem, value)
                        except KeyError:
                            self._data.addSCRepository(self.currentSystem, value) 
                        self.populateRepositoryList()
                        obj.SetStringSelection(value)
                    else:
                        obj.SetSelection(0)
                else:
                    obj.SetSelection(0)
            self.populateUserInfo()
            self.populateEnvironment()
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

class AutoWidthListCtrl(eclib.EEditListCtrl):
    ''' List control for showing and editing environmental variables '''
    def __init__(self, *args, **kwargs):
        super(AutoWidthListCtrl, self).__init__(*args, **kwargs)

        # Attributes
        self.col_locs = [0]
                
    def OnLeftDown(self, evt=None):
        """Examine the click and double
        click events to see if a row has been click on twice. If so,
        determine the current row and column and open the editor.

        """
        from bisect import bisect        

        if self.editor.IsShown():
            self.CloseEditor()
            
        xpos, ypos = evt.GetPosition()
        row = self.HitTest((xpos, ypos))[0]
        if row != self.curRow: # self.curRow keeps track of the current row
            evt.Skip()
            return
            
        # >>> Make sure that an item is selected first
        if not self.GetSelectedItemCount():
            evt.Skip()
            return
        # <<<
        
        # the following should really be done in the mixin's init but
        # the wx.ListCtrl demo creates the columns after creating the
        # ListCtrl (generally not a good idea) on the other hand,
        # doing this here handles adjustable column widths
        
        loc = 0
        for n in range(self.GetColumnCount()):
            loc = loc + self.GetColumnWidth(n)
            self.col_locs.append(loc)

        col = bisect(self.col_locs, xpos + self.GetScrollPos(wx.HORIZONTAL)) - 1
        self.OpenEditor(col, row)

#-----------------------------------------------------------------------------#

class ConfigData(dict):
    """ Configuration data storage class """
    __metaclass__ = ebmlib.Singleton
    def __init__(self, data=dict()):
        """ Create the config data object """
        super(ConfigData, self).__init__(self)

        self['source-control'] = {}
        self['general'] = {}
        self['projects'] = {}

        self.setFilters(sorted(['CVS', 'dntnd', '.DS_Store', '.dpp', '.newpp',
                                '*~', '*.a', '*.o', '.poem', '.dll', '._*',
                                '.localized', '.svn', '*.pyc', '*.bak', '#*',
                                '*.pyo','*%*', '.git', '*.previous', '*.swp',
                                '.#*', '.bzr', '.hg']))
        self.setBuiltinDiff(True)
        if wx.Platform == '__WXMAC__':
            self.setDiffProgram('opendiff')
        else:
            self.setDiffProgram('')
        self.setSyncWithNotebook(True)
        
        self.addSCSystem(CVS.CVS())
        self.addSCSystem(SVN.SVN())
        self.addSCSystem(GIT.GIT())
        self.addSCSystem(BZR.BZR())
        self.addSCSystem(HG.HG())
        
        self.load()

    @property
    def salt(self):
        return '"\x17\x9f/D\xcf'
        
    def addProject(self, path, options=dict()):
        """ Add a project and its options to the data """
        self['projects'][path] = options
        
    def removeProject(self, path):
        """ Remove a project from the configuration """
        try:
            del self['projects'][path]
        except KeyError:
            pass
        
    def clearProjects(self):
        """ Clear all project data """
        self['projects'].clear()
    
    def getProjects(self):
        """ Get all project data """
        return self['projects']
        
    def getProject(self, path):
        """ Get data for a specified project """
        return self['projects'][path]
        
    def setFilters(self, filters):
        """ Set the filters to use in filtering tree display """
        self['general']['filters'] = filters
        self.updateSCSystems()
        
    def getFilters(self):
        """ Get all filters """
        return self['general']['filters']
        
    def setBuiltinDiff(self, use_builtin=True):
        """ Set whether to use builtin diff or not
        @param use_builtin: bool

        """
        self['general']['built-in-diff'] = use_builtin
        
    def getBuiltinDiff(self):
        """ Use Projects builtin diff program """
        return self['general']['built-in-diff']
        
    def setDiffProgram(self, command):
        """ Set the diff program to use for comparing revisions """
        self['general']['diff-program'] = command
        
    def getDiffProgram(self):
        """ Get path/name of diff program to use """
        return self['general']['diff-program']
        
    def setSyncWithNotebook(self, do_sync=True):
        """ Set whether to syncronize tree with notebook or not
        @param do_sync: bool

        """
        self['general']['sync-with-notebook'] = do_sync
    
    def getSyncWithNotebook(self):
        """ Is the tree syncronized with the notebook """
        return self['general']['sync-with-notebook']
    
    def addSCSystem(self, instance, repositories=None):
        """ Add a source control system to the configuration """
        self['source-control'][instance.name] = self.newSCSystem(instance, repositories)
        self.updateSCSystems()
        return self['source-control'][instance.name]
    
    def updateSCSystems(self):
        """ Update all source control systems settings with the current 
        configuration data.
        
        """
        for key, value in self.getSCSystems().items():
            try:
                value['instance'].filters = self.getFilters()
                value['instance'].repositories = self.getSCRepositories(key)
                value['instance'].command = self.getSCCommand(key)
            except:
                pass
    
    def getSCSystems(self):
        """ Get all source control systems """
        return self['source-control']

    def getSCSystem(self, name):
        """ Get a specified source control system """
        return self['source-control'][name]

    def removeSCSystem(self, name):
        """ Remove a specified source control system from the config """
        try:
            del self['source-control'][name]
        except:
            pass

    def newSCSystem(self, instance, repositories=None):
        """ Create config object for a new source control system """
        system = {'command'  : instance.command,
                  'instance' : instance, 
                  'repositories': {'Default' : self.newSCRepository()}}
        if repositories is not None:
            system['repositories'].update(repositories)

        return system

    @staticmethod
    def newSCRepository():
        """ New empty config for a source control repository """
        return {'username':'', 'password':'', 'env':{}}
    
    def getSCRepositories(self, sc):
        """ Return all repositories for a given control system """
        return self.getSCSystem(sc)['repositories']
        
    def getSCRepository(self, sc, rep):
        """ Get the repository of a given source control system """
        return self.getSCRepositories(sc)[rep]
        
    def addSCRepository(self, sc, name):
        """ Add a new repository to a given systems data """
        self.getSCRepositories(sc)[name] = self.newSCRepository()
        
    def removeSCRepository(self, sc, name):
        """ Remove a repositories data from the given source control system """
        try:
            del self.getSCRepositories(sc)[name]
        except KeyError:
            pass
        
    def setSCUsername(self, sc, rep, name):
        """ Set the username for the given system and repository """
        self.getSCRepository(sc, rep)['username'] = name
    
    def removeSCUsername(self, sc, rep):
        """ Remove a username from the data of a given systems repository """
        try:
            del self.getSCRepository(sc, rep)['username']
        except KeyError:
            pass
        
    def getSCUsername(self, sc, rep):
        """ Get the username from the given system and repository """
        return self.getSCRepository(sc, rep)['username']
        
    def setSCPassword(self, sc, rep, password):
        """ Set the password for a given system and repository """
        if password.strip():
            enc_passwd = crypto.Encrypt(password, self.salt)
            self.getSCRepository(sc, rep)['password'] = enc_passwd
        else:
            self.getSCRepository(sc, rep)['password'] = ''            

    def getSCPassword(self, sc, rep):
        """ Get the password of the given systems repository """
        return self.getSCRepository(sc, rep)['password']

    def removeSCPassword(self, sc, rep):
        """ Remove the password data from a given systems repo """
        try:
            del self.getSCRepository(sc, rep)['password']
        except KeyError:
            pass
        
    def setSCCommand(self, sc, command):
        """ Set the command used to run the given source control system """
        system = self.getSCSystem(sc)
        system['instance'].command = system['command'] = command
    
    def getSCCommand(self, sc):
        """ Get the command used with the given system """
        return self.getSCSystem(sc)['command']

    def addSCEnvVar(self, sc, rep, name, value):
        """ Add environmental variables to use with a given system """
        self.getSCEnvVars(sc, rep)[name] = value
        
    def removeSCEnvVar(self, sc, rep, name):
        """ Remove the named environmental variable from the source system """
        try:
            del self.getSCEnvVars(sc, rep)[name]
        except KeyError:
            pass
        
    def getSCEnvVars(self, sc, rep):
        """ Get all environmental variables for the given systems repository """
        return self.getSCRepository(sc, rep)['env']

    def getSCEnvVar(self, sc, rep, name):
        """ Get a named environmental variable from the given system/repo """
        return self.getSCEnvVars(sc, rep)[name]
        
    def load(self):
        """ Load the saved configuration data from on disk config file """
        data = {}
        try:
            filename = ed_glob.CONFIG['CACHE_DIR'] + 'Projects.config'
            conf = util.GetFileReader(filename)
            if conf != -1:
                try: 
                    data = eval(conf.read())
                    conf.close()
                except:
                    conf.close()
                    os.remove(filename)
        except OSError:
            pass

        recursiveupdate(self, data)
        self.updateSCSystems()

    def save(self):
        """ Write the data out to disk """
        #print repr(self)
        try:
            filename = ed_glob.CONFIG['CACHE_DIR'] + 'Projects.config'
            conf = util.GetFileWriter(filename)
            if conf != -1:
                conf.write(repr(self))
                conf.close()
            os.chmod(filename, stat.S_IRUSR|stat.S_IWUSR)
        except OSError:
            pass

#-----------------------------------------------------------------------------#

def recursiveupdate(dest, src):
    """ Recursively update dst from src """
    for key, value in src.items():
        if key in dest:
            if isinstance(value, dict):
                recursiveupdate(dest[key], value)
            else:
                dest[key] = value
        else:
            dest[key] = value
    return dest
