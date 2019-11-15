# author = Minjae Kim
# ipython shell output management module
import re
import config
import wx

def dbgtrap(text):
    #filename = r'/home/m/test2.py'
    #textmatch = re.match(r'\('+filename+r':1\):', text)
       
    # in the case the output contains line info
    textmatch = re.match(r'\d+ ', text)
    if textmatch:
        linenum = textmatch.group(0)
        # Method 1: using selection
        p1 = config.ed_stc.PositionFromLine(int(linenum)-1)
        config.ed_stc.SetSelection(p1, p1)
        config.ed_stc.SetSelectionMode(2)
        text = ''

    return text
