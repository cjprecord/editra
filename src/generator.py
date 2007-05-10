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
import ed_menu
from ed_style import StyleItem
import plugin

#--------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

FONT_FALLBACKS = "Trebuchet, Tahoma, sans-serif"

#--------------------------------------------------------------------------#
# Plugin Interface
class GeneratorI(plugin.Interface):
    """Plugins that are to be used for generating code/document need
    to impliment this interface.

    """
    def Generate(self, txt_ctrl):
        """Generates the code. The txt_ctrl parameter is a reference
        to an ED_STC object (see ed_stc.py). The return value of this
        function needs to be a 2 item tuple with the first item being
        an associated file extention to use for setting highlighting
        if available and the second item is the string of the new document.

        """
        pass

    def GetId(self):
        """Must return the Id used for the generator objects
        menu id. This is used to identify which Generator to
        call on a menu event.

        """
        pass

    def GetMenuEntry(self, menu):
        """Returns the MenuItem entry for this generator"""
        pass

class Generator(plugin.Plugin):
    """Plugin Interface Extension Point for Generator
    type plugin objects. Generator objects are used
    to generate a document/code from one type to another.

    """
    observers = plugin.ExtensionPoint(GeneratorI)

    def InstallMenu(self, menu):
        """Appends the menu of available Generators onto
        the given menu.

        """
        menu_items = list()
        for ob in self.observers:
            mi = ob.GetMenuEntry(menu)
            if mi:
                menu_items.append((mi.GetLabel(), mi))
        menu_items.sort()
        genmenu = ed_menu.ED_Menu()
        for item in menu_items:
            genmenu.AppendItem(item[1])
        menu.AppendMenu(ed_glob.ID_GENERATOR, _("Generator"), genmenu,
                             _("Generate Code and Documents"))

    def GenerateText(self, e_id, txt_ctrl):
        """Generates the new document text based on the given
        generator id and contents of the given ED_STC text control.
        
        """
        gentext = None
        for ob in self.observers:
            if ob.GetId() == e_id:
                gentext = ob.Generate(txt_ctrl)
        return gentext

#--------------------------------------------------------------------------#

class Html(plugin.Plugin):
    """Transforms the text from a given Editra stc to a fully
    styled html page. Inline CSS is generated and inserted into
    the head of the Html to style the text regions by default 
    unless requested to generate a separate sheet.

    """
    plugin.Implements(GeneratorI)
    def __init__(self, mgr):
        """Creates the Html object from an Editra stc text control"""

        # Attributes
        self._id = ed_glob.ID_HTML_GEN
        self.stc = None #stc_ctrl
        self.head = wx.EmptyString #self.GenerateHead()
        self.css = dict()
        self.body = wx.EmptyString #self.GenerateBody()

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

    def Generate(self, stc_ctrl):
        """Generates and returns the document"""
        self.stc = stc_ctrl
        self.head = self.GenerateHead()
        self.body = self.GenerateBody()
        return ("html", self.__str__())

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

    def GetId(self):
        """Returns the menu identifier for the HTML generator"""
        return self._id

    def GetMenuEntry(self, menu):
        """Returns the Menu control for the HTML generator"""
        return wx.MenuItem(menu, self._id, _("Generate %s") % u"HTML",
                           _("Generate an %s page from the current document") % u"HTML")

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
            for item in default.GetDecorators():
                if item in self.css[key].GetDecorators():
                    self.css[key].RemoveDecorator(item)

    def TransformText(self, text):
        """Does character substitution on a string and returns
        the html equivlant of the given string.

        """
        text = text.replace('&', "&amp;")      # Ampersands
        text = text.replace('(C)', "&copy;")   # Copyright symbol
        text = text.replace('<', "&lt;")       # Less Than Symbols
        text = text.replace('>', "&gt;")       # Greater Than Symbols
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

    def GetDecorators(self):
        """Returns the list of decorators"""
        return self._decor

    def GetFont(self):
        """Returns the Font Name"""
        return self._font

    def GetFontSize(self):
        """Returns the Font Size"""
        return self._size

    def RemoveDecorator(self, item):
        """Removes a specifed decorator from the decorator set"""
        if item in self._decor:
            self._decor.remove(item)
        else:
            pass

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

#-----------------------------------------------------------------------------#

