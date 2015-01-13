#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from xml.etree import ElementTree
import threading
import logging
import sys
import time
import copy

from Console import *
from Items.MovieItem import MovieItem
from Items.ShowItem import ShowItem
from Items.SeasonItem import SeasonItem
from Items.EpisodeItem import EpisodeItem
from VideoItemProcessor import *

class SectionProcessor:
    """docstring for SectionProcessor"""
    def __init__(self, opts, request_handler):
        self.opts = opts
        self.request_handler = request_handler
        self.event = threading.Event()
        self.event.set()
        self.abort = False
    #end def __init__
    
    def process_section(self, section_element):
        self.breadcrumb = copy.deepcopy(self.opts.batch_breadcrumb)
        section_element_type = section_element.attrib['type']
        if section_element_type == "movie":
            self.movie_title_breadcrumb = self.breadcrumb.pop() if len(self.breadcrumb) > 0 else ''
            self.process_movie_section_element(section_element)
        elif section_element_type == "show":
            self.show_title_breadcrumb = self.breadcrumb.pop() if len(self.breadcrumb) > 0 else ''
            self.season_title_breadcrumb = self.breadcrumb.pop() if len(self.breadcrumb) > 0 else ''
            self.episode_title_breadcrumb = self.breadcrumb.pop() if len(self.breadcrumb) > 0 else ''
            self.process_show_section_element(section_element)
        else:
            logging.error( "'%s' content type is not supported" % section_element_type )
        #end if sectionType
    #end process_section

    def get_selection_for_media_container_element(self, media_container_element, context=None):
        view_group = media_container_element.attrib['viewGroup']
        breadcrumb = ''
        if view_group == 'movie':
            container_title = media_container_element.attrib['title1']
        elif view_group == 'show':
            container_title = media_container_element.attrib['title1']
        elif view_group == 'season':
            container_title = media_container_element.attrib['title2']
        elif view_group == 'episode':
            container_title = media_container_element.attrib['title2']
        else:
            logging.error( "'%s' view group is not supported" % view_group )
            return
        #end if view_group
        
        if view_group == 'movie':
            breadcrumb = self.movie_title_breadcrumb
            list_of_items = [MovieItem(self.opts, item) for item in media_container_element.getchildren()]
        elif view_group == 'show':
            breadcrumb = self.show_title_breadcrumb
            list_of_items = [ShowItem(self.opts, item) for item in media_container_element.getchildren()]
        elif view_group == 'season':
            breadcrumb = self.season_title_breadcrumb
            list_of_items = [SeasonItem(self.opts, item, context) for item in media_container_element.getchildren()]
        elif view_group == 'episode':
            breadcrumb = self.episode_title_breadcrumb
            list_of_items = [EpisodeItem(self.opts, item, context) for item in media_container_element.getchildren()]
        #end if view_group
        
        list_of_items_without_containers = []
        #filter the list
        for item in list_of_items:
            if not breadcrumb in item.title.lower():
                logging.info( " Disregarding '%s' because it does not match breadcrumb '%s'" % (item.title, breadcrumb) )
                continue
            if item.title != "All episodes":
                list_of_items_without_containers.append(item)
            #end if
        #end for
        list_of_items = list_of_items_without_containers
        
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
            selection = raw_input(indent_text("Item # to select $"))
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
    #end def get_selection_for_media_container_element_element

    def process_movie_section_element(self, section):
        section_key = section.attrib['key']
        movies_container_element_tree = self.request_handler.get_section_all_container_for_key(section_key)
        movies_media_container_element = movies_container_element_tree.getroot()
        selected_movie_items = self.get_selection_for_media_container_element(movies_media_container_element)
        
        contents_type = movies_media_container_element.get('viewGroup', "")
        for index, partial_movie_item in enumerate(selected_movie_items):
            if self.abort:
                raise RuntimeError('aborting')
            partial_movie_media_container = self.request_handler.get_metadata_container_for_key(partial_movie_item.key)
            full_movie_item = MovieItem(self.opts, partial_movie_media_container)
            logging.warning( generate_right_padded_string("processing %d/%d %ss : %s " % (index+1, len(selected_movie_items), contents_type, full_movie_item.name()), "-") )
            threading.Thread(None, self.process_video(full_movie_item)).start()
            self.event.wait()
        #end enumerate(selected_movies)
    #end process_movie_section

    def process_show_section_element(self, section):
        section_key = section.attrib['key']
        shows_container_element_tree = self.request_handler.get_section_all_container_for_key(section_key)
    
        shows_media_container_element = shows_container_element_tree.getroot()
        selected_show_items = self.get_selection_for_media_container_element(shows_media_container_element)
        
        contents_type = shows_media_container_element.get('viewGroup', "")
        for index, show_item in enumerate(selected_show_items):
            logging.warning( "processing %d/%d %ss : %s" % (index+1, len(selected_show_items), contents_type, show_item.name()) )
            self.process_season_section_element(show_item)
        #end enumerate(selected_show_items)
    #end process_show_section
    
    def process_season_section_element(self, show):
        #get the seasons for this show
        seasons_container_element_tree = self.request_handler.get_metadata_container_for_key(show.key)
            
        seasons_media_container_element = seasons_container_element_tree.getroot()
        selected_season_items = self.get_selection_for_media_container_element(seasons_media_container_element, show)
        
        contents_type = seasons_media_container_element.get('viewGroup', "")
        for index, season_item in enumerate(selected_season_items):
            logging.warning( "processing %d/%d %ss : %s" % (index+1, len(selected_season_items), contents_type, season_item.name()) )
            self.process_episode_section_element(season_item)
        #end enumerate(selected_seasons)
    #end process_season_section
    
    def process_episode_section_element(self, season):
        #get the seasons for this show
        episodes_container_element_tree = self.request_handler.get_metadata_container_for_key(season.key)
            
        episodes_media_container_element = episodes_container_element_tree.getroot()
        selected_episode_items = self.get_selection_for_media_container_element(episodes_media_container_element, season)
        
        contents_type = episodes_media_container_element.get('viewGroup', "")
        for index, partial_episode_item in enumerate(selected_episode_items):
            if self.abort:
                raise RuntimeError('aborting')
            partial_episode_media_container = self.request_handler.get_metadata_container_for_key(partial_episode_item.key)
            full_episode_item = EpisodeItem(self.opts, partial_episode_media_container, season)
            logging.warning( generate_right_padded_string("processing %d/%d %ss : %s " % (index+1, len(selected_episode_items), contents_type, full_episode_item.name()), "-") )
            threading.Thread(None, self.process_video(full_episode_item)).start()
            self.event.wait()
        #end enumerate(selected_episodes)
    #end process_episode_section
    
    def process_video(self, video_item):
        self.event.clear()
        video_item_processor = VideoItemProcessor(self.opts, video_item)
        video_item_processor.process()
        self.event.set()
#end SectionProcessor