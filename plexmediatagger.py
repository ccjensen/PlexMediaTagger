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
    root.setLevel(logging.WARNING)
    root.addHandler(ColorizingStreamHandler())
    
    parser = OptionParser(usage="\
%prog [options] [alternate IP/Domain (default is localhost)] [port number (default is 32400)]\n\
Example: %prog -of 192.168.0.2 55400\n\
%prog -h for full list of options\n\n\
Filepaths to media items in PMS need to be the same as on machine that is running this script.\
")
    
    parser.add_option(  "-b", "--batch", action="store_false", dest="interactive",
                        help="Disables interactive. Requires no human intervention once launched, and will perform operations on all files")
    parser.add_option(  "-i", "--interactive", action="store_true", dest="interactive",
                        help="interactivly select files to operate on [default]")
    parser.add_option(  "-o", "--optimize", action="store_true", dest="optimize",
                        help="Interleaves the audio and video samples, and puts the \"MooV\" atom at the beginning of the file.")
    parser.add_option(  "-v", "--verbose", dest="verbose", action="callback", 
                        callback=setLogLevel, help='Increase verbosity')
    parser.add_option(  "-q", "--quiet", action="store_false", dest="quiet",
                        help="For ninja-like processing (Can only be used when in batch mode)")
    parser.add_option(  "-f", "--force-tagging", action="store_true", dest="forcetagging",
                        help="Tags all chosen files, even previously tagged ones")
    parser.set_defaults( interactive=True, optimize=False, forcetagging=False,
                            removetags=False, quiet=False )
    
    opts, args = parser.parse_args()
    
    ip = "localhost"
    port = "32400"
    if len(args) == 1:
        ip = args[0]
    if len(args) == 2:
        ip = args[0]
        port = args[1]
    elif len(args) > 2:
        parser.error("Provide only one IP/Domain and port number")
    #end if args
    
    if opts.interactive and not root.isEnabledFor(logging.INFO):
        root.setLevel(logging.INFO)
    
    logging.error( "============ Plex Media Tagger Started ============" )
    
    request_handler = PmsRequestHandler()
    request_handler.ip = ip
    request_handler.port = port
    
    section_processor = SectionProcessor(opts, request_handler)
    
    logging.error( "Connecting to PMS at %s:%s" % (ip, port) )
    sections_container = request_handler.getSectionsContainer()
    media_container = sections_container.getroot()
    title = media_container.attrib['title1']
    sections = media_container.getchildren()
    
    section_choice = '' #default is empty == all
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
            section_choice = raw_input("Section to process $")
            if section_choice != '':
                try:
                    section_choice = int(section_choice)
                except ValueError, e:
                    logging.debug(e)
                    logging.critical( "'%s' is not a valid section number" % input )
                    sys.exit(1)
                #end try
            #end if section_choice
        #end if len(sections)
    #end if opts.interactive
    
    if section_choice == '': #all
        sections_to_process = sections
    else:
        sections_to_process = [sections[section_choice]]
    #end if
    
    logging.warning( "Processing sections..." )
    for index, section_to_process in enumerate(sections_to_process):
        section_title = section_to_process.attrib['title']
        logging.warning( "Loading section %d/%d : '%s'..." % (index+1, len(sections_to_process), section_title) )
        section_processor.process_section(section_to_process)
        logging.warning( "Section '%s' processed" % section_title )
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