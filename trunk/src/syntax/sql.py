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
# TODO:                                                                       #
# Only Comment/Number highlight seems to work right now need to do more       #
# investigating                                                               #
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
sql_kw = (0, "ABORT ACCESS ACCESSED ADD AFTER ALL ALTER AND ANY AS ASC ATTRIBUTE "
             "AUDIT AUTHORIZATION AVG BASE_TABLE BEFORE BETWEEN BY CASCADE CAST "
             "CHECK CLUSTER CLUSTERS COLAUTH COLUMN COMMENT COMPRESS CONNECT "
             "CONSTRAINT CRASH CREATE CURRENT DATA DATABASE DATA_BASE DBA "
             "DEFAULT DELAY DELETE DESC DISTINCT DROP DUAL ELSE EXCLUSIVE EXISTS "
             "EXTENDS EXTRACT FILE FORCE FOREIGN FROM GRANT GROUP HAVING HEAP "
             "IDENTIFIED IDENTIFIER IMMEDIATE IN INCLUDING INCREMENT INDEX "
             "INDEXES INITIAL INSERT INSTEAD INTERSECT INTO INVALIDATE IS "
             "ISOLATION KEY LIBRARY LIKE LOCK MAXEXTENTS MINUS MODE MODIFY "
             "MULTISET NESTED NOAUDIT NOCOMPRESS NOT NOWAIT OF OFF OFFLINE ON "
             "ONLINE OPERATOR OPTION OR ORDER ORGANIZATION PCTFREE PRIMARY PRIOR "
             "PRIVATE PRIVILEGES PUBLIC QUOTA RELEASE RENAME REPLACE RESOURCE "
             "REVOKE ROLLBACK ROW ROWLABEL ROWS SCHEMA SELECT SEPARATE SESSION "
             "SET SHARE SIZE SPACE START STORE SUCCESSFUL SYNONYM SYSDATE TABLE "
             "TABLES TABLESPACE TEMPORARY TO TREAT TRIGGER TRUNCATE UID UNION "
             "UNIQUE UNLIMITED UPDATE USE USER VALIDATE VALUES VIEW WHENEVER "
             "WHERE WITH TRUE FALSE NULL")
# SQL DB Objects (Types)
sql_dbo = (1, "ANYDATA ANYTYPE BFILE BINARY_INTEGER BLOB BOOLEAN BYTE CHAR "
              "CHARACTER CLOB CURSOR DATE DAY DEC DECIMAL DOUBLE "
              "DSINTERVAL_UNCONSTRAINED FLOAT HOUR INT INTEGER INTERVAL LOB LONG "
              "MINUTE MLSLABEL MONTH NATURAL NATURALN NCHAR NCHAR_CS NCLOB NUMBER "
              "NUMERIC NVARCHAR PLS_INT PLS_INTEGER POSITIVE POSITIVEN PRECISION "
              "RAW REAL RECORD SECOND SIGNTYPE SMALLINT STRING SYS_REFCURSOR TABLE "
              "TIME TIMESTAMP TIMESTAMP_UNCONSTRAINED TIMESTAMP_TZ_UNCONSTRAINED "
              "TIMESTAMP_LTZ_UNCONSTRAINED UROWID VARCHAR VARCHAR2 YEAR "
              "YMINTERVAL_UNCONSTRAINED ZONE")
# SQL PLDoc
sql_pld = (2, "TODO param author since return see deprecated")
# SQL Plus
sql_plus = (3, "acc~ept a~ppend archive log attribute bre~ak bti~tle c~hange cl~ear "
               "col~umn comp~ute conn~ect copy def~ine del desc~ribe disc~onnect "
               "e~dit exec~ute exit get help ho~st i~nput l~ist passw~ord pau~se "
               "pri~nt pro~mpt quit recover rem~ark repf~ooter reph~eader r~un "
               "sav~e set sho~w shutdown spo~ol sta~rt startup store timi~ng tti~tle "
               "undef~ine var~iable whenever oserror whenever sqlerror")
