###############################################################################
# Name: templates.py                                                          #
# Purpose: User interface and template classes for CodeTemplater              #
# Author: Erik Tollerud <erik.tollerud@gmail.com>                             #
# Copyright: (c) 2010 Erik Tollerud <erik.tollerud@gmail.com>                 #
# License: wxWindows License                                                  #
###############################################################################

"""CodeTemplater UI and CodeTemplate class"""
__author__ = "Erik Tollerud"

#-----------------------------------------------------------------------------#

import wx
import iface
import plugin
from os import path
from string import Template

from ed_glob import CONFIG,SB_INFO,ID_RELOAD_ENC
from ed_menu import EdMenu
from syntax import synglob,syntax
from profiler import Profile_Get, Profile_Set, Profile_Del
_ = wx.GetTranslation

PROFILE_KEY_TEMPLATES = 'CodeTemplater.Templates'

#-----------------------------------------------------------------------------#

class CodeTemplate(object):
    """
    a template for use with the CodeTemplater editra plugin
    """

    def __init__(self, name, templatestr, description=u'', indent=True):
        super(CodeTemplate, self).__init__()

        self.name = name
        self.templ = Template(templatestr)
        self.description = description
        self.indent = indent

    def DoTemplate(self, page):
        seltext = page.GetSelectedText().strip()

        submap = {}
        seltext.strip()
        submap['same'] = seltext
        if len(seltext) > 0:
            submap['upper'] = seltext[0].upper()+seltext[1:]
            submap['lower'] = seltext[0].lower()+seltext[1:]
        else:
            submap['upper'] = submap['lower'] = seltext
        wx.GetApp().GetLog()("[CodeTemplater][info] Applying template %s to %s"%(self.name,submap['same']))

        if self.indent:
            #compute indentation
            line = page.GetCurrentLine()
            indent =  page.GetTabWidth() if page.GetIndentChar()=='\t' else page.GetIndent()
            indentcount = page.GetLineIndentation(line)/indent
            indentstr = page.GetIndentChar()*indentcount
        else:
            indentstr = u''

        if seltext != '':
            page.DeleteBack()
        propstring = self.templ.safe_substitute(submap)
        propstring = propstring.replace('\t',page.GetIndentChar())
        fullstring = propstring.replace('\n',page.GetEOLChar()+indentstr)
        if '#CUR' in fullstring:
            curind = fullstring.index('#CUR')
            curoffset = len(fullstring) - 4 - curind
            fullstring = fullstring.replace('#CUR','',1)
        else:
            curoffset = None

        page.AddText(fullstring)
        if curoffset is not None:
            newpos = page.GetCurrentPos() - curoffset
            page.SetCurrentPos(newpos)
            page.SetSelection(newpos,newpos)

#-----------------------------------------------------------------------------#

