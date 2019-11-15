from setuptools import setup
 
__author__ = "Minjae Kim"
__doc__ = """Extended IPython Shell"""
__version__ = "0.0.1"
 
setup(
      name    = "xpyshell",    # Plugin Name
      version = __version__,   # Plugin Version
      description = __doc__,   # Short plugin description
      author = __author__,     # Your Name
      author_email = "the.minjae[at]gmail.com",  # Your contact
      license = "wxWindows",       # Plugins licensing info
      packages = ['xpyshell','ipythonmod','pyreadline'], # Package directory name(s)
      entry_points = '''
      [Editra.plugins]
      xPyShell = xpyshell:xPyShell
      '''
     )
