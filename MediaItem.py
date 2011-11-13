#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from BaseItem import *
from PartItem import *

class MediaItem(BaseItem):
    """docstring for MediaItem"""
    def __init__(self, opts, video_item, media_element):
        super(MediaItem, self).__init__(opts)
        self.opts = opts
        self.video_item = video_item
        self.media_element = media_element
        
        resolution = self.media_element.get('videoResolution', "")
        self.is_HD = resolution.isdigit() and int(resolution) >= 720
        
        part_element = self.media_element.find("Part")
        self.part_item = PartItem(self.opts, self, part_element)
    #end def __init__
    
    def tag_string(self):
        tag_string = self.video_item.tag_string()
        
        hd_value = "%d" % (1 if self.is_HD else 0)
        tag_string += self.new_tag_string_entry("HD Video", hd_value)
        
        return tag_string
    #end def tag_string
#end class MediaItem