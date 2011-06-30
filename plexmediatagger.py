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
import signal
import logging

from lxml import etree
from optparse import OptionParser
from ColorizingStreamHandler import *
from PmsRequestHandler import *
from SectionProcessor import *


def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ColorizingStreamHandler())
    
    parser = OptionParser(usage="%prog [options] <full path directory>\n%prog -h for full list of options")
    
    parser.add_option(  "-b", "--batch", action="store_false", dest="interactive",
                        help="selects first search result, requires no human intervention once launched")
    parser.add_option(  "-i", "--interactive", action="store_true", dest="interactive",
                        help="interactivly select correct show from search results [default]")
    parser.add_option(  "-o", "--optimize", action="store_true", dest="optimize",
                        help="Interleaves the audio and video samples, and puts the \"MooV\" atom at the begining of the file. [default]")
    parser.add_option(  "-d", "--debug", action="store_true", dest="debug", 
                        help="shows all debugging info")
    parser.add_option(  "-v", "--verbose", dest="verbose", action="callback", 
                        callback=setLogLevel, help='Increase verbosity')
    parser.add_option(  "-q", "--quiet", action="store_false", dest="verbose",
                        help="For ninja-like processing")
    parser.add_option(  "-f", "--force-tagging", action="store_true", dest="forcetagging",
                        help="Tags all valid files, even previously tagged ones")
    parser.set_defaults( interactive=True, optimize=True, debug=False, verbose=True, forcetagging=False,
                            removetags=False, rename=True, tagging=True )
    
    opts, args = parser.parse_args()
    
    ip = ""
    port = "32400"
    if len(args) == 0:
        parser.error("No pms ip supplied")
    elif len(args) > 1:
        parser.error("Provide single ip")
    else:
        ip = args[0]
    #end if args
    
    
    logging.error( "============ Plex Media Tagger Started ============" )
    
    requestHandler = PmsRequestHandler(ip, port)
    sectionProcessor = SectionProcessor(opts, requestHandler)
    
    sectionsContainer = requestHandler.getSectionsContainer()
    mediaContainer = sectionsContainer.getroot()
    title = mediaContainer.attrib['title1']
    sections = mediaContainer.getchildren()
    
    sectionChoice = len(sections) #default is count of sections, ie ALL
    if opts.interactive:
        logging.info( "List of sections for %s" % title )
        for index, section in enumerate(sections):
            logging.info( "%d. %s" %(index, section.attrib['title']) )
        #end for
        if len(sections) == 0:
            logging.error( "No sections found" )
        else:    
            logging.warning( "empty input equals all" )
    
            #ask user what sections should be processed
            sectionChoice = raw_input("Section to process $")
            if sectionChoice != '':
                try:
                    sectionChoice = int(sectionChoice)
                except ValueError, e:
                    logging.debug(e)
                    logging.critical( "'%s' is not a valid section number" % input )
                    sys.exit(1)
                #end try
            #end if sectionChoice
        #end if len(sections)
    #end if opts.interactive
    
    if sectionChoice == '': #all
        sectionsToProcess = sections
    else:
        sectionsToProcess = [sections[sectionChoice]]
    #end if
    
    logging.warning( "Processing sections..." )
    for index, sectionToProcess in enumerate(sectionsToProcess):
        sectionTitle = sectionToProcess.attrib['title']
        logging.warning( "Loading section %d/%d : '%s'..." % (index+1, len(sectionsToProcess), sectionTitle) )
        sectionProcessor.processSection(sectionToProcess)
        logging.warning( "Section '%s' processed" % sectionTitle )
    #end for
    logging.warning( "Processing sections completed" )
    logging.error( "============ Plex Media Tagger Completed ============" )
#end main


def setLogLevel(*args, **kwargs):
    logging.root.setLevel(logging.root.level - 10)


def signal_handler(signal, frame):
    logging.critical( "\r============ Terminating Plex Media Tagger ============" )
    sys.exit(0)
#end signal_handler

if __name__ == '__main__':
        sys.exit(main())
#end if __name__