###############################################################################
# Name: __init__.py                                                           #
# Purpose: Plugin to add the ability to submit code to thedailywtf.com        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2010 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
"""Adds "Submit to TDWTF" to the editor right click menu"""
__author__ = "Cody Precord"
__version__ = "0.1"

#-----------------------------------------------------------------------------#
# Imports
import wx

# Editra Imports
import util
import iface
import plugin
import ed_msg
import eclib
import ebmlib

#-----------------------------------------------------------------------------#
# Globals
from wx.lib.embeddedimage import PyEmbeddedImage

WTFICON = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAAZiS0dE"
    "AP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9oLCw8rCzVeQCUAAAG6"
    "SURBVDjLpdNPaM9xHMfxx/e33/p91mwtyZh2mMZlB9v3ICWSmFwnJxEnJy7KTVErl5G7g5I/"
    "KVzkRhxMkr6yaVGmuKiFmbF9SPs57DN9+yWRd30O7/fn9Xl9np/39/3lPyODIoS1OIIOzGET"
    "JjGcxzi2JC5CWIE+dGIK09UihAy7MYg2zGM9uvGyCOF5HuNC8tiOayWAIitCGMKNP1DeTGs8"
    "6XrLBlXsbzjwMVGsSflQwt6MBw0GKtiHUyl/hX48ajD9kQy3lGqzuF/JY5zLYzyJHmzDaewp"
    "Cd9jAlWEUn0clyulQi8uJKKlWMBVnEgmF1P9GYYxWYGJ1soyHMMO3EuiW9iF4+lprViV9jbg"
    "dR7jTBU+tCzP2ma/zCxkv0iu5zHuLTehCKETG/EZMc3LYlzq62u+c+Dg6k9v34R/mcIihK4M"
    "HmdZT3OtNlinHS24m8c42iDuxvlE0JX69bQKTbXaobrsKPWphDeP0YYLB7EVT9JMVLCzmobh"
    "XV29FeswXfk98eFEtzLlV/IYv1agvnjjmdT52x3fvo8snXoxPpYtxJhhBOfSp4WH5b+xH00Y"
    "yGgfiPHs3zbyJ27AfbbT4s3EAAAAAElFTkSuQmCC")

SUBMIT_TPL = """<Submit xmlns=\"http://thedailywtf.com/\">
<name>%s</name>
<emailAddress>%s</emailAddress>
<subject>%s</subject>
<comments>%s</comments>
<codeSubmission>%s</codeSubmission>
<doNotPublish>%s</doNotPublish>
</Submit>
"""

_ = wx.GetTranslation

# Register Plugin Translation Catalogs
try:
    wx.GetApp().AddMessageCatalog('dailywtf', __name__)
except:
    pass

#-----------------------------------------------------------------------------#

ID_TDWTF = wx.NewId()
class TheDailyWtf(plugin.Plugin):
    """Adds Submit to The DailyWtf context menu"""
    plugin.Implements(iface.MainWindowI)
    def PlugIt(self, parent):
        util.Log("[thedailywtf][info] PlugIt called")
        # Note: multiple subscriptions are ok it will only be 
        #       called once.
        ed_msg.Subscribe(self.OnContextMenu, ed_msg.EDMSG_UI_STC_CONTEXT_MENU)

    def GetMenuHandlers(self):
        """Not needed by this plugin"""
        return list()

    def GetUIHandlers(self):
        """Not needed by this plugin"""
        return list()

    def GetMinVersion(self):
        return u"0.5.86"

    #---- Implementation ----#

    @staticmethod
    def OnContextMenu(msg):
        """EdMsg Handler for customizing the buffers context menu"""
        menumgr = msg.GetData()
        menu = menumgr.GetMenu()
        if menu:
            menu.AppendSeparator()
            item = menu.Append(ID_TDWTF, _("Submit to TDWTF"))
            item.SetBitmap(WTFICON.GetBitmap())
            buf = menumgr.GetUserData('buffer')
            if buf:
                # Only enable the menu item if there is a selection in the
                # buffer.
                hassel = buf.HasSelection()
                item.Enable(hassel)
            menumgr.AddHandler(ID_TDWTF, OnSubmit)

#-----------------------------------------------------------------------------#

