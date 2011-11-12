#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
from BaseMetadataParser import *

class StreamMetadataParser(BaseMetadataParser):
    """docstring for StreamMetadataParser"""
    def __init__(self, opts, part_parser, node):
        super(StreamMetadataParser, self).__init__(opts)
        self.opts = opts
        self.part_parser = part_parser
        self.stream_node = node
        
        self.stream_type = self.stream_node.get('streamType', "")
        self.codec = self.stream_node.get('codec', "")
        self.channels = self.stream_node.get('channels', "")
        self.language = self.stream_node.get('language', "")
        self.language_code = self.stream_node.get('languageCode', "")
    #end def __init__