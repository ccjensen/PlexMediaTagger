#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
from BaseItem import *
from StreamItem import *

class PartItem(BaseItem):
    """docstring for PartItem"""
    def __init__(self, opts, media_parser, node):
        super(PartItem, self).__init__(opts)
        self.opts = opts
        self.media_parser = media_parser
        self.part_node = node
        
        self.file = self.part_node.attrib['file']
        self.file_type = os.path.splitext(self.file)[1]
        
        self.duration = self.part_node.attrib['duration']
        self.size = self.part_node.attrib['size']
        
        stream_nodes = self.part_node.findall("Stream")
        self.stream_parsers = []
        for stream_node in stream_nodes:
            stream_parser = StreamItem(self.opts, self, stream_node)
            self.stream_parsers.append(stream_parser)
        #end for stream_nodes
    #end def __init__
    
    def tag_string(self):
        tag_string = self.media_parser.tag_string()
        return tag_string
    #end def tag_string
    
#end class PartItem