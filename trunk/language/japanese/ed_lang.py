# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2006 Editra Development Team   		 	   #
#    staff@editra.org   						   #
#									   #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
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
# FILE:	ed_lang.py                                                         #
# AUTHOR: Anri Ito                                                         #
# LANG: Japanese                                                           #
#                                                                          #
# SUMMARY:                                                                 #
# Japanese language definitions for Editras menus                          #
#                                                                          #
# METHODS:                                                                 #
#    None                                                                  #
#--------------------------------------------------------------------------#
"""

__revision__ = "$Id: Exp $"

#--------------------------------------------------------------------------#
# Dependancies
from ed_glob import LANG # Language Dictionary

#--------------------------------------------------------------------------#

#---- Main Menus ----#

#--- File Menu ---#
LANG['File']     = [u"ファイル", u""]
LANG['New']      = [u"新規作成", u"Start a New File"]
LANG['Open']     = [u"開く", u"ファイルを開く"]
LANG['OpenR']    = [u"最近開かれたファイルを開く", u"最近開かれたファイル"]
LANG['Close']    = [u"閉じる", u"このページを閉じる"]
LANG['Save']     = [u"保存", u"保存"]
LANG['SaveAs']   = [u"名前を付けて保存", u"名前を付けて保存"]
LANG['SavePro']  = [u"プロフィールを保存", u"新しいプロフィールに現在の設定を保存する"]
LANG['LoadPro']  = [u"プロフィールを読み込む", u"カスタムプロフィールを読み込む"]
LANG['Print']    = [u"印刷", u"ファイルをプリントする"]
LANG['Exit']     = [u"エディトラを終了", u"プログラムを終了する"]

#--- Edit Menu ---#
LANG['Edit']     = [u"編集", u""]
LANG['Undo']     = [u"元に戻す", u"一つ前の操作に戻す"]
LANG['Redo']     = [u"やり直す", u"Undoをやり直す"]
LANG['Cut']      = [u"切り取り", u"ドキュメントから選択されたテキストを切り取る"]
LANG['Copy']     = [u"コピー", u"クリップボードに選択されたテキストをコピーする"]
LANG['Paste']    = [u"貼り付け", u"クリップボードからドキュメントにテキストを貼り付ける"]
LANG['SelectA']  = [u"すべてを選択", u"全てのテキストを選択する"]
LANG['Find']     = [u"検索", u"テキストを検索する"]
LANG['FReplace'] = [u"置換", u"テキストを検索し、新しいものと置き換える"]
LANG['Pref']     = [u"選択", u"設定を変更する"]

#--- View Menu ---#
LANG['View']     = u"表示"
LANG['ZoomO']    = u"縮小"
LANG['ZoomI']    = u"拡大"
LANG['ZoomD']    = u"初期設定に戻す"
LANG['WhiteS']   = [u"Show Whitespace", u"Show Whitespace Markers"]
LANG['IndentG']  = [u"Indentation Guides", u"インデントガイドを表示する"]
LANG['Toolbar']  = [u"ツールバー", u"ツールバーを表示する"]

#--- Format Menu ---#
LANG['Format']   = u"初期化"
LANG['WordWrap'] = [u"ワードラップ", u"横に向かってテキストを囲む"]
LANG['Font']     = [u"フォント", u"フォントの設定を変更する"]

#--- Settings Menu ---#
LANG['Settings'] = u"設定"
LANG['SyntaxHL'] = [u"Syntax Highlighting", u"Color Highlight Code Syntax"]
LANG['BraceHL']  = [u"Bracket Highlighting", u"Highlight Braces"]
LANG['KWHelper'] = [u"Keyword Helper", u"キーワードやヒントなどを提供する"]
LANG['Lexer']    = [u"Lexers", u"Manually Set a Lexer"]

#--- Help Menu ---#
LANG['Help']     = u"ヘルプ"
LANG['About']    = [u"バージョン情報", u"このプログラムについての情報"]

#---- End Main Menus ----#

#---- Status Bar ----#
LANG['Line']   = u"線"
LANG['Column'] = u"列"

#---- Dialogs ----#
LANG['SavedF']   = u"保存されたファイル"
LANG['SaveLoc']  = u"保存する場所を選ぶ"
LANG['ChooseF']  = u"ファイルを選ぶ"
LANG['SaveChg']  = [u"変更を保存する", u"変更を保存しますか？"]
LANG['Profile']  = u"Profile"
LANG['ProLoad']  = u"読み込まれたプロフィール"
LANG['NotFound'] = u"見つかりません"


