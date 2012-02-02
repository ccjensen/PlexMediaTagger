#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from BaseItem import *

class SeasonItem(BaseItem):
    """docstring for SeasonItem"""
    def __init__(self, opts, season_media_container, show):
        super(SeasonItem, self).__init__(opts)
        self.show = show
        
        self.key = season_media_container.attrib['key']
        self.type = season_media_container.get('type', "")
        self.title = season_media_container.get('title', "")
        self.index = season_media_container.get('index', "0")
        self.thumb = season_media_container.get('thumb', "")
        self.local_image_path = ""
    #end def __init__
    
    def name(self):
        return "%s - %s" % (self.show.name(), self.title)
    #end def name
    
    def export_image_to_temporary_location(self):
        self.export_image(None)
    #end image_path
    
    def export_image(self, desired_local_path):
        request_handler = PmsRequestHandler()
        partial_image_url = self.thumb
        logging.info("Downloading season artwork...")
        
        image_filename = request_handler.filesystem_compatible_name(self.name())
        if self.opts.dryrun:
            self.local_image_path = "/tmp/%s.jpg" % image_filename
        else:
            self.local_image_path = request_handler.download_image(partial_image_url, image_filename, None)
        #end if not dryrun
    #end export_image
    
    def tag_string(self):
        tag_string = self.show.tag_string()
        
        if self.opts.tag_prefer_season_artwork:
            if self.local_image_path == "":
                self.export_image_to_temporary_location()
            tag_string += self.new_tag_string_entry("Artwork", self.local_image_path)
        
        #Example: "The X-Files, Season 1"
        tag_string += self.new_tag_string_entry("Album", self.show.title+", "+self.title)
        tag_string += self.new_tag_string_entry("Disk #", self.index)
        tag_string += self.new_tag_string_entry("TV Season", self.index)
        
        return tag_string.strip()
    #end def tag_string
#end class SeasonItem