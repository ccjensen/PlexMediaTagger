#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from BaseItem import *
from StreamItem import *
from urllib2 import unquote
from unicodedata import normalize

class PartItem(BaseItem):
    """docstring for PartItem"""
    def __init__(self, opts, media_item, part_element):
        super(PartItem, self).__init__(opts)
        self.opts = opts
        self.media_item = media_item
        self.part_element = part_element
        
        file_path = self.part_element.attrib['file']
        self.file_path = normalize('NFC', unquote(file_path).decode('utf-8'))
        self.file_type = os.path.splitext(self.file_path)[1]
        self.duration = self.part_element.get('duration', "")
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
    
    def modified_file_path(self):
        new_file_path = self.file_path
        #loops through all the find&replace operations passed in on the cli
        logging.debug( "original path %s" % self.file_path)
        for path_modification in self.opts.path_modifications:
            find_string = path_modification[0]
            replace_string = path_modification[1]
            new_file_path = new_file_path.replace(find_string, replace_string)
        #end for
        logging.debug( "modified path %s" % new_file_path)
        return new_file_path
    #end def modified_file_path
    
#end class PartItem