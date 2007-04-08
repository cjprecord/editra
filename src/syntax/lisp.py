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
# FILE: lisp.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for Lisp Files.                                  #
#                                                                             #
# TODO:                                                                       #
# Add Standard Variables                                                      #
#-----------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#

# Lisp Functions/Operators
lisp_func = (0, "find-method find-package find-restart find-symbol finish-output "
                "first fixnum flet float float-digits float-precision float-radix "
                "float-sign floating-point-inexact floating-point-invalid-operation "
                "pprint-indent pprint-linear pprint-logical-block pprint-newline "
                "pprint-pop pprint-tab pprint-tabular prin1 prin1-to-string princ "
                "princ-to-string print print-not-readable print-not-readable-object "
                "print-object floating-point-underflow probe-file floatp proclaim "
                "abort abs access acons acos acosh add-method adjoin adjust-array "
                "adjustable-array-p allocate-instance alpha-char-p alphanumericp "
                "and append apply applyhook apropos apropos-list aref "
                "arithmetic-error arithmetic-error-operands arithmetic-error-operation "
                "array array-dimension array-dimension-limit array-dimensions "
                "array-displacement floor fmakunbound force-output format formatter "
                "fourth fresh-line fround ftruncate ftype funcall function "
                "function-keywords function-lambda-expression functionp gbitp "
                "gcd generic-function gensym gentemp get get-decoded-time "
                "get-dispatched-macro-character get-internal-real-time "
                "get-internal-run-time get-macro-character get-output-stream-string "
                "get-properties prog prog* prog1 prog2 progn program-error progv "
                "provide psetf psetq push pushnew putprop quote random random-state "
                "random-state-p rassoc rassoc-if rassoc-if-not ration rational "
                "rationalize rationalp read read-byte read-char read-car-no-hang "
                "array-element-type array-has-fill-pointer-p array-in-bounds-p "
                "array-rank array-rank-limit array-row-major-index array-total-size "
                "array-total-size-limit arrayp ash asin asinh assert assoc assoc-if "
                "assoc-if-not atan atanh atom base-char base-string bignum bit "
                "bit-and bit-andc1 bit-andc2 bit-eqv bit-ior bit-nand bit-nor "
                "get-setf-expansion get-setf-method get-universial-time getf gethash "
                "go graphic-char-p handler-bind handler-case hash-table "
                "hash-table-count hash-table-p hash-table-rehash-size hash-table-size "
                "hash-table-rehash-threshold hash-table-test host-namestring "
                "identity if if-exists ignorable ignore ignore-errors imagpart import "
                "in-package incf initialize-instance inline read-delimited-list "
                "read-eval-print read-from-string read-line read-preserving-whitespace "
                "read-squence reader-error readtable readtable-case readtablep "
                "real realp realpart reduce reinitialize-instance rem remf "
                "remhash remove remove-duplicates remove-if remove-if-not "
                "remove-method remprop rename-file rename-package replace require "
                "rest restart bit-not bit-orc1 bit-orc2 bit-vector bit-vector-p "
                "bit-xor block boole boole-1 boole-2 boole-and boole-andc1 boole-andc2 "
                "boole-c1 boole-c2 boole-clr boole-eqv boole-ior boole-nand "
                "boole-nor boole-orc1 boole-orc2 boole-set boole-xor boolean "
                "both-case-p boundp break broadcast-stream broadcast-stream-streams "
                "input-stream-p inspect int-char integer integer-decode-float "
                "integer-length integerp interactive-stream-p intern intersection "
                "internal-time-units-per-second invalid-method-error invoke-debugger "
                "invoke-restart invoke-restart-interactively isqrt keyword keywordp "
                "labels lambda lambda-list-keywords lambda-parameters-limit last "
                "lcm ldb ldb-test ldiff least-negative-double-float least-negative-"
                "long-float least-negative-normalized-double-float restart-bind "
                "restart-case restart-name return return-from revappend reverse "
                "room rotatef round row-major-aref rplaca rplacd safety satisfies "
                "sbit scale-float schar search second sequence serious-condition "
                "set set-char-bit set-difference set-dispatched-macro-character "
                "set-exclusive-or set-macro-character set-pprint-dispatch "
                "set-syntax-from-char built-in-class butlast byte byte-position "
                "byte-size call-arguments-limit call-method call-next-method "
                "capitalize car case catch ccase cdr ceiling ceil-error ceil-error-name "
                "cerror change-class char char-bit char-bits char-bits-limit "
                "char-code char-code-limit char-control-bit char-downcase "
                "least-negative-normalized-long-float least-negative-short-font "
                "least-negative-normalized-short-font least-negative-single-font "
                "least-negative-normalized-single-font least-positive-double-float "
                "least-positive-long-float least-positive-normalized-double-float "
                "least-positive-normalized-long-float least-positive-short-float "
                "least-positive-normalized-short-float least-positive-single-float "
                "least-positive-normalized-single-float length let let* lisp "
                "lisp-implementation-type lisp-implementation-version list list* "
                "list-all-packages list-lenght listen listp load shadow "
                "load-logical-pathname-translation shadowing-import shared-initialize "
                "shiftf signal signed-byte signum simple-condition simple-array "
                "simple-base-string simple-bit-vector- simple-bit-vector-p "
                "simple-condition-format-arguments simple-condition-format-control "
                "simple-error simple-string simple-string-p simple-type-error "
                "simple-vector setf setq seventh short-float short-float-epsilon "
                "short-float-negative-epsilon short-site-name simple-vector-p "
                "char-equal char-font char-font-limit char-greaterp char-hyper-bit "
                "char-int char-lessp char-meta-bit char-name char-not-equal "
                "char-not-greaterp char-not-lessp char-super-bit char-upcase char/= "
                "char<= char= char>= character characterp check-type cis class "
                "class-name class-of load-time-value locally log logand logandc1 "
                "logandc2 logbitp logcount logeqv logical-pathname logior lognand "
                "logical-pathname-translations lognor lognot logorc1 logorc2 logxor "
                "long-float long-float-epsilon long-float-negative-epsilon loop "
                "long-site-name loop-finish lower-case-p machine-instance "
                "simple-warning sin single-float-epsilon single-float sinh sixth "
                "single-float-negative-epsilon sleep slot-boundp slot-exists-p "
                "slot-makunbound slot-missing slot-unbound slot-value software-type "
                "software-version some sort space special special-form-p speed "
                "special-operator-p sqrt stable-sort standard clear-input close "
                "clear-output close cirhash code-char coerce commonp compilation-speed "
                "compile compile-file compile-file-pathname compiled-function "
                "compiled-function-p compiler-let compiler-macro complement complex "
                "compiler-macro-function complexp compute-applicable-methods "
                "compute-restarts concatenate concatenated-stream cond condition "
                "concatenated-stream-streams conjugate machine-type machine-version "
                "macro-function macroexpand macroexpand-1 macroexpand-l macrolet "
                "make-array make-broadcast-stream make-char make-concatenated-stream "
                "make-condition make-dispatch-macro-character make-echo-stream "
                "make-hash-table make-instance make-instances-obsolete make-list "
                "make-load-form make-load-form-saving-slots make-method make-package "
                "make-pathname make-random-state make-sequence make-string "
                "standard-char standard-char-p standard-class standard-method "
                "standard-generic-function standard-object step storage-condition "
                "standard-generic-function store-value stream stream-element-type "
                "stream-error stream-error-stream stream-external-format streamp "
                "streamup string string-capitalize string-char string-char-p "
                "string-downcase string-equal string-greaterp string-left-trim "
                "string-lessp string-not-equal string-not-greaterp cons consp "
                "constantly constantp continue control-error copy alist copy-list "
                "copy-pprint-dispatch copy-readtable copy-seq copy-structure "
                "copy-symbol copy-tree cos cosh count count-if count-if-not debug "
                "ctypecase decf declaim declaration declare decode-float "
                "decode-universal-time make-string-input-stream make-symbol "
                "make-string-output-stream make-synonym-stream make-two-way-stream "
                "makunbound map map-into mapc mapcan mapcar mapcon maphash mapl "
                "maplist mask-field max member member-if member-if-not merge "
                "merge-pathname merge-pathnames method method-combination "
                "method-combination-error method-qualifiers string-not-lessp "
                "string-right-strim string-right-trim string-stream string-trim "
                "string-upcase string/= string< string<= string= string> string>= "
                "stringp structure structure-class structure-object style-warning "
                "sublim sublis subseq subsetp subst subst-if subst-if-not substitute "
                "substitute-if substitute-if-not defclass defconstant defgeneric "
                "define-compiler-macro define-condition define-method-combination "
                "define-modify-macro define-setf-expander define-setf-method "
                "define-symbol-macro defmacro defmethod defpackage defparameter "
                "defsetf defstruct deftype defun defvar delete delete-duplicates "
                "delete-file delete-if delete-if-not delete-package denominator "
                "deposite-field min minusp mismatch mod most-negative-double-float "
                "most-negative-fixnum most-negative-long-float most-positive-fixnum "
                "most-negative-short-float most-negative-single-float muffle-warning "
                "most-positive-long-float most-positive-short-float multiple-value-bind "
                "most-positive-single-float multiple-value-call multiple-value-list "
                "multiple-value-prog1 multiple-value-seteq multiple-value-setq "
                "multiple-value-limit name-char namestring nbutlast nconc subtypep "
                "next-method-p svref sxhash symbol symbol-function symbol-macrolet "
                "symbol-name symbol-package symbol-plist symbol-value symbolp "
                "synonym-stream synonym-stream-symbol sys system t tagbody tailp "
                "tan tanh tenth terpri the third throw time trace describe "
                "describe-object destructuring-bind digit-char digit-char-p directory "
                "directory-namestring disassemble division-by-zero do do* dolist "
                "do-all-symbols do-external-symbols do-symbols dotimes double-float "
                "double-float-epsilon double-float-negative-epsilion dpb dribble "
                "dynamic-extent ecase echo-stream echo-stream-input-stream nil "
                "nintersection ninth no-applicable-method no-next-method not "
                "notany notevery notinline nreconc nreverse nset-difference "
                "nset-exclusive-or nstring nstring-capitalize nstring-downcase "
                "nstring-upcase nsublis nsubst nsubst-if nstubst-if-not nth nthcdr "
                "nth-value translate-logical-pathname translate-pathname tree-equal "
                "truename truncase truncate two-way-stream two-way-stream-input-stream "
                "two-way-stream-output-stream type type-error type-error-datnum "
                "type-error-expected-type type-of typecase typep unbound-slot "
                "unbound-slot-instance unbound-variable undefined-function unexport "
                "unintern union unless unread unread-char unsigned-byte ed eigth "
                "echo-stream-output-stream elt encode-universal-time end-of-file "
                "endp enough-namestring ensure-directories-exist eq eql equal "
                "ensure-generic-function equalp error etypecase eval eval-when "
                "evalhook evenp every exp export expt extend-char fboundp fceiling "
                "null number numberp numerator nunion oddp open open-stream-p "
                "optimize or otherwise output-stream-p package package-error "
                "package-error-package package-name package-nicknames packagep "
                "package-shadowing-symbols package-use-list package-used-by-list "
                "pairlis parse-error parse-integer parse-namestring pathname "
                "pathname-device untrace unuse-package unwind-protect upper-case-p "
                "update-instance-for-different-class upgraded-array-element-type "
                "update-instance-for-redefined-class upgraded-complex-part-type "
                "use-package use-value user user-homedir-pathname values "
                "value-list vector vector-pop vector-push vector-push-extend "
                "vectorp warn warning when wild-pathname-p with-accessors "
                "with-compilation-unit with-condition-restarts fdefinition "
                "with-hash-table-iterator fflor fifth file-author file-error "
                "file-error-pathname file-length file-namestring file-position "
                "file-stream file-string-length file-write-date fill fill-pointer "
                "find find-all-symbols find-class find-if find-if-not phase "
                "pathname-directory pathname-host pathname-match-p pathname-name "
                "pathname-type pathname-version pathnamep peek-char pi plusp pop "
                "position position-if position-if-not pprint pprint-dispatch "
                "pprint-exit-if-list-exhausted pprint-fill with-input-from-string "
                "with-open-file with-open-stream with-output-to-string with-slots "
                "with-package-iterator with-simple-restart with-standard-io-syntax "
                "write write-byte write-char write-line write-sequence write-string "
                "write-to-string y-or-n-p yes-or-no-p zerop")       

