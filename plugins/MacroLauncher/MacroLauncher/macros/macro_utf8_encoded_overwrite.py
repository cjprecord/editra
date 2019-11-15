# -*- coding: utf-8 -*-

__name__ = u'\u017elut\xfd \u010dern\xfd k\u016f\u0148'
__type__ = u'example'
__desc__ = u'Example of macro that contains accented chars and writes utf-8'

def run(txtctrl=None, nbook=None, log=None,**kwargs):
  global name
  #first create a new page
  if nbook:
      nbook.NewPage()
      nbook.GoCurrentPage()
      page = nbook.GetCurrentPage()
      #set some encoded string
      test = u'\u017elut\xfd \u010dern\xfd k\u016f\u0148'
      page.SetText(test)

      #then get the text back
      txt = page.GetText().strip()

      #write results back
      res = u''
      res += u'This macro: %s\n' % name
      res += u'Has written utf-8 encoded string into the buffer\n'
      res += u'then read it back\n'
      res += u'And here is the result:\n'
      res += u'Written: %s\n' % test
      res += u'Read: %s\n' % txt
      res += u'Repr: %s == %s\n' % (repr(txt), r"u'\u017elut\xfd \u010dern\xfd k\u016f\u0148'")
      res += u'Test succeeded: %s\n' % (txt == test)
      page.SetText(res)