def OnSubmit(buff, evt):
    """Callback for buffer context menu event.
    Opens the submission dialog
    @param buff: EditraStc
    @param evt: MenuEvent

    """
    if evt.GetId() == ID_TDWTF:
        app = wx.GetApp()
        dlg = SubmitDialog(buff, 
                           title=_("Submit your WTF"),
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        dlg.SetSenderName(wx.GetUserName())
        dlg.SetSnippetField(buff.GetSelectedText())
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            # send it
            info = dlg.GetSubmissionInfo()
            dlg.Destroy()
            # Need to encode as UTF-8
            try:
                info = [data.encode('utf-8') for data in info]
            except UnicodeEncodeError, msg:
                util.Log("[dailywtf][err] %s" % msg)
                return
            host = "thedailywtf.com"
            bodytxt = SUBMIT_TPL % tuple(info)
            message = ebmlib.SOAP12Message(host, "/SubmitWTF.asmx", bodytxt,
                                           "http://thedailywtf.com/Submit")
            message.Send()
            # TODO check return code to make sure it was submitted
        else:
            dlg.Destroy() # Canceled
    else:
        evt.Skip()

#-----------------------------------------------------------------------------#

class SubmitDialog(eclib.ECBaseDlg):
    def __init__(self, parent, *args, **kwargs):
        """Email submission dialog for sending a code snippet
        to the wtf.com.

        """
        super(SubmitDialog, self).__init__(parent, *args, **kwargs)

        # Attributes
        panel = SubmitPanel(self)

        # Setup
        self.SetIcon(WTFICON.GetIcon())
        self.SetPanel(panel)
        self.SetInitialSize((300, 350))

class SubmitPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(SubmitPanel, self).__init__(parent, *args, **kwargs)

        # Attributes
        statbox = wx.StaticBox(self, label=_("Submitter Info"))
        self._hdrsz = wx.StaticBoxSizer(statbox, wx.VERTICAL)
        self._name = wx.TextCtrl(self)
        self._email = wx.TextCtrl(self)
        self._subject = wx.TextCtrl(self)
        self._msg = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self._snippet = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self._submit = wx.Button(self, wx.ID_OK, label=_("Submit"))
        self._nopubcb = wx.CheckBox(self, label=_("Please Don't Publish"))
        tip = _("Even though I'm sure you'd do a fine job of anonymizing,\n"
                "I just wanted to be able to say that I sent code to\n"
                "The Daily WTF. Yes, I realize this hardly counts,\n"
                "but it's better than wallowing in my own misery.")
        self._nopubcb.SetToolTipString(tip)
        self._ctrls = (self._name, self._email, self._subject,
                       self._msg, self._snippet)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, self._submit)

    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        headsz = wx.FlexGridSizer(3, 2, 3, 3)
        headsz.AddGrowableCol(1, 1)
        for lbl, field in ((_("Your Name: "), self._name),
                           (_("Your E-mail: "), self._email),
                           (_("Subject: "), self._subject)):
            label = wx.StaticText(self, label=lbl)
            headsz.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)
            headsz.Add(field, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 2)
        self._hdrsz.Add(headsz, 0, wx.EXPAND|wx.ALL, 5)

        sizer.Add(self._hdrsz, 0, wx.EXPAND|wx.ALL, 8)

        sizer.Add(wx.StaticText(self, label=_("Message:")),
                  0, wx.TOP|wx.LEFT, 5)
        sizer.Add(self._msg, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(wx.StaticText(self, label=_("Code Snippet:")),
                  0, wx.TOP|wx.LEFT, 5)
        sizer.Add(self._snippet, 1, wx.EXPAND|wx.ALL, 5)
        # Layout the bottom row and button
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self._nopubcb, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        hsizer.AddStretchSpacer()
        hsizer.Add(self._submit, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        sizer.Add(hsizer, 0, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(sizer)

    def OnUpdateUI(self, event):
        if event.GetEventObject() is self._submit:
            for ctrl in self._ctrls:
                val = ctrl.GetValue()
                if not val:
                    event.Enable(False)
                    break
            else:
                event.Enable(True)
        else:
            event.Skip()

    @eclib.expose(SubmitDialog)
    def GetSubmissionInfo(self):
        """Get the submission info
        @return: tuple(name, email, subject, msg, code, dontPublish)

        """
        values = list()
        for ctrl in self._ctrls:
            value = ctrl.GetValue()
            if isinstance(value, bool):
                value = unicode(value).lower()
            values.append(value)
        pub = self._nopubcb.GetValue()
        values.append(unicode(pub).lower())
        return tuple(values)

    @eclib.expose(SubmitDialog)
    def SetSnippetField(self, snippet):
        self._snippet.SetValue(snippet)

    @eclib.expose(SubmitDialog)
    def SetSenderName(self, sender):
        self._name.SetValue(sender)

    @eclib.expose(SubmitDialog)
    def SetSenderEmail(self, email):
        self._email.SetValue(email)
