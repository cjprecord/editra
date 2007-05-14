###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    cprecord@editra.org                                                      #
#                                                                             #
#    Editra is free software; you can redistribute it and#or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    Editra is distributed in the hope that it will be useful,                #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program; if not, write to the                            #
#    Free Software Foundation, Inc.,                                          #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                #
###############################################################################

"""
#-----------------------------------------------------------------------------#
# FILE: html.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for HTML/DHTML/SGML.                             #
#                                                                             #
# TODO:                                                                       #
# Add Netscape/Microsoft Tag Extenstions (maybe)                              #
# Styleing needs lots of tweaking                                             #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#
# Dependancies
import synglob

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# HTML Tags (HTML4)
html_tags = (0, "address applet area a base basefont big blockquote br caption "
                "center cite code dd dfn dir div dl dt font form hr html img "
                "input isindex kbd li link map menu meta ol option param pre p "
                "samp span select small strike sub sup table td textarea th tr "
                "script noscript "
                "tt ul var xmp b i u h1 h2 h3 h4 h5 h6 em strong head body title "
                # HTML 4.0 Tags
                "abbr acronym bdo button col label colgroup del fieldset iframe "
                "ins legend object optgroup q s tbody tfoot thead "
                # Tag Attributes / Arguments
                "action align alink alt archive background bgcolor border "
                "bordercolor cellpadding cellspacing checked class clear code "
                "codebase color cols colspan content coords enctype face gutter "
                "height hspace id link lowsrc marginheight marginwidth maxlength "
                "method name prompt rel rev rows rowspan scrolling selected "
                "shape size src start target text type url usemap ismap valign "
                "value vlink vspace width wrap href title http-equiv "
                # HTML 4 Tag Attributes /Arguments
                "accept accesskey axis char charoff charset cite classid codetype "
                "compact data datetime declare defer dir disabled for frame "
                "headers hreflang lang language longdesc multiple nohref nowrap "
                "profile readonly rules scheme scope standby style summary "
                "tabindex valuetype version "
                # DHTML Support
                "dtml-var dtml-if dtml-unless dtml-in dtml-with dtml-let "
                "dtml-call dtml-raise dtml-try dtml-comment dtml-tree")

# JavaScript Keywords (see javascript.py)
import javascript
js_keywords = (1, javascript.KeywordString())

# VBScript Keywords (currently unsupported)
vbs_keywords = (2, "")

# Python Keywords (see python.py)
py_keywords = (3, "")

# PHP Keywords (see php.py)
# This module is loaded for files with a .html/htm extension so it is assumed
# that there is no php in the file. On the other hand the php module loads
# this module so that it can support embedded html. This behavior may be changed
# in the future

# XML Keywords (see xml.py)
# XML files are handled independantly from html although there is support for
# embedded xml highlighting it is currently not being used.

# SGML Keywords
sgml_keywords = (6, "#CURRENT #IMPLIED #REQUIRED ATTLIST CDATA DOCTYPE ELEMENT "
                    "ENTITY IDREF INCLUDE IGNORE NMTOKEN NUMBER RCDATA TEMP")
# SGML Block Keywords
sgml_block = (7, "")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_H_DEFAULT', 'default_style'),
                 ('STC_H_ASP', 'array_style'),
                 ('STC_H_ASPAT', 'array_style'),
                 ('STC_H_ATTRIBUTE', 'keyword2_style'),
                 ('STC_H_ATTRIBUTEUNKNOWN', 'error_style'),
                 ('STC_H_CDATA', 'default_style'), # Style ME
                 ('STC_H_COMMENT', 'comment_style'),
                 ('STC_H_DOUBLESTRING', 'string_style'),
                 ('STC_H_ENTITY', 'default_style'), # Style ME
                 ('STC_H_NUMBER', 'number_style'),
                 ('STC_H_OTHER', 'default_style'),  # Style Me
                 ('STC_H_QUESTION', 'scalar_style'),
                 ('STC_H_SCRIPT', 'funct_style'), # STYLE ME
            #     ('STC_H_SGML_1ST_PARAM', 'array_style'), # STYLE ME
                 ('STC_H_SGML_1ST_PARAM_COMMENT', 'comment_style'),
           #      ('STC_H_SGML_BLOCK_DEFAULT', 'array_style'), # STYLE ME
           #      ('STC_H_SGML_COMMAND', 'array_style'), # STYLE ME
                 ('STC_H_SGML_COMMENT', 'comment_style'),
                 ('STC_H_SGML_DEFAULT', 'array_style'), # STYLE ME
                 ('STC_H_SGML_DOUBLESTRING', 'string_style'),
           #      ('STC_H_SGML_ENTITY', 'array_style'), # STYLE ME
                 ('STC_H_SGML_ERROR', 'error_style'),
                 ('STC_H_SGML_SIMPLESTRING', 'string_style'),
           #      ('STC_H_SGML_SPECIAL', 'array_style'), # STYLE ME
                 ('STC_H_SINGLESTRING', 'string_style'),
                 ('STC_H_TAG', 'keyword_style'),
                 ('STC_H_TAGEND', 'keyword_style'),
                 ('STC_H_TAGUNKNOWN', 'error_style'),
                 ('STC_H_VALUE', 'number_style'),
                 ('STC_H_XCCOMMENT', 'comment_style'),
                 ('STC_H_XMLEND', 'scalar_style'),
                 ('STC_H_XMLSTART', 'scalar_style') ]

#---- Extra Properties ----#
fold = ("fold", "1")
fld_html = ("fold.html", "1")

#------------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    """Returns List of Keyword Specifications"""
    KEYWORDS = [html_tags, sgml_keywords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    return syntax_items + javascript.syntax_items

def Properties(type=0):
    """Extra Properties"""
    return [ fold, fld_html ]

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u'<!--', u'-->' ]
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String"""
    if option == synglob.ID_LANG_SGML:
        return sgml_keywords[1]
    else:
        return html_tags[1]

#---- End Syntax Modules Internal Functions ----#
