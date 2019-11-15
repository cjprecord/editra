# -*- coding: utf-8 -*-
# Name: VariablesList.py
# Purpose: Debugger plugin
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id: VariablesLists.py 1526 2012-03-30 20:44:03Z rans@email.com $"
__revision__ = "$Revision: 1526 $"

#----------------------------------------------------------------------------#
# Imports
import os
import types
import threading
import re
import wx
import wx.gizmos

# Editra Libraries
import ed_glob
import ed_msg

# Local Imports
from PyStudio.Common.PyStudioUtils import PyStudioUtils
from PyStudio.Common.PyStudioUtils import RunProcInThread
from PyStudio.Debugger.ExpressionDialog import ExpressionDialog
from PyStudio.Debugger.RpdbDebugger import RpdbDebugger

# Globals
_ = wx.GetTranslation

#----------------------------------------------------------------------------#

class VariablesList(wx.gizmos.TreeListCtrl):
    """List control for displaying stack frame results"""
    COL_NAME = 0
    COL_VALUE = 1
    COL_TYPE = 2

    # Image IDs
    IMG_CLASS, \
    IMG_FUNCT, \
    IMG_VAR = range(3)
    def __init__(self, parent, listtype, filterexpr, filterlevel):
        """Create a variable display list
        @param parent: parent window
        @param listtype: type of list
        @param filterexpr: initial filtering expression
        @param filterlevel: initial filtering level

        """
        super(VariablesList, self).__init__(parent)

        # Attributes
        self.tenspaces = self.GetTextExtent("          ")[0]
        self.colname_name = _("Name")
        self.colname_value = _("Value")
        self.colname_type = _("Type")

        self.listtype = listtype
        self.filterexpr = filterexpr
        self.filterlevel = filterlevel
        self.key = None
        self.ignoredwarnings = {'': True}
        self._imglst = wx.ImageList(16, 16)
        self._imgmap = dict() # type -> imgidx

        # Setup
        self.AddColumn(self.colname_name)
        self.AddColumn(self.colname_value)
        self.AddColumn(self.colname_type)
        if wx.Platform == '__WXMAC__':
            self.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        self.SetMainColumn(0)
        self.SetLineSpacing(0)
        ## Setup ImageList
        self.SetupImageList()

        # Event Handlers
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnItemExpanding)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSING, self.OnItemCollapsing)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.OnItemToolTip)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK ,self.OnItemRightClick)

    def set_mainwindow(self, mw):
        self._mainw = mw

    # Properties
    FilterExpr = property(lambda self: self.filterexpr,
                           lambda self, val: setattr(self, 'filterexpr', val))
    FilterLevel = property(lambda self: self.filterlevel,
                           lambda self, val: setattr(self, 'filterlevel', val))

    def SetupImageList(self):
        """Update all images"""
        self._imglst.RemoveAll()
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU)
        idx = self._imglst.Add(bmp)
        self._imgmap[VariablesList.IMG_CLASS] = idx
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_METHOD_TYPE), wx.ART_MENU)
        idx = self._imglst.Add(bmp)
        self._imgmap[VariablesList.IMG_FUNCT] = idx
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_VARIABLE_TYPE), wx.ART_MENU)
        idx = self._imglst.Add(bmp)
        self._imgmap[VariablesList.IMG_VAR] = idx
        self.SetImageList(self._imglst)
        self.Refresh()

    def Clear(self):
        """Delete all the rows """
        self.DeleteAllItems()

    def setcolumnwidths(self):
        root = self.GetRootItem()
        if not root:
            return
        self.SetColumnWidth(VariablesList.COL_NAME, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(VariablesList.COL_VALUE, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(VariablesList.COL_TYPE, wx.LIST_AUTOSIZE)
        namecolwidth = max(self.GetTextExtent(self.colname_name + "          ")[0], self.GetColumnWidth(VariablesList.COL_NAME) + self.tenspaces)
        reprcolwidth = max(self.GetTextExtent(self.colname_value + "          ")[0], self.GetColumnWidth(VariablesList.COL_VALUE) + self.tenspaces)
        typecolwidth = max(self.GetTextExtent(self.colname_type + "          ")[0], self.GetColumnWidth(VariablesList.COL_TYPE) + self.tenspaces)
        self.SetColumnWidth(VariablesList.COL_NAME, namecolwidth)
        self.SetColumnWidth(VariablesList.COL_VALUE, reprcolwidth)
        self.SetColumnWidth(VariablesList.COL_TYPE, typecolwidth)

    def PopulateRows(self, data):
        """Populate the list with the data
        @param data: dictionary of variables info

        """
        root = self.AddRoot("root")
        self.SetItemPyData(root, (self.listtype, False))
        self.SetItemHasChildren(root, True)

        variablelist = [root]

        while len(variablelist) > 0:
            item = variablelist.pop(0)
            self.expand_item(item, data, item is root)

            items = self.GetChildNodes(item)
            variablelist = items + variablelist

        self.setcolumnwidths()

    def UpdateVariablesList(self, variables):
        if not variables:
            return
        self.Clear()
        self.PopulateRows(variables)
        self.Refresh()

    def update_namespace(self, key, expressionlist):
        old_key = self.key
        old_expressionlist = self.get_expression_list()

        if key == old_key:
            expressionlist = old_expressionlist

        self.key = key

        if expressionlist is None:
            expressionlist = [(self.listtype, True)]

        worker = RunProcInThread(self.listtype, self.UpdateVariablesList,
                                 RpdbDebugger().catchexc_get_namespace,
                                 expressionlist, self.FilterLevel)
        worker.start()
        return (old_key, old_expressionlist)

    def OnItemRightClick(self, event):
        item = event.GetItem()
        (expr, is_valid) = self.GetPyData(item)
        if expr in [_("Loading..."), _("Data Retrieval Timeout"),
                    _("Namespace Warning")]:
            return
        wx.CallAfter(self._onitemrightclick, item)

    def _onitemrightclick(self, item):
        varname = self.GetItemText(item, VariablesList.COL_NAME)
        RpdbDebugger().setexpression(varname, True)
        RpdbDebugger().restoreexpressions()
        ed_msg.PostMessage(ed_msg.EDMSG_UI_SB_TXT, (ed_glob.SB_INFO, _("Added %s to PyExpression shelf.") % varname))
            
    def OnItemToolTip(self, event):
        item = event.GetItem()
        tooltip = self.GetItemText(item, VariablesList.COL_VALUE)[1:]
        event.SetToolTip(tooltip)

    def OnItemCollapsing(self, event):
        item = event.GetItem()
        event.Skip()

    def OnItemActivated(self, event):
        item = event.GetItem()
        (expr, is_valid) = self.GetPyData(item)
        if expr in [_("Loading..."), _("Data Retrieval Timeout"),
                    _("Namespace Warning")]:
            return
        wx.CallAfter(self._onitemactivated, item, expr, is_valid)

    def _onitemactivated(self, item, expr, is_valid):
        default_value = self.GetItemText(item, VariablesList.COL_VALUE)[1:]

        if is_valid:
            desc = "The new expression will be evaluated at the debuggee and its value will be set to the item."
            labeltext = "New Expression:"
            style=wx.TE_MULTILINE
        else:
            desc = "The current value of the expression (read only)."
            labeltext = "Current Expression:"
            style=wx.TE_MULTILINE|wx.TE_READONLY

        expr_dialog = ExpressionDialog(self, default_value, "Enter Expression", desc, labeltext, (1000, -1), style)
        pos = self.GetPositionTuple()
        expr_dialog.SetPosition((pos[0] + 50, pos[1] + 50))
        r = expr_dialog.ShowModal()
        if r != wx.ID_OK:
            expr_dialog.Destroy()
            return

        _expr = expr_dialog.get_expression()

        expr_dialog.Destroy()

        _suite = "%s = %s" % (expr, _expr)

        worker = RunProcInThread(self.listtype, self._onitemactivatedcallback,
                                 RpdbDebugger().execute, _suite)
        worker.start()

    def _onitemactivatedcallback(self, res):
        if not res:
            return

        if len(res) == 2:
            warning, error = res
        else:
            error = res

        PyStudioUtils.error_dialog(self, error)

        if not warning in self.ignoredwarnings:
            dlg = wx.MessageDialog(self,
                                   _("%s\n\nClick 'Cancel' to ignore this warning in this session.") % warning,\
                                   _("Warning"),
                                   wx.OK|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_WARNING)
            res = dlg.ShowModal()
            dlg.Destroy()

            if res == wx.ID_CANCEL:
                self.ignoredwarnings[warning] = True

    def OnItemExpanding(self, event):
        item = event.GetItem()
        if not self.ItemHasChildren(item):
            event.Skip()
            return

        if self.get_numberofchildren(item) > 0:
            event.Skip()
            self.Refresh();
            return

        wx.CallAfter(self._onitemexpanding, item)

    def _onitemexpanding(self, item):
        self.DeleteChildren(item)

        child = self.AppendItem(item, _("Loading..."))
        self.SetItemText(child, u' ' + _("Loading..."), VariablesList.COL_VALUE)
        self.SetItemText(child, ' ' + _("Loading..."), VariablesList.COL_TYPE)
        self.SetItemPyData(child, (_("Loading..."), False))

        (expr, is_valid) = self.GetPyData(item)

        item = self.find_item(expr)
        if item == None:
            return

        worker = RunProcInThread(self.listtype, self._itemexpandingcallback,
                                 RpdbDebugger().get_namespace, [(expr, True)],
                                 self.FilterLevel)
        worker.pass_parameter(item)
        worker.start()

    def _itemexpandingcallback(self, variables, item):
        """Callback for when tree node is expanding"""
        children = self.GetChildNodes(item)
        preselect_child = len(children) != 0 and children[0] == self.GetSelection()
        self.DeleteChildren(item)

        if not variables:
            child = self.AppendItem(item, _("Data Retrieval Timeout"))
            self.SetItemText(child, u' ' + _("Data Retrieval Timeout"),
                             VariablesList.COL_VALUE)
            self.SetItemText(child, u' ' + _("Data Retrieval Timeout"),
                             VariablesList.COL_TYPE)
            self.SetItemPyData(child, (_("Data Retrieval Timeout"), False))
            self.Expand(item)

            if preselect_child:
                self.SelectItem(child)
            return

        self.expand_item(item, variables, False, True)

        if preselect_child:
            children = self.GetChildNodes(item)
            self.SelectItem(children[0])

        self.setcolumnwidths()
        self.Refresh()

    # Helper functions
    def get_numberofchildren(self, item):
        nochildren = self.GetChildrenCount(item)
        if nochildren != 1:
            return nochildren

        child = self.GetChildNodes(item)[0]
        (expr, is_valid) = self.GetPyData(child)

        if expr in [_("Loading..."), _("Data Retrieval Timeout")]:
            return 0

        return 1

    def expand_item(self, item, variables, froot=False, fskip_expansion_check=False):
        if not self.ItemHasChildren(item):
            return

        if not froot and not fskip_expansion_check and self.IsExpanded(item):
            return

        if self.get_numberofchildren(item) > 0:
            return

        (expr, is_valid) = self.GetPyData(item)

        variables_with_expr = []
        for expression in variables:
            if hasattr(expression, "get") and expression.get("expr", None) == expr:
                variables_with_expr.append(expression)
        if variables_with_expr == []:
            return

        first_variable_with_expr = variables_with_expr[0]
        if first_variable_with_expr is None:
            return

        if "error" in first_variable_with_expr:
            return

        if first_variable_with_expr["n_subnodes"] == 0:
            self.SetItemHasChildren(item, False)
            return

        #
        # Create a list of the subitems.
        # The list is indexed by name or directory key.
        # In case of a list, no sorting is needed.
        #
        for subnode in first_variable_with_expr["subnodes"]:
            _name = unicode(subnode["name"])
            if not re.match(self.FilterExpr, _name):
                continue
            _type = unicode(subnode["type"])
            _value = PyStudioUtils.get_unicodevalue(subnode["repr"])

            child = self.AppendItem(item, _name)
            self.SetItemText(child, u' ' + _value, VariablesList.COL_VALUE)
            self.SetItemText(child, u' ' + _type, VariablesList.COL_TYPE)
            self.SetItemPyData(child, (subnode["expr"], subnode["fvalid"]))
            self.SetItemHasChildren(child, (subnode["n_subnodes"] > 0))
            # Add some bitmaps depending on the object type
            if subnode["type"] in ('type', 'module'):
                self.SetItemImage(child, self._imgmap[VariablesList.IMG_CLASS])
            elif subnode["type"] in ('function', 'builtin_function_or_method',
                                     'instancemethod'):
                self.SetItemImage(child, self._imgmap[VariablesList.IMG_FUNCT])
            else:
                self.SetItemImage(child, self._imgmap[VariablesList.IMG_VAR])

        self.Expand(item)

    def find_item(self, expr):
        item = self.GetRootItem()
        while item:
            (expr2, is_valid) = self.GetPyData(item)
            if expr2 == expr:
                return item

            item = self.GetNext(item)

        return None

    def GetChildNodes(self, item):
        (child, cookie) = self.GetFirstChild(item)
        children = []

        while child and child.IsOk():
            children.append(child)
            (child, cookie) = self.GetNextChild(item, cookie)

        return children

    def get_expression_list(self):
        if self.GetCount() == 0:
            return None

        item = self.GetRootItem()

        variablelist = [item]
        expressionlist = []

        while len(variablelist) > 0:
            item = variablelist.pop(0)
            (expr, is_valid) = self.GetPyData(item)
            fExpand = self.IsExpanded(item) and self.get_numberofchildren(item) > 0
            if not fExpand:
                continue

            expressionlist.append((expr, True))
            items = self.GetChildNodes(item)
            variablelist = items + variablelist

        return expressionlist
