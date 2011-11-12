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
from BaseItem import *

class VideoItem(BaseItem):
    """docstring for VideoItem"""
    def __init__(self, opts, media_container_node):
        super(VideoItem, self).__init__(opts)
        try:
            media_container = media_container_node.getroot()
        except AttributeError, e:
            self.video = media_container_node
            return #this will happen if it's not a detailed metadata container
        else:
            videos = media_container.getchildren()
            if len(videos) != 1:
                logging.critical("ERROR, MORE THAN ONE VIDEO TAG. ABORT")
                return
            #end if len
            self.video = videos[0]
            self.local_image_path = ""
            self.updated_at = self.video.get('updatedAt', "")
            self.view_count = self.video.get('viewCount', "0")
        #end try
    #end def __init__
    
    def array_of_attributes_with_key_from_child_nodes_with_name(self, node, node_name, key):
        result = [""]
        nodes = node.findall(node_name)
        if len(nodes) > 0:
            result = map(lambda n: n.attrib[key], nodes)
        return result
    #end def array_of_attributes_with_key_from_child_nodes_with_name
    
    def name(self):
        return "Generic Name"
    #end def name
#end class MetadataParser