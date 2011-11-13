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
from DataTokens import *

class VideoItem(BaseItem):
    """docstring for VideoItem"""
    def __init__(self, opts, media_container):
        super(VideoItem, self).__init__(opts)
        try:
            media_container_element = media_container.getroot()
        except AttributeError, e:
            self.video = media_container
            return #this will happen if it's not a detailed metadata container
        else:
            videos = media_container_element.getchildren()
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
    
    def name(self):
        return "Generic Name"
    #end def name
    
    def create_new_comment_tag_contents(self):        
        rating = int( float(self.rating) * 10 )
        rating_str = "%s%i" % (DataTokens.itunes_rating_token, rating)
        play_count_str = DataTokens.itunes_playcount_token + self.view_count
        updated_at_str = DataTokens.updated_at_token + self.updated_at
        
        itunes = [DataTokens.itunes_tag_data_token, rating_str, play_count_str, updated_at_str]
        itunes_str = DataTokens.tag_data_delimiter.join(itunes)
        return itunes_str
    #end create_new_comment_tag_contents
    
    def tag_string(self):
        tag_string = ""
        tag_string += self.new_tag_string_entry("Comments", self.create_new_comment_tag_contents())
        return tag_string.strip()
    #end def tag_string
#end class VideoItem