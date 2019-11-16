#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from VideoItem import *
from MediaItem import *

class EpisodeItem(VideoItem):
    """docstring for EpisodeItem"""
    def __init__(self, opts, episode_media_container, season):
        super(EpisodeItem, self).__init__(opts, episode_media_container)
        media_element = self.video.find("Media")
        self.media_items = [MediaItem(self.opts, self, media_element) for media_element in self.video.findall("Media")]
        
        self.season = season
        self.show = season.show
        
        self.key = self.video.attrib['key']
        self.type = self.video.get('type', "")
        self.title = self.video.get('title', "")
        self.summary = self.video.get('summary', "")
        self.index = self.video.get('index', "")
        self.parent_index = self.video.get('parentIndex', "")
        self.rating = self.video.get('rating', "0")
        self.thumb = self.video.get('thumb', "")
        self.originally_available_at = self.video.get('originallyAvailableAt', "")

        self.writer_names = self.array_of_attributes_with_key_from_child_elements_with_name(self.video, "Writer", "tag")
        self.writers = ', '.join(self.writer_names)

        self.director_names = self.array_of_attributes_with_key_from_child_elements_with_name(self.video, "Director", "tag")
        self.directors = ', '.join(self.director_names)
        
        #other metadata can/will be retreived from the season object which holds a link to the show object
    #end def __init__
    
    def name(self):
        return "%s - S%02dE%02d - %s" % (self.season.show.name(), int(self.season.index), int(self.index), self.title)
    #end def name
    
    def export_image_to_temporary_location(self):
        self.export_image(None)
    #end image_path
    
    def export_image(self, desired_local_path):
        if len(self.thumb) == 0:
            logging.warning("Could not find episode artwork...")
            return
        
        request_handler = PmsRequestHandler()
        partial_image_url = self.thumb
        logging.info("Downloading episode artwork...")
        
        image_filename = request_handler.filesystem_compatible_name(self.name())
        if self.opts.dryrun:
            self.local_image_path = "/tmp/%s.jpg" % image_filename
        else:
            self.local_image_path = request_handler.download_image(partial_image_url, image_filename, None)
        #end if not dryrun
    #end export_image
            
    
    def tag_string(self):
        tag_string = self.season.tag_string()
        tag_string += super(EpisodeItem, self).tag_string()
        
        if not self.opts.tag_prefer_season_artwork or not "{Cover Art:" in tag_string:
            if self.local_image_path == "":
                self.export_image_to_temporary_location()
            if self.local_image_path != "":
                tag_string += self.new_tag_string_entry("Cover Art", self.local_image_path)
        
        tag_string += self.new_tag_string_entry("Name", self.title)
        tag_string += self.new_tag_string_entry("Release Date", self.originally_available_at)
        tag_string += self.new_tag_string_entry("Track #", self.index+"/"+self.index)
        tag_string += self.new_tag_string_entry("TV Episode #", self.index)
        tag_string += self.new_tag_string_entry("TV Episode ID", self.season.index+self.index)
        tag_string += self.new_tag_string_entry("Description", self.summary)        
        tag_string += self.new_tag_string_entry("Long Description", self.summary)
        
        tag_string += self.new_tag_string_entry("Screenwriters", self.writers)
        tag_string += self.new_tag_string_entry("Director", self.directors)
        
        #no cast currently available for show/season/episode
        #tag_string += self.new_tag_string_entry("Cast", self.cast)        
        
        return tag_string.strip()
    #end def tag_string
#end class EpisodeItem