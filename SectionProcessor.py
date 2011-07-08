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
import subprocess
from MovieMetadataParser import *
from ShowMetadataParser import *
from SeasonMetadataParser import *
from EpisodeMetadataParser import *

class SectionProcessor:
    """docstring for PmsRequestHandler"""
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
            list_of_items = [MovieMetadataParser(self.opts, item) for item in media_container.getchildren()]
        elif viewGroup == 'show':
            container_title = media_container.attrib['title1']
            list_of_items = [ShowMetadataParser(self.opts, item) for item in media_container.getchildren()]
        elif viewGroup == 'season':
            container_title = media_container.attrib['title2']
            list_of_items = [SeasonMetadataParser(self.opts, item, context) for item in media_container.getchildren()]
        elif viewGroup == 'episode':
            container_title = media_container.attrib['title2']
            list_of_items = [EpisodeMetadataParser(self.opts, item, context) for item in media_container.getchildren()]
        #end if viewGroup
        
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
            movie = MovieMetadataParser(self.opts, movie_metadata_container)
            logging.error( "processing %d/%d %ss : %s..." % (index+1, len(selected_movies), contents_type, movie.name()) )
            self.tag_file(movie)
        #end for videos_to_process
    #end process_movie_section

    def process_show_section(self, section):
        section_key = section.attrib['key']
        shows_container = self.request_handler.get_section_all_container_for_key(section_key)
    
        shows_media_container = shows_container.getroot()
        selected_shows = self.get_selection_for_media_container(shows_media_container)
        
        contents_type = shows_media_container.get('viewGroup', "")
        for index, show in enumerate(selected_shows):
            logging.error( "processing %d/%d %ss : %s..." % (index+1, len(selected_shows), contents_type, show.name()) )
            self.process_season_section(show)
        #end for show_to_process
    #end process_show_section
    
    def process_season_section(self, show):
        #get the seasons for this show
        seasons_container = self.request_handler.get_metadata_container_for_key(show.key)
            
        seasons_media_container = seasons_container.getroot()
        selected_seasons = self.get_selection_for_media_container(seasons_media_container, show)
        
        contents_type = seasons_media_container.get('viewGroup', "")
        for index, season in enumerate(selected_seasons):
            logging.error( "processing %d/%d %ss : %s..." % (index+1, len(selected_seasons), contents_type, season.name()) )
            self.process_episode_section(season)
        #end for season_to_process
    #end process_season_section
    
    def process_episode_section(self, season):
        #get the seasons for this show
        episodes_container = self.request_handler.get_metadata_container_for_key(season.key)
            
        episodes_media_container = episodes_container.getroot()
        selected_episodes = self.get_selection_for_media_container(episodes_media_container, season)
        
        contents_type = episodes_media_container.get('viewGroup', "")
        for index, partial_episode_metadata in enumerate(selected_episodes):
            episode_metadata_container = self.request_handler.get_metadata_container_for_key(partial_episode_metadata.key)
            episode = EpisodeMetadataParser(self.opts, episode_metadata_container, season)
            logging.error( "processing %d/%d %ss : %s..." % (index+1, len(selected_episodes), contents_type, episode.name()) )
            self.tag_file(episode)
        #end for season_to_process
    #end process_season_section
    
    def tag_file(self, media_item):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        filepaths_to_tag = []
        
        for path in media_item.media_paths():
            file_type = os.path.splitext(path)[1]
            if file_type == '.m4v' or file_type == '.mp4':
                #check if we want to (re)tag the file no matter what, and if the file is untagged
                if self.opts.forcetagging or self.isFileUntagged(path, media_item.comments):
                    filepaths_to_tag.append(path)
                #end if not self.alreadyTagged
            else:
                logging.info("PlexMediaTagger cannot process '%s' files" % file_type)
            #end if file_type
        #end for
        
        any_files_to_tag = len(filepaths_to_tag) == 0
        if any_files_to_tag:
            logging.error("skipping: no files to tag")
            return
        #end if len
        
        logging.error("tagging...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]
        tag_cmd.append("-t")
        tag_cmd.append(media_item.tag_string()) #also downloads the artwork
    
        if self.opts.optimize:
            tag_cmd.append("-O")
        #end if self.opts.optimize
    
        for path in filepaths_to_tag:
            new_tag_cmd = tag_cmd
            new_tag_cmd.append("-i")
            new_tag_cmd.append(path)
        
            logging.debug("tag command arguements: %s" % new_tag_cmd)
            #run SublerCLI using the arguments we have created
            result = subprocess.Popen(new_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            if "Error" in result:
                logging.critical("Failed: %s" % result.strip())
            else:
                logging.error("Tagged '%s'" % path)
            #end if "Error"
        #end for paths
    #end tag_file
    
    def isFileUntagged(self, filepath, tagging_marker):
        """docstring for isFileUntagged"""
        AtomicParsley = os.path.join(sys.path[0], "AtomicParsley32")
        
        #Create the command line string
        get_tags_cmd = ['%s' % AtomicParsley]
        get_tags_cmd.append('%s' % filepath)
        get_tags_cmd.append('-t')
        
        #check if file has already been tagged
        result = subprocess.Popen(get_tags_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        
        #error checking
        if 'AtomicParsley error' in result:
            logging.critical("Failed to determine file tagged status")
            return False
        #end if 'AtomicParsley error' in result:
        
        if tagging_marker in result:
            logging.info("File previously tagged")
            return False
        else:
            logging.info("File untagged")
            return True
        #end if tagString in result
    #end isFileUntagged
#end SectionProcessor