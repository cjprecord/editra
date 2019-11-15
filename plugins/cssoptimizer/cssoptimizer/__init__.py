# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Css Optimizer Plugin                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################
# Plugin Metadata
"""Generate optimized Css code"""
__author__ = "Cody Precord"
__version__ = "0.4"

#-----------------------------------------------------------------------------#
# Imports
import re
import wx

# Editra Libraries
import plugin
from syntax.synglob import ID_LANG_CSS
import generator

#-----------------------------------------------------------------------------#
# Globals
ID_CSS_OPTIMIZER = wx.NewId()

# Try and add this plugins message catalogs to the app
try:
    wx.GetApp().AddMessageCatalog('cssoptimizer', __name__)
except:
    pass

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class CssOptimizer(plugin.Plugin):
    """ Optimizes Css Files """
    plugin.Implements(generator.GeneratorI)
    def Generate(self, txt_ctrl):
        """Generate an optimized version of the given css file.
        If the file does note appear to be css it will return the
        input verbatim.

        """
        stc = txt_ctrl
        eol = stc.GetEOLChar()
        fname = stc.GetFileName()
        if stc.GetLexer() == wx.stc.STC_LEX_CSS or fname.endswith(".css"):
            # Optimize the text
            lines = [stc.GetLine(x) for x in xrange(stc.GetLineCount()+1)]

            # First Pass compact everything
            for x in xrange(len(lines)):
                line = lines[x].strip()
                if u':' in line:
                    line = line.split(u':')
                    for y in xrange(len(line)):
                        line[y] = line[y].strip()
                    line = u':'.join(line)
                if u"{" in line:
                    line = line.split(u'{')
                    for y in xrange(len(line)):
                        line[y] = line[y].strip()
                    line = u'{'.join(line)
                if len(line) and line[-1] == u'}':
                    line += eol
                lines[x] = line

            # Remove all comments
            txt = "".join(lines)
            cmt_pat = re.compile("\/\*[^*]*\*+([^/][^*]*\*+)*\/")
            if re.search(cmt_pat, txt):
                txt = re.sub(cmt_pat, u'', txt)

            # Compact Redundant Color Defs
            for val in "0123456789abcdefABCDEF":
                find = val * 3
                txt = txt.replace("#" + (find * 2), "#" + find)
                
            ret = ('css', txt)
        else:
            ret = ('txt', stc.GetText())
        return ret

    def GetId(self):
        """Returns the identifing Id of this generator"""
        return ID_CSS_OPTIMIZER

    def GetMenuEntry(self, menu):
        """Returns the MenuItem entry for this generator"""
        mitem = wx.MenuItem(menu, ID_CSS_OPTIMIZER, _("Optimize %s") % u"CSS",
                            _("Generate an optimized version of the css"))
        mitem.SetBitmap(wx.ArtProvider.GetBitmap(str(ID_LANG_CSS), wx.ART_MENU))
        return mitem
