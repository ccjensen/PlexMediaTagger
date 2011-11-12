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
from MovieItem import *
from ShowItem import *
from SeasonItem import *
from EpisodeItem import *
from VideoItemProcessor import *

class SectionProcessor:
    """docstring for SectionProcessor"""
    def __init__(self, opts, request_handler):
        self.opts = opts
        self.request_handler = request_handler
    #end def __init__
    
    def process_section(self, section):
        section_type = section.attrib['type']
        if section_type == "movie":
            self.process_movie_section(section)
        elif section_type == "show":
            self.process_show_section(section)
        else:
            logging.error( "'%s' content type is not supported" % sectionType )
        #end if sectionType
    #end process_section

    def get_selection_for_media_container(self, media_container, context=None):
        viewGroup = media_container.attrib['viewGroup']
        if viewGroup == 'movie':
            container_title = media_container.attrib['title1']
            list_of_items = [MovieItem(self.opts, item) for item in media_container.getchildren()]
        elif viewGroup == 'show':
            container_title = media_container.attrib['title1']
            list_of_items = [ShowItem(self.opts, item) for item in media_container.getchildren()]
        elif viewGroup == 'season':
            container_title = media_container.attrib['title2']
            list_of_items = [SeasonItem(self.opts, item, context) for item in media_container.getchildren()]
        elif viewGroup == 'episode':
            container_title = media_container.attrib['title2']
            list_of_items = [EpisodeItem(self.opts, item, context) for item in media_container.getchildren()]
        #end if viewGroup
        
        list_of_items_mastered = []
        #filter the list
        for item in list_of_items:
            #this try-except block handles the "all episodes" in the season container
            try:
                item.leaf_count
            except AttributeError:
                #just add it
                list_of_items_mastered.append(item)
            else:
                #only interested in 1 leaf counted items
                if int(item.leaf_count) == 1:
                    list_of_items_mastered.append(item)
                #end if
            #end try
        #end for
        list_of_items = list_of_items_mastered
        
        if not self.opts.interactive:
            return list_of_items #all
        #end if not self.opts.interactive

        logging.info( "Type part of the item(s) name or leave empty for full list %s's content" % container_title )
        input = raw_input("Item name $")
        
        if input == '':
            logging.info( "List of items in %s" % container_title )
            filtered_list_of_items = list_of_items
        else:
            input = input.lower()
            logging.info( "List of items in %s matching '%s'" % (container_title, input) )
            filtered_list_of_items = [item for item in list_of_items if input in item.title.lower()]
        #end if input == 'ALL'
        
        for index, item in enumerate(filtered_list_of_items):
            logging.info( "%d. %s" % (index, item.name()) )
        #end for
        if len(filtered_list_of_items) == 0:
            logging.error( "No items found" )
            return []
        else:    
            logging.warning( "empty input equals all" )
            
            #ask user what videos should be processed
            selection = raw_input("Item # to select $")
            if selection != '':
                try:
                    selection = int(selection)
                except ValueError, e:
                    logging.debug(e)
                    logging.critical("'%s' is not a valid item ID" % input)
                    sys.exit(1)
                #end try
            #end if video_choice
        #end if len(list_of_videos)
    
        if selection == '': #all
            list_of_selected_items = filtered_list_of_items
        else:
            list_of_selected_items = [filtered_list_of_items[selection]]
        #end if
        return list_of_selected_items
    #end def get_selection_for_media_container

    def process_movie_section(self, section):
        section_key = section.attrib['key']
        contents_container = self.request_handler.get_section_all_container_for_key(section_key)
    
        movies_media_container = contents_container.getroot()
        selected_movies = self.get_selection_for_media_container(movies_media_container)
        
        contents_type = movies_media_container.get('viewGroup', "")
        for index, partial_movie_metadata in enumerate(selected_movies):
            movie_metadata_container = self.request_handler.get_metadata_container_for_key(partial_movie_metadata.key)
            movie = MovieItem(self.opts, movie_metadata_container)
            logging.warning( "processing %d/%d %ss : %s" % (index+1, len(selected_movies), contents_type, movie.name()) )
            video_item_processor = VideoItemProcessor(self.opts, movie)
            video_item_processor.process()
        #end enumerate(selected_movies)
    #end process_movie_section

    def process_show_section(self, section):
        section_key = section.attrib['key']
        shows_container = self.request_handler.get_section_all_container_for_key(section_key)
    
        shows_media_container = shows_container.getroot()
        selected_shows = self.get_selection_for_media_container(shows_media_container)
        
        contents_type = shows_media_container.get('viewGroup', "")
        for index, show in enumerate(selected_shows):
            logging.warning( "processing %d/%d %ss : %s" % (index+1, len(selected_shows), contents_type, show.name()) )
            self.process_season_section(show)
        #end enumerate(selected_shows)
    #end process_show_section
    
    def process_season_section(self, show):
        #get the seasons for this show
        seasons_container = self.request_handler.get_metadata_container_for_key(show.key)
            
        seasons_media_container = seasons_container.getroot()
        selected_seasons = self.get_selection_for_media_container(seasons_media_container, show)
        
        contents_type = seasons_media_container.get('viewGroup', "")
        for index, season in enumerate(selected_seasons):
            logging.warning( "processing %d/%d %ss : %s" % (index+1, len(selected_seasons), contents_type, season.name()) )
            self.process_episode_section(season)
        #end enumerate(selected_seasons)
    #end process_season_section
    
    def process_episode_section(self, season):
        #get the seasons for this show
        episodes_container = self.request_handler.get_metadata_container_for_key(season.key)
            
        episodes_media_container = episodes_container.getroot()
        selected_episodes = self.get_selection_for_media_container(episodes_media_container, season)
        
        contents_type = episodes_media_container.get('viewGroup', "")
        for index, partial_episode_metadata in enumerate(selected_episodes):
            episode_metadata_container = self.request_handler.get_metadata_container_for_key(partial_episode_metadata.key)
            episode = EpisodeItem(self.opts, episode_metadata_container, season)
            logging.warning( "processing %d/%d %ss : %s" % (index+1, len(selected_episodes), contents_type, episode.name()) )
            video_item_processor = VideoItemProcessor(self.opts, episode)
            video_item_processor.process()
        #end enumerate(selected_episodes)
    #end process_episode_section
#end SectionProcessor