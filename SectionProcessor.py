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
from MetadataParsers import *

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
            self.processShowSection(section)
        else:
            logging.error( "'%s' content type is not supported" % sectionType )
        #end if sectionType
    #end process_section


    def process_movie_section(self, section):
        section_key = section.attrib['key']
        contents_container = self.request_handler.get_section_all_container_for_key(section_key)
    
        media_container = contents_container.getroot()
        title = media_container.attrib['title1']
        videos = media_container.getchildren()
        
        video_choice = ''
        list_of_videos = videos #all
        
        if self.opts.interactive:
            logging.info( "Type part of the movie name or leave empty for full list %s" % title )
            input = raw_input("Movie name $")
            
            if input == '':
                logging.info( "List of items in %s" % title )
                list_of_videos = videos
            else:
                input = input.lower()
                logging.info( "List of items in %s matching '%s'" % (title, input) )
                list_of_videos = [video for video in videos if input in video.attrib['title'].lower()]
            #end if input == 'ALL'
            
            for index, video in enumerate(list_of_videos):
                logging.info( "%d. %s (%s)" % (index, video.attrib['title'], video.attrib['year']) )
            #end for
            if len(list_of_videos) == 0:
                logging.error( "No items found" )
            else:    
                logging.warning( "empty input equals all" )
                
                #ask user what videos should be processed
                video_choice = raw_input("Video # to tag $")
                if video_choice != '':
                    try:
                        video_choice = int(video_choice)
                    except ValueError, e:
                        logging.debug(e)
                        logging.critical("'%s' is not a valid video ID" % input)
                        sys.exit(1)
                    #end try
                #end if video_choice
            #end if len(list_of_videos)
        #end if
    
        if video_choice == '': #all
            videos_to_process = list_of_videos
        else:
            videos_to_process = [list_of_videos[video_choice]]
        #end if
        
        for index, video_to_process in enumerate(videos_to_process):
            url = video_to_process.attrib['key']
            video_metadata_container = self.request_handler.get_metadata_container_for_key(url)
            movie = MovieMetadataParser(self.opts, video_metadata_container)
            logging.info( "processing %d/%d : %s (%s)..." % (index+1, len(videos_to_process), movie.title, movie.year) )
            self.tag_file(movie)
        #end for videos_to_process
            
        
    #end process_movie_section

    def process_show_section(self, section):
        #TODO: implement
        return    
    #end processShowSection
    
    def tag_file(self, media_item):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        #TODO: implement
        if '.m4v' in media_item.file_types or '.mp4' in media_item.file_types:            
            #get any artwork
            
            logging.error("tagging %s" % media_item.name())
            
            #Create the command line string
            tag_cmd = ['%s' % SublerCLI]
            tag_cmd.append("-t")
            tag_cmd.append(media_item.tag_string())
            
            for paths in media_item.media_paths():
                new_tag_cmd = tag_cmd
                new_tag_cmd.append("-i")
                new_tag_cmd.append(paths)
                
                logging.debug("tag command arguements: %s" % new_tag_cmd)
                #run SublerCLI using the arguments we have created
                result = subprocess.Popen(new_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                if "Error" in result:
                    logging.critical(result.strip())
                else:
                    logging.error("Tagged: %s" % media_item.name())
                #end if "Error"
            #end for paths
        return    
    #end processShowSection