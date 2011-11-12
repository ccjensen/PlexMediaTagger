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
import os
import subprocess
from MovieMetadataParser import *
from ShowMetadataParser import *
from SeasonMetadataParser import *
from EpisodeMetadataParser import *

class MediaItemProcessor:
    """docstring for MediaItemProcessor"""
    def __init__(self, opts, media_item):
        self.opts = opts
        self.media_item = media_item
        self.media_parser = self.media_item.media_parser
        self.part_parsers = [self.media_parser.part_parser]
        
        self.tag_data_delimiter = "::::"
        self.itunes_tag_data_token = "I_T_U_N_E_S"
        self.itunes_rating_token = "R_"
        self.itunes_playcount_token = "PC_"
        self.updated_at_token = "D_"
    #end def __init__
    
    def canTag(self, part_parser):
        if part_parser.file_type == '.m4v' or part_parser.file_type == '.mp4':
            return True
        else:
            logging.info("PlexMediaTagger cannot tag '%s' files" % part_parser.file_type)
            return False
        #end if
    #end def canTag
    
    def shouldTag(self, part_parser):
        if self.opts.force:
            return True
        
        comment_tag_contents = self.getFileCommentTagContents(part_parser)
        for word in comment_tag_contents.split(" "):
            if word.startswith(self.itunes_tag_data_token):
                logging.info("File previously tagged")
                for item in word.split(self.tag_data_delimiter):
                    if item.startswith(self.updated_at_token):
                        tag_data_updated_at = item.split(self.updated_at_token)[1]
                        metadata_updated_at = self.media_item.updated_at
                        if (metadata_updated_at > tag_data_updated_at):
                            logging.info("Metadata has changed since last time")
                            return True
                        else:
                            logging.info("No change to the metadata since last time")
                            return False
                    #end inf
                #end for
                logging.info("Updated at token missing, will re-tag the file")
        return True
    #end def shouldTag
    
    def getFileCommentTagContents(self, part_parser):
        """docstring for getFileCommentTagContents"""
        AtomicParsley = os.path.join(sys.path[0], "AtomicParsley32")
        comment_tag = "Atom \"©cmt\""

        #Create the command line string
        get_tags_cmd = ['%s' % AtomicParsley]
        get_tags_cmd.append('%s' % part_parser.file)
        get_tags_cmd.append('-t')
        
        #check if file has already been tagged
        result = subprocess.Popen(get_tags_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        
        #error checking
        if 'AtomicParsley error' in result:
            logging.critical("Failed to determine file tagged status")
            return nil
        #end if 'AtomicParsley error' in result:
        
        for line in result.split("\n"):
            if comment_tag in line:
               return line

        logging.info("File untagged")
        return ""
        #end if tagString in result
    #end getFileCommentTagContents
    
    def remove_tags(self, part_parser):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        #removal of artwork doesn't seem to work
        all_tags = ["{Artwork:}", "{HD Video:}", "{Gapless:}", "{Content Rating:}", "{Media Kind:}", "{Name:}", "{Artist:}", "{Album Artist:}", "{Album:}", "{Grouping:}", "{Composer:}", "{Comments:}", "{Genre:}", "{Release Date:}", "{Track #:}", "{Disk #:}", "{TV Show:}", "{TV Episode #:}", "{TV Network:}", "{TV Episode ID:}", "{TV Season:}", "{Description:}", "{Long Description:}", "{Rating:}", "{Rating Annotation:}", "{Studio:}", "{Cast:}", "{Director:}", "{Codirector:}", "{Producers:}", "{Screenwriters:}", "{Lyrics:}", "{Copyright:}", "{Encoding Tool:}", "{Encoded By:}", "{contentID:}"]#these are currently not supported in subler cli tool, "{XID:}", "{iTunes Account:}", "{Sort Name:}", "{Sort Artist:}", "{Sort Album Artist:}", "{Sort Album:}", "{Sort Composer:}", "{Sort TV Show:}"]
        
        logging.warning("removing tags...")
        
        #Create the command line command
        tag_removal_cmd = ['%s' % SublerCLI]
        
        if self.opts.optimize:
            action_description = "Tags removed and optimized"
            tag_removal_cmd.append("-O")
        else:
            action_description = "Tags removed"
        #end if optimize
        
        tag_removal_cmd.append("-t")
        tag_removal_cmd.append("".join(all_tags))
        tag_removal_cmd.append("-i")
        tag_removal_cmd.append(part_parser.file)
        
        self.execute_command(part_parser.file, tag_removal_cmd, action_description)
    #end remove_tags
    
    def create_new_comment_tag_contents(self, part_parser):
        media_parser = part_parser.media_parser
        rating = int( float(media_parser.rating) * 10 )
        rating_str = "%s%i" % (self.itunes_rating_token, rating)
        play_count_str = self.itunes_playcount_token + media_parser.view_count
        updated_at_str = self.updated_at_token + media_parser.updated_at
        itunes = [self.itunes_tag_data_token, rating_str, play_count_str, updated_at_str]
        itunes_str = self.tag_data_delimiter.join(itunes)
        return itunes_str
    #end create_new_comment_tag_contents
    
    def tag(self, part_parser):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        
        logging.warning("tagging...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]

        if self.opts.optimize:
            action_description = "Tags added and optimized"
            tag_cmd.append("-O")
        else:
            action_description = "Tags added"
        #end if optimize

        tag_cmd.append("-t")
        tag_cmd.append(part_parser.tag_string()) #also downloads the artwork
        tag_cmd.append("-i")
        tag_cmd.append(part_parser.file)
        
        self.execute_command(part_parser.file, tag_cmd, action_description)
    #end tag
    
    def optimize(self, part_parser):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        
        logging.warning("optimizing file...")
        
        action_description = "Tags optimized"
        #Create the command line command
        optimize_cmd = ['%s' % SublerCLI]
        optimize_cmd.append("-O")
        optimize_cmd.append("-i")
        optimize_cmd.append(part_parser.file)
        
        self.execute_command(part_parser.file, optimize_cmd, action_description)
    #end remove_tags
    
    def execute_command(self, actionable_file_path, command, action_description):
        logging.debug("'%s' arguments: %s" % (action_description, command))
        if self.opts.dryrun:
            result = "dryrun"
        else:
            #run command
            result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        #end
        if "Error" in result:
            logging.critical("Failed: %s" % result.strip())
        else:
            logging.warning("'%s': %s" % (action_description, actionable_file_path))
        #end if "Error"
    #end def execute_command
    
    
    def process(self):
        skipped_all = True
        
        for part_parser in self.part_parsers:
            if self.opts.removetags and self.canTag(part_parser):
                skipped_all = False
                self.remove_tags(part_parser)
            #end if removetags
            if self.opts.tag and self.canTag(part_parser) and self.shouldTag(part_parser):
                skipped_all = False
                self.tag(part_parser)
            #end if tag   
            if self.opts.optimize and not self.opts.tag and not self.opts.removetags and self.canTag(part_parser):
                #optimize is done together with tagging or removing, so only needs to be done here if it's the exclusive action
                skipped_all = False
                self.optimize(part_parser)
            #end if optimize
        if skipped_all:
            logging.warning("skipping: no files to tag")
        #end if skipped_all
    #end def process_item
#end MediaPartProcessor