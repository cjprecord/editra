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

ID_CALC = wx.NewId()
#-----------------------------------------------------------------------------#

class Calculator(plugin.Plugin):
    """Simple Programmer's Calculator"""
    plugin.Implements(ed_main.MainWindowI)
    def PlugIt(self, parent):
        """Create the calculator and hook into the menu"""
        mw = parent
        self._log = wx.GetApp().GetLog()
        self._log("[calc] Installing calculator plugin")

        # Add Menu
        mb = mw.GetMenuBar()
        vm = mb.GetMenuByName("view")
        self._mi = vm.InsertAlpha(ID_CALC, _("Calculator"), ("Open Calculator"),
                                  wx.ITEM_CHECK, after=ed_glob.ID_PRE_MARK)

        # Event Handlers
        mw.Bind(wx.EVT_MENU, self.OnShowCalc, id=ID_CALC)

    def OnCalcClose(self):
        """Called when calculator is closed to update menu"""
        self._mi.Check(False)

    def OnShowCalc(self, evt):
        """Shows the filebrowser"""
        if evt.GetId() == ID_CALC:
            self._log("[calc] Calculator opened")
            if CalcFrame.INSTANCE is None:
                mw = wx.GetApp().GetMainWindow()
                calc = CalcFrame(mw, "Editra | Calculator", self.OnCalcClose)
                self._mi.Check(True)
                calc.Show()
            else:
                self._mi.Check(False)
                CalcFrame.INSTANCE.Destroy()
                CalcFrame.INSTANCE = None
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#
class CalcFrame(wx.MiniFrame):
    """Create the calculator. Only a single instance can exist at
    any given time.

    """
    INSTANCE = None
    def __init__(self, parent, title, close_callback):
        """Initialize the calculator frame"""
        wx.MiniFrame.__init__(self, parent, title=title, 
                              style=wx.DEFAULT_DIALOG_STYLE)
        
        # Attributes
        self.callback = close_callback
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(CalcPanel(self, ID_CALC), 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetInitialSize()
        self.CenterOnParent()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def __new__(cls, *args, **kargs):
        """Create the instance"""
        if cls.INSTANCE is None:
            cls.INSTANCE = wx.MiniFrame.__new__(cls, *args, **kargs)
        return cls.INSTANCE

    def Destroy(self):
        """Destroy the instance"""
        self.__class__.INSTANCE = None
        wx.MiniFrame.Destroy(self)

    def OnClose(self, evt):
        """Cleanup settings on close"""
        self.__class__.INSTANCE = None
        self.callback()
        evt.Skip()

class CalcPanel(wx.Panel):
    """Creates the calculators interface
    @todo: Dissable << and >> when floating values are present
    @todo: When integer values overflow display convert to scientific notation
    @todo: Keybindings to numpad and enter key

    """
    def __init__(self, parent, id_):
        """Initialiases the calculators main interface"""
        wx.Panel.__init__(self, parent, id_)

        # Attributes
        self._log = wx.GetApp().GetLog()
        self._leftop = u''
        self._rstart = False
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
        dspbox = wx.RadioBox(self, label=_("Char Display"), choices=["Ascii", "Unicode"],
                             majorDimension=2, style=wx.RA_SPECIFY_COLS)
        dspbox.SetStringSelection("Ascii")
        sizer.Add(dspbox, (4, 1), (1, 2), wx.ALIGN_LEFT)
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
                    ("<<", ">>"), (".", "^")):
            for label in row:
                b = wx.Button(self, label=label)
                gsizer2.Add(b)
        sizer.Add(gsizer2, (5, 4), (5, 2), wx.EXPAND)
        sizer.Add(self._eq, (10, 4), (1, 2), wx.EXPAND)
        sizer.Add((3, 3), (11, 0))
        self.SetSizer(sizer)
        self.SetInitialSize()

    def Compute(self):
        """Compute the result of the calculators entries"""
        try:
            if self._leftop.startswith('ERR'):
                self._leftop = 0
            rop = self._disp.GetValue()
            op = self._disp.GetOperator()
            if op == u'^':
                op = u'**'
            if self._disp.GetMode() == 'Dec' and \
               ('.' in self._leftop or '.' in rop):
                if self._leftop[-1] == '.':
                    self._leftop = self._leftop + '0'
                if rop[-1] == '.':
                    rop = rop + '0'
                if '.' not in self._leftop:
                    self._leftop = self._leftop + '.0'
                if '.' not in rop:
                    rop = rop + '.0'
            compute = "%s %s %s" % (self._leftop, op, rop)
            self._log("[calc] Calculating answer to %s" % compute)

            # Ignore empty calculation
            if not compute.strip():
                return

            # Calculate result
            result = eval(compute)

            mode = self._disp.GetMode()
            if mode == 'Hex':
                result = str(hex(result))
                result = '0x' + result.lstrip('0x').upper()
            elif mode == 'Oct':
                result = oct(result)
            else:
                pass

            # Show result
            self._disp.SetValue(str(result))
        except Exception, msg:
            self._log("[calc][err] %s" % str(msg))
            self._disp.PrintError()
            self._disp.SetOperator('')
            self._leftop = ''
            return

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
        for child in self.GetChildren():
            if isinstance(child, wx.Button):
                if child.GetLabel() == u'.':
                    keys.append(child)
                    break
        return keys

    def OnButton(self, evt):
        """Process the button clicks on the calculator"""
        e_obj = evt.GetEventObject()
        label = e_obj.GetLabel()
        
        if label == "=": # Calculate
            if self._disp.GetOperator() == u'=':
                return
            self.Compute()
            self._disp.SetOperator("=")
            self._leftop = u''
        elif label == 'AC' or (label == 'C' and e_obj not in self.GetKeys()):
            if label == 'AC':
                self._leftop = u''
                self._disp.SetOperator("")
            self._disp.SetValue("")
        else: # Just add button text to current calculation
            if label in ['*', '+', '/', '<<', '>>', '-', '^']:
                if len(self._leftop):
                    self.Compute()
                self._disp.SetOperator(label)
                tmp = self._disp.GetValue()
                if tmp.startswith('ERR'):
                    tmp = '0'
                    self._disp.SetValue(tmp)
                self._leftop = tmp
                self._rstart = True
            else:
                if self._leftop != wx.EmptyString and self._rstart:
                    self._disp.SetValue(label)
                    self._rstart = False
                elif self._disp.GetOperator() == u'=':
                    self._disp.SetValue(label)
                    self._disp.SetOperator('')
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
        if mode in ['Hex', 'Oct', 'Dec']:
            self._log("[calc] Changed to %s Mode" % mode)
            self._disp.SetMode(mode)
            if mode == "Hex":
                self.SetHexMode()
            elif mode == "Oct":
                self.SetOctMode()
            else:
                self.SetDecimalMode()
        else:
            if mode == 'Ascii':
                self._disp.SetAscii()
            else:
                self._disp.SetUnicode()

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
            if key.GetLabel() == u'.':
                key.Enable(False)
            else:
                key.Enable(True)

    def SetOctMode(self):
        """Set the calculator into octal mode"""
        for key in self.GetKeys():
            lbl = key.GetLabel()
            if lbl.isalpha() or lbl == u'.':
                key.Enable(False)
            elif lbl.isdigit() and len(lbl) == 1 and int(lbl) > 7:
                key.Enable(False)
            else:
                key.Enable(True)

