#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from BaseItem import *

class ShowItem(BaseItem):
    """docstring for ShowItem"""
    def __init__(self, opts, show_media_container):
        super(ShowItem, self).__init__(opts)
        
        self.key = show_media_container.attrib['key']
        self.studio = show_media_container.get('studio', "")
        self.type = show_media_container.get('type', "")
        self.title = show_media_container.get('title', "")
        self.content_rating = show_media_container.get('contentRating', "") #PG-13, etc.
        self.summary = show_media_container.get('summary', "")
        self.index = show_media_container.get('index', "")
        self.rating = show_media_container.get('rating', "")
        self.year = show_media_container.get('year', "")
        self.thumb = show_media_container.get('thumb', "")
        self.art = show_media_container.get('art', "")
        self.banner = show_media_container.get('banner', "")
        self.theme = show_media_container.get('theme', "")
        self.originally_available_at = show_media_container.get('originallyAvailableAt', "")
        
        self.genre_names = self.array_of_attributes_with_key_from_child_elements_with_name(show_media_container, "Genre", "tag")
        if len(self.genre_names) > 0: 
            self.genre = self.genre_names[0] 
        else: 
            self.genre = ''
        self.genres = ', '.join(self.genre_names)
        self.local_image_path = ""
    #end def __init__
    
    def name(self):
        return "%s (%s)" % (self.title, self.year)
    #end def name

    def export_image_to_temporary_location(self):
        self.export_image(None)
    #end image_path
    
    def export_image(self, desired_local_path):
        if len(self.thumb) == 0:
            logging.warning("Could not find show artwork...")
            return
        
        request_handler = PmsRequestHandler()
        partial_image_url = self.thumb
        logging.info("Downloading show artwork...")
        
        image_filename = request_handler.filesystem_compatible_name(self.name())
        if self.opts.dryrun:
            self.local_image_path = "/tmp/%s.jpg" % image_filename
        else:
            self.local_image_path = request_handler.download_image(partial_image_url, image_filename, None)
        #end if not dryrun
    #end export_image

    
    def tag_string(self):
        tag_string = ""
        tag_string += self.new_tag_string_entry("Media Kind", "10") #10 == TV Show
        tag_string += self.new_tag_string_entry("Artist", self.title)
        tag_string += self.new_tag_string_entry("Album Artist", self.title)
        
        #Example: "The X-Files, Season 1"
        tag_string += self.new_tag_string_entry("Genre", self.genre) #single genre
        tag_string += self.new_tag_string_entry("TV Show", self.title)
        tag_string += self.new_tag_string_entry("TV Network", self.studio)
        tag_string += self.new_tag_string_entry("Rating", self.content_rating)
        
        return tag_string.strip()
    #end def tag_string
#end class ShowItem