#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)
 
"""
plexmediatagger.py
Automatically tags compatible media items.
Uses data from the PlexMediaServer

thanks goes to:
the Subler team (http://code.google.com/p/subler/) for their excellent CLI tool to used to write the information to the media files
"""

__author__ = "ccjensen/Chris"
__version__ = "0.01"

import sys
import os
import re
import glob
import unicodedata
import logging
import signal

from lxml import etree
from optparse import OptionParser
from PmsRequestHandler import *
    
def processSection(opts, requestHandler, section):
    BASEINDENTATION = "  "
    sectionType = section.attrib['type']
    if sectionType == "movie":
        processMovieSection(opts, requestHandler, section)
    elif sectionType == "show":
        processShowSection(opts, requestHandler, section)
    else:
        print BASEINDENTATION+"'%s' content type is not supported" % sectionType
    #end if sectionType
#end processSection


def processMovieSection(opts, requestHandler, section):
    BASEINDENTATION = "    "
    sectionKey = section.attrib['key']
    contentsContainer = requestHandler.getSectionAllContainerForKey(sectionKey)
    
    mediaContainer = contentsContainer.getroot()
    title = mediaContainer.attrib['title1']
    videos = mediaContainer.getchildren()
    
    videoChoice = len(videos) #default is count of videos, ie ALL
    if opts.interactive:
        print BASEINDENTATION+"List of movies in %s" % title
        for index, video in enumerate(videos):
            print BASEINDENTATION+"%d. %s (%s)" % (index, video.attrib['title'], video.attrib['year'])
        #end for
        if len(videos) > 0:
            print BASEINDENTATION+"%d. %s" % (len(videos), "ALL")
        #end if
        
        #ask user what sections should be processed
        input = raw_input(BASEINDENTATION+"$ Video to tag: ")
        try:
            videoChoice = int(input)
        except ValueError, e:
            logging.debug(e)
            logging.critical("'%s' is not a valid video number" % input)
            sys.exit(1)
        #end try
    #end if
    
    if videoChoice == len(videos): #all
        videosToProcess = videos
    else:
        videosToProcess = [videos[videoChoice]]
    #end if
    
    for videoToProcess in videosToProcess:
        print BASEINDENTATION+"  processing %s (%s)" % (videoToProcess.attrib['title'], videoToProcess.attrib['year'])
        #TODO: here the file will actually be tagged
        
#end processMovieSection

def processShowSection(opts, requestHandler, section):
    #TODO: implement
    return    
#end processShowSection


def main():
    BASEINDENTATION = "  "
    signal.signal(signal.SIGINT, signal_handler)
    logging.basicConfig()
    parser = OptionParser(usage="%prog [options] <full path directory>\n%prog -h for full list of options")
    
    parser.add_option(  "-b", "--batch", action="store_false", dest="interactive",
                        help="selects first search result, requires no human intervention once launched")
    parser.add_option(  "-i", "--interactive", action="store_true", dest="interactive",
                        help="interactivly select correct show from search results [default]")
    parser.add_option(  "-d", "--debug", action="store_true", dest="debug", 
                        help="shows all debugging info")
    parser.add_option(  "-v", "--verbose", dest="verbose", action="callback", 
                        callback=setLogLevel, help='Increase verbosity')
    parser.add_option(  "-q", "--quiet", action="store_false", dest="verbose",
                        help="For ninja-like processing")
    parser.add_option(  "-f", "--force-tagging", action="store_true", dest="forcetagging",
                        help="Tags all valid files, even previously tagged ones")
    parser.set_defaults( interactive=True, debug=False, verbose=True, forcetagging=False,
                            removetags=False, rename=True, tagging=True )
    
    opts, args = parser.parse_args()
    
    # logging.debug('This is a debug message')
    # logging.info('This is an info message')
    # logging.warning('This is a warning message')
    # logging.error('This is an error message')
    # logging.critical('This is a critical error message')
    
    ip = ""
    port = "32400"
    if len(args) == 0:
        parser.error("No pms ip supplied")
    elif len(args) > 1:
        parser.error("Provide single ip")
    else:
        ip = args[0]
    #end if args
    
    
    logging.info("============ Plex Media Tagger Started ============")
    
    requestHandler = PmsRequestHandler(ip, "32400")
    sectionsContainer = requestHandler.getSectionsContainer()
    
    mediaContainer = sectionsContainer.getroot()
    title = mediaContainer.attrib['title1']
    sections = mediaContainer.getchildren()
    
    sectionChoice = len(sections) #default is count of sections, ie ALL
    if opts.interactive:
        print "List of sections for %s" % title
        for index, section in enumerate(sections):
            print "%d. %s" %(index, section.attrib['title'])
        #end for
        if len(sections) > 0:
            print "%d. %s" %(len(sections), "ALL")
        #end if
        
        #ask user what sections should be processed
        input = raw_input("$ Section to process: ")
        try:
            sectionChoice = int(input)
        except ValueError, e:
            logging.debug(e)
            logging.critical("'%s' is not a valid section number" % input)
            sys.exit(1)
        #end try
    #end if
    
    if sectionChoice == len(sections): #all
        sectionsToProcess = sections
    else:
        sectionsToProcess = [sections[sectionChoice]]
    #end if
    
    print "\nProcessing sections..."
    for index, sectionToProcess in enumerate(sectionsToProcess):
        sectionTitle = sectionToProcess.attrib['title']
        print "  Processing section %d/%d : '%s'" % (index+1, len(sectionsToProcess), sectionTitle)
        processSection(opts, requestHandler, sectionToProcess)
    #end for
    
    logging.info("============ Plex Media Tagger Completed ============")
#end main


def setLogLevel(*args, **kwargs):
    logging.root.setLevel(logging.root.level - 10)


def signal_handler(signal, frame):
    print '\nTerminating Plex Media Tagger'
    sys.exit(0)
#end signal_handler

if __name__ == '__main__':
        sys.exit(main())
#end if __name__