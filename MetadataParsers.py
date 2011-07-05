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

class MetadataParser(object):
    """docstring for MovieMetadataParser"""
    def __init__(self, opts, video_metadata_container):
        self.opts = opts
        media_container = video_metadata_container.getroot()
        videos = media_container.getchildren()
        if len(videos) != 1:
            return
        #end if len
        self.video = videos[0]
        media_paths = self.media_paths()
        self.file_types = map(lambda x: os.path.splitext(x)[1], media_paths)
        self.local_image_path = ""
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
        return ""
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
    

class MovieMetadataParser(MetadataParser):
    """docstring for MovieMetadataParser"""
    def __init__(self, opts, video_metadata_container):
        super(MovieMetadataParser, self).__init__(opts, video_metadata_container)
        
        self.studio = self.video.get('studio', "")
        self.type = self.video.get('type', "")
        self.title = self.video.get('title', "")
        self.content_rating = self.video.get('contentRating', "") #PG-13, etc.
        self.summary = self.video.get('summary', "")
        self.rating = self.video.get('rating', "") #not used
        self.year = self.video.get('year', "")
        self.tagline = self.video.get('tagline', "")
        self.thumb = self.video.get('thumb', "")
        self.originally_available_at = self.video.get('originallyAvailableAt', "")
        
        self.genre_names = self.array_of_attributes_with_key_from_child_nodes_with_name(self.video, "Genre", "tag")
        if len(self.genre_names) > 0: 
            self.genre = self.genre_names[0] 
        else: 
            self.genre = ''
        self.genres = ', '.join(self.genre_names)
        
        self.writer_names = self.array_of_attributes_with_key_from_child_nodes_with_name(self.video, "Writer", "tag")
        self.writers = ', '.join(self.writer_names)
        
        self.director_names = self.array_of_attributes_with_key_from_child_nodes_with_name(self.video, "Director", "tag")
        self.directors = ', '.join(self.director_names)
        
        self.cast_names = self.array_of_attributes_with_key_from_child_nodes_with_name(self.video, "Role", "tag")
        self.cast = ', '.join(self.cast_names)
    #end def __init__
    
    def name(self):
        return "%s (%s)" % (self.title, self.year)
    #end def name
    
    def get_local_image_path(self):
        request_handler = PmsRequestHandler()
        partial_image_url = self.video.attrib['thumb']
        logging.error("Downloading artwork...")
        self.local_image_path = request_handler.download_image(self.name(), partial_image_url)
    #end image_path
            
    
    def tag_string(self):        
        tag_string = ""
        
        if self.local_image_path == "":
            self.get_local_image_path()
        tag_string += self.new_tag_string_entry("Artwork", self.local_image_path)
        
        tag_string += self.new_tag_string_entry("Studio", self.studio)
        
        mediaType = ""
        if self.type == 'movie':
            mediaType = "Movie"
        elif self.type == 'show':
            mediaType = "TV Show"
        #end if self.type
        tag_string += self.new_tag_string_entry("Media Kind", mediaType)
        
        tag_string += self.new_tag_string_entry("Name", self.title)
        tag_string += self.new_tag_string_entry("Rating", self.content_rating)
        tag_string += self.new_tag_string_entry("Long Description", self.summary)
        tag_string += self.new_tag_string_entry("Release Date", self.originally_available_at)
        tag_string += self.new_tag_string_entry("Description", self.tagline if len(self.tagline) > 0 else self.summary)
        
        tag_string += self.new_tag_string_entry("Genre", self.genre) #single genre
        tag_string += self.new_tag_string_entry("Screenwriters", self.writers)
        tag_string += self.new_tag_string_entry("Director", self.directors)
        tag_string += self.new_tag_string_entry("Cast", self.cast)
        
        hd_value = "%d" % (1 if self.is_HD() else 0)
        tag_string += self.new_tag_string_entry("HD Video", hd_value)
        
        return tag_string.strip()
    #end def tag_string
#end class MovieMetadataParser
