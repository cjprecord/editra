# -*- coding: utf-8 -*-

__name__ = u'documentation#'
__type__ = u'help'
__desc__ = u'Gives you help on how to use the Macro Launcher'


def run(txtctrl=None, nbook=None, log=None,**kwargs):
  if nbook:
      nbook.NewPage()
      nbook.GoCurrentPage()
      page = nbook.GetCurrentPage()
      page.SetText(get_help_text())

def get_help_text():
    return '''
Macro Launcher - Help
--------------------


Macro Launcher (MLauncher) helps you to write short (or long) python
scripts and execute them. If you understand python, you can do virtually
anything

- automate tasks inside Editra (e.g. sorting files, removing spaces)
- help developing plugins (I am using it to reload plugins when I do some changes)
- change Editra settings, GUI etc.
- run testunits for Editra development
- script external programs, fire up tasks in threads

As a short note: I am calling the scripts inside MLauncher "macros" but
they are just normal python code (that you have to write or download)


What you need to do:
--------------------
1. Click on New Macro
   - new editor with a basic template will open
2. Write your code
   - when you hit Ctrl+Save, the code of the plugin is automatically
     reloaded
3. Run the macro
   - by double-clicking it
   - by clicking on the icon "Run"
   - by pressing Enter


Macro types:
----------------

There are two types of macros:
 1. blocking macro (started by call run())
 2. threaded macro (started by call to run_thread())

Threaded calls are started in a new thread (yes, you guessed it) which
means that editor remains responsive even if the macro is running -
and it can do some very complicated calculations, database queries etc.

If you use run_thread() for tasks that interact with Editra, a lot of
caution is needed. Because some operations are allowed only from the main
thread. For instances if you do this, Editra will crash (and you won't
even have time to blink):

This will kill your editor:

    def run_thread(nbook = None, **kwargs):
      nbook.AddPage()

This will be fine (call from main thread):

    import wx

    def run_thread(nbook = None, **kwargs):
      wx.CallAfter(nbook.AddPage)

For the best performance, the function run_thread() should periodically
return by yield():

    import time
    def run_thread(**kwargs):
        for x in range(5):
            time.sleep(.5)
            yield x

Look at the supplied macros to see examples. Try to select all macros
of type 'thread', right-click and choose run. You can start threaded
and non-threaded macros together. If the threaded macros are first on
the list, you will not wait.


Macro Arguments:
----------------
These are the keyword arguments available to your macros:
  txtctrl: wx.stc current editor
  nbook: notebook instance
  win: the main window
  log: log method for writing into the Editra log
  mlauncher: macro launcher instance (plugin)


Interesting (perhaps) info:
---------------------------
Where are the macros saved?
    They are saved inside the .Editra configuration directory (.Editra/macros)
    Where you can edit them, delete, copy etc. (But use the plugin interface
    for that)

To protect macro:
    Insert '#' in the name. Editor will refuse to delete/edit such a macro.

Example macros:
    Together with the plugin, you will find some example macros. This help is
    one of them. They are installed automatically (and may be overwritten by
    new versions, so do not save your work in them!)

Macro filenames
    The automatically created macro have special filename, but it is not important
    to follow any conventions. Except for one. The macros that have in its name
    '_overwrite.' may get overwritten by future updates.


About - credits:
----------------
- The idea of the Macro Launcher comes from the Pype editor.
- Parts of the code from the commentbrowser by DR0ID (dr0iddr0id at googlemail com)
- Of course, MLauncher is using Editra codebase
- The little what is left is by me, rca (http://www.roman-chyla.net)


TODO:
-----
- repository of downloadable macros?



  '''
