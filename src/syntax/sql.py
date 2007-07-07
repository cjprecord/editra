###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
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
# FILE: sql.py                                                                #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Oracle SQL                                   #
#                                                                             #
# @todo: Only Comment/Number highlight seems to work right now                #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Dependancies

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# SQL Keywords
SQL_KW = (0, "ABORT ACCESS ACCESSED ADD AFTER ALL ALTER AND ANY AS ASC "
             "ATTRIBUTE AUDIT AUTHORIZATION AVG BASE_TABLE BEFORE BETWEEN BY "
             "CASCADE CAST CHECK CLUSTER CLUSTERS COLAUTH COLUMN COMMENT "
             "COMPRESS CONNECT CONSTRAINT CRASH CREATE CURRENT DATA DATABASE "
             "DATA_BASE DBA DEFAULT DELAY DELETE DESC DISTINCT DROP DUAL ELSE "
             "EXCLUSIVE EXISTS EXTENDS EXTRACT FILE FORCE FOREIGN FROM GRANT "
             "GROUP HAVING HEAP IDENTIFIED IDENTIFIER IMMEDIATE IN INCLUDING "
             "INCREMENT INDEX INDEXES INITIAL INSERT INSTEAD INTERSECT INTO "
             "INVALIDATE IS ISOLATION KEY LIBRARY LIKE LOCK MAXEXTENTS MINUS "
             "MODE MODIFY MULTISET NESTED NOAUDIT NOCOMPRESS NOT NOWAIT OF OFF "
             "OFFLINE ON ONLINE OPERATOR OPTION OR ORDER ORGANIZATION PCTFREE "
             "PRIMARY PRIOR PRIVATE PRIVILEGES PUBLIC QUOTA RELEASE RENAME "
             "REPLACE RESOURCE REVOKE ROLLBACK ROW ROWLABEL ROWS SCHEMA SELECT "
             "SEPARATE SESSION SET SHARE SIZE SPACE START STORE SUCCESSFUL "
             "SYNONYM SYSDATE TABLE TABLES TABLESPACE TEMPORARY TO TREAT "
             "TRIGGER TRUNCATE UID UNION UNIQUE UNLIMITED UPDATE USE USER "
             "VALIDATE VALUES VIEW WHENEVER WHERE WITH TRUE FALSE NULL")

# SQL DB Objects (Types)
SQL_DBO = (1, "ANYDATA ANYTYPE BFILE BINARY_INTEGER BLOB BOOLEAN BYTE CHAR "
              "CHARACTER CLOB CURSOR DATE DAY DEC DECIMAL DOUBLE LONG NUMBER "
              "DSINTERVAL_UNCONSTRAINED FLOAT HOUR INT INTEGER INTERVAL LOB "
              "MINUTE MLSLABEL MONTH NATURAL NATURALN NCHAR NCHAR_CS NCLOB "
              "NUMERIC NVARCHAR PLS_INT PLS_INTEGER POSITIVE POSITIVEN TABLE "
              "RAW REAL RECORD SECOND SIGNTYPE SMALLINT STRING SYS_REFCURSOR "
              "TIME TIMESTAMP TIMESTAMP_UNCONSTRAINED ZONE PRECISION "
              "TIMESTAMP_LTZ_UNCONSTRAINED UROWID VARCHAR VARCHAR2 YEAR "
              "YMINTERVAL_UNCONSTRAINED TIMESTAMP_TZ_UNCONSTRAINED ")
# SQL PLDoc
SQL_PLD = (2, "TODO param author since return see deprecated")

# SQL Plus
SQL_PLUS = (3, "acc~ept a~ppend archive log attribute bre~ak bti~tle c~hange "
               "col~umn comp~ute conn~ect copy def~ine del desc~ribe pau~se "
               "e~dit exec~ute exit get help ho~st i~nput l~ist passw~ord "
               "pri~nt pro~mpt quit recover rem~ark repf~ooter reph~eader r~un "
               "sav~e set sho~w shutdown spo~ol sta~rt startup store timi~ng "
               "undef~ine var~iable whenever oserror whenever sqlerror cl~ear "
               "disc~onnect ti~tle ")

