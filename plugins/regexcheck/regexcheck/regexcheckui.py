###############################################################################
# Name: regexcheckui.py                                                       #
# Purpose: RegexCheck plugin                                                  #
# Author: Erik Tollerud <erik.tollerud@gmail.com>                             #
# Copyright: (c) 2010 Erik Tollerud <erik.tollerud@gmail.com>                 #
# License: wxWindows License                                                  #
###############################################################################

"""UI elements for the RegexCheck plugin."""
__author__ = "Erik Tollerud"
__version__ = "0.1"

#-----------------------------------------------------------------------------#

import wx      

_ = wx.GetTranslation

#color sequence from kiki 
COLORS = ["#0000AA", "#00AA00", "#FFAA55", "#AA0000", "#00AAAA", "#AA00AA", 
          "#AAAAAA", "#0000FF", "#00FF00", "#00FFFF", "#FF0000", "#DDDD00", 
          "#FF00FF", "#AAAAFF", "#FF55AA", "#AAFF55", "#FFAAAA", "#55AAFF", 
          "#FFAAFF", "#000077", "#007700", "#770000", "#007777", "#770077", 
          "#777700"]
          
          

class RegexCheckPanel(wx.Panel):
    """The Panel for RegexCheck"""
    
    def __init__(self,parent,*args,**kwargs):
        wx.Panel.__init__(self,parent,*args,**kwargs)
        
        #build UI elements
        toplabel = wx.StaticText(self, -1, _("Regular Expression:"))
        self.regextextctrl = wx.TextCtrl(self,-1,"")  
        
        
        insertbutton = wx.Button(self,-1,_("Insert Expression at Cursor"))
        self.rawcheckbox = wx.CheckBox(self,-1,_("Raw string?"))
        self.rawcheckbox.SetValue(True)
        self.strcharsingle = wx.CheckBox(self,-1,_("Use ' instead of \"?"))
        self.strcharsingle.SetValue(True)
        
        testbutton = wx.Button(self,-1,_("Test regex on selected text"))
        #self.matchchoices = wx.Choice(self,-1,choices=[_("Match"),_("Search"),_("Findall")])
        self.matchchoices = wx.Choice(self,-1,choices=[_("Match",_("Search"))])
        flagbutton = wx.Button(self,-1,_("Regex Flags..."))
        
        #flaglabel = wx.StaticText(self, -1, _("Compilation Flags:"))
        flags = [
        "IGNORECASE(I)",
        "LOCALE(L)",
        "MULTILINE(M)",
        "DOTALL(S)",
        "UNICODE(U)",
        "VERBOSE(X)"]
        self.flags = dict([(s,False) for s in flags])
        #self.flagcheckboxes = [wx.CheckBox(self,-1,f) for f in flags]
        
        outlabel = wx.StaticText(self, -1, _("Output:"))
        self.outputtextctrl = wx.TextCtrl(self,-1,"",style=wx.TE_MULTILINE)
        self.outputtextctrl.SetEditable(False)
        self.outputtextctrl.SetBackgroundColour(outlabel.GetBackgroundColour())
        
        #bind events
        testbutton.Bind(wx.EVT_BUTTON, self.OnTest)
        insertbutton.Bind(wx.EVT_BUTTON, self.OnInsert)
        flagbutton.Bind(wx.EVT_BUTTON, self.OnFlag)
        
        #build sizers and add elements
        
        basesizer = wx.BoxSizer(wx.VERTICAL)
        
        resizer = wx.BoxSizer(wx.HORIZONTAL)
        resizer.Add(toplabel, 0, wx.ALIGN_CENTRE|wx.ALL,border=2)
        resizer.Add(self.regextextctrl, 1, wx.ALIGN_LEFT|wx.ALL,border=2)
        basesizer.Add(resizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL)
        
        testsizer = wx.BoxSizer(wx.HORIZONTAL)
        testsizer.Add(testbutton, 0, wx.ALIGN_LEFT|wx.ALL,border=2)
        testsizer.Add(self.matchchoices, 0, wx.ALIGN_LEFT|wx.ALL,border=2)
        testsizer.Add(flagbutton, 0, wx.ALIGN_LEFT|wx.ALL,border=2)
        basesizer.Add(testsizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL)
        
        outsizer = wx.BoxSizer(wx.HORIZONTAL)
        outsizer.Add(outlabel, 0, wx.ALIGN_CENTRE|wx.ALL,border=2)
        outsizer.Add(self.outputtextctrl, 1, wx.GROW|wx.ALIGN_LEFT|wx.ALL,border=2)
        basesizer.Add(outsizer, 1, wx.GROW|wx.ALIGN_CENTRE|wx.ALL)
        
        insertsizer = wx.BoxSizer(wx.HORIZONTAL)
        insertsizer.Add(insertbutton, 0, wx.ALIGN_LEFT|wx.ALL,border=2)
        insertsizer.Add(self.rawcheckbox, 0, wx.ALIGN_LEFT|wx.ALL,border=2)
        insertsizer.Add(self.strcharsingle, 0, wx.ALIGN_LEFT|wx.ALL,border=2)
        basesizer.Add(insertsizer, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL)
        
        self.SetSizer(basesizer)
        basesizer.Fit(self)
        
        
        
    def GetStringChar(self):
        return "'" if self.strcharsingle else '"'
        
        
    def GetFormattedRegex(self):
        text = self.regextextctrl.GetValue()
        strchar = self.GetStringChar()
        if self.rawcheckbox.GetValue():
            text = "r" + strchar + text.replace(strchar,'\\'+strchar) + strchar
        else:
            text = strchar + text.replace("\\","\\\\") + strchar
        return text
        
    def OnTest(self,evt):
        import re
        retext = self.regextextctrl.GetValue()
        wx.GetApp().GetLog()("[regexcheck][info]trying re "+retext)
        
        flags = 0
        for cb,b in self.flags.iteritems():
            if b:
                flagname = cb.GetLabel().split("(")[0].strip()
                flagval = getattr(re,flagname)
                flags = flags|flagval
        wx.GetApp().GetLog()("[regexcheck][info]re flags "+str(flags))
        if retext.strip() == "":
            self.outputtextctrl.SetValue(_("No regex Entered"))
        else:
            try:
                current_buffer = wx.GetApp().GetCurrentBuffer()
                matchtext = current_buffer.GetSelectedText()
                
                sel = self.matchchoices.GetSelection()
                if sel == 2: #find all
                    matchlocs = []
                    for m in re.finditer(retext,matchtext,flags):
                        matchlocs.extend(self.FindMatchGroups(m,matchtext[m.start():m.end()]))
                    if len(matchlocs)>1: #remove final end
                        del matchlocs[-1]
                    self.ApplyOutput(matchlocs,matchtext)
                else:
                    if sel == 1: #search
                        match = re.search(retext,matchtext,flags)
                    else: #match
                        assert sel==0,"invalid choice option index %i"%sel
                        match = re.match(retext,matchtext,flags)
                    if match is None:
                        matchlocs = []
                    else:
                        matchlocs = self.FindMatchGroups(match,matchtext)
                    self.ApplyOutput(matchlocs,matchtext)
                        
            except re.error,e:
                self.outputtextctrl.SetValue(_("Regex compilation error: %s"%e.args))
                
    def FindMatchGroups(self,matchobj,text):
        """
        returns a sequence of tuples of (groupname,groupstartind,groupendind)
        """
        grps = []
        grps.append(("0",matchobj.start(),matchobj.end()))
        
        #create (grpnum,start,end) sequence
        for i,match in enumerate(matchobj.groups()):
            if match is not None:
                span = matchobj.span(i+1)
                grps.append((str(i+1),span[0],span[1]))
        
        #replace named groups with the correct name
        for k in matchobj.groupdict():
            span = matchobj.span(k)
            for i,(n,s,e) in enumerate(grps):
                if span[0]==s and span[1]==e:
                    break
            else:
                i = None
            if i is not None:
                grps[i] = (k,s,e)
        
        return grps
    def ApplyOutput(self,matchlocs,matchtext):
        import operator
        
        if len(matchlocs)==0:
            self.outputtextctrl.SetValue(_("No matches"))
        else:
            indstrs = []
            colori = 0
            for name,start,end in matchlocs[::-1]:
                indstrs.append((start,"(",colori))
                indstrs.append((end,")"+name,colori))
                colori += 1
            
            #see _str_3tuple_cmp for description of sort
            indstrs.sort(cmp=_str_3tuple_cmp)
            
            curri = 0
            strlist = []
            colors = []
            for ind,nm,color in indstrs:
                strlist.append(matchtext[curri:ind])
                colors.append(None)
                strlist.append(nm)
                colors.append(color)
                curri = ind
            #flip colors order to be forward again
            maxc = max(colors)
            colors = [None if c is None else maxc-c for c in colors]
                
            strlist.append(matchtext[curri:])
            self.outputtextctrl.SetValue("".join(strlist))
            
            curri = 0
            oldfont = self.outputtextctrl.GetFont()
            biggerfont = wx.Font(
                    oldfont.GetPointSize()+3,
                    oldfont.GetFamily(),
                    oldfont.GetStyle(),
                    oldfont.GetWeight())
            smallerfont = wx.Font(
                    oldfont.GetPointSize()-3,
                    oldfont.GetFamily(),
                    oldfont.GetStyle(),
                    oldfont.GetWeight())
            for substr,color in zip(strlist,colors):
                if color is not None:
                    self.outputtextctrl.SetStyle(curri,curri+1,wx.TextAttr(self.ColorCycle(color),wx.NullColour, biggerfont))
                    if len(substr)>1:
                        self.outputtextctrl.SetStyle(curri+1,curri+len(substr),wx.TextAttr(self.ColorCycle(color),wx.NullColour, smallerfont))
                curri += len(substr)
                
    def ColorCycle(self,colori):
        return COLORS[colori%len(COLORS)]
    
    def OnInsert(self,evt):
        retext = self.GetFormattedRegex()
        wx.GetApp().GetLog()("[regexcheck][info]inserting "+retext)
        
        current_buffer = wx.GetApp().GetCurrentBuffer()
        seltext = current_buffer.GetSelectedText()
        if seltext != "":
            current_buffer.DeleteBack()
        
        if retext.strip() != "":
            current_buffer.AddText(retext)
            
    def OnFlag(self,evt):
        dlg = wx.MultiChoiceDialog(self,_("Regex Compilation Flags"),
                                  _("Regex Compilation Flags"),
                                  self.flags.keys())
        dlg.SetSelections([i for i,b in enumerate(self.flags.values()) if b])
        
        
        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            ks = self.flags.keys()
            for k in ks:
                self.flags[k] = False
            for s in selections:
                self.flags[ks[s]] = True

        dlg.Destroy()
        
def _str_3tuple_cmp(e1,e2):
    """
    compares two 3-tuples, and return sorting order such that sort is by the
    first element or if the first elemnt matches, by the 3rd element in 
    reversed order, unless the second element contains closing parentheses
    """
    if e1[0]>e2[0]:
        return 1
    elif e1[0]<e2[0]:
        return -1
    else:
        swap =  ')' in e1[1] and ')' in e2[1]
        
        if e1[2]>e2[2]:
            return 1 if swap else -1
        elif e1[2]<e2[2]:
            return -1 if swap else 1 
        else:
            return 0
