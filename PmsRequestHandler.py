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
import tempfile
from urllib2 import urlopen, URLError, HTTPError
from urllib import quote_plus

class Singleton(object):
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class PmsRequestHandler(Singleton):
    """docstring for PmsRequestHandler"""
    def base_url(self):
        return "http://%s:%s" % (self.ip, self.port)
    #end def base_url
    
    def getContents(self, url):
        contents = []
        try:
            contents = etree.parse(url)
        except IOError, e:
            logging.debug(e)
            logging.critical("Could not connect to server %s:%s" % (self.ip, self.port))
            sys.exit(1)
        #end try
        return contents
    #end getSectionsList
    
    def getSectionsContainer(self):
        url = "%s/library/sections" % (self.base_url())
        return self.getContents(url)
    #end getSectionsContainer
    
    def get_section_all_container_for_key(self, section_key):
        url = "%s/library/sections/%s/all" % (self.base_url(), section_key)
        return self.getContents(url)
    #end getSection
    
    def get_metadata_container_for_key(self, partial_url):
        url = "%s%s" % (self.base_url(), partial_url)
        return self.getContents(url)
    #end getSection
    
    def download_image(self, item_name, partial_url):
        full_image_url = "%s%s" %(self.base_url(), partial_url)
        escaped_image_url = quote_plus(full_image_url)
        transcoder_image_url = "%s/photo/:/transcode?width=%d&height=%d&url=%s" % (self.base_url(), 1980, 1080, escaped_image_url)
        try:
            f = urlopen(transcoder_image_url)
            temporary_directory = tempfile.gettempdir()
            content_type = f.info()['Content-Type']
            if content_type == 'image/jpeg':
                image_path = os.path.join(temporary_directory, item_name+".jpg")
            elif content_type == 'image/png':
                image_path = os.path.join(temporary_directory, item_name+".jpg")
            else:
                raise TypeError("Failed to download image: Unknown image mimetype [%s]", content_type)
            #end if
            
            logging.debug( "saving temporary artwork to " + image_path)
            with open(image_path, "wb") as local_file:
                local_file.write(f.read())
            #end with open
            return image_path
            
        #handle errors
        except HTTPError, e:
            logging.critical( "HTTP Error:", e.code, url )
        except URLError, e:
            logging.critical( "URL Error:", e.reason, url )
        except TypeError, e:
            logging.critical( e.args )
        #end try
    #end def downloadImage
    
#end class PmsRequestHandler 