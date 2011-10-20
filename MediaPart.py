#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

import logging
import sys
import os
import subprocess

class MediaPart(object):
    """docstring for MediaPart"""
    def __init__(self, opts, media_item, path):
        self.opts = opts
        self.media_item = media_item
        self.path = path
        self.file_type = os.path.splitext(self.path)[1]
        
        self.tag_data_delimiter = "::::"
        self.itunes_tag_data_token = "I_T_U_N_E_S" + self.tag_data_delimiter
        self.itunes_rating_token = "R_"
        self.itunes_playcount_token = "PC_"
        self.updated_at_token = "D_"
    #end def __init__
    
    def canTag(self):
        return self.file_type == '.m4v' or self.file_type == '.mp4'
    #end def canTag
    
    def shouldTag(self):
        if not self.canTag():
            logging.info("PlexMediaTagger cannot process '%s' files" % self.file_type)
            return False
        
        if self.opts.forcetagging:
            return True
            
        #here
        self.comment_tag_contents = self.getFileCommentTagContents()
        for word in self.comment_tag_contents.split(" "):
            if word.startswith(self.itunes_tag_data_token):
                logging.info("File previously tagged")
                return False
        return True
    #end def shouldTag
    
    def getFileCommentTagContents(self):
        """docstring for getFileCommentTagContents"""
        AtomicParsley = os.path.join(sys.path[0], "AtomicParsley32")
        comment_tag = "Atom \"©cmt\""

        #Create the command line string
        get_tags_cmd = ['%s' % AtomicParsley]
        get_tags_cmd.append('%s' % self.path)
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
    
    def getCommentTagContents(self):
        rating = int( float(self.media_item.rating) * 10 )
        rating_str = "%s%i" % (self.itunes_rating_token, rating)
        play_count_str = self.itunes_playcount_token + self.media_item.view_count
        updated_at_str = self.updated_at_token + self.media_item.updated_at
        itunes = [self.itunes_tag_data_token, rating_str, play_count_str, updated_at_str]
        itunes_str = self.tag_data_delimiter.join(itunes)
        return itunes_str
    #end getCommentTagContents
    
    def remove_tags(self):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        #removal of artwork doesn't seem to work
        all_tags = ["{Artwork:}", "{HD Video:}", "{Gapless:}", "{Content Rating:}", "{Media Kind:}", "{Name:}", "{Artist:}", "{Album Artist:}", "{Album:}", "{Grouping:}", "{Composer:}", "{Comments:}", "{Genre:}", "{Release Date:}", "{Track #:}", "{Disk #:}", "{TV Show:}", "{TV Episode #:}", "{TV Network:}", "{TV Episode ID:}", "{TV Season:}", "{Description:}", "{Long Description:}", "{Rating:}", "{Rating Annotation:}", "{Studio:}", "{Cast:}", "{Director:}", "{Codirector:}", "{Producers:}", "{Screenwriters:}", "{Lyrics:}", "{Copyright:}", "{Encoding Tool:}", "{Encoded By:}", "{contentID:}"]#, "{XID:}", "{iTunes Account:}", "{Sort Name:}", "{Sort Artist:}", "{Sort Album Artist:}", "{Sort Album:}", "{Sort Composer:}", "{Sort TV Show:}"]
        
        if not self.canTag():
            return
        #end if not shouldTag
        
        logging.warning("removing tags...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]
        tag_cmd.append("-t")
        tag_cmd.append("".join(all_tags))
            
        if self.opts.optimize:
            tag_cmd.append("-O")
        #end if self.opts.optimize
        
        new_tag_cmd = tag_cmd
        new_tag_cmd.append("-i")
        new_tag_cmd.append(self.path)
        
        logging.debug("remove tags command arguments: %s" % new_tag_cmd)
        #run SublerCLI using the arguments we have created
        result = subprocess.Popen(new_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        if "Error" in result:
            logging.critical("Failed: %s" % result.strip())
        else:
            logging.warning("Tags removed from '%s'" % self.path)
        #end if "Error"
    #end remove_tags
    
    def tag(self):
        SublerCLI = os.path.join(sys.path[0], "SublerCLI-v010")
        
        if not self.shouldTag():
            return
        #end if not shouldTag
        
        logging.warning("tagging...")
        
        #Create the command line command
        tag_cmd = ['%s' % SublerCLI]
        tag_cmd.append("-t")
        tag_cmd.append(self.media_item.tag_string()) #also downloads the artwork
        
        if self.opts.optimize:
            tag_cmd.append("-O")
        #end if self.opts.optimize
        
        new_tag_cmd = tag_cmd
        new_tag_cmd.append("-i")
        new_tag_cmd.append(self.path)
        
        logging.debug("tag command arguments: %s" % new_tag_cmd)
        #run SublerCLI using the arguments we have created
        result = subprocess.Popen(new_tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        if "Error" in result:
            logging.critical("Failed: %s" % result.strip())
        else:
            logging.warning("Tagged '%s'" % self.path)
        #end if "Error"
    #end tag
    
#end class MetadataParser