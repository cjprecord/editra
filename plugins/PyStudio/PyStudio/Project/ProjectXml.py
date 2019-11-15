###############################################################################
# Name: ProjectXml.py                                                         #
# Purpose: Project Xml classes                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Project File

"""

# Test example xml
xml_str = """
<project name="FooBar">
    <optionset name='general'>
        <option type="" value=""/>
    </optionset>
    <package name="FooPy" path="./foo/bar">
        <optionset name="test">
            <option type="" value=""/>
        </optionset>
        <package name="FooTest" path="./foo/bar/test">
            <optionset name="custom">
                <option type="" value=""/>
            </optionset>
        </package>
    </package>
    <folder name="FooData" path="/foo/bar">
        <optionset name="general">
            <option type="" value=""/>
        </optionset>
    </folder>
</project>

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: ProjectXml.py 1530 2012-04-27 19:55:43Z CodyPrecord $"
__revision__ = "$Revision: 1530 $"

#-----------------------------------------------------------------------------#
# Imports
#import sys
#sys.path.append(r"/home/jigorou/Editra/src") # TEST

# Editra Imports
import ed_xml

# Constants
PYPROJ_XML_SCHEMA_VERSION = "1.0"

#-----------------------------------------------------------------------------#

class Option(ed_xml.EdXml):
    """General Option
    <option type="view" value="*.py"/>

    """
    class meta:
        tagname = "option"
    type = ed_xml.String(required=True)
    value = ed_xml.String(required=True)

class OptionSet(ed_xml.EdXml):
    """Collection of Options used for grouping
    option categories together.
    <optionset name="analysis">
        <option name='' value=''/>
    </optionset>

    """
    class meta:
        tagname = "optionset"
    name = ed_xml.String(required=True)
    options = ed_xml.List(ed_xml.Model(type=Option))

    def __GetOption(self, optname):
        for option in self.options:
            if option.type == optname:
                return option
        return None

    def DeleteOption(self, optname):
        """Remove an option from the set"""
        opt = self.__GetOption(optname)
        if opt:
            self.options.remove(opt)

    def GetOption(self, optname):
        """Get an option from the set
        @param optname: option name
        @return: L{Option}

        """
        opt = self.__GetOption(optname)
        return opt

    def SetOption(self, optname, value):
        """Set an options value"""
        opt = self.__GetOption(optname)
        if opt:
            # Update Existing value
            opt.value = value
        else:
            # Add new option to set
            self.options.append(Option(type=optname, value=value))

class File(ed_xml.EdXml):
    """Xml element to represent a file item (used by ProjectTemplate)
    <file name='__init__.py'>
        # File: __init__.py
        ''' docstring '''
    </file>

    """
    class meta:
        tagname = "file"
    name = ed_xml.String(required=True)
    data = ed_xml.String(tagname="data", required=False) # optional specify initial file contents

class Folder(ed_xml.EdXml):
    """General folder container
    <folder path="/foo/test></folder>"

    """
    class meta:
        tagname = "folder"
    name = ed_xml.String(required=True)
    optionsets = ed_xml.List(ed_xml.Model(type=OptionSet), required=False)
    packages = ed_xml.List(ed_xml.Model("package"), required=False)
    folders = ed_xml.List(ed_xml.Model("folder"), required=False)
    files = ed_xml.List(ed_xml.Model(type=File), required=False)

    def CreateOptionSet(self, setname):
        """Create a new option set. If an existing set of the
        same name already exists it will be returned instead
        @param setname: name to associate with the set
        @return: the option set

        """
        optset = self.GetOptionSet(setname)
        if optset is None:
            optset = OptionSet(name=setname)
            self.optionsets.append(optset)
        return optset

    def GetOptionSet(self, setname):
        """Get the set of options associated with a given name
        @param setname: name of set
        @return: L{OptionSet} or None

        """
        for optset in self.optionsets:
            if optset.name == setname:
                return optset
        return None

class PyPackage(Folder):
    """Python package directory. Container for python modules."""
    class meta:
        tagname = "package"

class ProjectXml(Folder):
    """Main project structure"""
    class meta:
        tagname = "project"
    version = ed_xml.String(default=PYPROJ_XML_SCHEMA_VERSION)

#-----------------------------------------------------------------------------#
# Test
#if __name__ == '__main__':
#    proj = ProjectXml()
#    proj.name = "FooBar"

#    pkg = PyPackage()
#    pkg.name = "foopackage"
#    pkg.path = "/foo/bar"

#    opt = Option()
#    opt.type = "wildcard"
#    opt.value = "*.py"

#    pkg.options.append(opt)
#    proj.packages.append(pkg)

#    tst = Folder()
#    tst.name = "TestFolder"
#    tst.path = r"C:\FooBar\test"

#    proj.folders.append(tst)

#    pp = Option()
#    pp.type = "PYTHONPATH"
#    pp.value = r"C:\Python26;C:\Desktop"

#    proj.options.append(pp)
#    print proj.PrettyXml
#    print "------------------------"
#    proj = ProjectXml.LoadString(xml_str)
#    print proj.PrettyXml
