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

class ShowMetadataParser(BaseMetadataParser):
    """docstring for ShowMetadataParser"""
    def __init__(self, opts, show_container):
        super(ShowMetadataParser, self).__init__(opts)
        
        self.key = show_container.attrib['key']
        self.studio = show_container.get('studio', "")
        self.type = show_container.get('type', "")
        self.title = show_container.get('title', "")
        self.content_rating = show_container.get('contentRating', "") #PG-13, etc.
        self.summary = show_container.get('summary', "")
        self.index = show_container.get('index', "")
        self.rating = show_container.get('rating', "") #not used
        self.year = show_container.get('year', "")
        self.thumb = show_container.get('thumb', "")
        self.art = show_container.get('art', "")
        self.banner = show_container.get('banner', "")
        self.theme = show_container.get('theme', "")
        self.originally_available_at = show_container.get('originallyAvailableAt', "")
        
        self.genre_names = self.array_of_attributes_with_key_from_child_nodes_with_name(show_container, "Genre", "tag")
        if len(self.genre_names) > 0: 
            self.genre = self.genre_names[0] 
        else: 
            self.genre = ''
        self.genres = ', '.join(self.genre_names)
    #end def __init__
    
    def name(self):
        return "%s (%s)" % (self.title, self.year)
    #end def name
#end class ShowMetadataParser