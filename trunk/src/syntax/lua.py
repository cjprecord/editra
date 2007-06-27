###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    staff@editra.org                                                         #
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
# FILE: lua.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Lua                                          #
#                                                                             #
# @todo: This setup for Lua5, maybe add Lua4 support                          #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
# Keywords
lua_keywords = (0, "and break do else elseif end false for function if "
                   "in local nil not or repeat return then true until while")

# Basic Functions
lua_funct = (1, "_VERSION assert collectgarbage dofile error gcinfo loadfile "
                "loadstring print rawget rawset require tonumber tostring type "
                "unpack "
                # Lua5 Basic functions
                "_G getfenv getmetatable ipairs loadlib next pairs pcall "
                "rawequal setfenv setmetatable xpcall \string table math "
                "coroutine io os debug \load module select")

# String, (table) & math functions Lua5
lua_str = (2, "string.byte string.char string.dump string.find string.len "
              "string.lower string.rep string.sub string.upper string.format "
              "string.gfind string.gsub table.concat table.foreach "
              "table.foreachi table.getn table.sort table.insert table.remove "
              "table.setn math.abs math.acos math.asin math.atan math.atan2 "
              "math.ceil math.cos math.deg math.exp math.floor math.frexp "
              "math.ldexp math.log math.log10 math.max math.min math.mod "
              "math.pi math.pow math.rad math.random math.randomseed math.sin "
              "math.sqrt math.tan string.gmatch string.match string.reverse "
              "table.maxn math.cosh math.fmod math.modf math.sinh math.tanh "
              "math.huge")

# (coroutines), I/O & system facilities
lua_co = (3, "coroutine.create coroutine.resume coroutine.status coroutine.wrap "
             "coroutine.yield io.close io.flush io.input io.lines io.open "
             "io.output io.read io.tmpfile io.type io.write io.stdin io.stdout "
             "io.stderr os.clock os.date os.difftime os.execute os.exit os.getenv "
             "os.remove os.rename os.setlocale os.time os.tmpname "
             "coroutine.running package.cpath package.loaded package.loadlib "
             "package.path package.preload package.seeall io.popen")

# user1
lua_u1 = (4, "")

# user2
lua_u2 = (5, "")

# user3
lua_u3 = (6, "")

# user4
lua_u4 = (7, "")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
syntax_items = [('STC_LUA_CHARACTER', 'char_style'),
                ('STC_LUA_COMMENT', 'comment_style'),
                ('STC_LUA_COMMENTDOC', 'dockey_style'),
                ('STC_LUA_COMMENTLINE', 'comment_style'),
                ('STC_LUA_DEFAULT', 'default_style'),
                ('STC_LUA_IDENTIFIER', 'default_style'), # style maybe
                ('STC_LUA_LITERALSTRING', 'string_style'),
                ('STC_LUA_NUMBER', 'number_style'),
                ('STC_LUA_OPERATOR', 'operator_style'),
                ('STC_LUA_PREPROCESSOR', 'pre_style'),
                ('STC_LUA_STRING', 'string_style'),
                ('STC_LUA_STRINGEOL', 'stringeol_style'),
                ('STC_LUA_WORD', 'keyword_style'),
                ('STC_LUA_WORD2', 'keyword3_style'),
                ('STC_LUA_WORD3', 'funct_style'),
                ('STC_LUA_WORD4', 'funct_style'),
                ('STC_LUA_WORD5', 'default_style'), # currently unused
                ('STC_LUA_WORD6', 'default_style'), # currently unused
                ('STC_LUA_WORD7', 'default_style'), # currently unused
                ('STC_LUA_WORD8', 'default_style')  # currently unused
               ]

#---- Extra Properties ----#
fold = ("fold", "1")
fold_comp = ("fold.compact", "1")

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [lua_keywords, lua_funct, lua_str, lua_co]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [fold, fold_comp]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [u'--']

#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
