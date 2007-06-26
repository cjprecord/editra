#/usr/bin/env python
# Some Comments about this file

__author__ = "Cody Precord"
__doc__ = """A test file for checking styles for the python highlighter.
          Its really quite a pointless script.
          
          """

import sys

def add(a, b):
    """A function to add two numbers"""
    return a + b

def say_hello():
    """Prints hello world to the console"""
    print "Hello World"

class Greeting:
    """A class to represent a greeting"""
    def __init__(self, language):
        """initializes the greeting"""
        self._lang = language

    def __str__(self):
        """Returns the string representation of the greeting"""
        if self._lang == "English":
            return "Hello"
        elif self._lang == "Spanish":
            return "Holla"
        else:
            return "Sorry I dont know %s" % self._lang

if __name__ == '__main__':
    say_hello()
    print '1 + 1 = %d' % add(1, 1)
    print Greeting('English')

    