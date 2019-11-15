# -*- coding: utf-8 -*-

__name__ = u'thread1'
__type__ = u'example'
__desc__ = u'Fast thread that prints into log - select both and right-click to run'

import time

def run_thread(log=None, **kwargs):
  for x in range(50):
      time.sleep(.1)
      if callable(log):
        log('thread1 printing')
      yield 
