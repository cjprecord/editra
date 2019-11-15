###############################################################################
# Name: CAResultsXml.py                                                       #
# Purpose: XML Persistance class for Code Analysis Results                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2011 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Stores and Loads Code Analysis Results to and from XML

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id: CAResultsXml.py 1518 2011-12-05 01:21:51Z CodyPrecord@gmail.com $"
__revision__ = "$Revision: 1518 $"

#-----------------------------------------------------------------------------#
# Imports
import ed_xml

#-----------------------------------------------------------------------------#

class Result(ed_xml.EdXml):
    """Individual result
    <result line="0" errType="Warning" errMsg="Line too long"/>

    """
    class meta:
        tagname = "result"
    line = ed_xml.String(required=True)
    errType = ed_xml.String(required=True)
    errMsg = ed_xml.String(required=True)

class AnalysisResults(ed_xml.EdXml):
    """Top level XML object
    <pylint path="/path/to/file"></pylint>

    """
    class meta:
        tagname = "pylint"
    path = ed_xml.String(required=True)
    results = ed_xml.List(ed_xml.Model(Result))

    def AddResult(self, line, errType, errMsg):
        """Add a result to the result list
        @param line: line number
        @param errType: error type identifier
        @param errMsg: error message text

        """
        result = Result()
        result.line = line
        result.errType = errType
        result.errMsg = errMsg
        self.results.append(result)

class ProjectAnalysis(ed_xml.EdXml):
    """Collection of L{AnalysisResults} for an entire project"""
    class meta:
        tagname = "projectanalysis"
    name = ed_xml.String(require=True) # Project Name
    resultsets = ed_xml.List(ed_xml.Model(type=AnalysisResults))
