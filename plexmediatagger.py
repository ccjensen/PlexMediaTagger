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
Uses data from the PlexMediaServer (http://www.plexapp.com/)

thanks goes to:
the Subler team (https://bitbucket.org/galad87/subler https://bitbucket.org/galad87/sublercli) for 
their excellent CLI tool to used to write the information to the media files
"""

__author__ = "ccjensen/Chris"
__version__ = "0.7"

import sys
import os
import re
import unicodedata
import signal
import logging
import threading
import getpass

from xml.etree import ElementTree
from optparse import OptionParser, OptionValueError
from ColorizingStreamHandler import *
from PmsRequestHandler import *
from SectionProcessor import *
from Summary import *
from LibraryStatistics import *
from Console import *

#global
section_processor = None

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    root.addHandler(ColorizingStreamHandler())
    
    parser = OptionParser(usage="\
%prog [options]\n\
Example 1: %prog --tag\n\
Example 2: %prog --tag -b --username='foo@bar.com' --interactive-password\n\
\ttag everything in the library, and authenticate to Plex Home as user foo@bar.com with password being prompted for (password can also be supplied using the --password option)\n\
Example 3: %prog -bq --tag --remove-all-tags --optimize --export-subtitles --embed-subtitles -ip 192.168.0.2 --port 55400\n\
Example 4: %prog --subtitles -m 'D:\Movies' '/Volumes/Media/Movies' -m '\\' '/'\n\
Example 5: %prog -tb --batch-mediatype=movie --batch-breadcrumb='kids>cars'\n\
\tonly tag movies who are in a section containing the word 'kids' and movies who's name contains 'cars'\n\
Example 6: %prog -tb --batch-mediatype=show --batch-breadcrumb='>lost>season 1>pilot'\n\
\tonly tag tv episodes, matches all sections, show name contains lost, season 1, episode title contains 'pilot'\n\
Example 7: %prog -tb --batch-breadcrumb='tv>weeds>>goat'\n\
\tonly tag items who are in a section who's title contains 'tv', where the movie or show name contains 'weeds', any season and episode title contains 'goat' \n\
%prog -h for full list of options\n\n\
Filepaths to media items in PMS need to be the same as on machine that is running this script (can be worked around by using the -m option to modify the file path).\
")
    parser.add_option(  "-t", "--tag", action="store_true", dest="tag",
                        help="tag all compatible file types, and update any previously tagged files (if metadata in plex has changed)")
    parser.add_option(  "--tag-update", action="store_true", dest="tag_update",
                        help="update previously tagged files if the PMS entry has changed since last time (modification time)")
    parser.add_option(  "--tag-tv-prefer-season-artwork", action="store_true", dest="tag_prefer_season_artwork",
                        help="when tagging tv show episodes, the season artwork will be used instead of the episode thumbnail")
    
    parser.add_option(  "-r", "--remove-tags", action="store_true", dest="removetags",
                        help="remove all compatible tags from the files")
    parser.add_option(  "-f", "--force", action="store_true", dest="force",
                        help="ignore previous work and steam ahead with task (will re-tag previously tagged files, re-enters data into iTunes, etc.)")
                        
    parser.add_option(  "-o", "--optimize", action="store_true", dest="optimize",
                        help="interleave the audio and video samples, and put the \"MooV\" atom at the beginning of the file")
    parser.add_option(  "--chapter-previews", action="store_true", dest="chapter_previews",
                        help="generate preview images for any chapter markers")
                        
    parser.add_option(  "--export-subtitles", action="store_true", dest="export_subtitles",
                        help="export any subtitles to the same path as the video file")
    parser.add_option(  "--embed-subtitles", action="store_true", dest="embed_subtitles",
                        help="embed compatible files with a compatible \"sidecar\" subtitle file if present")
                        
    parser.add_option(  "--export-artwork", action="store_true", dest="export_artwork",
                        help="export the artwork to the same path as the video file")
    parser.add_option(  "--stats", action="store_true", dest="gather_statistics",
                        help="gather \"interesting\" statistics about the items being processed")
    parser.add_option(  "-m", action="append", type="string", dest="path_modifications", nargs=2, metavar="<find> <replace>",
                        help="perform a find & replace operation on the pms' media file paths (useful if you are running the script on a different machine than the one who is hosting the pms, i.e. the mount paths are different). Supply multiple times to perform several different replacements (operations are performed in order supplied).")
    parser.add_option(  "--open", action="store_true", dest="open_file_location",
                        help="open a Finder window at the containing folder of the file just processed (Mac OS X only)")

    parser.add_option(  "--add-to-itunes", action="store_true", dest="add_to_itunes",
                        help="adds the item to iTunes if not already present")
                        
    parser.add_option(  "-i", "--ip", action="store", dest="ip", type="string",
                        help="specify an alternate IP address that hosts a PMS to connect to (default is localhost)")
    parser.add_option(  "-p", "--port", action="store", dest="port", type="int",
                        help="specify an alternate port number to use when connecting to the PMS (default is 32400)")
                        
    parser.add_option(  "--username", action="store", dest="username", type="string",
                        help="specify the username to use when authenticating with the PMS (default is no authentication)")
    parser.add_option(  "--password", action="store", dest="password", type="string",
                        help="specify the password to use when authenticating with the PMS (default is no authentication)")
    parser.add_option(  "--interactive-password", action="store_true", dest="interactive_password",
                        help="the password to use when authenticating with the PMS will be supplied interactively")
    
    parser.add_option(  "--interactive", action="store_true", dest="interactive",
                        help="interactivly select files to operate on [default]")
    parser.add_option(  "-b", "--batch", action="store_false", dest="interactive",
                        help="disable interactive mode. Requires no human intervention once launched, and will perform operations on all valid files")
    parser.add_option(  "--batch-mediatype", action="store", dest="batch_mediatype", type="choice", choices=["any", "movie", "show"], metavar="[movie/show]",
                        help="only specified media type will be processed")
    parser.add_option(  "--batch-breadcrumb", action="store", dest="batch_breadcrumb", type="string", metavar="breadcrumb",
                        help="only items matching the breadcrumb trail will be processed. Components seperated by '>' (case insensitive)")

    parser.add_option(  "-v", "--verbose", dest="verbose", action="callback", 
                        callback=setLogLevel, help='increase verbosity (can be supplied 0-2 times)')
    parser.add_option(  "-q", "--quiet", action="store_true", dest="quiet",
                        help="ninja-like processing (can only be used when in batch mode)")
    parser.add_option(  "-d", "--dry-run", action="store_true", dest="dryrun",
                        help="pretend to do the job, but never actually change or export anything. Pretends that all tasks succeed. Useful for testing purposes")

    parser.set_defaults( tag=False, tag_update=False, tag_prefer_season_artwork=False, remove_tags=False, 
                        optimize=False, chapter_previews=False, embed_subtitles=False,
                        export_resources=False, export_subtitles=False, export_artwork=False, 
                        gather_statistics=False, open_file_location=False, add_to_itunes=False,
                        force_tagging=False, dryrun=False,
                        interactive=True, quiet=False, batch_mediatype="any", batch_breadcrumb="",
                        ip="localhost", port=32400, username="", password="", interactive_password=False,
                        path_modifications=[])
    
    try:
        opts, args = parser.parse_args()
    except OptionValueError as e:
        parser.error(e)
    
    if opts.export_subtitles or opts.export_artwork:
        opts.export_resources = True
    
    if not opts.tag and not opts.removetags and not opts.optimize and not opts.export_resources and not opts.add_to_itunes and not opts.gather_statistics:
        parser.error("No task to perform. Our work here is done...")
    
    if opts.tag_prefer_season_artwork and not opts.tag:
        parser.error("Cannot prefer season artwork when not tagging...")
        
    if opts.chapter_previews and not opts.tag:
        parser.error("Cannot generate chapter previews when not tagging...")
        
    if opts.embed_subtitles and not opts.tag:
        parser.error("Cannot embed subtitles when not tagging...")
        
    if opts.tag_update and not opts.tag:
        parser.error("Cannot update tags when not tagging...")
    
    if opts.interactive and ( opts.batch_mediatype != "any" or len(opts.batch_breadcrumb) > 0):
        parser.error("Cannot use batch filtering options when batch mode is not active...")
        
    if opts.interactive_password:
        opts.password = getpass.getpass("Password $")
        
    if (len(opts.username) > 0 and not len(opts.password) > 0) or (len(opts.password) > 0 and not len(opts.username) > 0):
        parser.error("Must supply both username and password when using authentication to connect to PMS...")
    
    if len(opts.batch_breadcrumb) > 0:
        opts.batch_breadcrumb = opts.batch_breadcrumb.lower().split(">")
        opts.batch_breadcrumb.reverse()
    
    if opts.quiet:
        root.setLevel(logging.ERROR)
    
    if opts.interactive and not root.isEnabledFor(logging.INFO):
        root.setLevel(logging.INFO)
    
    if opts.dryrun:
        logging.critical( "WARNING, RUNNING IN 'DRY RUN MODE'. NO ACTUAL CHANGES WILL BE MADE" )
    elif opts.removetags:
        logging.critical( "WARNING, TAGS WILL BE REMOVED PERMANENTLY" )
    elif opts.force:
        logging.critical( "FORCE MODE ENABLED. THIS WILL BYPASS ANY 'HAS THIS BEEN DONE BEFORE' CHECKS" )
    
    logging.error( generate_centered_padded_string(" Plex Media Tagger Started ") )
    
    if opts.gather_statistics:
        statistics = LibraryStatistics()
    summary = Summary()
    request_handler = PmsRequestHandler()
    request_handler.ip = opts.ip
    request_handler.port = opts.port
    request_handler.setup_opener(opts.username, opts.password)
    
    global section_processor
    section_processor = SectionProcessor(opts, request_handler)
    
    logging.error( "Connecting to PMS at %s:%d" % (opts.ip, opts.port) )
    sections_container = request_handler.get_sections_container()
    media_container = sections_container.getroot()
    title = media_container.attrib['title1']
    section_elements = media_container.getchildren()
    
    section_element_choice = '' #default is empty == all
    if opts.interactive:
        logging.info( "List of sections for %s" % title )
        for index, section_element in enumerate(section_elements):
            logging.info( "%d. %s" %(index, section_element.attrib['title']) )
        #end for
        if len(section_elements) == 0:
            logging.error( "No sections found" )
        else:    
            logging.warning( "empty input equals all" )
    
            #ask user what sections should be processed
            section_element_choice = raw_input("Section to process $")
            if section_element_choice != '':
                try:
                    section_element_choice = int(section_element_choice)
                except ValueError, e:
                    logging.debug(e)
                    logging.critical( "'%s' is not a valid section number" % input )
                    sys.exit(1)
                #end try
            #end if section_element_choice
        #end if len(section_elements)
    #end if opts.interactive
    
    if section_element_choice == '': #all
        section_elements_to_process = section_elements
    else:
        section_elements_to_process = [section_elements[section_element_choice]]
    #end if
    
    breadcrumb = opts.batch_breadcrumb.pop() if len(opts.batch_breadcrumb) > 0 else ''
    logging.error( "Processing sections" )
    for index, section_element in enumerate(section_elements_to_process):
        section_title = section_element.attrib['title']
        logging.error( generate_right_padded_string("Processing section %d/%d : '%s' " % (index+1, len(section_elements_to_process), section_title)) )
        
        #check mediatype
        if opts.batch_mediatype != 'any':
            section_type = section_element.attrib['type']
            if opts.batch_mediatype != section_type:
                logging.error( " Skipping '%s' because it is not of type '%s'" % (section_title, opts.batch_mediatype) )
                continue
                
        #check breadcrumb
        if not breadcrumb in section_title.lower():
            logging.error( " Skipping '%s' because it does not match breadcrumb '%s'" % (section_title, breadcrumb) )
            continue
        
        section_processor.process_section(section_element)
        if section_processor.abort:
            break
        logging.warning( "Section '%s' processed " % section_title )
    #end for
    if not section_processor.abort:
        logging.error( "Processing sections completed" )
        logging.error( generate_centered_padded_string(" Plex Media Tagger Completed ") )
        results = summary.results()
        for result in results:
            logging.error(result)
    
    if opts.gather_statistics:
        logging.error( generate_centered_padded_string(" Items Processed Statistics ", "=") )
        results = statistics.results()
        for result in results:
            logging.error(result)
        #end for
    #end if stats
#end main

def setLogLevel(*args, **kwargs):
    logging.root.setLevel(logging.root.level - 10)


def signal_handler(signal, frame):
    if not section_processor.abort:
        section_processor.abort = True
        logging.critical( "\rPerforming safe abort... (ctrl+c again to exit immediately)" )
    else:
        logging.critical( "\rAborting immediately..." )
        sys.exit(0)
#end signal_handler

def abort():
    logging.critical( "\r" + generate_centered_padded_string(" Terminating Plex Media Tagger ", "#" ) )
    if section_processor:
        section_processor.event.wait()
    sys.exit(0)
#end def

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (EOFError, RuntimeError):
        abort()
    #end try
#end if __name__
