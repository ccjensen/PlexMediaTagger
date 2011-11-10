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
        super(StreamMetadataParser, self).__init__(opts, node)
        self.opts = opts
        self.part_parser = part_parser
        self.stream_node = node
        
        self.stream_type = self.part_node.get('streamType', "")
        self.codec = self.part_node.get('codec', "")
        self.channels = self.part_node.get('channels', "")
        self.language = self.part_node.get('language', "")
        self.language_code = self.part_node.get('languageCode', "")
        
        self.file = self.part_node.attrib['file']
        self.file_type = os.path.splitext(self.path)[1]
        
        self.duration = self.part_node.attrib['duration']
        self.size = self.part_node.attrib['size']
    #end def __init__