###############################################################################
# Name: emachine.py                                                           #
# Purpose: Text Encoder/Decoder Tools                                         #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2012 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""Text Encoder/Decoder interface
  * Base16 encoder/decoder
  * Base32 encoder/decoder
  * Base64 encoder/decoder

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id:  $"
__revision__ = "$Revision:  $"

#-----------------------------------------------------------------------------#
# Imports
import base64

# Editra Libraries
import ebmlib

#-----------------------------------------------------------------------------#

class EnigmaMachine(ebmlib.FactoryMixin):
    """Encoder decoder interface"""
    @classmethod
    def GetMetaDefaults(cls):
        """Get all default meta values for this classes meta data.
        @return: dict(string=value,...)

        """
        return dict(id=-1)

    def encode(self, txt):
        """Encode the text with the current encoder
        @param txt: text to encode
        @return: encoded string

        """
        return txt

    def decode(self, txt):
        """Decode the text with the current decoder
        @param txt: text to decode
        @return: decoded string

        """
        return txt

#-----------------------------------------------------------------------------#

class Base16(EnigmaMachine):
    class meta:
        id = "base16"

    def encode(self, txt):
        """Encode the text with the current encoder
        @param txt: text to encode
        @return: encoded string

        """
        return base64.b16encode(txt)

    def decode(self, txt):
        """Decode the text with the current decoder
        @param txt: text to decode
        @return: decoded string

        """
        try:
            txt = txt.replace("\n", "") # handle decode of unix eol
            txt = base64.b16decode(txt)
        except TypeError:
            pass # Log to status bar of error
        return txt

class Base32(EnigmaMachine):
    class meta:
        id = "base32"

    def encode(self, txt):
        """Encode the text with the current encoder
        @param txt: text to encode
        @return: encoded string

        """
        return base64.b32encode(txt)

    def decode(self, txt):
        """Decode the text with the current decoder
        @param txt: text to decode
        @return: decoded string

        """
        try:
            txt = base64.b32decode(txt)
        except TypeError:
            pass # Log to status bar of error
        return txt

class Base64(EnigmaMachine):
    class meta:
        id = "base64"

    def encode(self, txt):
        """Encode the text with the current encoder
        @param txt: text to encode
        @return: encoded string

        """
        return base64.b64encode(txt)

    def decode(self, txt):
        """Decode the text with the current decoder
        @param txt: text to decode
        @return: decoded string

        """
        try:
            txt = base64.b64decode(txt)
        except TypeError:
            pass # Log to status bar of error
        return txt

