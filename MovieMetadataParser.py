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
from MediaItemMetadataParser import *
from PmsRequestHandler import *

class MovieMetadataParser(MediaItemMetadataParser):
    """docstring for MovieMetadataParser"""
    def __init__(self, opts, movie_metadata_container):
        super(MovieMetadataParser, self).__init__(opts, movie_metadata_container)
        
        self.key = self.video.attrib['key']
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
        partial_image_url = self.thumb
        logging.info("Downloading artwork...")
        self.local_image_path = request_handler.download_image(self.name(), partial_image_url)
    #end image_path
            
    
    def tag_string(self):        
        tag_string = super(MovieMetadataParser, self).tag_string()
        
        if self.local_image_path == "":
            self.get_local_image_path()
        tag_string += self.new_tag_string_entry("Artwork", self.local_image_path)
        
        tag_string += self.new_tag_string_entry("Studio", self.studio)
        
        tag_string += self.new_tag_string_entry("Media Kind", "Movie")
        
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