# SQL User KW1 (PL/SQL Functions)
SQL_UKW1 = (4, "ABS ACOS ADD_MONTHS ASCII ASCIISTR ASIN ATAN ATAN2 BFILENAME "
               "BITAND CEIL CHARTOROWID CHR COALESCE COMMIT COMMIT_CM COMPOSE "
               "CONCAT CONVERT COS COSH COUNT CUBE CURRENT_DATE CURRENT_TIME "
               "CURRENT_TIMESTAMP DBTIMEZONE DECODE DECOMPOSE DEREF DUMP "
               "EMPTY_BLOB EMPTY_CLOB EXISTS EXP FLOOR FROM_TZ GETBND GLB "
               "GREATEST GREATEST_LB GROUPING HEXTORAW INITCAP NSTR INSTR2 "
               "INSTR4 INSTRB INSTRC ISNCHAR LAST_DAY LEAST LEAST_UB LENGTH "
               "LENGTH2 LENGTH4 LENGTHB LENGTHC LN LOCALTIME LOCALTIMESTAMP "
               "LOG LOWER LPAD LTRIM LUB MAKE_REF MAX MIN MOD MONTHS_BETWEEN "
               "NCHARTOROWID NCHR NEW_TIME NEXT_DAY NHEXTORAW NLS_INITCAP "
               "NLS_CHARSET_DECL_LEN NLS_CHARSET_ID NLS_CHARSET_NAME ROUND "
               "NLS_LOWER NLSSORT NLS_UPPER NULLFN NULLIF NUMTODSINTERVAL "
               "NUMTOYMINTERVAL NVL POWER RAISE_APPLICATION_ERROR RAWTOHEX "
               "RAWTONHEX REF REFTOHEX REPLACE ROLLBACK_NR ROLLBACK_SV ROLLUP "
               "ROWIDTOCHAR ROWIDTONCHAR ROWLABEL RPAD RTRIM SAVEPOINT SOUNDEX "
               "SESSIONTIMEZONE SETBND SET_TRANSACTION_USE SIGN SIN SINH "
               "SQLCODE SQLERRM SQRT STDDEV SUBSTR SUBSTR2 SUBSTR4 SUBSTRB "
               "SUBSTRC SUM SYS_AT_TIME_ZONE SYS_CONTEXT SYSDATE TO_DATE "
               "SYS_EXTRACT_UTC SYS_GUID SYS_LITERALTODATE SYS_OVER__DI"
               "SYS_LITERALTODSINTERVAL SYS_LITERALTOTIME SYS_OVER__TT "
               "SYS_LITERALTOTIMESTAMP SYS_LITERALTOTZTIME SYS_OVER__ID"
               "SYS_LITERALTOTZTIMESTAMP SYS_LITERALTOYMINTERVAL SYS_OVER__DD "
               "SYS_OVER_IID SYS_OVER_IIT SYS_OVER__IT SYS_OVER__TI TO_NUMBER "
               "SYSTIMESTAMP TAN TANH TO_ANYLOB TO_BLOB TO_CHAR TO_CLOB "
               "TO_DSINTERVAL TO_LABEL TO_MULTI_BYTE TO_NCHAR TO_NCLOB UID "
               "TO_RAW TO_SINGLE_BYTE TO_TIME TO_TIMESTAMP TO_TIMESTAMP_TZ "
               "TO_TIME_TZ TO_YMINTERVAL TRANSLATE TREAT TRIM TRUNC TZ_OFFSET "
               "UNISTR UPPER UROWID USER USERENV VALUE VARIANCE VSIZE WORK XOR")

# SQL User KW2 (PL/SQL Exceptions)
SQL_UKW2 = (5, "ACCESS_INTO_NULL CASE_NOT_FOUND COLLECTION_IS_NULL "
               "CURSOR_ALREADY_OPEN DUP_VAL_ON_INDEX INVALID_CURSOR "
               "LOGIN_DENIED NO_DATA_FOUND NOT_LOGGED_ON PROGRAM_ERROR "
               "ROWTYPE_MISMATCH SELF_IS_NULL STORAGE_ERROR INVALID_NUMBER"
               "SUBSCRIPT_OUTSIDE_LIMIT SYS_INVALID_ROWID TIMEOUT_ON_RESOURCE "
               "TOO_MANY_ROWS VALUE_ERROR ZERO_DIVIDE  SUBSCRIPT_BEYOND_COUNT ")

# SQL User KW3
SQL_UKW3 = (6, "")

# SQL User KW4
SQL_UKW4 = (7, "")

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [ ('STC_SQL_DEFAULT', 'default_style'),
                 ('STC_SQL_CHARACTER', 'char_style'),
                 ('STC_SQL_COMMENT', 'comment_style'),
                 ('STC_SQL_COMMENTDOC', 'comment_style'),
                 ('STC_SQL_COMMENTDOCKEYWORD', 'dockey_style'),
                 ('STC_SQL_COMMENTDOCKEYWORDERROR', 'error_style'),
                 ('STC_SQL_COMMENTLINE', 'comment_style'),
                 ('STC_SQL_COMMENTLINEDOC', 'comment_style'),
                 ('STC_SQL_IDENTIFIER', 'default_style'),
                 ('STC_SQL_NUMBER', 'number_style'),
                 ('STC_SQL_OPERATOR', 'operator_style'),
                 ('STC_SQL_QUOTEDIDENTIFIER', 'default_style'),
                 ('STC_SQL_SQLPLUS', 'scalar_style'),
                 ('STC_SQL_SQLPLUS_COMMENT', 'comment_style'),
                 ('STC_SQL_SQLPLUS_PROMPT', 'default_style'),
                 ('STC_SQL_STRING', 'string_style'),
                 ('STC_SQL_USER1', 'funct_style'),
                 ('STC_SQL_USER2', 'number2_style'),
                 ('STC_SQL_USER3', 'default_style'),
                 ('STC_SQL_USER4', 'default_style'),
                 ('STC_SQL_WORD', 'keyword_style'),
                 ('STC_SQL_WORD2', 'keyword2_style') ]

#---- Extra Properties ----#
FOLD = ("fold", "1")
FLD_COMMENT = ("fold.comment", "0")
FLD_COMPACT = ("fold.compact", "0")
FLD_SQL_OB = ("fold.sql.only.begin", "0")
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @param lang_id: used to select specific subset of keywords

    """
    return [SQL_KW, SQL_DBO, SQL_PLD, SQL_PLUS, SQL_UKW1, SQL_UKW2]

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @param lang_id: used for selecting a specific subset of syntax specs

    """
    return SYNTAX_ITEMS

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @param lang_id: used to select a specific set of properties

    """
    return [FOLD]

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @param lang_id: used to select a specific subset of comment pattern(s)

    """
    return [u'--']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
