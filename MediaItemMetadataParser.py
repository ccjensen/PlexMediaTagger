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
from MediaPart import *

class MediaItemMetadataParser(BaseMetadataParser):
    """docstring for MediaItemMetadataParser"""
    def __init__(self, opts, item_metadata_container):
        super(MediaItemMetadataParser, self).__init__(opts)
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
            self.media_parts = self.media_parts()
            self.local_image_path = ""
            self.updated_at = self.video.get('updatedAt', "")
            self.view_count = self.video.get('viewCount', "0")
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
    
    def media_parts(self):
        media_node = self.video.find("Media")
        media_paths = self.array_of_attributes_with_key_from_child_nodes_with_name(media_node, "Part", "file")
        media_parts = []
        for path in media_paths:
            media_part = MediaPart(self.opts, self, path)
            media_parts.append(media_part)
        #end for
        return media_parts
    #end media_parts

    def is_HD(self):
        mediaNode = self.video.find("Media")
        resolution = mediaNode.attrib['videoResolution']
        return resolution.isdigit() and int(resolution) >= 720
    #end isHD
    
    def tag_string(self):
        tag_string = ""
        tag_string += self.new_tag_string_entry("Comments", self.media_parts[0].getCommentTagContents())
        return tag_string
    #end def tag_string
    
    def new_tag_string_entry(self, key, value):
        try:
            #example: " blah blah: it's time to {come} home blah   "
            #becomes: "blah blah&#58; it's time to &#123;come&#125; home blah"
            cleaned_up_value = value.strip()
            cleaned_up_value = cleaned_up_value.replace('{', "&#123;")
            cleaned_up_value = cleaned_up_value.replace('}', "&#125;")
            cleaned_up_value = cleaned_up_value.replace(':', "&#58;")
            #example: "'{Long Description:blah blah...}'"
            return '{%s:%s}' % (key, value.strip())
        except AttributeError, e:
            return ""
        #end try
    #end def new_tag_string_entry
#end class MetadataParser