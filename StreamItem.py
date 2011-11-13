#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
from BaseItem import *

class StreamItem(BaseItem):
    """docstring for StreamItem"""
    def __init__(self, opts, part_item, stream_element):
        super(StreamItem, self).__init__(opts)
        self.opts = opts
        self.part_item = part_item
        self.stream_element = stream_element
        
        self.stream_type = self.stream_element.get('streamType', "")
        self.codec = self.stream_element.get('codec', "")
        self.channels = self.stream_element.get('channels', "")
        self.language = self.stream_element.get('language', "")
        self.language_code = self.stream_element.get('languageCode', "")
    #end def __init__
#end class StreamItem