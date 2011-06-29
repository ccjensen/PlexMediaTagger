#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from lxml import etree
import logging

class SectionProcessor:
    """docstring for PmsRequestHandler"""
    def __init__(self, opts, requestHandler):
        self.opts = opts
        self.requestHandler = requestHandler
    #end def __init__
    
    def processSection(self, section):
        BASEINDENTATION = "  "
        sectionType = section.attrib['type']
        if sectionType == "movie":
            self.processMovieSection(section)
        elif sectionType == "show":
            self.processShowSection(section)
        else:
            logging.error( BASEINDENTATION+"'%s' content type is not supported" % sectionType )
        #end if sectionType
    #end processSection


    def processMovieSection(self, section):
        BASEINDENTATION = "    "
        sectionKey = section.attrib['key']
        contentsContainer = self.requestHandler.getSectionAllContainerForKey(sectionKey)
    
        mediaContainer = contentsContainer.getroot()
        title = mediaContainer.attrib['title1']
        videos = mediaContainer.getchildren()
        
        videoChoice = ''
        listOfVideos = videos #all
        
        if self.opts.interactive:
            logging.info( BASEINDENTATION+"Type part of the movie name or leave empty for full list %s" % title )
            input = raw_input(BASEINDENTATION+"Movie name $")
            
            if input == '':
                logging.info( BASEINDENTATION+"List of items in %s" % title )
                listOfVideos = videos
            else:
                input = input.lower()
                logging.info( BASEINDENTATION+"List of items in %s matching '%s'" % (title, input) )
                listOfVideos = [video for video in videos if input in video.attrib['title'].lower()]
            #end if input == 'ALL'
            
            for index, video in enumerate(listOfVideos):
                logging.info( BASEINDENTATION+"%d. %s (%s)" % (index, video.attrib['title'], video.attrib['year']) )
            #end for
            if len(listOfVideos) == 0:
                logging.error( BASEINDENTATION+"No found items" )
            else:    
                logging.warning( BASEINDENTATION+"empty equals all" )
                
                #ask user what videos should be processed
                videoChoice = raw_input(BASEINDENTATION+"Video ID to tag $")
                if videoChoice != '':
                    try:
                        videoChoice = int(input)
                    except ValueError, e:
                        logging.debug(e)
                        logging.critical("'%s' is not a valid video ID" % input)
                        sys.exit(1)
                    #end try
                #end if input
            #end if len(listOfVideos)
        #end if
    
        if videoChoice == '': #all
            videosToProcess = listOfVideos
        else:
            videosToProcess = [listOfVideos[videoChoice]]
        #end if
        
        for index, videoToProcess in enumerate(videosToProcess):
            logging.info( BASEINDENTATION+"  processing %d/%d : %s (%s)..." % (index+1, len(videosToProcess), videoToProcess.attrib['title'], videoToProcess.attrib['year']) )
            #TODO: here the file will actually be tagged
        
    #end processMovieSection

    def processShowSection(self, section):
        #TODO: implement
        return    
    #end processShowSection