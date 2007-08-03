#!/usr/bin/env python
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
"""Simple Programmer's Calculator"""
__author__ = "Cody Precord"
__version__ = "0.1"

import wx
import ed_glob
import ed_main
import ed_menu
import plugin
import util

PANE_NAME = u'Calculator'
ID_CALC = wx.NewId()
class Calculator(plugin.Plugin):
    """Simple Programmer's Calculator"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
        """Create the calculator panel and give it to the auimgr"""
        mw = parent
        self._log = wx.GetApp().GetLog()

        # Add Menu
        mb = mw.GetMenuBar()
        vm = mb.GetMenuByName("view")
        self._mi = vm.InsertAlpha(ID_CALC, _("Calculator"), ("Open Calculator"),
                                  wx.ITEM_CHECK, after=ed_glob.ID_PRE_MARK)
        # Do Layout
        calcp = CalcPanel(mw, ID_CALC)
        mw._mgr.AddPane(calcp, wx.aui.AuiPaneInfo().Name(PANE_NAME).\
                            Caption("Editra | Calculator").Bottom().Layer(0).\
                            CloseButton(True).MaximizeButton(False).\
                            BestSize(calcp.GetSize()))

        # Event Handlers
        mw.Bind(wx.EVT_MENU, self.OnShowBrowser, id=ID_CALC)
        mw.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

    def OnPaneClose(self, evt):
        """Handles when the pane is closed to update the profile"""
        pane = evt.GetPane()
        if pane.name == PANE_NAME:
            self._mi.Check(False)
        else:
            evt.Skip()

    def OnShowBrowser(self, evt):
        """Shows the filebrowser"""
        if evt.GetId() == ID_CALC:
            mw = wx.GetApp().GetMainWindow().GetFrameManager()
            pane = mw.GetPane(PANE_NAME).Hide()
            if pane.IsShown():
                pane.Hide()
                self._mi.Check(False)
            else:
                pane.Show()
                self._mi.Check(True)
            mw.Update()
        else:
            evt.Skip()

class CalcPanel(wx.Panel):
    """Creates the calculators interface"""
    def __init__(self, parent, id_):
        """XXX"""
        wx.Panel.__init__(self, parent, id_)

        # Attributes
        self._disp = Display(self, "Dec")
        self._eq = wx.Button(self, label="=")
        self._ascii = wx.StaticText(self, label="")
        self._keys = wx.GridSizer(6, 3, 1, 1)

        # Layout
        self._DoLayout()

        # Configure Controls
        self.SetDecimalMode()
        self._eq.SetDefault()

        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_RADIOBOX, self.OnRadioBox)

    def _DoLayout(self):
        """Layout the calculator"""
        sizer = wx.GridBagSizer(1, 2)
        sizer.AddMany([((3, 3), (0, 0)), ((3, 3), (0, 6)), 
                       (self._disp, (1, 1), (3, 5), wx.EXPAND)])
#         sbox = wx.StaticBox(self, label="ASCII")
#         sbsizer = wx.StaticBoxSizer(sbox)
#         sbsizer.Add(self._ascii)
#         sizer.Add(sbsizer, (4, 1), (1, 1), wx.ALIGN_LEFT | wx.EXPAND)
        radbox = wx.RadioBox(self, label=_("Mode"), choices=["Hex", "Oct", "Dec"], 
                             majorDimension=3, style=wx.RA_SPECIFY_COLS)
        radbox.SetStringSelection("Dec")
        sizer.Add(radbox, (4, 3), (1, 3), wx.ALIGN_RIGHT)
        for row in (("D", "E", "F"), ("A", "B", "C"), ("7", "8", "9"),
                    ("4", "5", "6"), ("1", "2", "3"), ("FF", "0", "00")):
            for label in row:
                b = wx.Button(self, label=label)
                self._keys.Add(b)
        sizer.Add(self._keys, (5, 1), (6, 3), wx.EXPAND)
        gsizer2 = wx.GridSizer(6, 2, 1, 1)
        for row in (("AC", "C"), ("/", "-"), ("*", "+"), 
                    ("<<", ">>"), ("2's", "1's")):
            for label in row:
                b = wx.Button(self, label=label)
                gsizer2.Add(b)
        sizer.Add(gsizer2, (5, 4), (5, 2), wx.EXPAND)
        sizer.Add(self._eq, (10, 4), (1, 2), wx.EXPAND)
        sizer.Add((3, 3), (11, 0))
        self.SetSizer(sizer)
        self.SetInitialSize()

    def GetKeys(self):
        """Returns a list of buttons that are used for input
        of values.
        
        """
        sitems = self._keys.GetChildren()
        keys = list()
        for item in sitems:
            win = item.GetWindow()
            if win is not None:
                keys.append(win)
        return keys

    def OnButton(self, evt):
        """Process the button clicks on the calculator"""
        label = evt.GetEventObject().GetLabel()
        
        if label == "=": # Calculate
            try:
                compute = self._disp.GetValue()
                # Ignore empty calculation
                if not compute.strip():
                    return

                # Calculate result
                result = eval(compute)

                # Show result
                self._disp.SetValue(str(result))
            except Exception, e:
                wx.LogError(str(e))
                return
        elif label in ["AC", "C"]: # Clear
            self._disp.SetValue("")
        elif label == "1's": # 1's compliment
            pass
        elif label == "2's": # 2's compliment
            pass
        else: # Just add button text to current calculation
            if label in ['*', '+', '/', '<<', '>>', '-']:
                self._disp.SetOperator(label)
            else:
                self._disp.SetValue(self._disp.GetValue() + label)
            self._eq.SetFocus() # Set the [=] button in focus

    def OnPaint(self, evt):
        """Paints the calculators background"""
        dc = wx.PaintDC(self)
        rect = self.GetRect()
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)))
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
        evt.Skip()

    def OnRadioBox(self, evt):
        """Switches the calculators mode to the one selected
        in the RadioBox.

        """
        e_id = evt.GetInt()
        e_obj = evt.GetEventObject()
        mode = e_obj.GetItemLabel(e_id)
        self._disp.SetMode(mode)
        if mode == "Hex":
            self.SetHexMode()
        elif mode == "Oct":
            self.SetOctMode()
        else:
            self.SetDecimalMode()

    def SetDecimalMode(self):
        """Set the calculator to decimal mode"""
        for key in self.GetKeys():
            lbl = key.GetLabel()
            if lbl.isalpha():
                key.Enable(False)
            else:
                key.Enable(True)

    def SetHexMode(self):
        """Set the calculator into hex mode"""
        for key in self.GetKeys():
            key.Enable(True)

    def SetOctMode(self):
        """Set the calculator into octal mode"""
        for key in self.GetKeys():
            lbl = key.GetLabel()
            if lbl.isalpha():
                key.Enable(False)
            elif lbl.isdigit() and len(lbl) == 1 and int(lbl) > 7:
                key.Enable(False)
            else:
                key.Enable(True)

DISP_COLOR = wx.Colour(243, 248, 205)
class Display(wx.PyPanel):
    """Create the calculators display"""
    def __init__(self, parent, mode):
        """Initialize the display"""
        wx.PyPanel.__init__(self, parent)#, style=wx.SUNKEN_BORDER)
        
        # Attributes
        self._val = u'0'    # Current value in display
        self._mode = mode   # Current mode to display
        self._op = u' '     # Operation
        
        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def _DrawMode(self, gc, rect, font):
        """Draws the calculators mode and current opperator to the display"""
        font.SetPointSize(12)
        gc.SetFont(gc.CreateFont(font))
        mode = "%s        %s" % (self._op, self._mode)
        t_extent = gc.GetTextExtent(mode)
        gc.DrawText(mode, rect.width - (t_extent[0] + 10), rect.height - (t_extent[1] + 5))

    def _DrawValue(self, gc, rect, font):
        """Draws the value text in the upper right corner of the display
        using the given GraphicsContext.
        
        """
        font.SetPointSize(16)
        gc.SetFont(gc.CreateFont(font))
        t_extent = gc.GetTextExtent(self._val)
        gc.DrawText(self._val, rect.width - (t_extent[0] + 15), 3)

    def GetMode(self):
        """Returns the mode of the display"""
        return self._mode

    def GetOperator(self):
        """Returns the current operator"""
        return self._op

    def GetValue(self):
        """Gets the value in the control"""
        return self._val

    def OnPaint(self, evt):
        """Paint the display and its values"""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        rect = self.GetRect()
        w = rect.width
        h = rect.height

        gc.SetBrush(wx.Brush(DISP_COLOR))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, 0, w - 3, h - 3, 5)
        
        gc.SetBrush(wx.TRANSPARENT_BRUSH)
        color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVEBORDER)
        color = util.AdjustColour(color, -70)
        gc.SetPen(wx.Pen(color, 2))
        gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, 5)

        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        gc.SetPen(wx.BLACK_PEN)
        self._DrawValue(gc, rect, font)
        self._DrawMode(gc, rect, font)

        evt.Skip()

    def SetMode(self, mode):
        """Set the mode value of the display"""
        self._mode = str(mode)
        self.Refresh()

    def SetOperator(self, op):
        """Sets the displays operator value"""
        self._op = str(op)
        self.Refresh()

    def SetValue(self, val):
        """Set the value of the control"""
        self._val = str(val).lstrip('0')
        self.Refresh()
