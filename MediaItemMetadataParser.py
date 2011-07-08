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

class MediaItemMetadataParser(BaseMetadataParser):
    """docstring for MediaItemMetadataParser"""
    def __init__(self, opts, item_metadata_container):
        super(MediaItemMetadataParser, self).__init__(opts)
        self.comments = "Tagged by PlexMediaTagger"
        
        try:
            media_container = item_metadata_container.getroot()
        except AttributeError, e:
            self.video = item_metadata_container
            return #this will happen if it's not a detailed metadata container
        else:
            videos = media_container.getchildren()
            if len(videos) != 1:
                return
            #end if len
            self.video = videos[0]
            media_paths = self.media_paths()
            self.local_image_path = ""
        #end try
    #end def __init__
    
    def array_of_attributes_with_key_from_child_nodes_with_name(self, video, node_name, key):
        result = [""]
        nodes = video.findall(node_name)
        if len(nodes) > 0:
            result = map(lambda n: n.attrib[key], nodes)
        return result
    #end def arrayOfTagAttributesFromNodesWithName
    
    def name(self):
        return "Generic Name"
    #end def name
    
    def media_paths(self):
        media_node = self.video.find("Media")
        return self.array_of_attributes_with_key_from_child_nodes_with_name(media_node, "Part", "file")
    #end isHD

    def is_HD(self):
        mediaNode = self.video.find("Media")
        resolution = mediaNode.attrib['videoResolution']
        return resolution.isdigit() and int(resolution) >= 720
    #end isHD
    
    def tag_string(self):
        tag_string = ""
        tag_string += self.new_tag_string_entry("Comments", self.comments)
        return tag_string
    #end def tag_string
    
    def new_tag_string_entry(self, key, value):
        try:
            #example: "{'Long Description':'blah blah it\'s time to come home blah'}"
            return '{%s:%s}' % (key, value.strip())
        except AttributeError, e:
            return ""
        #end try
    #end def new_tag_string_entry
#end class MetadataParser