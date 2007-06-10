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

"""
#--------------------------------------------------------------------------#
# FILE: ed_print                                                           #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
# Provides a printer class can render the text from an stc into MemoryDC   #
# that is used for printing. Much of the code for scaling in this file is  #
# inspired a python module STCPrinting written by Riaan Booysen.           #
#                                                                          #
# METHODS:                                                                 #
# ED_Printer: Class for managing printing and providing print dialogs      #
# ED_Printout: Scales and renders the given document to a printer.         #
#                                                                          #
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import os
import wx
import wx.stc
import ed_glob
import dev_tool

#--------------------------------------------------------------------------#
# Globals
COLOURMODES = { 'black_white'    : wx.stc.STC_PRINT_BLACKONWHITE,
                'colour_white'   : wx.stc.STC_PRINT_COLOURONWHITE,
                'colour_default' : wx.stc.STC_PRINT_COLOURONWHITEDEFAULTBG,
                'inverse'        : wx.stc.STC_PRINT_INVERTLIGHT,
                'normal'         : wx.stc.STC_PRINT_NORMAL }
#--------------------------------------------------------------------------#
# XXX current minimum print font is set to 12 point
class ED_Printer:
    """Printer Class for the editor"""
    def __init__(self, parent, stc_callable, mode='normal'):
        """Initializes the Printer, the stc_callable parameter
        must be a callable function that returns an STC instance object

        """
        self.stc = stc_callable
        self.title = wx.EmptyString
        self.parent = parent
        self.print_mode = mode
        self.print_data = wx.PrintData()

    def CreatePrintout(self):
        """Creates a printout of the current stc window"""
        colour = COLOURMODES[self.print_mode]
        return ED_Printout(self.stc(), colour, self.stc().filename)

    def PageSetup(self):
        """Opens a print setup dialog"""
        dlg_data = wx.PageSetupDialogData(self.print_data)
        print_dlg = wx.PageSetupDialog(self.parent, dlg_data)
        print_dlg.ShowModal()
        self.print_data = wx.PrintData(dlg_data.GetPrintData())
        print_dlg.Destroy()

    def Preview(self):
        """Preview the Print"""
        printout = self.CreatePrintout()
        printout2 = self.CreatePrintout()
        preview = wx.PrintPreview(printout, printout2, self.print_data)
        pre_frame = wx.PreviewFrame(preview, self.parent, _("Print Preview"))
        pre_frame.Initialize()
        pre_frame.Show()

    def Print(self):
        """Prints the document"""
        pdd = wx.PrintDialogData()
        pdd.SetPrintData(self.print_data)
        printer = wx.Printer(pdd)
        printout = self.CreatePrintout()
        result = printer.Print(self.parent, printout)

        if result:
            self.print_data = wx.PrintData(printer.GetPrintDialogData().GetPrintData())
        printout.Destroy()
        
    def SetColourMode(self, mode_str):
        """Sets the color mode that the text is to be rendered with"""
        if COLOURMODES.has_key(mode_str):
            self.print_mode = mode_str
            ret = True
        else:
            ret = False
        return ret

#-----------------------------------------------------------------------------#
class ED_Printout(wx.Printout):
    """Creates an printout from a STC"""
    def __init__(self, stc_src, colour, title=wx.EmptyString):
        """Initializes the printout object"""
        wx.Printout.__init__(self)
        self.stc = stc_src
        self.colour = colour
        self.title = title

        self.margin = 0.1
        self.lines_pp = 69
        self.page_count, remainder = divmod(self.stc.GetLineCount(), self.lines_pp)
        if remainder:
            self.page_count += 1

    def HasPage(self, page):
        """Is a page within range"""
        if page <= self.page_count:
            return True
        else:
            return False

    def OnPrintPage(self, page):
        """Scales and Renders the page to a DC and prints it"""
        line_height = self.stc.TextHeight(0)
        
        # Calculate sizes
        dc = self.GetDC()
        dw, dh = dc.GetSizeTuple()

        margin_w = self.margin * dw
        margin_h = self.margin * dh
        text_area_w = dw - margin_w * 2
        text_area_h = dh - margin_h * 2

        scale = float(text_area_h) / (line_height * self.lines_pp)
        dc.SetUserScale(scale, scale)

        # Render the title and page numbers
        font = self.stc.GetDefaultFont()
        if font.GetPointSize() < 12:
            font.SetPointSize(12)
        dc.SetFont(font)

        if self.title:
            title_w, title_h = dc.GetTextExtent(self.title)
            dc.DrawText(self.title, int(dw/scale/2 - title_w/2),
                        int(margin_h/scale - title_h * 3))

        # Page Number
        page_lbl = _("Page: %d") % page
        pg_lbl_w, pg_lbl_h = dc.GetTextExtent(page_lbl)
        dc.DrawText(page_lbl, int(dw/scale/2 - pg_lbl_w/2), 
                    int((text_area_h + margin_h) / scale + pg_lbl_h * 2))

        # Render the STC window into a DC for printing
        start_pos = self.stc.PositionFromLine((page - 1) * self.lines_pp)
        end_pos = self.stc.GetLineEndPosition(page * self.lines_pp - 1)
        max_w = (dw / scale) - margin_w
        self.stc.SetPrintColourMode(self.colour)
        end_point = self.stc.FormatRange(True, start_pos, end_pos, dc, dc,
                                        wx.Rect(int(margin_w/scale),
                                                int(margin_h/scale),
                                                max_w, 
                                                int(text_area_h/scale)+1),
                                        wx.Rect(0, (page - 1) * self.lines_pp * \
                                                line_height, max_w, 
                                                line_height * self.lines_pp))

        if end_point < end_pos:
            dev_tool.DEBUGP("[ed_printout] [error] Rendering Error, page %s" % page)
        return True
