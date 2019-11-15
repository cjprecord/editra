# -*- coding: utf-8 -*-

__name__ = u'thread2'
__type__ = u'example'
__desc__ = u'Slower thread that prints into log - select both and right-click to run'

import time

def run_thread(log=None, **kwargs):
  for x in range(25):
      time.sleep(.2)
      if callable(log):
        log('thread2 printing')
      yield 
