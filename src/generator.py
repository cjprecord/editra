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
# FILE: generator.py                                                       #
# AUTHOR: Cody Precord                                                     #
# LANGUAGE: Python                                                         #
# SUMMARY:                                                                 #
#    Provides various methods and classes for generating code and          #
# transforming code to different formats such as html.                     #
#                                                                          #
# METHODS:                                                                 #
#
#
#
#--------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id: Exp $"
__revision__ = "$Revision:  $"

#--------------------------------------------------------------------------#
# Dependancies
import wx
import wx.stc
import ed_glob
from ed_style import StyleItem

#--------------------------------------------------------------------------#
# Globals
FONT_FALLBACKS = "Trebuchet, Tahoma, sans-serif"

#--------------------------------------------------------------------------#

class Html:
    """Transforms the text from a given Editra stc to a fully
    styled html page. Inline CSS is generated and inserted into
    the head of the Html to style the text regions by default 
    unless requested to generate a separate sheet.

    """
    def __init__(self, stc_ctrl, inline_css=True):
        """Creates the Html object from an Editra stc text control"""

        # Attributes
        self.stc = stc_ctrl
        self.head = self.GenerateHead()
        self.css = dict()
        self.body = self.GenerateBody()

    def __str__(self):
        """Returns the string of html"""
        style = "<style type=\"text/css\">\n%s</style>"
        css = wx.EmptyString
        for key in self.css:
            css += str(self.css[key]) + "\n"
        css = css % self.stc.GetFontDictionary()
        style = style % css
        head = self.head.replace('</head>', style + "\n</head>")
        html = "<html>\n%s\n%s\n</html>"
        html = html % (head, self.body)
        return html

    def Unicode(self):
        """Returns the html as unicode"""
        return unicode(self.__str__())

    def GenerateHead(self):
        """Generates the html head block"""
        return "<head>\n<title>%s</title>\n" \
               "<meta name=\"Generator\" content=\"Editra/%s\">\n" \
               "<meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\">" \
               "\n</head>" % (self.stc.filename, ed_glob.version)

    def GenerateBody(self):
        """Generates the body of the html from the stc's content. To do
        this it does a character by character parse of the stc to determine
        style regions and generate css and and styled spans of html in order
        to generate an 'exact' html reqresentation of the stc's window.

        """
        html = wx.EmptyString
        parse_pos = 0
        style_start = 0
        style_end = 0
        last_pos = self.stc.GetLineEndPosition(self.stc.GetLineCount())

        # Get Document start point info
        last_id = self.stc.GetStyleAt(parse_pos)
        tag = self.stc.FindTagById(last_id)
        if tag != wx.EmptyString:
            s_item = StyleItem()
            s_item.SetAttrFromStr(self.stc.GetStyleByName(tag))
            self.css[tag] = CssItem(tag.split('_')[0], s_item)
 
       # Build Html
        while parse_pos < last_pos:
            parse_pos += 1
            curr_id = self.stc.GetStyleAt(parse_pos)
            style_end = parse_pos
            # If style region has changed close section
            if curr_id == 0 and self.stc.GetStyleAt(parse_pos + 1) == last_id:
                curr_id = last_id

            if curr_id != last_id:
                tmp = self.stc.GetTextRange(style_start, style_end)
                tmp = self.TransformText(tmp)
                if tmp.isspace() or tag in ["default_style", "operator_style"]:
                    html += tmp
                else:
                    tmp2 = "<span class=\"%s\">%s</span>"
                    html += tmp2 % (tag.split('_')[0], tmp)

                last_id = curr_id
                style_start = style_end
                tag = self.stc.FindTagById(last_id)
                if not self.css.has_key(tag):
                    s_item = StyleItem()
                    s_item.SetAttrFromStr(self.stc.GetStyleByName(tag))
                    self.css[tag] = CssItem(tag.split('_')[0], s_item)
        if html == wx.EmptyString:
            # Case for unstyled documents
            s_item = StyleItem()
            s_item.SetAttrFromStr(self.stc.GetStyleByName('default_style'))
            self.css['default_style'] = CssItem('default', s_item)
            html = self.TransformText(self.stc.GetText())
        else:
            self.OptimizeCss()
        return "<body class=\"default\">\n<pre>\n%s\n</pre>\n</body>" % html

    def OptimizeCss(self):
        """Optimizes the CSS Set"""
        if not self.css.has_key('default_style'):
            return
        if self.css.has_key('operator_style'):
            self.css.pop('operator_style')
        default = self.css['default_style']
        for key in self.css:
            if key == 'default_style':
                continue
            if default.GetFont() == self.css[key].GetFont():
                self.css[key].SetFont(wx.EmptyString)
            if default.GetFontSize() == self.css[key].GetFontSize():
                self.css[key].SetFontSize(wx.EmptyString)
            if default.GetBackground() == self.css[key].GetBackground():
                self.css[key].SetBackground(wx.EmptyString)
            if default.GetColor() == self.css[key].GetColor():
                self.css[key].SetColor(wx.EmptyString)
            for item in default._decor:
                if item in self.css[key]._decor:
                    self.css[key]._decor.remove(item)

    def TransformText(self, text):
        """Does character substitution on a string and returns
        the html equivlant of the given string.

        """
        text = text.replace('&', "&amp;")      # Ampersands
        text = text.replace('(C)', "&copy;")   # Copyright symbol
        text = text.replace('<', "&lt;")       # Less Than Symbols
        text = text.replace('>', "&gt;")       # Greater Than Symbols
        #text = text.replace('\t', "&nbsp;" * int(ed_glob.PROFILE['TABWIDTH'])) # Tab Width
        text = text.replace("\"", "&quot;")
        return text

