###############################################################################
# Name: ProjectUtil.py                                                        #
# Purpose: Project Utility Classes and Methods                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Project Utilties


"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ProjectUtil.py 1539 2012-06-07 18:56:39Z CodyPrecord $"
__revision__ = "$Revision: 1539 $"

#-----------------------------------------------------------------------------#
# Dependencies
import wx

# Editra Libraries
import ed_glob
import syntax.synglob as synglob

# Local Libraries
import PyStudio.Common.Images as Images

#-----------------------------------------------------------------------------#


class FileIcons:
    """Namespace object for managing an IconList for a file tree."""
    # ImageList indexes
    IMAGES = range(5)
    IMG_FOLDER,\
    IMG_NO_ACCESS,\
    IMG_PACKAGE,\
    IMG_FILE,\
    IMG_PYTHON = IMAGES
    IMGMAP = { IMG_FOLDER  : ed_glob.ID_FOLDER,
               IMG_PACKAGE : ed_glob.ID_PACKAGE,
               IMG_FILE    : ed_glob.ID_FILE,
               IMG_PYTHON  : synglob.ID_LANG_PYTHON,
               IMG_NO_ACCESS : ed_glob.ID_STOP }
    # Non-themed images
    IMG_PROJECT = IMG_PYTHON + 1
    IMG_IMAGE   = IMG_PROJECT + 1

    @classmethod
    def PopulateImageList(cls, imglist):
        """Populate an ImageList with the icons for the file tree
        @param imglist: wx.ImageList instance (16x16)

        """
        imglist.RemoveAll()
        for img in FileIcons.IMAGES:
            imgid = FileIcons.IMGMAP[img]
            bmp = wx.ArtProvider_GetBitmap(str(imgid), wx.ART_MENU)
            imglist.Add(bmp)
        # Non themed images
        imglist.Add(Images.Project.Bitmap)
        imglist.Add(Images.Picture.Bitmap)
