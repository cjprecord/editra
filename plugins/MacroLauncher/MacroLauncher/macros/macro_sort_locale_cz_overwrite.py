# -*- coding: utf-8 -*-

__name__ = 'sort-example'
__type__ = 'example'
__desc__ = 'Sort lines by Czech locale'

import locale

def run(txtctrl = None, **kwargs):
    locale.setlocale(locale.LC_ALL,"cz")
    if txtctrl:
        lines = txtctrl.GetText().splitlines()
        lines.sort(cmp=locale.strcoll)
        txtctrl.SetText(txtctrl.GetEOLChar().join(lines))
