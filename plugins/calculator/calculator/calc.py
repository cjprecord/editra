###############################################################################
# Name: calc.py                                                               #
# Purpose: Simple Calculator                                                  #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: calc.py
AUTHOR: Cody Precord
LANGUAGE: Python
SUMMARY:
Provides a simple calculator with Oct/Hex/Decimal modes of operation

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: calc.py 850 2009-05-01 00:24:27Z CodyPrecord $"
__revision__ = "$Revision: 850 $"

#--------------------------------------------------------------------------#
# Dependancies
import wx

#--------------------------------------------------------------------------#
ID_CALC = wx.NewId()
_ = wx.GetTranslation

DISP_COLOR = wx.Colour(243, 248, 205) # Yellowish
KEY_MAP = { wx.WXK_NUMPAD0 : '0', wx.WXK_NUMPAD1 : '1', wx.WXK_NUMPAD2 : '2',
            wx.WXK_NUMPAD3 : '3', wx.WXK_NUMPAD4 : '4', wx.WXK_NUMPAD5 : '5',
            wx.WXK_NUMPAD6 : '6', wx.WXK_NUMPAD1 : '7', wx.WXK_NUMPAD0 : '8',
            wx.WXK_NUMPAD1 : '9', wx.WXK_NUMPAD_ADD : '+',
            wx.WXK_NUMPAD_DECIMAL : '.', wx.WXK_NUMPAD_DIVIDE : '/',
            wx.WXK_NUMPAD_EQUAL : '=', wx.WXK_NUMPAD_MULTIPLY : '*',
            wx.WXK_NUMPAD_SUBTRACT : '-', wx.WXK_SUBTRACT : '-',
            wx.WXK_ADD : '+', wx.WXK_DECIMAL : '.', wx.WXK_DIVIDE : '/',
            wx.WXK_MULTIPLY : '*'}

HEX_MODE = 0
OCT_MODE = 1
DEC_MODE = 2
MODE_MAP = { HEX_MODE : "Hex", OCT_MODE : "Oct", DEC_MODE : "Dec" }

#--------------------------------------------------------------------------#

def ShowCalculator(evt):
    """Shows the calculator"""
    if evt.GetId() == ID_CALC:
        if CalcFrame.INSTANCE is None:
            cframe = CalcFrame(None, _("Editra | Calculator"))
            cframe.Show()
        else:
            CalcFrame.INSTANCE.Destroy()
            CalcFrame.INSTANCE = None
    else:
        evt.Skip()

def UpdateMenu(evt):
    """Update the check mark in the menus of the windows"""
    evt.Check(CalcFrame.INSTANCE is not None)

#-----------------------------------------------------------------------------#

class CalcFrame(wx.MiniFrame):
    """Create the calculator. Only a single instance can exist at
    any given time.

    """
    INSTANCE = None
    def __init__(self, parent, title):
        """Initialize the calculator frame"""
        wx.MiniFrame.__init__(self, parent, title=title,
                              style=wx.DEFAULT_DIALOG_STYLE)

        # Attributes
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
        CalcFrame.INSTANCE = None
        evt.Skip()

#-----------------------------------------------------------------------------#
ID_CHAR_DSP = wx.NewId()

