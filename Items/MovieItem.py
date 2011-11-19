#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from VideoItem import *
from MediaItem import *

class MovieItem(VideoItem):
    """docstring for MovieItem"""
    def __init__(self, opts, movie_media_container):
        super(MovieItem, self).__init__(opts, movie_media_container)
        media_element = self.video.find("Media")
        self.media_item = MediaItem(self.opts, self, media_element)
        
        self.key = self.video.attrib['key']
        self.studio = self.video.get('studio', "")
        self.type = self.video.get('type', "")
        self.title = self.video.get('title', "")
        self.content_rating = self.video.get('contentRating', "") #PG-13, etc.
        self.summary = self.video.get('summary', "")
        self.rating = self.video.get('rating', "")
        self.year = self.video.get('year', "")
        self.tagline = self.video.get('tagline', "")
        self.thumb = self.video.get('thumb', "")
        self.originally_available_at = self.video.get('originallyAvailableAt', "")
        
        self.genre_names = self.array_of_attributes_with_key_from_child_elements_with_name(self.video, "Genre", "tag")
        if len(self.genre_names) > 0: 
            self.genre = self.genre_names[0] 
        else: 
            self.genre = ''
        self.genres = ', '.join(self.genre_names)
        
        self.writer_names = self.array_of_attributes_with_key_from_child_elements_with_name(self.video, "Writer", "tag")
        self.writers = ', '.join(self.writer_names)
        
        self.director_names = self.array_of_attributes_with_key_from_child_elements_with_name(self.video, "Director", "tag")
        self.directors = ', '.join(self.director_names)
        
        self.cast_names = self.array_of_attributes_with_key_from_child_elements_with_name(self.video, "Role", "tag")
        self.cast = ', '.join(self.cast_names)
    #end def __init__
    
    def name(self):
        return "%s (%s)" % (self.title, self.year)
    #end def name
    
    def export_image_to_temporary_location(self):
        self.export_image(None)
    #end image_path
    
    def export_image(self, desired_local_path):
        request_handler = PmsRequestHandler()
        partial_image_url = self.thumb
        logging.info("Downloading artwork...")
        if self.opts.dryrun:
            self.local_image_path = "/tmp/%s" % self.name()
        else:
            self.local_image_path = request_handler.download_image(partial_image_url, self.name(), None)
        #end if not dryrun
    #end export_image
    
    def tag_string(self):        
        if self.local_image_path == "":
            self.export_image_to_temporary_location()

        tag_string = ""

        tag_string += super(MovieItem, self).tag_string()
        tag_string += self.new_tag_string_entry("Artwork", self.local_image_path)
        tag_string += self.new_tag_string_entry("Media Kind", "Movie")
        tag_string += self.new_tag_string_entry("Name", self.title)
        tag_string += self.new_tag_string_entry("Artist", self.directors)
        tag_string += self.new_tag_string_entry("Genre", self.genre) #single genre
        tag_string += self.new_tag_string_entry("Release Date", self.originally_available_at)
        tag_string += self.new_tag_string_entry("Description", self.tagline if len(self.tagline) > 0 else self.summary)
        tag_string += self.new_tag_string_entry("Long Description", self.summary)
        tag_string += self.new_tag_string_entry("Rating", self.content_rating)
        tag_string += self.new_tag_string_entry("Cast", self.cast)
        tag_string += self.new_tag_string_entry("Director", self.directors)
        tag_string += self.new_tag_string_entry("Screenwriters", self.writers)
        tag_string += self.new_tag_string_entry("Studio", self.studio)
        
        return tag_string.strip()
    #end def tag_string
#end class MovieItem