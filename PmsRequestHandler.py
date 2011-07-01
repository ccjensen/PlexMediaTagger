#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
import logging
import sys

class PmsRequestHandler:
    """docstring for PmsRequestHandler"""
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.baseUrl = "http://%s:%s" % (self.ip, self.port)
    #end def __init__
    
    def getContents(self, url):
        contents = []
        try:
            contents = etree.parse(url)
        except IOError, e:
            logging.debug(e)
            logging.critical("Could not connect to server %s:%s" % (self.ip, self.port))
            sys.exit(1)
        #end try
        return contents
    #end getSectionsList
    
    def getSectionsContainer(self):
        url = "%s/library/sections" % (self.baseUrl)
        return self.getContents(url)
    #end getSectionsContainer
    
    def getSectionAllContainerForKey(self, sectionKey):
        url = "%s/library/sections/%s/all" % (self.baseUrl, sectionKey)
        return self.getContents(url)
    #end getSection
    
    def getMetadataContainerForKey(self, partialUrl):
        url = "%s%s" % (self.baseUrl, partialUrl)
        return self.getContents(url)
    #end getSection
    
#end class PmsRequestHandler 