class CalcPanel(wx.PyPanel):
    """Creates the calculators interface
    @todo: Dissable << and >> when floating values are present
    @todo: When integer values overflow display convert to scientific notation
    @todo: Keybindings to numpad and enter key

    """
    def __init__(self, parent, id_):
        """Initialiases the calculators main interface"""
        wx.PyPanel.__init__(self, parent, id_)

        # Attributes
        self._log = LogFunction
        self._leftop = u''
        self._rstart = False
        self._disp = Display(self, DEC_MODE)
        self._eq = wx.Button(self, label="=")
        self._ascii = wx.StaticText(self, label="")
        self._keys = wx.GridSizer(6, 3, 2, 2)

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
        sizer = wx.GridBagSizer(2, 2)

        # Character display mode
        sizer.AddMany([((3, 3), (0, 0)), ((3, 3), (0, 6)),
                       (self._disp, (1, 1), (3, 5), wx.EXPAND)])
        dspbox = wx.RadioBox(self, ID_CHAR_DSP, label=_("Char Display"),
                             choices=[_("Ascii"), _("Unicode")],
                             majorDimension=2, style=wx.RA_SPECIFY_COLS)
        dspbox.SetSelection(0)

        # Mode Selection
        sizer.Add(dspbox, (4, 1), (1, 2), wx.ALIGN_LEFT)
        radbox = wx.RadioBox(self, label=_("Mode"),
                             choices=[_("Hex"), _("Oct"), _("Dec")],
                             majorDimension=3, style=wx.RA_SPECIFY_COLS)
        radbox.SetSelection(DEC_MODE)
        sizer.Add(radbox, (4, 3), (1, 3), wx.ALIGN_RIGHT)

        # Make Buttons
        for row in (("D", "E", "F"), ("A", "B", "C"), ("7", "8", "9"),
                    ("4", "5", "6"), ("1", "2", "3"), ("FF", "0", "00")):
            for label in row:
                self._keys.Add(wx.Button(self, label=label))

        sizer.Add(self._keys, (5, 1), (6, 3), wx.EXPAND)
        gsizer2 = wx.GridSizer(6, 2, 2, 2)
        for row in (("AC", "C"), ("/", "-"), ("*", "+"),
                    ("<<", ">>"), (".", "^")):
            for label in row:
                gsizer2.Add(wx.Button(self, label=label))

        sizer.Add(gsizer2, (5, 4), (5, 2), wx.EXPAND)
        sizer.Add(self._eq, (10, 4), (1, 2), wx.EXPAND)
        sizer.Add((3, 3), (11, 0))
        self.SetSizer(sizer)
        self.SetInitialSize()

    def AcceptsFocus(self):
        """Allow this window to accept keyboard focus"""
        return True

    def Compute(self):
        """Compute the result of the calculators entries"""
        try:
            if self._leftop.startswith(_('Error')):
                self._leftop = 0
            rop = self._disp.GetValue()
            op = self._disp.GetOperator()
            if op == u'^':
                op = u'**'
            if self._disp.GetMode() == DEC_MODE and \
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
            self._log("[calc][info] Calculating answer to %s" % compute)

            # Ignore empty calculation
            if not compute.strip():
                return

            # Calculate result
            result = eval(compute)

            mode = self._disp.GetMode()
            if mode == HEX_MODE:
                result = str(hex(result))
                result = '0x' + result.lstrip('0x').upper()
            elif mode == OCT_MODE:
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

        if label == "=":
            # Process Values
            cop = self._disp.GetOperator().strip()
            if cop == u'=' or not len(cop):
                return
            self.Compute()
            self._disp.SetOperator("=")
            self._leftop = u''
        elif label == 'AC' or (label == 'C' and e_obj not in self.GetKeys()):
            # Clear display
            if label == 'AC':
                self._leftop = u''
                self._disp.SetOperator("")
            self._disp.SetValue("")
        else:
            # Send values to display
            if label in ['*', '+', '/', '<<', '>>', '-', '^']:
                self._disp.SetOperator(label)
                self._disp.ClearError() # Clear any errors
                tmp = self._disp.GetValue()
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
        e_obj = evt.GetEventObject()
        mode = evt.GetInt()
        if evt.GetId() != ID_CHAR_DSP:
            # Change calculator the mode
            self._log("[calc][evt] Changed to %s Mode" % e_obj.GetString(mode))
            self._disp.SetMode(mode)
            if mode == HEX_MODE:
                self.SetHexMode()
            elif mode == OCT_MODE:
                self.SetOctMode()
            else:
                self.SetDecimalMode()
        else:
            # Change the character display mode
            if mode == 0:
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
                break
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

