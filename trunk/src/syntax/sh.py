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
# FILE: sh.py                                                                 #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration file for Bourne, Bash, Kornshell and C-Shell scripts.   #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
import synglob
#-----------------------------------------------------------------------------#

# Bourne Shell Keywords (bash and kornshell have these too)
comm_keywords = ("break eval newgrp return ulimit cd exec pwd shift umask "
                 "chdir exit read test wait continue kill readonly trap "
                 "contained elif else then case esac do done for in if fi "
                 "until while set export unset")

# Bash/Kornshell extensions (in bash/kornshell but not bourne)
ext_keywords = ("function alias fg integer printf times autoload functions "
                "jobs r true bg getopts let stop type false hash nohup suspend "
                "unalias fc history print time whence typeset while select")

# Bash Only Keywords
bsh_keywords = ("bind disown local popd shopt builtin enable logout pushd "
                "source dirs help declare")

# Bash Shell Commands (statements)
bcmd_keywords = ("chmod chown chroot clear du egrep expr fgrep find gnufind gnugrep "
                 "grep install less ls mkdir mv reload restart rm rmdir rpm sed su "
                 "sleep start status sort strip tail touch complete stop echo")

# Korn Shell Only Keywords
ksh_keywords = "login newgrp"

# Korn Shell Commands (statements)
kcmd_keywords = ("cat chmod chown chroot clear cp du egrep expr fgrep find grep "
                 "install killall less ls mkdir mv nice printenv rm rmdir sed sort "
                 "strip stty su tail touch tput")

# C-Shell Keywords
csh_keywords = ("alias cd chdir continue dirs echo break breaksw foreach end "
                "eval exec exit glob goto case default history kill login "
                "logout nice nohup else endif onintr popd pushd rehash repeat "
                "endsw setenv shift source time umask switch unalias unhash "
                "unsetenv wait")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_SH_DEFAULT', 'default_style'),
                 ('STC_SH_BACKTICKS', 'scalar_style'),
                 ('STC_SH_CHARACTER', 'char_style'),
                 ('STC_SH_COMMENTLINE', 'comment_style'),
                 ('STC_SH_ERROR', 'error_style'),
                 ('STC_SH_HERE_DELIM', 'here_style'),
                 ('STC_SH_HERE_Q', 'here_style'),
                 ('STC_SH_IDENTIFIER', 'default_style'),
                 ('STC_SH_NUMBER', 'number_style'),
                 ('STC_SH_OPERATOR', 'operator_style'),
                 ('STC_SH_PARAM', 'scalar_style'),
                 ('STC_SH_SCALAR', 'scalar_style'),
                 ('STC_SH_STRING', 'string_style'),
                 ('STC_SH_WORD', 'keyword_style') ]

#---- Extra Properties ----#
fld_comment = ("fold.comment", "1")
fld_compact = ("fold.compact", "0")

#------------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    keywords = list()
    keyw_str = [comm_keywords]
    if langId == synglob.ID_LANG_CSH:
        keyw_str.append(csh_keywords)
    else:
        if langId != synglob.ID_LANG_BOURNE:
            keyw_str.append(ext_keywords)
        if langId == synglob.ID_LANG_BASH:
            keyw_str.append(bsh_keywords)
            keyw_str.append(bcmd_keywords)
        elif langId == synglob.ID_LANG_KSH:
            keyw_str.append(ksh_keywords)
            keyw_str.append(kcmd_keywords)
        else:
            pass
    keywords.append((0, " ".join(keyw_str)))
    return keywords

def SyntaxSpec(langId=0):
    """Syntax Specifications
    @param langId: used for selecting a specific subset of syntax specs

    """
    return syntax_items

def Properties(langId=0):
    """Returns a list of Extra Properties to set
    @param langId: used to select a specific set of properties

    """
    return [fld_comment, fld_compact]

def CommentPattern(langId=0):
    """Returns a list of characters used to comment a block of code
    @param langId: used to select a specific subset of comment pattern(s)

    """
    return [u'#']
#---- End Required Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
