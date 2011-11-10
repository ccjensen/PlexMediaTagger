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
        if self.opts.forcetagging:
            return True
        
        self.comment_tag_contents = self.getFileCommentTagContents(part_parser)
        for word in part_parser.comment_tag_contents.split(" "):
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
        all_tags = ["{Artwork:}", "{HD Video:}", "{Gapless:}", "{Content Rating:}", "{Media Kind:}", "{Name:}", "{Artist:}", "{Album Artist:}", "{Album:}", "{Grouping:}", "{Composer:}", "{Comments:}", "{Genre:}", "{Release Date:}", "{Track #:}", "{Disk #:}", "{TV Show:}", "{TV Episode #:}", "{TV Network:}", "{TV Episode ID:}", "{TV Season:}", "{Description:}", "{Long Description:}", "{Rating:}", "{Rating Annotation:}", "{Studio:}", "{Cast:}", "{Director:}", "{Codirector:}", "{Producers:}", "{Screenwriters:}", "{Lyrics:}", "{Copyright:}", "{Encoding Tool:}", "{Encoded By:}", "{contentID:}"]#, "{XID:}", "{iTunes Account:}", "{Sort Name:}", "{Sort Artist:}", "{Sort Album Artist:}", "{Sort Album:}", "{Sort Composer:}", "{Sort TV Show:}"]
        
        logging.warning("removing tags...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]
        tag_cmd.append("-t")
        tag_cmd.append("".join(all_tags))
        
        new_tag_cmd = tag_cmd
        new_tag_cmd.append("-i")
        new_tag_cmd.append(part_parser.file)
        
        logging.debug("remove tags command arguments: %s" % new_tag_cmd)
        #run SublerCLI using the arguments we have created
        result = ""#subprocess.Popen(new_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        if "Error" in result:
            logging.critical("Failed: %s" % result.strip())
        else:
            logging.warning("Tags removed from '%s'" % self.path)
        #end if "Error"
    #end remove_tags
    
    def tag(self, part_parser):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        
        logging.warning("tagging...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]
        tag_cmd.append("-t")
        tag_cmd.append(part_parser.media_item.tag_string()) #also downloads the artwork
        
        new_tag_cmd = tag_cmd
        new_tag_cmd.append("-i")
        new_tag_cmd.append(part_parser.file)
        
        logging.debug("tag command arguments: %s" % new_tag_cmd)
        #run SublerCLI using the arguments we have created
        result = "mm"#subprocess.Popen(new_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        if "Error" in result:
            logging.critical("Failed: %s" % result.strip())
        else:
            logging.warning("Tagged '%s'" % part_parser.file)
        #end if "Error"
    #end tag
    
    def process(self):
        skipped_all = True
        
        for part_parser in self.part_parsers:
            if self.opts.removetags and self.canTag(part_parser):
                skipped_all = False
                remove_tags(part_parser)
            #end if removetags
            if self.opts.tag and self.canTag(part_parser) and self.shouldTag(part_parser):
                skipped_all = False
                tag(part_parser)
            #end if tag   
            if self.opts.optimize and self.canTag(part_parser):
                skipped_all = False
                if self.opts.optimize:
                    tag_cmd.append("-O")
                #end if self.opts.optimize
            #end if optimize
        if skipped_all:
            logging.warning("skipping: no files to tag")
        #end if skipped_all
    #end def process_item
#end MediaPartProcessor