# SQL User KW1 (PL/SQL Functions)
sql_ukw1 = (4, "ABS ACOS ADD_MONTHS ASCII ASCIISTR ASIN ATAN ATAN2 BFILENAME "
               "BITAND CEIL CHARTOROWID CHR COALESCE COMMIT COMMIT_CM COMPOSE "
               "CONCAT CONVERT COS COSH COUNT CUBE CURRENT_DATE CURRENT_TIME "
               "CURRENT_TIMESTAMP DBTIMEZONE DECODE DECOMPOSE DEREF DUMP EMPTY_BLOB "
               "EMPTY_CLOB EXISTS EXP FLOOR FROM_TZ GETBND GLB GREATEST GREATEST_LB "
               "GROUPING HEXTORAW INITCAP NSTR INSTR2 INSTR4 INSTRB INSTRC ISNCHAR "
               "LAST_DAY LEAST LEAST_UB LENGTH LENGTH2 LENGTH4 LENGTHB LENGTHC LN "
               "LOCALTIME LOCALTIMESTAMP LOG LOWER LPAD LTRIM LUB MAKE_REF MAX MIN "
               "MOD MONTHS_BETWEEN NCHARTOROWID NCHR NEW_TIME NEXT_DAY NHEXTORAW "
               "NLS_CHARSET_DECL_LEN NLS_CHARSET_ID NLS_CHARSET_NAME NLS_INITCAP "
               "NLS_LOWER NLSSORT NLS_UPPER NULLFN NULLIF NUMTODSINTERVAL "
               "NUMTOYMINTERVAL NVL POWER RAISE_APPLICATION_ERROR RAWTOHEX "
               "RAWTONHEX REF REFTOHEX REPLACE ROLLBACK_NR ROLLBACK_SV ROLLUP ROUND "
               "ROWIDTOCHAR ROWIDTONCHAR ROWLABEL RPAD RTRIM SAVEPOINT "
               "SESSIONTIMEZONE SETBND SET_TRANSACTION_USE SIGN SIN SINH SOUNDEX "
               "SQLCODE SQLERRM SQRT STDDEV SUBSTR SUBSTR2 SUBSTR4 SUBSTRB SUBSTRC "
               "SUM SYS_AT_TIME_ZONE SYS_CONTEXT SYSDATE SYS_EXTRACT_UTC SYS_GUID "
               "SYS_LITERALTODATE SYS_LITERALTODSINTERVAL SYS_LITERALTOTIME "
               "SYS_LITERALTOTIMESTAMP SYS_LITERALTOTZTIME SYS_LITERALTOTZTIMESTAMP "
               "SYS_LITERALTOYMINTERVAL SYS_OVER__DD SYS_OVER__DI SYS_OVER__ID "
               "SYS_OVER_IID SYS_OVER_IIT SYS_OVER__IT SYS_OVER__TI SYS_OVER__TT "
               "SYSTIMESTAMP TAN TANH TO_ANYLOB TO_BLOB TO_CHAR TO_CLOB TO_DATE "
               "TO_DSINTERVAL TO_LABEL TO_MULTI_BYTE TO_NCHAR TO_NCLOB TO_NUMBER "
               "TO_RAW TO_SINGLE_BYTE TO_TIME TO_TIMESTAMP TO_TIMESTAMP_TZ "
               "TO_TIME_TZ TO_YMINTERVAL TRANSLATE TREAT TRIM TRUNC TZ_OFFSET UID "
               "UNISTR UPPER UROWID USER USERENV VALUE VARIANCE VSIZE WORK XOR")
# SQL User KW2 (PL/SQL Exceptions)
sql_ukw2 = (5, "ACCESS_INTO_NULL CASE_NOT_FOUND COLLECTION_IS_NULL "
               "CURSOR_ALREADY_OPEN DUP_VAL_ON_INDEX INVALID_CURSOR INVALID_NUMBER "
               "LOGIN_DENIED NO_DATA_FOUND NOT_LOGGED_ON PROGRAM_ERROR "
               "ROWTYPE_MISMATCH SELF_IS_NULL STORAGE_ERROR SUBSCRIPT_BEYOND_COUNT "
               "SUBSCRIPT_OUTSIDE_LIMIT SYS_INVALID_ROWID TIMEOUT_ON_RESOURCE "
               "TOO_MANY_ROWS VALUE_ERROR ZERO_DIVIDE")
# SQL User KW3
sql_ukw3 = (6, "")
# SQL User KW4
sql_ukw4 = (7, "")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_SQL_DEFAULT', 'default_style'),
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
fold = ("fold", "1")
fld_comment = ("fold.comment", "0")
fld_cmpact = ("fold.compact", "0")
fld_sql_ob = ("fold.sql.only.begin", "0")
#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(langId=0):
    """Returns Specified Keywords List
    @param langId: used to select specific subset of keywords

    """
    return [sql_kw, sql_dbo, sql_pld, sql_plus, sql_ukw1, sql_ukw2]

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
    return [u'--']
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#
