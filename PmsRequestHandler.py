#!/usr/bin/env python
#encoding:utf-8
#author:ccjensen/Chris
#project:PlexMediaTagger
#repository:http://github.com/ccjensen/plexmediatagger
#license:Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)

from xml.etree import ElementTree
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
    
    def get_contents(self, url):
        logging.debug("Get contents: %s" % url)
        contents = []
        try:
            xml = urlopen(url)
            contents = ElementTree.parse(xml)
        except IOError, e:
            logging.debug(e)
            logging.critical("Could not connect to server %s:%d" % (self.ip, self.port))
            sys.exit(1)
        #end try
        return contents
    #end getSectionsList
    
    def get_sections_container(self):
        url = "%s/library/sections" % (self.base_url())
        return self.get_contents(url)
    #end getSectionsContainer
    
    def get_section_all_container_for_key(self, section_key):
        url = "%s/library/sections/%s/all" % (self.base_url(), section_key)
        return self.get_contents(url)
    #end getSection
    
    def get_metadata_container_for_key(self, partial_url):
        url = "%s%s" % (self.base_url(), partial_url)
        return self.get_contents(url)
    #end getSection
    
    def download_image(self, partial_url, item_name, desired_item_path):
        full_image_url = "%s%s" %(self.base_url(), partial_url)
        escaped_image_url = quote_plus(full_image_url)
        transcoder_image_url = "%s/photo/:/transcode?width=%d&height=%d&url=%s" % (self.base_url(), 1980, 1080, escaped_image_url)
        try:
            directory = desired_item_path
            if not directory:
                directory = tempfile.gettempdir()
            #end if not directory
            
            f = urlopen(transcoder_image_url)
            content_type = f.info()['Content-Type']
            if content_type == 'image/jpeg':
                image_path = os.path.join(directory, item_name+".jpg")
            elif content_type == 'image/png':
                image_path = os.path.join(directory, item_name+".png")
            else:
                raise TypeError("Failed to download image: Unknown image mimetype [%s]", content_type)
            #end if
            
            logging.debug( "saving artwork to " + image_path)
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
    #end def download_image
    
    def download_stream(self, destination_path, partial_url):
        full_stream_url = "%s%s" %(self.base_url(), partial_url)
        try:
            f = urlopen(full_stream_url)            
            logging.debug( "saving stream to " + destination_path)
            with open(destination_path, "wb") as local_file:
                local_file.write(f.read())
            #end with open
            return destination_path
        #handle errors
        except HTTPError, e:
            logging.critical( "HTTP Error:", e.code, url )
        except URLError, e:
            logging.critical( "URL Error:", e.reason, url )
        except TypeError, e:
            logging.critical( e.args )
        #end try
    #end def download_stream
    
#end class PmsRequestHandler 