class CssItem:
    """Converts an Edtira StyleItem to a Css item for use in
    generating html.

    """
    def __init__(self, class_tag, style_item):
        """Initilizes a Css object equivilant of an Editra StyleItem
        NOTE: it is left up to the caller to do any string substituition
        for font faces and size values as this class will contruct the css
        item as a mere reformation of StyleItem"""
        self._tag = class_tag
        self._back = style_item.GetBack()
        self._fore = style_item.GetFore()
        self._font = style_item.GetFace()
        self._size = style_item.GetSize()
        # List of additional style specs
        self._decor = self.ExtractDecorators()

    def __eq__(self, css2):
        """Defines the == operator for the CssItem class"""
        if self.__str__() == str(css2):
            return True
        else:
            return False

    def __str__(self):
        """Outputs the css item as a formatted css block"""
        css = ".%s {\n%s}"
        css_body = wx.EmptyString
        if self._font != wx.EmptyString:
            font = self._font.split(',')
            css_body += u"\tfont-family: %s, %s;\n" % (font[0], FONT_FALLBACKS)
        if self._size != wx.EmptyString:
            size = self._size.split(',')
            css_body += u"\tfont-size: %s;\n" % str(size[0])
        if self._fore != wx.EmptyString:
            fore = self._fore.split(',')
            css_body += u"\tcolor: %s;\n" % fore[0]
        if self._back != wx.EmptyString:
            back = self._back.split(',')
            css_body += u"\tbackground-color: %s;\n" % back[0]
        for item in self._decor:
            if item == u'bold':
                css_body += u"\tfont-weight: %s;\n" % item
            elif item == u'italic':
                css_body += u"\tfont-style: %s;\n" % item
            elif item == u'underline':
                css_body += u"\ttext-decoration: %s;\n" % item
            else:
                pass
        if css_body != wx.EmptyString:
            return css % (self._tag, css_body)
        else:
            return css_body

    def ExtractDecorators(self):
        """Pulls additional style specs from the StyleItem such
        as bold, italic, and underline styles.

        """
        decor = list()
        for val in [ self._back, self._fore, self._font, self._size ]:
            tmp = val.split(u',')
            if len(tmp) < 2:
                continue
            else:
                decor.append(tmp[1])
        return decor

    def GetBackground(self):
        """Returns the Background value"""
        return self._back

    def GetColor(self):
        """Returns the Font/Fore Color"""
        return self._fore

    def GetFont(self):
        """Returns the Font Name"""
        return self._font

    def GetFontSize(self):
        """Returns the Font Size"""
        return self._size

    def SetBackground(self, hex_str):
        """Sets the Background Color"""
        self._back = hex_str

    def SetColor(self, hex_str):
        """Sets the Font/Fore Color"""
        self._fore = hex_str

    def SetFont(self, font_face):
        """Sets the Font Face"""
        self._font = font_face

    def SetFontSize(self, size_str):
        """Sets the Font Point Size"""
        self._size = size_str
