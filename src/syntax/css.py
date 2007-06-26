###############################################################################
#    Copyright (C) 2007 Editra Development Team                               #
#    staff@editra.org                                                         #
#                                                                             #
#    This program is free software; you can redistribute it and#or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
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
# FILE: css.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file for Cascading Style Sheets.                        #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# CSS1 Keywords (Idenifiers)
css1_keywords = (0, "font-family font-style font-variant font-weight font-size "
                    "font color background-color background-image background-repeat "
                    "background-position background word-spacing letter-spacing"
                    "text-decoration vertical-align text-transform text-align "
                    "text-indent line-height margin-top margin-right margin-left "
                    "margin padding-top padding-right padding-bottom padding-left "
                    "padding border-top-width border-right-width border-bottom-width "
                    "border-left-width border-width border-color border-style "
                    "border-top border-right border-bottom border-left border "
                    "width height float clear display white-space list-style-type "
                    "list-style-image list-style-position list-style margin-bottom "
                    "text-decoration min-width min-height")

# CSS Psuedo Classes
css_psuedo_class = (1, "link visited active hover focus before after left right "
                       "lang first-letter first-line first-child")

# CSS2 Keywords (Identifers2)
# This is meant for css2 specific keywords, but in order to get a better
# coloring effect this will contain special css properties as well.
css2_keywords = (2, "src stemv stemh slope ascent descent widths bbox baseline "
                    "centerline mathline topline all aqua black blue fuchsia "
                    "gray green lime maroon navy olive purple red silver teal "
                    "yellow ActiveBorder ActiveCaption AppWorkspace ButtonFace "
                    "ButtonHighlight ButtonShadow ButtonText CaptionText "
                    "GrayText Highlight HighlightText InactiveBorder "
                    "InactiveCaption InactiveCaptionText InfoBackground InfoText "
                    "Menu MenuText Scrollbar ThreeDDarkShadow ThreeDFace "
                    "ThreeDHighlight ThreeDLightShadow ThreeDShadow Window "
                    "WindowFrame WindowText Background auto none inherit top "
                    "bottom medium normal cursive fantasy monospace italic "
                    "oblique bold bolder lighter larger smaller icon menu "
                    "narrower wider color center scroll fixed underline overline "
                    "blink sub super middle capitalize uppercase lowercase "
                    "center justify baseline width height float clear overflow "
                    "clip visibility thin thick both dotted dashed solid double "
                    "groove ridge inset outset hidden visible scroll collapse "
                    "content quotes disc circle square hebrew armenian georgian "
                    "inside outside size marks inside orphans widows landscape "
                    "portrait crop cross always avoid cursor default crosshair "
                    "pointer move wait help invert position below level above "
                    "higher block inline compact static relative absolute fixed "
                    "ltr rtl embed bidi-override pre nowrap volume during "
                    "azimuth elevation stress richness silent non mix leftwards "
                    "rightwards behind faster slower male female child code "
                    "digits continuous separate show hide once ")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_CSS_DEFAULT', 'default_style'),
                 ('STC_CSS_ATTRIBUTE', 'funct_style'),
                 ('STC_CSS_CLASS', 'global_style'),
                 ('STC_CSS_COMMENT', 'comment_style'),
                 ('STC_CSS_DIRECTIVE', 'directive_style'),
                 ('STC_CSS_DOUBLESTRING', 'string_style'),
                 ('STC_CSS_ID', 'scalar_style'),
                 ('STC_CSS_IDENTIFIER', 'keyword_style'),
                 ('STC_CSS_IDENTIFIER2', 'keyword3_style'),
                 ('STC_CSS_IMPORTANT', 'error_style'),
                 ('STC_CSS_OPERATOR', 'operator_style'),
                 ('STC_CSS_PSEUDOCLASS', 'scalar_style'),
                 ('STC_CSS_SINGLESTRING', 'string_style'),
                 ('STC_CSS_TAG', 'keyword_style'),
                 ('STC_CSS_UNKNOWN_IDENTIFIER', 'unknown_style'),
                 ('STC_CSS_UNKNOWN_PSEUDOCLASS', 'unknown_style'),
                 ('STC_CSS_VALUE', 'char_style') ]

#---- Extra Properties ----#
fold = ("fold", "1")
#------------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    return [css1_keywords, css_psuedo_class, css2_keywords]

def SyntaxSpec(langId=0):
    """Syntax Specifications
    @param langId: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(langId=0):
    """Returns a list of Extra Properties to set
    @param langId: used to select a specific set of properties

    """
    return [fold]

def CommentPattern(langId=0):
    """Returns a list of characters used to comment a block of code
    @param langId: used to select a specific subset of comment pattern(s)

    """
    return [u'/*', u'*/']
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
