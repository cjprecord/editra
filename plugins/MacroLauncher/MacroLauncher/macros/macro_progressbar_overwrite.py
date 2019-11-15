# -*- coding: utf-8 -*-

__name__ = 'progressbar'
__type__ = 'example'
__desc__ = 'Shows a progressbar'

import  wx

def run(txtctrl=None, **kwargs):
  TestPanel(txtctrl, 1).OnButton(1)

class TestPanel(wx.Panel):
    def __init__(self, parent, log):
        self.log = log
        wx.Panel.__init__(self, parent, -1)

        #b = wx.Button(self, -1, "Create and Show a ProgressDialog", (50,50))
        #self.Bind(wx.EVT_BUTTON, self.OnButton, b)


    def OnButton(self, evt):
        max = 100
        dlg = wx.ProgressDialog("Macro: %s" % __name__,
                               "%s" % __desc__,
                               maximum=max,
                               parent=self,
                               style = wx.PD_CAN_ABORT
                                | wx.PD_APP_MODAL
                                #| wx.PD_CAN_SKIP
                                #| wx.PD_ELAPSED_TIME
                                #| wx.PD_SMOOTH
                                #| wx.PD_ESTIMATED_TIME
                                #| wx.PD_REMAINING_TIME
                                )

        keepGoing = True
        skip = False
        count = 0

        while keepGoing and not skip:
            wx.MilliSleep(50)
            (keepGoing, skip) = dlg.Pulse("Half-update!")

        dlg.Destroy()
