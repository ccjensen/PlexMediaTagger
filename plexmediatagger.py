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


def tagFile(opts, program, series, episode):
    """docstring for tagFile"""
    if not opts.forcetagging:
        #check if file has already been tagged
        alreadyTaggedCmd = "\"%s\" -i \"%s/%s\" -t" % (program.mp4tagger, program.dirPath, episode.fileName)
        #cmd = "\"" + program.mp4tagger + "\" -i \"" + program.dirPath + "/" + episode.fileName.encode("utf-8") + "\"" + " -t"
        if opts.debug:
            print "!!AlreadyTagged command: %s" % alreadyTaggedCmd
        #end if debug
        existingTagsUnsplit = os.popen(alreadyTaggedCmd).read()
        existingTags = existingTagsUnsplit.split('\r')
        for line in existingTags:
            if line.count("tagged by mp4tvtags"):
                if opts.verbose:
                    print "  %s already tagged" % episode.fileName
                #end if verbose
                return
            #end if line.count
        #end for line
    #end if opts.forcetagging
    #setup tags for the MP4Tagger function
    if series.artworkFileName != "":
        addArtwork = " --artwork \"%s/%s\"" % (program.dirPath, series.artworkFileName) #the file we downloaded earlier
    else:
        addArtwork = ""
    #end if series.artworkFileName != ""
    if series.rating != "":
        addRating = " --rating \"%s\"" % series.rating
    else:
        addRating = ""
    #end if series.rating != "":
    
    addMediaKind = " --media_kind \"TV Show\"" #set type to TV Show
    addArtist = " --artist \"%s\"" % series.seriesName
    addName =  " --name \"%s\"" % episode.episodeName
    addAlbum = " --album \"%s - Season %s\"" % (series.seriesName, series.seasonNumber)
    addGenre = " --genre \"%s\"" % series.genres[1] #cause first one is an empty string, and genre can only have one entry
    addAlbumArtist = " --album_artist \"%s\"" % series.seriesName
    addDescription = " --description \"%s\"" % episode.overview
    addLongDescription = " --long_description \"%s\"" % episode.longOverview
    addTVNetwork = " --tv_network \"%s\"" % series.network
    addTVShowName = " --tv_show \"%s\"" % series.seriesName
    addTVEpisode = " --tv_episode_id \"%s\"" % episode.productionCode
    addTVSeasonNum = " --tv_season \"%i\"" % series.seasonNumber
    
    #kept for clarity as it same decision is made
    if episode.singleEpisode:
        addTVEpisodeNum = " --tv_episode_n \"%i\"" % episode.episodeNumbers[0]
        addTracknum = " --track_n \"%i\"" % episode.episodeNumbers[0]
    else:
        addTVEpisodeNum = " --tv_episode_n \"%i\"" % episode.episodeNumbers[0]
        addTracknum = " --track_n \"%i\"" % episode.episodeNumbers[0]    
    #end if episode.singleEpisode
    
    addDisk = " --disk_n \"%i\"" % series.seasonNumber
    addReleaseDate = " --release_date \"%s\"" % episode.firstAired
    #addSortOrderName = " --sortOrder name \"%s\"" % episode.episodeName
    #addSortOrderArtist = " --sortOrder artist \"%s\"" % series.seriesName
    #addSortOrderAlbumArtist = " --sortOrder albumartist \"%s\"" % series.seriesName
    #addSortOrderAlbum = " --sortOrder album \"%s - Season %s\"" % (series.seriesName, series.seasonNumber)
    #addSortOrderShow = " --sortOrder show \"%s\"" % series.seriesName
    addComment = " --comment \"tagged by mp4tvtags\""
    
    addCast = ""
    addDirectors = ""
    addScreenwriters = ""
    
    if len(series.actors) > 0:
        actors = createCommaSeperatedStringFromArray(series.actors)
        addCast = " --cast \"%s\"" % actors
    #end if len 
    if len(episode.directors) > 0:
        directors = createCommaSeperatedStringFromArray(episode.directors)
        addDirectors = " --director \"%s\"" % directors
    #end if len
    if len(episode.writers) > 0:
        screenwriters = createCommaSeperatedStringFromArray(episode.writers)
        addScreenwriters = " --screenwriters \"%s\"" % screenwriters
    #end if len
    
    #Create the command line string
    tagCmd = "\"%s\" -i \"%s/%s\" %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" % \
    (program.mp4tagger, program.dirPath, episode.fileName, addArtwork.encode("utf-8"), addMediaKind.encode("utf-8"), \
    addArtist.encode("utf-8"), addName.encode("utf-8"), addAlbum.encode("utf-8"), addGenre.encode("utf-8"), \
    addAlbumArtist.encode("utf-8"), addDescription.encode("utf-8"), addTVNetwork.encode("utf-8"), addTVShowName.encode("utf-8"), \
    addTVEpisode.encode("utf-8"), addTVSeasonNum.encode("utf-8"), addTVEpisodeNum.encode("utf-8"), addDisk.encode("utf-8"), \
    addTracknum.encode("utf-8"), addRating.encode("utf-8"), addReleaseDate.encode("utf-8"), addComment.encode("utf-8"), \
    addLongDescription.encode("utf-8"), addCast.encode("utf-8"), addDirectors.encode("utf-8"), addScreenwriters.encode("utf-8"))
    
    #run MP4Tagger using the arguments we have created
    if opts.debug:
        print "!!Tag command: %s" % tagCmd
    #end if debug
    
    result = os.popen(tagCmd).read()
    if result.count("Program aborted") or result.count("Error"):
        print "** ERROR: %s" % result
        sys.exit(1)
    
    lockCmd = "chflags uchg \"" + program.dirPath + "/" + episode.fileName + "\""
    
    os.popen(lockCmd)
    if opts.verbose:
        print "  Tagged and locked: " + episode.fileName
    #end if verbose
    #end if overwrite
#end tagFile


def createCommaSeperatedStringFromArray(array):
    """docstring for createCommaSeperatedStringFromArray"""
    result = ""
    for item in array:
        if len(item) > 0:
            if result == "":
                result = "%s" % item
            else:
                result = "%s, %s" % (result, item)
        #end if len
    #end for item
    return result
#end createrdnsatom

def setLogLevel(*args, **kwargs):
    logging.root.setLevel(logging.root.level - 10)

def signal_handler(signal, frame):
        print '\nTerminating Plex Media Tagger'
        sys.exit(0)

def main():
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
    
    try:
        library = etree.parse ("http://%s:%s/library/sections" % (ip, port))
    except IOError, e:
        logging.debug(e)
        logging.critical("Could not connect to server [%s] at port [%s]" % (ip, port))
    #end try
    
    mediaContainer = library.getroot()
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
        input = raw_input("Section to process: ")
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
        sectionType = sectionToProcess.attrib['type']
        
        print "  Processing section %d/%d : '%s'" % (index+1, len(sectionsToProcess), sectionTitle)
        print "  Section contains %ss" % sectionType
    #end for
    
    logging.info("============ Plex Media Tagger Completed ============")
#end main


if __name__ == '__main__':
        sys.exit(main())
#end if __name__