# Lisp Keywords
lisp_keywords = (1, ":abort :adjustable :append :array :base :case :circle :conc-name "
                    ":constructor :copier :count :create :default :device :directory "
                    ":displaced-index-offset :displaced-to :element-type :end :end1 "
                    ":end2 :error :escape :external :from-end :gensym :host :include "
                    ":if-does-not-exist :if-exists :index :inherited :internal "
                    ":initial-contents :initial-element :initial-offset :initial-value "
                    ":input :io :junk-allowed :key :length :level :name :named "
                    ":new-version :nicknames :output :ouput=file :overwrite :predicate "
                    ":preserve-whitespace :pretty :print :print-function :probe "
                    ":radix :read-only :rehash-size :rehash-threshold :rename :size "
                    ":rename-and-delete :start :start1 :start2 :stream :supersede "
                    ":test :test-not :use :verbose :version")

#---- Syntax Style Specs ----#
syntax_items = [ ('STC_LISP_DEFAULT', 'default_style'),
                 ('STC_LISP_COMMENT', 'comment_style'),
                 ('STC_LISP_MULTI_COMMENT', 'comment_style'),
                 ('STC_LISP_IDENTIFIER', 'default_style'),
                 ('STC_LISP_KEYWORD', 'keyword_style'),
                 ('STC_LISP_KEYWORD_KW', 'keyword2_style'),
                 ('STC_LISP_NUMBER', 'number_style'),
                 ('STC_LISP_OPERATOR', 'operator_style'),
                 ('STC_LISP_SPECIAL', 'class_style'),
                 ('STC_LISP_STRING', 'string_style'),
                 ('STC_LISP_STRINGEOL', 'stringeol_style'),
                 ('STC_LISP_SYMBOL', 'scalar_style') ]

#---- Extra Properties ----#
fold = ('fold', '1')

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(type=0):
    KEYWORDS = [lisp_func, lisp_keywords]
    return KEYWORDS

def SyntaxSpec(type=0):
    """Syntax Specifications"""
    return syntax_items

def Properties(type=0):
    """Extra Properties"""
    return [fold]

def CommentPattern(type=0):
    """Returns a list of characters used to comment a block of code"""
    return [ u';' ]
#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString(option=0):
    # Currently Unused by this module
    return None

#---- End Syntax Modules Internal Functions ----#

#-----------------------------------------------------------------------------#