class LaTeX(plugin.Plugin):
    """Creates a LaTeX document object from the contents of the
    supplied document reference.
    
    """
    plugin.Implements(GeneratorI)
    def __init__(self, plgmgr):
        """Initializes the LaTeX object"""
        self._stc = None
        self._id = ed_glob.ID_TEX_GEN
        self._dback = wx.EmptyString
        self._dfore = wx.EmptyString
        self._dface = wx.EmptyString
        self._dsize = wx.EmptyString
        self._cmds = dict()
        self._body = wx.EmptyString
        self._preamble = wx.EmptyString

    def __str__(self):
        """Returns the string representation of the object"""
        return self._preamble + self._body

    def CreateCmdName(self, name):
        """Creates and returns a proper cmd name"""
        name = name.replace('_', '')
        tmp = u''
        alpha = "ABCDEFGHIJ"
        for ch in name:
            if ch.isdigit():
                tmp += alpha[int(ch)]
            else:
                tmp += ch
        return tmp
        
    def GenDoc(self):
        """Generates the document body of the LaTeX document"""
        tex = wx.EmptyString
        tmp_tex = wx.EmptyString
        parse_pos = 0
        style_start = 0
        style_end = 0
        last_pos = self._stc.GetLineEndPosition(self._stc.GetLineCount())

        # Define the default style
        self.RegisterStyleCmd('default_style', self._stc.GetItemByName('default_style'))

        # Get Document start point info
        last_id = self._stc.GetStyleAt(parse_pos)
        tmp_tex = self.TransformText(chr(self._stc.GetCharAt(parse_pos)))
        tag = self._stc.FindTagById(last_id)
        if tag != wx.EmptyString:
            self.RegisterStyleCmd(tag, self._stc.GetItemByName(tag))

        # Build LaTeX
        while parse_pos < last_pos:
            parse_pos += 1
            curr_id = self._stc.GetStyleAt(parse_pos)
            style_end = parse_pos
            if parse_pos > 1:
                tmp_tex += self.TransformText(chr(self._stc.GetCharAt(parse_pos - 1)))
            if curr_id == 0 and self._stc.GetStyleAt(parse_pos + 1) == last_id:
                curr_id = last_id

            # If style region has changed close section
            if curr_id != last_id or tmp_tex[-1] == "\n":
                if tag == "operator_style" or \
                   (tag == "default_style" and tmp_tex.isspace() and len(tmp_tex) <= 2):
                    tex += tmp_tex
                else:
                    if "\\\\*\n" in tmp_tex:
                        tmp_tex = tmp_tex.replace("\\\\*\n", "")
                        tmp2 = "\\%s{%s}\\\\*\n"
                    else:
                        tmp2 = "\\%s{%s}"

                    cmd = self.CreateCmdName(tag)
                    if cmd in [None, wx.EmptyString]:
                        cmd = "defaultstyle"
                    tex += tmp2 % (cmd, tmp_tex)

                last_id = curr_id
                style_start = style_end
                tag = self._stc.FindTagById(last_id)
                if tag not in [None, wx.EmptyString]:
                    self.RegisterStyleCmd(tag, self._stc.GetItemByName(tag))
                tmp_tex = u''
        if tex == wx.EmptyString:
            # Case for unstyled documents
            tex = self.TransformText(self._stc.GetText())
        return "\\begin{document}\n%s\n\\end{document}" % tex

    def Generate(self, stc_doc):
        """Generates the LaTeX document"""
        self._stc = stc_doc
        default_si = self._stc.GetItemByName('default_style')
        self._dback = default_si.GetBack().split(',')[0]
        self._dfore = default_si.GetFore().split(',')[0]
        self._dface = default_si.GetFace().split(',')[0]
        self._dsize = default_si.GetSize().split(',')[0]
        self._body = self.GenDoc()
        self._preamble = self.GenPreamble()
        return ("tex", self.__str__())

    def GenPreamble(self):
        """Generates the Preamble of the document"""
        pre = ("%% \iffalse meta-comment\n"
               "%%\n%% Generated by Editra %s\n"
               "%% This is generator is Very Experimental.\n"
               "%% The code should compile in most cases but there may\n"
               "%% be some display issues when rendered.\n"
               "%%\n%%\n\n"
               "\\documentclass[11pt, a4paper]{article}\n"
               "\\usepackage[a4paper, margin=2cm]{geometry}\n"
               "\\usepackage[T1]{fontenc}\n"
#               "\\usepackage{ucs}\n"
#               "\\usepackage[utf8x]{inputenc}\n"
               "\\usepackage{color}\n"
               "\\usepackage{alltt}\n"
               "\\usepackage{times}\n") % ed_glob.version
        pre += ("\\pagecolor[rgb]{%s}\n" % self.HexToRGB(self._dback))
        pre += "\\parindent=0in\n\n"
        pre += "%% Begin Styling Command Definitions"
        for cmd in self._cmds:
            pre += ("\n" + self._cmds[cmd])
        pre += "\n%% End Styling Command Definitions\n\n"
        return pre

    def GetId(self):
        """Returns the menu identifier for the LaTeX generator"""
        return self._id

    def GetMenuEntry(self, menu):
        """Returns the Menu control for the LaTeX generator"""
        return wx.MenuItem(menu, self._id, _("Generate %s") % u"LaTeX",
                           _("Generate an %s page from the current document") % u"LaTeX")

    def HexToRGB(self, hex_str):
        """Returns a comma separated rgb string representation
        of the input hex string. 1.0 = White, 0.0 = Black.
        
        """
        hex = hex_str
        if hex[0] == u"#":
            hex = hex[1:]
        ldiff = 6 - len(hex)
        hex += ldiff * u"0"
        # Convert hex values to integer
        red = round(float(float(int(hex[0:2], 16)) / 255), 2)
        green = round(float(float(int(hex[2:4], 16)) / 255), 2)
        blue = round(float(float(int(hex[4:], 16)) / 255), 2)
        return "%s,%s,%s" % (str(red), str(green), str(blue))

    def RegisterStyleCmd(self, cmd_name, s_item):
        """Registers and generates a command from the
        supplied StyleItem. 
        
        """
        cmd_name = self.CreateCmdName(cmd_name)
        if cmd_name in self._cmds:
            return

        # Templates
        uline_tmp = u"\\underline{%s}"
        ital_tmp = u"\\emph{%s}"
        bold_tmp = u"\\textbf{%s}"
        fore_tmp = u"\\textcolor[rgb]{%s}{%s}"
        back_tmp = u"\\colorbox[rgb]{%s}{#1}"
        cmd_tmp = u"\\newcommand{%s}[1]{%s}"

        # Get Style Attributes
        fore = s_item.GetFore()
        if fore == wx.EmptyString:
            fore = self._dfore
        back = s_item.GetBack()
        if back == wx.EmptyString:
            back = self._dback
        face = s_item.GetFace()
        if face == wx.EmptyString:
            face = self._dface
        size = s_item.GetSize()
        if face == wx.EmptyString:
            face = self._dsize

        back = back_tmp % self.HexToRGB(back.split(',')[0])
        fore = fore_tmp % (self.HexToRGB(fore.split(',')[0]), back)
        if "bold" in str(s_item):
            fore = bold_tmp % fore
        if "underline" in str(s_item):
            fore = uline_tmp % fore
        if "italic" in str(s_item):
            fore = ital_tmp % fore
        cmd = cmd_tmp % (("\\" + cmd_name), "\\texttt{\\ttfamily{%s}}" % fore)
        self._cmds[cmd_name] = cmd

    def TransformText(self, txt):
        """Transforms the given text into LaTeX format, by
        escaping all special characters and sequences.
        
        """
        ch_map = { "#" : "\\#", "$" : "\\$", "^" : "\\^",
                   "%" : "\\%", "&" : "\\&", "_" : "\\_",
                   "{" : "\\{", "}" : "\\}", "~" : "\\~",
                   "\\": "$\\backslash$", "\n" : "\\\\*\n",
                   "@" : "$@$", "<" : "$<$", ">" : "$>$",
                   "-" : "$-$", "|" : "$|$"
                 }
        if ch_map.has_key(txt):
            return ch_map[txt]
        else:
            return txt

#-----------------------------------------------------------------------------#

# TODO stub
class RtfGenerator:
    """Generates a fully styled RTF document from the given text 
    controls contents.
    
    """
    def __init__(self, stc_doc):
        """Creates the RTF object"""
        self._stc = stc_doc

    def __str__(self):
        """Returns the RTF object as a string"""
        return 

    def HexToRGB(self, hex_str):
        """Returns a list of red/green/blue values from a
        hex string.
        
        """
        hex = hex_str
        if hex[0] == u"#":
            hex = hex[1:]
        ldiff = 6 - len(hex)
        hex += ldiff * u"0"
        # Convert hex values to integer
        red = int(hex[0:2], 16)
        green =int(hex[2:4], 16)
        blue = int(hex[4:], 16)
        return [red, green, blue]

