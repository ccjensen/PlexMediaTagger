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
    def __init__(self, opts, requestHandler):
        self.opts = opts
        self.requestHandler = requestHandler
    #end def __init__
    
    def processSection(self, section):
        sectionType = section.attrib['type']
        if sectionType == "movie":
            self.processMovieSection(section)
        elif sectionType == "show":
            self.processShowSection(section)
        else:
            logging.error( "'%s' content type is not supported" % sectionType )
        #end if sectionType
    #end processSection


    def processMovieSection(self, section):
        sectionKey = section.attrib['key']
        contentsContainer = self.requestHandler.getSectionAllContainerForKey(sectionKey)
    
        mediaContainer = contentsContainer.getroot()
        title = mediaContainer.attrib['title1']
        videos = mediaContainer.getchildren()
        
        videoChoice = ''
        listOfVideos = videos #all
        
        if self.opts.interactive:
            logging.info( "Type part of the movie name or leave empty for full list %s" % title )
            input = raw_input("Movie name $")
            
            if input == '':
                logging.info( "List of items in %s" % title )
                listOfVideos = videos
            else:
                input = input.lower()
                logging.info( "List of items in %s matching '%s'" % (title, input) )
                listOfVideos = [video for video in videos if input in video.attrib['title'].lower()]
            #end if input == 'ALL'
            
            for index, video in enumerate(listOfVideos):
                logging.info( "%d. %s (%s)" % (index, video.attrib['title'], video.attrib['year']) )
            #end for
            if len(listOfVideos) == 0:
                logging.error( "No items found" )
            else:    
                logging.warning( "empty input equals all" )
                
                #ask user what videos should be processed
                videoChoice = raw_input("Video # to tag $")
                if videoChoice != '':
                    try:
                        videoChoice = int(videoChoice)
                    except ValueError, e:
                        logging.debug(e)
                        logging.critical("'%s' is not a valid video ID" % input)
                        sys.exit(1)
                    #end try
                #end if videoChoice
            #end if len(listOfVideos)
        #end if
    
        if videoChoice == '': #all
            videosToProcess = listOfVideos
        else:
            videosToProcess = [listOfVideos[videoChoice]]
        #end if
        
        for index, videoToProcess in enumerate(videosToProcess):
            url = videoToProcess.attrib['key']
            videoMetadataContainer = self.requestHandler.getMetadataContainerForKey(url)
            movie = MovieMetadataParser(self.opts, videoMetadataContainer)
            logging.info( "processing %d/%d : %s (%s)..." % (index+1, len(videosToProcess), movie.title, movie.year) )
            self.tagFile(movie)
        #end for videosToProcess
            
        
    #end processMovieSection

    def processShowSection(self, section):
        #TODO: implement
        return    
    #end processShowSection
    
    def tagFile(self, mediaItem):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        #TODO: implement
        if '.m4v' in mediaItem.fileTypes or '.mp4' in mediaItem.fileTypes:
            logging.error("tagging %s" % mediaItem.name())
            
            #Create the command line string
            tagCmd = ['%s' % SublerCLI]
            tagCmd.append("-t")
            tagCmd.append(mediaItem.tagString())
            
            for paths in mediaItem.mediaPaths():
                newTagCmd = tagCmd
                newTagCmd.append("-i")
                newTagCmd.append(paths)
                
                logging.debug("Tag command: %s" % newTagCmd)
                #run SublerCLI using the arguments we have created
                result = subprocess.Popen(newTagCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
                if "Error" in result:
                    logging.critical(result.strip())
                else:
                    logging.error("Tagged: %s" % mediaItem.name())
                #end if "Error"
            #end for paths
        return    
    #end processShowSection