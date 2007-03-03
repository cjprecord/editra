############################################################################
#    Copyright (C) 2007 Cody Precord                                       #
#    cprecord@editra.org                                                   #
#									   #
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

"""
#--------------------------------------------------------------------------#
# FILE:	ed_cmdbar.py
# AUTHOR: Cody Precord
# LANGUAGE: Python
# SUMMARY:
#
#
# METHODS:
#
#
#
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import ed_glob
import ed_search

#--------------------------------------------------------------------------#
# Encoded Art
from wx import ImageFromStream, BitmapFromImage
import cStringIO, zlib

def GetTabCloseData():
    return zlib.decompress(
'x\xda\x01.\x02\xd1\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\
\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\
\x08\x08\x08|\x08d\x88\x00\x00\x01\xe5IDAT8\x8d\xa5\x93\xcdkSA\x14\xc5\x7f\
\xaf_\xf9h\x89\xd1ML\xa3\xd1\xc4B\xbb\x10Z\x10\x91@1\x15)\xa8\xe0\xa6.\xa5\
\x0b\xc1\xbf\xc0?@Q\x8a\x0b\x17\x057Y\x89T\xba*\x08\n\xae\x04q!\xc5\xd2\x95A\
\x8b\xb5\xa0\x8dDB\xdab\xb1\xafm2\xf3\xde\x9b\x97\xb8\xb8)\xaf6\xc5M\x07.sg\
\x98s\xee\x99sg,\xab\xa3\x93\xa3\x8c.\x80\x0f\x8f\x1e4\xed\x85y\x9c\xf5*n\
\xa5\xfc_@O*M(\x91\xe4Xn\x94\xcb\xf7\x1fZ]\x00\xf6\xc2<\xf9\'\x8f\xe9\x1b\
\x1a\x04\x1a\xe0\x1b\t\xcf\x03c@\xf9\x80\x03\x0e\xd0T\xa8o+\xbc/\xcc\x04\n\
\x9c\xf5\xaa\x80\xd7~Ai9(\xe7\xa8}y]\xe6X\x8a\xc8\xd9\x0c\xe1X\x0c\x80\x0e \
\x90]\xf9!\xa0\xcc\x88\xacm[\xc2\n\xc3\xf0U\xd0\x1el\xfc\x04\xc0R\x9b\x01\
\x01\x00\xbe\x0b\xae\x0bC9\xe8\xcf\xc2\x85\xeb\x10OH\xe4n\xc8\xde\xa5k\xa0v\
\xdbM\x14\x02#\xf3\xca\'8\x91\x84pD\x80 \xb9VP\\<\xbc\x0b\x80\x18\xb6\xb1\
\x06\x9b[\xf0\xfb\x0f\xdc\xbc-@\x10\xf0l\x01*%p5\x9c9\x7f\x08\x811"o\xbb\x06\
\x11\xb7\xad\x12\x8e\x06{\x07v\xb7\xc5\x17\xad\x0ex\xa0Z.\'Rp\xebN [+\xc9\
\xef\xde\x83\xd3\xa7\xa0\xe1C\xad\x06\x8es\x80@+\xa8\x1b\xb8\x98\x0f\xc0\xcf\
\xa6%\xf6H\xf2\x13\xe0\xf9bv\xdb\x15t\xab\x0b/g`b\x12\xde\xbd\x81\xf2*x\x06\
\nS\x02~1\r\xdd\x9dPW\xff\x12\xf4f\x07du2\x0b[_\xe0\xf9S\x01\xfa\x06\x1a\x1a\
\x96\xbfB\xb1\x08\xa1\x1e87(g\x8f\'\x81\xcfB\x10MgPKKDR\xfd\x90\xb8\x02n\xab\
\x82r\xe5\xf1\xec\xbd\x91VeU\xa9\xd2\x0cE\x03\x05\xf1\xb1q>\xbe~K\xbd\\\xa2\
\xb6\xfa\xbd\xbd\x03\xfbFov\x80h:C|l\x1c\xe6^a\x1d\xf5;\xff\x05\xa0S\xc9\x11\
\xf0eA|\x00\x00\x00\x00IEND\xaeB`\x82?\x85\xea\x82' )

def GetTabCloseBitmap():
    return BitmapFromImage(GetTabCloseImage())

def GetTabCloseImage():
    stream = cStringIO.StringIO(GetTabCloseData())
    return ImageFromStream(stream)

#----------------------------------------------------------------------
def GetTabOnData():
    return zlib.decompress(
'x\xda\x011\x02\xce\xfd\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x0e\
\x00\x00\x00\x0e\x08\x02\x00\x00\x00\x90*\xba\x86\x00\x00\x00\x03sBIT\x08\
\x08\x08\xdb\xe1O\xe0\x00\x00\x01\xe9IDAT(\x91m\x92\xbdk\x13a\x18\xc0\x9f\
\xbb\\r\xd7Ks\xb9&\xc6\xd2j\x8f\xc6D\x08\x8a\xa2\xed\xe2G\x87,\x15\xc4\xb5\
\x8bH\x17-]\x02\x85:\x14\x84\xd0\x82J\x07A\x07\xc1\xff\xc1\xc1I\x04\x07\x11\
\x05\x15\x1d\x1cJ\x87\xa2\xd5\x96\x92&49\xe9\x99\xf4\xbc7w\xf7\xbe\xef\xf3:\
\xdcQ:\xf4\x99\x9e\x8f\x1f\xcf\xb7\xf4\xe9\xf1\xc3\xde\xd7\xcfAg/l5\xe08I\
\x9d\xb2\xd4\xe1\x91\xec\xd5)\xe9\xcd\xad\x1b\x93W.\x9bC\x05.\xfc(&h?\xa6h\
\xec\xe9\xb5\xbbk\x9b\xbbJ\xd0\xd93\xc6n\xd2\xfd\x16\xddo\xc7\x00c\x00\x80\
\x9cE\xa6f\x1a\xc6\xe9\x9c\xfasK\x0e[\rP\x12\x9cx\xd2@*=\xbb(\x8d\x8e!g\xc8\
\x99b\x95rs\x0f\xb8\xaa\xf9\xdd\x03\xa6&\xc5_[>\xecI\x9f\xa9\xa9\x95\x89\xec\
\xbd\xbab\x95\x14\xab\x94\x9f_V+\x13\x85\xd9E\x1f\xa9\xc2)\x00(\x00 \x04\x13\
\x10\x90\xf7\xaf\x92\xe3\x15Y\xd3\xf3\xf3\xcb\x00 k:\xfa\xc4y\xfb\xf20\x97\
\x02\x00\xd0%\xc1\xae\xc36\xb6\x83\xe6\xfd\x93+\xcfdM\x07\x00\xf4I\xa3\xbe\
\xe0o\xfd\x00\x00\x9e\x1b\x8dQ\xf6\x8f0/\xa0\xae/\x05\xec\xe8\x9a0\xe4\xcc\
\xf59"w\\\xc1\xb8\x0c\x00"d\x88"u\xf6\xfc\xc8\xea\xf3\xa8.\xfaD\xd6\xf4\xf1\
\'/\xf4s\x17\x00\x00(\x17!\x8d\xc7B\xa4\xd9\xdbw#ng\xa9\xb6\xb3T\x8b\xe8\xfc\
\x9d9\x00\x10,\x00\xc4\xc4LF+_\xbaHl\xdb\xfb\xf2!Y,\xb7\x9e>"\x9b\x1b\xb4\
\xd3\xf6\xd6\xbe\xcb\xb9Bc\xb5.3\xaa\r\x19\x9df[z}}r\xaaz\xad\xff\xc7>\xb0\
\x9b\xcc\x8d\xcf\xc3\x11#%\x91J\x0e\x9a\x99\xf4\xe0\xc0z\xb3\xa7\xe8V\xd1u\
\x1c#sB\xcb\xa4\x01@`\x185\x17\xd5e\x88\t\xce\xdc^\x1fr\xc3\x8aY\x9d\xfe\xf5\
\xf1\x1dY\xff\xe6m\xff>\xf6]\xd2g\xca\xbaU4\xab\xd3\xff\x01\xe3\xf6\xf0\x91\
\xbc\xe0^J\x00\x00\x00\x00IEND\xaeB`\x82\x7fU\x05\xed' )

def GetTabOnBitmap():
    return BitmapFromImage(GetTabOnImage())

def GetTabOnImage():
    stream = cStringIO.StringIO(GetTabOnData())
    return ImageFromStream(stream)

def LightColour(color, percent):
    """ Brighten input colour by percent. """ 
    end_color = wx.WHITE
    rd = end_color.Red() - color.Red()
    gd = end_color.Green() - color.Green()
    bd = end_color.Blue() - color.Blue()
    high = 100
    # We take the percent way of the color from color -. white
    i = percent
    r = color.Red() + ((i*rd*100)/high)/100
    g = color.Green() + ((i*gd*100)/high)/100
    b = color.Blue() + ((i*bd*100)/high)/100
    return wx.Colour(r, g, b)
#-----------------------------------------------------------------------------#
# Globals
ID_CLOSE_BUTTON = wx.NewId()
ID_SEARCH_CTRL = wx.NewId()

#-----------------------------------------------------------------------------#

class CommandBar(wx.Panel):
    """Creates a pane that houses various different command
    controls for the editor.

    """
    def __init__(self, parent, id, style=wx.TAB_TRAVERSAL):
        """Initializes the bar and its default widgets"""
        wx.Panel.__init__(self, parent, id, style=style)

        # Attributes
        self._parent = parent
        self._psizer = parent.GetSizer()
        self._h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._v_sizer = wx.BoxSizer(wx.VERTICAL)

        # Install Controls
        self._h_sizer.Add((7,7))
        self.close_b = wx.BitmapButton(self, ID_CLOSE_BUTTON, GetTabOnBitmap(), \
                                      size=(15,15), style=wx.BU_AUTODRAW | wx.BU_EXACTFIT)
        self._h_sizer.Add(self.close_b, 0, wx.ALIGN_CENTER_VERTICAL)
        self._h_sizer.Add(self._v_sizer)
        self.InstallSearchCtrl()
        self._h_sizer.Add((5,5))
        self.SetSizer(self._h_sizer)

        # Configure styles
        #self.SetBackgroundColour(wx.ColourRGB(long("666666", 16)))

        # Bind Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=ID_CLOSE_BUTTON)

        # Install self in parent
        self._psizer.Add(self, 0, wx.EXPAND)

    def Hide(self):
        """Hides the control and notifies the parent"""
        wx.Panel.Hide(self)
        if self._psizer != None:
            self._psizer.Layout()
        self._parent.SendSizeEvent()

    def InstallSearchCtrl(self):
        """Installs the search context controls into the panel.
        Other controls should be removed from the panel before calling
        this method.

        """
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        v_sizer.Add((4,4))
        search = ed_search.ED_SearchCtrl(self, ID_SEARCH_CTRL, menulen=5, size=(200, 24))
        v_sizer.Add(search)
        v_sizer.Add((1,1))
        h_sizer.Add((10,10))
        h_sizer.Add(v_sizer)

        self._h_sizer.Add(h_sizer)

    def OnClose(self, evt):
        """Closes the panel and cleans up the controls"""
        e_id = evt.GetId()
        if e_id == ID_CLOSE_BUTTON:
            self.Hide()
            #self.Uninstall()
        else:
            evt.Skip()

    def OnPaint(self, evt):
        """Paints the background of the bar with a nice gradient"""
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = LightColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DSHADOW), 0)
        col2 = LightColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), 50)
        grad = gc.CreateLinearGradientBrush(0,1,0,29, col1, col2)
        grad2 = gc.CreateLinearGradientBrush(0,1,0,29, col2, col1)
        rect = self.GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width-0.5, rect.height-0.5)

        gc.SetPen(wx.Pen(LightColour(col1,-60), 1))
        gc.SetBrush(grad)
        gc.DrawPath(path)
        evt.Skip()

    def Show(self):
        """Shows the control and installs it in the parents
        sizer.

        """
        self._psizer = self._parent.GetSizer()
        self._psizer.Layout()
        self._parent.SendSizeEvent()
        wx.Panel.Show(self)
        ctrl = self.FindWindowById(ID_SEARCH_CTRL)
        if ctrl != None:
            ctrl.SetFocus()

    def Uninstall(self):
        """Uninstalls self from parent control"""
        for item in self.GetChildren():
            item.Destroy()
        self._psizer.Remove(self)
        self._psizer.Layout()
        self._parent.SendSizeEvent()
        self.Destroy()