#-----------------------------------------------------------------------------#

DISP_COLOR = wx.Colour(243, 248, 205) # Yellowish
class Display(wx.PyPanel):
    """Create the calculators display. The display is a custom drawn
    panel that is used to display the information that the calculator
    recieves as input and displays as output. The format of the layout
    is as shown below.
            |-------------------------------|
            |                        Value  |
            |                               |
            |Charval           Op     Mode  |
             -------------------------------
    """
    def __init__(self, parent, mode):
        """Initialize the display the mode parameter is the
        mode that the calculator is initialized with (Dec, Hex, Oct)

        """
        wx.PyPanel.__init__(self, parent)
        
        # Attributes
        self._val = u'0'    # Current value in display
        self._mode = mode   # Current mode to display
        self._op = u' '     # Operation
        self._ascii = True  # Show ascii by default
        
        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def _DrawText(self, gc, rect, font):
        """Draws the text into the display"""
        # Draw the Value
        font.SetPointSize(16)
        gc.SetFont(gc.CreateFont(font))
        v_extent = gc.GetTextExtent(self._val)
        if v_extent[0] > rect.width:
            self._val = "ERROR: Display Overflow"
            v_extent = gc.GetTextExtent(self._val)
        gc.DrawText(self._val, rect.width - (v_extent[0] + 15), 3)

        # Draw the mode and operator
        font.SetPointSize(12)
        gc.SetFont(gc.CreateFont(font))
        mode = "%s        %s" % (self._op, self._mode)
        t_extent = gc.GetTextExtent(mode)
        gc.DrawText(mode, rect.width - (t_extent[0] + 10), 
                    rect.height - (t_extent[1] + 5))

        # Draw Ascii/Unicode char equivalent of the value
        try:
            if self._mode in ['Oct', 'Hex']:
                val = self._val.lstrip('0').lstrip('0x')
                if not len(val):
                    val = '0'
            if self._mode == 'Dec':
                val = long(self._val)
            elif self._mode == 'Oct':
                val = long(val, 8)
            else:
                val = long(val, 16)
        except (ValueError, OverflowError):
            val = 0

        if self._ascii:
            asc_val = u''
            if val >= 0 and val < 255:
                asc_val = chr(val)
            chr_val = "ascii: " + asc_val.decode('latin-1')
        else:
            try:
                uni_val = unichr(val)
            except (OverflowError, ValueError):
                uni_val = u''
            chr_val = u"unicode: " + uni_val
        gc.DrawText(chr_val, 5, rect.height - (t_extent[1] + 5))

    def GetMode(self):
        """Returns the mode of the display"""
        return self._mode

    def GetOperator(self):
        """Returns the current operator"""
        return self._op

    def GetValue(self):
        """Gets the value in the control"""
        return self._val

    def GetValAsInt(self):
        """Gets the value of the display as an integer
        @note: Floating point values are rounded and only
               works for when display is in decimal mode

        """
        val = self._val
        if u'.' in val:
            tmp = val.split(u'.')
            if len(tmp) > 1:
                fval = int(tmp[0])
                if int(tmp[1]) >= 5:
                    fval = fval + 1
            else:
                if int(tmp[0]) >= 5:
                    fval = 1
                else:
                    fval = 0
        else:
            fval = int(val)
        return fval

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
        self._DrawText(gc, rect, font)

        evt.Skip()

    def PrintError(self, msg=u''):
        """Set the display to show error condition
        @todo: perhaps add more detailed messages

        """
        if msg != u'':
            self.SetValue("ERROR: %s" % msg)
        else:
            self.SetValue("ERROR")

    def SetAscii(self):
        """Set the character display to show ascii"""
        self._ascii = True
        self.Refresh()

    def SetMode(self, mode):
        """Set the mode value of the display"""
        if self._mode == 'Dec':
            tmp = self.GetValAsInt()
            if mode == 'Oct':
                val = oct(tmp)
            elif mode == 'Hex':
                val = str(hex(tmp))
                val = '0x' + val.lstrip('0x').upper()
            else:
                val = self._val
        elif self._mode == 'Oct':
            tmp = self._val.lstrip('0').rstrip('L')
            if not len(tmp):
                tmp = '0'
            if mode == 'Dec' and len(tmp):
                val = int(tmp, 8)
            elif mode == 'Hex' and len(tmp):
                val = str(hex(int(tmp, 8)))
                val = '0x' + val.lstrip('0x').upper()
            else:
                val = self._val
        else:
            tmp = self._val.lstrip('0x').rstrip('L')
            if mode == 'Dec':
                val = int(tmp, 16)
            elif mode == 'Oct':
                val = oct(int(tmp, 16))
            else:
                val = self._val
        self._val = str(val)
        self._mode = str(mode)
        self.Refresh()

    def SetOperator(self, op):
        """Sets the displays operator value"""
        self._op = str(op)
        self.Refresh()

    def SetUnicode(self):
        """Set the character display to show unicode"""
        self._ascii = False
        self.Refresh()

    def SetValue(self, val):
        """Set the value of the control"""
        tmp = str(val)
        if tmp.startswith("ERROR"):
            self._val = tmp
            self.Refresh()
            return
        if len(tmp) > 1 and self._mode == 'Dec':
            tmp = tmp.lstrip('0')
        if not len(tmp):
            tmp = u'0'
        if self._mode == 'Hex':
            tmp = tmp.lstrip('0x').lstrip('0')
            if len(tmp):
                tmp = u'0x' + tmp
            else:
                tmp = u'0x0'
        elif self._mode == 'Oct':
            tmp = u'0' + tmp.lstrip('0')
        self._val = tmp
        self.Refresh()
