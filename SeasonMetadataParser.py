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
import os
from PmsRequestHandler import *
from BaseMetadataParser import *

class SeasonMetadataParser(BaseMetadataParser):
    """docstring for SeasonMetadataParser"""
    def __init__(self, opts, season_container, show):
        super(SeasonMetadataParser, self).__init__(opts)
        self.show = show
        
        self.key = season_container.attrib['key']
        self.type = season_container.get('type', "")
        self.title = season_container.get('title', "")
        self.index = season_container.get('index', "")
        self.thumb = season_container.get('thumb', "")
        self.leaf_count = season_container.get('leafCount', "1")
    #end def __init__
    
    def name(self):
        return "%s - %s" % (self.show.name(), self.title)
    #end def name
#end class SeasonMetadataParser