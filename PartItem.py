#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from BaseItem import *
from StreamItem import *

class PartItem(BaseItem):
    """docstring for PartItem"""
    def __init__(self, opts, media_item, part_element):
        super(PartItem, self).__init__(opts)
        self.opts = opts
        self.media_item = media_item
        self.part_element = part_element
        
        self.file = self.part_element.attrib['file']
        self.file_type = os.path.splitext(self.file)[1]
        
        self.duration = self.part_element.attrib['duration']
        self.size = self.part_element.attrib['size']
        
        stream_elements = self.part_element.findall("Stream")
        
        self.stream_items = []
        for stream_element in stream_elements:
            stream_item = StreamItem(self.opts, self, stream_element)
            self.stream_items.append(stream_item)
        #end for stream_elements
    #end def __init__
    
    def tag_string(self):
        tag_string = self.media_item.tag_string()
        return tag_string
    #end def tag_string
    
#end class PartItem