class TemplateEditorDialog(wx.Dialog):
    def __init__(self, parent, plugin, ID, title, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER,
                 initiallang=None):
        super(TemplateEditorDialog, self).__init__(parent, ID, title, pos,
                                                   size, style)

        basesizer = wx.BoxSizer(wx.VERTICAL)
        self.edpanel = TemplateEditorPanel(self, plugin, initiallang, -1)
        basesizer.Add(self.edpanel, 1, wx.EXPAND)

        line = wx.StaticLine(self, wx.ID_ANY,
                             size=(20,-1), style=wx.LI_HORIZONTAL)
        basesizer.Add(line, 0,
                      wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        # Layout buttons
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.AddStretchSpacer()
        okbtn = wx.Button(self, wx.ID_CLOSE)
        okbtn.Bind(wx.EVT_BUTTON, self.OnClose)
        btnsizer.Add(okbtn, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        profbtn = wx.Button(self, wx.ID_SAVE,_("Save"))
        tooltip = _("Save to the Profile to be reloaded on next Startup")
        profbtn.SetToolTipString(tooltip)
        profbtn.Bind(wx.EVT_BUTTON, self.OnSaveProfile)
        btnsizer.Add(profbtn, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        resetbtn = wx.Button(self, wx.ID_RESET, _("Reset to defaults"))
        tooltip = _("Resets the Profile to default as well as the Current Setup")
        resetbtn.SetToolTipString(tooltip)
        resetbtn.Bind(wx.EVT_BUTTON, self.OnResetProfile)
        btnsizer.Add(resetbtn, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        btnsizer.AddStretchSpacer()
        basesizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER)

        self.SetSizer(basesizer)
        self.SetInitialSize()

    def OnSaveProfile(self,reset=False):
        #profile key should be in language name
        #d = dict([(synglob.GetDescriptionFromId(k),v) for k,v in tempd.iteritems()])
        #translate template objects into their dict instead of CodeTemplate objects
        self.edpanel.ApplyTemplateInfo(updatelistind=self.edpanel.lastind)

        newd = {}
        for lang,ld in self.edpanel.plugin.templates.iteritems():
            newld = {}
            for k,v in ld.iteritems():
                newld[k] = v.__dict__.copy()
                newld[k]['templ'] = newld[k]['templ'].template
            newd[synglob.GetDescriptionFromId(lang)] = newld

        Profile_Set(PROFILE_KEY_TEMPLATES,newd)

    def OnResetProfile(self,evt):
        Profile_Set(PROFILE_KEY_TEMPLATES,None)
        self.edpanel.plugin.templates = load_templates()
        self.edpanel.listbox.SetItems(self.edpanel.GetTemplateNames())

    def OnClose(self,evt):
        self.Destroy()

#-----------------------------------------------------------------------------#

class TemplateEditorPanel(wx.Panel):
    def __init__(self,parent,plugin,initiallang=None, *args, **kwargs):
        super(TemplateEditorPanel, self).__init__(parent, *args, **kwargs)

        # Attributes
        self.plugin = plugin
        self.removing = False
        self.lastind = None
        self.lastname = ''

        # Layout left side of panel to display and alter list of templates
        basesizer = wx.BoxSizer(wx.HORIZONTAL)
        listsizer = wx.BoxSizer(wx.VERTICAL)
        staticbox = wx.StaticBox(self, label=_("Code Templates"))
        boxsz = wx.StaticBoxSizer(staticbox, wx.VERTICAL)

        langchoices = get_language_list()
        if isinstance(initiallang,basestring):
            id = synglob.GetIdFromDescription(initiallang)
        else:
            id = initiallang
            initiallang = synglob.GetDescriptionFromId(initiallang)

        if initiallang is None or initiallang not in langchoices:
            initiallang = langchoices[0]

        self.lastlangstr = initiallang

        self.langchoice = wx.Choice(self, wx.ID_ANY, choices=langchoices)
        self.langchoice.SetSelection(self.langchoice.FindString(initiallang))
        self.Bind(wx.EVT_CHOICE, self.OnLangChange, self.langchoice)
        listsizer.Add(self.langchoice,0,wx.ALIGN_CENTRE|wx.ALL, 5)

        self.listbox = wx.ListBox(self, wx.ID_ANY, size=(150,300),
                                  choices=self.GetTemplateNames(),
                                  style=wx.LB_SINGLE)
        self.Bind(wx.EVT_LISTBOX, self.OnListChange, self.listbox)
        listsizer.Add(self.listbox, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        addbutton = wx.Button(self, wx.ID_ADD)
        addbutton.SetToolTipString(_("Add a New Template"))
        self.Bind(wx.EVT_BUTTON, self.OnAdd, addbutton)
        buttonsizer.Add(addbutton, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.rembutton = wx.Button(self,wx.ID_DELETE)
        self.rembutton.SetToolTipString(_("Remove the selected Template"))
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.rembutton)
        self.rembutton.Enable(False)
        buttonsizer.Add(self.rembutton,1,wx.ALIGN_CENTRE|wx.ALL, 5)
        listsizer.Add(buttonsizer, 0, wx.ALIGN_CENTRE|wx.ALL, 2)
        boxsz.Add(listsizer, 1, wx.EXPAND)
        basesizer.Add(boxsz, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        # Layout right side of panel to display the selected template
        templateinfo = wx.BoxSizer(wx.VERTICAL)

        namesizer = wx.BoxSizer(wx.HORIZONTAL)
        helplabel = wx.StaticText(self, wx.ID_ANY, _("Name:"))
        namesizer.Add(helplabel,0,wx.ALIGN_CENTRE|wx.ALL, 2)
        self.nametxt = wx.TextCtrl(self, wx.ID_ANY)
        namesizer.Add(self.nametxt,1,wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 2)
        templateinfo.Add(namesizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)
        self.nametxt.Enable(False)

        helpsizer = wx.BoxSizer(wx.HORIZONTAL)
        helplabel = wx.StaticText(self, wx.ID_ANY, _("Help Text:"))
        helpsizer.Add(helplabel,0,wx.ALIGN_CENTRE|wx.ALL, 2)
        self.helptxt = wx.TextCtrl(self, wx.ID_ANY)
        helpsizer.Add(self.helptxt, 1, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 2)
        templateinfo.Add(helpsizer, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)
        self.helptxt.Enable(False)

        indsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.indentcb = wx.CheckBox(self,label=_("Obey Indentation?"))
        tooltip = _("Check to have all lines of the template be indented to match the indentation at which the template is inserted")
        self.indentcb.SetToolTipString(tooltip)
        indsizer.Add(self.indentcb,0,wx.ALIGN_CENTRE|wx.ALL, 2)
        templateinfo.Add(indsizer, 0, wx.ALIGN_CENTER|wx.ALL, 2)
        self.indentcb.Enable(False)

        templabel = wx.StaticText(self, wx.ID_ANY, _("Template Codes:\n")+
                '"${same}": '+_('Replace with selected text.\n"')+
                '${upper}":'+_('Replace with selected, first character upper case.\n')+
                '"${lower}":'+_('Replace with selected, first character lower case.\n')+
                '"$$":'+_('An "$" character.') + u'\n' +
                '"#CUR":'+_('Move cursor to this location after inserting template.')+'\n'+
                _('tabs will be replaced by the appropriate indent.')
                )
        templateinfo.Add(templabel, 0, wx.ALIGN_CENTER|wx.ALL, 2)
        self.temptxt = wx.TextCtrl(self, wx.ID_ANY, size=(300,200),
                                   style=wx.TE_MULTILINE)
        templateinfo.Add(self.temptxt, 1, wx.EXPAND|wx.ALL, 2)
        self.temptxt.Enable(False)

        basesizer.Add(templateinfo, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)

        self.SetSizer(basesizer)

    def GetLangTemplateDict(self, lastlangstr=False):
        if lastlangstr:
            langId = synglob.GetIdFromDescription(self.lastlangstr)
        else:
            csel = self.langchoice.GetStringSelection()
            langId = synglob.GetIdFromDescription(csel)
        return self.plugin.templates[langId]

    def GetTemplateNames(self):
        return self.GetLangTemplateDict().keys()

    def UpdateTemplateinfoUI(self,name):
        try:
            templ = self.GetLangTemplateDict()[name]
        except KeyError:
            templ = None

        if templ is None:
            #starts out blank
            self.nametxt.SetValue(unicode(name) if name is not None else u'')
            self.temptxt.SetValue(u'')
            self.helptxt.SetValue(u'')
            self.indentcb.SetValue(False)
        else:
            self.nametxt.SetValue(templ.name)
            self.temptxt.SetValue(templ.templ.template)
            self.helptxt.SetValue(templ.description)
            self.indentcb.SetValue(templ.indent)

        enabled = name is not None
        self.nametxt.Enable(enabled)
        self.temptxt.Enable(enabled)
        self.helptxt.Enable(enabled)
        self.indentcb.Enable(enabled)

        self.lastname = name

    def ApplyTemplateInfo(self, updatelistind=None, lastlangstr=False):
        name = self.nametxt.GetValue()
        if name.startswith(u'<') or name.endswith(u'>') or name.strip() == u'':
            return # don't apply initial names

        help = self.helptxt.GetValue()
        tempstr = self.temptxt.GetValue()
        obeyind = self.indentcb.GetValue()

        ct = CodeTemplate(name, tempstr, help, obeyind)
        templates = self.GetLangTemplateDict(lastlangstr)
        templates[name] = ct

        if name != self.lastname:
            if self.lastname in templates:
                del templates[self.lastname]
            self.lastname = name

        if updatelistind is not None:
            self.listbox.SetString(updatelistind,name)

    def OnAdd(self,evt):
        ntstr = u'<' + _("New Template")
        i = 1
        for s in self.listbox.GetStrings():
            if s.startswith(ntstr):
                i+=1
        self.listbox.Append(ntstr + u'%i>' % i)

    def OnRemove(self,evt):
        self.removing = True
        name = self.listbox.GetStringSelection()
        self.listbox.Delete(self.listbox.GetSelection())
        try:
            del self.GetLangTemplateDict()[name]
        except KeyError:
            pass # ignore removal of non-existent template
        self.lastind = None
        self.UpdateTemplateinfoUI(None)
        self.removing = False

    def OnListChange(self,evt):
        if not self.removing:
            self.ApplyTemplateInfo(updatelistind=self.lastind)
        self.UpdateTemplateinfoUI(evt.GetString())
        self.lastind = evt.GetSelection()
        self.rembutton.Enable(evt.GetSelection() != -1)

    def OnLangChange(self,evt):
        self.ApplyTemplateInfo(lastlangstr=True)
        self.listbox.SetItems(self.GetTemplateNames())
        self.plugin._log("[codetemplater][info]setting %s to %s" % \
                         (self.lastlangstr,self.langchoice.GetStringSelection()))
        self.UpdateTemplateinfoUI(None)
        self.plugin.currentlang = synglob.GetIdFromDescription(self.langchoice.GetStringSelection())
        self.lastlangstr = self.langchoice.GetStringSelection()

def get_language_list():
    #ids = [v[0] for v in synglob.LANG_MAP.values()]
    ids = syntax.SyntaxIds()
    names = [synglob.GetDescriptionFromId(id) for id in ids]
    names.sort()
    return names

def load_templates():
    """
    returns a dictionary mapping template names to template objects for the
    requested lexer type
    """
    from collections import defaultdict

    wx.GetApp().GetLog()('[codetemplater][info]getting %s' % PROFILE_KEY_TEMPLATES)
    temps = Profile_Get(PROFILE_KEY_TEMPLATES)

    templd = defaultdict(lambda:dict())
    try:
        if temps is None:
            dct = load_default_templates()
            #default templates have text name keys instead of IDs like the plugin wants

            for k,v in dct.iteritems():
                templd[synglob.GetIdFromDescription(k)] = v
        else:
            #saved templates store the dict instead of objects,
            # and use language names instead of IDs
            logfunct = wx.GetApp().GetLog()
            for langname,ld in temps.iteritems():
                newld = {}
                for tempname,d in ld.iteritems():
                    logfunct('[codetemplater][info]dkeys %s'%d.keys())
                    logfunct('[codetemplater][info]dname %s'%d['name'])
                    logfunct('[codetemplater][info]templ %s'%d['templ'])
                    logfunct('[codetemplater][info]description %s'%d['description'])
                    logfunct('[codetemplater][info]indent %s'%d['indent'])
                    newld[tempname] = CodeTemplate(d['name'],d['templ'],
                                                   d['description'],d['indent'])
                templd[synglob.GetIdFromDescription(langname)] = newld

        return templd
    except:
        Profile_Del(PROFILE_KEY_TEMPLATES)
        raise
#        if len(temps)>0 and not isinstance(temps.values()[0],CodeTemplate):
#            dct = temps
#        else:
#            #if values are templates, assume we're loading an old version of the
#            #profile where all the values are python templates
#            dct = {'python':temps}

#    #saved profile/default has text name keys instead of IDs like the plugin wants
#    dd = defaultdict(lambda:dict())
#    for k,v in dct.iteritems():
#        dd[synglob.GetIdFromDescription(k)] = v
#    return dd

def load_default_templates():
    """
    loads the default set of templates (as a defaultdict)
    """
    pytemps = []
    proptemp = """
def _get${upper}(self):
\t#CUR
def _set${upper}(self,val):
\traise NotImplementedError
${same} = property(_get${upper},_set${upper},doc=None)
"""[1:] #remove first EOL
    pytemps.append(CodeTemplate('Property',proptemp,_('Convert Selection to Get/Set Property'),True))

    delproptemp = """
def _get${upper}(self):
\t#CUR
def _set${upper}(self,val):
\traise NotImplementedError
def _del${upper}(self):
\traise NotImplementedError
${same} = property(_get${upper},_set${upper},_del${upper},doc=None)
"""[1:] #remove first EOL
    pytemps.append(CodeTemplate('DelProperty',delproptemp,_('Convert Selection to Get/Set/Del Property'),True))

    getproptemp = """
@property
def ${same}(self):
\t#CUR
"""[1:] #remove first EOL
    pytemps.append(CodeTemplate('ROProperty',getproptemp,_('Convert Selection to read-only Property'),True))

    iteritemstemp = """
for k,v in ${same}.iteritems():
\t#CUR
"""[1:] #remove first EOL
    pytemps.append(CodeTemplate('Iterdict',iteritemstemp,_('Iterate over items of selected dictionary'),True))

    methodtemp = """
def ${same}(self):
\t#CUR
"""[1:] #remove first EOL
    pytemps.append(CodeTemplate('Method',methodtemp,_('Convert selection into a method'),True))

    nietemp = 'raise NotImplementedError'
    pytemps.append(CodeTemplate('NotImplementedError',nietemp,u'',True))

    pytemps = dict([(t.name,t) for t in pytemps])

    return {'python':pytemps}