class Display(wx.PyPanel):
    """Create the calculators display. The display is a custom drawn
    panel that is used to display the information that the calculator
    recieves as input and displays as output. The format of the layout
    is as shown below.
            |-------------------------------|
            |                        Value  |
            |                               |
            |Charval           Op     Mode  |
            |-------------------------------|

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
        self._error = False # Is an error displayed

        # Setup
        self.SetMinSize((250, 60))

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBG)

    def _DrawText(self, gc, rect, font):
        """Draws the text into the display"""
        # Draw the Value
        font.SetPointSize(16)
        gc.SetFont(font)
        v_extent = gc.GetTextExtent(self._val)
        if v_extent[0] > rect.width:
            self._val = _("Error: Display Overflow")
            v_extent = gc.GetTextExtent(self._val)
        gc.DrawText(self._val, rect.width - (v_extent[0] + 15), 3)

        # Draw the mode and operator
        font.SetPointSize(12)
        gc.SetFont(font)
        mstr = _(MODE_MAP.get(self._mode, "Dec"))
        mode = "%s        %s" % (self._op, mstr)
        t_extent = gc.GetTextExtent(mode)
        gc.DrawText(mode, rect.width - (t_extent[0] + 12),
                    rect.height - (t_extent[1] + 5))

        # Draw Ascii/Unicode char equivalent of the value
        try:
            val = '0'
            if self._mode in [OCT_MODE, HEX_MODE]:
                val = self._val.lstrip('0').lstrip('0x')
                if not len(val):
                    val = '0'

            if self._mode == DEC_MODE:
                val = long(self._val)
            elif self._mode == OCT_MODE:
                val = long(val, 8)
            else:
                val = long(val, 16)

        except (ValueError, OverflowError):
            val = 0

        if self._ascii:
            asc_val = u''
            if val >= 0 and val < 128:
                c_val = chr(val)
            else:
                c_val = u''

            chr_val = _("ascii: %s")
        else:
            try:
                c_val = unichr(val)
            except:
                c_val = u''
            chr_val = _("unicode: %s")

        # Trap encoding errors that can happen on a non unicode build
        try:
            gc.DrawText(chr_val % c_val, 5, rect.height - (t_extent[1] + 5))
        except UnicodeEncodeError:
            pass

    def ClearError(self):
        """Clear an errors in the display"""
        if self._error:
            self._error = False
            self.SetValue('0')

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
            tmp = [ x for x in val.split(u'.') if len(x) ]
            print tmp
            if len(tmp) > 1:
                fval = int(tmp[0])
                if not tmp[1].startswith('0') and int(tmp[1]) >= 5:
                    fval = fval + 1
            else:
                # Round up for decimal point conversion
                if not tmp[0].startswith('0') and int(tmp[0]) >= 5:
                    fval = 1
                else:
                    fval = 0
        else:
            fval = int(val)
        return fval

    def OnEraseBG(self, evt):
        """Reduce flickering on msw"""
        pass

    def OnPaint(self, evt):
        """Paint the display and its values"""
        if wx.Platform == "__WXMSW__":
            dc = wx.BufferedPaintDC(self)
            brush =wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENU), wx.SOLID)
            dc.SetBackground(brush)
            dc.Clear()
        else:
            dc = wx.PaintDC(self)

        gc = wx.GCDC(dc)

        rect = self.GetRect()
        w = rect.width
        h = rect.height

        gc.SetBrush(wx.Brush(DISP_COLOR))
        color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVEBORDER)
        color = AdjustColour(color, -30)
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
        self._error = True
        if msg != u'':
            self.SetValue(_("Error: %s") % msg)
        else:
            self.SetValue(_("Error"))

    def SetAscii(self):
        """Set the character display to show ascii"""
        self._ascii = True
        self.Refresh()

    def SetMode(self, mode):
        """Set the mode value of the display"""
        if self._mode == DEC_MODE:
            tmp = self.GetValAsInt()
            if mode == OCT_MODE:
                val = oct(tmp)
            elif mode == HEX_MODE:
                val = str(hex(tmp))
                val = '0x' + val.lstrip('0x').upper()
            else:
                val = self._val
        elif self._mode == OCT_MODE:
            tmp = self._val.lstrip('0').rstrip('L')
            if not len(tmp):
                tmp = '0'
            if mode == DEC_MODE and len(tmp):
                val = int(tmp, 8)
            elif mode == HEX_MODE and len(tmp):
                val = str(hex(int(tmp, 8)))
                val = '0x' + val.lstrip('0x').upper()
            else:
                val = self._val
        else:
            tmp = self._val.lstrip('0x').rstrip('L')
            if not len(tmp):
                tmp = '0'
            if mode == DEC_MODE:
                val = int(tmp, 16)
            elif mode == OCT_MODE:
                val = oct(int(tmp, 16))
            else:
                val = self._val
        self._val = str(val)
        self._mode = mode
        self.Refresh()

    def SetOperator(self, op):
        """Sets the displays operator value"""
        self._op = str(op)
        self.Refresh()

    def SetUnicode(self):
        """Set the character display to show unicode"""
        self._ascii = False
        self.Refresh()

    def SetValue(self, val, verbatim=False):
        """Set the value of the control main display portion
        @param val: Value to set in display
        @keyword verbatim: Print the value verbatim without transformations

        """
        tmp = unicode(val)
        if verbatim:
            self._val = tmp
            self.Refresh()
            return
        if len(tmp) > 1 and self._mode == DEC_MODE:
            tmp = tmp.lstrip('0')
        if not len(tmp):
            tmp = u'0'
        if self._mode == HEX_MODE:
            tmp = tmp.lstrip('0x').lstrip('0')
            if len(tmp):
                tmp = u'0x' + tmp
            else:
                tmp = u'0x0'
        elif self._mode == OCT_MODE:
            tmp = u'0' + tmp.lstrip('0')
        self._val = tmp
        self.Refresh()

#-----------------------------------------------------------------------------#
# Utility Function

def AdjustColour(color, percent, alpha=wx.ALPHA_OPAQUE):
    """ Brighten/Darken input colour by percent and adjust alpha
    channel if needed. Returns the modified color.
    @param color: color object to adjust
    @type color: wx.Colour
    @param percent: percent to adjust +(brighten) or -(darken)
    @type percent: int
    @keyword alpha: Value to adjust alpha channel to

    """
    radj, gadj, badj = [ int(val * (abs(percent) / 100.))
                         for val in color.Get() ]

    if percent < 0:
        radj, gadj, badj = [ val * -1 for val in [radj, gadj, badj] ]
    else:
        radj, gadj, badj = [ val or percent for val in [radj, gadj, badj] ]

    red = min(color.Red() + radj, 255)
    green = min(color.Green() + gadj, 255)
    blue = min(color.Blue() + badj, 255)
    return wx.Colour(red, green, blue, alpha)

def LogFunction(msg):
    """Print Log Messages
    @param msg: string

    """
    try:
        wx.GetApp().GetLog()(msg)
    except AttributeError:
        pass

#-----------------------------------------------------------------------------#
# Test

if __name__ == '__main__':
    APP = wx.App(False)
    CALC = CalcFrame(None, _("Calculator"))
    CALC.Show(True)
    APP.MainLoop()
